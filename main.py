import requests
import re
import json
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class DarkWebCrawler:
    def __init__(self):
        self.session = requests.Session()
        
        # --- CONFIGURATION ---
        self.tor_port = 9150  # 9150 for Browser, 9050 for Service
        self.deep_crawl_limit = 3  # Max pages to visit per engine (Speed vs Depth)
        self.request_timeout = 45  # Seconds to wait for a page
        
        # 1. ROTATING USER AGENTS (Stealth)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/115.0'
        ]

        # 2. KEYWORD FILTERING (Relevance)
        # Skip results if Title/Snippet contains these
        self.negative_keywords = [
            "porn", "xxx", "sex", "erotic", "adult", "casino", 
            "drug", "cannabis", "cocaine", "hitman", "weapon", "gun"
        ]

        # 3. ARTIFACT EXTRACTION (Data Mining)
        self.patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "btc_address": r'\b(bc1|[13])[a-zA-Z0-9]{25,39}\b',
            "onion_link": r'(http[s]?://[a-z2-7]{16,56}\.onion)',
            "pgp_key": r'-----BEGIN PGP PUBLIC KEY BLOCK-----'
        }

        # PROXY SETUP
        self.proxies = {
            'http': f'socks5h://127.0.0.1:{self.tor_port}',
            'https': f'socks5h://127.0.0.1:{self.tor_port}'
        }
        self.session.proxies.update(self.proxies)
        
        self.findings = []
        self.visited_links = set()

    def _get_random_header(self):
        """Returns headers with a random User-Agent to avoid fingerprinting."""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def verify_tor(self):
        """Checks if traffic is routing through Tor."""
        print("[*] Verifying Tor Connection...")
        try:
            r = self.session.get("https://check.torproject.org/api/ip", headers=self._get_random_header(), timeout=20)
            if r.json().get("IsTor"):
                print(f"[+] Connected to Tor! (IP: {r.json().get('IP')})")
                return True
        except Exception as e:
            print(f"[!] Tor Connection Failed: {e}")
        return False

    def _is_safe(self, text):
        """Returns False if text contains negative keywords."""
        text = text.lower()
        for bad_word in self.negative_keywords:
            if bad_word in text:
                return False
        return True

    def _extract_artifacts(self, text):
        """Scans text for Emails, BTC addresses, etc."""
        artifacts = {}
        for key, pattern in self.patterns.items():
            matches = list(set(re.findall(pattern, text)))
            if matches:
                artifacts[key] = matches
        return artifacts

    def deep_crawl_page(self, url):
        """5. CRAWL DEPTH: Visits the actual page to scrape hidden data."""
        if url in self.visited_links:
            return {}
        
        print(f"    --> Deep Crawling: {url[:40]}...")
        self.visited_links.add(url)
        
        try:
            resp = self.session.get(url, headers=self._get_random_header(), timeout=self.request_timeout)
            if resp.status_code == 200:
                # Scan the internal HTML for artifacts
                return self._extract_artifacts(resp.text)
        except:
            print("    [!] Deep crawl timed out or failed.")
        
        return {}

    # --- ENGINE 1: TORCH ---
    def search_torch(self, query):
        base_url = "http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion/search"
        print(f"[*] Querying Engine: TORCH for '{query}'...")
        
        try:
            resp = self.session.get(base_url, params={'query': query, 'action': 'search'}, headers=self._get_random_header(), timeout=60)
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('h5') # Torch headers are h5
            
            count = 0
            for h5 in results:
                link_tag = h5.find('a')
                if not link_tag: continue
                
                url = link_tag['href']
                title = link_tag.get_text(strip=True)
                
                if not self._is_safe(title):
                    continue

                # Prepare Result Object
                result_data = {
                    "engine": "Torch",
                    "title": title,
                    "url": url,
                    "artifacts": {}
                }

                # Trigger Deep Crawl if within limit
                if count < self.deep_crawl_limit:
                    extracted = self.deep_crawl_page(url)
                    if extracted:
                        result_data["artifacts"] = extracted
                
                self.findings.append(result_data)
                count += 1
                
            print(f"[+] Torch found {count} relevant results.")

        except Exception as e:
            print(f"[!] Torch failed: {e}")

    # --- ENGINE 2: AHMIA ---
    def search_ahmia(self, query):
        # Using Public Mirror for stability, routed through Tor for privacy
        base_url = "https://ahmia.fi/search/"
        print(f"[*] Querying Engine: AHMIA for '{query}'...")
        
        try:
            resp = self.session.get(base_url, params={'q': query}, headers=self._get_random_header(), timeout=30)
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('li', class_='result')
            
            count = 0
            for res in results:
                try:
                    title = res.find('h4').get_text(strip=True)
                    url = res.find('a')['href']
                    snippet = res.find('p').get_text(strip=True) if res.find('p') else ""
                    
                    full_text = f"{title} {snippet}"
                    
                    if not self._is_safe(full_text):
                        continue

                    result_data = {
                        "engine": "Ahmia",
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "artifacts": self._extract_artifacts(full_text) # Check snippet first
                    }
                    
                    # Deep Crawl
                    if count < self.deep_crawl_limit:
                        deep_data = self.deep_crawl_page(url)
                        # Merge deep findings with snippet findings
                        for k, v in deep_data.items():
                            if k in result_data["artifacts"]:
                                result_data["artifacts"][k].extend(v)
                            else:
                                result_data["artifacts"][k] = v

                    self.findings.append(result_data)
                    count += 1
                except: continue
                
            print(f"[+] Ahmia found {count} relevant results.")

        except Exception as e:
            print(f"[!] Ahmia failed: {e}")

    def run(self, query):
        if not self.verify_tor():
            return

        print(f"[*] Starting Multi-Engine Crawl for: {query}")
        print("[-] Note: Deep crawling is enabled. This will take time.")
        
        # 4. MULTI-ENGINE EXECUTION
        self.search_torch(query)
        self.search_ahmia(query)
        
        self.save_report()

    def save_report(self):
        filename = "osint_report.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.findings, f, indent=4)
            print(f"[*] Crawl finished. Saved {len(self.findings)} findings to {filename}")
        except IOError as e:
            print(f"[!] Error saving file: {e}")

if __name__ == "__main__":
    crawler = DarkWebCrawler()
    
    # Simple CLI
    target = input("Enter target (Email/User/Name): ").strip()
    if target:
        crawler.run(target)
    else:
        print("[!] Target cannot be empty.")