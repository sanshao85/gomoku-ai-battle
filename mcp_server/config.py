"""
MCP服务器配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class MCPSettings(BaseSettings):
    """MCP服务器配置"""
    
    # MCP服务器配置
    server_name: str = "gomoku-mcp-server"
    server_version: str = "1.0.0"
    server_description: str = "五子棋游戏MCP服务器"
    
    # 游戏服务端连接配置
    game_server_url: str = "http://localhost:8000"
    game_server_api_prefix: str = "/api/v1"
    
    # 连接配置
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 玩家配置
    default_player_name_prefix: str = "AI_Player"
    auto_create_player: bool = True
    
    # 游戏配置
    max_suggestions: int = 5
    enable_game_analysis: bool = True
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 调试配置
    debug: bool = False
    verbose: bool = False
    
    class Config:
        env_file = ".env"
        env_prefix = "MCP_"


# 全局配置实例
mcp_settings = MCPSettings()
