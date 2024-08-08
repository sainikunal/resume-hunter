from models import Position, City
from bs4 import BeautifulSoup
from hunter import tools 
import storage
from multiprocessing import Pool
import logging

from hunter import Scraper

TOTAL_NUMBER_RESUME_LIMIT = 2_000
CURRENT_POSITION_ID = None
CURRENT_CITY_ID = 0

def find_profession(profession: Position) -> None:
    url = tools.create_query(professionName=profession.title)
    total_number_of_resumes = tools.get_count_of_resumes(url)
    if not total_number_of_resumes: 
        logging.info(f"No resumes found for this query: {url}")
        return
    
    global CURRENT_POSITION_ID
    CURRENT_POSITION_ID = profession.id
    if total_number_of_resumes <= TOTAL_NUMBER_RESUME_LIMIT:
        logging.info(f"Found {total_number_of_resumes} resumes. Searching only in Russia")
        find_profession_in_Russia(profession)
    else:
        logging.info(f"Found {total_number_of_resumes} resumes. Searching in individual cities")
        find_profession_in_all_cities_separately(profession)


def find_profession_in_Russia(profession: Position):
    city = City(name="Russia", edwica_id=0, head_hunter_id=113, rabota_ru="russia")
    find_profession_in_current_city(profession, city)

def find_profession_in_all_cities_separately(profession: Position):
    cities = storage.get_cities()
    for city in cities:
        CURRENT_CITY_ID = city.edwica_id
        logging.info(f"Searching profession in {city.name}")
        find_profession_in_current_city(profession, city)


def find_profession_in_current_city(profession: Position, city: City):
    url = tools.create_query(profession.title, area=city.head_hunter_id)
    pages = tools.get_count_of_pages(url)
    for page in range(pages):
        logging.info(f"Page {page+1} of {pages}")
        scrape_professions_on_page(page=f"{url}&page={page}")


def scrape_professions_on_page(page: str) -> None:
    soup = tools.get_soup(page)
    resumes_block = soup.find("div", class_="resume-serp")
    if not resumes_block: return
    blocks = []

    for block in resumes_block.find_all("div", class_="serp-item"):
        blocks.append(block)
    logging.info(f"Resumes available on page: {len(blocks)}")

    with Pool(10) as process:
        process.map_async(
            func=scrape_resume,
            iterable=blocks,
            error_callback=lambda x: logging.fatal(x))
        process.close()
        process.join()

def scrape_resume(block: BeautifulSoup):
    resume_url = "https://hh.ru" + block.find("a", class_="serp-item__title")["href"]
    resume_date_update = block.find("span", class_="bloko-text bloko-text_tertiary").text.replace("Updated", "").strip()
    resume_scraper = Scraper(resume_url, CURRENT_POSITION_ID, CURRENT_CITY_ID, resume_date_update)
    save(scraper=resume_scraper)
    
def save(scraper: Scraper) -> None:
    saved = storage.add_resume(scraper.get_resume())
    if saved:
        storage.add_additional(scraper.get_additional())
        storage.add_experience(scraper.get_experience())
        storage.add_education(scraper.get_education())
