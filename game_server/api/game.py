"""
游戏相关API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.room_manager import RoomManager
from ..services.player_manager import PlayerManager
from ..services.game_logic import GameLogic
from ..models.game import PlayerColor

router = APIRouter(prefix="/game", tags=["game"])

# 全局管理器实例
room_manager = RoomManager()
player_manager = PlayerManager()
game_logic = GameLogic()


class GetSuggestionsRequest(BaseModel):
    room_id: str
    player_id: str
    count: Optional[int] = 5


@router.get("/statistics")
async def get_statistics():
    """获取游戏统计信息"""
    try:
        room_stats = room_manager.get_statistics()
        player_stats = player_manager.get_statistics()
        
        return {
            "success": True,
            "statistics": {
                "rooms": room_stats,
                "players": player_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, sort_by: str = "win_rate"):
    """获取排行榜"""
    try:
        leaderboard = player_manager.get_leaderboard(limit=limit, sort_by=sort_by)
        
        return {
            "success": True,
            "leaderboard": leaderboard,
            "total": len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/players/{player_id}/stats")
async def get_player_stats(player_id: str):
    """获取玩家统计信息"""
    stats = player_manager.get_player_stats(player_id)
    if not stats:
        raise HTTPException(status_code=404, detail="玩家不存在")
    
    return {
        "success": True,
        "stats": stats
    }


@router.get("/players")
async def list_players(status: Optional[str] = None):
    """获取玩家列表"""
    try:
        from ..models.player import PlayerStatus
        
        player_status = None
        if status:
            try:
                player_status = PlayerStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail="无效的玩家状态")
        
        players = player_manager.list_players(status=player_status)
        
        return {
            "success": True,
            "players": [player.get_player_info() for player in players],
            "total": len(players)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/players/online")
async def get_online_players():
    """获取在线玩家列表"""
    try:
        players = player_manager.get_online_players()
        
        return {
            "success": True,
            "players": [player.get_player_info() for player in players],
            "total": len(players)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/players/available")
async def get_available_players():
    """获取可用玩家列表（可以加入游戏的玩家）"""
    try:
        players = player_manager.get_available_players()
        
        return {
            "success": True,
            "players": [player.get_player_info() for player in players],
            "total": len(players)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions")
async def get_move_suggestions(request: GetSuggestionsRequest):
    """获取下棋建议"""
    try:
        room = room_manager.get_room(request.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        if not room.current_game:
            raise HTTPException(status_code=400, detail="房间中没有进行中的游戏")
        
        game = room.current_game
        player_color = game.get_player_color(request.player_id)
        if not player_color:
            raise HTTPException(status_code=400, detail="玩家不在此游戏中")
        
        suggestions = game_logic.get_suggested_moves(
            game.board, player_color, request.count
        )
        
        return {
            "success": True,
            "suggestions": [{"x": x, "y": y} for x, y in suggestions],
            "count": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/valid-moves")
async def get_valid_moves(room_id: str):
    """获取有效下棋位置"""
    try:
        room = room_manager.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        if not room.current_game:
            raise HTTPException(status_code=400, detail="房间中没有进行中的游戏")
        
        valid_moves = game_logic.get_valid_moves(room.current_game.board)
        
        return {
            "success": True,
            "valid_moves": [{"x": x, "y": y} for x, y in valid_moves],
            "count": len(valid_moves)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/evaluate")
async def evaluate_position(room_id: str, player_id: str):
    """评估当前局面"""
    try:
        room = room_manager.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        if not room.current_game:
            raise HTTPException(status_code=400, detail="房间中没有进行中的游戏")
        
        game = room.current_game
        player_color = game.get_player_color(player_id)
        if not player_color:
            raise HTTPException(status_code=400, detail="玩家不在此游戏中")
        
        score = game_logic.evaluate_position(game.board, player_color)
        
        return {
            "success": True,
            "evaluation": {
                "score": score,
                "player_color": player_color.value,
                "advantage": "优势" if score > 0 else "劣势" if score < 0 else "均势"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_resources():
    """清理资源（管理员功能）"""
    try:
        room_manager.cleanup_empty_rooms()
        player_manager.cleanup_inactive_players()
        
        return {
            "success": True,
            "message": "资源清理完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/history")
async def get_game_history(room_id: str):
    """获取房间游戏历史"""
    try:
        room = room_manager.get_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="房间不存在")
        
        return {
            "success": True,
            "history": {
                "room_id": room.room_id,
                "game_count": len(room.game_history),
                "game_ids": room.game_history,
                "current_game_id": room.current_game.game_id if room.current_game else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
