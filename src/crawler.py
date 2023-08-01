
import os
import sys
import chardet
import logging
import sqlite3
import requests
from queue import Queue
from bs4 import BeautifulSoup
from typing import Optional

import config
from models.webpage import Webpage
from models.metadata import Metadata


class Crawler:
    """TODO"""
    def __init__(self, **kwargs):
        """
        Initializes the crawler with necessary parameters and establishes a database connection.
        """
        self.logger: logging.Logger
        self.session: requests.Session
        self.conn: sqlite3.Connection
        self.cursor: sqlite3.Cursor
        self.err_conn: sqlite3.Connection
        self.err_cursor: sqlite3.Cursor

        self._logging_setup(kwargs.get("logs_path"))

        self.logger.info("Initializing crawler config")

        self._session_setup()

        db_path: str = os.path.join(kwargs.get("data_path", "."), kwargs.get("db_name", "webpages.db"))
        self._database_setup(db_path)

        err_db_path: str = os.path.join(kwargs.get("err_path", "."), kwargs.get("err_db_name", "errors.db"))
        self._err_database_setup(err_db_path)

    def start(self) -> None:
        self.logger.info("Started Crawler.")

        queue: Queue[Webpage] = Queue()  # Queue to crawl
        queued: set[Webpage] = set()
        self._execute_preprocess(queue, queued)

        while not queue.empty():
            webpage: Webpage = queue.get()

            try:
                self.logger.info(f"Processing Webpage object: {webpage}.")
                webpage.process(self.session)
            except Exception as e:
                self.logger.error(f"Error while processing webpage: {webpage.url}")
                self._err_database_insert(webpage.url, str(e))
                continue

            if webpage.is_crawlable:
                if webpage.is_metadata:
                    metadata = Metadata(webpage)
                    try:
                        self._database_insert_metadata(metadata)
                    except Exception as e:
                        self.logger.error(f"Unable to store metadata for {metadata.url} in database. Error: {e}")
                        self._err_database_insert(metadata.url, f"{e}")
                        continue

                for hyperlink in webpage.children_hyperlinks:
                    child_webpage: Webpage = Webpage(hyperlink)
                    if child_webpage.is_crawlable and child_webpage not in queued:
                        try:
                            self.logger.info(f"Inserting in database: {webpage.url}")
                            self._database_insert_webpage(webpage)
                            queue.put(child_webpage)
                            queued.add(child_webpage)
                        except Exception as e:
                            self.logger.error(f"Could not insert in database: {child_webpage.url}")
                            self._err_database_insert(child_webpage.url, str(e))
            self._database_update_crawled(webpage)

    def crawl_sitemap(self):
        self.logger.info("Started Sitemap Crawler")
        sitemap_urls = [
            'https://www.teses.usp.br/sitemap/sitemap01.xml',
            'https://www.teses.usp.br/sitemap/sitemap02.xml',
            'https://www.teses.usp.br/sitemap/sitemap03.xml',
            'https://www.teses.usp.br/sitemap/201905.xml',
            'https://www.teses.usp.br/sitemap/201906.xml',
            'https://www.teses.usp.br/sitemap/201907.xml',
            'https://www.teses.usp.br/sitemap/201908.xml',
            'https://www.teses.usp.br/sitemap/201909.xml',
            'https://www.teses.usp.br/sitemap/201910.xml',
            'https://www.teses.usp.br/sitemap/201911.xml',
            'https://www.teses.usp.br/sitemap/201912.xml',
            'https://www.teses.usp.br/sitemap/202001.xml',
            'https://www.teses.usp.br/sitemap/202002.xml',
            'https://www.teses.usp.br/sitemap/202003.xml',
            'https://www.teses.usp.br/sitemap/202004.xml',
            'https://www.teses.usp.br/sitemap/202005.xml',
            'https://www.teses.usp.br/sitemap/202006.xml',
            'https://www.teses.usp.br/sitemap/202007.xml',
            'https://www.teses.usp.br/sitemap/202008.xml',
            'https://www.teses.usp.br/sitemap/202009.xml',
            'https://www.teses.usp.br/sitemap/202010.xml',
            'https://www.teses.usp.br/sitemap/202011.xml',
            'https://www.teses.usp.br/sitemap/202012.xml',
            'https://www.teses.usp.br/sitemap/202101.xml',
            'https://www.teses.usp.br/sitemap/202102.xml',
            'https://www.teses.usp.br/sitemap/202103.xml',
            'https://www.teses.usp.br/sitemap/202104.xml',
            'https://www.teses.usp.br/sitemap/202105.xml',
            'https://www.teses.usp.br/sitemap/202106.xml',
            'https://www.teses.usp.br/sitemap/202107.xml',
            'https://www.teses.usp.br/sitemap/202108.xml',
            'https://www.teses.usp.br/sitemap/202109.xml',
            'https://www.teses.usp.br/sitemap/202110.xml',
            'https://www.teses.usp.br/sitemap/202111.xml',
            'https://www.teses.usp.br/sitemap/202112.xml',
            'https://www.teses.usp.br/sitemap/202201.xml',
            'https://www.teses.usp.br/sitemap/202202.xml',
            'https://www.teses.usp.br/sitemap/202203.xml',
            'https://www.teses.usp.br/sitemap/202204.xml',
            'https://www.teses.usp.br/sitemap/202205.xml',
            'https://www.teses.usp.br/sitemap/202206.xml',
            'https://www.teses.usp.br/sitemap/202207.xml',
            'https://www.teses.usp.br/sitemap/202208.xml',
            'https://www.teses.usp.br/sitemap/202209.xml',
            'https://www.teses.usp.br/sitemap/202210.xml',
            'https://www.teses.usp.br/sitemap/202211.xml',
            'https://www.teses.usp.br/sitemap/202212.xml',
            'https://www.teses.usp.br/sitemap/202301.xml',
            'https://www.teses.usp.br/sitemap/202302.xml',
            'https://www.teses.usp.br/sitemap/202303.xml',
            'https://www.teses.usp.br/sitemap/202304.xml',
            'https://www.teses.usp.br/sitemap/202305.xml',
            'https://www.teses.usp.br/sitemap/202306.xml'
        ]

        queue: Queue[Webpage] = Queue()  # Queue to crawl
        for url in sitemap_urls:
            try:
                response = self.session.get(url)
                if not response.ok:
                    raise Exception(f"Request Error @ url {url}. Status Code: {response.status_code}")
                encoding = chardet.detect(response.content)['encoding']
                response.encoding = encoding

                self.logger.info(f"Parsing url: {url}")
                xml_soup = BeautifulSoup(response.content, "xml")
            except Exception as e:
                self.logger.error(f"Error while requesting and parsing: {url}")
                self._err_database_insert(url, str(e))
                continue

            for child_url in (loc.text for loc in xml_soup.find_all("loc")):
                try:
                    webpage = Webpage(child_url)
                    if not self._database_contains_webpage(webpage.url):
                        self.logger.info(f"Inserting in database: {webpage.url}")
                        self._database_insert_webpage(webpage)
                    else:
                        self.logger.info(f"Database already contains url: {child_url}. Continuing.")

                    if not self._database_contains_metadata(webpage.url):
                        self.logger.info(f"Queueing: {child_url}")
                        queue.put(webpage)
                except Exception as e:
                    self.logger.error(f"Could not parse webpage: {child_url}")
                    self._err_database_insert(child_url, str(e))

        while not queue.empty():
            webpage: Webpage = queue.get()
            try:
                self.logger.info(f"Processing Webpage object: {webpage}.")
                webpage.process(self.session)
            except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
                self.logger.error(f"Error while requesting url: {webpage.url}. Error: {e}")
                self._err_database_insert(webpage.url, str(e))
                self._session_setup()
                webpage.delete_cache()
                queue.put(webpage)
                continue
            except Exception as e:
                self.logger.error(f"Error while processing webpage: {webpage.url}")
                self._err_database_insert(webpage.url, str(e))
                continue

            if webpage.is_metadata:
                try:
                    metadata: Metadata = Metadata(webpage)
                except Exception as e:
                    self.logger.error(f"Unable to parse metadata for {webpage.url}. Error: {e}")
                    self._err_database_insert(webpage.url, f"{e}")
                    continue

                try:
                    self._database_insert_metadata(metadata)
                except Exception as e:
                    self.logger.error(f"Unable to store metadata for {metadata.url} in database. Error: {e}")
                    self._err_database_insert(metadata.url, f"{e}")
                    continue

            self._database_update_crawled(webpage)

    def stop(self, exit_code=0) -> None:
        self.logger.info("Stoping crawler")
        self.conn.close()
        self.err_conn.close()
        sys.exit(exit_code)

    def _session_setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept-Language": "pt-br,pt-BR"})

    def _logging_setup(self, logs_path):
        logging.basicConfig(
            level=logging.INFO,
            filename=os.path.join(logs_path, "crawler.log"),
            filemode="a",
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def _database_setup(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS webpages (
                url TEXT PRIMARY KEY,
                metadata BOOLEAN NOT NULL DEFAULT 0,
                document BOOLEAN NOT NULL DEFAULT 0,
                crawled BOOLEAN NOT NULL DEFAULT 0
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                url TEXT PRIMARY KEY,
                doi TEXT UNIQUE,
                type TEXT,
                author TEXT,
                institute TEXT,
                knowledge_area TEXT,
                committee TEXT,
                title_pt TEXT,
                title_en TEXT,
                keywords_pt TEXT,
                keywords_en TEXT,
                abstract_pt TEXT,
                abstract_en TEXT,
                publish_date TEXT
            );
        """)
        self.conn.commit()

    def _execute_preprocess(self, queue: Queue[Webpage], queued: set[Webpage]):
        if self.cursor.execute("SELECT url FROM webpages LIMIT 1").fetchone() is None:
            self.logger.info("Database empty. Starting crawl from config.BASE_URL.")
            webpage = Webpage(config.BASE_URL)
            try:
                self._database_insert_webpage(webpage)
            except Exception as e:
                self.logger.error(f"Execute preprocess error: 'Could not insert to database': {e}")
                self.stop(1)
            queue.put(webpage)
            queued.add(webpage)
        else:
            self.logger.info("Database not empty. Adding visited urls to visited set and to queue.")
            query = self.cursor.execute("SELECT url, crawled FROM webpages;")
            for url, crawled in query.fetchall():
                webpage = Webpage(url)
                queued.add(webpage)
                if not crawled:
                    queue.put(webpage)

    def _database_select_instance(self, table: str, column: str, value: str) -> Optional[tuple]:
        query = f"SELECT * FROM {table} WHERE {column} = ?;"
        self.cursor.execute(query, (value, ))
        return self.cursor.fetchone()

    def _database_contains_webpage(self, url: str) -> bool:
        return self._database_select_instance("webpages", "url", url) is not None

    def _database_contains_metadata(self, url: str) -> bool:
        return self._database_select_instance("metadata", "url", url) is not None

    def _database_update_crawled(self, webpage: Webpage) -> None:
        self.cursor.execute("""UPDATE webpages SET crawled = 1 WHERE url = ?;""", (webpage.url,))
        self.conn.commit()

    def _err_database_setup(self, err_db_path: str) -> None:
        self.err_conn = sqlite3.connect(err_db_path)
        self.err_cursor = self.err_conn.cursor()
        self.err_cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                error TEXT
            );
        """)

    def _err_database_insert(self, url: str, error: str) -> None:
        try:
            self.err_cursor.execute("INSERT INTO crawler VALUES(?, ?)", (url, error))
            self.err_conn.commit()
        except Exception as e:
            self.logger.error(f"Unable to store error in error database. Error: {e}.")

    def _database_insert_webpage(self, webpage: Webpage) -> None:
        self.cursor.execute(
            "INSERT INTO webpages VALUES(?, ?, ?, ?)",
            (webpage.url, webpage.is_metadata, webpage.is_document, 0)  # crawled = 0
        )
        self.conn.commit()

    def _database_insert_metadata(self, metadata: Metadata) -> None:
        self.cursor.execute("""
            INSERT INTO metadata (
                url, 
                doi, 
                type, 
                author, 
                institute, 
                knowledge_area, 
                committee, 
                title_pt, 
                title_en, 
                keywords_pt, 
                keywords_en, 
                abstract_pt, 
                abstract_en, 
                publish_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata.url,
            metadata.doi,
            metadata.type,
            metadata.author,
            metadata.institute,
            metadata.knowledge_area,
            metadata.committee,
            metadata.title_pt,
            metadata.title_en,
            metadata.keywords_pt,
            metadata.keywords_en,
            metadata.abstract_pt,
            metadata.abstract_en,
            metadata.publish_date
        ))
        self.conn.commit()


if __name__ == "__main__":
    crawler = Crawler(
        data_path=config.DATA_DIR,
        logs_path=config.LOGS_DIR,
        err_path=config.ERRORS_DIR,
        db_name=config.WEBPAGES_DATABASE,
        err_db_name=config.ERRORS_DATABASE,
    )
    # crawler.start()
    crawler.crawl_sitemap()
    crawler.stop()
