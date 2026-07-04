FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends screen openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data && chown 1000:1000 data

CMD ["python", "main.py"]
