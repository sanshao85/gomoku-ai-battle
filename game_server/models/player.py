"""
玩家模型
"""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PlayerStatus(str, Enum):
    """玩家状态枚举"""
    ONLINE = "online"        # 在线
    OFFLINE = "offline"      # 离线
    IN_GAME = "in_game"      # 游戏中
    SPECTATING = "spectating"  # 观战中


class PlayerStats(BaseModel):
    """玩家统计信息"""
    games_played: int = Field(default=0, description="总游戏数")
    games_won: int = Field(default=0, description="胜利数")
    games_lost: int = Field(default=0, description="失败数")
    games_draw: int = Field(default=0, description="平局数")
    total_moves: int = Field(default=0, description="总下棋数")
    average_move_time: float = Field(default=0.0, description="平均下棋时间(秒)")
    longest_game: int = Field(default=0, description="最长游戏步数")
    shortest_win: int = Field(default=0, description="最短获胜步数")
    
    @property
    def win_rate(self) -> float:
        """胜率"""
        if self.games_played == 0:
            return 0.0
        return self.games_won / self.games_played
    
    @property
    def loss_rate(self) -> float:
        """败率"""
        if self.games_played == 0:
            return 0.0
        return self.games_lost / self.games_played
    
    def update_game_result(self, won: bool, draw: bool = False, moves: int = 0, game_time: float = 0.0):
        """更新游戏结果统计"""
        self.games_played += 1
        
        if draw:
            self.games_draw += 1
        elif won:
            self.games_won += 1
            if self.shortest_win == 0 or moves < self.shortest_win:
                self.shortest_win = moves
        else:
            self.games_lost += 1
        
        if moves > self.longest_game:
            self.longest_game = moves
        
        # 更新平均下棋时间
        if moves > 0:
            self.total_moves += moves
            total_time = self.average_move_time * (self.total_moves - moves) + game_time
            self.average_move_time = total_time / self.total_moves


class Player(BaseModel):
    """玩家模型"""
    player_id: str = Field(..., description="玩家ID")
    name: str = Field(..., description="玩家名称")
    status: PlayerStatus = Field(default=PlayerStatus.OFFLINE, description="玩家状态")
    current_room_id: Optional[str] = Field(None, description="当前房间ID")
    current_game_id: Optional[str] = Field(None, description="当前游戏ID")
    stats: PlayerStats = Field(default_factory=PlayerStats, description="统计信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_seen: datetime = Field(default_factory=datetime.now, description="最后在线时间")
    last_move_time: Optional[datetime] = Field(None, description="最后下棋时间")
    preferences: dict = Field(default_factory=dict, description="玩家偏好设置")
    
    def set_online(self):
        """设置玩家在线"""
        self.status = PlayerStatus.ONLINE
        self.last_seen = datetime.now()
    
    def set_offline(self):
        """设置玩家离线"""
        self.status = PlayerStatus.OFFLINE
        self.current_room_id = None
        self.current_game_id = None
    
    def join_room(self, room_id: str):
        """加入房间"""
        self.current_room_id = room_id
        self.status = PlayerStatus.ONLINE
        self.last_seen = datetime.now()
    
    def leave_room(self):
        """离开房间"""
        self.current_room_id = None
        self.current_game_id = None
        self.status = PlayerStatus.ONLINE
    
    def start_game(self, game_id: str):
        """开始游戏"""
        self.current_game_id = game_id
        self.status = PlayerStatus.IN_GAME
        self.last_seen = datetime.now()
    
    def finish_game(self, won: bool = False, draw: bool = False, moves: int = 0, game_time: float = 0.0):
        """结束游戏"""
        self.current_game_id = None
        self.status = PlayerStatus.ONLINE
        self.stats.update_game_result(won, draw, moves, game_time)
        self.last_seen = datetime.now()
    
    def start_spectating(self, room_id: str):
        """开始观战"""
        self.current_room_id = room_id
        self.status = PlayerStatus.SPECTATING
        self.last_seen = datetime.now()
    
    def stop_spectating(self):
        """停止观战"""
        self.current_room_id = None
        self.status = PlayerStatus.ONLINE
    
    def make_move(self):
        """记录下棋动作"""
        self.last_move_time = datetime.now()
        self.last_seen = datetime.now()
    
    def is_in_room(self) -> bool:
        """检查是否在房间中"""
        return self.current_room_id is not None
    
    def is_in_game(self) -> bool:
        """检查是否在游戏中"""
        return self.current_game_id is not None
    
    def is_available(self) -> bool:
        """检查是否可以加入新游戏"""
        return self.status == PlayerStatus.ONLINE and not self.is_in_room()
    
    def get_player_info(self) -> dict:
        """获取玩家基本信息"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "status": self.status.value,
            "current_room_id": self.current_room_id,
            "is_in_game": self.is_in_game(),
            "last_seen": self.last_seen.isoformat(),
            "win_rate": self.stats.win_rate,
            "games_played": self.stats.games_played
        }
    
    def get_detailed_stats(self) -> dict:
        """获取详细统计信息"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "stats": {
                "games_played": self.stats.games_played,
                "games_won": self.stats.games_won,
                "games_lost": self.stats.games_lost,
                "games_draw": self.stats.games_draw,
                "win_rate": self.stats.win_rate,
                "loss_rate": self.stats.loss_rate,
                "total_moves": self.stats.total_moves,
                "average_move_time": self.stats.average_move_time,
                "longest_game": self.stats.longest_game,
                "shortest_win": self.stats.shortest_win
            },
            "created_at": self.created_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "last_move_time": self.last_move_time.isoformat() if self.last_move_time else None
        }
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "status": self.status.value,
            "current_room_id": self.current_room_id,
            "current_game_id": self.current_game_id,
            "stats": self.stats.model_dump(),
            "created_at": self.created_at.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "last_move_time": self.last_move_time.isoformat() if self.last_move_time else None,
            "preferences": self.preferences
        }
