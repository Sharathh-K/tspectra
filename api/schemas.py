from datetime import date as Date
from typing import Literal

from pydantic import BaseModel


class RiskScene(BaseModel):
    date: Date
    field: str
    source: str
    crs: Literal["EPSG:4326"]
    source_crs: str
    width: int
    height: int
    band_count: int
    pixel_area_m2: float
    corners: list[tuple[float, float]]
    labels: list[Literal[0, 1]]
    image: str
