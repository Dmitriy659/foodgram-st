# Foodgram

## 🛠️ Использующиеся технологии

- **Backend**: Python, Django, Django REST Framework (DRF), Gunicorn  
- **Frontend**: React  
- **Web-сервер**: Nginx  
- **Контейнеризация**: Docker

---

## Подготовка перед запуском проекта

Перед запуском проекта необходимо создать файл `.env` и ввести данные для работы проекта.  
Шаблон можно посмотреть в файле `.env_template`.

---

## Запуск проекта локально

### 1. Клонирование репозитория

```bash
git clone https://github.com/Dmitriy659/foodgram-st.git
```

### 2. Установка Docker, Docker-compose
```bash
sudo apt update
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin
```
### 3. Создать образы и контейнеры, испоьзуя команду ниже в директории infra
```bash
docker compose up
```
При создании контейнера foodgram-backend будет запущен скрипт run_server.sh, который применит все необходимые миграции, а также загрузит в таблицу ингредиенты, если их там нет
