FROM python:3.11-bullseye

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]