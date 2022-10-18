WQP maps processing
===================

The docker composition presented in this repository aims to support the continued production of the Water Quality Parameters (WQPs) maps for the SIMILE project. The build of the image base in the `mundialis/esa-snap:8.0-ubuntu` latest image, and set up multiple python libraries to enable the creation of an interactive environment for processing satellite images.

-------------------
## Requirements

The Virtual Machine is composed inside a Docker container. Then, to build the processing environment, install Docker in your system. Follow the instructions presented in https://docs.docker.com/get-docker/ for your working OS.

-------------------

## Setup Environment

1. Clone the project.

```
# Clone the repository
git clone https://github.com/JFToro192/jpbnWQPsimile.git

# Move to the location of the cloned project.
```

2. Setup Config Files

The notebooks inside the project work following a specific folder structure. In the cloned repository, you will find all the necessary folders and configuration files to correctly execute the notebooks. Before beginning the processing, extract the folders and files in the `./env.zip` and `./notebooks/folder-structure.zip` files.

* `./env.zip`: contains the environment file for the docker composition
* `./notebooks/folder-structure.zip`: has the folder structure and secrets for using the APIs calls for retrieving data from different sources (`./notebooks/.env`; i.e. WEkEO DIAS HDA API and Regione Lombardia Socrata API)

Once the compressed files are extracted, the file structure should be the following:

```
jpbnWQPsimile
└───notebooks
│   │   in
│   │   meteo
│   │   out
│   │   src
│   │   vector
│   │   .env
|   |   downloadMeteoARPA.ipynb
|   |   downloadWEkEO.ipynb
|   |   README.md
|   |   WQP_Coregistration.ipynb
|   |   WQP_istSOS.ipynb
|   |   WQP_Production.ipynb
|   |   WQP_Statistics.ipynb
│
└───packages
└───setup
└───static
|
|   .dockerignore
|   .env
|   .gitignore
|   docker-compose.yml
|   Dockerfile
|   environment.yml
│   README.md 


```

3. Build the VM docker container.

```
# Build the Image
docker-compose build

# Run the container
docker-compose up -d
```