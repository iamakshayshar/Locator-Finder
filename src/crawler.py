"""
Web Crawler Module - Interactive mode web page crawler
"""

import logging
import hashlib
from typing import List, Dict, Set
from urllib.parse import urlparse
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebCrawler:
    """Interactive web crawler that captures page elements"""

    def __init__(
        self,
        headless: bool = False,
        timeout: int = 10,
        implicit_wait: int = 5,
        page_load_timeout: int = 120,
    ):
        """
        Initialize the web crawler

        Args:
            headless: Run browser in headless mode (default: False for interactive)
            timeout: Request timeout in seconds
            implicit_wait: Implicit wait time for elements
            page_load_timeout: Page load timeout
        """
        self.headless = headless
        self.timeout = timeout
        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout
        self.driver = None

    def _initialize_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.page_load_strategy = "eager"

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.implicitly_wait(self.implicit_wait)

        logger.info("WebDriver initialized successfully")

    def _extract_elements(self, soup: BeautifulSoup, page_url: str) -> List[Dict]:
        """
        Extract interactive elements from HTML

        Args:
            soup: BeautifulSoup object
            page_url: URL of the page

        Returns:
            List of element dictionaries
        """
        elements = []

        target_tags = ["button", "a", "input", "select", "textarea", "img"]

        for tag in soup.find_all(target_tags):
            try:
                if tag.get("style") and "display:none" in tag.get("style"):
                    continue

                if tag.get("aria-hidden") == "true":
                    continue

                element_info = {
                    "tag_name": tag.name,
                    "element_type": tag.get("type", ""),
                    "element_id": tag.get("id", ""),
                    "element_class": tag.get("class", []),
                    "element_name": tag.get("name", ""),
                    "element_text": tag.get_text(strip=True)[:100],
                    "placeholder": tag.get("placeholder", ""),
                    "aria_label": tag.get("aria-label", ""),
                    "data_testid": tag.get("data-testid", ""),
                    "href": tag.get("href", ""),
                    "src": tag.get("src", ""),
                    "attributes": dict(tag.attrs),
                    "page_url": page_url,
                }

                if (
                    element_info["element_text"]
                    or element_info["element_id"]
                    or element_info["element_name"]
                    or element_info["data_testid"]
                ):
                    elements.append(element_info)

            except Exception as e:
                logger.debug(f"Error extracting element: {e}")
                continue

        return elements

    def _get_page_hash(self) -> str:
        """
        Generate a hash of the current DOM for change detection

        Returns:
            Hash string of current page HTML
        """
        if not self.driver:
            return ""

        try:
            page_source = self.driver.page_source
            return hashlib.md5(page_source.encode()).hexdigest()
        except Exception as e:
            logger.debug(f"Error generating page hash: {e}")
            return ""

    def _generate_page_name(self) -> str:
        """
        Generate a page name from title or URL

        Returns:
            Generated page name (e.g., 'home_page', 'login_page')
        """
        if not self.driver:
            return "unknown_page"

        try:
            title = self.driver.title.strip().lower()
            if title:
                page_name = title.replace(" ", "_").replace("-", "_")
                page_name = "".join(c if c.isalnum() or c == "_" else "" for c in page_name)
                return f"{page_name}_page" if page_name else "page"

            current_url = self.driver.current_url
            path = urlparse(current_url).path.strip("/").split("/")[-1]
            if path:
                page_name = path.replace("-", "_").split(".")[0]
                return f"{page_name}_page" if page_name else "page"

            return "home_page"

        except Exception as e:
            logger.debug(f"Error generating page name: {e}")
            return "unknown_page"

    def get_current_page_state(self) -> Dict:
        """
        Capture the current page state including elements

        Returns:
            Dictionary with page information and elements
        """
        if not self.driver:
            return {"status": "error", "elements": []}

        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            page_name = self._generate_page_name()
            current_url = self.driver.current_url

            elements = self._extract_elements(soup, current_url)

            return {
                "status": "success",
                "page_name": page_name,
                "url": current_url,
                "title": self.driver.title,
                "elements": elements,
                "page_hash": self._get_page_hash(),
                "element_count": len(elements),
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"Error capturing page state: {e}")
            return {"status": "error", "elements": [], "error": str(e)}

    def start_interactive_mode(self, url: str, poll_interval: int = 2) -> Dict[str, Dict]:
        """
        Start interactive mode - opens browser and monitors for DOM changes.

        The browser will remain open allowing user interaction. As user navigates
        or performs actions, the tool detects page/DOM changes and captures locators.

        User can exit by closing the browser window.

        Args:
            url: Initial URL to open
            poll_interval: Seconds between DOM change checks

        Returns:
            Dictionary mapping page names to their captured elements
        """
        self.headless = False

        if not self.driver:
            self._initialize_driver()

        pages_captured = {}
        last_page_hash = ""

        try:
            logger.info(f"Starting interactive mode at {url}")
            print("\n" + "=" * 70)
            print("INTERACTIVE MODE STARTED")
            print("=" * 70)
            print(f"Initial URL: {url}")
            print("\nInstructions:")
            print("1. Interact with the website normally (click links, fill forms, etc.)")
            print("2. Each page navigation automatically captures locators")
            print("3. Close the browser window to finish and export locators")
            print("4. Or press Ctrl+C to stop monitoring")
            print("=" * 70 + "\n")

            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning(f"Initial page load timed out, continuing: {e}")
            time.sleep(3)

            while True:
                try:
                    page_state = self.get_current_page_state()

                    if page_state["status"] == "success":
                        current_hash = page_state["page_hash"]
                        current_page_name = page_state["page_name"]

                        if current_hash != last_page_hash:
                            logger.info(f"Page changed: {current_page_name}")

                            page_key = current_page_name
                            counter = 1
                            while page_key in pages_captured:
                                page_key = f"{current_page_name}_{counter}"
                                counter += 1

                            pages_captured[page_key] = {
                                "page_name": current_page_name,
                                "url": page_state["url"],
                                "title": page_state["title"],
                                "elements": page_state["elements"],
                                "element_count": len(page_state["elements"]),
                                "timestamp": page_state["timestamp"],
                            }

                            print(f"  Captured: {page_key} ({len(page_state['elements'])} elements)")

                            last_page_hash = current_hash

                    try:
                        _ = self.driver.current_url
                    except Exception:
                        logger.info("Browser closed by user")
                        break

                    time.sleep(poll_interval)

                except KeyboardInterrupt:
                    logger.info("Interactive mode interrupted by user")
                    break
                except Exception as e:
                    logger.debug(f"Error in monitoring loop: {e}")
                    time.sleep(poll_interval)

            print("\n" + "=" * 70)
            print(f"INTERACTIVE MODE COMPLETED")
            print(f"Total pages captured: {len(pages_captured)}")
            print("=" * 70 + "\n")

            if pages_captured:
                print("Pages captured:")
                for i, page_name in enumerate(pages_captured.keys(), 1):
                    page_data = pages_captured[page_name]
                    print(f"  {i}. {page_name}: {page_data['element_count']} elements")
                print()

            return pages_captured

        except Exception as e:
            logger.error(f"Error in interactive mode: {e}")
            print(f"Error: {e}")
            return pages_captured

    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def __enter__(self):
        """Context manager entry"""
        self._initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
