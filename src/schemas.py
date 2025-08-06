from pydantic import BaseModel, field_validator


class CoordinatesRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, val):
        if not -90 <= val <= 90:
            raise ValueError("Широта должна быть в диапазоне от -90 до 90")
        return val

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, val):
        if not -180 <= val <= 180:
            raise ValueError("Долгота должна быть в диапазоне от -180 до 180")
        return val

    @field_validator("radius")
    @classmethod
    def validate_radius(cls, val):
        if val <= 0:
            raise ValueError("Радиус должен быть положительным числом")
        return val



class GeoJSONGeometry(BaseModel):
    type: str  
    coordinates: list[list[list[float]]]

class GeoJSONResponse(BaseModel):
    type: str  
    geometry: GeoJSONGeometry
    properties: dict
