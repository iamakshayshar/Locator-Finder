# Website Crawler for Automation Testers

This Python project crawls websites and generates unique locators (XPath and CSS selectors) for automation testing.

## Project Overview

The project provides:
- **Web Crawling**: Navigate and parse website pages using Selenium and BeautifulSoup
- **DOM Analysis**: Identify interactive elements (buttons, links, inputs, etc.)
- **Locator Generation**: Generate unique XPath and CSS selectors with uniqueness validation
- **Multi-format Export**: Save locators to CSV, JSON, Excel, Python, or simple text formats
- **CLI Interface**: Easy-to-use command-line interface

## Key Features

- Automatic page crawling with depth control
- Dynamic content support via Selenium WebDriver
- **Authenticated access** - Automated login and session management for protected pages
- **Cookie reuse** - Save and restore login sessions for faster crawling
- XPath and CSS selector generation
- Locator uniqueness validation
- Batch processing of multiple URLs
- Comprehensive logging and error handling
- Multiple export formats (CSV, JSON, Excel, Python, **Locators Text**)

## Setup Instructions

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the crawler:
   ```bash
   python -m src.cli --url "https://example.com" --output locators.csv
   ```

## Project Structure

```
Website-Crawler/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Module entry point
│   ├── cli.py               # Command-line interface
│   ├── crawler.py           # Web crawling logic
│   ├── locator_generator.py # Locator generation
│   ├── exporter.py          # CSV/JSON/Excel/Locators export
│   └── validator.py         # Element validation
├── config/
│   └── config.yaml          # Configuration file
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py      # Crawler tests
│   ├── test_locator.py      # Locator generator tests
│   └── test_exporter.py     # Exporter tests
├── output/                  # Generated locator files
├── logs/                    # Log files
├── venv/                    # Virtual environment
├── requirements.txt         # Project dependencies
├── README.md               # Full documentation
├── main.py                 # Direct execution entry point
└── .gitignore             # Git ignore rules
```

## Usage Examples

### Basic crawling:
```bash
python -m src.cli --url "https://example.com"
```

### Advanced crawling with multiple formats:
```bash
python -m src.cli \
  --url "https://example.com" \
  --depth 2 \
  --output locators \
  --export csv json excel python locators \
  --remove-duplicates
```

### Quick locator reference (simple text format):
```bash
python -m src.cli --url "https://example.com" --export locators
```
Creates a simple text file: `login_btn = //button[@id='login']`

### Crawl authenticated applications:
```bash
# Login and crawl protected pages
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "user@example.com" \
  --password "password123" \
  --username-field "input[name='email']" \
  --password-field "input[type='password']" \
  --login-button "button.login-btn" \
  --wait-for ".dashboard" \
  --export locators

# Reuse saved session cookies (much faster!)
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --cookies cookies.json \
  --export locators
```

### Run tests:
```bash
source venv/bin/activate
python -m unittest discover -s tests -p "test_*.py" -v
```

## Dependencies

All dependencies are listed in requirements.txt:
- selenium: Web browser automation
- beautifulsoup4: HTML parsing
- requests: HTTP requests
- pandas: Data manipulation
- openpyxl: Excel export
- pyyaml: Configuration management
- lxml: XML/HTML processing
- webdriver-manager: Automatic driver management
- pytest: Testing framework

## Development

Code follows PEP 8 style guidelines. All tests are in the `tests/` folder.

## Project Status

✅ Project successfully created and validated
✅ All 21 unit tests passing
✅ Virtual environment configured
✅ CLI fully functional
✅ All export formats working (CSV, JSON, Excel, Python, Locators Text)
✅ Simple text locator format added
✅ Documentation complete
