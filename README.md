# midjourney-cient

the _SINGULARITY_ is_near

## Requirements

- Python
- pip
- MidJourney and Discord API account

## Set up

Create a config.yaml file with the same schema as config.example.yaml and fill in the the required variables

### Run it

Copy `config.example.yaml` into `config.yaml` and set it's variables

### Docker

```bash
docker build -t midjourney-client .
docker run -d -p 8001:8001 -v /var/run/docker.sock:/var/run/docker.sock midjourney-client
```

### Raw

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
