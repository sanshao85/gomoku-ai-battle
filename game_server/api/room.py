"""
房间相关API
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

from ..services.room_manager import RoomManager
from ..services.player_manager import PlayerManager
from ..models.room import RoomConfig, RoomStatus

router = APIRouter(prefix="/rooms", tags=["rooms"])

# 全局管理器实例（在实际应用中应该使用依赖注入）
room_manager = RoomManager()
player_manager = PlayerManager()


class CreateRoomRequest(BaseModel):
    name: str
    creator_id: str
    config: Optional[RoomConfig] = None


class JoinRoomRequest(BaseModel):
    player_id: str


class MakeMoveRequest(BaseModel):
    player_id: str
    x: int
    y: int


@router.post("/")
async def create_room(request: CreateRoomRequest):
    """创建房间"""
    try:
        # 确保玩家存在
        player_manager.get_or_create_player(request.creator_id)
        
        room = room_manager.create_room(
            creator_id=request.creator_id,
            name=request.name,
            config=request.config
        )
        
        # 创建者自动加入房间
        success, message = room_manager.join_room(room.room_id, request.creator_id)
        if success:
            player_manager.player_join_room(request.creator_id, room.room_id)
        
        return {
            "success": True,
            "message": "房间创建成功",
            "room": room.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_rooms(status: Optional[RoomStatus] = None):
    """获取房间列表"""
    try:
        rooms = room_manager.list_rooms(status)
        return {
            "success": True,
            "rooms": [room.get_room_info() for room in rooms],
            "total": len(rooms)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}")
async def get_room(room_id: str):
    """获取房间详情"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    return {
        "success": True,
        "room": room.to_dict()
    }


@router.post("/{room_id}/join")
async def join_room(room_id: str, request: JoinRoomRequest):
    """加入房间"""
    try:
        # 确保玩家存在
        player_manager.get_or_create_player(request.player_id)
        
        success, message = room_manager.join_room(room_id, request.player_id)
        
        if success:
            player_manager.player_join_room(request.player_id, room_id)
        
        return {
            "success": success,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{room_id}/leave")
async def leave_room(room_id: str, request: JoinRoomRequest):
    """离开房间"""
    try:
        success, message = room_manager.leave_room(room_id, request.player_id)
        
        if success:
            player_manager.player_leave_room(request.player_id)
        
        return {
            "success": success,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{room_id}/start")
async def start_game(room_id: str, request: JoinRoomRequest):
    """开始游戏"""
    try:
        success, message, game = room_manager.start_game(room_id, request.player_id)
        
        if success and game:
            # 更新玩家状态
            for player_id in game.players:
                player_manager.player_start_game(player_id, game.game_id)
        
        return {
            "success": success,
            "message": message,
            "game": game.to_dict() if game else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{room_id}/move")
async def make_move(room_id: str, request: MakeMoveRequest):
    """下棋"""
    try:
        success, message, result = room_manager.make_move(
            room_id, request.player_id, request.x, request.y
        )
        
        if success:
            player_manager.player_make_move(request.player_id)
            
            # 如果游戏结束，更新玩家统计
            if result:
                room = room_manager.get_room(room_id)
                if room and room.current_game:
                    game = room.current_game
                    for player_id in game.players:
                        won = (result.get("winner") == game.get_player_color(player_id).value)
                        draw = (result.get("winner") is None)
                        player_manager.player_finish_game(
                            player_id, won=won, draw=draw, 
                            moves=len(game.moves)
                        )
        
        return {
            "success": success,
            "message": message,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{room_id}/game")
async def get_game_state(room_id: str):
    """获取游戏状态"""
    game_state = room_manager.get_room_game_state(room_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="房间中没有进行中的游戏")
    
    return {
        "success": True,
        "game": game_state
    }


@router.post("/{room_id}/spectate")
async def join_spectate(room_id: str, request: JoinRoomRequest):
    """加入观战"""
    try:
        # 确保玩家存在
        player_manager.get_or_create_player(request.player_id)
        
        success, message = room_manager.add_spectator(room_id, request.player_id)
        
        return {
            "success": success,
            "message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{room_id}")
async def delete_room(room_id: str, creator_id: str):
    """删除房间（仅创建者可删除）"""
    room = room_manager.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    if room.creator != creator_id:
        raise HTTPException(status_code=403, detail="只有创建者可以删除房间")
    
    success = room_manager.delete_room(room_id)
    
    return {
        "success": success,
        "message": "房间删除成功" if success else "房间删除失败"
    }
