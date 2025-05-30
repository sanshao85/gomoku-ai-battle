#!/usr/bin/env python3
"""
启动游戏服务端脚本
"""
import sys
import os
import uvicorn
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_server.config import settings


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动五子棋游戏服务端")
    parser.add_argument("--host", default=settings.host, help="服务器主机地址")
    parser.add_argument("--port", type=int, default=settings.port, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="启用自动重载")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--log-level", default=settings.log_level, help="日志级别")
    
    args = parser.parse_args()
    
    print(f"启动五子棋游戏服务端...")
    print(f"地址: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    print(f"调试模式: {args.debug}")
    print(f"自动重载: {args.reload}")
    
    try:
        uvicorn.run(
            "game_server.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload or args.debug,
            log_level=args.log_level.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
