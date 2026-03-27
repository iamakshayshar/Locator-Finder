"""
Exporter Module - Export locators to simple text format
"""

import logging
from typing import Dict
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Exporter:
    """Export locators to simple text format"""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize exporter

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")

    def export_interactive_mode_pages(self, pages_data: Dict[str, Dict]) -> str:
        """
        Export pages captured in interactive mode to a text file

        Args:
            pages_data: Dictionary mapping page_name to page data

        Returns:
            Path to the exported text file
        """
        return self._export_interactive_locators_txt(pages_data)

    def _export_interactive_locators_txt(self, pages_data: Dict[str, Dict]) -> str:
        """
        Export interactive mode pages to simple text format

        Format per element: element_name = locator_value

        Args:
            pages_data: Dictionary mapping page names to page data

        Returns:
            Path to the exported text file
        """
        from src.locator_generator import LocatorGenerator

        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"locators_{timestamp}.txt"
        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Locators - Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Total Pages: {len(pages_data)}\n")
                f.write(f"# Format: element_name = locator_value\n\n")

                for page_name, page_data in pages_data.items():
                    elements = page_data.get("elements", [])

                    f.write(f"\n# Page: {page_data.get('title', page_name)}\n")
                    f.write(f"# URL: {page_data.get('url', 'N/A')}\n\n")

                    for idx, element in enumerate(elements):
                        locator_result = generator.generate_locators(element)
                        locators = locator_result.get("locators", {})
                        best_locator = self._pick_best_locator(locators)
                        element_name = self._generate_element_name(element, idx)

                        if element_name and best_locator:
                            f.write(f"{element_name} = {best_locator}\n")

                    f.write("\n")

            logger.info(f"Exported {len(pages_data)} pages to text: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to text: {e}")
            raise

    def _generate_element_name(self, element_info: Dict, idx: int) -> str:
        """
        Generate a meaningful element name from element info

        Args:
            element_info: Element information dictionary
            idx: Element index

        Returns:
            Element name string
        """
        # Try to use meaningful names in priority order
        if element_info.get("element_id"):
            return element_info["element_id"]

        if element_info.get("data_testid"):
            return element_info["data_testid"]

        if element_info.get("element_name"):
            return element_info["element_name"]

        # Generate from tag and text
        tag = element_info.get("tag_name", "element")
        text = element_info.get("element_text", "").strip()

        if text:
            # Clean text: lowercase, replace spaces with underscores
            clean_text = text.lower().replace(" ", "_")[:30]
            # Remove special characters
            clean_text = "".join(c for c in clean_text if c.isalnum() or c == "_")
            return f"{tag}_{clean_text}"

        # Fallback to tag with index
        return f"{tag}_{idx}"

    def _pick_best_locator(self, locators: Dict) -> str:
        """
        Pick the best/most reliable locator from available options

        Priority: xpath > xpath_with_text > css_selector > id > data_testid > name

        Args:
            locators: Dictionary of locators

        Returns:
            Best locator string or empty string
        """
        priority_keys = [
            "xpath",
            "xpath_with_text",
            "css_selector",
            "id",
            "data_testid",
            "name",
        ]

        for key in priority_keys:
            if key in locators and locators[key]:
                return locators[key]

        return ""
