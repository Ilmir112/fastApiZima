#!/bin/bash

alembic upgrade head

gunicorn zimaApp.main:App --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000