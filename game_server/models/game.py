"""
五子棋游戏模型
"""
from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class GameStatus(str, Enum):
    """游戏状态枚举"""
    WAITING = "waiting"      # 等待玩家
    PLAYING = "playing"      # 游戏进行中
    FINISHED = "finished"    # 游戏结束
    PAUSED = "paused"        # 游戏暂停


class PlayerColor(int, Enum):
    """玩家颜色枚举"""
    EMPTY = 0    # 空位
    BLACK = 1    # 黑子
    WHITE = 2    # 白子


class Move(BaseModel):
    """下棋动作模型"""
    x: int = Field(..., ge=0, le=14, description="X坐标 (0-14)")
    y: int = Field(..., ge=0, le=14, description="Y坐标 (0-14)")
    player: PlayerColor = Field(..., description="下棋玩家")
    timestamp: datetime = Field(default_factory=datetime.now, description="下棋时间")


class GameResult(BaseModel):
    """游戏结果模型"""
    winner: Optional[PlayerColor] = Field(None, description="获胜者，None表示平局")
    winning_line: Optional[List[Tuple[int, int]]] = Field(None, description="获胜连线坐标")
    reason: str = Field(..., description="游戏结束原因")
    finished_at: datetime = Field(default_factory=datetime.now, description="结束时间")


class GameBoard(BaseModel):
    """游戏棋盘模型"""
    board: List[List[int]] = Field(
        default_factory=lambda: [[0 for _ in range(15)] for _ in range(15)],
        description="15x15棋盘，0=空，1=黑，2=白"
    )
    size: int = Field(default=15, description="棋盘大小")

    def get_cell(self, x: int, y: int) -> PlayerColor:
        """获取指定位置的棋子"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return PlayerColor(self.board[y][x])
        return PlayerColor.EMPTY

    def set_cell(self, x: int, y: int, player: PlayerColor) -> bool:
        """在指定位置放置棋子"""
        if 0 <= x < self.size and 0 <= y < self.size and self.board[y][x] == 0:
            self.board[y][x] = player.value
            return True
        return False

    def is_empty(self, x: int, y: int) -> bool:
        """检查指定位置是否为空"""
        return self.get_cell(x, y) == PlayerColor.EMPTY

    def get_empty_positions(self) -> List[Tuple[int, int]]:
        """获取所有空位置"""
        positions = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == 0:
                    positions.append((x, y))
        return positions

    def copy(self) -> "GameBoard":
        """复制棋盘"""
        new_board = GameBoard(size=self.size)
        new_board.board = [row[:] for row in self.board]
        return new_board


class Game(BaseModel):
    """五子棋游戏模型"""
    game_id: str = Field(..., description="游戏ID")
    board: GameBoard = Field(default_factory=GameBoard, description="游戏棋盘")
    current_player: PlayerColor = Field(default=PlayerColor.BLACK, description="当前轮到的玩家")
    status: GameStatus = Field(default=GameStatus.WAITING, description="游戏状态")
    players: List[str] = Field(default_factory=list, description="玩家列表")
    moves: List[Move] = Field(default_factory=list, description="下棋历史")
    result: Optional[GameResult] = Field(None, description="游戏结果")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    finished_at: Optional[datetime] = Field(None, description="结束时间")
    last_move_time: Optional[datetime] = Field(None, description="最后下棋时间")
    move_timeout: int = Field(default=120, description="每步超时时间(秒，默认2分钟)")
    auto_move_on_timeout: bool = Field(default=True, description="超时自动下棋")

    def add_player(self, player_id: str) -> bool:
        """添加玩家"""
        if len(self.players) < 2 and player_id not in self.players:
            self.players.append(player_id)
            if len(self.players) == 2:
                self.status = GameStatus.PLAYING
                self.started_at = datetime.now()
            return True
        return False

    def remove_player(self, player_id: str) -> bool:
        """移除玩家"""
        if player_id in self.players:
            self.players.remove(player_id)
            if self.status == GameStatus.PLAYING:
                self.status = GameStatus.PAUSED
            return True
        return False

    def get_player_color(self, player_id: str) -> Optional[PlayerColor]:
        """获取玩家颜色"""
        if player_id not in self.players:
            return None
        index = self.players.index(player_id)
        return PlayerColor.BLACK if index == 0 else PlayerColor.WHITE

    def is_player_turn(self, player_id: str) -> bool:
        """检查是否轮到指定玩家"""
        player_color = self.get_player_color(player_id)
        return player_color == self.current_player

    def make_move(self, player_id: str, x: int, y: int) -> bool:
        """下棋"""
        # 检查游戏状态
        if self.status != GameStatus.PLAYING:
            return False

        # 检查是否轮到该玩家
        if not self.is_player_turn(player_id):
            return False

        # 检查位置是否有效
        if not self.board.is_empty(x, y):
            return False

        # 下棋
        player_color = self.get_player_color(player_id)
        if self.board.set_cell(x, y, player_color):
            # 记录移动
            move = Move(x=x, y=y, player=player_color)
            self.moves.append(move)

            # 更新最后下棋时间
            self.last_move_time = datetime.now()

            # 切换玩家
            self.current_player = PlayerColor.WHITE if self.current_player == PlayerColor.BLACK else PlayerColor.BLACK

            return True

        return False

    def get_last_move(self) -> Optional[Move]:
        """获取最后一步"""
        return self.moves[-1] if self.moves else None

    def is_move_timeout(self) -> bool:
        """检查当前玩家是否超时"""
        if self.status != GameStatus.PLAYING:
            return False

        if not self.last_move_time:
            # 如果没有下过棋，从游戏开始时间算
            start_time = self.started_at or self.created_at
        else:
            start_time = self.last_move_time

        elapsed = (datetime.now() - start_time).total_seconds()
        return elapsed > self.move_timeout

    def get_remaining_time(self) -> int:
        """获取当前玩家剩余时间(秒)"""
        if self.status != GameStatus.PLAYING:
            return 0

        if not self.last_move_time:
            start_time = self.started_at or self.created_at
        else:
            start_time = self.last_move_time

        elapsed = (datetime.now() - start_time).total_seconds()
        remaining = max(0, self.move_timeout - elapsed)
        return int(remaining)

    def auto_move_on_timeout(self) -> Optional[tuple]:
        """超时自动下棋，返回下棋位置"""
        if not self.is_move_timeout() or not self.auto_move_on_timeout:
            return None

        # 找一个随机的空位置
        empty_positions = self.board.get_empty_positions()
        if empty_positions:
            import random
            return random.choice(empty_positions)

        return None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "game_id": self.game_id,
            "board": self.board.board,
            "current_player": self.current_player.value,
            "status": self.status.value,
            "players": self.players,
            "moves_count": len(self.moves),
            "last_move": self.get_last_move().model_dump() if self.get_last_move() else None,
            "result": self.result.model_dump() if self.result else None,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
