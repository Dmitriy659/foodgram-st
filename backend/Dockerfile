FROM python:3.12-slim

RUN apt-get update --fix-missing && \
    apt-get upgrade -y && \
    apt-get install -y libpq-dev gcc netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

COPY .. .

RUN chmod +x run_server.sh
ENTRYPOINT ["./run_server.sh"]
