from etl.transform import FilmTransformer
import psycopg2

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