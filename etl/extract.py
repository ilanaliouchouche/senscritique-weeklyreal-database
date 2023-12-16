import requests
import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

class BaseExtract:
    
    URL = "https://www.senscritique.com/liste/films_2023/3376363"

    def __init__(self, url=URL):
        self.url = url
        self.urls_films = None
        self.informations = None

    @staticmethod
    def get_number_of_pages(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        pagination = soup.find("nav", class_="Pagination__WrapperPagination-sc-1h0mvsr-0 dFTVxz")
        
        if pagination:
            last = pagination.find_all("span")[-1].text
            return int(last)
        else:
            return 1 

    def get_urls_films(self):
        urls_films = []

        pages = self.get_number_of_pages(self.url)
              
        for page in tqdm(range(1, pages + 1)):
            url_page = f"{self.url}?page={page}"
            response = requests.get(url_page)
            soup = BeautifulSoup(response.content, 'html.parser')

            script = soup.find('script', {'type': 'application/ld+json'})
            if script:
                data = json.loads(script.string)

                for element in data.get('itemListElement', []):
                    film_url = element.get('url')
                    if film_url:
                        urls_films.append(film_url)

        self.urls_films = urls_films
    
    @staticmethod
    def get_film_details(detail_url):
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        info_div = soup.find("div", class_="Text__SCText-sc-1aoldkr-0 Movie__Text-sc-1tik1a1-1 gATBvI kkLsHK")
        infos = []
        if info_div:
            for span in info_div.find_all("span"):
                text = span.text.strip()
                if not text.endswith(':') and len(text) > 0:
                    infos.append(text)
        infos_dict = {info.split(' : ', 1)[0].strip(): info.split(' : ', 1)[1].strip() for info in infos}
        return infos_dict

    @staticmethod
    def get_title(detail_url):
        response = requests.get(detail_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_titre = soup.find("div", class_="ProductDetails__WrapperTitle-sc-5nxbfw-5 hKtmtY")
        if div_titre:
            h1_titre = div_titre.find("h1", class_="Text__SCTitle-sc-1aoldkr-1 iTBZrv")
        if h1_titre:
            return h1_titre.text.strip()

        raise Exception("Title not found")
    
    @staticmethod
    def get_rate(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        div_note = soup.find("div", class_="Rating__GlobalRating-sc-1b09g9c-5 itJntU")
        if div_note:
            return float(div_note.text.strip())  
        return None
    
    def extract_all_film_details(self):
        all_details = {}
        for url in tqdm(self.urls_films):
            detail_url = url + "/details"
            details = self.get_film_details(detail_url)
            title = self.get_title(detail_url)
            all_details[title] = details
            all_details[title]['url'] = url
            all_details[title]['rate'] = self.get_rate(url)
        self.informations = all_details
        
    
    

    


class Extract(BaseExtract):

    def __init__(self, url):
        super().__init__(url)
    



