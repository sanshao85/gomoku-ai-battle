"""
游戏操作相关的MCP工具
"""
import httpx
import logging
from typing import Optional, Dict, Any

from ..config import mcp_settings

logger = logging.getLogger(__name__)


class GameAPIClient:
    """游戏服务端API客户端"""

    def __init__(self):
        self.base_url = mcp_settings.game_server_url + mcp_settings.game_server_api_prefix
        self.timeout = mcp_settings.timeout
        self.max_retries = mcp_settings.max_retries
        self.retry_delay = mcp_settings.retry_delay

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, follow_redirects=True, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logger.error(f"请求失败: {e}")
                raise Exception(f"连接游戏服务器失败: {e}")
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
                error_detail = e.response.json().get("detail", str(e)) if e.response.headers.get("content-type", "").startswith("application/json") else str(e)
                raise Exception(f"游戏服务器错误: {error_detail}")

    async def create_room(self, creator_id: str, room_name: str) -> Dict[str, Any]:
        """创建房间"""
        data = {
            "name": room_name,
            "creator_id": creator_id
        }
        return await self._make_request("POST", "/rooms/", json=data)

    async def join_room(self, room_id: str, player_id: str) -> Dict[str, Any]:
        """加入房间"""
        data = {"player_id": player_id}
        return await self._make_request("POST", f"/rooms/{room_id}/join", json=data)

    async def leave_room(self, room_id: str, player_id: str) -> Dict[str, Any]:
        """离开房间"""
        data = {"player_id": player_id}
        return await self._make_request("POST", f"/rooms/{room_id}/leave", json=data)

    async def start_game(self, room_id: str, player_id: str) -> Dict[str, Any]:
        """开始游戏"""
        data = {"player_id": player_id}
        return await self._make_request("POST", f"/rooms/{room_id}/start", json=data)

    async def make_move(self, room_id: str, player_id: str, x: int, y: int) -> Dict[str, Any]:
        """下棋"""
        data = {
            "player_id": player_id,
            "x": x,
            "y": y
        }
        return await self._make_request("POST", f"/rooms/{room_id}/move", json=data)

    async def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """获取房间信息"""
        return await self._make_request("GET", f"/rooms/{room_id}")

    async def get_game_state(self, room_id: str) -> Dict[str, Any]:
        """获取游戏状态"""
        return await self._make_request("GET", f"/rooms/{room_id}/game")

    async def list_rooms(self, status: Optional[str] = None) -> Dict[str, Any]:
        """获取房间列表"""
        params = {"status": status} if status else {}
        return await self._make_request("GET", "/rooms/", params=params)

    async def get_move_suggestions(self, room_id: str, player_id: str, count: int = 5) -> Dict[str, Any]:
        """获取下棋建议"""
        data = {
            "room_id": room_id,
            "player_id": player_id,
            "count": count
        }
        return await self._make_request("POST", "/game/suggestions", json=data)

    async def get_valid_moves(self, room_id: str) -> Dict[str, Any]:
        """获取有效下棋位置"""
        return await self._make_request("GET", f"/game/rooms/{room_id}/valid-moves")

    async def evaluate_position(self, room_id: str, player_id: str) -> Dict[str, Any]:
        """评估当前局面"""
        params = {"player_id": player_id}
        return await self._make_request("GET", f"/game/rooms/{room_id}/evaluate", params=params)

    async def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """获取玩家统计"""
        return await self._make_request("GET", f"/game/players/{player_id}/stats")

    async def get_leaderboard(self, limit: int = 10, sort_by: str = "win_rate") -> Dict[str, Any]:
        """获取排行榜"""
        params = {"limit": limit, "sort_by": sort_by}
        return await self._make_request("GET", "/game/leaderboard", params=params)


# 全局API客户端实例
api_client = GameAPIClient()


async def create_room_tool(creator_id: str, room_name: str) -> str:
    """
    创建游戏房间

    Args:
        creator_id: 创建者ID
        room_name: 房间名称

    Returns:
        str: 操作结果描述
    """
    try:
        result = await api_client.create_room(creator_id, room_name)
        if result.get("success"):
            room = result.get("room", {})
            room_id = room.get("room_id")
            return f"成功创建房间 '{room_name}'，房间ID: {room_id}"
        else:
            return f"创建房间失败: {result.get('message', '未知错误')}"
    except Exception as e:
        logger.error(f"创建房间工具错误: {e}")
        return f"创建房间失败: {str(e)}"


async def join_room_tool(room_id: str, player_id: str) -> str:
    """
    加入游戏房间

    Args:
        room_id: 房间ID
        player_id: 玩家ID

    Returns:
        str: 操作结果描述
    """
    try:
        result = await api_client.join_room(room_id, player_id)
        if result.get("success"):
            return f"成功加入房间 {room_id}"
        else:
            return f"加入房间失败: {result.get('message', '未知错误')}"
    except Exception as e:
        logger.error(f"加入房间工具错误: {e}")
        return f"加入房间失败: {str(e)}"


async def leave_room_tool(room_id: str, player_id: str) -> str:
    """
    离开游戏房间

    Args:
        room_id: 房间ID
        player_id: 玩家ID

    Returns:
        str: 操作结果描述
    """
    try:
        result = await api_client.leave_room(room_id, player_id)
        if result.get("success"):
            return f"成功离开房间 {room_id}"
        else:
            return f"离开房间失败: {result.get('message', '未知错误')}"
    except Exception as e:
        logger.error(f"离开房间工具错误: {e}")
        return f"离开房间失败: {str(e)}"


async def make_move_tool(room_id: str, player_id: str, x: int, y: int) -> str:
    """
    在指定位置下棋

    Args:
        room_id: 房间ID
        player_id: 玩家ID
        x: X坐标 (0-14)
        y: Y坐标 (0-14)

    Returns:
        str: 下棋结果描述
    """
    try:
        # 验证坐标范围
        if not (0 <= x <= 14 and 0 <= y <= 14):
            return f"无效的坐标: ({x}, {y})，坐标范围应为 0-14"

        result = await api_client.make_move(room_id, player_id, x, y)
        if result.get("success"):
            message = result.get("message", "下棋成功")
            game_result = result.get("result")

            if game_result:
                winner = game_result.get("winner")
                if winner is None:
                    return f"{message}，游戏平局！"
                elif winner == 1:
                    return f"{message}，黑子获胜！"
                elif winner == 2:
                    return f"{message}，白子获胜！"
                else:
                    return f"{message}，游戏结束"
            else:
                return message
        else:
            return f"下棋失败: {result.get('message', '未知错误')}"
    except Exception as e:
        logger.error(f"下棋工具错误: {e}")
        return f"下棋失败: {str(e)}"


async def start_game_tool(room_id: str, player_id: str) -> str:
    """
    开始游戏

    Args:
        room_id: 房间ID
        player_id: 玩家ID

    Returns:
        str: 操作结果描述
    """
    try:
        result = await api_client.start_game(room_id, player_id)
        if result.get("success"):
            return f"游戏开始！房间 {room_id} 中的游戏已启动"
        else:
            return f"开始游戏失败: {result.get('message', '未知错误')}"
    except Exception as e:
        logger.error(f"开始游戏工具错误: {e}")
        return f"开始游戏失败: {str(e)}"
