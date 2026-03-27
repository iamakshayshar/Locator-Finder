"""
CLI Module - Interactive mode interface for the web crawler
"""

import argparse
import logging
import sys
from pathlib import Path
import yaml

from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

# Ensure logs directory exists
Path("logs").mkdir(parents=True, exist_ok=True)

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
    """Interactive mode interface for website crawler"""

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

    def run(self, args=None):
        """
        Run the CLI in interactive mode

        Args:
            args: Command-line arguments (for testing)
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        if not parsed_args.url:
            parser.print_help()
            return

        try:
            self._execute_interactive_crawl(parsed_args)
        except KeyboardInterrupt:
            logger.info("Crawling interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during crawling: {e}", exc_info=True)
            sys.exit(1)

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description="Website Crawler - Interactive mode locator generator for automation testers",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start interactive mode
  python -m src.cli --url "https://example.com"

  # With custom output directory
  python -m src.cli --url "https://example.com" --output output/locators.txt

  # With custom timeout
  python -m src.cli --url "https://example.com" --timeout 15

  # Verbose output
  python -m src.cli --url "https://example.com" --verbose
            """,
        )

        parser.add_argument(
            "--url",
            "-u",
            required=False,
            help="URL to open in interactive mode",
        )

        parser.add_argument(
            "--output",
            "-o",
            default="output/locators.txt",
            help="Output file path (default: output/locators.txt)",
        )

        parser.add_argument(
            "--timeout",
            "-t",
            type=int,
            default=10,
            help="Page load timeout in seconds (default: 10)",
        )

        parser.add_argument(
            "--implicit-wait",
            type=int,
            default=5,
            help="Implicit wait time in seconds (default: 5)",
        )

        parser.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            help="Verbose output",
        )

        return parser

    def _execute_interactive_crawl(self, args):
        """Execute interactive crawling mode"""
        logger.info("=" * 80)
        logger.info("Website Crawler - Interactive Mode")
        logger.info("=" * 80)

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize crawler (always non-headless for interactive mode)
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

            # Export results to text file
            print("\nExporting captured locators...")
            filepath = self.exporter.export_interactive_mode_pages(pages_data)

            print(f"\n  Locators exported to: {filepath}")

            logger.info("=" * 80)
            logger.info("Interactive Mode Completed Successfully")
            logger.info(f"Exported locators for {len(pages_data)} pages")
            logger.info("=" * 80)

        except KeyboardInterrupt:
            logger.info("Interactive mode interrupted by user")
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
        finally:
            self.crawler.close()


def main():
    """Main entry point"""
    cli = CrawlerCLI()
    cli.run()


if __name__ == "__main__":
    main()
