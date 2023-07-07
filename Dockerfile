FROM tiangolo/uvicorn-gunicorn:python3.10

RUN apt-get update
RUN apt-get install libpq-dev python3-dev -y
RUN apt-get install openssl
RUN apt-get install ffmpeg -y
COPY . .
RUN pip install --upgrade pip && pip install -r req.txt
