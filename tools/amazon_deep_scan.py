"""Amazon VRP Deep Scan - IDOR and Business Logic Testing"""
import requests
import time
import re
from datetime import datetime

session = requests.Session()
session.cookies.set('session-id', '137-5920558-2461442', domain='.amazon.com')
session.cookies.set('ubid-main', '134-4405918-4002641', domain='.amazon.com')
session.cookies.set('session-token', 'hAZKvc0fQbHdBwWY2Ugl2SY7irU9dtYatVbSFCQ1Jg0dnhFTgVmY3cDbQKWSnyDK9wRG/TnJZ2k+ho3Y5ijbzL20/JehF//FRihtW9Y3JDp+L231liyWjb7igFJaGV4TSY6mNQnFaXR88VJsVAAdICGj+vE4vlZM665nUDzr1XsQavgdVa4IF9tO01v+B1duqQ34poka/jOH2V2sls/E8JqffaVrN4KHNib/rf+3LH0vGmVOY/e2+SZVJRQu36DuFHoxCNvMrR84Gc3kjJyzzPB/RpxD0xNvQ69BWGpwkREIFmRGIlQjj0TbNodU1aL51PLBJ3jHu8eLuu1Jszb/tfh4u0iCpu2VSGeHLUqCiiJk4n+BeNZjZQ==', domain='.amazon.com')
session.cookies.set('x-main', 'lMKvZAHusJgD0ppHYujzZAJzny1iJAHPjXFL1tQRjyskTwGPumhhBJCnkAKhut4@', domain='.amazon.com')
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

RATE = 0.3
findings = []

print('='*60)
print('DEEP VULNERABILITY TESTING')
print('='*60)

# 1. IDOR - Order Details
print('\n[IDOR] Testing order access control...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gp/css/order-history')
order_ids = list(set(re.findall(r'([0-9]{3}-[0-9]{7}-[0-9]{7})', r.text)))

if order_ids:
    own_order = order_ids[0]
    print(f'  Own order: {own_order}')

    time.sleep(RATE)
    fake_order = '999-9999999-9999999'
    r2 = session.get(f'https://www.amazon.com/gp/css/summary/print.html?orderID={fake_order}')
    if 'order' in r2.text.lower() and r2.status_code == 200:
        if 'not found' not in r2.text.lower() and 'error' not in r2.text.lower():
            print('  [!] POTENTIAL IDOR - fake order returned data!')
            findings.append({'type': 'IDOR', 'severity': 'HIGH', 'location': 'Order access'})
        else:
            print('  [OK] Fake order properly rejected')
    else:
        print('  [OK] Order access controlled')
else:
    print('  No orders found to test')

# 2. Account enumeration
print('\n[ENUM] Testing account enumeration...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/ap/forgotpassword')
if r.status_code == 200:
    print('  [INFO] Password reset page accessible')

# 3. Wishlist privacy
print('\n[PRIVACY] Testing wishlist visibility...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/hz/wishlist/ls')
wishlist_ids = re.findall(r'id=([A-Z0-9]{10,})', r.text)
if wishlist_ids:
    print(f'  Found {len(wishlist_ids)} wishlist IDs')
else:
    print('  No wishlists found')

# 4. Gift card balance
print('\n[LOGIC] Testing gift card endpoints...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gc/balance')
if r.status_code == 200:
    print('  [+] Gift card balance page accessible')
    balance = re.search(r'\$([0-9,.]+)', r.text)
    if balance:
        print(f'  [INFO] Balance: ${balance.group(1)}')

# 5. Data leakage check
print('\n[LEAK] Checking for data leakage...')
time.sleep(RATE)
r = session.get('https://www.amazon.com/gp/css/account/info/view.html')
comments = re.findall(r'<!--.*?-->', r.text, re.DOTALL)
sensitive = ['password', 'secret', 'apikey', 'private']
leaked = False
for comment in comments:
    for s in sensitive:
        if s in comment.lower():
            print(f'  [!] Sensitive keyword in comment: {s}')
            findings.append({'type': 'Info Leak', 'severity': 'LOW', 'detail': s})
            leaked = True
if not leaked:
    print('  [OK] No sensitive data in comments')

# 6. Check hidden inputs
print('\n[HIDDEN] Checking hidden form fields...')
hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', r.text)
print(f'  Found {len(hidden_inputs)} hidden inputs')
for inp in hidden_inputs[:3]:
    name = re.search(r'name=["\']([^"\']+)["\']', inp)
    if name:
        print(f'    - {name.group(1)}')

print('\n' + '='*60)
print('DEEP TESTING COMPLETE')
print('='*60)
print(f'Findings: {len(findings)}')
for f in findings:
    sev = f['severity']
    typ = f['type']
    print(f'  [{sev}] {typ}')
if not findings:
    print('  No critical vulnerabilities found')
    print('\n  Manual testing recommended:')
    print('  - Burp Suite for parameter tampering')
    print('  - Race conditions on checkout')
    print('  - GraphQL introspection')
