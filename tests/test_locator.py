"""Test suite for Locator Generator module"""

import unittest
from src.locator_generator import LocatorGenerator


class TestLocatorGenerator(unittest.TestCase):
    """Test cases for LocatorGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LocatorGenerator()
        self.sample_element = {
            "tag_name": "button",
            "element_id": "submit_btn",
            "element_class": ["btn", "btn-primary"],
            "element_name": "submit",
            "element_text": "Submit Form",
            "element_type": "submit",
            "data_testid": "submit-button",
            "aria_label": "Submit the form",
            "page_url": "https://example.com",
        }

    def test_generator_initialization(self):
        """Test generator initialization"""
        self.assertIsNone(self.generator.driver)

    def test_generate_css_selector_by_id(self):
        """Test CSS selector generation by ID"""
        css = self.generator._generate_css_selector(self.sample_element)
        self.assertEqual(css, "#submit_btn")

    def test_generate_css_selector_by_class(self):
        """Test CSS selector generation by class"""
        element = {
            "tag_name": "div",
            "element_class": ["container", "main"],
        }
        css = self.generator._generate_css_selector(element)
        self.assertIn("div", css)
        self.assertIn("container", css)

    def test_generate_xpath_by_id(self):
        """Test XPath generation by ID"""
        xpath = self.generator._generate_xpath(self.sample_element)
        self.assertIn("@id='submit_btn'", xpath)

    def test_generate_xpath_by_name(self):
        """Test XPath generation by name"""
        element = {
            "tag_name": "input",
            "element_name": "email",
        }
        xpath = self.generator._generate_xpath(element)
        self.assertIn("@name='email'", xpath)

    def test_generate_xpath_with_text(self):
        """Test XPath with text generation"""
        xpath = self.generator._generate_xpath_with_text(self.sample_element)
        self.assertIn("Submit Form", xpath)

    def test_generate_locators_complete(self):
        """Test complete locator generation"""
        locators = self.generator.generate_locators(self.sample_element)

        self.assertIn("locators", locators)
        self.assertIn("element_info", locators)

        loc_dict = locators["locators"]
        self.assertIn("id", loc_dict)
        self.assertIn("xpath", loc_dict)
        self.assertIn("css_selector", loc_dict)

    def test_calculate_priority_high(self):
        """Test priority calculation - high"""
        locators = {"id": "test_id"}
        priority = self.generator._calculate_priority(locators)
        self.assertEqual(priority, "high")

    def test_calculate_priority_medium(self):
        """Test priority calculation - medium"""
        locators = {"xpath_with_text": "//button[text()='Click']"}
        priority = self.generator._calculate_priority(locators)
        self.assertEqual(priority, "medium")

    def test_calculate_priority_low(self):
        """Test priority calculation - low"""
        locators = {"css_selector": "button"}
        priority = self.generator._calculate_priority(locators)
        self.assertEqual(priority, "low")

    def test_create_locator_strategy(self):
        """Test complete locator strategy creation"""
        strategy = self.generator.create_locator_strategy(self.sample_element)

        self.assertIn("element", strategy)
        self.assertIn("locators", strategy)
        self.assertIn("recommendations", strategy)
        self.assertIn("priority", strategy)

        self.assertEqual(strategy["element"]["tag"], "button")
        self.assertEqual(strategy["priority"], "high")


if __name__ == "__main__":
    unittest.main()
