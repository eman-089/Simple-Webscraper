"""
Simple Web Scraper MVP
Usage: python scraper.py <url> [options]
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "--break-system-packages", "-q"])
    import requests
    from bs4 import BeautifulSoup


def scrape(url: str, tag: str = None, class_name: str = None, extract_links: bool = False) -> dict:
    """
    Scrape a URL and return structured data.

    Args:
        url: Target URL to scrape
        tag: HTML tag to extract (e.g. 'h1', 'p', 'a')
        class_name: Filter by CSS class name
        extract_links: Whether to extract all links from the page

    Returns:
        dict with scraped data
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SimpleScraper/1.0)"
    }

    print(f"[*] Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "url": url,
        "status_code": response.status_code,
        "scraped_at": datetime.now().isoformat(),
        "title": soup.title.string.strip() if soup.title else None,
        "data": [],
        "links": [],
    }

    # Extract elements by tag / class
    if tag or class_name:
        kwargs = {}
        if class_name:
            kwargs["class_"] = class_name
        elements = soup.find_all(tag or True, **kwargs)
        result["data"] = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]
        print(f"[+] Found {len(result['data'])} element(s) matching the selector")
    else:
        # Default: grab all paragraph text
        result["data"] = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
        print(f"[+] Extracted {len(result['data'])} paragraph(s)")

    # Extract links
    if extract_links:
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("http"):
                links.add(href)
            elif href.startswith("/"):
                links.add(urljoin(base, href))
        result["links"] = sorted(links)
        print(f"[+] Found {len(result['links'])} unique link(s)")

    return result


def save_json(data: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✓] Saved JSON → {path}")


def save_csv(data: dict, path: str):
    rows = [{"url": data["url"], "scraped_at": data["scraped_at"], "content": item}
            for item in data["data"]]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "scraped_at", "content"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"[✓] Saved CSV  → {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Simple Web Scraper MVP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scraper.py https://example.com
  python scraper.py https://news.ycombinator.com --tag a --class titleline
  python scraper.py https://example.com --links --output results.json
  python scraper.py https://example.com --output data.csv
        """
    )
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--tag", help="HTML tag to extract (e.g. h1, p, a, li)")
    parser.add_argument("--class", dest="class_name", help="CSS class name to filter by")
    parser.add_argument("--links", action="store_true", help="Extract all hyperlinks")
    parser.add_argument("--output", "-o", help="Output file (.json or .csv). Defaults to stdout.")

    args = parser.parse_args()

    try:
        result = scrape(
            url=args.url,
            tag=args.tag,
            class_name=args.class_name,
            extract_links=args.links,
        )

        if args.output:
            if args.output.endswith(".csv"):
                save_csv(result, args.output)
            else:
                save_json(result, args.output)
        else:
            # Pretty print to stdout
            print("\n── Result ──────────────────────────────")
            print(f"Title : {result['title']}")
            print(f"Items : {len(result['data'])}")
            if result["data"]:
                print("\nContent preview (first 5):")
                for item in result["data"][:5]:
                    print(f"  • {item[:120]}")
            if result["links"]:
                print(f"\nLinks ({len(result['links'])} total, first 5):")
                for link in result["links"][:5]:
                    print(f"  → {link}")
            print()

    except requests.exceptions.RequestException as e:
        print(f"[✗] Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[✗] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
