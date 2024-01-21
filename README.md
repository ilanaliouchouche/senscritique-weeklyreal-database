# SensCritique WeekReal Database 🎬
<p align="center">
  <img src="res/sc.jpg" width="200">
</p>

## Table of Contents  
- [Overview](#overview)
- [Key Features](#key-features)
- [Important Note](#important-note)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
- [Reporting and visualization](#reporting-and-visualization)

## Overview
The SensCritique WeeklyReal Database project is an advanced ETL (Extract, Transform, Load) application developed in Python. It focuses on gathering weekly cinema release data from [sens-critique](https://www.senscritique.com/). For the transformation phase, we will leverage a Large Language Model (LLM) and the [TEI](https://github.com/huggingface/text-embeddings-inference) project to vectorize the reviews. The project's primary aim is to extract movie data, transform it using these advanced tools, and then store it in a [PGVector](https://github.com/pgvector/pgvector) database, a specialized vector data structure. This choice is motivated by the need to process and embed movie reviews, categorizing them into positive or negative sentiments, which is pivotal for subsequent data analysis and visualization.

## Key Features
- **Automated ETL Pipeline**: Extracts data from [sens-critique](https://www.senscritique.com/), transforms it, and loads it into a PGVector database.
- **Review Analysis**: Captures and categorizes movie reviews, enabling detailed sentiment analysis.
- **Vector Database Utilization**: Leverages [PGVector]((https://github.com/pgvector/pgvector)) for efficient handling and querying of vector data.
- **Dashboard Compatibility**: Designed to support data visualization and dashboard creation in PowerBI.
- **Scheduled and On-Demand Execution**: The process can be executed at any time, with checks to prevent reprocessing of current week's data.

## Important Note
:rotating_light::rotating_light::rotating_light:
- **Code Maintenance**: The code might not always be up-to-date due to possible changes in [sens-critique](https://www.senscritique.com/)'s website structure. While re-adaptation of the code is straightforward, regular updates may not be feasible.

## Technology Stack
<img src="res/hf.png" width="50"> <img src="res/pg.png" width="50"><img src="res/dock.jpg" width="50"><img src="res/sel.png" width="50"><img src="res/pbi.png" height="50">


- **Text Embedding Inference (TEI)**: For processing and embedding review texts.
- **PGVector**: A vector database for efficient data storage and retrieval.
- **Docker**: For containerizing the ETL process.
- **Selenium**: For web scraping and data extraction.
- **PwerBI**: For reporting.

## Repository Structure
| Directory/File        | Description                                  |
|-----------------------|----------------------------------------------|
| `etl/`                | Package containing Extract, Transform, Load modules. |
| `docker-compose.yml`  | Docker Compose file to link VDB, the app, and TEI.   |
| `Dockerfile`          | Dockerfile for creating the application's image.     |
| `main.py`             | Script to execute the ETL process.                   |
| `setup_vcb.py`        | Script for initial database setup (if running without volumes). |
| `bddr-sc-env.yml`        | Script for setup the conda env. |
| `requirements.txt`        | To install the dependencies with pip. |
|`reporting/`| Folder containing all the reporting section. |

## Usage
- **Docker Setup**: Fetch the `docker-compose.yml`, required volumes, and project image. Run `main.py` within the container. If running 
without volumes, execute `setup_vcb.py` first.
- **Conda Environment**: Setup a Conda environment and execute `main.py`, or use the classes within a Notebook. **In this case, setup the rights ENV VAR**  
**Note**: Don't forget to launch pgvector and TEI images.  

**HANDBOOK available [here](https://github.com/ilanaliouchouche/senscritique-weeklyreal-database/tree/main/handbook/README.md)**

- **Reporting**: For reporting purposes, retrieve only the volume, launch a PGVector instance, and connect to the database from PowerBI. See [`reporting/`](/reporting/).

# 🎬
