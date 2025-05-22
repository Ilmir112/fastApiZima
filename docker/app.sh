#!/bin/bash

alembic upgrade head

gunicorn ZimaApp.main:App --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=192.167.1.202:8000