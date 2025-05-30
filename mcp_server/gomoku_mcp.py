#!/usr/bin/env python3
"""
五子棋游戏MCP服务器
"""
import logging
import asyncio
from mcp.server.fastmcp import FastMCP

from .config import mcp_settings
from .tools.game_tools import (
    create_room_tool,
    join_room_tool,
    leave_room_tool,
    make_move_tool,
    start_game_tool
)
from .tools.info_tools import (
    get_board_state_resource,
    get_game_info_resource,
    get_room_list_resource,
    get_player_info_resource,
    get_move_suggestions_tool,
    get_leaderboard_tool
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, mcp_settings.log_level.upper()),
    format=mcp_settings.log_format
)
logger = logging.getLogger(__name__)

# 创建MCP服务器
mcp = FastMCP(
    name=mcp_settings.server_name,
    dependencies=["httpx", "pydantic-settings"]
)


# ==================== 游戏操作工具 ====================

@mcp.tool()
async def create_room(creator_id: str, room_name: str) -> str:
    """
    创建游戏房间

    Args:
        creator_id: 创建者ID（AI的唯一标识）
        room_name: 房间名称
    """
    logger.info(f"创建房间: {room_name}, 创建者: {creator_id}")
    return await create_room_tool(creator_id, room_name)


@mcp.tool()
async def join_room(room_id: str, player_id: str) -> str:
    """
    加入游戏房间

    Args:
        room_id: 房间ID
        player_id: 玩家ID（AI的唯一标识）
    """
    logger.info(f"玩家 {player_id} 加入房间 {room_id}")
    return await join_room_tool(room_id, player_id)


@mcp.tool()
async def leave_room(room_id: str, player_id: str) -> str:
    """
    离开游戏房间

    Args:
        room_id: 房间ID
        player_id: 玩家ID（AI的唯一标识）
    """
    logger.info(f"玩家 {player_id} 离开房间 {room_id}")
    return await leave_room_tool(room_id, player_id)


@mcp.tool()
async def start_game(room_id: str, player_id: str) -> str:
    """
    开始游戏（需要房间内有2名玩家）

    Args:
        room_id: 房间ID
        player_id: 发起者ID
    """
    logger.info(f"玩家 {player_id} 在房间 {room_id} 开始游戏")
    return await start_game_tool(room_id, player_id)


@mcp.tool()
async def make_move(room_id: str, player_id: str, x: int, y: int) -> str:
    """
    在指定位置下棋

    Args:
        room_id: 房间ID
        player_id: 玩家ID（AI的唯一标识）
        x: X坐标（0-14，从左到右）
        y: Y坐标（0-14，从上到下）
    """
    logger.info(f"玩家 {player_id} 在房间 {room_id} 下棋: ({x}, {y})")
    return await make_move_tool(room_id, player_id, x, y)


@mcp.tool()
async def get_move_suggestions(room_id: str, player_id: str, count: int = 5) -> str:
    """
    获取AI推荐的下棋位置

    Args:
        room_id: 房间ID
        player_id: 玩家ID
        count: 建议数量（1-10）
    """
    logger.info(f"为玩家 {player_id} 获取 {count} 个下棋建议")
    return await get_move_suggestions_tool(room_id, player_id, count)


# ==================== 信息查询资源 ====================

@mcp.resource("board_state://{room_id}")
async def board_state(room_id: str) -> str:
    """
    获取指定房间的棋盘状态

    Args:
        room_id: 房间ID
    """
    logger.info(f"获取房间 {room_id} 的棋盘状态")
    return await get_board_state_resource(room_id)


@mcp.resource("game_info://{room_id}")
async def game_info(room_id: str) -> str:
    """
    获取指定房间的游戏信息

    Args:
        room_id: 房间ID
    """
    logger.info(f"获取房间 {room_id} 的游戏信息")
    return await get_game_info_resource(room_id)


@mcp.resource("gomoku://room_list")
async def room_list() -> str:
    """获取所有可用房间列表"""
    logger.info("获取房间列表")
    return await get_room_list_resource()


@mcp.resource("player_info://{player_id}")
async def player_info(player_id: str) -> str:
    """
    获取指定玩家的信息和统计数据

    Args:
        player_id: 玩家ID
    """
    logger.info(f"获取玩家 {player_id} 的信息")
    return await get_player_info_resource(player_id)


# ==================== 其他工具 ====================

@mcp.tool()
async def get_leaderboard(limit: int = 10, sort_by: str = "win_rate") -> str:
    """
    获取玩家排行榜

    Args:
        limit: 返回数量限制（1-50）
        sort_by: 排序字段（win_rate/games_played/games_won）
    """
    logger.info(f"获取排行榜: 限制 {limit}, 排序 {sort_by}")
    return await get_leaderboard_tool(limit, sort_by)


@mcp.tool()
async def wait_for_turn(room_id: str, player_id: str, wait_seconds: int = 20) -> str:
    """
    等待指定时间后检查是否轮到自己下棋

    Args:
        room_id: 房间ID
        player_id: 玩家ID
        wait_seconds: 等待时间（秒），默认20秒
    """
    import asyncio

    logger.info(f"玩家 {player_id} 等待 {wait_seconds} 秒后检查轮次")

    # 等待指定时间
    await asyncio.sleep(wait_seconds)

    # 检查是否轮到自己
    try:
        from .tools.info_tools import get_board_state_resource
        board_state = await get_board_state_resource(room_id)

        # 简单解析当前玩家
        if "当前轮到: 黑子" in board_state:
            current_player = "黑子"
        elif "当前轮到: 白子" in board_state:
            current_player = "白子"
        else:
            current_player = "未知"

        # 检查游戏状态
        if "游戏结束" in board_state or "获胜" in board_state or "平局" in board_state:
            return f"等待 {wait_seconds} 秒后检查：游戏已结束"

        return f"等待 {wait_seconds} 秒后检查：当前轮到 {current_player}，请查看棋盘状态决定是否下棋"

    except Exception as e:
        logger.error(f"等待检查失败: {e}")
        return f"等待 {wait_seconds} 秒后检查失败: {str(e)}"


