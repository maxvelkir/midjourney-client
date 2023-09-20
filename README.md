# midjourney-cient

the _SINGULARITY_ is_near

This is a client for the MidJourney API. It is a simple web server that listens for events from the MidJourney API and sends them to a Discord channel.

It is split into 2 parts:

- A web server that listens for image_generation events from the BE
- A web server that serves the generated images

## Requirements

- Python
- pip
- MidJourney and Discord API account

## Set up

Create a config.yaml file with the same schema as config.example.yaml and fill in the the required variables

### Run it

Copy `config.example.yaml` into `config.yaml` and set it's variables

### Docker

#### image_generator

```bash
docker build -t midjourney-generator .
docker run \
-d \
-p 8001:8001 \
-v ./images:/code/images \
-v /var/run/docker.sock:/var/run/docker.sock \
midjourney-generator
```

#### image_server

```bash
docker build -t midjouney-server .
docker run \
-d \
-p 8002:8002 \
-v ./images:/code/images \
midjourney-server
```

### Raw

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001 # or 8002 for the server
```
