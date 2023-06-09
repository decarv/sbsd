
import re
import urllib
import urllib.parse
import requests
from typing import Optional
from bs4 import BeautifulSoup

import config


class Webpage:
    def __init__(self, link: str):
        self.errors = {}

        self.url: str
        self.parsed_url: urllib.parse.ParseResult
        self.is_crawlable: bool

        self._preprocess(link)

        if self.is_crawlable:
            self.html: Optional[bytes] = None
            self.soup: Optional[BeautifulSoup] = None
            self.is_document: bool
            self.is_metadata: bool
            self.children_hyperlinks = []

            self._process()

    def _preprocess(self, link):
        if "//" == link[0:2]:
            link = link[2:]
        parsed_link = urllib.parse.urlparse(link)

        # Ignore external webpages
        if parsed_link.netloc not in config.BASE_URL or "".join(parsed_link.netloc.split("www.")) not in config.BASE_URL:
            self.is_crawlable = False
        # Ignore webpages in other languages
        elif "lang" in parsed_link.query and "lang=pt" not in parsed_link.query:
            self.is_crawlable = False
        # Ignore hrefs that are not urls
        elif parsed_link.scheme and parsed_link.scheme != "http" and parsed_link.scheme != "https":
            self.is_crawlable = False
        else:
            self.url = urllib.parse.urljoin(config.BASE_URL, link)
            self.parse_url = urllib.parse.urlparse(self.url)
            self.is_crawlable = True

    def _process(self):
        document_pattern: str = r"\.[A-z|0-9]+$"
        metadata_pattern: str = r"tde-\d+-\d+"
        self.is_document = re.search(document_pattern, self.url) is not None
        self.is_metadata = re.search(metadata_pattern, self.url) is not None and not self.is_document

        if not self.is_document:
            self._get_html()
            if self.html:
                self._get_soup()
                self._get_children_hyperlinks()

            if not self.is_metadata:
                self.delete_cache()

    def _get_children_hyperlinks(self):
        a_tags = self.soup.find_all("a")
        for a_tag in a_tags:
            hyperlink: str = a_tag.attrs.get("href")
            if hyperlink is not None:
                self.children_hyperlinks.append(hyperlink)

    def _get_html(self):
        try:
            response = requests.get(self.url)
            if response.ok:
                self.html = response.content
            else:
                self.errors["cache_html"] = f"Bad request: Status Code: {response.status_code}"
        except Exception as e:
            self.errors["cache_html"] = e

    def _get_soup(self):
        try:
            self.soup = BeautifulSoup(self.html, "html.parser")
        except Exception as e:
            self.errors["cache_soup"] = e

    def delete_cache(self):
        self.html = None
        self.soup = None

    def __hash__(self):
        if self.html:
            return hash(self.html)
        return hash(self.url)

    def __eq__(self, other):
        if not isinstance(other, Webpage):
            raise TypeError(f"Comparing Webpage object with {type(other)}")
        return self.url == other.url
