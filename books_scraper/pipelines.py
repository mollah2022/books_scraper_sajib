"""
pipelines module for the Books scraper project.

handles data cleaning, normalization, and database storage.
Two pipelines are defined:
i. dataCleaningPipeline = cleans and normalizes scraped data
ii. sqlitePipeline = stores cleaned data into sqlite database
"""

import re
import sqlite3
import logging
from itemadapter import ItemAdapter

logger = logging.getLogger(__name__)

class DateCleaningPipeline:
    """
    cleans and normalizes scraped book data.

    processing steps:
       i.strip leading/trailing whitespace from all string fields
       ii.remove currency symbols from price and convert to folat
       iii.normalize availability to boolean (True = In stock)
    """

    def process_item(self, item, spider):
        """
        process and clean a single BookItem.

        args:
            item: The scraped BookItem instance
            spider: The spider that scraped the item

        returns:
               BookItem: The cleaned and normalized item
        """

        adapter = ItemAdapter(item)

        #strip whitespace from all string fields
        self._strip_whitespace(adapter)

        #normalize price remove currency symbol, convert to float
        self._normalize_price(adapter)

        #normalize availability convert to boolean
        self._normalize_availability(adapter)

        return item

    def _strip_whitespace(self, adapter):
        """
        remove leading and trailing whitespace from all string fields.

        aregs:
             adapter: ItemAdapter wrapping the current item
        """

        for field_name in adapter.fields_names():
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()

            elseif isinstance(value, list):
                #join list value and strip( e.g., availability text)
                adapter[field_name] = " ".join(value).strip()

    def _normalize_price(self, adapter):
        """
        remove currency symbol and convert price to float.

        example:
            '£12.99' -> 12.99
            'Â£12.99' -> 12.99

        Args:
            adapter: ItemAdapter wrapping the current item
        """

        raw_price = adapter.get("price", "")

        #remove any non numeric characters expect dot
        cleaned_price = re.sub(r"[^\d.]", "", str(raw_price))

        try:
            adapter["price"] = float(cleaned_price)
        except ValueError:
            logger.warning(f"could not convert price: {raw_price}")
            adapter["price"] = 0.0

    def _normalize_availability(self, adapter):
        """
        normalize availability status to boolean.

        'In stock' == True
        any other value == False

        args:
           adapter: ItemAdapter wrapping the current item
        """
        raw_availability = adapter.get("availability", "")
        adapter["availability"] = "in stock" in str(raw_availability).lower()

class SQLitePipeline:
    """
    stores cleaned book data into a SQLite database.
    Database file is created at : database/books.db
    Table: books (created automatically if not exists)
    """

    def __init__(self):
        """
        Initialize database connection attributes.
        """

        self.connection = None
        self.cursor = None


    def open_spider(self, spider):
        """
        open sqlite connection and create table when spider starts.

        args:
            spider: The spider instance that us being opened
        """
        self.connection = sqlite3.connect("database/books.db")
        self.cursor = self.connection.cursor()
        self._create_table()
        logger.info("SQLite database connection opened")

    def _create_table(self):
        """
        Create the books table if it does not already exist.

        Columns match exactly with BookItem fields.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                price        REAL NOT NULL,
                availability INTEGER NOT NULL,
                product_url  TEXT NOT NULL,
                image_url    TEXT,
                category     TEXT NOT NULL,
                scraped_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        logger.info("Books table ready in SQLite") 

    def process_item(self, item, spider):
        """
        Insert a single cleaned BookItem into the SQLite database.

        Args:
            item: The cleaned BookItem instance
            spider: The spider that scraped the item

        Returns:
            BookItem: The item (passed through for feed exports)
        """
        adapter = ItemAdapter(item)

        self.cursor.execute("""
            INSERT INTO books (
                title, price, availability,
                product_url, image_url, category
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            adapter.get("title"),
            adapter.get("price"),
            int(adapter.get("availability")),
            adapter.get("product_url"),
            adapter.get("image_url"),
            adapter.get("category"),
        ))

        self.connection.commit()
        logger.info(f"Inserted book into database: {adapter.get('title')}")

        return item

    def close_spider(self, spider):
        """
        close the sqlite database connection when spider finishes.

        args:
           spider: The spider instance that is being closed
        """

        if self.connection:
            self.connection.close()
            logger.info("SQLite database connection closed")

