#!/usr/bin/env python3
"""
智能AI玩家 - 演示如何使用MCP工具进行智能等待和下棋
"""
import asyncio
import random
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client.mcp_client import GomokuMCPClient


class SmartAIPlayer:
    """智能AI玩家类"""
    
    def __init__(self, player_id: str, room_id: str):
        """
        初始化智能AI玩家
        
        Args:
            player_id: AI玩家ID
            room_id: 房间ID
        """
        self.player_id = player_id
        self.room_id = room_id
        self.client = GomokuMCPClient()
        self.is_playing = False
    
    async def __aenter__(self):
        await self.client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()
    
    def calculate_wait_time(self) -> int:
        """
        计算智能等待时间
        
        Returns:
            等待时间(秒)，范围20-60秒
        """
        # 随机等待20-60秒，模拟AI思考时间
        return random.randint(20, 60)
    
    def choose_move_position(self, board_state: str) -> tuple:
        """
        根据棋盘状态选择下棋位置
        
        Args:
            board_state: 棋盘状态字符串
            
        Returns:
            (x, y): 选择的位置
        """
        # 简单策略：优先选择中心区域
        center_positions = [
            (7, 7), (7, 8), (8, 7), (8, 8),  # 中心4格
            (6, 6), (6, 7), (6, 8), (6, 9),  # 周围一圈
            (7, 6), (7, 9), (8, 6), (8, 9),
            (9, 6), (9, 7), (9, 8), (9, 9)
        ]
        
        # 检查哪些位置是空的
        available_positions = []
        for x, y in center_positions:
            # 简单检查：如果棋盘状态中没有提到这个位置，认为是空的
            pos_str = f"({x}, {y})"
            if pos_str not in board_state:
                available_positions.append((x, y))
        
        if available_positions:
            return random.choice(available_positions)
        else:
            # 如果中心区域都满了，随机选择
            return random.randint(0, 14), random.randint(0, 14)
    
    async def play_turn(self):
        """
        执行一轮智能下棋
        
        Returns:
            bool: 是否成功下棋
        """
        try:
            print(f"🤖 {self.player_id} 开始分析局面...")
            
            # 1. 检查是否轮到自己
            turn_result = await self.client.check_my_turn(self.room_id, self.player_id)
            print(f"📋 轮次检查: {turn_result}")
            
            if "轮到您下棋" not in turn_result:
                print(f"⏳ 还没轮到我，需要等待...")
                return False
            
            # 2. 获取剩余时间
            try:
                time_result = await self.client.get_remaining_time(self.room_id, self.player_id)
                print(f"⏰ 剩余时间: {time_result}")
            except Exception as e:
                print(f"⚠️ 获取时间失败: {e}")
            
            # 3. 获取棋盘状态
            board_state = await self.client.get_board_state(self.room_id)
            print(f"📊 棋盘状态已获取")
            
            # 4. 获取AI建议（可选）
            try:
                suggestions = await self.client.get_move_suggestions(
                    self.room_id, self.player_id, 3
                )
                print(f"💡 AI建议: {suggestions}")
            except Exception as e:
                print(f"⚠️ 获取建议失败: {e}")
            
            # 5. 选择下棋位置
            x, y = self.choose_move_position(board_state)
            print(f"🎯 选择位置: ({x}, {y})")
            
            # 6. 下棋
            move_result = await self.client.make_move(self.room_id, self.player_id, x, y)
            print(f"✅ 下棋结果: {move_result}")
            
            # 检查是否获胜或游戏结束
            if "获胜" in move_result or "平局" in move_result or "游戏结束" in move_result:
                print(f"🏁 游戏结束: {move_result}")
                self.is_playing = False
                return True
            
            return True
            
        except Exception as e:
            print(f"❌ 下棋失败: {e}")
            return False
    
    async def smart_play_loop(self):
        """
        智能游戏循环
        """
        print(f"🎮 {self.player_id} 开始智能对战模式")
        self.is_playing = True
        
        while self.is_playing:
            try:
                # 1. 智能等待
                wait_time = self.calculate_wait_time()
                print(f"🧠 {self.player_id} 思考中，等待 {wait_time} 秒...")
                
                # 使用MCP工具等待
                wait_result = await self.client.wait_for_turn(
                    self.room_id, self.player_id, wait_time
                )
                print(f"⏰ 等待结果: {wait_result}")
                
                # 2. 尝试下棋
                success = await self.play_turn()
                
                if not success:
                    # 如果没有成功下棋，短暂等待后重试
                    print(f"⏳ 等待5秒后重试...")
                    await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print(f"🛑 {self.player_id} 手动停止")
                break
            except Exception as e:
                print(f"❌ 游戏循环错误: {e}")
                await asyncio.sleep(10)  # 错误后等待10秒
        
        print(f"🏁 {self.player_id} 结束游戏")


async def demo_smart_ai():
    """演示智能AI对战"""
    
    # 创建房间
    print("🏠 创建演示房间...")
    async with GomokuMCPClient() as client:
        room_result = await client.create_room("SmartAI_Demo", "智能AI演示房间")
        print(f"房间创建结果: {room_result}")
        
        # 提取房间ID（简单解析）
        if "room_" in room_result:
            room_id = room_result.split("room_")[1].split("'")[0]
            room_id = "room_" + room_id
            print(f"房间ID: {room_id}")
        else:
            print("❌ 无法获取房间ID")
            return
    
    # 创建两个智能AI
    ai1 = SmartAIPlayer("SmartAI_1", room_id)
    ai2 = SmartAIPlayer("SmartAI_2", room_id)
    
    print("🤖 启动双AI智能对战...")
    
    try:
        # 让第二个AI加入房间
        async with ai2:
            join_result = await ai2.client.join_room(room_id, "SmartAI_2")
            print(f"AI2加入结果: {join_result}")
        
        # 并行运行两个智能AI
        async with ai1, ai2:
            await asyncio.gather(
                ai1.smart_play_loop(),
                ai2.smart_play_loop()
            )
    
    except Exception as e:
        print(f"❌ 演示失败: {e}")


if __name__ == "__main__":
    print("🎯 五子棋智能AI演示")
    print("特性:")
    print("- 智能等待20-60秒")
    print("- 自动检查轮次")
    print("- 获取剩余时间")
    print("- AI建议辅助")
    print("- 智能位置选择")
    print("- 2分钟超时保护")
    print()
    
    try:
        asyncio.run(demo_smart_ai())
    except KeyboardInterrupt:
        print("\n🛑 演示已停止")
    except Exception as e:
        print(f"\n❌ 演示错误: {e}")
