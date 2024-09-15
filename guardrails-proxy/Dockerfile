FROM python:3.10

WORKDIR /guardrails-proxy

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install guardrails-ai
RUN guardrails hub install hub://guardrails/toxic_language

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet')"

COPY ./app ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]