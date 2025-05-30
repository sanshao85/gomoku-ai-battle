"""
MCP服务器测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from mcp_server.tools.game_tools import GameAPIClient
from mcp_server.tools.info_tools import (
    get_board_state_resource,
    get_game_info_resource,
    get_room_list_resource
)


class TestGameAPIClient:
    """游戏API客户端测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.client = GameAPIClient()
    
    @pytest.mark.asyncio
    async def test_create_room(self):
        """测试创建房间"""
        mock_response = {
            "success": True,
            "message": "房间创建成功",
            "room": {
                "room_id": "room_12345",
                "name": "测试房间",
                "creator": "test_player"
            }
        }
        
        with patch.object(self.client, '_make_request', return_value=mock_response) as mock_request:
            result = await self.client.create_room("test_player", "测试房间")
            
            mock_request.assert_called_once_with(
                "POST", "/rooms", 
                json={"name": "测试房间", "creator_id": "test_player"}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_join_room(self):
        """测试加入房间"""
        mock_response = {
            "success": True,
            "message": "成功加入房间"
        }
        
        with patch.object(self.client, '_make_request', return_value=mock_response) as mock_request:
            result = await self.client.join_room("room_12345", "test_player")
            
            mock_request.assert_called_once_with(
                "POST", "/rooms/room_12345/join",
                json={"player_id": "test_player"}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_make_move(self):
        """测试下棋"""
        mock_response = {
            "success": True,
            "message": "下棋成功",
            "result": None
        }
        
        with patch.object(self.client, '_make_request', return_value=mock_response) as mock_request:
            result = await self.client.make_move("room_12345", "test_player", 7, 7)
            
            mock_request.assert_called_once_with(
                "POST", "/rooms/room_12345/move",
                json={"player_id": "test_player", "x": 7, "y": 7}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_get_game_state(self):
        """测试获取游戏状态"""
        mock_response = {
            "success": True,
            "game": {
                "game_id": "game_123",
                "board": [[0 for _ in range(15)] for _ in range(15)],
                "current_player": 1,
                "status": "playing",
                "players": ["player1", "player2"],
                "moves_count": 0
            }
        }
        
        with patch.object(self.client, '_make_request', return_value=mock_response) as mock_request:
            result = await self.client.get_game_state("room_12345")
            
            mock_request.assert_called_once_with("GET", "/rooms/room_12345/game")
            assert result == mock_response


class TestInfoTools:
    """信息工具测试类"""
    
    @pytest.mark.asyncio
    async def test_get_board_state_resource(self):
        """测试获取棋盘状态资源"""
        mock_game_state = {
            "success": True,
            "game": {
                "board": [[0 for _ in range(15)] for _ in range(15)],
                "current_player": 1,
                "status": "playing",
                "players": ["player1", "player2"],
                "moves_count": 0,
                "last_move": {"x": 7, "y": 7}
            }
        }
        
        # 在棋盘上放置一些棋子
        mock_game_state["game"]["board"][7][7] = 1  # 黑子
        mock_game_state["game"]["board"][7][8] = 2  # 白子
        
        with patch('mcp_server.tools.info_tools.api_client.get_game_state', 
                  return_value=mock_game_state) as mock_api:
            result = await get_board_state_resource("room_12345")
            
            mock_api.assert_called_once_with("room_12345")
            assert "当前棋盘状态:" in result
            assert "●" in result  # 黑子符号
            assert "○" in result  # 白子符号
            assert "房间ID: room_12345" in result
            assert "当前轮到: 黑子" in result
    
    @pytest.mark.asyncio
    async def test_get_game_info_resource(self):
        """测试获取游戏信息资源"""
        mock_room_info = {
            "success": True,
            "room": {
                "room_id": "room_12345",
                "name": "测试房间",
                "status": "playing",
                "creator": "player1",
                "players": ["player1", "player2"],
                "spectators": [],
                "created_at": "2024-01-01T00:00:00Z",
                "current_game": {
                    "game_id": "game_123",
                    "status": "playing",
                    "current_player": 1,
                    "moves_count": 5,
                    "started_at": "2024-01-01T00:05:00Z"
                }
            }
        }
        
        with patch('mcp_server.tools.info_tools.api_client.get_room_info', 
                  return_value=mock_room_info) as mock_api:
            result = await get_game_info_resource("room_12345")
            
            mock_api.assert_called_once_with("room_12345")
            assert "房间 room_12345 详细信息:" in result
            assert "房间名称: 测试房间" in result
            assert "房间状态: playing" in result
            assert "当前游戏信息:" in result
            assert "已下步数: 5" in result
    
    @pytest.mark.asyncio
    async def test_get_room_list_resource(self):
        """测试获取房间列表资源"""
        mock_room_list = {
            "success": True,
            "rooms": [
                {
                    "room_id": "room_1",
                    "name": "房间1",
                    "status": "waiting",
                    "player_count": 1,
                    "max_players": 2,
                    "creator": "player1",
                    "is_full": False
                },
                {
                    "room_id": "room_2",
                    "name": "房间2",
                    "status": "playing",
                    "player_count": 2,
                    "max_players": 2,
                    "creator": "player2",
                    "is_full": True
                }
            ],
            "total": 2
        }
        
        with patch('mcp_server.tools.info_tools.api_client.list_rooms', 
                  return_value=mock_room_list) as mock_api:
            result = await get_room_list_resource()
            
            mock_api.assert_called_once()
            assert "房间列表 (共 2 个房间):" in result
            assert "房间ID: room_1" in result
            assert "房间ID: room_2" in result
            assert "[可加入]" in result
            assert "[房间已满]" in result
    
    @pytest.mark.asyncio
    async def test_get_board_state_resource_error(self):
        """测试获取棋盘状态资源错误情况"""
        mock_error_response = {
            "success": False,
            "message": "房间不存在"
        }
        
        with patch('mcp_server.tools.info_tools.api_client.get_game_state', 
                  return_value=mock_error_response) as mock_api:
            result = await get_board_state_resource("invalid_room")
            
            mock_api.assert_called_once_with("invalid_room")
            assert "获取游戏状态失败: 房间不存在" in result
    
    @pytest.mark.asyncio
    async def test_get_room_list_resource_empty(self):
        """测试获取空房间列表"""
        mock_empty_list = {
            "success": True,
            "rooms": [],
            "total": 0
        }
        
        with patch('mcp_server.tools.info_tools.api_client.list_rooms', 
                  return_value=mock_empty_list) as mock_api:
            result = await get_room_list_resource()
            
            mock_api.assert_called_once()
            assert "当前没有可用的房间" in result
