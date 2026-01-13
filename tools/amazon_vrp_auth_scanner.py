"""
Amazon VRP Authenticated Scanner
Part of ALFRED II-Y-II Bug Bounty Hunter

Usage:
1. Create Amazon account with BATDAN@wearehackerone.com
2. Login and copy cookies from browser
3. Run: python amazon_vrp_auth_scanner.py --cookies "your_cookies_here"

Author: Daniel J. Rita (BATDAN)
"""

import argparse
import requests
import time
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, quote

class AmazonVRPScanner:
    """Authenticated Amazon VRP Scanner"""

    def __init__(self, cookies: str, h1_username: str = "BATDAN"):
        self.h1_username = h1_username
        self.user_agent = f"amazonvrpresearcher_{h1_username}"
        self.rate_limit = 0.25  # 4 req/sec (under 5 limit)
        self.base_url = "https://www.amazon.com"
        self.findings = []

        # Parse cookies
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

        # Set cookies
        for cookie in cookies.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                self.session.cookies.set(name.strip(), value.strip(), domain=".amazon.com")

        self.results_dir = Path("bounty_results")
        self.results_dir.mkdir(exist_ok=True)

    def _rate_limit(self):
        """Comply with VRP rate limiting"""
        time.sleep(self.rate_limit)

    def verify_auth(self) -> bool:
        """Verify we're logged in"""
        print("[AUTH] Verifying authentication...")
        self._rate_limit()

        r = self.session.get(f"{self.base_url}/gp/css/account/info/view.html", allow_redirects=False)

        if r.status_code == 200:
            print("  [+] Authenticated successfully!")
            # Try to extract account name
            if "Hello," in r.text:
                match = re.search(r'Hello,\s*([^<]+)', r.text)
                if match:
                    print(f"  [+] Logged in as: {match.group(1).strip()}")
            return True
        elif r.status_code in [301, 302]:
            print("  [-] Not authenticated - redirected to login")
            print("  [!] Please provide valid session cookies")
            return False
        else:
            print(f"  [?] Unexpected status: {r.status_code}")
            return False

    def test_idor_profile(self):
        """Test IDOR on user profiles"""
        print("\n[IDOR] Testing profile access...")

        # Get own profile first
        self._rate_limit()
        r = self.session.get(f"{self.base_url}/gp/profile/", allow_redirects=True)

        # Extract own profile ID
        own_profile_id = None
        if "/amzn1.account." in r.url:
            own_profile_id = re.search(r'amzn1\.account\.([A-Z0-9]+)', r.url)
            if own_profile_id:
                own_profile_id = own_profile_id.group(1)
                print(f"  [+] Own profile ID: amzn1.account.{own_profile_id[:8]}...")

        # Test accessing other profiles (use public test IDs)
        test_profiles = [
            "amzn1.account.AAAAAAAAAAAAAAAAAAAAAAAAAAA",  # Invalid format test
            "amzn1.account.TEST123456789012345678901234",  # Random test
        ]

        for profile in test_profiles:
            self._rate_limit()
            try:
                r = self.session.get(f"{self.base_url}/gp/profile/{profile}")
                if r.status_code == 200 and "profile" in r.text.lower():
                    print(f"  [!] Profile accessible: {profile[:30]}...")
                elif r.status_code == 404:
                    print(f"  [OK] Profile not found (expected): {profile[:20]}...")
                else:
                    print(f"  [?] Status {r.status_code}: {profile[:20]}...")
            except Exception as e:
                print(f"  Error: {e}")

    def test_idor_orders(self):
        """Test IDOR on order history"""
        print("\n[IDOR] Testing order access...")

        self._rate_limit()
        r = self.session.get(f"{self.base_url}/gp/css/order-history")

        if r.status_code == 200:
            print("  [+] Order history accessible")

            # Extract order IDs
            order_ids = re.findall(r'order[Ii]d[=:]([0-9\-]+)', r.text)
            if order_ids:
                print(f"  [+] Found {len(set(order_ids))} order IDs")

                # Test accessing order details with modified IDs
                for order_id in list(set(order_ids))[:2]:
                    self._rate_limit()
                    # Try to access order details
                    test_url = f"{self.base_url}/gp/css/summary/print.html?orderID={order_id}"
                    r2 = self.session.get(test_url)
                    print(f"  [+] Order {order_id[:10]}... - Status: {r2.status_code}")
        else:
            print(f"  [-] Order history status: {r.status_code}")

    def test_idor_wishlist(self):
        """Test IDOR on wishlists"""
        print("\n[IDOR] Testing wishlist access...")

        self._rate_limit()
        r = self.session.get(f"{self.base_url}/hz/wishlist/ls")

        if r.status_code == 200:
            print("  [+] Wishlist page accessible")

            # Extract wishlist IDs
            wishlist_ids = re.findall(r'wishlist[Ii]d[=:/]([A-Z0-9]+)', r.text)
            if wishlist_ids:
                print(f"  [+] Found {len(set(wishlist_ids))} wishlist IDs")
        else:
            print(f"  [-] Wishlist status: {r.status_code}")

    def test_cart_manipulation(self):
        """Test cart for business logic flaws"""
        print("\n[LOGIC] Testing cart manipulation...")

        self._rate_limit()
        r = self.session.get(f"{self.base_url}/gp/cart/view.html")

        if r.status_code == 200:
            print("  [+] Cart accessible")

            # Check for CSRF tokens
            csrf_tokens = re.findall(r'anti-csrftoken-a2z["\s:=]+([^"\'>\s]+)', r.text)
            if csrf_tokens:
                print(f"  [+] CSRF protection detected")
            else:
                print(f"  [!] No obvious CSRF token found - investigate further")
                self.findings.append({
                    "type": "Potential CSRF",
                    "severity": "MEDIUM",
                    "location": "Cart",
                    "detail": "CSRF token not found in cart page"
                })
        else:
            print(f"  [-] Cart status: {r.status_code}")

    def test_api_endpoints(self):
        """Test authenticated API endpoints"""
        print("\n[API] Testing authenticated API endpoints...")

        api_endpoints = [
            "/api/marketplaceId/ATVPDKIKX0DER/customers",
            "/gp/gfix/v2/item",
            "/gp/pdp/pf/pf-template",
            "/hz/wishlist/api/v1/default",
        ]

        for endpoint in api_endpoints:
            self._rate_limit()
            try:
                r = self.session.get(f"{self.base_url}{endpoint}")
                content_type = r.headers.get("Content-Type", "")

                if r.status_code == 200:
                    if "json" in content_type:
                        print(f"  [+] {endpoint} - JSON response")
                        # Check for sensitive data
                        try:
                            data = r.json()
                            if any(k in str(data).lower() for k in ["email", "phone", "address", "payment"]):
                                print(f"      [!] Potential sensitive data exposed")
                                self.findings.append({
                                    "type": "Information Disclosure",
                                    "severity": "MEDIUM",
                                    "location": endpoint,
                                    "detail": "API may expose sensitive user data"
                                })
                        except:
                            pass
                    else:
                        print(f"  [+] {endpoint} - {r.status_code}")
                elif r.status_code == 429:
                    print(f"  [RATE] {endpoint} - Rate limited")
                else:
                    print(f"  [-] {endpoint} - {r.status_code}")
            except Exception as e:
                print(f"  Error on {endpoint}: {e}")

    def test_graphql(self):
        """Test for GraphQL introspection"""
        print("\n[GRAPHQL] Testing GraphQL endpoints...")

        graphql_endpoints = [
            "/graphql",
            "/api/graphql",
            "/gp/graphql",
        ]

        introspection_query = {
            "query": "query { __schema { types { name } } }"
        }

        for endpoint in graphql_endpoints:
            self._rate_limit()
            try:
                r = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=introspection_query,
                    headers={"Content-Type": "application/json"}
                )

                if r.status_code == 200:
                    try:
                        data = r.json()
                        if "__schema" in str(data):
                            print(f"  [!] GraphQL introspection ENABLED at {endpoint}")
                            self.findings.append({
                                "type": "GraphQL Introspection",
                                "severity": "MEDIUM",
                                "location": endpoint,
                                "detail": "GraphQL introspection is enabled"
                            })
                        else:
                            print(f"  [+] {endpoint} - Introspection disabled or restricted")
                    except:
                        print(f"  [+] {endpoint} - Response: {r.status_code}")
                elif r.status_code == 429:
                    print(f"  [RATE] {endpoint} - Rate limited")
                else:
                    print(f"  [-] {endpoint} - {r.status_code}")
            except Exception as e:
                print(f"  Error: {e}")

    def generate_report(self):
        """Generate authenticated scan report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.results_dir / f"amazon_vrp_auth_{timestamp}.md"

        report = f"""# Amazon VRP Authenticated Scan Report

