"""
Email Service using Resend
Transactional emails for beta signups, welcome emails, etc.

Author: Daniel J Rita (BATDAN)
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import Resend
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    resend = None
    RESEND_AVAILABLE = False

# Configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "ALFRED Systems <noreply@alfredsystems.ai>")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://alfredsystems.vercel.app")

# Initialize Resend
if RESEND_AVAILABLE and RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend email service initialized")
else:
    logger.warning("Resend not configured - emails will be logged only")


def send_email(to: str, subject: str, html: str) -> bool:
    """Send an email using Resend"""
    if not RESEND_AVAILABLE or not RESEND_API_KEY:
        logger.info(f"[EMAIL LOG] To: {to}, Subject: {subject}")
        return True  # Pretend success for dev

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html
        })
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


def send_beta_welcome(email: str, name: Optional[str] = None) -> bool:
    """Send beta welcome email with access instructions"""
    display_name = name or "there"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .content {{ background: #f9f9f9; border-radius: 12px; padding: 30px; margin: 20px 0; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 500; }}
            .features {{ list-style: none; padding: 0; }}
            .features li {{ padding: 8px 0; padding-left: 24px; position: relative; }}
            .features li::before {{ content: "✓"; position: absolute; left: 0; color: #e94560; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; padding: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">ALFRED SYSTEMS</div>
            </div>

            <div class="content">
                <h2>Welcome to the Beta, {display_name}!</h2>

                <p>You're in! As a beta tester, you get <strong>Pro features free</strong> while we perfect the platform.</p>

                <p>What you get:</p>
                <ul class="features">
                    <li>5 AI Agents (instead of 1)</li>
                    <li>1,000 messages/day</li>
                    <li>Unlimited memory</li>
                    <li>All personality presets</li>
                    <li>Voice customization</li>
                    <li>Priority support</li>
                </ul>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{FRONTEND_URL}/signup" class="button">Create Your Account</a>
                </p>

                <p>Already signed up? <a href="{FRONTEND_URL}/login">Sign in here</a></p>
            </div>

            <div class="footer">
                <p>Patent-Pending AI Technology by Daniel J Rita (BATDAN)</p>
                <p>CAMDAN Enterprises LLC</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(email, "Welcome to ALFRED Systems Beta!", html)


def send_signup_welcome(email: str, name: Optional[str] = None) -> bool:
    """Send welcome email after account creation"""
    display_name = name or "there"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; padding: 20px 0; }}
            .logo {{ font-size: 24px; font-weight: bold; background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .content {{ background: #f9f9f9; border-radius: 12px; padding: 30px; margin: 20px 0; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 500; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; padding: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">ALFRED SYSTEMS</div>
            </div>

            <div class="content">
                <h2>Welcome, {display_name}!</h2>

                <p>Your ALFRED Systems account is ready. Time to birth your first AI agent!</p>

                <p style="text-align: center; margin: 30px 0;">
                    <a href="{FRONTEND_URL}/dashboard" class="button">Go to Dashboard</a>
                </p>

                <p><strong>Quick Start:</strong></p>
                <ol>
                    <li>Click "Birth New Agent" on your dashboard</li>
                    <li>Choose a personality (British Butler, Coder, Coach, etc.)</li>
                    <li>Give your agent a name</li>
                    <li>Start chatting!</li>
                </ol>

                <p>Questions? Reply to this email or reach out on Twitter @BATDAN.</p>
            </div>

            <div class="footer">
                <p>Patent-Pending AI Technology by Daniel J Rita (BATDAN)</p>
                <p>CAMDAN Enterprises LLC</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(email, "Welcome to ALFRED Systems!", html)
