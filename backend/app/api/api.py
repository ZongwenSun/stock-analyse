from fastapi import APIRouter
from app.api.endpoints import stock

api_router = APIRouter()
api_router.include_router(stock.router, prefix="/stock", tags=["stock"]) 