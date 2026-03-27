"""Test suite for Web Crawler module"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.crawler import WebCrawler


class TestWebCrawler(unittest.TestCase):
    """Test cases for WebCrawler"""

    def setUp(self):
        """Set up test fixtures"""
        self.crawler = WebCrawler(headless=True, timeout=10)

    def tearDown(self):
        """Clean up after tests"""
        if self.crawler.driver:
            self.crawler.close()

    def test_crawler_initialization(self):
        """Test crawler initialization"""
        self.assertEqual(self.crawler.headless, True)
        self.assertEqual(self.crawler.timeout, 10)
        self.assertEqual(len(self.crawler.visited_urls), 0)

    def test_is_valid_url(self):
        """Test URL validation"""
        base_url = "https://example.com"

        # Valid URLs
        self.assertTrue(
            self.crawler._is_valid_url("https://example.com/page", base_url)
        )
        self.assertTrue(
            self.crawler._is_valid_url("https://example.com/page/", base_url)
        )

        # Invalid URLs
        self.assertFalse(self.crawler._is_valid_url("#anchor", base_url))
        self.assertFalse(self.crawler._is_valid_url("javascript:void(0)", base_url))
        self.assertFalse(
            self.crawler._is_valid_url("https://other-domain.com", base_url)
        )

    @patch("src.crawler.BeautifulSoup")
    def test_extract_elements(self, mock_bs):
        """Test element extraction"""
        mock_soup = MagicMock()
        mock_button = MagicMock()
        mock_button.name = "button"
        mock_button.get_text.return_value = "Click me"
        mock_button.get.return_value = None
        mock_button.attrs = {"class": "btn"}

        mock_soup.find_all.return_value = [mock_button]

        elements = self.crawler._extract_elements(mock_soup, "https://example.com")

        self.assertGreater(len(elements), 0)
        self.assertEqual(elements[0]["tag_name"], "button")


class TestWebCrawlerIntegration(unittest.TestCase):
    """Integration tests for WebCrawler"""

    @patch("src.crawler.webdriver.Chrome")
    def test_context_manager(self, mock_driver):
        """Test context manager functionality"""
        with WebCrawler() as crawler:
            self.assertIsNotNone(crawler)

        # Driver should be closed
        # This is a simplified test


class TestWebCrawlerInteractiveMode(unittest.TestCase):
    """Test cases for interactive mode functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.crawler = WebCrawler(headless=True, timeout=10)

    def tearDown(self):
        """Clean up after tests"""
        if self.crawler.driver:
            self.crawler.close()

    def test_generate_page_name_from_title(self):
        """Test page name generation from browser title"""
        with patch.object(self.crawler, '_initialize_driver'):
            with patch.object(self.crawler, 'driver') as mock_driver:
                mock_driver.title = "Login Page"
                page_name = self.crawler._generate_page_name()
                self.assertIn("login", page_name.lower())
                self.assertTrue(page_name.endswith("_page"))

    def test_generate_page_name_fallback(self):
        """Test page name generation fallback to URL"""
        with patch.object(self.crawler, '_initialize_driver'):
            with patch.object(self.crawler, 'driver') as mock_driver:
                mock_driver.title = ""
                mock_driver.current_url = "https://example.com/dashboard"
                page_name = self.crawler._generate_page_name()
                self.assertIn("dashboard", page_name.lower())

    def test_get_current_page_state_success(self):
        """Test getting current page state"""
        with patch('src.crawler.BeautifulSoup'):
            with patch.object(self.crawler, '_initialize_driver'):
                with patch.object(self.crawler, 'driver') as mock_driver:
                    with patch.object(self.crawler, '_extract_elements') as mock_extract:
                        with patch.object(self.crawler, '_get_page_hash') as mock_hash:
                            mock_driver.page_source = "<html></html>"
                            mock_driver.current_url = "https://example.com"
                            mock_driver.title = "Home"
                            mock_extract.return_value = [{"tag": "button"}]
                            mock_hash.return_value = "abc123"
                            
                            self.crawler.driver = mock_driver
                            state = self.crawler.get_current_page_state()
                            
                            self.assertEqual(state["status"], "success")
                            self.assertEqual(len(state["elements"]), 1)
                            self.assertIn("page_name", state)
                            self.assertIn("url", state)

    def test_get_page_hash_generation(self):
        """Test page hash generation for change detection"""
        with patch.object(self.crawler, '_initialize_driver'):
            with patch.object(self.crawler, 'driver') as mock_driver:
                mock_driver.page_source = "<html><button>Click me</button></html>"
                
                self.crawler.driver = mock_driver
                hash1 = self.crawler._get_page_hash()
                
                # Hash should be consistent
                hash2 = self.crawler._get_page_hash()
                self.assertEqual(hash1, hash2)
                self.assertTrue(len(hash1) > 0)


if __name__ == "__main__":
    unittest.main()
