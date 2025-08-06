import asyncio
import hashlib
import time

import geojson
from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import transform
from sqlalchemy import select

from .db import AsyncSession
from .models import GeoJSONCache

def make_cache_key(latitude: float, longitude: float, radius: float) -> str:
    """
    Генерирует уникальный ключ для кэширования по координатам и радиусу.

    :param latitude: Широта (float)
    :param longitude: Долгота (float)
    :param radius: Радиус (float)
    :return: Хеш-строка (str)
    """
    key_str = f"{latitude}:{longitude}:{radius}"
    return hashlib.sha256(key_str.encode()).hexdigest()

async def get_from_cache(
    db: AsyncSession, latitude: float, longitude: float, radius: float
):
    """
    Получает результат из кэша по координатам и радиусу.

    :param db: Сессия БД (AsyncSession)
    :param latitude: Широта (float)
    :param longitude: Долгота (float)
    :param radius: Радиус (float)
    :return: Результат из кэша (dict) или None
    """
    key = make_cache_key(latitude, longitude, radius)
    q = await db.execute(select(GeoJSONCache).where(GeoJSONCache.hash == key))
    row = q.scalar_one_or_none()
    return row.result if row else None

async def save_to_cache(
    db: AsyncSession, latitude: float, longitude: float, radius: float, result: dict
):
    """
    Сохраняет результат в кэш по координатам и радиусу.

    :param db: Сессия БД (AsyncSession)
    :param latitude: Широта (float)
    :param longitude: Долгота (float)
    :param radius: Радиус (float)
    :param result: Сохраняемый результат (dict)
    """
    key = make_cache_key(latitude, longitude, radius)
    cache_entry = GeoJSONCache(
        hash=key,
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        result=result,
    )
    db.add(cache_entry)
    await db.commit()


async def create_geojson_polygon(
    lat: float, lon: float, radius_meters: float
) -> dict:
    """
    Асинхронно строит GeoJSON-полигон-круг заданного радиуса вокруг точки.

    :param lat: Широта центра (float)
    :param lon: Долгота центра (float)
    :param radius_meters: Радиус круга в метрах (float)
    :return: GeoJSON-полигон (dict)
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, compute_geojson_polygon, lat, lon, radius_meters
    )


def compute_geojson_polygon(
    lat: float, lon: float, radius_meters: float
) -> geojson.Feature:
    """
    Строит GeoJSON-полигон-круг заданного радиуса вокруг точки (lat, lon).

    Flow:
      1. Переводит координаты центра в метры (EPSG:3857).
      2. Строит круг нужного радиуса.
      3. Преобразует координаты круга обратно в градусы (EPSG:4326).
      4. Возвращает geojson.Feature с геометрией круга.

    :param lat: Широта центра (float)
    :param lon: Долгота центра (float)
    :param radius_meters: Радиус круга в метрах (float)
    :return: geojson.Feature с геометрией круга
    """
    try:
        time.sleep(5)  # Имитируем тяжелую задачу 5 секунд

        center = Point(lon, lat)
        project_to_m = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True).transform
        project_back_to_deg = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True).transform
        center_m = transform(project_to_m, center)
        circle_m = center_m.buffer(radius_meters, resolution=32)
        circle_deg = transform(project_back_to_deg, circle_m)
        geojson_polygon = geojson.Feature(geometry=circle_deg, properties={})

        return geojson_polygon
    except Exception as e:
        raise RuntimeError("Ошибка обработки координат") from e
