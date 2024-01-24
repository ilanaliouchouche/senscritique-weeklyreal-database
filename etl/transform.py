from typing import List
from etl.extract import BaseFilmExtractor
import pandas as pd
import re
from datetime import datetime
from tqdm.auto import tqdm
import requests
from copy import deepcopy
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

class FilmTransformer:
    ''' Transform data from extractor to multiple dataframes '''

    def __init__(self, extractor : BaseFilmExtractor) -> None:
        ''' FilmTransformer constructor:
            - extractor : BaseFilmExtractor object '''
        self.extractor = extractor
        self.df_films, self.df_genres, self.df_producteurs, self.df_realisateurs, self.df_scenaristes, self.df_pays, self.df_reviews = self.__transform()
    
    @staticmethod
    def get_embeddings(reviews : list[str]) -> List[List[float]]:
        ''' Get embeddings from TEI API:
            - reviews : list of reviews '''
        embeddings = []
        print("Computing embeddings...")

        for r in tqdm(reviews):
            response = requests.post(f"http://{os.getenv('TEI_HOSTNAME')}:{os.getenv('TEI_HPORT')}/embed", json={
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

    
    def __transform(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        ''' Transform data from extractor to multiple dataframes '''
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