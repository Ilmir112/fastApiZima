import asyncio
import difflib
import email
import imaplib
import re
import smtplib
from datetime import datetime, timedelta
from io import BytesIO
from nntplib import decode_header

import pandas as pd
import pytz
from fastapi.params import Depends
from pydantic import EmailStr
import email.utils

from sqlalchemy.sql.functions import current_user

from zimaApp.brigade.dao import BrigadeDAO
from zimaApp.config import settings
from zimaApp.files.dao import ExcelRead
from zimaApp.logger import logger
from zimaApp.repairGis.schemas import SRepairsGis
from zimaApp.repairtime.dao import RepairTimeDAO

from zimaApp.summary.schemas import SUpdateSummary
from zimaApp.tasks.celery_app import celery_app
from zimaApp.tasks.email_templates import create_zima_confirmation_template
from telegram import Bot

from zimaApp.tasks.rabbitmq.producer import send_message_to_queue
from zimaApp.users.models import Users
from zimaApp.well_classifier.dao import WellClassifierDAO
from zimaApp.wells_data.dao import WellsDatasDAO


@celery_app.task
def send_plan_work_confirmation_email(well_repair: dict, email_to: EmailStr):
    email_to_mock = settings.SMTP_USER
    msg_content = create_zima_confirmation_template(well_repair, email_to_mock)

    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.REDIS_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASS)
        server.send_message(msg_content)


@celery_app.task
def send_message(chat_id, text, token=settings.TOKEN):
    bot = Bot(token)
    asyncio.run(bot.send_message(chat_id, text=text))


@celery_app.task(name="tasks.check_emails_async")
def check_emails_async():
    result = None
    try:
        logger.info("Задача check_emails_async запущена")
        msg_bytes = check_emails()
        result = asyncio.run(send_message_to_queue(msg_bytes, "repair_gis"))
        return result
    except Exception as e:
        logger.info(f"Ошибка в check_emails_async: {e}")
        return result

@celery_app.task(name="tasks.check_emails_summary")
def check_emails_summary():
    result = None
    try:
        logger.info("Задача check_emails_summary запущена")
        excel_info = check_emails_for_excel()
        result = asyncio.run(send_message_to_queue(excel_info, "summary_info"))
        return result
    except Exception as e:
        logger.info(f"Ошибка в check_emails_async: {e}")
        return result

def check_emails():
    try:
        mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER)
        mail.login(settings.EMAIL_ACCOUNT, settings.PASSWORD)
        mail.select("inbox")
        subject_search = "Телефонограмма"
        search_criteria = f'(SUBJECT "{subject_search}")'
        search_bytes = search_criteria.encode("utf-8")
        status, messages = mail.search(None, search_bytes)
        email_ids = messages[0].split()

        now_time = datetime.now()
        message_list = []
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg_bytes = response_part[1]
                    msg = email.message_from_bytes(msg_bytes)
                    from_header = msg.get("From")
                    from_address = email.utils.parseaddr(from_header)[1]
                    date_header = msg.get("Date")

                    # Парсинг даты и времени получения
                    date_tuple = email.utils.parsedate_tz(date_header)
                    if date_tuple:
                        dt = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        received_date = dt.strftime("%Y-%m-%d %H:%M")

                    # Обработка заголовка Subject
                    raw_subject = msg["Subject"]
                    if raw_subject:
                        decoded_headers = decode_header(raw_subject)
                        if decoded_headers:
                            first_part = decoded_headers
                            if len(first_part) == 2:
                                subject, encoding = first_part
                            else:
                                subject = first_part
                                encoding = None
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or "utf-8")
                        else:
                            subject = ""
                    else:
                        subject = ""
                    if subject and "RE:" not in subject.upper():
                        if dt < now_time - timedelta(minutes=2):
                            continue  # пропускаем это письмо

                    # Остальной код обработки тела письма...
                    body_text = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body_bytes = part.get_payload(decode=True)
                                body_text += body_bytes.decode(
                                    part.get_content_charset() or "utf-8"
                                )
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        body_text = body_bytes.decode(
                            msg.get_content_charset() or "utf-8"
                        )

                    if (
                            from_address in settings.EMAIL_CHECK_LIST
                            and "просто" in body_text
                    ):
                        message_list.append((from_address, subject, body_text, dt))
        mail.logout()
        return message_list
        #     try:
        #        result = await send_message_to_queue(msg_bytes, "repair_gis")
        #
        #        return result
        #     except Exception as e:
        #         print(e)

        # # Проверка содержания письма
        # if "просто" in body_text:
        #     parsed_data = parse_telephonegram(body_text, from_address, dt)
        #     if parsed_data:
        #         return add_telephonegram_to_db(parsed_data)


    except Exception as e:
        logger.error(f"Error checking emails: {e}")