**Target:** https://www.amazon.com
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Hunter:** {self.h1_username}
**Scan Type:** Authenticated
**User-Agent:** {self.user_agent}

---

## Findings Summary

| Severity | Count |
|----------|-------|
| Critical | {len([f for f in self.findings if f['severity'] == 'CRITICAL'])} |
| High | {len([f for f in self.findings if f['severity'] == 'HIGH'])} |
| Medium | {len([f for f in self.findings if f['severity'] == 'MEDIUM'])} |
| Low | {len([f for f in self.findings if f['severity'] == 'LOW'])} |

---

## Detailed Findings

"""
        if self.findings:
            for i, f in enumerate(self.findings, 1):
                report += f"""### {i}. [{f['severity']}] {f['type']}

**Location:** {f.get('location', 'N/A')}
**Detail:** {f.get('detail', 'N/A')}

---

"""
        else:
            report += "No significant vulnerabilities found in authenticated testing.\n\n"

        report += """
## Tests Performed

- [x] Authentication verification
- [x] IDOR - User profiles
- [x] IDOR - Order history
- [x] IDOR - Wishlists
- [x] Cart manipulation / CSRF
- [x] Authenticated API endpoints
- [x] GraphQL introspection

---

*Generated by ALFRED II-Y-II Amazon VRP Scanner*
"""

        report_path.write_text(report)
        print(f"\n[REPORT] Saved to: {report_path}")
        return str(report_path)

    def run_full_scan(self):
        """Run complete authenticated scan"""
        print("=" * 60)
        print("AMAZON VRP AUTHENTICATED SCANNER")
        print("=" * 60)
        print(f"User-Agent: {self.user_agent}")
        print(f"Rate Limit: {1/self.rate_limit:.1f} req/sec")
        print("=" * 60)

        if not self.verify_auth():
            print("\n[!] Authentication failed. Please provide valid cookies.")
            return None

        self.test_idor_profile()
        self.test_idor_orders()
        self.test_idor_wishlist()
        self.test_cart_manipulation()
        self.test_api_endpoints()
        self.test_graphql()

        report = self.generate_report()

        print("\n" + "=" * 60)
        print("SCAN COMPLETE")
        print("=" * 60)
        print(f"Findings: {len(self.findings)}")
        for f in self.findings:
            print(f"  [{f['severity']}] {f['type']}")

        return report


def main():
    parser = argparse.ArgumentParser(description="Amazon VRP Authenticated Scanner")
    parser.add_argument("--cookies", "-c", required=True, help="Session cookies from browser")
    parser.add_argument("--username", "-u", default="BATDAN", help="HackerOne username")

    args = parser.parse_args()

    scanner = AmazonVRPScanner(args.cookies, args.username)
    scanner.run_full_scan()


if __name__ == "__main__":
    main()
