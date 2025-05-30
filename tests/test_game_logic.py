"""
游戏逻辑测试
"""
import pytest
from game_server.models.game import Game, GameBoard, PlayerColor
from game_server.services.game_logic import GameLogic


class TestGameLogic:
    """游戏逻辑测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.game_logic = GameLogic()
        self.board = GameBoard()
    
    def test_is_valid_move(self):
        """测试有效移动检查"""
        # 测试有效位置
        assert self.game_logic.is_valid_move(self.board, 7, 7) == True
        assert self.game_logic.is_valid_move(self.board, 0, 0) == True
        assert self.game_logic.is_valid_move(self.board, 14, 14) == True
        
        # 测试无效位置
        assert self.game_logic.is_valid_move(self.board, -1, 0) == False
        assert self.game_logic.is_valid_move(self.board, 0, -1) == False
        assert self.game_logic.is_valid_move(self.board, 15, 0) == False
        assert self.game_logic.is_valid_move(self.board, 0, 15) == False
        
        # 测试已占用位置
        self.board.set_cell(7, 7, PlayerColor.BLACK)
        assert self.game_logic.is_valid_move(self.board, 7, 7) == False
    
    def test_check_winner_horizontal(self):
        """测试水平获胜检查"""
        # 设置水平五子连珠
        for x in range(5, 10):
            self.board.set_cell(x, 7, PlayerColor.BLACK)
        
        result = self.game_logic.check_winner(self.board, (7, 7))
        assert result is not None
        assert result.winner == PlayerColor.BLACK
        assert len(result.winning_line) == 5
    
    def test_check_winner_vertical(self):
        """测试垂直获胜检查"""
        # 设置垂直五子连珠
        for y in range(5, 10):
            self.board.set_cell(7, y, PlayerColor.WHITE)
        
        result = self.game_logic.check_winner(self.board, (7, 7))
        assert result is not None
        assert result.winner == PlayerColor.WHITE
        assert len(result.winning_line) == 5
    
    def test_check_winner_diagonal(self):
        """测试对角线获胜检查"""
        # 设置主对角线五子连珠
        for i in range(5):
            self.board.set_cell(5 + i, 5 + i, PlayerColor.BLACK)
        
        result = self.game_logic.check_winner(self.board, (7, 7))
        assert result is not None
        assert result.winner == PlayerColor.BLACK
        assert len(result.winning_line) == 5
    
    def test_check_winner_anti_diagonal(self):
        """测试反对角线获胜检查"""
        # 设置反对角线五子连珠
        for i in range(5):
            self.board.set_cell(9 - i, 5 + i, PlayerColor.WHITE)
        
        result = self.game_logic.check_winner(self.board, (7, 7))
        assert result is not None
        assert result.winner == PlayerColor.WHITE
        assert len(result.winning_line) == 5
    
    def test_no_winner(self):
        """测试无获胜者情况"""
        # 设置一些棋子但不构成五子连珠
        self.board.set_cell(7, 7, PlayerColor.BLACK)
        self.board.set_cell(7, 8, PlayerColor.BLACK)
        self.board.set_cell(7, 9, PlayerColor.BLACK)
        self.board.set_cell(7, 10, PlayerColor.BLACK)
        
        result = self.game_logic.check_winner(self.board, (7, 7))
        assert result is None
    
    def test_get_valid_moves(self):
        """测试获取有效移动"""
        # 空棋盘应该有225个有效位置
        valid_moves = self.game_logic.get_valid_moves(self.board)
        assert len(valid_moves) == 225
        
        # 放置一个棋子后应该减少一个有效位置
        self.board.set_cell(7, 7, PlayerColor.BLACK)
        valid_moves = self.game_logic.get_valid_moves(self.board)
        assert len(valid_moves) == 224
        assert (7, 7) not in valid_moves
    
    def test_evaluate_position(self):
        """测试局面评估"""
        # 空棋盘评估应该为0
        score = self.game_logic.evaluate_position(self.board, PlayerColor.BLACK)
        assert score == 0
        
        # 放置一些黑子
        self.board.set_cell(7, 7, PlayerColor.BLACK)
        self.board.set_cell(7, 8, PlayerColor.BLACK)
        
        score_black = self.game_logic.evaluate_position(self.board, PlayerColor.BLACK)
        score_white = self.game_logic.evaluate_position(self.board, PlayerColor.WHITE)
        
        # 黑子应该有优势
        assert score_black > 0
        assert score_white < 0
    
    def test_get_suggested_moves(self):
        """测试获取建议移动"""
        # 空棋盘的建议
        suggestions = self.game_logic.get_suggested_moves(self.board, PlayerColor.BLACK, 5)
        assert len(suggestions) <= 5
        
        # 有棋子的情况
        self.board.set_cell(7, 7, PlayerColor.BLACK)
        suggestions = self.game_logic.get_suggested_moves(self.board, PlayerColor.WHITE, 3)
        assert len(suggestions) <= 3
        assert (7, 7) not in suggestions


class TestGame:
    """游戏模型测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.game = Game(game_id="test_game")
    
    def test_add_player(self):
        """测试添加玩家"""
        assert self.game.add_player("player1") == True
        assert len(self.game.players) == 1
        assert self.game.status.value == "waiting"
        
        assert self.game.add_player("player2") == True
        assert len(self.game.players) == 2
        assert self.game.status.value == "playing"
        
        # 不能添加第三个玩家
        assert self.game.add_player("player3") == False
        assert len(self.game.players) == 2
    
    def test_get_player_color(self):
        """测试获取玩家颜色"""
        self.game.add_player("player1")
        self.game.add_player("player2")
        
        assert self.game.get_player_color("player1") == PlayerColor.BLACK
        assert self.game.get_player_color("player2") == PlayerColor.WHITE
        assert self.game.get_player_color("player3") is None
    
    def test_make_move(self):
        """测试下棋"""
        self.game.add_player("player1")
        self.game.add_player("player2")
        
        # 黑子先下
        assert self.game.make_move("player1", 7, 7) == True
        assert self.game.board.get_cell(7, 7) == PlayerColor.BLACK
        assert self.game.current_player == PlayerColor.WHITE
        assert len(self.game.moves) == 1
        
        # 白子下
        assert self.game.make_move("player2", 7, 8) == True
        assert self.game.board.get_cell(7, 8) == PlayerColor.WHITE
        assert self.game.current_player == PlayerColor.BLACK
        assert len(self.game.moves) == 2
        
        # 不能在已占用位置下棋
        assert self.game.make_move("player1", 7, 7) == False
        
        # 不能在不是自己回合时下棋
        assert self.game.make_move("player2", 8, 8) == False
