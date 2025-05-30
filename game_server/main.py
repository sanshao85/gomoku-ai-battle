"""
五子棋游戏服务端主应用
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .api import health, room, game


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时的初始化
    logger.info("启动五子棋游戏服务端...")
    logger.info(f"服务器配置: {settings.host}:{settings.port}")
    logger.info(f"调试模式: {settings.debug}")

    yield

    # 关闭时的清理
    logger.info("关闭五子棋游戏服务端...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.debug else "Internal server error"
        }
    )


# 挂载静态文件
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 注册路由
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(room.router, prefix=settings.api_prefix)
app.include_router(game.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """根路径 - 重定向到演示页面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/demo.html")

@app.get("/api")
async def api_info():
    """API信息"""
    return {
        "message": "五子棋游戏服务端API",
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "web_ui": "/static/index.html"
    }


@app.get("/info")
async def get_server_info():
    """获取服务器信息"""
    return {
        "title": settings.title,
        "version": settings.version,
        "description": settings.description,
        "api_prefix": settings.api_prefix,
        "board_size": settings.board_size,
        "win_length": settings.win_length,
        "max_rooms": settings.max_rooms,
        "max_players_per_room": settings.max_players_per_room
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "game_server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
