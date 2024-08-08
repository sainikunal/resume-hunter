# Translated version of the provided Python code from Russian to English

from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import re
import logging

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

def create_query(professionName: str, area: int = 113) -> str:
    params = {
        "area": area,
        "pos": "position",
        "text": professionName,
        "no_magic": False,
        "order_by": "relevance",
        "exp_period": "all_time",
        "logic": "normal",
        "search_period": 0,
        "items_on_page": 20,
        }
    url = f"https://hh.ru/search/resume?" + urlencode(params)
    return url

def get_count_of_resumes(url: str) -> int:
    try:
        soup = get_soup(url)
        text = soup.find("div", class_="resume-search-header").text.replace(u"\xa0", u"")
        found = re.findall("Found.*?resumes", text)
        return int(re.findall("\d+", found[0])[0])
    except BaseException as err:
        logging.error(f"Error counting resumes at '{url}'. Error: {err}")
        return 0

def get_soup(url: str) -> BeautifulSoup:
    try:
        req = requests.get(url, headers=headers)
    except BaseException as err:
        logging.error(f"Failed to send request to: {url}\nError text:{err}")
    soup = BeautifulSoup(req.text, 'lxml')
    return soup

def get_count_of_pages(url: str) -> int:
    """Will always return at least one"""
    soup = get_soup(url)
    try:
        count = int(soup.find_all("a", attrs={"data-qa": "pager-page"})[-1].text)
    except BaseException as err:
        count = 1
        logging.error(f"Failed to count the number of pages: {err} {url}")
    finally:
        return count
