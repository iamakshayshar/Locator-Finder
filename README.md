# Website Crawler for Automation Testers

A powerful Python utility that crawls websites and generates unique, reliable locators (XPath, CSS selectors, and other strategies) for automation testing. Designed for QA engineers and automation specialists who need to quickly generate element locators for test automation frameworks like Selenium, Cypress, and Playwright.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Output Formats](#output-formats)
- [Examples](#examples)
- [Testing](#testing)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

### Core Capabilities
- **Multi-Strategy Locator Generation**
  - XPath expressions (absolute and attribute-based)
  - CSS selectors with class and ID targeting
  - Element ID, name, and data-testid locators
  - Aria-label and text-based locators
  - Intelligent fallback strategies

- **Smart Web Crawling**
  - Selenium-powered dynamic content support
  - Recursive page crawling with depth control
  - Domain-aware URL filtering
  - Parallel element extraction
  - Automatic browser driver management
  - **Authenticated access** - Login automation and session management
  - **Cookie reuse** - Save and restore sessions for faster crawling

- **Multi-Format Export**
  - CSV with detailed element information
  - JSON with metadata and recommendations
  - Excel workbooks with formatted columns
  - Python code for direct test framework integration
  - Structured summary reports

- **Quality Assurance**
  - Element uniqueness validation
  - Duplicate element detection and filtering
  - Implicit element visibility checks
  - Locator syntax validation
  - Comprehensive error handling

- **Developer-Friendly**
  - Simple command-line interface
  - Configurable via YAML
  - Extensive logging and debugging
  - Unit and integration tests included
  - Easy Python API integration

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome/Chromium browser (for Selenium)
- pip package manager

### Step 1: Clone or Download
```bash
git clone https://github.com/yourusername/Website-Crawler.git
cd Website-Crawler
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python -m src.cli --help
```

## Quick Start

### Basic Usage
```bash
# Crawl a website and export locators as CSV
python -m src.cli --url "https://example.com"
```

### With Options
```bash
# Crawl with depth 2 and export as JSON
python -m src.cli \
  --url "https://example.com" \
  --depth 2 \
  --output locators.json \
  --export json
```

### Using Python API
```python
from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

# Initialize components
crawler = WebCrawler(headless=True)
generator = LocatorGenerator(crawler.driver)
exporter = Exporter(output_dir="output")

# Crawl page
results = crawler.crawl_page("https://example.com")

# Generate locators
locators_data = []
for element in results["elements"]:
    locators = generator.generate_locators(element)
    locators_data.append(locators)

# Export
exporter.export_to_csv(locators_data, "locators.csv")

# Cleanup
crawler.close()
```

## Usage

### Command-Line Interface

```bash
python -m src.cli [OPTIONS]
```

#### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--url` | `-u` | str | Required | URL to crawl |
| `--depth` | `-d` | int | 1 | Maximum crawl depth |
| `--max-pages` | `-m` | int | 50 | Maximum pages to crawl |
| `--output` | `-o` | str | output/locators.csv | Output file path |
| `--export` | `-e` | str... | csv | Export formats (csv, json, excel, python, all) |
| `--headless` | | flag | True | Run browser in headless mode |
| `--no-headless` | | flag | - | Run browser with GUI |
| `--timeout` | `-t` | int | 10 | Request timeout (seconds) |
| `--implicit-wait` | | int | 5 | Implicit wait time (seconds) |
| `--validate` | | flag | False | Validate locator uniqueness |
| `--remove-duplicates` | | flag | False | Remove duplicate elements |
| `--interactive` | `-i` | flag | False | **Interactive mode - capture locators as you navigate** |
| `--verbose` | `-v` | flag | False | Verbose output |

### Interactive Mode

**Interactive Mode** is a powerful feature that allows you to manually navigate a website while the tool automatically captures locators for each page state. This is perfect when you want to test dynamic pages, interactive workflows, or need to validate locators as you use the application.

#### How It Works

1. Start the crawler in interactive mode
2. Browser opens in normal (non-headless) mode with your site loaded
3. **You navigate freely** - click links, fill forms, interact with the page
4. **Tool monitors automatically:**
   - DOM changes are detected
   - Each page state is captured with a unique name (e.g., `home_page`, `login_page`, `dashboard_page`)
   - All locators on that page are generated automatically
5. **Page names are auto-generated** based on:
   - Page title if available
   - URL slug as fallback
6. When you're done, **close the browser window** to export results
7. Locators are exported per-page in your chosen formats

#### Usage

```bash
# Interactive mode - just add the --interactive flag
python -m src.cli --url "https://example.com" --interactive --export locators json csv
```

#### Interactive Mode Example

```bash
# Start interactive mode at login page
python -m src.cli \
  --url "https://app.example.com/login" \
  --interactive \
  --no-headless \
  --export locators

# What happens:
# 1. Browser opens at login page
# 2. Tool captures: login_page (with username field, password field, login button, etc.)
# 3. You fill credentials and click login
# 4. Tool detects page change and captures: dashboard_page (with navbar, menu items, etc.)
# 5. You click around, perform actions
# 6. Tool captures new states when DOM changes: filter_results_page, etc.
# 7. Close browser when done
# 8. All pages exported to output/ folder

# Output files:
# - login_page_locators_TIMESTAMP.txt
# - dashboard_page_locators_TIMESTAMP.txt
# - filter_results_page_locators_TIMESTAMP.txt
# - interactive_pages_TIMESTAMP.json
# - interactive_pages_TIMESTAMP.csv
```

#### Key Features of Interactive Mode

✅ **Manual Navigation** - You control what pages to test
✅ **Automatic Detection** - DOM changes trigger captures
✅ **Per-Page Naming** - Each page stored separately
✅ **No Login Configuration** - Unlike standard mode, no credentials needed!
✅ **Dynamic Content** - Captures locators after your actions
✅ **Multi-Format Export** - Export as text, JSON, CSV, Excel, Python

#### Common Interactive Mode Scenarios

**Scenario 1: Testing a Login Flow**
```bash
python -m src.cli \
  --url "https://myapp.com/login" \
  --interactive \
  --no-headless \
  --export locators json

# 1. Login page loads
# 2. You enter credentials manually
# 3. After login, dashboard appears
# 4. Tool captures both pages
# 5. Close browser to finish
```

**Scenario 2: Testing Dynamic Interactions**
```bash
python -m src.cli \
  --url "https://myapp.com/dashboard" \
  --interactive \
  --export locators

# 1. Dashboard page captured
# 2. You click "Show Filters"
# 3. Filter panel appears, automatically captured
# 4. You apply a filter
# 5. Results update, automatically captured
# 6. Close browser when done
```

**Scenario 3: Multi-Step Workflow Testing**
```bash
python -m src.cli \
  --url "https://myapp.com/order" \
  --interactive \
  --export json csv

# Flow captured:
# - order_page (main form)
# - shipping_page (after clicking Next)
# - payment_page (after shipping details)  
# - confirmation_page (after payment)
```

### Examples

#### Example 1: Basic Single-Page Crawl
```bash
python -m src.cli --url "https://example.com"
```
**Output:** CSV file with all locators found

#### Example 2: Deep Recursive Crawl
```bash
python -m src.cli \
  --url "https://example.com" \
  --depth 3 \
  --max-pages 100 \
  --export csv json
```
**Output:** Multiple formats covering entire site structure

#### Example 3: Testing Configuration
```bash
python -m src.cli \
  --url "https://staging.example.com" \
  --output test_locators.json \
  --export json \
  --headless \
  --timeout 15 \
  --remove-duplicates \
  --verbose
```

#### Example 4: Export as Python Code
```bash
python -m src.cli \
  --url "https://example.com" \
  --output locators \
  --export python
```
**Output:** Python file with LOCATORS dictionary for direct use in tests

## Authentication

### Overview
For crawling protected application pages that require login, the crawler supports multiple authentication methods:

1. **Automated Login** - Provide credentials to auto-login before crawling
2. **Cookie Reuse** - Save login cookies and reuse them for faster crawling
3. **Custom Form Selectors** - Support for any login form layout

### Authentication Methods

#### Method 1: Automated Login (with credentials)
Automatically logs in using provided username/password:

```bash
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "user@example.com" \
  --password "mypassword" \
  --username-field "input[name='email']" \
  --password-field "input[type='password']" \
  --login-button "button.login-btn" \
  --wait-for ".dashboard"
```

**Key Parameters:**
- `--login-url` - URL of the login page
- `--username` - Username or email for login
- `--password` - Password (use env vars for security!)
- `--username-field` - CSS selector for username input
- `--password-field` - CSS selector for password input
- `--login-button` - CSS selector for login/submit button
- `--wait-for` - CSS selector to wait for after successful login

#### Method 2: Cookie Reuse (fastest!)
Save login cookies once, then reuse them for subsequent crawls:

**Step 1: First run - save cookies**
```bash
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "user@example.com" \
  --password "mypassword" \
  --wait-for ".dashboard" \
  --save-cookies cookies.json
```

**Step 2: Subsequent runs - reuse cookies**
```bash
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --cookies cookies.json \
  --export locators
```

Much faster - no need to crawl the login form!

#### Method 3: Configuration File
Define auth settings in `config/config.yaml`:

```yaml
authentication:
  enabled: true
  login_url: "https://app.example.com/login"
  username: "user@example.com"
  password: "mypassword"
  username_field: "input[name='email']"
  password_field: "input[name='password']"
  login_button: "button.submit"
  wait_for_element: ".dashboard"
  save_cookies: true
  save_cookies_file: "cookies.json"
```

### Finding the Right Selectors

To find CSS selectors for your login form:

1. **Open the login page in browser**
   ```bash
   python -m src.cli --url "https://app.example.com/login" --no-headless
   ```

2. **Inspect elements**
   - Right-click on username field → Inspect → Find CSS class/id/name
   - Right-click on password field → Inspect → Find CSS class/id/name
   - Right-click on login button → Inspect → Find CSS class/id/name

3. **Common patterns:**
   ```
   input[name='username']          # by name attribute
   input[name='email']             # email field
   input[id='password']            # by id attribute
   input.form-control             # by class name
   button[type='submit']           # submit button
   button.btn-login                # by class name
   input[aria-label='Password']    # by aria-label
   ```

### Security Best Practices

**Never hardcode credentials!** Use environment variables:

```bash
# Set environment variables
export APP_USERNAME="user@example.com"
export APP_PASSWORD="mypassword"

# Use in command (bash)
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "$APP_USERNAME" \
  --password "$APP_PASSWORD" \
  --wait-for ".dashboard"
```

Or in Python:
```python
import os
from src.cli import CrawlerCLI

cli = CrawlerCLI()
args = type('obj', (object,), {
    'url': "https://app.example.com/dashboard",
    'login_url': "https://app.example.com/login",
    'username': os.getenv('APP_USERNAME'),
    'password': os.getenv('APP_PASSWORD'),
    'wait_for': ".dashboard",
    'cookies': None,
    'save_cookies': None,
})()

cli._execute_crawl(args)
```

### Testing Your Login Flow

Before full crawl, test the login flow:

```bash
# Verbose mode shows login steps
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "testuser" \
  --password "testpass" \
  --wait-for ".dashboard" \
  --no-headless \
  --verbose
```

## Configuration

### YAML Configuration File
Edit `config/config.yaml` to customize crawler behavior:

```yaml
crawler:
  element_tags:
    - button
    - a
    - input
    - select
  timeout: 10
  user_agent: "Mozilla/5.0..."

selenium:
  browser: chrome
  headless: true
  implicit_wait: 5
  page_load_timeout: 20

locator:
  types:
    - xpath
    - css_selector
    - id
  validate_uniqueness: true

export:
  default_format: csv
  columns:
    - tag_name
    - element_text
    - xpath
    - css_selector
```

## Output Formats

### CSV Format
Simple, spreadsheet-friendly format:
```
Tag,Text,Type,ID,Name,Data-TestID,XPath,CSS Selector
button,Submit Form,submit,submit_btn,submit,submit-button,//button[@id='submit_btn'],#submit_btn
a,Sign In,,sign_in_link,,,,a.nav-link
```

### JSON Format
Structured format with metadata:
```json
{
  "metadata": {
    "exported_at": "2026-03-27T10:30:00",
    "total_elements": 2,
    "format_version": "1.0"
  },
  "locators": [
    {
      "element_info": {
        "tag_name": "button",
        "element_text": "Submit Form",
        "element_id": "submit_btn"
      },
      "locators": {
        "id": "submit_btn",
        "xpath": "//button[@id='submit_btn']",
        "css_selector": "#submit_btn"
      }
    }
  ]
}
```

### Excel Format
Formatted spreadsheet with:
- Header row with blue background
- Frozen panes for easy scrolling
- Auto-adjusted column widths
- Wrapped text in cells

### Python Format
Direct integration with test frameworks:
```python
LOCATORS = {
    "button_0": {
        # Submit Form
        'tag': 'button',
        'id': 'submit_btn',
        'xpath': "//button[@id='submit_btn']",
        'css_selector': '#submit_btn',
    }
}
```

### Locators Text Format (NEW)
Simple, easy-to-read text format - **Perfect for quick reference!**
```
# Locators - Web Elements
# Generated: 2026-03-27T10:30:00
# Format: element_name = locator_value

submit_btn = //button[@id='submit_btn']
sign_in_link = //a[text()='Sign In']
username_field = //input[@name='username']
```

**Features:**
- One locator per line: `element_name = locator_value`
- Automatically picks the best locators (priority: ID > data-testid > XPath > CSS)
- Clear header comments
- Perfect for copying into test code
- Minimal file size
- Human-readable and easy to reference

## Examples

### Example 1: E-commerce Product Page
```bash
python -m src.cli \
  --url "https://example-shop.com/products" \
  --export csv json \
  --output product_locators
```

### Example 2: Multi-Page Form Application
```bash
python -m src.cli \
  --url "https://forms.example.com/register" \
  --depth 2 \
  --max-pages 20 \
  --remove-duplicates \
  --export excel python
```

### Example 3: Quick Locator Reference
```bash
python -m src.cli \
  --url "https://example.com" \
  --export locators
```
Output file: `locators_locators.txt` - Simple format for quick reference

### Example 4: All Export Formats
```bash
python -m src.cli \
  --url "https://staging.example.com" \
  --export all \
  --output staging_locators
```
Exports: CSV, JSON, Excel, Python, and Locators text formats

### Example 5: Python Script Usage
```python
from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

# Use context manager for automatic cleanup
with WebCrawler(headless=True) as crawler:
    generator = LocatorGenerator(crawler.driver)
    exporter = Exporter()
    
    # Crawl
    results = crawler.crawl_page("https://example.com")
    elements = results.get("elements", [])
    
    # Process
    locators_data = []
    for element in elements:
        locators = generator.generate_locators(element)
        locators_data.append(locators)
    
    # Export
    csv_file = exporter.export_to_csv(locators_data)
    json_file = exporter.export_to_json(locators_data)
    
    print(f"CSV: {csv_file}")
    print(f"JSON: {json_file}")
```

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Module
```bash
pytest tests/test_locator.py -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Test Modules
- `test_crawler.py` - Web crawling functionality
- `test_locator.py` - Locator generation strategies
- `test_exporter.py` - Export functionality for all formats

## Architecture

### Project Structure
```
Website-Crawler/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Module entry point
│   ├── cli.py               # Command-line interface (350+ lines)
│   ├── crawler.py           # Web crawling engine (250+ lines)
│   ├── locator_generator.py # Locator strategy engine (300+ lines)
│   ├── exporter.py          # Multi-format export (350+ lines)
│   └── validator.py         # Element and locator validation (100+ lines)
├── config/
│   └── config.yaml          # Configuration file
├── tests/
│   ├── __init__.py
│   ├── test_crawler.py      # Crawler unit tests
│   ├── test_locator.py      # Locator generation tests
│   └── test_exporter.py     # Export functionality tests
├── output/                  # Generated files directory
├── logs/                    # Log files
├── requirements.txt         # Project dependencies
├── main.py                  # Direct execution entry point
├── README.md               # This file
├── .gitignore             # Git ignore rules
└── .github/
    └── copilot-instructions.md  # GitHub Copilot instructions
```

### Core Classes

#### WebCrawler
Main crawling engine with:
- Dynamic content support via Selenium
- Multi-domain URL filtering
- Automatic element extraction
- Recursive crawling capabilities

#### LocatorGenerator
Multi-strategy locator generation:
- ID-based locators (highest reliability)
- XPath expressions (various strategies)
- CSS selectors (modern approach)
- Text-based locators
- Data attribute locators

#### Exporter
Multi-format export support:
- CSV (spreadsheet-friendly)
- JSON (structured data)
- Excel (formatted workbooks)
- Python (code integration)
- Text summaries

#### ElementValidator
Quality assurance:
- Element validation
- Locator syntax checking
- Duplicate detection
- Similarity comparison

### Data Flow
```
URL Input → WebCrawler → HTML Elements → LocatorGenerator → 
Locator Strategies → Exporter → Output File(s)
```

## API Reference

### WebCrawler

```python
class WebCrawler:
    def __init__(self, headless=True, timeout=10, implicit_wait=5):
        """Initialize crawler"""
        
    def crawl_page(self, url: str) -> Dict:
        """Crawl single page and extract elements"""
        
    def crawl_recursive(self, start_url: str, max_depth=2, max_pages=50) -> List[Dict]:
        """Recursively crawl pages up to max depth"""
        
    def close(self):
        """Close WebDriver"""
```

### LocatorGenerator

```python
class LocatorGenerator:
    def __init__(self, driver=None):
        """Initialize generator"""
        
    def generate_locators(self, element_info: Dict) -> Dict:
        """Generate multiple locator strategies"""
        
    def create_locator_strategy(self, element_info: Dict) -> Dict:
        """Create comprehensive locator strategy"""
        
    def validate_locator(self, locator: str, locator_type: str) -> bool:
        """Validate locator uniqueness"""
```

### Exporter

```python
class Exporter:
    def __init__(self, output_dir: str = "output"):
        """Initialize exporter"""
        
    def export_to_csv(self, locators_data: List[Dict], filename: str = None) -> str:
        """Export to CSV"""
        
    def export_to_json(self, locators_data: List[Dict], filename: str = None) -> str:
        """Export to JSON"""
        
    def export_to_excel(self, locators_data: List[Dict], filename: str = None) -> str:
        """Export to Excel"""
        
    def export_to_python(self, locators_data: List[Dict], filename: str = None) -> str:
        """Export as Python code"""
```

## Troubleshooting

### Issue: Chrome Driver Not Found
**Solution:**
```bash
pip install webdriver-manager
```
The project auto-downloads the correct ChromeDriver version.

### Issue: Timeout During Crawl
**Solution:** Increase timeout value:
```bash
python -m src.cli --url "https://example.com" --timeout 30
```

### Issue: Too Many Duplicate Elements
**Solution:** Use the duplicate filter:
```bash
python -m src.cli --url "https://example.com" --remove-duplicates
```

### Issue: JavaScript Content Not Loading
**Reason:** Dynamic content requires Selenium (default enabled)
**Solution:** Ensure headless mode is compatible with your Chrome version

### Issue: Locators Not Unique
**Solution:** Use `--validate` flag and review recommendations:
```bash
python -m src.cli --url "https://example.com" --validate
```

## Contributing

Contributions are welcome! Follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Run tests: `pytest tests/`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature/your-feature`
7. Submit pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Project Issues](https://github.com/yourusername/Website-Crawler/issues)
- Documentation: See README.md and inline code comments

## Changelog

### Version 1.0.0 (2026-03-27)
- Initial release
- Web crawling with Selenium
- Multi-strategy locator generation
- Export to CSV, JSON, Excel, Python
- Comprehensive testing suite
- Full documentation

---

**Happy Test Automation! 🚀**
