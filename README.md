# Abyss 

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Tor](https://img.shields.io/badge/Network-Tor-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> "If you gaze long enough into an abyss, the abyss will gaze back into you."

**Abyss** is a defensive Open Source Intelligence (OSINT) tool designed to monitor the Tor network for data leaks. This script routes traffic through the Tor network to query onion search engines (Torch, Ahmia), identifies potential matches for specific targets (emails, usernames, domains), and extracts high-value artifacts using Regex.

> **⚠️ Disclaimer:** This tool is intended for **educational and defensive security research purposes only** (e.g., monitoring your own data exposure). The author is not responsible for any misuse of this software.

## 🚀 Features

* **Multi-Engine Support:** Automatically queries **Torch** and falls back to **Ahmia** if primary engines fail.
* **Tor Routing:** All traffic is routed through the Tor SOCKS5 proxy to maintain anonymity.
* **Artifact Mining:** Automatically extracts:
    * 📧 Email Addresses
    * ₿ Bitcoin (BTC) Addresses
    * 🧅 Onion V3 Links
    * 🔑 PGP Keys
* **Deep Crawl:** Visits top search results to scan internal HTML for hidden data (not just snippets).
* **Stealth Mode:** Rotates `User-Agent` headers for every request to avoid fingerprinting.
* **Smart Filtering:** Filters out irrelevant or NSFW results using a customizable keyword blocklist.

## 🛠️ Prerequisites

1.  **Python 3.x**
2.  **Tor Browser** (running in the background)
    * *Note:* The script defaults to port `9150` (Tor Browser). If using the standalone Tor Service, change the port in `main.py` to `9050`.

## 📦 Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/saltfry/Abyss.git](https://github.com/saltfry/Abyss.git)
    cd Defensive-OSINT-Monitor
    ```

2.  **Install Dependencies**
    ```bash
    pip install requests[socks] beautifulsoup4
    ```

3.  **Start Tor**
    * Open **Tor Browser** and minimize it.
    * Wait until it connects to the network.

## 💻 Usage

Run the main script from your terminal:

```bash
python main.py

```

**Enter your target when prompted:**

* **Email:** `target@example.com`
* **Username:** `admin_user`
* **Keyword:** `company_name`

### Example Output

```text
[*] Verifying Tor Connection...
[+] Connected to Tor! (IP: 192.42.x.x)
[*] Starting Multi-Engine Crawl for: bitcoin
[*] Querying Engine: TORCH for 'bitcoin'...
    --> Deep Crawling: [http://example.onion/](http://example.onion/)...
[+] Torch found 12 relevant results.
[*] Crawl finished. Saved 12 findings to osint_report.json

```

## 📂 Output Data

Results are saved to `osint_report.json`.

```json
[
    {
        "engine": "Torch",
        "title": "Donate to our Project",
        "url": "[http://sampleaddress.onion](http://sampleaddress.onion)",
        "artifacts": {
            "btc_address": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"],
            "email": ["contact@secure-mail.onion"]
        }
    }
]

```

## ⚙️ Configuration

You can customize the crawler behavior in the `__init__` section of `main.py`:

* **`self.tor_port`**: Change to `9050` if using Linux Tor service.
* **`self.deep_crawl_limit`**: Increase to crawl more pages (slower but deeper).
* **`self.negative_keywords`**: Add words to this list to filter out junk results.

## 🤝 Contributing

Contributions are welcome! Please ensure any pull requests adhere to the defensive/educational nature of this tool.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) file for details.
