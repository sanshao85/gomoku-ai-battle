"""
游戏房间模型
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from .game import Game, GameStatus


class RoomStatus(str, Enum):
    """房间状态枚举"""
    WAITING = "waiting"      # 等待玩家加入
    PLAYING = "playing"      # 游戏进行中
    FINISHED = "finished"    # 游戏结束
    CLOSED = "closed"        # 房间关闭


class RoomConfig(BaseModel):
    """房间配置"""
    max_players: int = Field(default=2, description="最大玩家数")
    auto_start: bool = Field(default=True, description="人满自动开始")
    allow_spectators: bool = Field(default=False, description="允许观战")
    time_limit: Optional[int] = Field(30, description="每步时间限制(秒)")
    total_time_limit: Optional[int] = Field(600, description="总游戏时间限制(秒)")
    auto_play: bool = Field(default=False, description="AI自动对战模式")


class Room(BaseModel):
    """游戏房间模型"""
    room_id: str = Field(..., description="房间ID")
    name: str = Field(..., description="房间名称")
    status: RoomStatus = Field(default=RoomStatus.WAITING, description="房间状态")
    config: RoomConfig = Field(default_factory=RoomConfig, description="房间配置")
    players: List[str] = Field(default_factory=list, description="玩家列表")
    spectators: List[str] = Field(default_factory=list, description="观战者列表")
    current_game: Optional[Game] = Field(None, description="当前游戏")
    game_history: List[str] = Field(default_factory=list, description="历史游戏ID列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    creator: str = Field(..., description="房间创建者")

    def add_player(self, player_id: str) -> bool:
        """添加玩家到房间"""
        if len(self.players) >= self.config.max_players:
            return False

        if player_id in self.players:
            return False

        self.players.append(player_id)
        self.updated_at = datetime.now()

        # 如果人满且配置为自动开始，则开始游戏
        if len(self.players) == self.config.max_players and self.config.auto_start:
            self.start_game()

        return True

    def remove_player(self, player_id: str) -> bool:
        """从房间移除玩家"""
        if player_id not in self.players:
            return False

        self.players.remove(player_id)
        self.updated_at = datetime.now()

        # 如果游戏进行中，暂停游戏
        if self.current_game and self.current_game.status == GameStatus.PLAYING:
            self.current_game.remove_player(player_id)
            if len(self.players) < 2:
                self.status = RoomStatus.WAITING

        # 如果房间空了，关闭房间
        if not self.players:
            self.status = RoomStatus.CLOSED

        return True

    def add_spectator(self, player_id: str) -> bool:
        """添加观战者"""
        if not self.config.allow_spectators:
            return False

        if player_id in self.spectators or player_id in self.players:
            return False

        self.spectators.append(player_id)
        self.updated_at = datetime.now()
        return True

    def remove_spectator(self, player_id: str) -> bool:
        """移除观战者"""
        if player_id not in self.spectators:
            return False

        self.spectators.remove(player_id)
        self.updated_at = datetime.now()
        return True

    def start_game(self) -> bool:
        """开始新游戏"""
        if len(self.players) < 2:
            return False

        if self.current_game and self.current_game.status == GameStatus.PLAYING:
            return False

        # 创建新游戏
        game_id = f"{self.room_id}_game_{len(self.game_history) + 1}"
        self.current_game = Game(game_id=game_id)

        # 添加玩家到游戏
        for player_id in self.players:
            self.current_game.add_player(player_id)

        self.status = RoomStatus.PLAYING
        self.updated_at = datetime.now()

        return True

    def finish_game(self) -> bool:
        """结束当前游戏"""
        if not self.current_game:
            return False

        # 将游戏添加到历史记录
        self.game_history.append(self.current_game.game_id)

        # 更新房间状态
        self.status = RoomStatus.FINISHED
        self.updated_at = datetime.now()

        return True

    def reset_for_new_game(self) -> bool:
        """重置房间准备新游戏"""
        if self.status != RoomStatus.FINISHED:
            return False

        self.current_game = None
        self.status = RoomStatus.WAITING if len(self.players) < 2 else RoomStatus.WAITING
        self.updated_at = datetime.now()

        return True

    def get_player_count(self) -> int:
        """获取玩家数量"""
        return len(self.players)

    def get_spectator_count(self) -> int:
        """获取观战者数量"""
        return len(self.spectators)

    def is_full(self) -> bool:
        """检查房间是否已满"""
        return len(self.players) >= self.config.max_players

    def is_player_in_room(self, player_id: str) -> bool:
        """检查玩家是否在房间中"""
        return player_id in self.players

    def is_spectator_in_room(self, player_id: str) -> bool:
        """检查是否为观战者"""
        return player_id in self.spectators

    def get_room_info(self) -> dict:
        """获取房间信息"""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "status": self.status.value,
            "player_count": self.get_player_count(),
            "max_players": self.config.max_players,
            "spectator_count": self.get_spectator_count(),
            "is_full": self.is_full(),
            "created_at": self.created_at.isoformat(),
            "creator": self.creator,
            "current_game_id": self.current_game.game_id if self.current_game else None,
            "game_count": len(self.game_history)
        }

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "status": self.status.value,
            "config": self.config.model_dump(),
            "players": self.players,
            "spectators": self.spectators,
            "current_game": self.current_game.to_dict() if self.current_game else None,
            "game_history": self.game_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "creator": self.creator
        }
