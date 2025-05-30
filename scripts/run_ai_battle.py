#!/usr/bin/env python3
"""
运行AI对战脚本
"""
import sys
import os
import asyncio
import logging
import argparse
from typing import List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client.simple_ai import SimpleGomokuAI


async def run_single_ai(ai_id: str, room_name: str = None, room_id: str = None):
    """
    运行单个AI
    
    Args:
        ai_id: AI标识
        room_name: 房间名称
        room_id: 房间ID
    """
    logger = logging.getLogger(f"AI_{ai_id}")
    logger.info(f"启动AI {ai_id}")
    
    try:
        ai = SimpleGomokuAI(f"AI_{ai_id}")
        async with ai:
            await ai.run(room_name=room_name, room_id=room_id)
    except Exception as e:
        logger.error(f"AI {ai_id} 运行失败: {e}")


async def run_ai_battle(ai_count: int = 2, room_name: str = "AI对战房间"):
    """
    运行AI对战
    
    Args:
        ai_count: AI数量
        room_name: 房间名称
    """
    logger = logging.getLogger("AIBattle")
    logger.info(f"启动 {ai_count} 个AI进行对战")
    
    # 创建AI任务
    tasks = []
    
    # 第一个AI创建房间
    task1 = asyncio.create_task(
        run_single_ai("1", room_name=room_name)
    )
    tasks.append(task1)
    
    # 等待一段时间让第一个AI创建房间
    await asyncio.sleep(3)
    
    # 其他AI加入房间（这里简化处理，实际应该获取房间ID）
    for i in range(2, ai_count + 1):
        task = asyncio.create_task(
            run_single_ai(str(i))
        )
        tasks.append(task)
        await asyncio.sleep(1)  # 错开启动时间
    
    # 等待所有AI完成
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"AI对战过程中出错: {e}")
    
    logger.info("AI对战结束")


async def run_ai_vs_room(ai_id: str, room_id: str):
    """
    让AI加入指定房间
    
    Args:
        ai_id: AI标识
        room_id: 房间ID
    """
    logger = logging.getLogger(f"AI_{ai_id}")
    logger.info(f"AI {ai_id} 加入房间 {room_id}")
    
    try:
        ai = SimpleGomokuAI(f"AI_{ai_id}")
        async with ai:
            await ai.run(room_id=room_id)
    except Exception as e:
        logger.error(f"AI {ai_id} 运行失败: {e}")


def setup_logging(log_level: str = "INFO"):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ai_battle.log')
        ]
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行五子棋AI对战")
    parser.add_argument("--mode", choices=["battle", "join"], default="battle",
                       help="运行模式: battle=AI对战, join=加入房间")
    parser.add_argument("--ai-count", type=int, default=2,
                       help="AI数量（battle模式）")
    parser.add_argument("--room-name", default="AI对战房间",
                       help="房间名称（battle模式）")
    parser.add_argument("--room-id", help="房间ID（join模式）")
    parser.add_argument("--ai-id", default="1", help="AI标识（join模式）")
    parser.add_argument("--log-level", default="INFO",
                       help="日志级别")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger("Main")
    
    try:
        if args.mode == "battle":
            logger.info(f"启动AI对战模式，AI数量: {args.ai_count}")
            asyncio.run(run_ai_battle(args.ai_count, args.room_name))
        elif args.mode == "join":
            if not args.room_id:
                logger.error("join模式需要指定 --room-id")
                sys.exit(1)
            logger.info(f"AI {args.ai_id} 加入房间 {args.room_id}")
            asyncio.run(run_ai_vs_room(args.ai_id, args.room_id))
        
    except KeyboardInterrupt:
        logger.info("用户中断，停止AI对战")
    except Exception as e:
        logger.error(f"运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
