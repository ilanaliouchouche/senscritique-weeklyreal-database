import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import json
from datetime import datetime
from copy import deepcopy
import psycopg2

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

        pagination = soup.find("nav")
        
        if pagination:
            last = pagination.find_all("span")[-1].text
            return int(last)
        else:
            return 1 

    def extract_all_film_links(self, cpt = 4):
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
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        h1_titre = soup.find("h1", class_="sc-e6f263fc-1 bwGoop")
        if h1_titre:
            return h1_titre.text.strip()

        raise Exception("Title not found")
    
    @staticmethod
    def extract_film_rating(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_note = soup.find("div", class_="sc-8251ce8c-5 fdoSxm")
        if div_note:
            return float(div_note.text.strip())  
        return None
    
    @staticmethod
    def extract_image(url):
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
        if cpt == 0:
            raise Exception("Too many attempts")
        
        driver = webdriver.Chrome()

        review_url = f"{url}/critiques"

        driver.get(review_url)

        time.sleep(7)
        try:
            cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
            cookie_button.click()
            time.sleep(5)
        except Exception as e:
            raise Exception("Cookie button not found or already clicked")

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
        print("Done with all films, extracting reviews...")
        for title, details in tqdm(all_details.items()):
            for review_type, review_links in details['reviews'].items():
                reviews = []
                for link in review_links:
                    reviews.append(self.extract_review_details(link))
                details['reviews'][review_type] = reviews
        self.informations = all_details


class CurrentMovieExtractor(BaseFilmExtractor):

    URL  = "https://www.senscritique.com/films/cette-semaine"

    def __init__(self, url=URL):
        super().__init__(url)
        self.url = url
    
    def extract_all_film_links(self):
        print("Extracting all films links...")
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        links = soup.find_all('a', class_='sc-e976169f-2 juEctl')

        base_url = "https://www.senscritique.com/"
        self.urls_films = [base_url + link.get('href') for link in links if link.get('href')]
        print("Done with all films links")
    
    @classmethod
    def extract_reviews(cls, url, is_negative=True):
        driver = webdriver.Chrome()

        review_url = f"{url}/critiques"

        driver.get(review_url)

        time.sleep(7)
        try:
            cookie_button = driver.find_element(By.ID, "didomi-notice-agree-button")
            cookie_button.click()
            time.sleep(5)
        except Exception as e:
            raise Exception("Cookie button not found or already clicked")

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



class FilmTransformer:

    def __init__(self, extractor : BaseFilmExtractor):
        self.extractor = extractor
        self.df_films, self.df_genres, self.df_producteurs, self.df_realisateurs, self.df_scenaristes, self.df_pays, self.df_reviews = self.__transform()
    
    @staticmethod
    def get_embeddings(reviews):
        embeddings = []
        print("Computing embeddings...")

        for r in tqdm(reviews):
            response = requests.post("http://0.0.0.0:8088/embed", json={
            "inputs": r,
            "normalize": True,
            "truncate": False
            })
            if response.status_code == 200:
                embeddings.extend(response.json())
            else:
                embeddings.append(None)
        print("Done with embeddings")

        return embeddings

    
    def __transform(self):
        informations = deepcopy(self.extractor.informations)
        films_cols  = ['url', 'rate', 'Date de sortie (France)', 'image', 'Bande originale', 'Groupe', 'Année', 'Durée']
        df_films = pd.DataFrame(columns=['film',*films_cols])
        df_genres = pd.DataFrame(columns=['film', 'genre'])
        df_producteurs = pd.DataFrame(columns=['film', 'producteur'])
        df_realisateurs = pd.DataFrame(columns=['film', 'realisateur'])
        df_scenaristes = pd.DataFrame(columns=['film', 'scenariste'])
        df_pays = pd.DataFrame(columns=['film', 'pays'])
        df_reviews = pd.DataFrame(columns=['film', 'is_negative', 'title', 'likes', 'comments', 'content', 'url'])

        for title, info in informations.items():
            for key in list(info.keys()):
                if re.match(r"^Prod.*", key):
                    info['Producteurs'] = info.pop(key)
                elif re.match(r"^Scénar.*", key):
                    info['Scénaristes'] = info.pop(key)
                elif re.match(r"^Genr.*", key):
                    info['Genre'] = info.pop(key)
                elif re.match(r"^Réal.*", key):
                    info['Réalisateurs'] = info.pop(key)
                elif re.match(r"^Pays d.*", key):
                    info['Pays d\'origine'] = info.pop(key)

            groups = re.match(r'(\d+)\s*h(\s*(\d+)\s*min)?', info.get('Durée', ''))

            if groups:
                heures = groups.group(1)
                minutes = groups.group(3) if groups.group(3) else 0
                info['Durée'] = int(heures) * 60 + int(minutes) 
            else:
                info['Durée'] = None

            mois_fr_to_num = {
                "janvier": "01", "février": "02", "mars": "03",
                "avril": "04", "mai": "05", "juin": "06",
                "juillet": "07", "août": "08", "septembre": "09",
                "octobre": "10", "novembre": "11", "décembre": "12"
            }
            for mois_fr, mois_num in mois_fr_to_num.items():
                info['Date de sortie (France)'] = re.sub(mois_fr, mois_num, info.get('Date de sortie (France)', ''))
            info['Date de sortie (France)'] = datetime.strptime(info['Date de sortie (France)'], '%d %m %Y').strftime('%Y-%m-%d')
            film_dict = dict(**{'film' : title}, **{key: info.get(key, None) for key in films_cols})
        

            df_films = df_films._append(film_dict, ignore_index=True)


            for review in info.get('reviews', {}).get('Positives', []):
                df_reviews = df_reviews._append({'film': title, 'is_negative': False, **review}, ignore_index=True)

            for review in info.get('reviews', {}).get('Negatives', []):
                df_reviews = df_reviews._append({'film': title, 'is_negative': True, **review}, ignore_index=True)

            
            for producteur in info.get('Producteurs', '').split(', '):
                df_producteurs = df_producteurs._append({'film': title, 'producteur': producteur}, ignore_index=True)
            for realisateur in info.get('Réalisateurs', '').split(', '):
                df_realisateurs = df_realisateurs._append({'film': title, 'realisateur': realisateur}, ignore_index=True)
            for scenariste in info.get('Scénaristes', '').split(', '):
                df_scenaristes = df_scenaristes._append({'film': title, 'scenariste': scenariste}, ignore_index=True)
            for pays in info.get('Pays d\'origine', '').split(', '):
                df_pays = df_pays._append({'film': title, 'pays': pays}, ignore_index=True)
            for genre in info.get('Genre', '').split(', '):
                df_genres = df_genres._append({'film': title, 'genre': genre}, ignore_index=True)


        df_reviews['embedding'] = self.get_embeddings(df_reviews['content'].tolist())
        df_films['Durée'] = pd.to_numeric(df_films['Durée'], errors='coerce', downcast='integer')
        df_films['Année'] = pd.to_numeric(df_films['Année'], errors='coerce', downcast='integer')
        df_reviews['likes'] = pd.to_numeric(df_reviews['likes'], errors='coerce', downcast='integer')
        df_reviews['comments'] = pd.to_numeric(df_reviews['comments'], errors='coerce', downcast='integer')
        return df_films, df_genres, df_producteurs, df_realisateurs, df_scenaristes, df_pays, df_reviews

class FilmLoader:

    def __init__(self, data : FilmTransformer, dbname : str, user : str, password : str, host : str, port : int):
        self.data = data
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        try:
            self.conx = psycopg2.connect(self())
            self.conx.autocommit = True
        except:
            raise Exception("Connection failed")
    
    def __load(self, df, table_name):
        with self.conx.cursor() as cursor:
            for _, row in df.iterrows():
                columns = []
                placeholders = []
                values = []
                for col, val in zip(df.columns, row.values):
                    if col == 'Date de sortie (France)':
                        col = 'date_sortie'
                    elif col == 'Durée':
                        col = 'duree'
                    elif col == 'Année':
                        col = 'annee'
                    elif col == 'Bande originale':
                        col = 'bande_originale'
                    elif col == 'Groupe':
                        col = 'groupe'
                    
                    columns.append(col)
                    placeholders.append("%s")
                    values.append(val)

                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, values)
    
    def loading(self):
        print("Loading data...")
        self.__load(self.data.df_films, 'films')
        self.__load(self.data.df_genres, 'genres')
        self.__load(self.data.df_producteurs, 'producteurs')
        self.__load(self.data.df_realisateurs, 'realisateurs')
        self.__load(self.data.df_scenaristes, 'scenaristes')
        self.__load(self.data.df_pays, 'pays')
        self.__load(self.data.df_reviews, 'reviews')
        print("Done with loading")
    
    def __str__(self):
        return f"dbname={self.dbname} user={self.user} password={self.password} host={self.host} port={self.port}"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self):
        return self.__str__()
        
        

        
