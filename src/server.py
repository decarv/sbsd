import bs4
import random
import requests
from fastapi import FastAPI

from models.webpage import Webpage
from models.metadata import Metadata
from utils import get_request
from config import THESES_QUERY_URL, RESULT_SIZE
from searcher import Searcher


class Server:
    """
    TODO: documentation
    """
    def __init__(self, search_client: Searcher):
        self.search_client = search_client
        self.app = FastAPI()

        @self.app.get("/search")
        async def search(query: str):
            """

            :param query:
            :return:
            """
            website_results: list[dict] = self.website_query(query)
            engine_results: list[dict] = self.engine_query(query)
            random.shuffle(website_results)
            random.shuffle(engine_results)

            results: list[list[int, str]] = []
            results_set: set[str] = set()
            i = j = 0
            while len(results) < RESULT_SIZE and i < len(website_results) and j < len(engine_results):
                if website_results[i]['doi'] not in results_set:
                    results.append([i, website_results[i]])
                    results_set.add(website_results[i]['url'])
                i += 1

                if engine_results[j] not in results_set:
                    results.append([j, engine_results[j]])
                    results_set.add(engine_results[j]['url'])
                j += 1

            return {
                "result": results
            }

    @staticmethod
    def website_query(query) -> list[dict]:
        """
        TODO: documentation
        """
        formatted_theses_query_url: str = THESES_QUERY_URL.format(query.replace(" ", "%20"))
        metadata_urls: list[str] = []
        for page in range(1, 4):
            url = formatted_theses_query_url + str(page)
            response: requests.Response = get_request(url)
            if response is not None:
                soup = bs4.BeautifulSoup(response.content, 'html.parser')
                divs = soup.find_all(
                    "div",
                    class_=["dadosLinha dadosCor1", "dadosLinha dadosCor2"]
                )
                metadata_urls += [div.a['href'] for div in divs]
            else:
                # TODO
                pass

        results: list[dict] = []
        for url in metadata_urls:
            webpage = Webpage(url)
            webpage.process()
            results.append(Metadata(webpage).to_dict())

        return results

    def engine_query(self, query) -> list[dict]:
        """
        TODO: documentation
        """
        results: list[dict] = self.search_client.retrieve(query)
        return results
