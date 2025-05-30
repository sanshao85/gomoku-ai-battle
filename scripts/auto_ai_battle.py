#!/usr/bin/env python3
"""
自动AI对战脚本 - 让AI自动检测轮到自己并下棋
"""
import asyncio
import logging
import sys
import os
import argparse
import random
from typing import Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client.mcp_client import GomokuMCPClient

logger = logging.getLogger(__name__)


class AutoAI:
    """自动AI对战类"""
    
    def __init__(self, player_id: str, room_id: str, check_interval: float = 2.0):
        """
        初始化自动AI
        
        Args:
            player_id: AI玩家ID
            room_id: 房间ID
            check_interval: 检查间隔(秒)
        """
        self.player_id = player_id
        self.room_id = room_id
        self.check_interval = check_interval
        self.client = GomokuMCPClient()
        self.is_running = False
        self.my_color = None  # 1=黑子, 2=白子
    
    async def __aenter__(self):
        await self.client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()
    
    def parse_board_state(self, board_text: str) -> tuple:
        """
        解析棋盘状态
        
        Returns:
            (current_player, is_my_turn, board_array, game_status)
        """
        try:
            lines = board_text.split('\n')
            
            # 解析当前玩家
            current_player = 1  # 默认黑子
            if "当前轮到: 白子" in board_text:
                current_player = 2
            elif "当前轮到: 黑子" in board_text:
                current_player = 1
            
            # 解析游戏状态
            game_status = "playing"
            if "游戏结束" in board_text or "获胜" in board_text or "平局" in board_text:
                game_status = "finished"
            
            # 解析棋盘
            board = [[0 for _ in range(15)] for _ in range(15)]
            for i, line in enumerate(lines):
                if line.strip().startswith(str(i)) and i < 15:
                    row_data = line.strip().split()[1:]  # 跳过行号
                    for j, cell in enumerate(row_data[:15]):
                        if cell == '●':
                            board[i][j] = 1  # 黑子
                        elif cell == '○':
                            board[i][j] = 2  # 白子
            
            # 确定我的颜色（如果还不知道）
            if self.my_color is None:
                # 通过游戏信息确定我的颜色
                if f"玩家: {self.player_id}" in board_text:
                    # 简单假设：第一个玩家是黑子
                    self.my_color = 1 if self.player_id.endswith("1") else 2
                else:
                    self.my_color = 1  # 默认黑子
            
            # 判断是否轮到我
            is_my_turn = (current_player == self.my_color)
            
            return current_player, is_my_turn, board, game_status
            
        except Exception as e:
            logger.error(f"解析棋盘状态失败: {e}")
            return 1, False, None, "error"
    
    def choose_move(self, board: list) -> tuple:
        """
        选择下棋位置（简单AI策略）
        
        Args:
            board: 15x15棋盘数组
            
        Returns:
            (x, y): 选择的位置
        """
        if not board:
            return 7, 7  # 默认中心
        
        # 策略1: 如果中心空着，下中心
        if board[7][7] == 0:
            return 7, 7
        
        # 策略2: 找到所有空位
        empty_positions = []
        for y in range(15):
            for x in range(15):
                if board[y][x] == 0:
                    empty_positions.append((x, y))
        
        if not empty_positions:
            return 0, 0  # 不应该发生
        
        # 策略3: 优先选择已有棋子附近的位置
        nearby_positions = []
        for x, y in empty_positions:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] != 0:
                        nearby_positions.append((x, y))
                        break
                if nearby_positions and nearby_positions[-1] == (x, y):
                    break
        
        if nearby_positions:
            return random.choice(nearby_positions)
        else:
            return random.choice(empty_positions)
    
    async def auto_play(self):
        """自动对战主循环"""
        logger.info(f"开始自动对战: {self.player_id} 在房间 {self.room_id}")
        self.is_running = True
        
        try:
            while self.is_running:
                try:
                    # 获取棋盘状态
                    board_state = await self.client.get_board_state(self.room_id)
                    
                    # 解析状态
                    current_player, is_my_turn, board, game_status = self.parse_board_state(board_state)
                    
                    # 检查游戏是否结束
                    if game_status == "finished":
                        logger.info(f"游戏结束: {board_state}")
                        break
                    
                    # 如果轮到我，就下棋
                    if is_my_turn and board:
                        logger.info(f"轮到 {self.player_id} (颜色: {'黑子' if self.my_color == 1 else '白子'})")
                        
                        # 获取AI建议（可选）
                        try:
                            suggestions = await self.client.get_move_suggestions(
                                self.room_id, self.player_id, 3
                            )
                            logger.info(f"AI建议: {suggestions}")
                        except Exception as e:
                            logger.warning(f"获取建议失败: {e}")
                        
                        # 选择下棋位置
                        x, y = self.choose_move(board)
                        logger.info(f"{self.player_id} 选择位置: ({x}, {y})")
                        
                        # 下棋
                        result = await self.client.make_move(self.room_id, self.player_id, x, y)
                        logger.info(f"下棋结果: {result}")
                        
                        # 检查是否获胜
                        if "获胜" in result or "平局" in result:
                            logger.info(f"游戏结束: {result}")
                            break
                    
                    else:
                        logger.debug(f"等待对手下棋... (当前: {'黑子' if current_player == 1 else '白子'})")
                    
                    # 等待一段时间再检查
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"对战循环出错: {e}")
                    await asyncio.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("用户中断对战")
        except Exception as e:
            logger.error(f"自动对战失败: {e}")
        finally:
            self.is_running = False
            logger.info(f"{self.player_id} 结束自动对战")
    
    def stop(self):
        """停止自动对战"""
        self.is_running = False


async def run_auto_battle(room_id: str, player1_id: str, player2_id: str, 
                         check_interval: float = 2.0):
    """
    运行双AI自动对战
    
    Args:
        room_id: 房间ID
        player1_id: 玩家1 ID
        player2_id: 玩家2 ID
        check_interval: 检查间隔
    """
    logger.info(f"启动双AI自动对战: {player1_id} vs {player2_id}")
    
    # 创建两个AI实例
    ai1 = AutoAI(player1_id, room_id, check_interval)
    ai2 = AutoAI(player2_id, room_id, check_interval)
    
    try:
        async with ai1, ai2:
            # 并行运行两个AI
            await asyncio.gather(
                ai1.auto_play(),
                ai2.auto_play()
            )
    except Exception as e:
        logger.error(f"自动对战失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动AI对战")
    parser.add_argument("--room-id", required=True, help="房间ID")
    parser.add_argument("--player1", default="Auto_AI_1", help="玩家1 ID")
    parser.add_argument("--player2", default="Auto_AI_2", help="玩家2 ID")
    parser.add_argument("--interval", type=float, default=2.0, help="检查间隔(秒)")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        asyncio.run(run_auto_battle(
            args.room_id, args.player1, args.player2, args.interval
        ))
    except KeyboardInterrupt:
        logger.info("自动对战已停止")
    except Exception as e:
        logger.error(f"运行失败: {e}")


if __name__ == "__main__":
    main()
