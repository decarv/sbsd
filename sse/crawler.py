
import os
import sys
import logging
import sqlite3
import requests
from queue import Queue

import config
from models.webpage import Webpage
from models.metadata import Metadata


class Crawler:
    def __init__(self, **kwargs):
        """
        Initializes the crawler with necessary parameters and establishes a database connection.
        """
        self.logger: logging.Logger
        self.conn: sqlite3.Connection
        self.cursor: sqlite3.Cursor
        self.err_conn: sqlite3.Connection
        self.err_cursor: sqlite3.Cursor

        self._logging_setup(kwargs.get("logs_path"))

        self.logger.info("INITIATING CRAWLER")

        db_path: str = os.path.join(
            kwargs.get("data_path", "."),
            kwargs.get("db_name", "webpages.db")
        )
        self._database_setup(db_path)

        err_db_path: str = os.path.join(
            kwargs.get("err_path", "."),
            kwargs.get("err_db_name", "errors.db")
        )
        self._err_database_setup(err_db_path)

        # session setup
        self.session = requests.Session()
        self.session.headers.update({"Accept-Language": "pt-br,pt-BR"})

    def start(self) -> None:

        self.logger.info("CRAWLER STARTED")

        queue: Queue[Webpage] = Queue()  # Queue to crawl
        queued: set[Webpage] = set()
        self._execute_preprocess(queue, queued)

        # Traverse the website as BFS
        while not queue.empty():
            webpage: Webpage = queue.get()
            self.logger.info(f"SCRAPING URL: {webpage.url}.")
            if not webpage.is_document:
                if webpage.is_metadata:
                    self._database_insert_metadata(Metadata(webpage))

                for hyperlink in webpage.children_hyperlinks():
                    child_webpage = Webpage(hyperlink)
                    if child_webpage.errors:
                        self._err_database_insert(webpage.url, str(webpage.errors))
                        continue

                    if child_webpage.is_crawlable and child_webpage not in queued:
                        success = self._database_insert_webpage(child_webpage)
                        if success:
                            self.logger.info(f"NEW CHILD URL INSERTED IN DATABASE: {webpage.url}")
                            queued.add(child_webpage)
                            if not child_webpage.is_document:
                                self.logger.info(f"CHILD URL ENQUEUED")
                                queue.put(child_webpage)
            self._database_update_crawled(webpage)
            webpage.delete_cache()

    def stop(self, exit_code=0) -> None:
        self.logger.info("STOPING CRAWLER")
        self.conn.close()
        self.err_conn.close()
        sys.exit(exit_code)

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
                doi TEXT,
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
            success, err = self._database_insert_webpage(config.BASE_URL)
            if not success:
                self.logger.error("Execute preprocess error: 'Could not insert to database'")
                self.stop(1)
            webpage = Webpage(config.BASE_URL)
            queue.put(webpage)
            queued.add(webpage)
        else:
            self.logger.info("Database not empty. Adding visited urls to visited set and to queue.")
            query = self.cursor.execute("SELECT url, crawled FROM webpages")
            for url, crawled in query.fetchall():
                webpage = Webpage(url)
                queued.add(webpage)
                if not crawled:
                    queue.put(webpage)

    def _database_select_instance(self, column: str, value: str) -> tuple:
        query = f"SELECT * FROM webpages WHERE {column} = ?"
        self.cursor.execute(query, (value, ))
        return self.cursor.fetchone()

    def _database_update_crawled(self, webpage: Webpage) -> None:
        self.cursor.execute("""UPDATE webpages SET crawled = 1 WHERE url = ?;""", (webpage.url,))
        self.conn.commit()

    def _err_database_setup(self, err_db_path: str) -> None:
        self.err_conn = sqlite3.connect(err_db_path)
        self.err_cursor = self.err_conn.cursor()
        self.err_cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawler (
                url TEXT PRIMARY KEY,
                error TEXT
            );
        """)

    def _err_database_insert(self, url: str, error: str) -> None:
        try:
            self.err_cursor.execute("INSERT INTO crawler VALUES(?, ?)", (url, error))
            self.err_conn.commit()
        except Exception as e:
            self.logger.error(f"Unable to store error in error database. Error: {e}.")

    def _database_insert_webpage(self, webpage: Webpage) -> bool:
        try:
            self.cursor.execute("INSERT INTO webpages VALUES(?, ?, ?, ?)",
                                (webpage.url, webpage.is_metadata, webpage.is_document, 0)  # crawled = 0
                                )
            self.conn.commit()
            return True
        except Exception as e:
            self.logger.error(f"Unable to store {webpage.url} in database. Error: {e}")
            self._err_database_insert(webpage.url, f"{e}")
            return False

    def _database_insert_metadata(self, metadata: Metadata) -> bool:
        try:
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
            return True
        except Exception as e:
            self.logger.error(f"Unable to store metadata for {metadata.url} in database. Error: {e}")
            self._err_database_insert(metadata.url, f"{e}")
            return False


if __name__ == "__main__":
    crawler = Crawler(
        data_path=config.DATA_PATH,
        logs_path=config.LOGS_PATH,
        err_path=config.ERRORS_PATH,
        db_name=config.WEBPAGES_DATABASE,
        err_db_name=config.ERRORS_DATABASE,
    )
    crawler.start()
    crawler.stop()
