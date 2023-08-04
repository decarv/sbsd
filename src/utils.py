"""
utils.py

Copyright (c) 2023 Henrique Araújo de Carvalho

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import time
import logging
import sqlite3
from typing import Optional
import requests
import functools

from models import Metadata
from config import DATA_DIR, DATABASE

def log(level=logging.INFO):
    """
    Creates a sort of automatic logging for functions.

    Usage:

        @log(logging.DEBUG)
        def func(a, b):
            ...

    """
    logging.basicConfig(level=level)

    # noinspection PyMissingOrEmptyDocstring
    def inner_decorator(func):
        logger = logging.getLogger(func.__name__)

        # noinspection PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Running {func.__name__}")
                s = time.time()
                ret = func(*args, **kwargs)
                logger.info(f"{func.__name__} took {time.time() - s} seconds")
                return ret
            except Exception as e:
                logger.error(f"Exception raised in function {func.__name__}. Exception: {e}")
                raise e
        return wrapper

    return inner_decorator


def get_request(
        url: str, timeout: int = 5, max_attempts: int = 5, wait_time: float = 10.0
) -> Optional[requests.Response]:
    """
    Abstracts HTTP GET request with requests library, using timeout, max_attempts and wait_time.

    :param url:
    :param timeout:
    :param max_attempts:
    :param wait_time:
    :return: Response or None if the request fails.
    """
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException:
            return None
        if not response.ok:
            # logging.INFO(f"Response code was not 2XX: ({response.status_code=})")
            time.sleep(wait_time)
            continue
        return response

    # logging.warning(f"Failed to request the URI after {max_attempts} attempts")
    return None


def post_request(
        url: str, params: dict, headers: dict, data: dict,
        timeout: int = 5, max_attempts: int = 5, wait_time: float = 5.0
) -> Optional[requests.Response]:
    """
    Abstracts HTTP POST request with requests library, using params, headers, data (payload),
    timeout, max_attempts and wait_time. The function requests cookies before posting.

    :param url:
    :param params:
    :param headers:
    :param data:
    :param timeout:
    :param max_attempts:
    :param wait_time:
    :return: Response or None if the request fails.
    """
    cookies = get_request(url).cookies
    for attempt in range(max_attempts):
        # logging.INFO(f"Making POST request {attempt}/{max_attempts} to resource " + uri)
        try:
            response = requests.post(
                url, params=params, headers=headers, data=data, cookies=cookies, timeout=timeout
            )
        except requests.exceptions.RequestException:
            # logging.ERROR(f"Error making the request")
            return None

        if not response.ok:
            # logging.INFO(f"Response code was not 2XX: ({response.status_code=})")
            time.sleep(wait_time)
            continue
        return response

    # logging.ERROR(f"Failed to request the URI after {max_attempts} attempts")
    return None


@log(logging.DEBUG)
def load_metadata() -> list[Metadata]:
    conn = sqlite3.connect(os.path.join(DATA_DIR, DATABASE))
    res: list[Metadata] = []
    instances = conn.cursor().execute("select * from metadata").fetchall()
    for inst in instances:
        m = Metadata()
