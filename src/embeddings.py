
import re
from utils import log


def split_by_delimiters(string, delimiters: list[str] | str) -> list[str]:
    """
    Splits the given string by one or multiple delimiters.

    Args:
        string: The string to be split.
        delimiters: A string or list of strings used as delimiters.

    Returns:
        A list of substrings.
    """
    if isinstance(delimiters, list):
        pattern = r"|".join(delimiters)
    else:
        pattern = r"{}".format(delimiters)
    return re.split(pattern, string)


def split_keywords(string: str) -> list[str]:
    """
    Splits a given string of keywords.

    Parameters:
        - string (str): The string to split.

    Returns:
        - list[str]: List of keywords.
    """
    keywords: list[str] = []
    keyword = ""
    for word in string.split():
        if word[0].isupper():
            print(word)
            if keyword != "":
                keywords.append(keyword.strip())
            keyword = word
        else:
            keyword += " " + word
    keywords.append(keyword)
    return keywords


def strip_strings(lst: list[str]) -> list[str]:
    """
    Removes leading and trailing whitespace from each string in the given list.

    Args:
        strings: A list of strings.

    Returns:
        The same list with whitespace stripped from each string.
    """
    for i, s in enumerate(lst):
        lst[i] = s.strip()
    return lst


def remove_empty_strings(lst: list[str]) -> list[str]:
    """
    Removes empty strings from the given list of strings.

    Args:
        strings: A list of strings.

    Returns:
        A new list with empty strings removed.
    """
    empty_filtered_lst = [s for s in lst if s != '']
    return empty_filtered_lst


def clean_embedding_units(lst: list[str]) -> list[str]:
    lst = strip_strings(lst)
    lst = remove_empty_strings(lst)
    return lst


def generate_embedding_units(title: str, abstract: str, keywords: str) -> dict[str, list[str]]:
    """
    Generate various textual groupings to serve as inputs for embeddings.

    Parameters:
        - title (str): Document title.
        - abstract (str): Document abstract.
        - keywords (str): Document keywords.

    Returns:
        - dict: Dictionary containing:
            "sentences" -> List of sentences as units to be vectorized.
            "text" -> List containing the whole concatenated text.
            "sentences_and_text" -> Combined list of sentences and the entire text.
    """

    sentences = clean_embedding_units(
        title.split(".") + split_keywords(keywords) + abstract.split(".")
        )
    text = clean_embedding_units([title + ". " + abstract + " " + keywords])
    sentence_and_text = sentences + text

    return {
        # "words": (title + abstract + keywords).replace(".", "").split(" "),
        "sentences": sentences,
        "text": text,
        "sentences_and_text": sentences + text
    }


@log
def structure_data_for_embedding(data):
    """
    Prepare the entire dataset for generating embeddings.

    Parameters:
        - data: Input data containing 'title_pt', 'abstract_pt', and 'keywords_pt'.

    Returns:
        - dict: Dictionary structured as:
            {
                "text/sentences/sentences_and_text": {
                    "indices": List mapping single encode input to the index in data.
                    "embedding_units": List of text units for encoding.
                }
            }
    """
    data_for_processing = {
        k: {"indices": [], "embedding_units": []} for k in
        ["text", "sentences", "sentences_and_text"]
    }

    for index, row in data.iterrows():
        embedding_units = generate_embedding_units(
            row["title_pt"], row["abstract_pt"], row["keywords_pt"]
            )
        # for k in inputs.keys():
        #     data_for_processing[k]["embedding_units"] += embedding_units[k]
        #     data_for_processing[k]["indices"] += [index for _ in range(len(embedding_units[k]))]

    return data_for_processing


def tf_idf(document_collection: list):
    """
    Receives a document
    """
    pass


def compute_term_doc_co_occurence_matrix(document_collection: list[str]):
    """
    Receives a document collection and computes the term-document co-occurence matrix.
    """
    doc_by_term = {}
    term_by_doc = {}
    pass