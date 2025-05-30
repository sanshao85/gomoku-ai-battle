"""
房间管理服务
"""
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from ..models.room import Room, RoomStatus, RoomConfig
from ..models.game import Game
from .game_logic import GameLogic


class RoomManager:
    """房间管理器"""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.game_logic = GameLogic()
        self.cleanup_interval = timedelta(hours=1)  # 清理间隔

    def create_room(self, creator_id: str, name: str, config: Optional[RoomConfig] = None) -> Room:
        """
        创建新房间

        Args:
            creator_id: 创建者ID
            name: 房间名称
            config: 房间配置

        Returns:
            Room: 创建的房间对象
        """
        room_id = self._generate_room_id()
        room_config = config or RoomConfig()

        room = Room(
            room_id=room_id,
            name=name,
            config=room_config,
            creator=creator_id
        )

        self.rooms[room_id] = room
        return room

    def get_room(self, room_id: str) -> Optional[Room]:
        """获取房间"""
        return self.rooms.get(room_id)

    def delete_room(self, room_id: str) -> bool:
        """删除房间"""
        if room_id in self.rooms:
            del self.rooms[room_id]
            return True
        return False

    def list_rooms(self, status: Optional[RoomStatus] = None) -> List[Room]:
        """
        获取房间列表

        Args:
            status: 过滤房间状态

        Returns:
            List[Room]: 房间列表
        """
        rooms = list(self.rooms.values())

        if status:
            rooms = [room for room in rooms if room.status == status]

        # 按创建时间排序
        rooms.sort(key=lambda r: r.created_at, reverse=True)
        return rooms

    def join_room(self, room_id: str, player_id: str) -> Tuple[bool, str]:
        """
        玩家加入房间

        Args:
            room_id: 房间ID
            player_id: 玩家ID

        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在"

        if room.status == RoomStatus.CLOSED:
            return False, "房间已关闭"

        if room.is_full():
            return False, "房间已满"

        if room.is_player_in_room(player_id):
            return False, "您已在房间中"

        if room.add_player(player_id):
            return True, "成功加入房间"
        else:
            return False, "加入房间失败"

    def leave_room(self, room_id: str, player_id: str) -> Tuple[bool, str]:
        """
        玩家离开房间

        Args:
            room_id: 房间ID
            player_id: 玩家ID

        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在"

        if not room.is_player_in_room(player_id):
            return False, "您不在此房间中"

        if room.remove_player(player_id):
            # 如果房间空了，删除房间
            if room.status == RoomStatus.CLOSED:
                self.delete_room(room_id)
            return True, "成功离开房间"
        else:
            return False, "离开房间失败"

    def start_game(self, room_id: str, player_id: str) -> Tuple[bool, str, Optional[Game]]:
        """
        开始游戏

        Args:
            room_id: 房间ID
            player_id: 发起者ID

        Returns:
            Tuple[bool, str, Optional[Game]]: (成功标志, 消息, 游戏对象)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在", None

        if not room.is_player_in_room(player_id):
            return False, "您不在此房间中", None

        if room.get_player_count() < 2:
            return False, "需要至少2名玩家才能开始游戏", None

        if room.start_game():
            return True, "游戏开始", room.current_game
        else:
            return False, "开始游戏失败", None

    def make_move(self, room_id: str, player_id: str, x: int, y: int) -> Tuple[bool, str, Optional[dict]]:
        """
        在房间中下棋

        Args:
            room_id: 房间ID
            player_id: 玩家ID
            x, y: 下棋位置

        Returns:
            Tuple[bool, str, Optional[dict]]: (成功标志, 消息, 游戏结果)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在", None

        if not room.current_game:
            return False, "房间中没有进行中的游戏", None

        if not room.is_player_in_room(player_id):
            return False, "您不在此房间中", None

        # 使用游戏逻辑处理下棋
        success, message, result = self.game_logic.process_move(
            room.current_game, player_id, x, y
        )

        if success and result:
            # 游戏结束，更新房间状态
            room.finish_game()

        return success, message, result.model_dump() if result else None

    def get_room_game_state(self, room_id: str) -> Optional[dict]:
        """
        获取房间游戏状态

        Args:
            room_id: 房间ID

        Returns:
            Optional[dict]: 游戏状态字典
        """
        room = self.get_room(room_id)
        if not room or not room.current_game:
            return None

        return room.current_game.to_dict()

    def add_spectator(self, room_id: str, player_id: str) -> Tuple[bool, str]:
        """
        添加观战者

        Args:
            room_id: 房间ID
            player_id: 玩家ID

        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在"

        if room.add_spectator(player_id):
            return True, "成功加入观战"
        else:
            return False, "加入观战失败"

    def remove_spectator(self, room_id: str, player_id: str) -> Tuple[bool, str]:
        """
        移除观战者

        Args:
            room_id: 房间ID
            player_id: 玩家ID

        Returns:
            Tuple[bool, str]: (成功标志, 消息)
        """
        room = self.get_room(room_id)
        if not room:
            return False, "房间不存在"

        if room.remove_spectator(player_id):
            return True, "成功离开观战"
        else:
            return False, "离开观战失败"

    def cleanup_empty_rooms(self):
        """清理空房间和过期房间"""
        current_time = datetime.now()
        rooms_to_delete = []

        for room_id, room in self.rooms.items():
            # 删除关闭的房间
            if room.status == RoomStatus.CLOSED:
                rooms_to_delete.append(room_id)
            # 删除长时间无人的房间
            elif (room.get_player_count() == 0 and
                  current_time - room.updated_at > self.cleanup_interval):
                rooms_to_delete.append(room_id)

        for room_id in rooms_to_delete:
            self.delete_room(room_id)

    def get_player_room(self, player_id: str) -> Optional[Room]:
        """获取玩家所在的房间"""
        for room in self.rooms.values():
            if room.is_player_in_room(player_id) or room.is_spectator_in_room(player_id):
                return room
        return None

    def _generate_room_id(self) -> str:
        """生成房间ID"""
        return f"room_{uuid.uuid4().hex[:8]}"

    def get_statistics(self) -> dict:
        """获取房间管理统计信息"""
        total_rooms = len(self.rooms)
        waiting_rooms = len([r for r in self.rooms.values() if r.status == RoomStatus.WAITING])
        playing_rooms = len([r for r in self.rooms.values() if r.status == RoomStatus.PLAYING])
        finished_rooms = len([r for r in self.rooms.values() if r.status == RoomStatus.FINISHED])

        total_players = sum(r.get_player_count() for r in self.rooms.values())
        total_spectators = sum(r.get_spectator_count() for r in self.rooms.values())

        return {
            "total_rooms": total_rooms,
            "waiting_rooms": waiting_rooms,
            "playing_rooms": playing_rooms,
            "finished_rooms": finished_rooms,
            "total_players": total_players,
            "total_spectators": total_spectators
        }
