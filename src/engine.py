"""

"""

from processor import Processor
from indexer import Indexer
from searcher import Searcher


class Engine:
    def __init__(self, processor: Processor, indexer: Indexer, searcher: Searcher):
        self.processor = processor
        self.indexer = indexer
        self.searcher = searcher

    # receive_query
    # process_query
    def search_query(self, query: str):
        self.searcher.process_query()
