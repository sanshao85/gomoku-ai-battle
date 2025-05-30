"""
健康检查API
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "gomoku-game-server"
    }


@router.get("/ping")
async def ping():
    """简单ping端点"""
    return {"message": "pong"}