def find_best_match(name: str, text: str):
    # Проверка точного вхождения
    if name in text:
        return 1
    # Если нет точного совпадения, ищем наиболее похожее
    else:
        # Получаем список всех возможных фрагментов из текста для сравнения
        # Можно искать по словам или по подстрокам длиной примерно с название
        # Для простоты сравним с полным текстом
        seq = difflib.SequenceMatcher(None, name, text)
        ratio = seq.ratio()
        return ratio


# Функция для парсинга тела письма и извлечения нужных данных
async def parse_telephonegram(body_text: str, from_address: email, dt: datetime):
    from zimaApp.well_classifier.router import get_unique_well_data

    # Пример парсинга: ищем дату и описание (подстроить под конкретный формат)
    # Для примера ищем строку с датой и текст сообщения
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4}г\.)", body_text)
    if from_address == "teh-BNPT@bn.rosneft.ru":
        contractor_gis = "ООО «Башнефть-ПЕТРОТЕСТ»"
    elif from_address == "alert@bngf.ru":
        contractor_gis = "АО «Башнефтегеофизика»"
    else:
        contractor_gis = ""

    body_text = body_text[:600]
    # Ваши шаблоны
    date_pattern = r"(\d{1,2}\.\d{1,2}\.\d{2,4})"
    time_pattern = r"(\d{1,2}:\d{2})"
    # Регулярное выражение для номера скважины
    well_number_pattern = r"скв\.?\s*(\d+)"
    # Регулярное выражение для площади месторождения
    field_pattern = r"скв\.?\s*\d+\s+([^,]+),"

    # Поиск даты
    date_match = re.search(date_pattern, body_text)
    date_str = date_match.group(1) if date_match else None

    # Поиск времени
    time_match = re.search(r"с\s*" + time_pattern, body_text)
    time_str = time_match.group(1) if time_match else None

    if date_str and time_str:
        # Объединяем дату и время в строку
        datetime_str = f"{date_str} {time_str}"
        # Определяем формат для strptime
        # В зависимости от года (двух- или четырехзначный)
        if len(date_str.split(".")[-1]) == 2:
            dt_format = "%d.%m.%y %H:%M"
        else:
            dt_format = "%d.%m.%Y %H:%M"
        # Преобразуем в datetime
        dt_object = datetime.strptime(datetime_str, dt_format)
    else:
        dt_object = None

    # Поиск номера скважины
    well_match = re.search(well_number_pattern, body_text)
    well_number_found = well_match.group(1) if well_match else None
    wells_area_list = [
        result
        for result in await WellClassifierDAO.get_unique_well_area()
        if len(result) > 4
    ]

    # Для каждого элемента ищем лучшее совпадение
    results = []

    for name in sorted(wells_area_list):
        for text in body_text.split(" "):
            ratio = find_best_match(name.replace("_", " ").lower(), text.lower())
            if ratio > 0.007:
                results.append((name, ratio))

    well_area = max(results, key=lambda x: x[1])[0]

    find_wells = await WellsDatasDAO.find_one_or_none(
        well_area=well_area, well_number=well_number_found
    )
    if find_wells:
        return {
            "wells_id": find_wells.id,
            "contractor_gis": contractor_gis,
            "message_time": dt,
            "work_goal": "dff",
            "downtime_start": dt_object,
            "downtime_reason": body_text,
            # добавьте другие поля по необходимости
        }
    return None


required_columns = ['Дата', 'Работы', 'Примечание']


async def add_telephonegram_to_db(parsed_data: dict):
    from zimaApp.repairGis.router import add_wells_data

    # Предполагается, что у вас есть экземпляр router или вы можете вызвать функцию напрямую.
    # Ниже пример вызова через API роутер (можно заменить на прямой вызов функции DAO)

    repair_info = SRepairsGis(
        contractor_gis=parsed_data["contractor_gis"],
        message_time=parsed_data["message_time"],
        work_goal=parsed_data["work_goal"],
        downtime_start=parsed_data["downtime_start"],
        downtime_end=None,
        downtime_duration=None,
        downtime_reason=parsed_data["downtime_reason"],
        contractor_opinion=None,
        downtime_duration_meeting_result=None,
        meeting_result=None,
        image_pdf=None,
        well_id=parsed_data["wells_id"],
    )

    # Вызов вашего роутера или функции добавления данных
    return await add_wells_data(repair_info)


def decode_mime_words(s):
    decoded_fragments = decode_header(s)
    decoded_string = ''
    if len(decoded_fragments) == 2:
        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                encoding = encoding or 'utf-8'
                try:
                    decoded_string += fragment.decode(encoding)
                except Exception:
                    decoded_string += fragment.decode('utf-8', errors='ignore')
            else:
                decoded_string += fragment
    else:
        decoded_string = decoded_fragments
    return decoded_string


