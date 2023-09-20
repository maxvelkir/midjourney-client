import asyncio
from contextlib import asynccontextmanager
from typing import List

import docker
import midjourney
import schemas
from fastapi import APIRouter, BackgroundTasks, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from logger import logger

import images

router = APIRouter()

QUEUES = {}


def clear_docker_continers():
    client = docker.DockerClient(base_url="unix://var/run/docker.sock")
    containers = client.containers.list(filters={"ancestor": "omegasz/midjourney-api"})
    for container in containers:
        container.remove(force=True)


# split and save images in the background for concurrency
async def periodic_task():
    while True:
        await asyncio.sleep(10)
        logger.info(f"heartbeat")

        # cleanup leftover containers
        if not QUEUES["PRIORITY_IMAGE_QUEUE"] and not QUEUES["IMAGE_QUEUE"]:
            clear_docker_continers()

        for queue in QUEUES.keys():
            if QUEUES["PRIORITY_IMAGE_QUEUE"] and queue == "IMAGE_QUEUE":
                break

            for gen_image in QUEUES[queue]:
                image = gen_image["image"]
                container = gen_image["container"]
                fail_count = gen_image["fail_count"]

                if fail_count > 5:
                    logger.info(
                        f"Failed to generate image from {queue} for idea_id: {image.idea_id}"
                    )

                    container.remove(force=True)
                    QUEUES[queue].remove(gen_image)

                    continue

                is_generated = images.get_split_save_image(image, container)

                if is_generated:
                    container.remove(force=True)
                    QUEUES[queue].remove(gen_image)
                else:
                    gen_image["fail_count"] = fail_count + 1


async def generate_images(images: [schemas.GenImage]):
    i = 0
    for ungenerated_image in images:
        # start containers to generate images without waiting for them to finish (keep it async)
        container = await midjourney.prompt(ungenerated_image.image_prompt)
        if i < 4:
            QUEUES["PRIORITY_IMAGE_QUEUE"].append(
                {"image": ungenerated_image, "container": container, "fail_count": 0}
            )
            logger.info(
                f"Queued priority image for idea_id: {ungenerated_image.idea_id}"
            )
        else:
            QUEUES["IMAGE_QUEUE"].append(
                {"image": ungenerated_image, "container": container, "fail_count": 0}
            )
            logger.info(f"Queued image for idea_id: {ungenerated_image.idea_id}")

        # sending requests too fast will cause MidJourney to miss some generations
        await asyncio.sleep(5)
        if i % 3 == 1:
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app=FastAPI):
    QUEUES["PRIORITY_IMAGE_QUEUE"] = []
    QUEUES["IMAGE_QUEUE"] = []

    asyncio.create_task(periodic_task())

    yield

    QUEUES["PRIORITY_IMAGE_QUEUE"] = []
    QUEUES["IMAGE_QUEUE"] = []


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
    "http://34.132.251.186",
    "http://34.132.251.186:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.post(
    "/queue_midjourney_image_generation",
    status_code=status.HTTP_201_CREATED,
)
async def queue_midjourney_image_generation(
    gen_images: List[schemas.GenImage],
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(generate_images, gen_images)


@router.get(
    "/flush_queue",
    status_code=status.HTTP_201_CREATED,
)
async def flush_queue():
    QUEUES["PRIORITY_IMAGE_QUEUE"] = []
    QUEUES["IMAGE_QUEUE"] = []

    clear_docker_continers()


app.include_router(router)
