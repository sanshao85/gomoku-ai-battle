"""
游戏服务端配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # API配置
    api_prefix: str = "/api/v1"
    title: str = "Gomoku Game Server"
    description: str = "五子棋游戏服务端API"
    version: str = "1.0.0"
    
    # CORS配置
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # 游戏配置
    board_size: int = 15
    win_length: int = 5
    max_rooms: int = 100
    max_players_per_room: int = 2
    room_cleanup_interval: int = 3600  # 秒
    player_cleanup_interval: int = 86400  # 秒
    
    # 安全配置
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # 数据库配置（如果需要）
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 监控配置
    enable_metrics: bool = False
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        env_prefix = "GOMOKU_"


# 全局配置实例
settings = Settings()
