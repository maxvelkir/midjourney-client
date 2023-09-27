from config import IMAGE_PATH
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/" + IMAGE_PATH,
    StaticFiles(directory=IMAGE_PATH),
    name="images",
)

origins = [
    "http://localhost:8000",
    "http://portal.omnithink.ai",
    "https://portal.omnithink.ai",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
