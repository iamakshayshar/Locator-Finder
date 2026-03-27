"""
Website Crawler - Python Entry Point

This allows running the crawler as a module:
    python -m src.cli --url "https://example.com"
"""

from src.cli import main

if __name__ == "__main__":
    main()
