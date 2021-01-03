from fastapi import APIRouter

from api.endpoints import car

api_router = APIRouter()

api_router.include_router(car.router, prefix="/car", tags=["Car"])
