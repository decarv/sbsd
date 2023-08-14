import bs4
import random
import requests
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from models.webpage import Webpage
from models.metadata import Metadata
from utils import get_request
from config import RESULT_SIZE
from searcher import Searcher


import config
from searcher import LocalSearcher
from utils import load_embeddings, load_imap, load_metadata_from_csv, log


units_type = "sentences"
language = "pt"
model_name = config.MODELS[1]

data = load_metadata_from_csv()
embeddings = load_embeddings(config.EMBEDDINGS_DIR, model_name=model_name, units_type=units_type, language=language)
encoder_model = SentenceTransformer(model_name, device='cuda', cache_folder=config.MODELS_DIR)
imap = load_imap(config.INDICES_DIR, units_type=units_type, language=language)

searcher = LocalSearcher(
    collection_name="abstracts",
    encoder_model=encoder_model,
    ranking_model=None,
    language=language,
    embeddings=embeddings,
    data=data,
    imap=imap
)

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/app", StaticFiles(directory="app"), name="static")

@app.get("/search")
async def search():
    return FileResponse("app/search.html")

@app.get("/experiment")
async def experiment(query: str):
    """TODO: documentation"""



    half_total_size = config.RESULT_SIZE//2
    website_results: list[dict] = website_query(query, hits_cnt=half_total_size)
    # TODO DEBUG: delete after testing
    html_page = generate_experiment_html(website_results)
    print(html_page)
    return HTMLResponse(content=html_page)

    engine_results: list[dict] = searcher.retrieve(query, hits_cnt=half_total_size)

    wr_idxs = list(range(len(website_results)))
    random.shuffle(wr_idxs)
    er_idxs = list(range(len(engine_results)))
    random.shuffle(er_idxs)

    results: list[list[int, str]] = []
    results_set: set[str] = set()
    for i in range(half_total_size):
        wr_i = wr_idxs[i]
        if website_results[wr_i]['url'] not in results_set:
            results.append([wr_i, website_results[wr_i]])
            results_set.add(website_results[wr_i]['url'])

        er_j = er_idxs[i]
        if engine_results[er_j]['url'] not in results_set:
            results.append([er_j, engine_results[er_j]])
            results_set.add(engine_results[er_j]['url'])

    return generate_experiment_html(results)

def generate_experiment_html(results):
    html_head = """<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Buscador de Teses</title>
    <link rel="stylesheet" type="text/css" href="/app/experiment.css">
</head>
<body>
    <div id="main-container">
        <div id="left-column">"""

    html_body = ""
    for result in results:
        html_body += f"""<div class="draggable" draggable="true">
            <b>Título</b>: {result['title_pt']} <br>
            <b>Resumo</b>: {result['abstract_pt']} <br>
            <b>Autor</b>: {result['author']} <br>
        </div>"""

    html_tail = """        </div>
        <div id="right-column" ondragover="allowDrop(event)" ondrop="drop(event)">
            <!-- This is where items will be dropped -->
        </div>
    </div>
    <script src="/app/experiment.js"></script>
</body>
</html>"""
    return html_head + html_body + html_tail


@log
def website_query(query, hits_cnt=30) -> list[dict]:
    """TODO: documentation"""
    formatted_theses_query_url: str = config.THESES_QUERY_URL.format(query.replace(" ", "%20"))
    metadata_urls: list[str] = []
    page = 1
    while len(metadata_urls) < hits_cnt:
        url = formatted_theses_query_url + str(page)
        import requests
        response: requests.Response = requests.get(url)
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

        page += 1

    results: list[dict] = []
    for url in metadata_urls[:hits_cnt]:
        webpage = Webpage(url)
        webpage.process()
        results.append(Metadata(webpage).to_dict())

    return results

def engine_query(query, searcher: Searcher) -> list[dict]:
    """TODO: documentation"""
    ...