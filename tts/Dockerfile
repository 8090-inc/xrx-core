FROM python:3.10-slim

WORKDIR /tts
    
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /tts/cache

COPY ./app ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]