import re
from typing import Optional

import docker

from config import config
from logger import logger

client = docker.DockerClient(base_url="unix://var/run/docker.sock")


def get_midjourney_image_url(container) -> Optional[str]:
    regex = r"https:\/\/cdn\.discordapp\.com\/attachments\/.+?png"

    try:
        logs = container.logs().decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to get logs from container: {e}")
        return None

    match = re.search(regex, logs)

    if match:
        return match.group(0)


async def prompt(prompt: str):
    if prompt == "None":
        return None

    server_id = config["midjourney"]["server_id"]
    channel_id = config["midjourney"]["channel_id"]
    salai_token = config["midjourney"]["salai_token"]

    container = client.containers.run(
        "omegasz/midjourney-api",
        environment=[
            f"SERVER_ID={server_id}",
            f"CHANNEL_ID={channel_id}",
            f"SALAI_TOKEN={salai_token}",
            f"PROMPT={prompt}. Add small random feature --turbo",
        ],
        command="tsx example/imagine-ws.ts",
        detach=True,
        remove=False,
        auto_remove=False,
    )

    return container
