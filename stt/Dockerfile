FROM python:3.10-slim

RUN apt-get update && apt-get install -y libsndfile1

WORKDIR /stt


RUN apt-get update && apt-get install -y libsndfile1


COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY ./app ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
