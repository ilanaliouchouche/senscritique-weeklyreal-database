import psycopg2
import os

class SetupPGVector:
    ''' Setup database with vector extension '''

    def __init__(self, dbname, user, password, host, port):
        ''' Constructor for SetupPGVector:
            - dbname : database name
            - user : user name
            - password : password
            - host : host name
            - port : port number '''
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
    
    def setup_vdb(self, vector_size = 1024):
        ''' Setup database with vector extension '''
        with self.conx.cursor() as cursor:
            cursor.execute(f"CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(f"DROP TABLE IF EXISTS films")
            cursor.execute(f"DROP TABLE IF EXISTS genres")
            cursor.execute(f"DROP TABLE IF EXISTS producteurs")
            cursor.execute(f"DROP TABLE IF EXISTS realisateurs")
            cursor.execute(f"DROP TABLE IF EXISTS scenaristes")
            cursor.execute(f"DROP TABLE IF EXISTS pays")
            cursor.execute(f"DROP TABLE IF EXISTS reviews")
            cursor.execute(f"CREATE TABLE films (id SERIAL PRIMARY KEY, film VARCHAR(255), url VARCHAR(255), rate FLOAT, date_sortie DATE, image VARCHAR(255), bande_originale VARCHAR(255), groupe VARCHAR(255), annee FLOAT, duree FLOAT)")
            cursor.execute(f"CREATE TABLE genres (id SERIAL PRIMARY KEY, film VARCHAR(255), genre VARCHAR(255))")
            cursor.execute(f"CREATE TABLE producteurs (id SERIAL PRIMARY KEY, film VARCHAR(255), producteur VARCHAR(255))")
            cursor.execute(f"CREATE TABLE realisateurs (id SERIAL PRIMARY KEY, film VARCHAR(255), realisateur VARCHAR(255))")
            cursor.execute(f"CREATE TABLE scenaristes (id SERIAL PRIMARY KEY, film VARCHAR(255), scenariste VARCHAR(255))")
            cursor.execute(f"CREATE TABLE pays (id SERIAL PRIMARY KEY, film VARCHAR(255), pays VARCHAR(255))")
            cursor.execute(f"CREATE TABLE reviews (id SERIAL PRIMARY KEY, film VARCHAR(255), is_negative BOOLEAN, title VARCHAR(255), likes FLOAT, comments FLOAT, content TEXT, url VARCHAR(255), embedding vector({vector_size}))")
        
    
    def __str__(self):
        ''' String representation of SetupPGVector '''
        return f"dbname={self.dbname} user={self.user} password={self.password} host={self.host} port={self.port}"
    
    def __repr__(self):
        ''' Representation of SetupPGVector '''
        return self.__str__()
    
    def __call__(self):
        ''' Call SetupPGVector '''
        return self.__str__()  


if __name__ == "__main__":
    setup = SetupPGVector(dbname=os.getenv("PG_DBNAME"), user=os.getenv("PG_USER"), password=os.getenv("PG_DBPASSWORD"), host=os.getenv("PG_HOSTNAME"), port=os.getenv("PG_HPORT"))
    setup.setup_vdb()

        