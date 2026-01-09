"""
Stripe Billing Integration
Subscriptions, payments, and checkout

Subscription Tiers:
- Free: 1 MaiAI agent, 100 messages/day
- Pro ($9.99/mo): 5 agents, 1000 messages/day, priority support
- Enterprise ($49.99/mo): Unlimited agents, unlimited messages, API access

Author: Daniel J Rita (BATDAN)
"""

import os
import logging
from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from pydantic import BaseModel

# Import Stripe (optional - graceful degradation)
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False

from .database import UserDB
from .auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["Billing"])


# ============================================================================
# Configuration
# ============================================================================

# Stripe keys from environment
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Product/Price IDs (create these in Stripe Dashboard)
PRICE_IDS = {
    "pro_monthly": os.getenv("STRIPE_PRICE_PRO_MONTHLY", "price_pro_monthly"),
    "pro_yearly": os.getenv("STRIPE_PRICE_PRO_YEARLY", "price_pro_yearly"),
    "enterprise_monthly": os.getenv("STRIPE_PRICE_ENTERPRISE_MONTHLY", "price_enterprise_monthly"),
    "enterprise_yearly": os.getenv("STRIPE_PRICE_ENTERPRISE_YEARLY", "price_enterprise_yearly"),
}

# Tier limits
TIER_LIMITS = {
    "free": {
        "agents": 1,
        "messages_per_day": 100,
        "price": 0,
        "features": ["1 MaiAI Agent", "100 messages/day", "Community support"]
    },
    "pro": {
        "agents": 5,
        "messages_per_day": 1000,
        "price": 999,  # cents
        "features": ["5 MaiAI Agents", "1,000 messages/day", "Priority support", "Voice customization"]
    },
    "enterprise": {
        "agents": -1,  # unlimited
        "messages_per_day": -1,  # unlimited
        "price": 4999,  # cents
        "features": ["Unlimited Agents", "Unlimited messages", "API access", "Custom integrations", "Dedicated support"]
    }
}

# Initialize Stripe
if STRIPE_AVAILABLE and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
    logger.info("Stripe initialized")
else:
    logger.warning("Stripe not configured - billing features disabled")


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateCheckoutRequest(BaseModel):
    price_id: str  # e.g., "pro_monthly"
    success_url: str
    cancel_url: str


class CreatePortalRequest(BaseModel):
    return_url: str


# ============================================================================
# Billing Endpoints
# ============================================================================

@router.get("/tiers")
async def get_tiers():
    """
    Get available subscription tiers and pricing
    """
    return {
        "tiers": TIER_LIMITS,
        "stripe_enabled": STRIPE_AVAILABLE and bool(STRIPE_SECRET_KEY)
    }


@router.get("/status")
async def get_billing_status(user: dict = Depends(get_current_user)):
    """
    Get current user's billing status
    """
    tier = user["subscription_tier"]
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])

    return {
        "tier": tier,
        "status": user["subscription_status"],
        "expires": user["subscription_expires"],
        "limits": limits,
        "stripe_customer_id": user.get("stripe_customer_id")
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session for subscription

    Returns checkout URL to redirect user to
    """
    if not STRIPE_AVAILABLE or not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")

    price_id = PRICE_IDS.get(request.price_id)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid price ID")

    try:
        # Create or get Stripe customer
        if user.get("stripe_customer_id"):
            customer_id = user["stripe_customer_id"]
        else:
            customer = stripe.Customer.create(
                email=user["email"],
                name=user.get("name"),
                metadata={"user_id": str(user["id"])}
            )
            customer_id = customer.id
            UserDB.update_subscription(
                user_id=user["id"],
                tier=user["subscription_tier"],
                status=user["subscription_status"],
                stripe_customer_id=customer_id
            )

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            mode="subscription",
            success_url=request.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.cancel_url,
            metadata={
                "user_id": str(user["id"])
            }
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(
    request: CreatePortalRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create Stripe customer portal session

    Allows user to manage subscription, update payment method, view invoices
    """
    if not STRIPE_AVAILABLE or not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Billing not configured")

    if not user.get("stripe_customer_id"):
        raise HTTPException(status_code=400, detail="No subscription found")

    try:
        session = stripe.billing_portal.Session.create(
            customer=user["stripe_customer_id"],
            return_url=request.return_url
        )

        return {"portal_url": session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events

    Events handled:
    - checkout.session.completed: Subscription created
    - customer.subscription.updated: Subscription changed
    - customer.subscription.deleted: Subscription cancelled
    - invoice.payment_failed: Payment failed
    """
    if not STRIPE_AVAILABLE or not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhooks not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle events
    event_type = event["type"]
    data = event["data"]["object"]

    logger.info(f"Stripe webhook: {event_type}")

    if event_type == "checkout.session.completed":
        # Subscription created
        user_id = int(data.get("metadata", {}).get("user_id", 0))
        if user_id:
            # Determine tier from price
            tier = "pro"  # Default to pro for now
            if "enterprise" in str(data.get("amount_total", 0)):
                tier = "enterprise"

            UserDB.update_subscription(
                user_id=user_id,
                tier=tier,
                status="active",
                stripe_customer_id=data.get("customer")
            )
            logger.info(f"User {user_id} subscribed to {tier}")

    elif event_type == "customer.subscription.updated":
        customer_id = data.get("customer")
        status = data.get("status")

        # Find user by customer ID and update
        # (Would need to add a method to find user by stripe_customer_id)
        logger.info(f"Subscription updated for customer {customer_id}: {status}")

    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        logger.info(f"Subscription cancelled for customer {customer_id}")
        # Downgrade to free tier

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        logger.warning(f"Payment failed for customer {customer_id}")

    return {"received": True}


# ============================================================================
# Testing Endpoint (remove in production)
# ============================================================================

@router.post("/test-upgrade")
async def test_upgrade(tier: str = "pro", user: dict = Depends(get_current_user)):
    """
    Test endpoint to upgrade subscription without payment
    FOR DEVELOPMENT ONLY - remove in production
    """
    if tier not in TIER_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid tier")

    UserDB.update_subscription(
        user_id=user["id"],
        tier=tier,
        status="active"
    )

    return {"message": f"Upgraded to {tier}", "tier": tier}
