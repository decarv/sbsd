"""

"""
import os
import re
import json
import urllib
import logging
import datetime
import sqlite3
import requests
import collections
from queue import Queue
from bs4 import BeautifulSoup


class Crawler:
    """
    A web crawler that fetches and stores webpages from a given base URL.

    Attributes:
        base_url (str): The base URL from which the crawler starts.
        data_path (str): Path to the directory where data will be stored.
        logs_path (str): Path to the directory where logs will be stored.
        errors_path (str): Path to the directory where error logs will be stored.
        database (str): Name of the SQLite database to use for storing webpages.
    """

    def __init__(self, **kwargs):
        """
        Initializes the crawler with necessary parameters and establishes a database connection.

        Args:
            **kwargs: Keyword arguments for configuration parameters.
        """
        logging.basicConfig(
            level=logging.INFO,
            filename=os.path.join(kwargs.get("logs_path"), "crawler.log"),
            filemode="a",
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        self.base_url: str = kwargs.get("base_url")
        self.data_path: str = kwargs.get("data_path", ".")
        self.logs_path: str = kwargs.get("logs_path", ".")
        self.errors_path: str = kwargs.get("errors_path", ".")
        self.database: str = kwargs.get("database", "webpages.db")

        self.errors = collections.defaultdict(lambda: [])
        self.session = requests.Session()
        self.session.headers.update({"Accept-Language": "pt-br,pt-BR"})

        # Establish connection and create table webpages
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS webpages (
                url TEXT PRIMARY KEY,
                webpage BLOB,
                metadata BOOLEAN NOT NULL DEFAULT 0,
                document BOOLEAN NOT NULL DEFAULT 0,
                parsed BOOLEAN NOT NULL DEFAULT 0
            );
        """)
        self.conn.commit()

    def execute(self):
        """
        Executes the web crawling operation, starting from the base URL and traversing its children URLs.
        """
        self.logger.info("started execution")

        queue = Queue()

        visited = set()
        # If database is empty, add base_url to queue, otherwise add all already visited urls
        if self.cursor.execute("SELECT url FROM webpages LIMIT 1").fetchone() is None:
            success = self.database_insert(self.base_url)
            if not success:
                return self.stop()
            queue.put(self.base_url)
            visited.add(self.base_url)
        else:
            res = self.cursor.execute("SELECT url FROM webpages")
            visited_urls = [[_] for _ in res.fetchall()]
            for url in visited_urls:
                queue.put(url)
                visited.add(url)

        # Traverse the website as BFS
        while not queue.empty():
            current: str = queue.get()
            [webpage] = self.database_select_instance(column="url", value=current)
            soup = BeautifulSoup(webpage, "html.parser")

            # Obtain children urls of current webpage
            children = []
            a_tags = soup.find_all("a")
            for a_tag in a_tags:
                url: str = a_tag.attrs.get("href")
                if url is not None:
                    url = urllib.parse.urljoin(self.base_url, url)
                    children.append(url)

            # Traverse children urls
            for child in children:
                parsed_url = urllib.parse.urlparse(child)

                # Ignore the website in other languages
                query: str = parsed_url.query
                if "lang" in query and "lang=pt" not in query:
                    self.logger.warning(f"found lang!=pt: {child}, continuing")
                    continue

                # Ignore links that are not urls
                if parsed_url.scheme and (parsed_url.scheme != "http" or parsed_url.scheme != "https"):
                    self.logger.warning(f"found link!=url: {child}, continuing")
                    continue

                url = urllib.parse.urljoin(self.base_url, child)
                if url not in visited:
                    success = self.database_insert(url)
                    if success:
                        queue.put(url)
                        visited.add(url)

        self.stop()

    def stop(self) -> None:
        """
        Stops the web crawler, closes the database connection and logs the errors encountered during
        execution.
        """
        self.conn.close()
        with open(os.path.join(self.errors_path, "errors_crawler.json"), "w") as f:
            f.write(json.dumps(self.errors))
        self.logger.info(f"Stopping crawler. #Errors: {len(self.errors)}")

    def database_insert(self, url: str) -> bool:
        """
        Fetches the webpage at the given URL and inserts it into the database.

        Args:
            url (str): The URL of the webpage to fetch and insert into the database.

        Returns:
            bool: True if the webpage was successfully inserted into the database, False otherwise.
        """
        response = self.session.get(url)
        if not response.ok:
            self.logger.error(f"unable to obtain {url}. Code: {response.status_code}")
            self.errors["request"].append((url, response.status_code))
            return False

        webpage: bytes = response.content
        metadata: bool = False
        document: bool = False
        if re.search("tde-\d+-\d+", url) is not None:
            if re.search(".pdf$", url) is not None:
                document = True
            else:
                metadata = True
        self.cursor.execute("""
            INSERT INTO webpages VALUES(?, ?, ?, ?, ?)
        """, (url, webpage, metadata, document, 0))
        self.conn.commit()

        self.logger.info(f"successfully inserted {url} to webpages")

        return True

    def database_contains(self, url: str) -> bool:
        """
        Checks if the database contains a webpage at the given URL.
        Args:
            url (str): The URL to check in the database.
        Returns:
            bool: True if the database contains a webpage at the given URL, False otherwise.
        """
        return self.database_select_instance(column="url", value=url) is None

    def database_select_instance(self, column: str, value: str) -> tuple:
        """
        Fetches a row from the database where the given column matches the given value.
        Args:
            column (str): The column to match.
            value (str): The value to match in the column.
        Returns:
            tuple: The row from the database where the column matches the value, or None if no such
            row exists.
        """
        query = f"SELECT * FROM webpages WHERE {column} = ?"
        self.cursor.execute(query, (value, ))
        return self.cursor.fetchone()
