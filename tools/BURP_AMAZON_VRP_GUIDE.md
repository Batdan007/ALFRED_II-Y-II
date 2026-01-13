# Burp Suite Amazon VRP Testing Guide

**Hunter:** BATDAN
**Target:** Amazon.com (VRP Program)
**Bounty Range:** $200 - $25,000

---

## Quick Setup

### 1. Install Burp Suite
```
choco install burp-suite-free-edition -y
```
Or download: https://portswigger.net/burp/communitydownload

### 2. Configure Proxy
- Burp listens on: `127.0.0.1:8080`
- Set browser proxy to this address
- Or use FoxyProxy extension

### 3. Install CA Certificate
1. With proxy on, visit: http://burp
2. Click "CA Certificate"
3. Import into browser certificate store

### 4. Load VRP Config
1. Open Burp → Project Options → Load from file
2. Select: `tools/burp_amazon_vrp.json`
3. This sets Amazon scope and VRP User-Agent

---

## VRP Rules Reminder

- [x] Use User-Agent: `amazonvrpresearcher_BATDAN`
- [x] Max 5 requests/second
- [x] Only test in-scope (*.amazon.com)
- [x] NO AWS assets
- [x] NO other users' data
- [x] NO DoS attacks

---

## High-Value Test Cases

### 1. Price Manipulation ($2K-$6K)

**Where:** Cart, Checkout, Gift Cards

**How:**
1. Add item to cart
2. Intercept checkout request in Burp
3. Find price parameter
4. Send to Repeater
5. Modify price value (0, -1, 0.01)
6. Check if order processes

**Payloads:**
```
0
-1
0.01
0.001
```

### 2. Race Conditions ($6K-$25K)

**Where:** Coupon redemption, Gift card balance, Checkout

**How:**
1. Capture coupon apply request
2. Send to Turbo Intruder
3. Send 50+ simultaneous requests
4. Check if coupon applied multiple times

**Turbo Intruder Script:**
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                          concurrentConnections=50,
                          requestsPerConnection=1,
                          pipeline=False)
    for i in range(50):
        engine.queue(target.req)

def handleResponse(req, interesting):
    if 'success' in req.response.lower():
        table.add(req)
```

### 3. IDOR - Order Access ($2K-$6K)

**Where:** Order history, Order details, Invoices

**How:**
1. Get your order ID (e.g., `123-4567890-1234567`)
2. Find order detail request in Proxy history
3. Send to Intruder
4. Fuzz the order ID parameter
5. Check for other users' order data

**Payloads:**
```
123-4567890-1234568
123-4567890-1234566
124-4567890-1234567
```

### 4. IDOR - Profile Access ($2K-$6K)

**Where:** User profiles, Wishlists, Reviews

**How:**
1. Get your profile ID from URL
2. Find profile request
3. Modify profile ID
4. Check if other profiles accessible

### 5. GraphQL Attacks ($2K-$12K)

**Where:** Any GraphQL endpoint

**Tests:**
```graphql
# Introspection
query { __schema { types { name } } }

# Batch query attack
query {
  user1: user(id: "1") { email }
  user2: user(id: "2") { email }
  user3: user(id: "3") { email }
}

# Deep query (DoS - be careful)
query { user { friends { friends { friends { name } } } } }
```

### 6. Session Fixation ($2K-$6K)

**How:**
1. Note session-id before login
2. Login
3. Check if session-id changed
4. If same = Session Fixation!

### 7. Cart Manipulation ($2K-$6K)

**Tests:**
- Negative quantity
- Zero price items
- Currency confusion (USD → INR)
- Add item, change price, checkout

### 8. Gift Card Abuse ($2K-$6K)

**Tests:**
- Redeem same code twice (race condition)
- Partial redemption bypass
- Gift card enumeration
- Balance transfer bugs

---

## Burp Extensions to Install

### Essential
1. **Autorize** - Auto IDOR testing
2. **Param Miner** - Find hidden parameters
3. **Turbo Intruder** - Race condition testing
4. **JSON Web Tokens** - JWT analysis

### Optional
5. **Active Scan++** - Enhanced scanner
6. **Backslash Powered Scanner** - Server-side injection
7. **HTTP Request Smuggler** - Smuggling attacks

---

## Testing Workflow

### Phase 1: Mapping (30 min)
1. Browse Amazon authenticated
2. Let Burp capture all traffic
3. Review Site Map
4. Identify interesting endpoints

### Phase 2: Parameter Analysis (1 hr)
1. Run Param Miner on key endpoints
2. Note hidden parameters
3. Check for debug/admin params

### Phase 3: Access Control (2 hrs)
1. Enable Autorize extension
2. Get second Amazon account cookies
3. Test all endpoints for IDOR
4. Check horizontal/vertical access

### Phase 4: Business Logic (2 hrs)
1. Test cart manipulation
2. Test checkout flow
3. Test coupon/promo codes
4. Test gift card redemption

### Phase 5: Race Conditions (1 hr)
1. Use Turbo Intruder
2. Test coupon stacking
3. Test gift card balance
4. Test checkout double-spend

---

## Endpoints to Focus On

| Endpoint | Test For |
|----------|----------|
| /gp/cart/view.html | Price tampering |
| /gp/buy/spc/handlers/display.html | Checkout bypass |
| /gp/css/order-history | Order IDOR |
| /hz/wishlist/ls | Wishlist IDOR |
| /gp/profile | Profile IDOR |
| /gc/redeem | Gift card abuse |
| /cpe/yourpayments | Payment IDOR |
| /ap/signin | Auth bypass |
| /graphql | GraphQL attacks |

---

## Report Template

When you find something, use this format for HackerOne:

```markdown
## Summary
[One line description]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Impact
[What can an attacker do?]

## Proof of Concept
[Screenshots, video, or code]

## Remediation
[How to fix]
```

---

## Files Created

| File | Purpose |
|------|---------|
| `burp_amazon_vrp.json` | Burp project config with scope |
| `burp_amazon_payloads.txt` | Intruder payload lists |
| `BURP_AMAZON_VRP_GUIDE.md` | This guide |

---

## Quick Reference

**Bounty Tiers:**
- Critical: $12,000 - $25,000
- High: $2,000 - $6,000
- Medium: $400 - $600
- Low: $200

**Best Targets:**
1. Race conditions on money operations
2. IDOR on sensitive data
3. Business logic in checkout
4. GraphQL authorization bypass

**Pro Tips:**
- Test mobile API (different controls)
- Check seller central (if in scope)
- Look at new features (less hardened)
- Test during sales events (more traffic)

---

*Created by ALFRED II-Y-II for BATDAN*
