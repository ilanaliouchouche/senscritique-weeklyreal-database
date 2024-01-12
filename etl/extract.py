import requests
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options 
import time
import json
from dotenv import load_dotenv
import os
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class BaseFilmExtractor:
    ''' Base class for film extractor, it contains all the methods to extract films informations from senscritique.com in a given year. '''
    
    URL = "https://www.senscritique.com/films/sorties-cinema/"

    def __init__(self, year, url=URL):
        ''' Constructor for BaseFilmExtractor :
            - year : year of the films
            - url : url of the page to extract films from (default : https://www.senscritique.com/films/sorties-cinema/)) '''
        self.url = f"{url}/{year}"
        self.urls_films = None
        self.informations = None
    
    @staticmethod
    def extract_film_links_from_page(driver):
        ''' Extract all film links from a given page '''
        elements = driver.find_elements(By.CLASS_NAME, "Poster__SubLink-sc-yale2-2.jhmgpI")
        return [element.get_attribute('href') for element in elements]

    @staticmethod
    def calculate_total_pages(url):
        ''' Calculate the total number of pages for a given url '''
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pagination = soup.find("nav")
        
        if pagination:
            last = pagination.find_all("span")[-1].text
            return int(last)
        else:
            return 1 

    def extract_all_film_links(self, cpt = 4):
        ''' Extract all film links from a given url '''
        print("Extracting all films links...")
        if cpt == 0:
            raise Exception("Too many attempts")
        n = self.calculate_total_pages(self.url)
        driver = webdriver.Chrome()
        driver.get(self.url)

        time.sleep(5)
        cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
        cookie_button.click()
        time.sleep(5)

        all_film_links = []

        page_number = 1
        while True:
            film_links = self.extract_film_links_from_page(driver)
            all_film_links.extend(film_links)

            try:
                page_number += 1
                next_page_button = self.driver.find_element(By.XPATH, f"//nav[contains(@class, 'Pagination__WrapperPagination-sc-1h0mvsr-0')]//span[normalize-space()='{page_number}']")
                next_page_button.click()
                time.sleep(5)
            except Exception as e:
                if page_number - 1 != n:
                    c = cpt - 1
                    driver.quit()
                    self.extract_all_film_links(cpt=c)
                else:
                    self.urls_films = all_film_links
                    print(f"Done with page {page_number - 1}")
                    driver.quit()
                    break
        print("Done with all films links")
    
    @staticmethod
    def extract_film_details(detail_url):
        ''' Extract all film details from a given url '''
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        info_div = soup.find("div", class_="sc-e6f263fc-0 sc-fa5905bc-1 iZcnfH egYIEb")
        infos = []
        if info_div:
            for span in info_div.find_all("span"):
                text = span.text.strip()
                if not text.endswith(':') and len(text) > 0 and " : " in text:
                    infos.append(text)
        infos_dict = {info.split(' : ', 1)[0].strip(): info.split(' : ', 1)[1].strip() for info in infos}
        return infos_dict

    @staticmethod
    def extract_film_title(detail_url):
        ''' Extract film title from a given url '''
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        h1_titre = soup.find("h1", class_="sc-e6f263fc-1 bwGoop")
        if h1_titre:
            return h1_titre.text.strip()

        raise Exception("Title not found")
    
    @staticmethod
    def extract_film_rating(url):
        ''' Extract film rating from a given url '''
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_note = soup.find("div", class_="sc-8251ce8c-5 fdoSxm")
        if div_note:
            return float(div_note.text.strip())  
        return None
    
    @staticmethod
    def extract_image(url):
        ''' Extract film image from a given url '''
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        png_link = soup.find_all('script', attrs={'type': 'application/ld+json'})
        if png_link:
            json_data = json.loads(png_link[0].string)
            image_url = json_data['image']
            return image_url
        return None

    @classmethod
    def extract_reviews(cls, url, is_negative=True, cpt = 100):
        ''' Extract all film reviews from a given url '''
        if cpt == 0:
            raise Exception("Too many attempts")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Remote(f"http://{os.getenv('SEL_HOSTNAME')}:{os.getenv('SEL_HPORT')}/wd/hub", options=chrome_options)

        review_url = f"{url}/critiques"

        driver.get(review_url)

        review_type = 'Négatives' if is_negative else 'Positives'
        link_reviews = driver.find_element(By.XPATH, f"//a[contains(text(), '{review_type}')]")
        link_reviews.click()
        time.sleep(2)
        try :
            first_nav = driver.find_element(By.TAG_NAME, "nav")
            last_span = first_nav.find_elements(By.TAG_NAME, "span")[-1]
            n = int(last_span.text)
        except:
            n = 1

        all_links = []
        page_number = 1

        while True:
            time.sleep(5)

            elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'sc-e6f263fc-0') and contains(@class, 'sc-a0949da7-0') and contains(@class, 'iZcnfH') and contains(@class, 'cYbaKn') and contains(@class, 'link')]")
            links = [element.get_attribute('href') for element in elements]
            all_links.extend(links)

            try:
                page_number += 1
                page_span = first_nav.find_element(By.XPATH, f".//span[normalize-space(text())='{page_number}']")
                page_span.click()
            except Exception as e:
                if (page_number - 1) == n:
                    driver.quit()
                    break
                else:
                    c = cpt - 1
                    driver.quit()
                    BaseFilmExtractor.extract_reviews(url, is_negative, cpt=c)


        return all_links
    
    @staticmethod
    def extract_review_details(url):
        ''' Extract review details from a given url '''
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        review_content = soup.find("div", class_="sc-cfcc05b8-0 fywlHd")
        content = review_content.find("p").text if review_content else "Content not found"

        review_title = soup.find("h1", class_="sc-e6f263fc-2 sc-b23687b5-0 ewlOkU gmTbwg sc-6b0a5f14-7 jPNYGd")
        title = review_title.text if review_title else "Title not found"

        ctas = soup.find_all("div", class_="sc-ede15b33-0 bBMXjh")
        likes, comments = None, None
        if ctas:
            spans = [cta.find("span", class_="sc-e6f263fc-1 sc-ede15b33-1 erFyGe iblteA") for cta in ctas]
            if len(spans) >= 2:
                likes = spans[0].text if spans[0] else 0
                comments = spans[1].text if spans[1] else 0

        return {
            "title": title,
            "likes": likes,
            "comments": comments,
            "content": content,
            "url": url
        }
        
    
    def extract_all_film_data(self):
        ''' Extract all film data from a given url using all the methods above'''
        all_details = {}
        print("Extracting all films informations...")
        for url in tqdm(self.urls_films):
            detail_url = url + "/details"
            details = self.extract_film_details(detail_url)
            title = self.extract_film_title(detail_url)
            all_details[title] = details
            all_details[title]['url'] = url
            all_details[title]['rate'] = self.extract_film_rating(url)
            all_details[title]['image'] = self.extract_image(url)
            all_details[title]['reviews'] = {'Positives' : self.extract_reviews(url, is_negative=False), 'Negatives' : self.extract_reviews(url, is_negative=True)}
        print(all_details)
        print("Done with all films, extracting reviews...")
        for title, details in tqdm(all_details.items()):
            for review_type, review_links in details['reviews'].items():
                reviews = []
                for link in review_links:
                    reviews.append(self.extract_review_details(link))
                details['reviews'][review_type] = reviews
        print("Done with all reviews")
        self.informations = all_details

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class CurrentMovieExtractor(BaseFilmExtractor):

    ''' Class to extract films informations from senscritique.com in the current week. '''
    URL  = "https://www.senscritique.com/films/cette-semaine"

    def __init__(self, url=URL):
        ''' Constructor for CurrentMovieExtractor :
            - url : url of the page to extract films from (default : https://www.senscritique.com/films/cette-semaine)) '''
        super().__init__(url)
        self.url = url
    
    def extract_all_film_links(self):
        ''' Extract all film links from a given url '''
        print("Extracting all films links...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', class_='sc-e6f263fc-0 sc-a0949da7-1 cTitej eGjRhz sc-4495ecbb-3 hCRsTs')

        base_url = "https://www.senscritique.com/"
        self.urls_films = [base_url + link.get('href') for link in links if link.get('href')]
        print("Done with all films links")
    
    @classmethod
    def extract_reviews(cls, url, is_negative=True):
        ''' Extract all film reviews from a given url '''
        options = Options()
        options.headless = True
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options, service=Service(GeckoDriverManager().install()))
        review_url = f"{url}/critiques"

        driver.get(review_url)
        time.sleep(2)
        
        try:
            review_type = 'Négatives' if is_negative else 'Positives'
            link_reviews = driver.find_element(By.XPATH, f"//a[contains(text(), '{review_type}')]")
            link_reviews.click()
        except:
            time.sleep(2)
            cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
            cookie_button.click()
            time.sleep(3)
            review_type = 'Négatives' if is_negative else 'Positives'
            link_reviews = driver.find_element(By.XPATH, f"//a[contains(text(), '{review_type}')]")
            link_reviews.click()

                

        time.sleep(2)
        
        all_links = []

        time.sleep(5)

        elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'sc-e6f263fc-0') and contains(@class, 'sc-a0949da7-0') and contains(@class, 'iZcnfH') and contains(@class, 'cYbaKn') and contains(@class, 'link')]")
        links = [element.get_attribute('href') for element in elements]
        all_links.extend(links)
        
        return all_links


        
