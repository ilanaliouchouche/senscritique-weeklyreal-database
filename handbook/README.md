# Project Usage Guide 👨‍💻

This guide provides step-by-step instructions on how to set up and use the project using Conda and by cloning the repository.

- [Locally, with conda](#locally-with-conda)
- [Using containers with docker-compose](#using-containers-with-docker-compose)

## Locally, with conda

### Prerequisites
- Conda environment manager
- Git
- Docker

### 1. Clone the Repository
First, clone the repository to your local machine using Git:
```bash
git clone https://github.com/ilanaliouchouche/senscritique-weeklyreal-database
```
### 2. Create a Conda Environement 
After cloning the repository, create a new Conda environment using the provided YAML file:
```bash
conda env create -f bddr-sc-env.yml -n bddr-sc-env
```
### 3. Activate the Environment
Once the environment is successfully created, activate it:
```bash
conda activate bddr-sc-env
```
### 2 & 3 bis. Install requirements
Alternatively, you can use directly [/requirements.txt](/requirements.txt)
```bash
pip install -r requirements.txt
```
### 4. Launch Containers
Launch two containers:
 - One for the TEI (Text Encoding Inference)
 - Another for PGVector
**Note**: Specific commands for launching these containers will depend on your containerization tool and the configurations required for TEI and PGVector.
Example:
```bash
docker run --name db_sc -p 5432:5432 -e POSTGRES_PASSWORD=dw2 -v data:/var/lib/postgresql/data  -d ankane/pgvector 

docker run --name tei_sc -p 8088:80 -v llm_data:/data --pull always -d ghcr.io/huggingface/text-embeddings-inference:cpu-0.6 --model-id intfloat/multilingual-e5-large --revision refs/pr/5 
```
### 5. Run the script
```bash
python main.py
```

### 5bis. Alternative manual execution
Alternatively, you can manually execute the processes by following the instructions in the provided [notebook](https://github.com/ilanaliouchouche/senscritique-weeklyreal-database/blob/main/example.ipynb).


## Using containers with docker-compose

### 1. Build with docker-compose
```bash
sudo docker-compose build
```
**Note**: Superuser rights are required due to the volume of the PGVector container

### 2. Launch the docker-compose
```bash
docker-compose up -d
```

### 3. Retrieve the name of the app's container
```bash
docker ps | grep "app"
```

### 4. Go into the container via bash and execute the program
```bash
docker exec -it <RETRIEVED NAME> bash
# You are inside the container
# If volume is empty
python setup_vcb.py
python main.py
# Else
python main.py
```

