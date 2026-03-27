"""
Validator Module - Validate elements and locators
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ElementValidator:
    """Validates element information and locators"""

    @staticmethod
    def is_valid_element(element_info: Dict) -> bool:
        """
        Check if element information is valid

        Args:
            element_info: Element information dictionary

        Returns:
            True if element is valid
        """
        if not element_info:
            return False

        # Must have a tag name
        if not element_info.get("tag_name"):
            return False

        # Element should be interactive (has text, id, name, or other identifying info)
        has_identifying_info = any(
            [
                element_info.get("element_text"),
                element_info.get("element_id"),
                element_info.get("element_name"),
                element_info.get("data_testid"),
                element_info.get("aria_label"),
            ]
        )

        return has_identifying_info

    @staticmethod
    def validate_locator_syntax(locator: str, locator_type: str) -> bool:
        """
        Validate locator syntax

        Args:
            locator: Locator string
            locator_type: Type of locator

        Returns:
            True if syntax is valid
        """
        if not locator or not locator_type:
            return False

        try:
            if locator_type == "xpath":
                # Basic XPath validation
                if not locator.startswith("//"):
                    return False
                if "/" not in locator[2:]:
                    return False

            elif locator_type == "css_selector":
                # Basic CSS selector validation
                if not locator:
                    return False

            elif locator_type == "id":
                # ID should not contain special characters
                if not locator or " " in locator:
                    return False

            return True

        except Exception as e:
            logger.debug(f"Error validating locator syntax: {e}")
            return False

    @staticmethod
    def compare_elements(
        element1: Dict, element2: Dict, threshold: float = 0.8
    ) -> float:
        """
        Compare similarity of two elements

        Args:
            element1: First element
            element2: Second element
            threshold: Similarity threshold

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not element1 or not element2:
            return 0.0

        matching_fields = 0
        total_fields = 5

        # Compare key fields
        if element1.get("tag_name") == element2.get("tag_name"):
            matching_fields += 1

        if (
            element1.get("element_text", "").strip()
            == element2.get("element_text", "").strip()
        ):
            matching_fields += 1

        if element1.get("element_id") == element2.get("element_id"):
            matching_fields += 1

        if element1.get("element_name") == element2.get("element_name"):
            matching_fields += 1

        if element1.get("data_testid") == element2.get("data_testid"):
            matching_fields += 1

        return matching_fields / total_fields

    @staticmethod
    def filter_duplicates(
        elements: List[Dict], similarity_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Filter out duplicate or very similar elements

        Args:
            elements: List of element dictionaries
            similarity_threshold: Threshold for considering elements as duplicates

        Returns:
            Filtered list of unique elements
        """
        if not elements:
            return []

        unique_elements = []
        seen_indices = set()

        for idx, element in enumerate(elements):
            if idx in seen_indices:
                continue

            unique_elements.append(element)
            seen_indices.add(idx)

            # Mark similar elements as seen
            for compare_idx in range(idx + 1, len(elements)):
                if compare_idx in seen_indices:
                    continue

                similarity = ElementValidator.compare_elements(
                    element, elements[compare_idx], similarity_threshold
                )

                if similarity >= similarity_threshold:
                    seen_indices.add(compare_idx)

        logger.info(
            f"Filtered {len(elements) - len(unique_elements)} duplicate elements"
        )
        return unique_elements

    @staticmethod
    def validate_crawl_result(result: Dict) -> bool:
        """
        Validate crawl result

        Args:
            result: Crawl result dictionary

        Returns:
            True if result is valid
        """
        if not result:
            return False

        # Must have URL
        if not result.get("url"):
            return False

        # Must have status
        if not result.get("status"):
            return False

        # If successful, should have elements or title
        if result.get("status") == "success":
            return bool(result.get("elements") or result.get("title"))

        return True
