FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Script d'entrée qui lit $PORT au runtime
RUN echo '#!/bin/sh\nexec python app.py' > /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE ${PORT:-8080}

ENTRYPOINT ["/entrypoint.sh"]
