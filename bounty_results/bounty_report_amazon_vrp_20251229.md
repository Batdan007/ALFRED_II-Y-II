# Amazon VRP Bug Bounty Report

**Target:** https://www.amazon.com
**Date:** 2025-12-29
**Hunter:** BATDAN
**Program:** Amazon Vulnerability Research Program (VRP)
**User-Agent:** `amazonvrpresearcher_BATDAN`
**Scan Type:** External/Unauthenticated (VRP-Compliant)

---

## Executive Summary

| Severity | Count | Potential Bounty |
|----------|-------|------------------|
| Critical | 0 | $0 |
| High | 0 | $0 |
| Medium | 0 | $0 |
| Low | 1 | $200 |
| Informational | 2 | $0 |

**Overall Assessment:** Amazon.com has robust security controls. The site employs strong HSTS, proper input sanitization, and no obvious vulnerabilities were detected in unauthenticated testing.

---

## Infrastructure Analysis

### Server Information
- **Server Header:** `Server` (generic - good practice)
- **CDN/WAF:** Amazon CloudFront
- **HSTS:** `max-age=47474747; includeSubDomains; preload` (EXCELLENT)

### Security Contact
- **security.txt:** Present at `/.well-known/security.txt`
- **Bug Bounty:** https://hackerone.com/amazonvrp
- **Hiring:** https://www.amazon.jobs/en/teams/infosec

---

## Findings

### 1. [LOW] Missing Security Headers

**Description:** Several recommended security headers are not implemented.

**Missing Headers:**
| Header | Risk | Impact |
|--------|------|--------|
| Content-Security-Policy | XSS mitigation | Medium |
| X-Frame-Options | Clickjacking | Low |
| X-Content-Type-Options | MIME sniffing | Low |
| Permissions-Policy | Feature control | Low |

**Note:** Amazon likely uses other compensating controls. Per VRP policy, this may receive reduced severity or be marked as "Biz Accepted Risk" due to mitigating controls.

**Recommendation:** Implement CSP header for defense-in-depth.

**CVSS 3.0:** 3.1 (Low)

---

### 2. [INFO] API Rate Limiting Detected

**Endpoint:** `/api/`
**Response:** 429 Too Many Requests

**Description:** The API endpoint correctly implements rate limiting.

**Assessment:** This is GOOD security practice, not a vulnerability.

---

### 3. [INFO] Robots.txt Reveals Internal Paths

**Description:** The robots.txt file discloses internal application paths.

**Interesting Disallowed Paths:**
```
/exec/obidos/account-access-login
/gp/cart
/gp/sign-in
/gp/reader
/gp/product/rate-this-item
/gp/richpub/syltguides/create
```

**Assessment:** Standard practice for search engine control. Not a vulnerability, but useful for attack surface mapping.

---

## Negative Findings (No Vulnerabilities)

### Tests Performed - All Passed

| Test | Result | Notes |
|------|--------|-------|
| Open Redirect | NOT VULNERABLE | Redirect parameters properly validated |
| Reflected XSS | NOT VULNERABLE | Search input sanitized |
| CORS Misconfiguration | NOT VULNERABLE | Proper CORS configuration |
| HTTP Method Tampering | NOT VULNERABLE | Methods not disclosed |
| Web Cache Poisoning | NOT VULNERABLE | Headers not reflected |
| Directory Traversal | NOT VULNERABLE | N/A for tested endpoints |

---

## Endpoints Discovered

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/ap/signin` | 200 | Authentication portal |
| `/hz/contact-us/` | 200 | Customer support |
| `/gp/cart/view.html` | 200 | Shopping cart |
| `/dp/B0` | 200 | Product pages |
| `/gp/goldbox` | 302 | Deals (seasonal redirect) |
| `/.well-known/security.txt` | 200 | Security contact |
| `/api/` | 429 | Rate-limited API |
| `/gp/profile/` | 302 | Requires auth |
| `/gp/css/order-history` | 302 | Requires auth |

---

## Recommendations for Deeper Testing

### Authenticated Testing Required
These areas require a valid Amazon account for testing:

1. **Account Takeover Vectors**
   - Password reset flow
   - Session management
   - MFA bypass attempts

2. **IDOR Testing**
   - `/gp/profile/{user_id}`
   - Order history access
   - Wishlist privacy

3. **Payment Flow**
   - Cart manipulation
   - Price tampering
   - Gift card abuse

4. **Seller Central** (if in scope)
   - Seller account takeover
   - Inventory manipulation
   - Review manipulation

### API Testing
- GraphQL introspection (if available)
- Mobile API endpoints
- Rate limit bypass

---

## Compliance Notes

### VRP Rules Followed
- [x] Used `amazonvrpresearcher_BATDAN` User-Agent
- [x] Rate limited to < 5 requests/second
- [x] No AWS assets tested
- [x] No attempt to access other users' data
- [x] No denial of service attempts
- [x] No social engineering

### Out of Scope (Not Tested)
- AWS infrastructure
- Third-party integrations
- Physical security
- Social engineering

---

## Conclusion

Amazon.com demonstrates mature security practices:

1. **Strong HSTS** - Excellent implementation with preload
2. **Input Sanitization** - No obvious XSS vectors
3. **Rate Limiting** - API properly protected
4. **Generic Headers** - Server type not disclosed
5. **Security.txt** - Clear vulnerability reporting path

The only low-severity finding (missing optional headers) is likely a known business decision given Amazon's scale and other compensating controls.

**Recommendation:** Authenticated testing would be required to find higher-severity vulnerabilities. Consider creating a test account and focusing on:
- IDOR in user-specific endpoints
- Business logic flaws in cart/checkout
- Session management issues

---

## References

- Amazon VRP Program: https://hackerone.com/amazonvrp
- VRP Policy: https://hackerone.com/amazonvrp/policy
- CVSS Calculator: https://www.first.org/cvss/calculator/3.0

---

*Generated by ALFRED II-Y-II Bug Bounty Hunter*
*Hunter: Daniel J. Rita (BATDAN)*
*Compliant with Amazon VRP Rules of Engagement*
