#!/usr/bin/env python3
"""
启动MCP服务器脚本
"""
import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.config import mcp_settings


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="启动五子棋MCP服务器")
    parser.add_argument("--game-server", default=mcp_settings.game_server_url, 
                       help="游戏服务器URL")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--log-level", default=mcp_settings.log_level, 
                       help="日志级别")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 更新配置
    if args.game_server != mcp_settings.game_server_url:
        mcp_settings.game_server_url = args.game_server
    
    if args.debug:
        mcp_settings.debug = True
        mcp_settings.log_level = "DEBUG"
    
    if args.log_level != mcp_settings.log_level:
        mcp_settings.log_level = args.log_level
    
    if args.verbose:
        mcp_settings.verbose = True
    
    print(f"启动五子棋MCP服务器...")
    print(f"服务器名称: {mcp_settings.server_name}")
    print(f"版本: {mcp_settings.server_version}")
    print(f"游戏服务器: {mcp_settings.game_server_url}")
    print(f"调试模式: {mcp_settings.debug}")
    print(f"日志级别: {mcp_settings.log_level}")
    print(f"详细输出: {mcp_settings.verbose}")
    print()
    print("MCP服务器将通过stdio与客户端通信...")
    print("使用 Ctrl+C 停止服务器")
    print()
    
    try:
        # 导入并运行MCP服务器
        from mcp_server.gomoku_mcp import main as mcp_main
        mcp_main()
    except KeyboardInterrupt:
        print("\nMCP服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
