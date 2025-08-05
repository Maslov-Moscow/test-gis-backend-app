from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .schemas import CoordinatesRequest, GeoJSONResponse
from .services import create_geojson_polygon, get_from_cache, save_to_cache

router = APIRouter()

@router.post("/convert-to-polygon", response_model=GeoJSONResponse)
async def convert_to_polygon(
    request: CoordinatesRequest, db: AsyncSession = Depends(get_db)
):
    cached = await get_from_cache(db, request.latitude, request.longitude, request.radius)
    if cached:
        return cached

    geojson_feature = await create_geojson_polygon(
        request.latitude, request.longitude, request.radius
    )
    await save_to_cache(db, request.latitude, request.longitude, request.radius, geojson_feature)
    return geojson_feature
