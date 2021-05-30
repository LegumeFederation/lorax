FROM python:3.8.10-slim-buster

RUN apt update && apt install -y --no-install-recommends \
  curl \
  hmmer \
  fasttree \
  raxml \
  time \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app
COPY lorax ./lorax

CMD ["gunicorn", "lorax:app"]
