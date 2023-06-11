
import re
import urllib
import urllib.parse
import requests
from typing import Optional, Any
from bs4 import BeautifulSoup

import config


class Webpage:
    def __init__(self, link: str):

        self.url: str = link
        self.is_crawlable: bool = False
        self.html: Optional[bytes] = None
        self.soup: Optional[BeautifulSoup] = None
        self.is_document: bool = False
        self.is_metadata: bool = False
        self.children_hyperlinks: list = []


        self._preprocess(link)

    def _preprocess(self, link):
        if link[0:2] == "//":
            link = link[2:]

        # TODO: self.parsed_url does not need to be an object variable
        self.parsed_url: urllib.parse.ParseResult = urllib.parse.urlparse(link)

        # Ignore external webpages
        if self.parsed_url.netloc not in config.BASE_URL or "".join(self.parsed_url.netloc.split("www.")) not in config.BASE_URL:
            self.is_crawlable = False
        # Ignore webpages in other languages
        elif "lang" in self.parsed_url.query and "lang=pt" not in self.parsed_url.query:
            self.is_crawlable = False
        # Ignore hrefs that are not urls
        elif self.parsed_url.scheme and self.parsed_url.scheme != "http" and self.parsed_url.scheme != "https":
            self.is_crawlable = False
        # All the good urls fall here
        else:
            self.url = urllib.parse.urljoin(config.BASE_URL, link)

            # Clean some bad urls
            if self.url.endswith("pt-br.php"):
                self.url = self.url.removesuffix("pt-br.php")

            self.parsed_url = urllib.parse.urlparse(self.url)

            webfiles = [".html", ".php"]
            document_pattern: str = r"\.[A-z|0-9]+$"
            document_pattern_search = re.search(document_pattern, self.url)
            self.is_document = document_pattern_search is not None and document_pattern_search.group() not in webfiles

            metadata_pattern: str = r"tde-\d+-\d+"
            self.is_metadata = re.search(metadata_pattern, self.url) is not None and not self.is_document

            self.is_crawlable = not self.is_document

    def process(self, session: Optional[requests.Session] = None) -> None:
        self._get_html()
        if self.html:
            self._get_soup()
            self._get_children_hyperlinks()

    def _get_children_hyperlinks(self):
        a_tags = self.soup.find_all("a")
        for a_tag in a_tags:
            hyperlink: str = a_tag.attrs.get("href")
            if hyperlink is not None:
                self.children_hyperlinks.append(hyperlink)

    def _get_html(self, session: Optional[requests.Session] = None) -> None:
        try:
            if session is not None:
                response = session.get(self.url)
            else:
                response = requests.get(self.url)
            if response.ok:
                self.html = response.content
            else:
                raise Exception(f"Bad request: Status Code: {response.status_code}")
        except Exception as e:
            raise e

    def _get_soup(self):
        try:
            self.soup = BeautifulSoup(self.html, "html.parser")
        except Exception as e:
            raise e

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

    def __repr__(self):
        return f"{self.url}"