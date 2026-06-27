# Books Scraper - Enterprise Web Scraping Pipeline

A production-ready web scraping pipeline built with Scrapy. It crawls [books.toscrape.com](https://books.toscrape.com), dynamically discovers all book categories, randomly picks 5 categories, then randomly picks 5 books from each category — giving 25 books per run. All data is cleaned through an item pipeline, stored in SQLite, and exported to JSON, CSV, and XML. The project is deployed via Scrapyd and fully containerized with Docker.

- GitHub: https://github.com/mollah2022/books_scraper_sajib
- Target: https://books.toscrape.com

---

## How It Works

1. Spider starts from the homepage
2. Discovers all book categories dynamically — no hardcoded URLs
3. Randomly selects 5 categories
4. Collects all books from each selected category across all pages
5. Randomly selects 5 books from each category
6. Extracts title, price, availability, product URL, image URL, and category
7. Cleans and normalizes data through item pipelines
8. Stores data in SQLite database
9. Exports data to JSON, CSV, and XML

---

## Tech Stack

| Tool           | Version  | Purpose                          |
| -------------- | -------- | -------------------------------- |
| Python         | 3.12     | Core language                    |
| Scrapy         | 2.11.2   | Web scraping framework           |
| Scrapyd        | 1.5.0    | Spider deployment server         |
| scrapyd-client | 2.0.0    | CLI tool to deploy spiders       |
| SQLite         | Built-in | Database storage                 |
| Docker         | Latest   | Containerization                 |
| Docker Compose | 1.29+    | Multi-container orchestration    |
| Twisted        | 24.3.0   | Async networking                 |
| itemadapter    | 0.9.0    | Unified item access in pipelines |
| w3lib          | 2.2.1    | URL utilities                    |

---

## Project Structure
books_scraper/

├── books_scraper/

│   ├── spiders/

│   │   ├── init.py

│   │   └── books_spider.py      # Main spider - crawling logic

│   ├── init.py

│   ├── items.py                 # BookItem data model

│   ├── pipelines.py             # Data cleaning + SQLite storage

│   ├── middlewares.py           # Middlewares

│   └── settings.py              # All Scrapy configuration

├── database/

│   └── books.db                 # SQLite database (auto-created)

├── output/

│   ├── books.json               # JSON export

│   ├── books.csv                # CSV export

│   └── books.xml                # XML export

├── logs/

│   └── scraper.log              # Scraping logs

├── Dockerfile                   # Docker image definition

├── docker-compose.yml           # Docker Compose config

├── entrypoint.sh                # Container startup script

├── scrapy.cfg                   # Scrapy + Scrapyd config

├── scrapyd.cfg                  # Scrapyd server config

├── requirements.txt             # Python dependencies

└── README.md                    # This file
---

## Setup and Run

### Requirements

- Python 3.12+
- Git
- Docker + Docker Compose (for containerized run only)

---

### Step 1 - Clone the Repository

```bash
git clone https://github.com/mollah2022/books_scraper_sajib.git
cd books_scraper_sajib
```

---

### Step 2 - Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 - Install Dependencies

```bash
pip install -r requirements.txt
```

If you are behind a proxy:

```bash
pip install --trusted-host pypi.org \
            --trusted-host files.pythonhosted.org \
            -r requirements.txt
```

---

### Step 4 - Create Required Directories

```bash
mkdir -p output logs database
```

---

### Step 5 - Run the Spider

```bash
scrapy crawl books
```

## After the run you will find:

### Check the Database

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('database/books.db')
cursor = conn.cursor()
cursor.execute('SELECT title, price, availability, category FROM books')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

---

## Run with Docker

### Step 1 - Build and Start

```bash
docker-compose up --build
```

This will automatically:

- Build the Docker image
- Start the Scrapyd server
- Deploy the spider to Scrapyd
- Expose Scrapyd UI at http://localhost:6800

---

### Step 2 - Open Scrapyd in Browser

You will see the Scrapyd web UI with books_scraper listed as a project.

---

### Step 3 - Run Spider via API

```bash
curl http://localhost:6800/schedule.json \
     -d project=books_scraper \
     -d spider=books
```

Response:

```json
{ "status": "ok", "jobid": "abc123..." }
```

---

### Step 4 - Check Job Status

```bash
curl http://localhost:6800/listjobs.json?project=books_scraper
```

---

### Step 5 - Stop Docker

```bash
docker-compose down
```

## Output files are saved locally via Docker volumes:

## Run with Scrapyd Locally

### Step 1 - Start Scrapyd

```bash
scrapyd
```

### Step 2 - Deploy Spider

Open a new terminal:

```bash
source venv/bin/activate
scrapyd-deploy local -p books_scraper
```

### Step 3 - Schedule Spider

```bash
curl http://localhost:6800/schedule.json \
     -d project=books_scraper \
     -d spider=books
```

### Step 4 - Monitor at Browser

---

## Output Format

### JSON

```json
[
  {
    "title": "A Light in the Attic",
    "price": 51.77,
    "availability": true,
    "product_url": "https://books.toscrape.com/catalogue/...",
    "image_url": "https://books.toscrape.com/media/...",
    "category": "Poetry"
  }
]
```

### CSV

### XML

```xml
<items>
    <item>
        <title>A Light in the Attic</title>
        <price>51.77</price>
        <availability>True</availability>
        <product_url>https://...</product_url>
        <image_url>https://...</image_url>
        <category>Poetry</category>
    </item>
</items>
```

---

## Database Schema

| Column       | Type      | Description                    |
| ------------ | --------- | ------------------------------ |
| id           | INTEGER   | Auto-increment primary key     |
| title        | TEXT      | Book title                     |
| price        | REAL      | Price as float e.g. 12.99      |
| availability | INTEGER   | 1 = In stock, 0 = Out of stock |
| product_url  | TEXT      | Book detail page URL           |
| image_url    | TEXT      | Book cover image URL           |
| category     | TEXT      | Book category                  |
| scraped_at   | TIMESTAMP | Time of insertion              |

---

## Design Decisions

**Two separate pipelines** - DataCleaningPipeline handles normalization. SQLitePipeline handles storage. Each has one responsibility and is independently maintainable.

**Random selection at spider level** - random.sample() is used inside the spider so the pipeline stays clean and only handles data processing.

**CSS and XPath both used** - CSS for simple tag and class selections, XPath for text extraction and complex navigation.

**Pagination before selection** - All books are collected across every page of a category before randomly picking 5. This gives true random distribution.

**cb_kwargs for state** - Category name travels through the request chain via cb_kwargs, keeping the spider stateless.

**FEEDS in settings** - All three export formats are configured in settings.py using Scrapy's built-in FEEDS. No custom export code needed.

---

## Known Limitations

- Results differ on every run due to random selection
- SQLite is not suitable for high concurrency
- No deduplication — multiple runs create duplicate records
- No retry logic for failed book pages
- Scrapyd is single node only

---

## Git Branch Strategy

Flow: feature/\* -> dev -> main

---

## Author

Sajib - https://github.com/mollah2022
