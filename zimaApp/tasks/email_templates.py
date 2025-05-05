from email.message import EmailMessage

from pydantic import EmailStr

from zimaApp.config import settings


def create_booking_confirmation_template(
        well_repair: dict,
        email_to: EmailStr
):
    email = EmailMessage()
    email["Subject"] = 'План сделан'
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
        <h1> План сделан </h1>
        Нужно проверить план работ {well_repair['well_number']} {well_repair["well_area"]}
        """,
        subtype="html")