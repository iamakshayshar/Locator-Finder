"""Test suite for Exporter module"""

import unittest
import os
from pathlib import Path
from src.exporter import Exporter


class TestExporter(unittest.TestCase):
    """Test cases for Exporter"""

    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.test_output_dir = "test_output"
        cls.exporter = Exporter(output_dir=cls.test_output_dir)

        # Sample raw element data (as captured by interactive mode)
        cls.sample_elements = [
            {
                "tag_name": "button",
                "element_text": "Submit",
                "element_id": "submit_btn",
                "element_type": "submit",
                "element_class": ["btn"],
                "element_name": "",
                "data_testid": "",
                "placeholder": "",
                "aria_label": "",
                "href": "",
                "src": "",
                "attributes": {},
                "page_url": "https://example.com",
            },
            {
                "tag_name": "input",
                "element_text": "",
                "element_name": "email",
                "element_type": "email",
                "element_id": "",
                "element_class": [],
                "data_testid": "",
                "placeholder": "Enter email",
                "aria_label": "",
                "href": "",
                "src": "",
                "attributes": {},
                "page_url": "https://example.com",
            },
        ]

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        import shutil

        if os.path.exists(cls.test_output_dir):
            shutil.rmtree(cls.test_output_dir)

    def test_exporter_initialization(self):
        """Test exporter initialization"""
        self.assertTrue(os.path.exists(self.test_output_dir))

    def test_export_interactive_mode_pages(self):
        """Test export of interactive mode pages to text file"""
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "element_count": 2,
                "elements": self.sample_elements,
            },
        }

        filepath = self.exporter.export_interactive_mode_pages(pages_data)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".txt"))

        with open(filepath, "r") as f:
            content = f.read()

        # Should contain header comments
        self.assertIn("# Locators", content)
        self.assertIn("# Page: Home", content)
        self.assertIn("https://example.com", content)
        # Should contain element entries in name = locator format
        self.assertIn("=", content)
        self.assertIn("submit_btn", content)

    def test_export_interactive_locators_txt(self):
        """Test interactive text locators export"""
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "elements": self.sample_elements,
            },
        }

        filepath = self.exporter._export_interactive_locators_txt(pages_data)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r") as f:
            content = f.read()

        self.assertIn("Home", content)
        self.assertIn("https://example.com", content)
        self.assertIn("=", content)

    def test_export_multiple_pages(self):
        """Test export with multiple pages"""
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "elements": self.sample_elements,
            },
            "login_page": {
                "url": "https://example.com/login",
                "title": "Login",
                "elements": [self.sample_elements[0]],
            },
        }

        filepath = self.exporter.export_interactive_mode_pages(pages_data)
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r") as f:
            content = f.read()

        self.assertIn("# Page: Home", content)
        self.assertIn("# Page: Login", content)

    def test_generate_element_name_by_id(self):
        """Test element name generation using ID"""
        element = {"element_id": "login_btn", "element_name": "", "data_testid": ""}
        name = self.exporter._generate_element_name(element, 0)
        self.assertEqual(name, "login_btn")

    def test_generate_element_name_by_data_testid(self):
        """Test element name generation using data-testid"""
        element = {"element_id": "", "data_testid": "submit-btn", "element_name": ""}
        name = self.exporter._generate_element_name(element, 0)
        self.assertEqual(name, "submit-btn")

    def test_generate_element_name_by_name(self):
        """Test element name generation using name attribute"""
        element = {"element_id": "", "data_testid": "", "element_name": "username"}
        name = self.exporter._generate_element_name(element, 0)
        self.assertEqual(name, "username")

    def test_generate_element_name_by_text(self):
        """Test element name generation from text"""
        element = {
            "element_id": "",
            "data_testid": "",
            "element_name": "",
            "tag_name": "button",
            "element_text": "Click Me",
        }
        name = self.exporter._generate_element_name(element, 0)
        self.assertEqual(name, "button_click_me")

    def test_generate_element_name_fallback(self):
        """Test element name generation fallback to index"""
        element = {
            "element_id": "",
            "data_testid": "",
            "element_name": "",
            "tag_name": "div",
            "element_text": "",
        }
        name = self.exporter._generate_element_name(element, 5)
        self.assertEqual(name, "div_5")

    def test_pick_best_locator(self):
        """Test best locator selection"""
        locators = {
            "xpath": "//button[@id='submit']",
            "css_selector": "#submit",
            "id": "submit",
        }
        best = self.exporter._pick_best_locator(locators)
        self.assertEqual(best, "//button[@id='submit']")

    def test_pick_best_locator_empty(self):
        """Test best locator selection with empty dict"""
        best = self.exporter._pick_best_locator({})
        self.assertEqual(best, "")


if __name__ == "__main__":
    unittest.main()
