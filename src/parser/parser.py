
class Parser():
    """
    Parser for documents and for metadata webpage
    """



for url in urls:
    self.parse_thesis(url)


def to_json(self):
    return json.dumps(
        {
            k: v.__dict__
            for k, v in self.theses.items()
        }
    )


def store_theses(self):
    full_path = os.path.join(self.data_path, "theses.json")
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    dump_string = self.to_json()
    with open(full_path, "w") as fp:
        fp.write(dump_string)
    self.logger.info(f"Theses stored in file: {full_path}")

def parse_thesis(url):
    webpage = requests.get(url, headers={"Accept-Language": "pt-br,pt-BR"})
    if not webpage.ok:
        logger.warning(f"Error retrieving webpage: {url}")
        return None
    thesis = Thesis()
    thesis.parse_webpage(webpage.content)
    [id] = re.findall("tde-\d+-\d+", url)
    theses[id] = thesis
    logger.info(f"Thesis parsed: {id}")


    def extract_webpages_urls(self, base_url):
        theses_webpages_urls = []
        for page in range(1, self.base_urls[base_url]):
            url = f'{base_url}{page}'
            list_webpage = requests.get(url, headers={"Accept-Language": "pt-br,pt-BR"})
            if list_webpage is None or not list_webpage.ok:
                self.errors.append(url)
                self.logger.warning(f"Error retrieving webpage: {url}")
                continue

            soup = BeautifulSoup(list_webpage.content, 'html.parser')
            elements = soup.select("div.dadosDocNome a")
            urls = [el.get('href') for el in elements]
            for _ in urls:
                theses_webpages_urls.append(_)

            urls_in_page, *_ = self.extract_instances_count(soup)
            logging.info(f"Number of extracted elements in page: {len(urls)}. Expected number of "
                         f"extracted elements {urls_in_page}")
            if len(urls) != urls_in_page:
                logging.warning(f"Unexpected error while extracting webpage urls from {url}")

        return theses_webpages_urls

    def extract_instances_count(self, soup):
        page_info = soup.find(class_="dadosLinha").text
        numbers = re.findall(r"\d+", page_info)
        return list(map(int, numbers))

