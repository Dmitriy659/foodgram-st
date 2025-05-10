FROM python:3.12-slim

# Установка зависимостей
RUN apt-get update --fix-missing && \
    apt-get upgrade -y && \
    apt-get install -y libpq-dev gcc netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта, включая run_server.sh
COPY .. .

# Установка прав на выполнение для скрипта
RUN chmod +x run_server.sh

# Указание правильного пути для ENTRYPOINT
ENTRYPOINT ["./run_server.sh"]
