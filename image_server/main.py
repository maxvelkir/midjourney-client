from config import IMAGE_PATH
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/" + IMAGE_PATH,
    StaticFiles(directory=IMAGE_PATH),
    name="images",
)
