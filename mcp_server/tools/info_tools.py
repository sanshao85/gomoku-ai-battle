"""
信息查询相关的MCP工具
"""
import logging
from typing import Optional, Dict, Any, List

from .game_tools import api_client
from ..config import mcp_settings

logger = logging.getLogger(__name__)


async def get_board_state_resource(room_id: str) -> str:
    """
    获取棋盘状态资源
    
    Args:
        room_id: 房间ID
        
    Returns:
        str: 棋盘状态的文本描述
    """
    try:
        result = await api_client.get_game_state(room_id)
        if not result.get("success"):
            return f"获取游戏状态失败: {result.get('message', '未知错误')}"
        
        game = result.get("game", {})
        board = game.get("board", [])
        current_player = game.get("current_player", 1)
        status = game.get("status", "unknown")
        players = game.get("players", [])
        moves_count = game.get("moves_count", 0)
        last_move = game.get("last_move")
        
        # 构建棋盘显示
        board_text = "当前棋盘状态:\n"
        board_text += "   " + " ".join([f"{i:2d}" for i in range(15)]) + "\n"
        
        for y in range(15):
            row_text = f"{y:2d} "
            for x in range(15):
                cell = board[y][x] if y < len(board) and x < len(board[y]) else 0
                if cell == 0:
                    row_text += " ·"
                elif cell == 1:
                    row_text += " ●"  # 黑子
                elif cell == 2:
                    row_text += " ○"  # 白子
                else:
                    row_text += " ?"
            board_text += row_text + "\n"
        
        # 添加游戏信息
        info_text = f"\n游戏信息:\n"
        info_text += f"- 房间ID: {room_id}\n"
        info_text += f"- 游戏状态: {status}\n"
        info_text += f"- 玩家: {', '.join(players)}\n"
        info_text += f"- 当前轮到: {'黑子' if current_player == 1 else '白子'} (玩家{current_player})\n"
        info_text += f"- 已下步数: {moves_count}\n"
        
        if last_move:
            info_text += f"- 最后一步: ({last_move.get('x')}, {last_move.get('y')})\n"
        
        return board_text + info_text
        
    except Exception as e:
        logger.error(f"获取棋盘状态错误: {e}")
        return f"获取棋盘状态失败: {str(e)}"


async def get_game_info_resource(room_id: str) -> str:
    """
    获取游戏信息资源
    
    Args:
        room_id: 房间ID
        
    Returns:
        str: 游戏信息的文本描述
    """
    try:
        # 获取房间信息
        room_result = await api_client.get_room_info(room_id)
        if not room_result.get("success"):
            return f"获取房间信息失败: {room_result.get('message', '未知错误')}"
        
        room = room_result.get("room", {})
        
        info_text = f"房间 {room_id} 详细信息:\n\n"
        info_text += f"房间名称: {room.get('name', 'Unknown')}\n"
        info_text += f"房间状态: {room.get('status', 'unknown')}\n"
        info_text += f"创建者: {room.get('creator', 'Unknown')}\n"
        info_text += f"玩家列表: {', '.join(room.get('players', []))}\n"
        info_text += f"观战者: {', '.join(room.get('spectators', []))}\n"
        info_text += f"创建时间: {room.get('created_at', 'Unknown')}\n"
        
        # 如果有当前游戏，添加游戏信息
        current_game = room.get("current_game")
        if current_game:
            info_text += f"\n当前游戏信息:\n"
            info_text += f"游戏ID: {current_game.get('game_id', 'Unknown')}\n"
            info_text += f"游戏状态: {current_game.get('status', 'unknown')}\n"
            info_text += f"当前轮到: {'黑子' if current_game.get('current_player') == 1 else '白子'}\n"
            info_text += f"已下步数: {current_game.get('moves_count', 0)}\n"
            
            if current_game.get('started_at'):
                info_text += f"开始时间: {current_game.get('started_at')}\n"
            
            if current_game.get('result'):
                result = current_game.get('result')
                winner = result.get('winner')
                if winner is None:
                    info_text += f"游戏结果: 平局\n"
                elif winner == 1:
                    info_text += f"游戏结果: 黑子获胜\n"
                elif winner == 2:
                    info_text += f"游戏结果: 白子获胜\n"
                info_text += f"结束原因: {result.get('reason', 'Unknown')}\n"
        
        return info_text
        
    except Exception as e:
        logger.error(f"获取游戏信息错误: {e}")
        return f"获取游戏信息失败: {str(e)}"


async def get_room_list_resource() -> str:
    """
    获取房间列表资源
    
    Returns:
        str: 房间列表的文本描述
    """
    try:
        result = await api_client.list_rooms()
        if not result.get("success"):
            return f"获取房间列表失败: {result.get('message', '未知错误')}"
        
        rooms = result.get("rooms", [])
        total = result.get("total", 0)
        
        if total == 0:
            return "当前没有可用的房间"
        
        list_text = f"房间列表 (共 {total} 个房间):\n\n"
        
        for room in rooms:
            room_id = room.get("room_id", "Unknown")
            name = room.get("name", "Unknown")
            status = room.get("status", "unknown")
            player_count = room.get("player_count", 0)
            max_players = room.get("max_players", 2)
            creator = room.get("creator", "Unknown")
            
            list_text += f"房间ID: {room_id}\n"
            list_text += f"  名称: {name}\n"
            list_text += f"  状态: {status}\n"
            list_text += f"  玩家: {player_count}/{max_players}\n"
            list_text += f"  创建者: {creator}\n"
            list_text += f"  {'[房间已满]' if room.get('is_full') else '[可加入]'}\n\n"
        
        return list_text
        
    except Exception as e:
        logger.error(f"获取房间列表错误: {e}")
        return f"获取房间列表失败: {str(e)}"


