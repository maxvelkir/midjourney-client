FROM python:3.11-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./config.yaml /code/config.yaml
COPY ./main.py /code/main.py
COPY ./config.py /code/config.py
COPY ./images.py /code/images.py
COPY ./logger.py /code/logger.py
COPY ./schemas.py /code/schemas.py
COPY ./midjourney.py /code/midjourney.py

RUN mkdir /code/images

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
