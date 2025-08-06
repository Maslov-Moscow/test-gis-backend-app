from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .schemas import CoordinatesRequest, GeoJSONResponse
from .services.geojson_services import (
    create_geojson_polygon,
    get_from_cache,
    save_to_cache,
)
from .services.google_sheets_service import log_polygon_request_to_google_sheet

router = APIRouter()

@router.post("/convert-to-polygon", response_model=GeoJSONResponse)
async def convert_to_polygon(
    request: CoordinatesRequest,background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    """
    Преобразует координаты и радиус в GeoJSON-полигон.

    Workflow:
      1. Проверяет наличие полигона в кэше по координатам и радиусу.
      2. Если найден — возвращает кэшированный результат.
      3. Если нет — создает новый полигон, сохраняет его в кэш и возвращает.
      4. Запись в гугл таблицу
    """
    cached = await get_from_cache(db, request.latitude, request.longitude, request.radius)
    if cached:
        return cached

    geojson = await create_geojson_polygon(
        request.latitude, request.longitude, request.radius
    )
    await save_to_cache(db, request.latitude, request.longitude, request.radius, geojson)

    background_tasks.add_task(
    log_polygon_request_to_google_sheet,
        request.latitude,
        request.longitude,
        request.radius,
    )
    return geojson
