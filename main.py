from etl.extract import CurrentMovieExtractor
from etl.transform import FilmTransformer
from etl.load import FilmLoader
import os
from dotenv import load_dotenv
import datetime
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

''' Main script to extract, transform and load data into database '''

def get_current_week():
    ''' Get current week number '''
    current_date = datetime.datetime.now()
    current_week = current_date.isocalendar()[1]
    current_day = current_date.weekday() 

    # If current day is monday or tuesday, we consider that we are still in the previous week.
    # Indeed, the new movies are released on wednesday.
    if current_day <= 2: 
        current_week -= 1

    return current_week

def remove_current_week():
    ''' Remove current week from .env file '''
    env_file = '.env'

    with open(env_file, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("CURRENT_WEEK"):
            del lines[i]
            break

    with open(env_file, 'w') as file:
        file.writelines(lines)

def update_env_file(key, value):
    ''' Update .env file '''
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
        lines.append(f"\n{key}={value}\n")

    with open(env_file, 'w') as file:
        file.writelines(lines)

def main():
    ''' Main function '''
    current_week = get_current_week()
    first_load = False
    try:
        if current_week == int(os.getenv("CURRENT_WEEK")):
            print("Current week is already loaded")
            return
    except:
        first_load = True
        pass
    if not first_load:
        last_week = int(os.getenv("CURRENT_WEEK")) 
    os.environ["CURRENT_WEEK"] = str(current_week)
    update_env_file("CURRENT_WEEK", str(current_week))
    
    try:
        extractor = CurrentMovieExtractor()
        extractor.extract_all_film_links()
        extractor.extract_all_film_data()
    except Exception as e:
        if not first_load:
            os.environ["CURRENT_WEEK"] = str(last_week)
            update_env_file("CURRENT_WEEK", str(last_week))
        else:
            remove_current_week()
        print("Error during extraction : ", e)
    
    try:
        transformer = FilmTransformer(extractor)
    except Exception as e:
        if not first_load:
            os.environ["CURRENT_WEEK"] = str(last_week)
            update_env_file("CURRENT_WEEK", str(last_week))
        else:
            remove_current_week()
        print("Error during transformation : ", e)
    
    try:
        loader = FilmLoader(transformer, dbname=os.getenv("PG_DBNAME"), user=os.getenv("PG_USER"), password=os.getenv("PG_DBPASSWORD"), host=os.getenv("PG_HOSTNAME"), port=os.getenv("PG_HPORT"))
        loader.loading()
    except Exception as e:
        if not first_load:
            os.environ["CURRENT_WEEK"] = str(last_week)
            update_env_file("CURRENT_WEEK", str(last_week))
        else:
            remove_current_week()
        print("Error during loading : ", e)
    print("--------------------[DONE]--------------------")
    
if __name__ == "__main__":
    main()



