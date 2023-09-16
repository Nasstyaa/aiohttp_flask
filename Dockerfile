FROM python:3.11
COPY . ./flask
WORKDIR /flask

# pip install --no-cache-dir -r /app/requirements.txt