async def get_player_info_resource(player_id: str) -> str:
    """
    获取玩家信息资源
    
    Args:
        player_id: 玩家ID
        
    Returns:
        str: 玩家信息的文本描述
    """
    try:
        result = await api_client.get_player_stats(player_id)
        if not result.get("success"):
            return f"获取玩家信息失败: {result.get('message', '未知错误')}"
        
        stats = result.get("stats", {})
        player_stats = stats.get("stats", {})
        
        info_text = f"玩家 {player_id} 信息:\n\n"
        info_text += f"玩家名称: {stats.get('name', 'Unknown')}\n"
        info_text += f"创建时间: {stats.get('created_at', 'Unknown')}\n"
        info_text += f"最后在线: {stats.get('last_seen', 'Unknown')}\n"
        
        if stats.get('last_move_time'):
            info_text += f"最后下棋: {stats.get('last_move_time')}\n"
        
        info_text += f"\n游戏统计:\n"
        info_text += f"总游戏数: {player_stats.get('games_played', 0)}\n"
        info_text += f"胜利数: {player_stats.get('games_won', 0)}\n"
        info_text += f"失败数: {player_stats.get('games_lost', 0)}\n"
        info_text += f"平局数: {player_stats.get('games_draw', 0)}\n"
        info_text += f"胜率: {player_stats.get('win_rate', 0):.2%}\n"
        info_text += f"败率: {player_stats.get('loss_rate', 0):.2%}\n"
        info_text += f"总下棋数: {player_stats.get('total_moves', 0)}\n"
        info_text += f"平均下棋时间: {player_stats.get('average_move_time', 0):.2f}秒\n"
        info_text += f"最长游戏: {player_stats.get('longest_game', 0)}步\n"
        
        if player_stats.get('shortest_win', 0) > 0:
            info_text += f"最短获胜: {player_stats.get('shortest_win')}步\n"
        
        return info_text
        
    except Exception as e:
        logger.error(f"获取玩家信息错误: {e}")
        return f"获取玩家信息失败: {str(e)}"


async def get_move_suggestions_tool(room_id: str, player_id: str, count: int = 5) -> str:
    """
    获取下棋建议工具
    
    Args:
        room_id: 房间ID
        player_id: 玩家ID
        count: 建议数量
        
    Returns:
        str: 下棋建议的文本描述
    """
    try:
        if count <= 0 or count > 10:
            return "建议数量应在1-10之间"
        
        result = await api_client.get_move_suggestions(room_id, player_id, count)
        if not result.get("success"):
            return f"获取下棋建议失败: {result.get('message', '未知错误')}"
        
        suggestions = result.get("suggestions", [])
        suggestion_count = result.get("count", 0)
        
        if suggestion_count == 0:
            return "当前没有可用的下棋建议"
        
        suggestion_text = f"为玩家 {player_id} 推荐的下棋位置 (共 {suggestion_count} 个):\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            x = suggestion.get("x")
            y = suggestion.get("y")
            suggestion_text += f"{i}. 位置 ({x}, {y})\n"
        
        suggestion_text += f"\n建议优先考虑位置 ({suggestions[0].get('x')}, {suggestions[0].get('y')})"
        
        return suggestion_text
        
    except Exception as e:
        logger.error(f"获取下棋建议错误: {e}")
        return f"获取下棋建议失败: {str(e)}"


async def get_leaderboard_tool(limit: int = 10, sort_by: str = "win_rate") -> str:
    """
    获取排行榜工具
    
    Args:
        limit: 返回数量限制
        sort_by: 排序字段
        
    Returns:
        str: 排行榜的文本描述
    """
    try:
        if limit <= 0 or limit > 50:
            return "排行榜数量应在1-50之间"
        
        valid_sort_fields = ["win_rate", "games_played", "games_won"]
        if sort_by not in valid_sort_fields:
            return f"无效的排序字段，支持的字段: {', '.join(valid_sort_fields)}"
        
        result = await api_client.get_leaderboard(limit, sort_by)
        if not result.get("success"):
            return f"获取排行榜失败: {result.get('message', '未知错误')}"
        
        leaderboard = result.get("leaderboard", [])
        total = result.get("total", 0)
        
        if total == 0:
            return "排行榜暂无数据"
        
        sort_name_map = {
            "win_rate": "胜率",
            "games_played": "游戏数",
            "games_won": "胜利数"
        }
        
        leaderboard_text = f"排行榜 (按{sort_name_map.get(sort_by, sort_by)}排序，共 {total} 名玩家):\n\n"
        
        for entry in leaderboard:
            rank = entry.get("rank", 0)
            name = entry.get("name", "Unknown")
            player_id = entry.get("player_id", "Unknown")
            win_rate = entry.get("win_rate", 0)
            games_played = entry.get("games_played", 0)
            games_won = entry.get("games_won", 0)
            games_lost = entry.get("games_lost", 0)
            
            leaderboard_text += f"{rank}. {name} ({player_id})\n"
            leaderboard_text += f"   胜率: {win_rate:.2%} | 游戏数: {games_played} | 胜/负: {games_won}/{games_lost}\n\n"
        
        return leaderboard_text
        
    except Exception as e:
        logger.error(f"获取排行榜错误: {e}")
        return f"获取排行榜失败: {str(e)}"
