#!/bin/bash

if [[ "${1}" == "celery" ]]; then
    celery --app=ZimaApp.tasks.celery:celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
    celery --app=ZimaApp.tasks.celery:celery flower
fi