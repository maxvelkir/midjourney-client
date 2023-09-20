from pathlib import Path

import yaml

# Config
CONFIG_PATH = "config.yaml"

with open(CONFIG_PATH, mode="r") as fp:
    config = yaml.safe_load(fp)

IMAGE_PATH = config["static"]["images"]
