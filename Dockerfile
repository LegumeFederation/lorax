FROM python:3.8.9-slim-buster

RUN apt update && apt install -y --no-install-recommends \
  hmmer \
  fasttree \
  raxml \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app
COPY lorax ./lorax
RUN echo 'version = "0.94"' > lorax/version.py

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "lorax:app"]
