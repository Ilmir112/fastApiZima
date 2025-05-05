import smtplib

from pydantic import EmailStr

from zimaApp.config import settings
from zimaApp.tasks.celery_work import celery_app
from zimaApp.tasks.email_templates import create_booking_confirmation_template


@celery_app.task
def send_plan_work_confirmation_email(
        well_repair: dict,
        email_to: EmailStr
):
    email_to_mock = settings.SMTP_USER
    msg_content = create_booking_confirmation_template(well_repair, email_to_mock)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.REDIS_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)

