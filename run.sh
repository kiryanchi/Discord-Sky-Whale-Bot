#zsh

poetry export --without-hashes --format=requirements.txt > requirements.txt
docker compose up -d --build