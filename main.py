from etl.extract import CurrentMovieExtractor
from etl.transform import FilmTransformer
from etl.load import FilmLoader
import os
from dotenv import load_dotenv
import datetime
load_dotenv()

def get_current_week():
    current_date = datetime.datetime.now()
    current_week = current_date.isocalendar()[1]
    current_day = current_date.weekday() 

    if current_day <= 2: 
        current_week -= 1

    return current_week

import os

def update_env_file(key, value):
    env_file = '.env'

    with open(env_file, 'r') as file:
        lines = file.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = f"{key}={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{key}={value}\n")

    with open(env_file, 'w') as file:
        file.writelines(lines)

current_week = get_current_week()
if current_week == int(os.getenv("CURRENT_WEEK")):
    print("Current week is already loaded")
else:
    os.environ["CURRENT_WEEK"] = str(current_week)
    update_env_file("CURRENT_WEEK", str(current_week))


def main():
    current_week = get_current_week()
    if current_week == int(os.getenv("CURRENT_WEEK")):
        print("Current week is already loaded")
        return
    os.environ["CURRENT_WEEK"] = str(current_week)
    update_env_file("CURRENT_WEEK", str(current_week))
    
    try:
        extractor = CurrentMovieExtractor()
        extractor.extract_all_film_links()
        extractor.extract_all_film_data()
    except Exception as e:
        print("Error during extraction : ", e)
    
    try:
        transformer = FilmTransformer(extractor)
    except Exception as e:
        print("Error during transformation : ", e)
    
    try:
        loader = FilmLoader(transformer, dbname=os.getenv("PG_DBNAME"), user=os.getenv("PG_USER"), password=os.getenv("PG_PASSWORD"), host=os.getenv("PG_HOSTNAME"), port=os.getenv("PG_HPORT"))
        loader.loading()
    except Exception as e:
        print("Error during loading : ", e)
    




