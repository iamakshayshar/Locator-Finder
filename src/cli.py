"""
CLI Module - Command-line interface for the web crawler
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional
import yaml

from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter
from src.validator import ElementValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/crawler.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


class CrawlerCLI:
    """Command-line interface for website crawler"""

    def __init__(self):
        """Initialize CLI"""
        self.config = self._load_config()
        self.crawler = None
        self.generator = None
        self.exporter = None

    def _load_config(self) -> dict:
        """Load configuration from config file"""
        config_file = Path("config/config.yaml")

        if config_file.exists():
            with open(config_file, "r") as f:
                return yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config file not found at {config_file}")
            return {}

    def run(self, args: Optional[list] = None):
        """
        Run the CLI

        Args:
            args: Command-line arguments (for testing)
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.url:
            parser.print_help()
            return

        try:
            self._execute_crawl(parsed_args)
        except KeyboardInterrupt:
            logger.info("Crawling interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during crawling: {e}", exc_info=True)
            sys.exit(1)

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description="Website Crawler - Generate unique locators for automation testers",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic crawling
  python -m src.cli --url "https://example.com"

  # Advanced crawling with options
  python -m src.cli \\
    --url "https://example.com" \\
    --depth 2 \\
    --max-pages 50 \\
    --output locators.json \\
    --headless \\
    --no-images

  # Export in multiple formats
  python -m src.cli \\
    --url "https://example.com" \\
    --export csv json excel python locators

  # Quick locator reference (simple text format)
  python -m src.cli \\
    --url "https://example.com" \\
    --export locators

  # Crawl authenticated application (with login)
  python -m src.cli \\
    --url "https://app.example.com/dashboard" \\
    --login-url "https://app.example.com/login" \\
    --username "user@example.com" \\
    --password "mypassword" \\
    --username-field "input[name='email']" \\
    --password-field "input[type='password']" \\
    --login-button "button.login-btn" \\
    --wait-for ".dashboard"

  # Reuse existing session with saved cookies
  python -m src.cli \\
    --url "https://app.example.com/dashboard" \\
    --cookies cookies.json \\
    --export locators

  # Login and save cookies for future reuse
  python -m src.cli \\
    --url "https://app.example.com/dashboard" \\
    --login-url "https://app.example.com/login" \\
    --username "user@example.com" \\
    --password "mypassword" \\
    --wait-for ".dashboard" \\
    --save-cookies cookies.json
            """,
        )

        # Required arguments
        parser.add_argument(
            "--url",
            "-u",
            required=False,
            help="URL to crawl",
        )

        # Optional arguments
        parser.add_argument(
            "--depth",
            "-d",
            type=int,
            default=1,
            help="Crawl depth (default: 1)",
        )

        parser.add_argument(
            "--max-pages",
            "-m",
            type=int,
            default=50,
            help="Maximum pages to crawl (default: 50)",
        )

        parser.add_argument(
            "--output",
            "-o",
            default="output/locators.csv",
            help="Output file (default: output/locators.csv)",
        )

        parser.add_argument(
            "--export",
            "-e",
            nargs="+",
            choices=["csv", "json", "excel", "python", "locators", "all"],
            default=["csv"],
            help="Export formats: csv, json, excel, python, locators (default: csv)",
        )

        parser.add_argument(
            "--headless",
            action="store_true",
            default=True,
            help="Run browser in headless mode (default: True)",
        )

        parser.add_argument(
            "--no-headless",
            action="store_false",
            dest="headless",
            help="Run browser with GUI",
        )

        parser.add_argument(
            "--no-images",
            action="store_true",
            help="Disable image loading",
        )

        parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=10,
            help="Request timeout in seconds (default: 10)",
        )

        parser.add_argument(
            "--implicit-wait",
            type=int,
            default=5,
            help="Implicit wait time in seconds (default: 5)",
        )

        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate locator uniqueness",
        )

        parser.add_argument(
            "--remove-duplicates",
            action="store_true",
            help="Remove duplicate elements",
        )

        # Authentication arguments
        parser.add_argument(
            "--login-url",
            help="Login page URL (required for authenticated access)",
        )

        parser.add_argument(
            "--username",
            "-un",
            help="Username/email for login",
        )

        parser.add_argument(
            "--password",
            "-pw",
            help="Password for login",
        )

        parser.add_argument(
            "--username-field",
            default="input[name='username']",
            help="CSS selector for username field (default: input[name='username'])",
        )

        parser.add_argument(
            "--password-field",
            default="input[name='password']",
            help="CSS selector for password field (default: input[name='password'])",
        )

        parser.add_argument(
            "--login-button",
            default="button[type='submit']",
            help="CSS selector for login button (default: button[type='submit'])",
        )

        parser.add_argument(
            "--wait-for",
            help="CSS selector to wait for after login (e.g., '.dashboard')",
        )

        parser.add_argument(
            "--cookies",
            help="Load cookies from file (JSON format) to reuse existing session",
        )

        parser.add_argument(
            "--save-cookies",
            help="Save cookies to file after login (for reusing sessions)",
        )

        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Verbose output",
        )

        parser.add_argument(
            "--interactive",
            "-i",
            action="store_true",
            help="Interactive mode: Open browser and capture locators as you navigate",
        )

        return parser

    def _execute_crawl(self, args):
        """Execute the crawling process"""
        logger.info("=" * 80)
        logger.info("Website Crawler Started")
        logger.info("=" * 80)

        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Route to appropriate execution mode
        if args.interactive:
            self._execute_interactive_crawl(args)
        else:
            self._execute_standard_crawl(args)

    def _execute_interactive_crawl(self, args):
        """Execute interactive crawling mode"""
        # Force non-headless in interactive mode
        args.headless = False

        # Initialize crawler
        self.crawler = WebCrawler(
            headless=False,
            timeout=args.timeout,
            implicit_wait=args.implicit_wait,
        )

        self.generator = LocatorGenerator(self.crawler.driver)
        output_dir = Path(args.output).parent
        self.exporter = Exporter(output_dir=str(output_dir))

        try:
            logger.info(f"Starting interactive mode at: {args.url}")

            # Start interactive mode
            pages_data = self.crawler.start_interactive_mode(
                url=args.url, poll_interval=2
            )

            if not pages_data:
                logger.warning("No pages captured in interactive mode")
                print("\nNo pages were captured. Exiting.")
                return

            logger.info(f"Captured {len(pages_data)} pages in interactive mode")

            # Export results in multiple formats
            export_formats = args.export
            if "all" in export_formats:
                export_formats = ["csv", "json", "excel", "python", "locators"]

            print("\nExporting captured pages...")
            exported_files = self.exporter.export_interactive_mode_pages(
                pages_data, formats=export_formats
            )

            # Print results
            print("\nExported Files:")
            for fmt_name, filepath in exported_files.items():
                print(f"  ✓ {fmt_name.upper()}: {filepath}")

            logger.info("=" * 80)
            logger.info("Interactive Mode Completed Successfully")
            logger.info(f"Exported {len(exported_files)} formats for {len(pages_data)} pages")
            logger.info("=" * 80)

        except KeyboardInterrupt:
            logger.info("Interactive mode interrupted by user")
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
        finally:
            self.crawler.close()

    def _execute_standard_crawl(self, args):
        """Execute standard crawling (non-interactive)"""
        # Initialize components
        self.crawler = WebCrawler(
            headless=args.headless,
            timeout=args.timeout,
            implicit_wait=args.implicit_wait,
        )

        self.generator = LocatorGenerator(self.crawler.driver)

        output_dir = Path(args.output).parent
        self.exporter = Exporter(output_dir=str(output_dir))

        try:
            # Handle authentication
            if args.cookies:
                # Load existing cookies
                logger.info(f"Loading session cookies from: {args.cookies}")
                self.crawler.load_cookies_from_file(args.cookies)
                # Refresh to apply cookies
                self.crawler.driver.get(args.url)
                time.sleep(2)

            elif args.login_url and args.username and args.password:
                # Perform login
                logger.info("Authenticating with provided credentials...")
                login_success = self.crawler.login_with_credentials(
                    login_url=args.login_url,
                    username=args.username,
                    password=args.password,
                    username_field_selector=args.username_field,
                    password_field_selector=args.password_field,
                    login_button_selector=args.login_button,
                    wait_for_selector=args.wait_for,
                )

                if not login_success:
                    logger.error("Login failed - check credentials and selectors")
                    return

                # Save cookies if requested
                if args.save_cookies:
                    logger.info(f"Saving session cookies to: {args.save_cookies}")
                    self.crawler.save_cookies_to_file(args.save_cookies)

            # Crawl pages
            logger.info(f"Starting crawl from: {args.url}")

            if args.depth > 1:
                results = self.crawler.crawl_recursive(
                    args.url, max_depth=args.depth, max_pages=args.max_pages
                )
            else:
                results = [self.crawler.crawl_page(args.url)]

            # Process results
            all_elements = []
            for result in results:
                if result.get("status") == "success":
                    all_elements.extend(result.get("elements", []))

            logger.info(f"Total elements found: {len(all_elements)}")

            # Validate elements
            valid_elements = [
                elem for elem in all_elements if ElementValidator.is_valid_element(elem)
            ]
            logger.info(f"Valid elements: {len(valid_elements)}")

            # Remove duplicates if requested
            if args.remove_duplicates:
                valid_elements = ElementValidator.filter_duplicates(valid_elements)

            # Generate locators
            print("\nGenerating locators...")
            locators_data = []

            for idx, element in enumerate(valid_elements):
                locators = self.generator.generate_locators(element)
                locators_data.append(locators)

                if (idx + 1) % 10 == 0:
                    print(f"  Processed {idx + 1}/{len(valid_elements)} elements")

            logger.info(f"Generated locators for {len(locators_data)} elements")

            # Export results
            self._export_results(args, locators_data)

            logger.info("=" * 80)
            logger.info("Crawling Completed Successfully")
            logger.info("=" * 80)

        finally:
            self.crawler.close()

    def _export_results(self, args, locators_data):
        """Export results in requested formats"""
        print("\nExporting locators...")

        export_formats = args.export
        if "all" in export_formats:
            export_formats = ["csv", "json", "excel", "python", "locators"]

        # Determine base filename
        output_path = Path(args.output)
        output_file = output_path.stem  # filename without extension

        exported_files = []

        for fmt in set(export_formats):
            try:
                if fmt == "csv":
                    filepath = self.exporter.export_to_csv(
                        locators_data, f"{output_file}.csv"
                    )
                    exported_files.append(("CSV", filepath))

                elif fmt == "json":
                    filepath = self.exporter.export_to_json(
                        locators_data, f"{output_file}.json"
                    )
                    exported_files.append(("JSON", filepath))

                elif fmt == "excel":
                    filepath = self.exporter.export_to_excel(
                        locators_data, f"{output_file}.xlsx"
                    )
                    exported_files.append(("Excel", filepath))

                elif fmt == "python":
                    filepath = self.exporter.export_to_python(
                        locators_data, f"{output_file}.py"
                    )
                    exported_files.append(("Python", filepath))

                elif fmt == "locators":
                    filepath = self.exporter.export_to_locators_txt(
                        locators_data, f"{output_file}_locators.txt"
                    )
                    exported_files.append(("Locators", filepath))

            except Exception as e:
                logger.warning(f"Could not export as {fmt}: {e}")

        # Export summary
        try:
            summary_file = self.exporter.export_summary(locators_data)
            exported_files.append(("Summary", summary_file))
        except Exception as e:
            logger.warning(f"Could not create summary: {e}")

        # Print results
        print("\nExported Files:")
        for fmt_name, filepath in exported_files:
            print(f"  ✓ {fmt_name}: {filepath}")

        logger.info(f"Exported {len(exported_files)} files")


def main():
    """Main entry point"""
    cli = CrawlerCLI()
    cli.run()


if __name__ == "__main__":
    main()
