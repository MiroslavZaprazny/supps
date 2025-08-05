FROM python:3.13-slim

WORKDIR /src

ENV SITE = ""

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    pkg-config \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src

CMD python3 src/main.py $SITE