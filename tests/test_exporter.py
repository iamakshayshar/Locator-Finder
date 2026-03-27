"""Test suite for Exporter module"""

import unittest
import os
import json
import csv
from pathlib import Path
from src.exporter import Exporter


class TestExporter(unittest.TestCase):
    """Test cases for Exporter"""

    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.test_output_dir = "test_output"
        cls.exporter = Exporter(output_dir=cls.test_output_dir)

        # Sample locator data
        cls.sample_locators = [
            {
                "element_info": {
                    "tag_name": "button",
                    "element_text": "Submit",
                    "element_id": "submit_btn",
                    "element_type": "submit",
                    "page_url": "https://example.com",
                },
                "locators": {
                    "id": "submit_btn",
                    "xpath": "//button[@id='submit_btn']",
                    "css_selector": "#submit_btn",
                },
                "recommendations": ["ID is most reliable"],
            },
            {
                "element_info": {
                    "tag_name": "input",
                    "element_text": "",
                    "element_name": "email",
                    "element_type": "email",
                    "page_url": "https://example.com",
                },
                "locators": {
                    "name": "email",
                    "xpath": "//input[@name='email']",
                    "css_selector": "input[name='email']",
                },
                "recommendations": ["Use name attribute"],
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

    def test_export_to_csv(self):
        """Test CSV export"""
        filepath = self.exporter.export_to_csv(
            self.sample_locators, "test_locators.csv"
        )

        self.assertTrue(os.path.exists(filepath))

        # Verify CSV content
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Tag"], "button")
        self.assertEqual(rows[0]["Text"], "Submit")

    def test_export_to_json(self):
        """Test JSON export"""
        filepath = self.exporter.export_to_json(
            self.sample_locators, "test_locators.json"
        )

        self.assertTrue(os.path.exists(filepath))

        # Verify JSON content
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("locators", data)
        self.assertEqual(len(data["locators"]), 2)

    def test_export_to_python(self):
        """Test Python export"""
        filepath = self.exporter.export_to_python(
            self.sample_locators, "test_locators.py"
        )

        self.assertTrue(os.path.exists(filepath))

        # Verify Python file is valid
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("LOCATORS = {", content)
        self.assertIn("button_0", content)

    def test_export_summary(self):
        """Test summary export"""
        filepath = self.exporter.export_summary(
            self.sample_locators, "test_summary.txt"
        )

        self.assertTrue(os.path.exists(filepath))

        # Verify summary content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("Total Elements Found: 2", content)
        self.assertIn("button: 1", content)
        self.assertIn("input: 1", content)

    def test_export_to_locators_txt(self):
        """Test locators text format export"""
        filepath = self.exporter.export_to_locators_txt(
            self.sample_locators, "test_locators.txt"
        )

        self.assertTrue(os.path.exists(filepath))

        # Verify content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Should contain the header
        self.assertIn("# Locators - Web Elements", content)
        self.assertIn("# Format: element_name = locator_value", content)

        # Should contain element entries
        self.assertIn("=", content)  # Format: name = locator
        self.assertIn("submit_btn", content)  # Element ID
        self.assertIn("email", content)  # Element name

    def test_export_interactive_mode_pages(self):
        """Test export of interactive mode pages"""
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "element_count": 2,
                "elements": self.sample_locators,
            },
            "login_page": {
                "url": "https://example.com/login",
                "title": "Login",
                "element_count": 1,
                "elements": [self.sample_locators[0]],
            },
        }

        # Test JSON export
        exported = self.exporter.export_interactive_mode_pages(
            pages_data, formats=["json"]
        )
        self.assertIn("json", exported)
        self.assertTrue(os.path.exists(exported["json"]))

    def test_export_interactive_json(self):
        """Test interactive JSON export"""
        # Create raw element data
        raw_elements = [
            {
                "tag_name": "button",
                "element_text": "Click me",
                "element_id": "btn1",
                "element_type": "button",
                "page_url": "https://example.com",
                "element_class": [],
                "element_name": "",
                "data_testid": "",
                "placeholder": "",
                "aria_label": "",
                "href": "",
                "src": "",
                "attributes": {},
            },
        ]
        
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "timestamp": 1234567890,
                "elements": raw_elements,
            },
        }

        filepath = self.exporter._export_interactive_json(pages_data)
        self.assertTrue(os.path.exists(filepath))

        # Verify JSON content
        with open(filepath, "r") as f:
            data = json.load(f)

        self.assertIn("home_page", data)
        self.assertEqual(data["home_page"]["url"], "https://example.com")

    def test_export_interactive_locators_txt(self):
        """Test interactive text locators export"""
        # Create raw element data (not processed with locators yet)
        raw_elements = [
            {
                "tag_name": "button",
                "element_text": "Submit",
                "element_id": "submit_btn",
                "element_type": "submit",
                "page_url": "https://example.com",
                "element_class": ["btn"],
                "element_name": "",
                "data_testid": "",
                "placeholder": "",
                "aria_label": "",
                "href": "",
                "src": "",
                "attributes": {},
            },
            {
                "tag_name": "input",
                "element_text": "",
                "element_name": "email",
                "element_type": "email",
                "page_url": "https://example.com",
                "element_class": [],
                "element_id": "",
                "data_testid": "",
                "placeholder": "Enter email",
                "aria_label": "",
                "href": "",
                "src": "",
                "attributes": {},
            },
        ]
        
        pages_data = {
            "home_page": {
                "url": "https://example.com",
                "title": "Home",
                "elements": raw_elements,
            },
        }

        filepath = self.exporter._export_interactive_locators_txt(pages_data)
        self.assertTrue(os.path.exists(filepath))

        # Verify content
        with open(filepath, "r") as f:
            content = f.read()

        self.assertIn("INTERACTIVE MODE LOCATORS", content)
        self.assertIn("Home", content)
        self.assertIn("https://example.com", content)


if __name__ == "__main__":
    unittest.main()
