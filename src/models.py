from datetime import datetime

from sqlalchemy import Column, DateTime, Float, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GeoJSONCache(Base):
    __tablename__ = "geojson_cache"
    hash = Column(String, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius = Column(Float, nullable=False)
    result = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
