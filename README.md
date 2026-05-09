# Simple Web Scraper MVP

A clean, no-frills Python web scraper that extracts text content and links from any public webpage.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Scrape paragraphs from a page (default)
python scraper.py https://example.com

# Extract specific HTML tags
python scraper.py https://example.com --tag h2

# Filter by CSS class
python scraper.py https://news.ycombinator.com --tag a --class titleline

# Extract all links
python scraper.py https://example.com --links

# Save to JSON
python scraper.py https://example.com --output results.json

# Save to CSV
python scraper.py https://example.com --tag p --output results.csv
```

## Options

| Flag | Description |
|------|-------------|
| `--tag` | HTML tag to extract (`h1`, `p`, `a`, `li`, etc.) |
| `--class` | CSS class name to filter by |
| `--links` | Extract all hyperlinks from the page |
| `--output` / `-o` | Save to `.json` or `.csv` file |

## Output Format (JSON)

```json
{
  "url": "https://example.com",
  "status_code": 200,
  "scraped_at": "2024-01-15T10:30:00",
  "title": "Page Title",
  "data": ["text item 1", "text item 2"],
  "links": ["https://...", "https://..."]
}
```
