FROM python:3.9

RUN mkdir /zimaApp

WORKDIR /zimaApp

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Предоставляет доступ контейнеру для запуска bash скрипта, если это необходимо
# Запускать bash скрипты без доступа к ним на ОС Linux невозможно. На Windows - возможно,
# но так как контейнеры работают на Linux, приходится давать доступ независимо от вашей ОС.
# RUN chmod a+x /booking/docker/*.sh

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Эта команда выведена в bash скрипт
# RUN alembic upgrade head

# КОММЕНТАРИЙ НИЖЕ ТОЛЬКО ДЛЯ DOCKER COMPOSE. РАСКОММЕНТИРУЙТЕ КОД, ЕСЛИ ВЫ ИСПОЛЬЗУЕТЕ ТОЛЬКО DOCKERFILE
# Эта команда также выведена в bash скрипт
 CMD ["gunicorn", "ZimaApp.main:app", "--workers", "3", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=192.167.1.202:8000192.167.1.202:8000"]