@mcp.tool()
async def check_my_turn(room_id: str, player_id: str) -> str:
    """
    检查是否轮到自己下棋

    Args:
        room_id: 房间ID
        player_id: 玩家ID
    """
    try:
        from .tools.info_tools import get_board_state_resource
        board_state = await get_board_state_resource(room_id)

        # 解析当前玩家和游戏状态
        if "游戏结束" in board_state or "获胜" in board_state or "平局" in board_state:
            return "游戏已结束，无需下棋"

        if "当前轮到: 黑子" in board_state:
            current_player = "黑子"
        elif "当前轮到: 白子" in board_state:
            current_player = "白子"
        else:
            return "无法确定当前轮到谁，请查看游戏状态"

        # 简单判断逻辑（可以根据实际需要改进）
        # 这里假设玩家ID包含数字，1是黑子，2是白子
        if player_id.endswith("1") or "AI_1" in player_id:
            my_color = "黑子"
        else:
            my_color = "白子"

        if current_player == my_color:
            return f"是的，现在轮到您下棋！您是{my_color}，请选择位置下棋。"
        else:
            return f"还没轮到您，当前轮到{current_player}，您是{my_color}。建议等待20秒后再检查。"

    except Exception as e:
        logger.error(f"检查轮次失败: {e}")
        return f"检查轮次失败: {str(e)}"


@mcp.tool()
async def get_remaining_time(room_id: str, player_id: str) -> str:
    """
    获取当前玩家剩余下棋时间

    Args:
        room_id: 房间ID
        player_id: 玩家ID
    """
    try:
        from .tools.game_tools import api_client

        # 获取游戏状态
        result = await api_client.get_game_state(room_id)
        if not result.get("success"):
            return f"获取游戏状态失败: {result.get('message', '未知错误')}"

        game = result.get("game", {})

        # 检查游戏状态
        if game.get("status") != "playing":
            return "游戏未在进行中，无需计时"

        # 简单计算剩余时间（这里需要根据实际API返回的数据调整）
        # 每步2分钟(120秒)限制
        move_timeout = 120

        # 获取最后下棋时间
        last_move_time = game.get("last_move_time")
        if last_move_time:
            from datetime import datetime
            import dateutil.parser

            last_time = dateutil.parser.parse(last_move_time)
            elapsed = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds()
            remaining = max(0, move_timeout - elapsed)
        else:
            # 如果没有下过棋，从游戏开始时间算
            started_at = game.get("started_at")
            if started_at:
                start_time = dateutil.parser.parse(started_at)
                elapsed = (datetime.now() - start_time.replace(tzinfo=None)).total_seconds()
                remaining = max(0, move_timeout - elapsed)
            else:
                remaining = move_timeout

        remaining_int = int(remaining)

        if remaining_int <= 0:
            return f"⚠️ 时间已到！当前玩家应该立即下棋，否则系统将自动下棋"
        elif remaining_int <= 10:
            return f"⏰ 紧急！剩余时间: {remaining_int} 秒，请立即下棋！"
        elif remaining_int <= 30:
            return f"⏳ 注意！剩余时间: {remaining_int} 秒，请尽快下棋"
        else:
            return f"⏱️ 剩余时间: {remaining_int} 秒"

    except Exception as e:
        logger.error(f"获取剩余时间失败: {e}")
        return f"获取剩余时间失败: {str(e)}"


@mcp.tool()
async def get_server_status() -> str:
    """获取MCP服务器状态信息"""
    return f"""MCP服务器状态:
- 服务器名称: {mcp_settings.server_name}
- 版本: {mcp_settings.server_version}
- 描述: {mcp_settings.server_description}
- 游戏服务器: {mcp_settings.game_server_url}
- 连接超时: {mcp_settings.timeout}秒
- 最大重试: {mcp_settings.max_retries}次
- 调试模式: {mcp_settings.debug}
- 日志级别: {mcp_settings.log_level}

可用工具:
- create_room: 创建游戏房间
- join_room: 加入游戏房间
- leave_room: 离开游戏房间
- start_game: 开始游戏
- make_move: 下棋
- get_move_suggestions: 获取下棋建议
- get_leaderboard: 获取排行榜
- get_server_status: 获取服务器状态

可用资源:
- board_state://{{room_id}}: 获取棋盘状态
- game_info://{{room_id}}: 获取游戏信息
- gomoku://room_list: 获取房间列表
- player_info://{{player_id}}: 获取玩家信息
"""


def main():
    """主函数"""
    logger.info(f"启动 {mcp_settings.server_name} v{mcp_settings.server_version}")
    logger.info(f"连接到游戏服务器: {mcp_settings.game_server_url}")

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP服务器已停止")
    except Exception as e:
        logger.error(f"MCP服务器错误: {e}")
        raise


if __name__ == "__main__":
    main()
