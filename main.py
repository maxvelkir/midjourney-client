import asyncio
from contextlib import asynccontextmanager
from typing import List

import docker
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import images
import midjourney
import schemas
from config import IMAGE_PATH
from logger import logger

router = APIRouter()

QUEUES = {}


# split and save images in the background for concurrency
async def periodic_task():
    while True:
        await asyncio.sleep(10)
        logger.info(f"heartbeat")

        for priority_gen_image in QUEUES["PRIORITY_IMAGE_QUEUE"]:
            if priority_gen_image["fail_count"] > 5:
                logger.info(
                    f"Failed to generate image for idea_id: {priority_gen_image['image'].idea_id}"
                )
                if priority_gen_image["container"].status == "running":
                    priority_gen_image["container"].remove(force=True)
                QUEUES["PRIORITY_IMAGE_QUEUE"].remove(priority_gen_image)
                continue

            is_generated = images.get_split_save_image(
                priority_gen_image["image"], priority_gen_image["container"]
            )

            if is_generated:
                priority_gen_image["container"].remove(force=True)
                QUEUES["PRIORITY_IMAGE_QUEUE"].remove(priority_gen_image)
            else:
                priority_gen_image["fail_count"] += 1

        for gen_image in QUEUES["IMAGE_QUEUE"]:
            if QUEUES["PRIORITY_IMAGE_QUEUE"]:
                break

            if gen_image["fail_count"] > 5:
                logger.info(
                    f"Failed to generate image for idea_id: {gen_image['image'].idea_id}"
                )
                if gen_image["container"].status == "running":
                    gen_image["container"].remove(force=True)
                QUEUES["IMAGE_QUEUE"].remove(gen_image)
                continue

            is_generated = images.split_and_save_image(
                gen_image["image"], gen_image["container"]
            )

            if is_generated:
                gen_image["container"].remove(force=True)
                QUEUES["IMAGE_QUEUE"].remove(gen_image)
            else:
                gen_image["fail_count"] += 1

        if not QUEUES["PRIORITY_IMAGE_QUEUE"] and not QUEUES["IMAGE_QUEUE"]:
            client = docker.DockerClient(base_url="unix://var/run/docker.sock")
            client.containers.prune()


async def generate_images(images: [schemas.Image]):
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
        await asyncio.sleep(3.5)
        if i % 3 == 1:
            await asyncio.sleep(3.5)


@asynccontextmanager
async def lifespan(app=FastAPI):
    QUEUES["PRIORITY_IMAGE_QUEUE"] = []
    QUEUES["IMAGE_QUEUE"] = []

    asyncio.create_task(periodic_task())

    yield

    QUEUES["PRIORITY_IMAGE_QUEUE"] = []
    QUEUES["IMAGE_QUEUE"] = []


app = FastAPI(lifespan=lifespan)

origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/" + IMAGE_PATH,
    StaticFiles(directory=IMAGE_PATH),
    name="images",
)


@router.post(
    "/queue_midjourney_image_generation",
    status_code=status.HTTP_201_CREATED,
)
async def queue_midjourney_image_generation(
    gen_images: List[schemas.Image],
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(generate_images, gen_images)


app.include_router(router)
