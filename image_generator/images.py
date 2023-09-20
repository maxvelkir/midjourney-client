import io

import midjourney
import requests
import schemas
from config import IMAGE_PATH
from logger import logger
from PIL import Image


def image_crop(
    image: schemas.GenImage, byte_code: bytes, xPieces: int, yPieces: int
) -> bool:
    pil_image = Image.open(io.BytesIO(byte_code))

    imgwidth, imgheight = pil_image.size
    height = imgheight // yPieces
    width = imgwidth // xPieces

    for i in range(0, yPieces):
        for j in range(0, xPieces):
            box = (j * width, i * height, (j + 1) * width, (i + 1) * height)

            try:
                gen_image = pil_image.crop(box)
            except Exception as e:
                logger.error(f"Failed to split image with hash: {image.hash}")
                return False

            try:
                gen_image_url = (
                    IMAGE_PATH + image.hash + "-" + str(i) + "-" + str(j) + ".png"
                )

                gen_image.save(gen_image_url)

                logger.info(f"Saved image to: {gen_image_url}")
            except Exception as e:
                logger.error(e)
                return False

    return True


def get_split_save_image(image: schemas.GenImage, container) -> bool:
    midjourney_image_url = midjourney.get_midjourney_image_url(container)

    if not midjourney_image_url:
        return False
    image.midjourney_image_url = midjourney_image_url

    logger.info(f"Image url is: {image.midjourney_image_url}")
    logger.info(f"Creating image for idea_id: {image.idea_id}")

    try:
        image_byte_code = requests.get(image.midjourney_image_url).content
    except Exception as e:
        logger.info(f"Failed to get image from url: {e}")
        return False

    if not image_crop(image, image_byte_code, 2, 2):
        logger.error(
            f"Failed to create images for idea: {image.idea_id}. Crop/Save failed."
        )
        return False

    return True