def check_emails_for_excel():
    try:
        mail = imaplib.IMAP4_SSL(settings.IMAP_SERVER)
        mail.login(settings.EMAIL_ACCOUNT, settings.PASSWORD)
        mail.select("inbox")
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        today_str = now.strftime('%d-%b-%Y')  # формат: 01-Oct-2023

        status, messages = mail.search(None, f'SINCE {today_str}')

        email_ids = messages[0].split()
        results_files = []

        now_time = datetime.now()

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    # Получаем время письма из заголовка Date
                    date_header = msg.get("Date")
                    if date_header:
                        # Преобразуем строку в datetime
                        email_date_tuple = email.utils.parsedate_tz(date_header)
                        if email_date_tuple:
                            email_timestamp = email.utils.mktime_tz(email_date_tuple)
                            email_datetime = datetime.fromtimestamp(email_timestamp)

                            # Проверяем, что письмо пришло за последний час
                            if now_time - timedelta(hours=1) <= email_datetime <= now_time:
                                for part in msg.walk():
                                    content_disposition = str(part.get("Content-Disposition"))
                                    if "attachment" in content_disposition:
                                        filename = part.get_filename()
                                        if filename:
                                            filename = decode_mime_words(filename)
                                            if filename.endswith(('.xlsx', '.xls')):
                                                file_data = part.get_payload(decode=True)
                                                excel_bytesio = BytesIO(file_data)
                                                try:
                                                    df = pd.read_excel(excel_bytesio)
                                                    if all(col in df.columns for col in required_columns):
                                                        results_files.append({
                                                            "filename": filename,
                                                            "dataframe": df
                                                        })
                                                except Exception as e:
                                                    print(f"Ошибка чтения файла {filename}: {e}")

        return results_files

    except Exception as e:
        print(f"Ошибка при проверке почты: {e}")
        return []


async def work_with_excel_summary(filename, df):
    from zimaApp.repairtime.router import open_summary_data
    from zimaApp.summary.router import add_summary

    excel_xlrd = ExcelRead(df)
    # Регулярное выражение для поиска номера бригады и МКВ
    brigade_pattern = r'№\s*(\d+)'  # ищет номер бригады после символа №
    mkv_pattern = r'скв\s*([\w\d]+)'  # ищет МКВ после 'МКВ'

    # Поиск номера бригады
    brigade_match = re.search(brigade_pattern, filename)
    # Поиск МКВ
    mkv_match = re.search(mkv_pattern, filename)
    well_number = mkv_match.group(1)
    brigade_number = brigade_match.group(1)
    skv_number, mesto_matches, region, date_value, start_time = excel_xlrd.find_pars()
    if mesto_matches:
        mesto_matches = mesto_matches[0]
    else:
        mesto_matches = ''
    if skv_number not in well_number:
        return
    contractor = "ООО Ойл-сервис"
    well_data = await WellsDatasDAO.find_all(well_number=well_number, contractor=contractor)

    if well_data:
        if len(well_data) == 1:
            well_data = well_data[0]
        elif len(well_data) > 1:
            for data in well_data:
                if data.well_oilfield[:4].lower() == mesto_matches[:4].lower():
                    well_data = data
                    break
    else:
        logger.error(f'Скважины {skv_number} по бригаде {brigade_number} не в базе')
        return

    if type(well_data) is list:
        logger.error(f"Добавление сводки не получилось\nНесколько скважин с номером {skv_number} ")
        return

    if brigade_number:
        brigade_data = await BrigadeDAO.find_one_or_none(number_brigade=brigade_number, contractor=contractor)

        if brigade_data and well_number == well_data.well_number:

            summary_info = await RepairTimeDAO.find_one_or_none(brigade_id=brigade_data.id, status='открыт')

            for row in df.itertuples():
                date_str, work_details = ExcelRead.extract_datetimes(row)
                work_data = SUpdateSummary(date_summary=date_str,
                                           work_details=work_details)
                if summary_info is None:

                    open_status = await open_summary_data(
                        summary_info=work_data,
                        well_data=well_data,
                        brigade=brigade_data
                    )
                    if open_status.status_code == 409:
                        break

                    summary_info = open_status["data"]
                    continue

                results = await add_summary(work_data=work_data, work_details=work_details,
                                            summary_info=summary_info.id)

                if 'завершен' in work_details.lower() or 'сдача с' in work_details.lower():
                    match = re.search(r'\d{2}:\d{2}', work_details.lower())
                    if match:
                        time_str = match.group()
                        t = datetime.strptime(time_str, "%H:%M").time()

                        # заменяем время
                        date_str = date_str.replace(hour=t.hour, minute=t.minute) + timedelta(hours=5)
                        results = await RepairTimeDAO.update_data(summary_info.id, end_time=date_str, status="закрыт")

        else:
            logger.info(f"Бригада {brigade_number} отсутствует")
            return
    return well_data
