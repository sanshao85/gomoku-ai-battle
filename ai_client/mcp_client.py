"""
MCP客户端封装
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class GomokuMCPClient:
    """五子棋MCP客户端"""

    def __init__(self, mcp_server_script: str = "scripts/start_mcp_server.py"):
        """
        初始化MCP客户端

        Args:
            mcp_server_script: MCP服务器启动脚本路径
        """
        self.mcp_server_script = mcp_server_script
        self.session: Optional[ClientSession] = None
        self.server_params = StdioServerParameters(
            command="python",
            args=[mcp_server_script]
        )

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()

    async def connect(self):
        """连接到MCP服务器"""
        try:
            logger.info("连接到MCP服务器...")
            self.stdio_client = stdio_client(self.server_params)
            self.read_stream, self.write_stream = await self.stdio_client.__aenter__()

            self.session = ClientSession(self.read_stream, self.write_stream)
            await self.session.__aenter__()

            # 初始化连接
            await self.session.initialize()
            logger.info("MCP客户端连接成功")

        except Exception as e:
            logger.error(f"连接MCP服务器失败: {e}")
            raise

    async def disconnect(self):
        """断开MCP服务器连接"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None

            if hasattr(self, 'stdio_client'):
                await self.stdio_client.__aexit__(None, None, None)

            logger.info("MCP客户端已断开连接")
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        调用MCP工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            str: 工具执行结果
        """
        if not self.session:
            raise RuntimeError("MCP客户端未连接")

        try:
            logger.debug(f"调用工具: {tool_name}, 参数: {arguments}")
            result = await self.session.call_tool(tool_name, arguments)

            # 提取工具结果内容
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and len(result.content) > 0:
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        return content_item.text
                    elif hasattr(content_item, 'content'):
                        return str(content_item.content)
                return str(result.content)

            return str(result)

        except Exception as e:
            logger.error(f"调用工具 {tool_name} 失败: {e}")
            raise

    async def read_resource(self, resource_uri: str) -> str:
        """
        读取MCP资源

        Args:
            resource_uri: 资源URI

        Returns:
            str: 资源内容
        """
        if not self.session:
            raise RuntimeError("MCP客户端未连接")

        try:
            logger.debug(f"读取资源: {resource_uri}")
            content, mime_type = await self.session.read_resource(resource_uri)
            return content

        except Exception as e:
            logger.error(f"读取资源 {resource_uri} 失败: {e}")
            raise

    # ==================== 游戏操作方法 ====================

    async def create_room(self, creator_id: str, room_name: str) -> str:
        """创建房间"""
        return await self.call_tool("create_room", {
            "creator_id": creator_id,
            "room_name": room_name
        })

    async def join_room(self, room_id: str, player_id: str) -> str:
        """加入房间"""
        return await self.call_tool("join_room", {
            "room_id": room_id,
            "player_id": player_id
        })

    async def leave_room(self, room_id: str, player_id: str) -> str:
        """离开房间"""
        return await self.call_tool("leave_room", {
            "room_id": room_id,
            "player_id": player_id
        })

    async def start_game(self, room_id: str, player_id: str) -> str:
        """开始游戏"""
        return await self.call_tool("start_game", {
            "room_id": room_id,
            "player_id": player_id
        })

    async def make_move(self, room_id: str, player_id: str, x: int, y: int) -> str:
        """下棋"""
        return await self.call_tool("make_move", {
            "room_id": room_id,
            "player_id": player_id,
            "x": x,
            "y": y
        })

    async def get_move_suggestions(self, room_id: str, player_id: str, count: int = 5) -> str:
        """获取下棋建议"""
        return await self.call_tool("get_move_suggestions", {
            "room_id": room_id,
            "player_id": player_id,
            "count": count
        })

    async def get_leaderboard(self, limit: int = 10, sort_by: str = "win_rate") -> str:
        """获取排行榜"""
        return await self.call_tool("get_leaderboard", {
            "limit": limit,
            "sort_by": sort_by
        })

    async def get_server_status(self) -> str:
        """获取服务器状态"""
        return await self.call_tool("get_server_status", {})

    # ==================== 信息查询方法 ====================

    async def get_board_state(self, room_id: str) -> str:
        """获取棋盘状态"""
        return await self.read_resource(f"board_state://{room_id}")

    async def get_game_info(self, room_id: str) -> str:
        """获取游戏信息"""
        return await self.read_resource(f"game_info://{room_id}")

    async def get_room_list(self) -> str:
        """获取房间列表"""
        return await self.read_resource("gomoku://room_list")

    async def get_player_info(self, player_id: str) -> str:
        """获取玩家信息"""
        return await self.read_resource(f"player_info://{player_id}")

    # ==================== 便捷方法 ====================

    async def list_available_tools(self) -> List[str]:
        """列出可用工具"""
        if not self.session:
            raise RuntimeError("MCP客户端未连接")

        try:
            tools = await self.session.list_tools()
            return [tool.name for tool in tools.tools] if tools.tools else []
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            return []

    async def list_available_resources(self) -> List[str]:
        """列出可用资源"""
        if not self.session:
            raise RuntimeError("MCP客户端未连接")

        try:
            resources = await self.session.list_resources()
            return [resource.uri for resource in resources.resources] if resources.resources else []
        except Exception as e:
            logger.error(f"获取资源列表失败: {e}")
            return []
