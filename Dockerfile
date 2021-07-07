FROM python:3.8.11-slim-buster

RUN apt update && apt install -y --no-install-recommends \
  curl \
  hmmer \
  fasttree \
  raxml \
  time \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p -m 700 /usr/local/var/data \
 && chown daemon:daemon /usr/local/var/data

WORKDIR /usr/src/app
COPY lorax ./lorax

USER daemon

CMD ["gunicorn", "--bind=0.0.0.0:8000", "lorax:app"]
VOLUME ["/usr/local/var/data"]

EXPOSE 8000
