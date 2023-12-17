import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class BaseFilmExtractor:
    
    URL = "https://www.senscritique.com/films/sorties-cinema/"

    def __init__(self, year, url=URL):
        self.url = f"{url}/{year}"
        self.urls_films = None
        self.informations = None
    
    @staticmethod
    def extract_film_links_from_page(driver):
        elements = driver.find_elements(By.CLASS_NAME, "Poster__SubLink-sc-yale2-2.jhmgpI")
        return [element.get_attribute('href') for element in elements]

    @staticmethod
    def calculate_total_pages(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pagination = soup.find("nav", class_="Pagination__WrapperPagination-sc-1h0mvsr-0 dFTVxz")
        
        if pagination:
            last = pagination.find_all("span")[-1].text
            return int(last)
        else:
            return 1 

    def extract_all_film_links(self, cpt = 4):
        if cpt == 0:
            raise Exception("Too many attempts")
        n = self.calculate_total_pages(self.url)
        driver = webdriver.Chrome()
        driver.get(self.url)

        time.sleep(5)
        cookie_button = self.driver.find_element(By.ID, "didomi-notice-agree-button")
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
                if page_number != n:
                    c = cpt - 1
                    driver.quit()
                    self.extract_all_film_links(cpt=c)
                else:
                    self.urls_films = all_film_links
                    print(f"Done with page {page_number - 1}")
                    driver.quit()
                    break
    
    @staticmethod
    def extract_film_details(detail_url):
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        info_div = soup.find("div", class_="Text__SCText-sc-1aoldkr-0 Movie__Text-sc-1tik1a1-1 gATBvI kkLsHK")
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
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_titre = soup.find("div", class_="ProductDetails__WrapperTitle-sc-5nxbfw-5 hKtmtY")
        if div_titre:
            h1_titre = div_titre.find("h1", class_="Text__SCTitle-sc-1aoldkr-1 iTBZrv")
        if h1_titre:
            return h1_titre.text.strip()

        raise Exception("Title not found")
    
    @staticmethod
    def extract_film_rating(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_note = soup.find("div", class_="Rating__GlobalRating-sc-1b09g9c-5 itJntU")
        if div_note:
            return float(div_note.text.strip())  
        return None
    
    @staticmethod
    def extract_image(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        span_image = soup.find("span", class_="Poster__WrapperImage-sc-yale2-10 jPPcbD")

        data_srcname = None
        if span_image and 'data-srcname' in span_image.attrs:
            data_srcname = span_image.attrs['data-srcname']
        return data_srcname

    @staticmethod
    def extract_reviews(url, is_negative=True, cpt = 4):
        if cpt == 0:
            raise Exception("Too many attempts")
        
        driver = webdriver.Chrome()

        n = BaseFilmExtractor.calculate_total_pages(url)

        review_url = f"{url}/critiques"
        driver.get(review_url)

        time.sleep(5)
        try:
            cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
            cookie_button.click()
            time.sleep(5)
        except Exception as e:
            raise Exception("Cookie button not found or already clicked")

        review_type = 'Négatives' if is_negative else 'Positives'
        link_reviews = driver.find_element(By.XPATH, f"//a[contains(text(), '{review_type}')]")
        link_reviews.click()

        all_links = []
        page_number = 1

        while True:
            time.sleep(5)

            elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'Text__SCText-sc-1aoldkr-0') and contains(@class, 'Link__PrimaryLink-sc-1v081j9-0') and contains(@class, 'gATBvI') and contains(@class, 'hJEAZk') and contains(@class, 'link')]")
            links = [element.get_attribute('href') for element in elements]
            all_links.extend(links)

            try:
                page_number += 1
                next_page_button = driver.find_element(By.XPATH, f"//nav[contains(@class, 'Pagination__WrapperPagination-sc-1h0mvsr-0') and contains(@class, 'dFTVxz')]//span[normalize-space()='{page_number}']")
                next_page_button.click()
            except Exception as e:
                if page_number != n:
                    c = cpt - 1
                    driver.quit()
                    BaseFilmExtractor.extract_reviews(url, is_negative, cpt=c)
                else:
                    print(f"Done with page {page_number - 1} for {url}")
                    break

        driver.quit()

        return all_links
    
    def extract_all_film_data(self):
        all_details = {}
        for url in tqdm(self.urls_films):
            detail_url = url + "/details"
            details = self.extract_film_details(detail_url)
            title = self.extract_film_title(detail_url)
            all_details[title] = details
            all_details[title]['url'] = url
            all_details[title]['rate'] = self.extract_film_rating(url)
            all_details[title]['image'] = self.extract_image(url)
            all_details[title]['reviews'] = {'Positives' : self.extract_reviews(url, is_negative=False), 'Negatives' : self.extract_reviews(url, is_negative=True)}
        self.informations = all_details


class Extract(BaseFilmExtractor):

    def __init__(self, url):
        super().__init__(url)
