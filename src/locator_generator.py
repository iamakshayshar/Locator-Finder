"""
Locator Generator Module - Generates unique XPath and CSS selectors
"""

import logging
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class LocatorGenerator:
    """Generates unique locators (XPath and CSS selectors) for elements"""

    def __init__(self, driver: webdriver.Chrome = None):
        """
        Initialize locator generator

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver

    def generate_locators(self, element_info: Dict) -> Dict:
        """
        Generate multiple locator strategies for an element

        Args:
            element_info: Element information dictionary

        Returns:
            Dictionary with generated locators
        """
        locators = {
            "element_info": element_info,
            "locators": {},
        }

        # Generate ID locator (if available)
        if element_info.get("element_id"):
            locators["locators"]["id"] = element_info["element_id"]

        # Generate Name locator (if available)
        if element_info.get("element_name"):
            locators["locators"]["name"] = element_info["element_name"]

        # Generate CSS Selector
        css_selector = self._generate_css_selector(element_info)
        if css_selector:
            locators["locators"]["css_selector"] = css_selector

        # Generate XPath
        xpath = self._generate_xpath(element_info)
        if xpath:
            locators["locators"]["xpath"] = xpath

        # Generate XPath with text
        xpath_with_text = self._generate_xpath_with_text(element_info)
        if xpath_with_text:
            locators["locators"]["xpath_with_text"] = xpath_with_text

        # Generate CSS with text
        css_with_text = self._generate_css_with_text(element_info)
        if css_with_text:
            locators["locators"]["css_with_text"] = css_with_text

        # Generate data-testid locator (if available)
        if element_info.get("data_testid"):
            locators["locators"]["data_testid"] = f'[data-testid="{element_info["data_testid"]}"]'

        # Generate aria-label locator (if available)
        if element_info.get("aria_label"):
            locators["locators"]["aria_label"] = f"//*[@aria-label='{element_info['aria_label']}']"

        return locators

    def _generate_css_selector(self, element_info: Dict) -> Optional[str]:
        """
        Generate CSS selector for element

        Args:
            element_info: Element information

        Returns:
            CSS selector string or None
        """
        tag = element_info.get("tag_name", "")
        element_id = element_info.get("element_id", "")
        element_class = element_info.get("element_class", [])

        try:
            # Try ID first (most specific)
            if element_id:
                return f"#{element_id}"

            # Try class selector
            if element_class:
                classes = " ".join(element_class) if isinstance(element_class, list) else element_class
                return f"{tag}.{'.'.join(classes.split())}"

            # Try attribute selectors
            if element_info.get("data_testid"):
                return f"{tag}[data-testid='{element_info['data_testid']}']"

            if element_info.get("element_name"):
                return f"{tag}[name='{element_info['element_name']}']"

            # Fallback to tag + type
            if element_info.get("element_type"):
                return f"{tag}[type='{element_info['element_type']}']"

            return tag

        except Exception as e:
            logger.debug(f"Error generating CSS selector: {e}")
            return None

    def _generate_xpath(self, element_info: Dict) -> Optional[str]:
        """
        Generate XPath for element

        Args:
            element_info: Element information

        Returns:
            XPath string or None
        """
        tag = element_info.get("tag_name", "")

        try:
            # By ID
            if element_info.get("element_id"):
                return f"//{tag}[@id='{element_info['element_id']}']"

            # By name attribute
            if element_info.get("element_name"):
                return f"//{tag}[@name='{element_info['element_name']}']"

            # By type and name
            if element_info.get("element_type") and element_info.get("element_name"):
                return f"//{tag}[@type='{element_info['element_type']}'][@name='{element_info['element_name']}']"

            # By data-testid
            if element_info.get("data_testid"):
                return f"//{tag}[@data-testid='{element_info['data_testid']}']"

            # By class
            if element_info.get("element_class"):
                classes = element_info["element_class"]
                if isinstance(classes, list) and classes:
                    class_str = " ".join(classes)
                    return f"//{tag}[contains(@class, '{classes[0]}')]"

            # Fallback
            return f"//{tag}"

        except Exception as e:
            logger.debug(f"Error generating XPath: {e}")
            return None

    def _generate_xpath_with_text(self, element_info: Dict) -> Optional[str]:
        """
        Generate XPath using text content

        Args:
            element_info: Element information

        Returns:
            XPath with text or None
        """
        tag = element_info.get("tag_name", "")
        text = element_info.get("element_text", "").strip()

        if not text:
            return None

        try:
            # Exact text match
            return f"//{tag}[text()='{text}']"
        except Exception as e:
            logger.debug(f"Error generating XPath with text: {e}")
            return None

    def _generate_css_with_text(self, element_info: Dict) -> Optional[str]:
        """
        Generate CSS selector note (CSS doesn't support text, using placeholder)

        Args:
            element_info: Element information

        Returns:
            Description string
        """
        text = element_info.get("element_text", "").strip()

        if not text:
            return None

        # CSS doesn't support text matching, return a note
        return f"/* Element with text: '{text[:50]}' - use XPath for text matching */"

    def validate_locator(self, locator: str, locator_type: str) -> bool:
        """
        Validate if a locator is unique on the current page

        Args:
            locator: Locator string
            locator_type: Type of locator (xpath, css_selector, etc.)

        Returns:
            True if locator is unique (returns exactly 1 element)
        """
        if not self.driver:
            logger.warning("No driver available for validation")
            return False

        try:
            if locator_type == "xpath":
                by = By.XPATH
            elif locator_type == "css_selector":
                by = By.CSS_SELECTOR
            elif locator_type == "id":
                by = By.ID
            elif locator_type == "name":
                by = By.NAME
            else:
                return False

            elements = self.driver.find_elements(by, locator)
            
            if len(elements) == 1:
                logger.debug(f"Locator is unique: {locator_type} = {locator}")
                return True
            else:
                logger.debug(
                    f"Locator is not unique ({len(elements)} elements): {locator}"
                )
                return False

        except Exception as e:
            logger.debug(f"Error validating locator: {e}")
            return False

    def enhance_locator(self, element_info: Dict, locators: Dict) -> Dict:
        """
        Enhance locator with additional information

        Args:
            element_info: Element information
            locators: Generated locators

        Returns:
            Enhanced locator dictionary
        """
        enhanced = {
            **locators,
            "recommendations": [],
        }

        # Provide recommendations
        if "id" in locators["locators"]:
            enhanced["recommendations"].append("ID is most reliable - use this")
        elif "xpath_with_text" in locators["locators"]:
            enhanced["recommendations"].append("Text-based XPath is readable")
        elif "data_testid" in locators["locators"]:
            enhanced["recommendations"].append("data-testid is stable and recommended")
        else:
            enhanced["recommendations"].append("Multiple strategies available")

        return enhanced

    def create_locator_strategy(self, element_info: Dict) -> Dict:
        """
        Create a comprehensive locator strategy for an element

        Args:
            element_info: Element information

        Returns:
            Complete locator strategy
        """
        locators = self.generate_locators(element_info)
        enhanced = self.enhance_locator(element_info, locators)

        return {
            "element": {
                "tag": element_info.get("tag_name"),
                "text": element_info.get("element_text"),
                "visible": True,
            },
            "locators": enhanced["locators"],
            "recommendations": enhanced["recommendations"],
            "priority": self._calculate_priority(enhanced["locators"]),
        }

    def _calculate_priority(self, locators: Dict) -> str:
        """
        Calculate priority/reliability of locators

        Args:
            locators: Dictionary of locators

        Returns:
            Priority level: high, medium, or low
        """
        if "id" in locators:
            return "high"
        elif "data_testid" in locators or "xpath_with_text" in locators:
            return "medium"
        else:
            return "low"
