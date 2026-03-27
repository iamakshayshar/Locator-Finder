"""
Exporter Module - Export locators to text format
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

    def export_to_json(
        self, locators_data: List[Dict], filename: str = None, pretty: bool = True
    ) -> str:
        """
        Export locators to JSON format

        Args:
            locators_data: List of locator dictionaries
            filename: Output filename (default: auto-generated)
            pretty: Format JSON with indentation

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"locators_{timestamp}.json"

        filepath = self.output_dir / filename

        try:
            # Prepare data with summary
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "total_elements": len(locators_data),
                    "format_version": "1.0",
                },
                "locators": locators_data,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(
                    export_data,
                    f,
                    indent=2 if pretty else None,
                    ensure_ascii=False,
                )

            logger.info(f"Exported {len(locators_data)} locators to JSON: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise

    def export_to_excel(
        self, locators_data: List[Dict], filename: str = None
    ) -> str:
        """
        Export locators to Excel format

        Args:
            locators_data: List of locator dictionaries
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not OPENPYXL_AVAILABLE:
            logger.error("openpyxl not installed. Install with: pip install openpyxl")
            raise ImportError("openpyxl is required for Excel export")

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"locators_{timestamp}.xlsx"

        filepath = self.output_dir / filename

        try:
            from openpyxl import Workbook

            wb = Workbook()
            ws = wb.active
            ws.title = "Locators"

            # Define headers
            headers = [
                "Tag",
                "Text",
                "Type",
                "ID",
                "Name",
                "Data-TestID",
                "Aria-Label",
                "XPath",
                "XPath (Text)",
                "CSS Selector",
                "CSS (Text)",
                "Recommendations",
                "Page URL",
            ]

            # Add headers with formatting
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            # Add data rows
            for row_num, item in enumerate(locators_data, 2):
                element_info = item.get("element_info", {})
                locators = item.get("locators", {})

                row_data = [
                    element_info.get("tag_name", ""),
                    element_info.get("element_text", "")[:100],
                    element_info.get("element_type", ""),
                    element_info.get("element_id", ""),
                    element_info.get("element_name", ""),
                    element_info.get("data_testid", ""),
                    element_info.get("aria_label", ""),
                    locators.get("xpath", ""),
                    locators.get("xpath_with_text", ""),
                    locators.get("css_selector", ""),
                    locators.get("css_with_text", ""),
                    ", ".join(item.get("recommendations", [])),
                    element_info.get("page_url", ""),
                ]

                for col_num, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_num, column=col_num)
                    cell.value = value
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 20
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass

                ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

            # Freeze header row
            ws.freeze_panes = "A2"

            # Save workbook
            wb.save(filepath)

            logger.info(f"Exported {len(locators_data)} locators to Excel: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise

    def export_to_python(
        self, locators_data: List[Dict], filename: str = None
    ) -> str:
        """
        Export locators as Python code/dictionary

        Args:
            locators_data: List of locator dictionaries
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"locators_{timestamp}.py"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write('"""\n')
                f.write("Auto-generated locators mapping\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write('"""\n\n')

                f.write("LOCATORS = {\n")

                for idx, item in enumerate(locators_data):
                    element_info = item.get("element_info", {})
                    locators = item.get("locators", {})

                    # Create a key based on element info
                    text = element_info.get("element_text", "").replace("'", "\\'")[:50]
                    tag = element_info.get("tag_name", "unknown")
                    key = f"{tag}_{idx}"

                    f.write(f'    "{key}": {{\n')
                    f.write(f"        # {text}\n")
                    f.write(f"        'tag': '{tag}',\n")

                    for loc_type, loc_value in locators.items():
                        f.write(f"        '{loc_type}': '{loc_value}',\n")

                    f.write("    },\n")

                f.write("}\n")

            logger.info(f"Exported {len(locators_data)} locators to Python: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting to Python: {e}")
            raise

    def export_to_locators_txt(
        self, locators_data: List[Dict], filename: str = None
    ) -> str:
        """
        Export locators as simple text format for easy reference

        Format: element_name = locator_value

        Args:
            locators_data: List of locator dictionaries
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"locators_{timestamp}.txt"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Locators - Web Elements\n")
                f.write("# Generated: " + datetime.now().isoformat() + "\n")
                f.write("# Format: element_name = locator_value\n\n")

                for idx, item in enumerate(locators_data):
                    element_info = item.get("element_info", {})
                    locators = item.get("locators", {})

                    # Generate element name from available information
                    element_name = self._generate_element_name(element_info, idx)

                    # Pick the best locator (in priority order)
                    best_locator = self._pick_best_locator(locators)

                    if best_locator:
                        f.write(f"{element_name} = {best_locator}\n")

            logger.info(f"Exported locators to text: {filepath}")
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

        Priority:
        1. ID (most reliable)
        2. data-testid (stable)
        3. XPath with text (readable)
        4. XPath (reliable)
        5. CSS selector (modern)

        Args:
            locators: Dictionary of locators

        Returns:
            Best locator string or empty string
        """
        # Priority order
        priority_keys = [
            "id",
            "data_testid",
            "xpath_with_text",
            "xpath",
            "css_selector",
            "name",
        ]

        for key in priority_keys:
            if key in locators and locators[key]:
                return locators[key]

        # If no good match, return any available
        for value in locators.values():
            if value and not isinstance(value, str) or (isinstance(value, str) and value):
                return value

        return ""

    def export_summary(self, locators_data: List[Dict], filename: str = None) -> str:
        """
        Export summary report

        Args:
            locators_data: List of locator dictionaries
            filename: Output filename (default: auto-generated)

        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_{timestamp}.txt"

        filepath = self.output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("LOCATOR EXTRACTION SUMMARY\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Export Date: {datetime.now()}\n")
                f.write(f"Total Elements Found: {len(locators_data)}\n\n")

                # Count by tag
                tag_counts = {}
                for item in locators_data:
                    tag = item.get("element_info", {}).get("tag_name", "unknown")
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

                f.write("Elements by Type:\n")
                for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"  {tag}: {count}\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("SAMPLE LOCATORS\n")
                f.write("=" * 80 + "\n\n")

                for idx, item in enumerate(locators_data[:10]):
                    element_info = item.get("element_info", {})
                    locators = item.get("locators", {})

                    f.write(f"\n{idx + 1}. {element_info.get('tag_name', 'unknown')}\n")
                    f.write(f"   Text: {element_info.get('element_text', 'N/A')[:100]}\n")

                    if "xpath" in locators:
                        f.write(f"   XPath: {locators['xpath']}\n")

                    if "css_selector" in locators:
                        f.write(f"   CSS: {locators['css_selector']}\n")

                f.write("\n" + "=" * 80 + "\n")

            logger.info(f"Exported summary to: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Error exporting summary: {e}")
            raise

    def export_interactive_mode_pages(
        self, pages_data: Dict[str, Dict], formats: List[str] = None
    ) -> Dict[str, str]:
        """
        Export pages captured in interactive mode to multiple formats
        
        Args:
            pages_data: Dictionary mapping page_name to page data
                       {
                           'home_page': {'elements': [...], 'url': '...', ...},
                           'login_page': {'elements': [...], 'url': '...', ...},
                       }
            formats: List of export formats (['csv', 'json', 'excel', 'python', 'locators'])
        
        Returns:
            Dictionary mapping format names to exported file paths
        """
        if not formats:
            formats = ["csv", "json", "locators"]
        
        exported_files = {}
        
        try:
            for format_type in formats:
                if format_type.lower() == "csv":
                    filepath = self._export_interactive_csv(pages_data)
                    exported_files["csv"] = filepath
                    
                elif format_type.lower() == "json":
                    filepath = self._export_interactive_json(pages_data)
                    exported_files["json"] = filepath
                    
                elif format_type.lower() == "excel":
                    filepath = self._export_interactive_excel(pages_data)
                    exported_files["excel"] = filepath
                    
                elif format_type.lower() == "python":
                    filepath = self._export_interactive_python(pages_data)
                    exported_files["python"] = filepath
                    
                elif format_type.lower() in ["locators", "txt"]:
                    filepath = self._export_interactive_locators_txt(pages_data)
                    exported_files["locators"] = filepath
            
            logger.info(f"Exported {len(pages_data)} pages to {len(exported_files)} formats")
            return exported_files
        
        except Exception as e:
            logger.error(f"Error exporting interactive mode pages: {e}")
            raise

    def _export_interactive_csv(self, pages_data: Dict[str, Dict]) -> str:
        """Export interactive mode pages to separate CSV files per page"""
        from src.locator_generator import LocatorGenerator
        
        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            for page_name, page_data in pages_data.items():
                elements = page_data.get("elements", [])
                
                # Generate locators for each element
                locators_data = []
                for element in elements:
                    locators = generator.generate_locators(element)
                    locators_data.append(
                        {
                            "element_info": element,
                            "locators": locators,
                            "recommendations": "",
                        }
                    )
                
                # Export to CSV file with page name
                filename = f"{page_name}_locators_{timestamp}.csv"
                self.export_to_csv(locators_data, filename=filename)
            
            # Return path to first page CSV as representative
            pages = list(pages_data.keys())
            if pages:
                filename = f"{pages[0]}_locators_{timestamp}.csv"
                return str(self.output_dir / filename)
            
            return ""
        
        except Exception as e:
            logger.error(f"Error exporting interactive CSV: {e}")
            raise

    def _export_interactive_json(self, pages_data: Dict[str, Dict]) -> str:
        """Export interactive mode pages to a single JSON file"""
        from src.locator_generator import LocatorGenerator
        
        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interactive_pages_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            output_data = {}
            
            for page_name, page_data in pages_data.items():
                elements = page_data.get("elements", [])
                
                # Generate locators for each element
                page_locators = []
                for element in elements:
                    locators = generator.generate_locators(element)
                    page_locators.append(
                        {
                            "element_info": element,
                            "locators": locators,
                        }
                    )
                
                output_data[page_name] = {
                    "url": page_data.get("url", ""),
                    "title": page_data.get("title", ""),
                    "timestamp": page_data.get("timestamp", ""),
                    "element_count": len(elements),
                    "elements": page_locators,
                }
            
            # Write to JSON
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(pages_data)} pages to JSON: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error exporting interactive JSON: {e}")
            raise

    def _export_interactive_excel(self, pages_data: Dict[str, Dict]) -> str:
        """Export interactive mode pages to Excel with separate sheets per page"""
        from src.locator_generator import LocatorGenerator
        
        if not OPENPYXL_AVAILABLE:
            logger.warning("openpyxl not available, skipping Excel export")
            return ""
        
        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interactive_pages_{timestamp}.xlsx"
        filepath = self.output_dir / filename
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            
            wb = Workbook()
            wb.remove(wb.active)  # Remove default sheet
            
            for page_name, page_data in pages_data.items():
                elements = page_data.get("elements", [])
                ws = wb.create_sheet(title=page_name[:30])  # Excel sheet name limit
                
                # Add headers
                headers = [
                    "Tag", "Text", "Type", "ID", "Name", "Data-TestID",
                    "XPath", "CSS Selector", "URL"
                ]
                ws.append(headers)
                
                # Style header
                header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                header_font = Font(bold=True, color="FFFFFF")
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(wrap_text=True)
                
                # Add element data
                for element in elements:
                    locators = generator.generate_locators(element)
                    row = [
                        element.get("tag_name", ""),
                        element.get("element_text", "")[:100],
                        element.get("element_type", ""),
                        element.get("element_id", ""),
                        element.get("element_name", ""),
                        element.get("data_testid", ""),
                        locators.get("xpath", ""),
                        locators.get("css_selector", ""),
                        page_data.get("url", ""),
                    ]
                    ws.append(row)
                
                # Auto-adjust column widths
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value or "")) > max_length:
                                max_length = len(str(cell.value or ""))
                        except Exception:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            wb.save(filepath)
            logger.info(f"Exported {len(pages_data)} pages to Excel: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error exporting interactive Excel: {e}")
            raise

    def _export_interactive_python(self, pages_data: Dict[str, Dict]) -> str:
        """Export interactive mode pages to Python code file"""
        from src.locator_generator import LocatorGenerator
        
        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interactive_pages_{timestamp}.py"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Auto-generated locators from interactive mode crawl\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write("# Each page includes a dictionary of element locators\n\n")
                
                for page_name, page_data in pages_data.items():
                    elements = page_data.get("elements", [])
                    f.write(f"\n# Page: {page_data.get('title', page_name)}\n")
                    f.write(f"# URL: {page_data.get('url', '')}\n")
                    f.write(f"{page_name} = {{\n")
                    
                    for idx, element in enumerate(elements):
                        locators = generator.generate_locators(element)
                        best_locator = self._pick_best_locator(locators)
                        
                        element_name = self._generate_element_name(element, idx)
                        if element_name:
                            f.write(f"    '{element_name}': '{best_locator}',\n")
                    
                    f.write("}\n")
            
            logger.info(f"Exported {len(pages_data)} pages to Python: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error exporting interactive Python: {e}")
            raise

    def _export_interactive_locators_txt(self, pages_data: Dict[str, Dict]) -> str:
        """Export interactive mode pages to simple text format with page separators"""
        from src.locator_generator import LocatorGenerator
        
        generator = LocatorGenerator()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interactive_pages_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("INTERACTIVE MODE LOCATORS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Total Pages: {len(pages_data)}\n")
                f.write("=" * 80 + "\n\n")
                
                for page_name, page_data in pages_data.items():
                    elements = page_data.get("elements", [])
                    
                    f.write(f"\n{'='*80}\n")
                    f.write(f"PAGE: {page_data.get('title', page_name)}\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"URL: {page_data.get('url', 'N/A')}\n")
                    f.write(f"Elements Found: {len(elements)}\n")
                    f.write(f"{'-'*80}\n\n")
                    
                    for idx, element in enumerate(elements):
                        locators = generator.generate_locators(element)
                        best_locator = self._pick_best_locator(locators)
                        element_name = self._generate_element_name(element, idx)
                        
                        if element_name and best_locator:
                            f.write(f"{element_name} = {best_locator}\n")
                    
                    f.write("\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF LOCATORS\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"Exported {len(pages_data)} pages to text: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Error exporting interactive text: {e}")
            raise
