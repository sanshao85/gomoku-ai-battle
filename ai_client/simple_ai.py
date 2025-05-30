#!/usr/bin/env python3
"""
简单AI客户端实现
"""
import asyncio
import logging
import random
import re
from typing import Optional, Tuple, List

from .mcp_client import GomokuMCPClient

logger = logging.getLogger(__name__)


class SimpleGomokuAI:
    """简单的五子棋AI"""
    
    def __init__(self, player_id: str, mcp_server_script: str = "scripts/start_mcp_server.py"):
        """
        初始化AI
        
        Args:
            player_id: AI玩家ID
            mcp_server_script: MCP服务器脚本路径
        """
        self.player_id = player_id
        self.mcp_client = GomokuMCPClient(mcp_server_script)
        self.current_room_id: Optional[str] = None
        self.is_playing = False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.mcp_client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.mcp_client.disconnect()
    
    async def create_and_join_room(self, room_name: str) -> bool:
        """
        创建并加入房间
        
        Args:
            room_name: 房间名称
            
        Returns:
            bool: 是否成功
        """
        try:
            # 创建房间
            result = await self.mcp_client.create_room(self.player_id, room_name)
            logger.info(f"创建房间结果: {result}")
            
            # 从结果中提取房间ID
            room_id_match = re.search(r'房间ID: (\w+)', result)
            if room_id_match:
                self.current_room_id = room_id_match.group(1)
                logger.info(f"AI {self.player_id} 创建并加入房间: {self.current_room_id}")
                return True
            else:
                logger.error(f"无法从结果中提取房间ID: {result}")
                return False
                
        except Exception as e:
            logger.error(f"创建房间失败: {e}")
            return False
    
    async def join_existing_room(self, room_id: str) -> bool:
        """
        加入现有房间
        
        Args:
            room_id: 房间ID
            
        Returns:
            bool: 是否成功
        """
        try:
            result = await self.mcp_client.join_room(room_id, self.player_id)
            logger.info(f"加入房间结果: {result}")
            
            if "成功" in result:
                self.current_room_id = room_id
                logger.info(f"AI {self.player_id} 成功加入房间: {room_id}")
                return True
            else:
                logger.error(f"加入房间失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"加入房间失败: {e}")
            return False
    
    async def find_and_join_available_room(self) -> bool:
        """
        查找并加入可用房间
        
        Returns:
            bool: 是否成功
        """
        try:
            # 获取房间列表
            room_list = await self.mcp_client.get_room_list()
            logger.info(f"房间列表: {room_list}")
            
            # 解析房间列表，查找可加入的房间
            room_id_matches = re.findall(r'房间ID: (\w+).*?\[可加入\]', room_list, re.DOTALL)
            
            if room_id_matches:
                # 随机选择一个可用房间
                room_id = random.choice(room_id_matches)
                return await self.join_existing_room(room_id)
            else:
                logger.info("没有找到可加入的房间")
                return False
                
        except Exception as e:
            logger.error(f"查找房间失败: {e}")
            return False
    
    async def wait_for_game_start(self, max_wait_time: int = 60) -> bool:
        """
        等待游戏开始
        
        Args:
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            bool: 游戏是否开始
        """
        if not self.current_room_id:
            return False
        
        wait_time = 0
        while wait_time < max_wait_time:
            try:
                # 检查游戏状态
                game_info = await self.mcp_client.get_game_info(self.current_room_id)
                
                if "游戏状态: playing" in game_info:
                    logger.info(f"游戏已开始，房间: {self.current_room_id}")
                    self.is_playing = True
                    return True
                elif "游戏状态: waiting" in game_info:
                    # 尝试开始游戏
                    start_result = await self.mcp_client.start_game(self.current_room_id, self.player_id)
                    logger.info(f"尝试开始游戏: {start_result}")
                
                await asyncio.sleep(2)
                wait_time += 2
                
            except Exception as e:
                logger.error(f"等待游戏开始时出错: {e}")
                await asyncio.sleep(1)
                wait_time += 1
        
        logger.warning(f"等待游戏开始超时: {max_wait_time}秒")
        return False
    
    def parse_board_state(self, board_text: str) -> Tuple[List[List[int]], int, bool]:
        """
        解析棋盘状态
        
        Args:
            board_text: 棋盘状态文本
            
        Returns:
            Tuple[List[List[int]], int, bool]: (棋盘, 当前玩家, 是否轮到我)
        """
        board = [[0 for _ in range(15)] for _ in range(15)]
        current_player = 1
        is_my_turn = False
        
        try:
            lines = board_text.split('\n')
            
            # 解析棋盘
            for i, line in enumerate(lines):
                if line.strip().startswith(str(i)) and i < 15:
                    row_data = line.strip().split()[1:]  # 跳过行号
                    for j, cell in enumerate(row_data[:15]):
                        if cell == '●':
                            board[i][j] = 1  # 黑子
                        elif cell == '○':
                            board[i][j] = 2  # 白子
            
            # 解析当前玩家
            if "当前轮到: 黑子" in board_text:
                current_player = 1
            elif "当前轮到: 白子" in board_text:
                current_player = 2
            
            # 判断是否轮到我（简单假设：如果我是第一个玩家就是黑子）
            # 这里需要根据实际游戏信息来判断
            is_my_turn = True  # 简化处理，实际应该检查玩家颜色
            
        except Exception as e:
            logger.error(f"解析棋盘状态失败: {e}")
        
        return board, current_player, is_my_turn
    
    def choose_move(self, board: List[List[int]]) -> Tuple[int, int]:
        """
        选择下棋位置（简单策略）
        
        Args:
            board: 棋盘状态
            
        Returns:
            Tuple[int, int]: 选择的位置 (x, y)
        """
        # 简单策略：
        # 1. 如果中心位置空着，下中心
        # 2. 否则在已有棋子附近随机选择
        # 3. 最后随机选择空位
        
        center_x, center_y = 7, 7
        if board[center_y][center_x] == 0:
            return center_x, center_y
        
        # 找到所有空位
        empty_positions = []
        for y in range(15):
            for x in range(15):
                if board[y][x] == 0:
                    empty_positions.append((x, y))
        
        if not empty_positions:
            return 0, 0  # 不应该发生
        
        # 优先选择已有棋子附近的位置
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
    
    async def play_game(self) -> bool:
        """
        进行游戏
        
        Returns:
            bool: 游戏是否正常结束
        """
        if not self.current_room_id or not self.is_playing:
            return False
        
        logger.info(f"AI {self.player_id} 开始游戏")
        
        try:
            while self.is_playing:
                # 获取棋盘状态
                board_state = await self.mcp_client.get_board_state(self.current_room_id)
                logger.debug(f"棋盘状态:\n{board_state}")
                
                # 检查游戏是否结束
                if "游戏结束" in board_state or "获胜" in board_state or "平局" in board_state:
                    logger.info(f"游戏结束: {board_state}")
                    self.is_playing = False
                    break
                
                # 解析棋盘状态
                board, current_player, is_my_turn = self.parse_board_state(board_state)
                
                if is_my_turn:
                    # 获取AI建议
                    try:
                        suggestions = await self.mcp_client.get_move_suggestions(
                            self.current_room_id, self.player_id, 3
                        )
                        logger.info(f"AI建议: {suggestions}")
                    except Exception as e:
                        logger.warning(f"获取AI建议失败: {e}")
                    
                    # 选择下棋位置
                    x, y = self.choose_move(board)
                    logger.info(f"AI {self.player_id} 选择位置: ({x}, {y})")
                    
                    # 下棋
                    move_result = await self.mcp_client.make_move(
                        self.current_room_id, self.player_id, x, y
                    )
                    logger.info(f"下棋结果: {move_result}")
                    
                    # 检查游戏是否结束
                    if "获胜" in move_result or "平局" in move_result:
                        logger.info(f"游戏结束: {move_result}")
                        self.is_playing = False
                        break
                
                # 等待一段时间再检查
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"游戏过程中出错: {e}")
            return False
        
        return True
    
    async def run(self, room_name: Optional[str] = None, room_id: Optional[str] = None):
        """
        运行AI
        
        Args:
            room_name: 要创建的房间名称
            room_id: 要加入的房间ID
        """
        logger.info(f"启动AI {self.player_id}")
        
        try:
            # 连接或加入房间
            if room_id:
                success = await self.join_existing_room(room_id)
            elif room_name:
                success = await self.create_and_join_room(room_name)
            else:
                success = await self.find_and_join_available_room()
                if not success:
                    # 如果没有可用房间，创建一个
                    success = await self.create_and_join_room(f"AI_{self.player_id}_Room")
            
            if not success:
                logger.error("无法加入或创建房间")
                return
            
            # 等待游戏开始
            if await self.wait_for_game_start():
                # 开始游戏
                await self.play_game()
            else:
                logger.error("游戏未能开始")
            
        except Exception as e:
            logger.error(f"AI运行出错: {e}")
        finally:
            # 清理
            if self.current_room_id:
                try:
                    await self.mcp_client.leave_room(self.current_room_id, self.player_id)
                except Exception as e:
                    logger.error(f"离开房间失败: {e}")


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    # 创建AI实例
    ai = SimpleGomokuAI("simple_ai_1")
    
    async with ai:
        await ai.run(room_name="AI测试房间")


if __name__ == "__main__":
    asyncio.run(main())
