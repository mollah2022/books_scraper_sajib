"""
Settings module for the books scraper project.

central configuration for the scrapy application including
pipleline, feed exports, logging, and crawl behavior.
"""

# Project Settings
BOT_NAME = "books_scraper"

SPIDER_MODULES = ["books_scraper.spiders"]
NEWSPIDER_MODULE = "books_scraper.spiders"


# Identity the bot to the website
USER_AGENT = (
    "Mozilla/5.0 (compatible; BooksScraper/1.0; "
    "+https://books.toscrape.com)"   
)


# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# CRAWL BEHAVIOR
# Number of concurrent requests
CONCURRENT_REQUESTS = 8

# Delay between requests (in seconds) — be polite to the server
DOWNLOAD_DELAY = 0.5

# Disable cookies (not needed for this site)
COOKIES_ENABLED = False


# ITEM PIPELINES
# lower numbr = higher priority (runs first)
ITEM_PIPELINES = {
    "books_scraper.pipelines.DataCleaningPipeline": 100,
    "books_scraper.pipelines.SQLitePipeline": 200,
}


# FEED EXPORTS — JSON, CSV, XML
FEEDS = {
    # JSON export
    "output/books.json": {
        "format": "json",
        "encoding": "utf-8",
        "store_empty": False,
        "indent": 4,
        "overwrite": True,
    },
    # CSV export
    "output/books.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "store_empty": False,
        "overwrite": True,
        "fields": [
            "title",
            "price",
            "availability",
            "product_url",
            "image_url",
            "category",
        ],
    },
    # XML export
    "output/books.xml": {
        "format": "xml",
        "encoding": "utf-8",
        "store_empty": False,
        "overwrite": True,
    },
}

# LOGGING
LOG_LEVEL = "INFO"
LOG_FILE = "logs/scraper.log"
LOG_FILE_APPEND = False


# REQUEST FINGERPRINTER
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
