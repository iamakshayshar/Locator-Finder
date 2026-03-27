"""
Website Crawler - Generate unique locators for automation testers
"""

__version__ = "1.0.0"
__author__ = "Automation Tester Team"

from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

__all__ = ["WebCrawler", "LocatorGenerator", "Exporter"]
