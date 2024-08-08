import re
from typing import NamedTuple

from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

from models import Education, Resume, ExperienceStep

class Salary(NamedTuple):
    amount: int
    currency: str

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

# FIXME: Format the salary and convert it to rubles

class Scraper:
    def __init__(self, url: str, position_id: int, city_id: int, date_update: str = ""):
        self.url = re.split("\?.*?", url)[0]
        self.date_update = date_update
        self.position_id = position_id
        self.city_id = city_id
        self.soup = self.__get_soup()
        self.id = self.__get_id()

        self.tags_education = {
            "item": {
                "attr": "class",
                "name": "resume-block-item-gap",  
            },
            "item_list": {
                "attr": "class",
                "name": "resume-block-item-gap",
            },
            "title": {
                "attr": "data-qa",
                "name": "resume-block-education-name",
            },
            "organization": {
                "attr": "data-qa",
                "name": "resume-block-education-organization",
            },
            "year": {
                "attr": "class",
                "name": "bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2",
            },
        }

    def get_resume(self) -> Resume:
        return Resume(
            id=self.id,
            url=self.url,
            position_id=self.position_id,
            date_update=self.date_update,
            city_id=self.city_id,
            city=self.__get_city(),
            title=self.__get_title(),
            skills=self.__get_skills(),
            salary=self.__get_salary().amount,
            currency=self.__get_salary().currency,
            languages=self.__get_languages(),
            specialization=self.__get_specializations(),
            experience_duration=self.__get_experience_term_in_months(),
        )

    def get_experience(self) -> list[ExperienceStep]:
        experience: list[ExperienceStep] = []
        experience_soup: BeautifulSoup = self.soup
        
        if experience_soup.find('span', class_='resume-industries__open'):
            experience_soup = self.__open_all_branches(self.url)
        
        blocks = experience_soup.find(attrs={'data-qa': 'resume-block-experience', 'class': 'resume-block'})
        if not blocks: return []
        for block in blocks.find_all('div', class_='resume-block-item-gap')[1:]:
            step = self.__get_step(block)
            experience.append(step)
        return experience        
    
    def get_education(self) -> list[Education]:
        education_list: list[Education] = []
        try:
            education_block = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(
                'div', attrs={self.tags_education["item_list"]["attr"]: self.tags_education["item_list"]["name"]}).find_all(
                    'div', attrs={self.tags_education["item"]["attr"]: self.tags_education["item"]["name"]})
            if education_block: 
                education_list = self.__parse_vuz(education_block)
            else: 
                middle_education = self.__parse_middle_education()
                if middle_education:
                    education_list.append(middle_education)
        except BaseException as error:
            print("Error parsing education ", error)
        finally:
            return education_list
    
    def get_additional(self) -> list[Education]:
        additional: list[Education] = []
        block = self.soup.find('div', attrs={'data-qa': 'resume-block-additional-education', 'class':'resume-block'})
        if not block: return self.__get_attestation()
        for item in block.find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap'):
            additional.append(Education(
                resume_id=self.id,
                title=item.find(attrs={self.tags_education["title"]["attr"]: self.tags_education["title"]["name"]}).text,
                direction=item.find(attrs={self.tags_education["organization"]["attr"]: self.tags_education["organization"]["name"]}).text,
                year_of_release=re.sub(" ", "", item.find('div', attrs={self.tags_education["year"]["attr"]: self.tags_education["year"]["name"]}).text)
            ))        
        return additional
    
    
    def __get_soup(self) -> BeautifulSoup:
        try:
            req = requests.get(self.Url, headers=headers)  # headers must be defined elsewhere
            return BeautifulSoup(req.text, 'lxml')
        except BaseException as err:
            exit(err)
            # logger.error(f"Failed to send request to: {url}\nError text:{err}")

    def __get_id(self) -> str:
        return re.sub('.*?resume\/|\?.*', '', self.Url)

    def __get_title(self) -> str:
        try:
            title = self.soup.find(attrs={'data-qa': 'resume-block-title-position', 'class': 'resume-block__title-text'}).text
        except BaseException:
            title = ''
        return title

    def __get_salary(self) -> Salary:
        try:
            text = self.soup.find('span', class_='resume-block__salary').text.replace("\u2009", "").replace("\xa0", " ")
            digit = int(''.join(re.findall(r"\d+", text)))
            currency = re.sub(r"\d+", "", text)
            if "rub" in currency:
                currency = "RUR"
            salary = Salary(digit, currency)
        except BaseException:
            salary = Salary(Digit=0, Currency="")
        return salary

    def __get_specializations(self) -> list[str]:
        block = self.soup.find_all('li', class_='resume-block__specialization')
        if block:
            return [i.text for i in block]

    def __get_skills(self) -> list[str]:
        skills = []
        block_skills = self.soup.find('div', class_='bloko-tag-list')
        if block_skills:
            for skill in block_skills.find_all("span"):
                skills.append(skill.text)
        return skills

    def __get_languages(self) -> list[str]:
        languages = []
        languages_with_levels = [item.text for item in self.soup.find(attrs={'data-qa': 'resume-block-languages'}).find_all('p')]
        for language in languages_with_levels:
            new_lang = language.split('—')[0].strip() + f" ({language.split(' — ')[1].strip()})"
            languages.append(new_lang)
        return languages

    def __get_city(self) -> str:
        city = self.soup.find('span', attrs={"data-qa": 'resume-personal-address'})
        return city.text if city else ""

    def __get_experience_term_in_months(self) -> int:
        try:
            total_work_experience = self.soup.find('span', class_='resume-block__title-text resume-block__title-text_sub').text
        except:
            return 0

        if 'work experience' in total_work_experience.lower():
            total_work_experience = total_work_experience.replace('\xa0', ' ').replace('Work experience', '')
        else:
            total_work_experience = self.soup.find_all('span', class_='resume-block__title-text resume-block__title-text_sub')[1].text.replace('\xa0', ' ').replace('Work experience', '')
        return experience_to_months(total_work_experience)

    def __parse_vuz(self, block) -> list[Education]:
        universities = []
        for item in block:
            try:
                direction = item.find(attrs={'data-qa': 'resume-block-education-organization'}).text
            except:
                direction = ""
            universities.append(Education(
                ResumeId=self.Id,
                Title=item.find(attrs={self.TagsEducation["title"]["attr"]: self.TagsEducation["title"]["name"]}).text,
                Direction=direction,
                YearOfRelease=re.sub(" ", "", item.find('div', attrs={self.TagsEducation["year"]["attr"]: self.TagsEducation["year"]["name"]}).text)
            ))
        return universities

    def __parse_middle_education(self) -> Education | None:
        education_type = self.soup.find(attrs={'data-qa': 'resume-block-education'}).find(class_='bloko-header-2').text
        if education_type == 'Education':
            return Education(ResumeId=self.Id, Direction=None, YearOfRelease=None, Title=self.soup.find(attrs={'data-qa': 'resume-block-education'}).find_all('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-8 bloko-column_m-9 bloko-column_l-12')[-1].text)

    def __get_attestation(self) -> list[Education]:
        attestation = []
        block = self.soup.find("div", attrs={"data-qa": "resume-block-attestation-education", "class": "resume-block"})
        if not block:
            return []
        for item in block.find('div', class_='resume-block-item-gap').find_all('div', 'resume-block-item-gap'):
            attestation.append(Education(
                ResumeId=self.Id,
                Title=item.find(attrs={self.TagsEducation["title"]["attr"]: self.TagsEducation["title"]["name"]}).text,
                Direction=item.find(attrs={self.TagsEducation["organization"]["attr"]: self.TagsEducation["organization"]["name"]}).text,
                YearOfRelease=re.sub(" ", "", item.find('div', attrs={self.TagsEducation["year"]["attr"]: self.TagsEducation["year"]["name"]}).text)
            ))
        return attestation

    def __open_all_branches(self, url) -> BeautifulSoup:
        options = Options()
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        browser = webdriver(options=options, log_path="NUL")
        browser.get(url)
        browser.implicitly_wait(3)
        see_more_btns = browser.find_elements(By.XPATH, "//span[@class='bloko-text bloko-text_small bloko-text_secondary']")
        for btn in see_more_btns:
            print("clicked...")
            btn.click()

        soup = BeautifulSoup(browser.page_source, 'lxml')
        browser.quit()
        return soup

    def __get_step(self, block: BeautifulSoup) -> ExperienceStep:
        return ExperienceStep(
            ResumeId=self.Id,
            Post=block.find('div', {'data-qa': 'resume-block-experience-position', "class": 'bloko-text bloko-text_strong'}).text,
            Interval=self.__get_step_interval(block),
            Duration=experience_to_months(self.__get_step_duration(block)),
            Branch=self.__get_step_branches(block),
            Subbranch=self.__get_step_subbranches(block)
        )

    def __get_step_interval(self, block: BeautifulSoup) -> str:
        interval_block = block.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text.replace('\xa0', ' ')
        result = re.findall('\w+ \d{4} — \w+ \d{4}', interval_block)
        if result:
            return result[0]
        else:
            return re.findall('\w+ \d{4} — .*?\d', interval_block)[0][:-1]

    def __get_step_duration(self, block: BeautifulSoup) -> str:
        interval_block = block.find('div', class_='bloko-column bloko-column_xs-4 bloko-column_s-2 bloko-column_m-2 bloko-column_l-2').text.replace('\xa0', ' ')
        result = re.split('\w+ \d{4} — \w+ \d{4}', interval_block)
        if len(result) > 1:
            duration = result[-1]
        else:
            duration = re.findall('\d+', re.findall('\w+ \d{4} — .*?\d+', interval_block)[0].split()[-1])[-1] + ' '.join(re.split('\w+ \d{4} — .*?\d+', interval_block))
        return duration

    def __get_step_branches(self, block: BeautifulSoup) -> list[str]:
        branches = []
        try:
            branches = [item.text for item in block.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('p')]
        except:
            branches = [block.find('div', class_='resume-block__experience-industries resume-block_no-print').text.split('...')[0]]
        finally:
            return branches

    def __get_step_subbranches(self, block: BeautifulSoup) -> list[str]:
        subbranches = []
        try:
            for item in block.find('div', class_='resume-block__experience-industries resume-block_no-print').find_all('ul'):
                subbranch = ' ; '.join([li.text for li in item.find_all('li')])
                subbranches.append(subbranch)
        finally:
            return subbranches

def experience_to_months(experience: str) -> int:
    experience = re.sub(' +', ' ', experience)
    month_pattern = '\d{2} m|\d m'
    year_pattern = '\d{2} y|\d y'

    try:
        months = int(re.findall(month_pattern, experience)[0].split(' ')[0])
    except IndexError:
        months = 0
    try:
        years = int(re.findall(year_pattern, experience)[0].split(' ')[0])
    except IndexError:
        years = 0

    if years:
        return years * 12 + months
    else:
        return months
