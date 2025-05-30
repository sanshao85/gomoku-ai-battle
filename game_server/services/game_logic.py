"""
五子棋游戏逻辑服务
"""
from typing import List, Tuple, Optional
from datetime import datetime

from ..models.game import Game, GameBoard, PlayerColor, GameResult, GameStatus


class GameLogic:
    """五子棋游戏逻辑处理类"""
    
    def __init__(self):
        self.board_size = 15
        self.win_length = 5
    
    def check_winner(self, board: GameBoard, last_move: Tuple[int, int]) -> Optional[GameResult]:
        """
        检查是否有获胜者
        
        Args:
            board: 游戏棋盘
            last_move: 最后一步的坐标 (x, y)
            
        Returns:
            GameResult: 如果有获胜者返回结果，否则返回None
        """
        x, y = last_move
        player = board.get_cell(x, y)
        
        if player == PlayerColor.EMPTY:
            return None
        
        # 检查四个方向：水平、垂直、对角线
        directions = [
            (1, 0),   # 水平
            (0, 1),   # 垂直
            (1, 1),   # 主对角线
            (1, -1),  # 反对角线
        ]
        
        for dx, dy in directions:
            line = self._get_line(board, x, y, dx, dy, player)
            if len(line) >= self.win_length:
                return GameResult(
                    winner=player,
                    winning_line=line,
                    reason=f"{player.name} 获得五子连珠胜利",
                    finished_at=datetime.now()
                )
        
        # 检查是否平局（棋盘满了）
        if self._is_board_full(board):
            return GameResult(
                winner=None,
                winning_line=None,
                reason="棋盘已满，平局",
                finished_at=datetime.now()
            )
        
        return None
    
    def _get_line(self, board: GameBoard, x: int, y: int, dx: int, dy: int, player: PlayerColor) -> List[Tuple[int, int]]:
        """
        获取指定方向上的连续棋子
        
        Args:
            board: 游戏棋盘
            x, y: 起始位置
            dx, dy: 方向向量
            player: 玩家颜色
            
        Returns:
            List[Tuple[int, int]]: 连续棋子的坐标列表
        """
        line = [(x, y)]
        
        # 向正方向搜索
        nx, ny = x + dx, y + dy
        while (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
               board.get_cell(nx, ny) == player):
            line.append((nx, ny))
            nx, ny = nx + dx, ny + dy
        
        # 向负方向搜索
        nx, ny = x - dx, y - dy
        while (0 <= nx < self.board_size and 0 <= ny < self.board_size and 
               board.get_cell(nx, ny) == player):
            line.insert(0, (nx, ny))
            nx, ny = nx - dx, ny - dy
        
        return line
    
    def _is_board_full(self, board: GameBoard) -> bool:
        """检查棋盘是否已满"""
        for y in range(self.board_size):
            for x in range(self.board_size):
                if board.get_cell(x, y) == PlayerColor.EMPTY:
                    return False
        return True
    
    def is_valid_move(self, board: GameBoard, x: int, y: int) -> bool:
        """
        检查下棋位置是否有效
        
        Args:
            board: 游戏棋盘
            x, y: 下棋位置
            
        Returns:
            bool: 位置是否有效
        """
        # 检查坐标范围
        if not (0 <= x < self.board_size and 0 <= y < self.board_size):
            return False
        
        # 检查位置是否为空
        return board.is_empty(x, y)
    
    def get_valid_moves(self, board: GameBoard) -> List[Tuple[int, int]]:
        """
        获取所有有效的下棋位置
        
        Args:
            board: 游戏棋盘
            
        Returns:
            List[Tuple[int, int]]: 有效位置列表
        """
        return board.get_empty_positions()
    
    def evaluate_position(self, board: GameBoard, player: PlayerColor) -> int:
        """
        评估当前局面对指定玩家的优势
        
        Args:
            board: 游戏棋盘
            player: 玩家颜色
            
        Returns:
            int: 评估分数，正数表示优势，负数表示劣势
        """
        score = 0
        opponent = PlayerColor.WHITE if player == PlayerColor.BLACK else PlayerColor.BLACK
        
        # 评估所有位置的连子情况
        for y in range(self.board_size):
            for x in range(self.board_size):
                if board.get_cell(x, y) == player:
                    score += self._evaluate_position_score(board, x, y, player)
                elif board.get_cell(x, y) == opponent:
                    score -= self._evaluate_position_score(board, x, y, opponent)
        
        return score
    
    def _evaluate_position_score(self, board: GameBoard, x: int, y: int, player: PlayerColor) -> int:
        """评估单个位置的分数"""
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            line = self._get_line(board, x, y, dx, dy, player)
            length = len(line)
            
            # 根据连子长度给分
            if length >= 5:
                score += 10000  # 获胜
            elif length == 4:
                score += 1000   # 四子连珠
            elif length == 3:
                score += 100    # 三子连珠
            elif length == 2:
                score += 10     # 两子连珠
        
        return score
    
    def get_suggested_moves(self, board: GameBoard, player: PlayerColor, count: int = 5) -> List[Tuple[int, int]]:
        """
        获取建议的下棋位置
        
        Args:
            board: 游戏棋盘
            player: 玩家颜色
            count: 返回建议数量
            
        Returns:
            List[Tuple[int, int]]: 建议位置列表，按优先级排序
        """
        valid_moves = self.get_valid_moves(board)
        if not valid_moves:
            return []
        
        # 评估每个位置的分数
        move_scores = []
        for x, y in valid_moves:
            # 临时下棋
            test_board = board.copy()
            test_board.set_cell(x, y, player)
            
            # 评估分数
            score = self.evaluate_position(test_board, player)
            move_scores.append(((x, y), score))
        
        # 按分数排序
        move_scores.sort(key=lambda item: item[1], reverse=True)
        
        # 返回前count个建议
        return [move for move, score in move_scores[:count]]
    
    def process_move(self, game: Game, player_id: str, x: int, y: int) -> Tuple[bool, str, Optional[GameResult]]:
        """
        处理下棋动作
        
        Args:
            game: 游戏对象
            player_id: 玩家ID
            x, y: 下棋位置
            
        Returns:
            Tuple[bool, str, Optional[GameResult]]: (成功标志, 消息, 游戏结果)
        """
        # 检查游戏状态
        if game.status != GameStatus.PLAYING:
            return False, "游戏未在进行中", None
        
        # 检查是否轮到该玩家
        if not game.is_player_turn(player_id):
            return False, "不是您的回合", None
        
        # 检查位置是否有效
        if not self.is_valid_move(game.board, x, y):
            return False, "无效的下棋位置", None
        
        # 执行下棋
        if not game.make_move(player_id, x, y):
            return False, "下棋失败", None
        
        # 检查游戏结果
        result = self.check_winner(game.board, (x, y))
        if result:
            game.result = result
            game.status = GameStatus.FINISHED
            game.finished_at = datetime.now()
            return True, "下棋成功，游戏结束", result
        
        return True, "下棋成功", None
