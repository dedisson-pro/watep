FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

CMD ["/bin/sh", "-c", "python -c \"import os,subprocess; subprocess.run(['gunicorn','app:app','--bind','0.0.0.0:'+str(os.environ.get('PORT','8080')),'--workers','2','--timeout','120'])\""]
