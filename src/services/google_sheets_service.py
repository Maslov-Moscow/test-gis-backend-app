import math
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
from src.config import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'
WORKSHEET_NAME = 'Лист1'

# Авторизация
gc = None
if os.path.exists(SERVICE_ACCOUNT_FILE):
    credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
    )
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)
else:
    print("Файл credentials.json не найден. Запись в таблицу отключена.")



def compute_area_square_meters(radius_meters: float) -> float:
    """
    Вычисляет площадь круга по радиусу в метрах.

    :param radius_meters: Радиус круга
    :return: Площадь в м²
    """
    return math.pi * radius_meters ** 2


def ensure_worksheet_header(worksheet: gspread.Worksheet) -> None:
    """
    Проверяет и устанавливает заголовок таблицы, если он отсутствует.
    """
    existing_header = worksheet.row_values(1)
    expected_header = ["Дата", "Широта", "Долгота", "Радиус (м)", "Площадь (м²)"]

    if existing_header != expected_header:
        worksheet.insert_row(expected_header, index=1)


def log_polygon_request_to_google_sheet(
    latitude: float,
    longitude: float,
    radius_meters: float,
    spreadsheet_id: str = settings.SPREADSHEET_ID,
    worksheet_name: str = WORKSHEET_NAME
) -> None:
    """
    Добавляет запись в Google Таблицу о выполненном запросе.

    :param latitude: Широта
    :param longitude: Долгота
    :param radius_meters: Радиус в метрах
    :param spreadsheet_id: ID таблицы (по умолчанию из конфига)
    :param worksheet_name: Имя листа (по умолчанию из конфига)
    """
    if gc is None:
        print("Логирование пропущено — отсутствует credentials.json")
        return
    try:
        sheet = gc.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        ensure_worksheet_header(worksheet)

        area_sq_m = compute_area_square_meters(radius_meters)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, latitude, longitude, radius_meters, area_sq_m]
        worksheet.append_row(row, value_input_option='USER_ENTERED')

    except Exception as e:
        raise RuntimeError(f"Ошибка при записи в Google Таблицу: {e}")
