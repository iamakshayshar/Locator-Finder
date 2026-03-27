"""
Web Crawler Module - Fetches and parses web pages
"""

import logging
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)


class WebCrawler:
    """Crawls web pages and identifies interactive elements"""

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 10,
        implicit_wait: int = 5,
        page_load_timeout: int = 20,
    ):
        """
        Initialize the web crawler

        Args:
            headless: Run browser in headless mode
            timeout: Request timeout in seconds
            implicit_wait: Implicit wait time for elements
            page_load_timeout: Page load timeout
        """
        self.headless = headless
        self.timeout = timeout
        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout
        self.driver = None
        self.visited_urls: Set[str] = set()
        self.elements_found: List[Dict] = []

    def _initialize_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        self.driver.set_page_load_timeout(self.page_load_timeout)
        self.driver.implicitly_wait(self.implicit_wait)
        
        logger.info("WebDriver initialized successfully")

    def login_with_credentials(
        self,
        login_url: str,
        username: str,
        password: str,
        username_field_selector: str = "input[name='username']",
        password_field_selector: str = "input[name='password']",
        login_button_selector: str = "button[type='submit']",
        wait_for_selector: str = None,
        wait_timeout: int = 10,
    ) -> bool:
        """
        Perform login with provided credentials

        Args:
            login_url: URL of login page
            username: Username/email to login
            password: Password for login
            username_field_selector: CSS selector for username field (default: input[name='username'])
            password_field_selector: CSS selector for password field (default: input[name='password'])
            login_button_selector: CSS selector for login button (default: button[type='submit'])
            wait_for_selector: CSS selector to wait for after login (optional)
            wait_timeout: Timeout in seconds for waiting

        Returns:
            True if login successful, False otherwise
        """
        if not self.driver:
            self._initialize_driver()

        try:
            logger.info(f"Navigating to login page: {login_url}")
            self.driver.get(login_url)
            time.sleep(2)  # Wait for page to load

            # Fill username field
            logger.debug(f"Finding username field: {username_field_selector}")
            username_field = self.driver.find_element(By.CSS_SELECTOR, username_field_selector)
            username_field.clear()
            username_field.send_keys(username)
            logger.debug("Username entered")

            # Fill password field
            logger.debug(f"Finding password field: {password_field_selector}")
            password_field = self.driver.find_element(By.CSS_SELECTOR, password_field_selector)
            password_field.clear()
            password_field.send_keys(password)
            logger.debug("Password entered")

            # Click login button
            logger.debug(f"Finding login button: {login_button_selector}")
            login_button = self.driver.find_element(By.CSS_SELECTOR, login_button_selector)
            login_button.click()
            logger.info("Login button clicked")

            # Wait for login to complete
            if wait_for_selector:
                logger.debug(f"Waiting for {wait_for_selector} to appear (timeout: {wait_timeout}s)")
                WebDriverWait(self.driver, wait_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
                logger.info("Login successful - Element appeared")
            else:
                # Just wait for page to load
                time.sleep(3)
                logger.info("Login completed - Waiting 3 seconds")

            return True

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def load_cookies_from_file(self, file_path: str) -> bool:
        """
        Load cookies from a JSON file and apply to driver

        Args:
            file_path: Path to cookie file

        Returns:
            True if cookies loaded, False otherwise
        """
        import json
        from pathlib import Path

        if not self.driver:
            self._initialize_driver()

        try:
            cookie_file = Path(file_path)
            if not cookie_file.exists():
                logger.warning(f"Cookie file not found: {file_path}")
                return False

            with open(cookie_file, "r") as f:
                cookies = json.load(f)

            # Navigate to domain first (required for setting cookies)
            domain = cookies[0].get("domain", "example.com") if cookies else "example.com"
            self.driver.get(f"https://{domain}")

            # Add cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Could not add cookie: {e}")

            logger.info(f"Loaded {len(cookies)} cookies from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error loading cookies: {e}")
            return False

    def save_cookies_to_file(self, file_path: str) -> bool:
        """
        Save current driver cookies to a JSON file

        Args:
            file_path: Path to save cookies

        Returns:
            True if saved successfully, False otherwise
        """
        import json
        from pathlib import Path

        if not self.driver:
            logger.warning("No driver available to save cookies")
            return False

        try:
            cookies = self.driver.get_cookies()
            output_file = Path(file_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(cookies, f, indent=2)

            logger.info(f"Saved {len(cookies)} cookies to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving cookies: {e}")
            return False

    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL is valid and belongs to same domain"""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Ignore anchors and javascript
            if url.startswith("#") or url.startswith("javascript:"):
                return False
            
            # Check if same domain
            return parsed_url.netloc == parsed_base.netloc
        except Exception as e:
            logger.debug(f"Invalid URL {url}: {e}")
            return False

    def crawl_page(self, url: str) -> Dict:
        """
        Crawl a single page and extract interactive elements

        Args:
            url: URL to crawl

        Returns:
            Dictionary with page info and found elements
        """
        if not self.driver:
            self._initialize_driver()

        if url in self.visited_urls:
            logger.debug(f"URL already visited: {url}")
            return {"url": url, "status": "already_visited", "elements": []}

        try:
            logger.info(f"Crawling: {url}")
            
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
            
            self.visited_urls.add(url)
            
            # Find interactive elements
            elements = self._extract_elements(soup, url)
            
            logger.info(f"Found {len(elements)} interactive elements on {url}")
            
            return {
                "url": url,
                "status": "success",
                "elements": elements,
                "title": self.driver.title,
            }
        
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return {
                "url": url,
                "status": "error",
                "error": str(e),
                "elements": [],
            }

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
        
        # Tags to extract
        target_tags = ["button", "a", "input", "select", "textarea", "img"]
        
        for tag in soup.find_all(target_tags):
            try:
                # Skip hidden elements
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
                    "element_text": tag.get_text(strip=True)[:100],  # First 100 chars
                    "placeholder": tag.get("placeholder", ""),
                    "aria_label": tag.get("aria-label", ""),
                    "data_testid": tag.get("data-testid", ""),
                    "href": tag.get("href", ""),
                    "src": tag.get("src", ""),
                    "attributes": dict(tag.attrs),
                    "page_url": page_url,
                }
                
                # Only include elements with meaningful content
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

    def crawl_recursive(
        self, start_url: str, max_depth: int = 2, max_pages: int = 50
    ) -> List[Dict]:
        """
        Recursively crawl pages up to max depth

        Args:
            start_url: Starting URL
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl

        Returns:
            List of crawl results
        """
        if not self.driver:
            self._initialize_driver()

        results = []
        urls_to_visit = [(start_url, 0)]
        visited = set()

        while urls_to_visit and len(visited) < max_pages:
            current_url, depth = urls_to_visit.pop(0)

            if current_url in visited or depth > max_depth:
                continue

            result = self.crawl_page(current_url)
            visited.add(current_url)
            results.append(result)

            if depth < max_depth and result["status"] == "success":
                # Extract links for next iteration
                try:
                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    
                    for link in soup.find_all("a", href=True):
                        next_url = urljoin(current_url, link["href"])
                        
                        if (
                            self._is_valid_url(next_url, start_url)
                            and next_url not in visited
                        ):
                            urls_to_visit.append((next_url, depth + 1))
                
                except Exception as e:
                    logger.debug(f"Error extracting links: {e}")

        return results

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
            # Create a simple hash based on element count and structure
            import hashlib
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
            # Try to use page title first
            title = self.driver.title.strip().lower()
            if title:
                # Convert title to snake_case and add _page suffix
                page_name = title.replace(" ", "_").replace("-", "_")
                page_name = "".join(c if c.isalnum() or c == "_" else "" for c in page_name)
                return f"{page_name}_page" if page_name else "page"
            
            # Fallback to URL path
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
            Example: {
                'home_page': {'elements': [...], 'url': '...', 'title': '...'},
                'login_page': {'elements': [...], 'url': '...', 'title': '...'},
                'dashboard_page': {'elements': [...], 'url': '...', 'title': '...'}
            }
        """
        # Force non-headless mode for interactive use
        self.headless = False
        
        if not self.driver:
            self._initialize_driver()
        
        pages_captured = {}
        last_page_hash = ""
        last_page_name = ""
        
        try:
            logger.info(f"Starting interactive mode at {url}")
            logger.info("Browser will remain open. Close it when done or press Ctrl+C.")
            print("\n" + "="*70)
            print("INTERACTIVE MODE STARTED")
            print("="*70)
            print(f"Initial URL: {url}")
            print("\nInstructions:")
            print("1. Interact with the website normally (click links, fill forms, etc.)")
            print("2. Each page navigation automatically captures locators")
            print("3. Close the browser window to finish and export locators")
            print("4. Or press Ctrl+C to stop monitoring")
            print("="*70 + "\n")
            
            self.driver.get(url)
            time.sleep(2)  # Wait for initial page load
            
            while True:
                try:
                    # Get current page state
                    page_state = self.get_current_page_state()
                    
                    if page_state["status"] == "success":
                        current_hash = page_state["page_hash"]
                        current_page_name = page_state["page_name"]
                        
                        # Check if page has changed
                        if current_hash != last_page_hash:
                            logger.info(f"Page changed: {current_page_name}")
                            
                            # Ensure unique page names by adding counter if needed
                            page_key = current_page_name
                            counter = 1
                            while page_key in pages_captured:
                                page_key = f"{current_page_name}_{counter}"
                                counter += 1
                            
                            # Store page data
                            pages_captured[page_key] = {
                                "page_name": current_page_name,
                                "url": page_state["url"],
                                "title": page_state["title"],
                                "elements": page_state["elements"],
                                "element_count": len(page_state["elements"]),
                                "timestamp": page_state["timestamp"],
                            }
                            
                            print(f"✓ Captured: {page_key} ({len(page_state['elements'])} elements)")
                            
                            last_page_hash = current_hash
                            last_page_name = current_page_name
                    
                    # Check if browser is still open
                    try:
                        _ = self.driver.current_url
                    except Exception:
                        # Browser was closed by user
                        logger.info("Browser closed by user")
                        break
                    
                    time.sleep(poll_interval)
                
                except KeyboardInterrupt:
                    logger.info("Interactive mode interrupted by user")
                    break
                except Exception as e:
                    logger.debug(f"Error in monitoring loop: {e}")
                    time.sleep(poll_interval)
            
            print("\n" + "="*70)
            print(f"INTERACTIVE MODE COMPLETED")
            print(f"Total pages captured: {len(pages_captured)}")
            print("="*70 + "\n")
            
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
