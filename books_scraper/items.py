
"""
Define the book data structure.
Each field stores a piece of information
about a book from the website.
"""

import scrapy

class BookItem(scrapy.Item):
    """
    Represents a single book scraped from books.todcrape.com
    """

    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Fiedl()
    product_url = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()