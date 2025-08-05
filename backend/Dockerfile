FROM python:3.11-slim-bullseye

WORKDIR /code

# Install socat utility
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY . /code/app


CMD ["fastapi", "run", "app/main.py", "--port", "80"]
