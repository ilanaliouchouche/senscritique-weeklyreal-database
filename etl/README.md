
# ETL Package

## Overview

The `etl` package is a comprehensive solution for handling data related to films. It comprises three primary modules: `extract`, `transform`, and `load`, each responsible for different stages of the ETL (Extract, Transform, Load) process. This package is designed to streamline the workflow from data extraction to database integration.

## Modules

### Extract
The `extract` module is focused on data extraction. It contains two classes:

| Class                 | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `BaseFilmExtractor`   | Extracts film data by year.                                  |
| `CurrentFilmExtractor`| Extracts data for films released in the current week.        |

### Transform
The `transform` module is responsible for data transformation, including the embedding of reviews with TEI (Text Embedding Inference).

| Class           | Description                                     |
| --------------- | ----------------------------------------------- |
| `FilmTransformer` | Transforms the extracted data and performs embedding with TEI. |

### Load
The `load` module handles connecting and loading data into a PGVector database.

| Class        | Description                                      |
| ------------ | ------------------------------------------------ |
| `FilmLoader` | Connects to and loads data into a PGVector database. |

## Prerequisites
- Python 3.11.5
- Dependencies: available in `/requirements.txt`

## Usage

Here is a basic example of how to use the `etl` package:

```python
from etl.extract import CurrentFilmExtractor
from etl.transform import FilmTransformer
from etl.load import FilmLoader

# Extract data
extractor = CurrentFilmExtractor()
extractor.extract_all_film_links()
extractor.extract_all_film_data()

# Transform data
transformer = FilmTransformer(extractor)

# Load data
loader = FilmLoader(transformer, dbname=os.getenv("PG_DBNAME"), user=os.getenv("PG_USER"), password=os.getenv("PG_DBPASSWORD"), host=os.getenv("PG_HOSTNAME"), port=os.getenv("PG_HPORT"))
loader.load()
```
See this [notebook](https://github.com/ilanaliouchouche/senscritique-weeklyreal-database/blob/main/example.ipynb) for a real example.
