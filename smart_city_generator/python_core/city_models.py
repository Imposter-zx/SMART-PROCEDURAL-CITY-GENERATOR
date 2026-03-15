try:
    from pydantic import BaseModel, Field
except ImportError:
    # Very basic fallback if pydantic is missing
    print("Warning: Pydantic not found. Using basic class fallback.")
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items(): setattr(self, k, v)
        def model_dump_json(self):
            import json
            def custom_serializer(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                return str(obj)
            return json.dumps(self, default=custom_serializer, indent=2)
    def Field(**kwargs): return kwargs.get("default")

from typing import List, Dict, Any

class CityParameters(BaseModel):
    city_type: str = "modern" # modern / medieval / cyberpunk / arabic / futuristic
    city_size: str = "medium" # small / medium / large
    building_density: float = 0.7
    number_of_parks: int = 5
    road_style: str = "grid" # grid / organic / radial / voronoi
    time_of_day: str = "day" # day / night

class Point2D(BaseModel):
    x: float
    y: float

class RoadSegment(BaseModel):
    start: Point2D
    end: Point2D
    width: float
    type: str # highway / local / alley

class BuildingLot(BaseModel):
    footprint: List[Point2D]
    zone: str # downtown / residential / commercial / industrial / park
    style_override: str = ""

class CityGeometry(BaseModel):
    roads: List[RoadSegment]
    lots: List[BuildingLot]
    parks: List[List[Point2D]]
