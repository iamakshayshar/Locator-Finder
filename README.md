# Locator-Finder - Interactive Locator Generator

A Python tool that opens a browser in interactive mode, lets you navigate a website, and automatically captures element locators (XPath/CSS) for each page you visit. Designed for QA engineers and automation testers who need to quickly generate locators for frameworks like Selenium, Cypress, and Playwright.

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- **Interactive Mode** - Browser opens in GUI mode; you navigate the site, the tool captures locators automatically
- **Automatic Page Detection** - DOM changes are detected and each page state is captured with a unique name
- **Multi-Strategy Locators** - XPath, CSS selectors, ID, name, data-testid, and aria-label locators
- **Simple Text Output** - Locators exported in easy-to-use `element_name = locator` format
- **Smart Naming** - Elements are named using ID, data-testid, name attribute, or generated from tag + text
- **Automatic Driver Management** - Chrome WebDriver is downloaded and managed automatically

## Installation

### Prerequisites
- Python 3.8+
- Chrome/Chromium browser

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/Website-Crawler.git
cd Website-Crawler

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Verify Installation
```bash
python -m src.cli --help
```

## Quick Start

```bash
python -m src.cli --url "https://example.com"
```

This will:
1. Open Chrome browser at the given URL
2. Monitor for page changes as you navigate
3. Capture all interactive elements on each page
4. Export locators to a `.txt` file when you close the browser

## How It Works

1. **Start** - Run the command with your target URL
2. **Browse** - Interact with the website normally (click links, fill forms, navigate pages)
3. **Auto-Capture** - The tool detects DOM changes and captures elements for each page state
4. **Finish** - Close the browser window (or press Ctrl+C) to export all captured locators
5. **Output** - A `.txt` file is generated with locators in `element_name = locator` format

## Usage

### Basic Usage
```bash
python -m src.cli --url "https://example.com"
```

### With Custom Output Path
```bash
python -m src.cli --url "https://example.com" --output output/my_locators.txt
```

### With Increased Timeout
```bash
python -m src.cli --url "https://example.com" --timeout 15
```

### Verbose Mode
```bash
python -m src.cli --url "https://example.com" --verbose
```

### CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--url` | `-u` | Required | URL to open in the browser |
| `--output` | `-o` | `output/locators.txt` | Output file path |
| `--timeout` | `-t` | `10` | Page load timeout in seconds |
| `--implicit-wait` | | `5` | Implicit wait time in seconds |
| `--verbose` | `-v` | `False` | Enable verbose/debug logging |

## Output Format

Locators are exported as a simple text file:

```
# Locators - Generated: 2026-03-27T10:30:00
# Total Pages: 2
# Format: element_name = locator_value

# Page: Home
# URL: https://example.com

login_btn = //button[@id='login_btn']
username_txt = //input[@name='username']
a_sign_in = //a[text()='Sign In']
search = //input[@name='search']

# Page: Login
# URL: https://example.com/login

email = //input[@name='email']
password = //input[@name='password']
submit_btn = //button[@id='submit_btn']
a_forgot_password = //a[text()='Forgot Password']
```

### Element Naming Rules
Elements are named automatically using the best available identifier:
1. **Element ID** (e.g., `submit_btn`)
2. **data-testid** attribute (e.g., `login-form`)
3. **name** attribute (e.g., `username`)
4. **Tag + text** content (e.g., `button_sign_in`)
5. **Tag + index** as fallback (e.g., `input_3`)

### Locator Priority
The best locator is selected automatically:
1. XPath (most reliable)
2. XPath with text
3. CSS selector
4. ID
5. data-testid
6. name

## Example Scenarios

### Testing a Login Flow
```bash
python -m src.cli --url "https://myapp.com/login"

# 1. Login page loads - elements captured
# 2. You enter credentials manually
# 3. Dashboard loads - new elements captured
# 4. Close browser - both pages exported
```

### Testing Dynamic Content
```bash
python -m src.cli --url "https://myapp.com/dashboard"

# 1. Dashboard captured
# 2. Click "Show Filters" - filter panel elements captured
# 3. Apply filter - updated results captured
# 4. Close browser when done
```

### Multi-Step Workflow
```bash
python -m src.cli --url "https://myapp.com/checkout"

# Captures each step:
# - cart_page (items, quantities)
# - shipping_page (address fields)
# - payment_page (card fields)
# - confirmation_page (order summary)
```

## Project Structure

```
Website-Crawler/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Module entry point
│   ├── cli.py               # Interactive mode CLI
│   ├── crawler.py           # Web crawling & page monitoring
│   ├── locator_generator.py # XPath/CSS locator generation
│   ├── exporter.py          # Text file export
│   └── validator.py         # Element validation utilities
├── config/
│   └── config.yaml          # Configuration file
├── tests/
│   ├── test_crawler.py      # Crawler tests
│   ├── test_locator.py      # Locator generator tests
│   └── test_exporter.py     # Exporter tests
├── output/                  # Generated locator files
├── logs/                    # Log files
├── requirements.txt         # Dependencies
├── main.py                  # Entry point
└── README.md                # This file
```

## Configuration

Edit `config/config.yaml` to customize behavior:

```yaml
crawler:
  element_tags:
    - button
    - a
    - input
    - select
    - textarea
  timeout: 10

selenium:
  browser: chrome
  headless: false
  implicit_wait: 5
  page_load_timeout: 20
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_locator.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Dependencies

- **selenium** - Browser automation
- **beautifulsoup4** - HTML parsing
- **pyyaml** - Configuration management
- **webdriver-manager** - Automatic ChromeDriver management
- **lxml** - XML/HTML processing

## Troubleshooting

### Chrome Driver Not Found
webdriver-manager handles this automatically. Ensure Chrome browser is installed.

### Timeout During Page Load
Increase timeout: `python -m src.cli --url "..." --timeout 30`

### No Elements Captured
Ensure the page has interactive elements (buttons, inputs, links). Hidden elements (`display:none`, `aria-hidden="true"`) are excluded.

## License

MIT License
