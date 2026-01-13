# Missing X-Content-Type-Options Header

## Summary
The application at stripchat.com does not set the X-Content-Type-Options header, allowing browsers to perform MIME-type sniffing.

## Severity
**Low** (CVSS 2.1)

## Steps to Reproduce
1. Navigate to https://stripchat.com
2. Open browser Developer Tools (F12)
3. Go to Network tab
4. Refresh the page
5. Click on the main document request
6. Check Response Headers
7. Observe that `X-Content-Type-Options` header is missing

## Expected Behavior
The server should return `X-Content-Type-Options: nosniff` header.

## Actual Behavior
No X-Content-Type-Options header is present.

## Impact
Without this header:
- Browsers may interpret files as a different MIME type
- Could lead to XSS if user-uploaded content is served with incorrect type
- Reduces defense-in-depth

## Proof of Concept
```bash
curl -I https://stripchat.com 2>/dev/null | grep -i "x-content-type-options"
# Returns empty - header not set
```

## Remediation
Add the following header to all responses:
```
X-Content-Type-Options: nosniff
```

## References
- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
- https://owasp.org/www-project-secure-headers/

---
**Hunter:** BATDAN
**Date:** 2025-12-29
