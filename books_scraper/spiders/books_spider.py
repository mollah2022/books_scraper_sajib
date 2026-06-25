"""
Books spider module for the books scraper project.
This spider crawls books.toscrape.com, dynamically discovers all categories,
randomly selects 5 categories, then randomly selects 5 books from each
selected category and extracts the required book data.
"""

import random
import logging
import scrapy
from books_scraper.items import BookItem

logger = logging.getLogger(__name__)

class BooksSpider(scrapy.Spider):
    """
    spider for scraping books from books.toscrape.com
    crawling strategy:
    i.start from homepahe
    ii.dynamically discover all book categories
    iii.randomly seletc 5 categories
    iv.from each category, collect all books
    v.randomly select 5 books per category
    vi.extract full details from each book detail page
    """

    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/index.html"]


    def parse(self, response):
        """
        parse the homepage and extract all category links dynamically.
        randomly selects CATEGORY_SAMPLE_SIZE categories to crawl.

        args: 
            response: scrapy response obejct from homepage

        yields:
            scrapy.Request: request for each selected category page
        """

        # CSS selector extract all category links from sidebar
        all_categories = response.css("ul.nav-list > li > ul > li > a")

        logger.info(f"Total categories discovered : {len(all_categories)}")

        #randomly seletc 5 categories
        selected_categories = random.sample(
            list(all_categories),
            min(self.CATEGORY_SAMPLE_SIZE, len(all_categories))
        )

        for category in selected_categories:
            #Xpath extract text and stripe whitespace
            category_name = category.xpath("normalize-space(text())").get()

            #CSS extract href attribute
            category_url = category.css("::attr(href)").get()

            logger.info(f"selected category: {category_name}")

            yield response.follow(
                category_url,
                callback=self.parse_category,
                cb_kwargs={"category_name": category_name}
            )

    def parse_category(self, response, category_name):
        """
        parse a category page, collect all book links,
        then randomly select BOOK_SAMPLE_SIZE books.

        args:
            response: scrapy response object from category page
            category_name: Name of the current category

        yields:
              scrapy.Request: request for each selected book details page
        """

        # CSS selector get all book links on this page
        all_books = response.css("article.product_pod h3 a")

        # handle pagination get all books from all pages first
        all_book_links = [book.css("::attr(href)").get() for book in all_books]

        #check for next page
        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category_paginated,
                cb_kwargs={
                    "category_name": category_name,
                    "collected_books": all_book_links
                }
            )
        else:
            # No more page select random books
            yield from self._select_and_crawl_books(
                response, all_book_links, category_name
            )

    def parse_category_paginated(self, response, category_name, collected_books):
        """
        Handle paginated category pages, collecting all book links
        before randomly selecting books.

        args:
            response: scrapy response obejct from paginated category page
            category_name: Name of the current category
            collected_books: List of book URLs collected so far

        yield:
            scrapy.Request: next page request or book detail requests
        """
        
        # CSS collect books from this page too
        page_books = response.css("article.product_pod h3 a::attr(href)").getall()
        collected_books.extend(page_books)

        next_page = response.css("li.next a::attr(href)").get()

        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse_category_paginated,
                cb_kwargs={
                    "category_name": category_name,
                    "collected_books": collected_books
                }
            )
        else:
            yield from self._select_and_crawl_books(
                response, collected_books, category_name
            )

    def _select_crawl_books(self, response, booklinks, category_name):
        """
        randomly select BOOK_SAMPLE_SIZE books from collected links
        and send requests to their detail pages.

        args:
            response: current scrapy response object
            book_links: List of all book URLs in this category
            category_nmae: Name of the current category

        yields:
             scrapy.Request: request for each selected book details page
        """

        selected_books = random.simple(
            book_links,
            min(self.BOOK_SAMPLE_SIZE, len(book_links))
        )

        logger.info(
            f"Category '{category_name}' : "
            f"{len(book_links)} books found, "
            f"{lne(selected_books)} selected"
        )

        for book_url in selected_books:
            yield response.follow(
                book_yrl,
                callback=self.parse_book,
                cb_kwargs={"category_name": category_name}
            )

    def parse_book(self, response, category_name):
        """
        parse a book detail page and extract all required fields.
        uses both CSS and Xpath selectors.

        args:
            response: scrapy response object form book details page
            category_name: Name of the category this book belongs to

        yield:
             BookItem: populated item with all extracted book data
        """

        item = BookItem()

        #Xpath extract book title from h1 tag
        item["title"] = response.xpath("//div[@class='col-sm-6 product_main']/h1/text()").get()

        # CSS extract price
        item["price"] = response.css("p.price_color::text").get()
    
        # XPath — extract availability text
        item["availability"] = response.xpath(
            "//p[@class='instock availability']/text()"
        ).getall()

        # CSS — current page URL as product URL
        item["product_url"] = response.url

        # XPath — extract image source
        raw_image_url = response.xpath("//div[@class='item active']//img/@src").get()

        # Convert relative image URL to absolute URL
        item["image_url"] = response.urljoin(raw_image_url) if raw_image_url else None

        # Passed from category page via cb_kwargs
        item["category"] = category_name

        logger.info(f"Scraped book: {item['title']} | Category: {category_name}")

        yield item





