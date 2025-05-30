# 五子棋AI对战项目

基于MCP (Model Context Protocol) 的五子棋AI对战平台，让AI通过MCP接口进行五子棋对战。

## ✨ 项目亮点

- 🤖 **真实AI对战**: 支持Claude等AI通过MCP协议直接对战
- 👁️ **实时观战**: 精美的Web界面实时显示对战过程
- 🎯 **完整游戏逻辑**: 标准15x15五子棋规则，支持胜负判断
- 📊 **数据统计**: 玩家排行榜、游戏历史、统计分析
- 🔧 **易于扩展**: 模块化设计，支持自定义AI算法

## 🎮 演示效果

**已成功实现Claude AI vs Claude AI对战！**

- ✅ 两个AI实例同时连接
- ✅ 实时下棋和状态更新
- ✅ Web界面完美显示棋盘
- ✅ 游戏逻辑完全正确

## 项目结构

```
gomoku-ai-battle/
├── README.md                    # 项目说明
├── requirements.txt             # Python依赖
├── GOMOKU_AI_BATTLE_PROJECT.md  # 详细项目文档
├──
├── game_server/                 # 游戏服务端
│   ├── main.py                  # FastAPI应用入口
│   ├── config.py                # 配置文件
│   ├── models/                  # 数据模型
│   ├── services/                # 业务逻辑
│   └── api/                     # API路由
│
├── mcp_server/                  # MCP服务器
│   ├── gomoku_mcp.py            # MCP服务器主文件
│   ├── config.py                # MCP配置
│   └── tools/                   # MCP工具
│
├── ai_client/                   # AI客户端
│   ├── mcp_client.py            # MCP客户端封装
│   └── simple_ai.py             # 简单AI实现
│
├── scripts/                     # 脚本工具
│   ├── start_game_server.py     # 启动游戏服务端
│   ├── start_mcp_server.py      # 启动MCP服务器
│   └── run_ai_battle.py         # 运行AI对战
│
└── tests/                       # 测试代码
    ├── test_game_logic.py       # 游戏逻辑测试
    └── test_mcp_server.py       # MCP服务器测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动游戏服务端

```bash
python scripts/start_game_server.py
```

游戏服务端将在 `http://localhost:8000` 启动：
- 🌐 **Web界面**: http://localhost:8000
- 📚 **API文档**: http://localhost:8000/docs
- 🎮 **观战台**: http://localhost:8000/static/index.html

### 3. 配置Claude Desktop

在Claude Desktop配置文件中添加MCP服务器：

**配置文件位置:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

**配置内容:**
```json
{
  "mcpServers": {
    "gomoku-mcp-server": {
      "command": "python",
      "args": ["D:\\your\\project\\path\\scripts\\start_mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "MCP_GAME_SERVER_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 4. 启动MCP服务器

```bash
python scripts/start_mcp_server.py
```

### 5. 重启Claude Desktop

完全关闭并重新打开Claude Desktop，让配置生效。

### 6. 开始AI对战！

现在Claude AI可以直接通过MCP工具进行五子棋对战：

```
我想创建一个五子棋房间开始对战
```

或者运行示例AI客户端：

```bash
# 运行2个AI对战
python scripts/run_ai_battle.py --mode battle --ai-count 2

# 让AI加入指定房间
python scripts/run_ai_battle.py --mode join --room-id room_12345 --ai-id AI_Test
```

## 使用说明

### 游戏服务端API

游戏服务端提供REST API接口：

- `POST /api/v1/rooms` - 创建房间
- `GET /api/v1/rooms` - 获取房间列表
- `POST /api/v1/rooms/{room_id}/join` - 加入房间
- `POST /api/v1/rooms/{room_id}/move` - 下棋
- `GET /api/v1/rooms/{room_id}/game` - 获取游戏状态

### 🛠️ MCP工具

MCP服务器提供以下工具供AI调用：

**游戏操作工具：**
- `create_room(creator_id, room_name)` - 创建房间
- `join_room(room_id, player_id)` - 加入房间
- `leave_room(room_id, player_id)` - 离开房间
- `start_game(room_id, player_id)` - 开始游戏
- `make_move(room_id, player_id, x, y)` - 下棋
- `get_move_suggestions(room_id, player_id, count)` - 获取下棋建议
- `get_leaderboard(limit, sort_by)` - 获取排行榜
- `get_server_status()` - 获取服务器状态

**信息查询资源：**
- `board_state://{room_id}` - 获取棋盘状态
- `game_info://{room_id}` - 获取游戏信息
- `gomoku://room_list` - 获取房间列表
- `player_info://{player_id}` - 获取玩家信息

### 🎯 AI对战示例

**创建房间并开始对战：**
```
Claude: 我想创建一个五子棋房间
AI: 成功创建房间 'Claude的AI对战房间'，房间ID: room_3b93ac16

Claude: 让另一个AI加入房间
AI: 成功加入房间 room_3b93ac16

Claude: 开始游戏并下第一步棋在中心位置
AI: 下棋成功

Claude: 查看当前棋盘状态
AI: [显示15x15棋盘，中心有黑子●]
```

**实际演示结果：**
- ✅ 成功创建房间：`room_3b93ac16`
- ✅ 两个AI同时对战：`Claude_AI_1 vs Claude_AI_2`
- ✅ 已进行7步对战，游戏进行中
- ✅ Web界面实时显示棋盘状态

### AI客户端开发

使用 `GomokuMCPClient` 类可以轻松开发AI客户端：

```python
from ai_client.mcp_client import GomokuMCPClient

async def my_ai():
    async with GomokuMCPClient() as client:
        # 创建房间
        result = await client.create_room("my_ai", "测试房间")

        # 获取棋盘状态
        board = await client.get_board_state("room_id")

        # 下棋
        result = await client.make_move("room_id", "my_ai", 7, 7)
```

## 配置

### 游戏服务端配置

在 `game_server/config.py` 中可以配置：

- 服务器地址和端口
- 棋盘大小和获胜条件
- 房间和玩家限制
- 日志级别

### MCP服务器配置

在 `mcp_server/config.py` 中可以配置：

- 游戏服务器连接地址
- 连接超时和重试设置
- AI建议数量限制
- 日志级别

## 开发和测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_game_logic.py
pytest tests/test_mcp_server.py
```

### 开发模式

```bash
# 启动游戏服务端（开发模式）
python scripts/start_game_server.py --debug --reload

# 启动MCP服务器（调试模式）
python scripts/start_mcp_server.py --debug --log-level DEBUG
```

## 🏗️ 架构说明

### 系统架构

```
┌─────────────┐    MCP     ┌─────────────┐    HTTP    ┌─────────────┐
│   Claude AI  │ ←────────→ │  MCP 服务器   │ ←────────→ │  游戏服务端   │
│  (黑子玩家)   │            │             │            │             │
└─────────────┘            └─────────────┘            └─────────────┘
                                  ↑                           ↑
                                  │ MCP                       │ HTTP
                                  ↓                           ↓
┌─────────────┐            ┌─────────────┐            ┌─────────────┐
│   Claude AI  │ ←────────→ │  MCP 服务器   │            │   Web 观战台  │
│  (白子玩家)   │            │   (同一个)    │            │             │
└─────────────┘            └─────────────┘            └─────────────┘
```

### 数据流

1. **AI连接**: Claude AI通过MCP协议连接到MCP服务器
2. **指令转换**: MCP服务器将AI指令转换为HTTP API调用
3. **游戏处理**: 游戏服务端处理五子棋逻辑并更新状态
4. **结果返回**: MCP服务器将游戏结果返回给AI
5. **实时观战**: Web界面实时显示棋盘状态

### 技术栈

- **游戏服务端**: Python + FastAPI + Pydantic + Uvicorn
- **MCP服务器**: MCP Python SDK (FastMCP) + httpx
- **Web界面**: HTML5 + CSS3 + JavaScript + 实时刷新
- **AI客户端**: Claude Desktop + MCP协议
- **通信协议**: HTTP REST API + MCP stdio + WebSocket(可选)

### 核心特性

- 🔄 **实时同步**: 游戏状态实时同步到所有客户端
- 🎯 **精确控制**: 坐标系统(0-14)，支持精确下棋
- 🛡️ **错误处理**: 完善的异常处理和重试机制
- 📊 **状态管理**: 完整的游戏状态和房间管理
- 🎮 **多模式**: 支持AI vs AI、观战、统计等多种模式

## 🎉 成功案例

### 实际对战记录

**房间信息:**
- 房间ID: `room_3b93ac16`
- 房间名: "Claude的AI对战房间"
- 对战双方: `Claude_AI_1` (黑子) vs `Claude_AI_2` (白子)

**对战进程:**
1. ✅ Claude_AI_1 创建房间
2. ✅ Claude_AI_2 成功加入
3. ✅ 游戏自动开始
4. ✅ 已进行7步对战
5. ✅ Web界面实时显示

**棋盘状态:**
```
当前棋盘 (第7步后):
   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
 0  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
 1  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·
 ...
 7  ·  ·  ·  ·  ○  ●  ●  ●  ○  ○  ·  ·  ·  ·  ·
 8  ·  ·  ·  ·  ·  ·  ·  ·  ●  ·  ·  ·  ·  ·  ·
 ...
```

**技术验证:**
- ✅ MCP协议通信正常
- ✅ 游戏逻辑完全正确
- ✅ Web界面实时更新
- ✅ 多AI并发支持
- ✅ 错误处理机制有效

## 🚀 扩展功能

项目支持以下扩展：

- 🧠 更复杂的AI算法 (已有基础框架)
- 👁️ Web界面观战 (✅ 已实现)
- 📹 游戏回放功能
- 🎲 多种棋类支持 (象棋、围棋等)
- 💾 数据库持久化
- 🔐 用户认证系统
- 📊 高级统计分析
- 🏆 AI算法评分系统
- 🌐 多人在线对战
- 📱 移动端支持

## 🔧 故障排除

### 常见问题及解决方案

1. **MCP服务器无法启动**
   ```
   错误: URL validation error
   解决: 检查资源URI格式，确保使用有效的URL scheme
   ```

2. **HTTP 307重定向错误**
   ```
   错误: 游戏服务器错误: 307 Temporary Redirect
   解决: 在httpx请求中添加 follow_redirects=True
   ```

3. **Claude Desktop看不到MCP工具**
   ```
   问题: 配置文件修改后工具不显示
   解决:
   - 确保配置文件路径正确
   - 完全重启Claude Desktop
   - 检查MCP服务器是否启动
   ```

4. **游戏服务端连接失败**
   ```
   错误: 连接游戏服务器失败
   解决:
   - 确保游戏服务端在 http://localhost:8000 运行
   - 检查端口是否被占用
   - 查看防火墙设置
   ```

5. **下棋失败**
   ```
   错误: 无效的下棋位置
   解决:
   - 确保坐标在0-14范围内
   - 检查位置是否已被占用
   - 确认轮到当前玩家
   ```

### 调试步骤

1. **验证服务端状态**
   ```bash
   curl http://localhost:8000/api/v1/health
   # 应返回: {"status":"healthy",...}
   ```

2. **检查MCP连接**
   ```bash
   python scripts/start_mcp_server.py --debug
   # 查看详细日志输出
   ```

3. **测试API调用**
   ```bash
   curl http://localhost:8000/api/v1/rooms/
   # 应返回房间列表JSON
   ```

### 日志查看

```bash
# 查看游戏服务端日志
python scripts/start_game_server.py --log-level DEBUG

# 查看MCP服务器日志
python scripts/start_mcp_server.py --debug --log-level DEBUG

# 查看AI对战日志
tail -f ai_battle.log
```

### 成功验证清单

- ✅ 游戏服务端启动: `http://localhost:8000`
- ✅ MCP服务器启动: 显示"启动五子棋MCP服务器"
- ✅ Claude Desktop重启: 配置生效
- ✅ MCP工具可见: 在Claude中可以调用工具
- ✅ 创建房间成功: 返回房间ID
- ✅ 下棋成功: 返回"下棋成功"
- ✅ Web界面显示: 棋盘实时更新

## 贡献

欢迎提交Issue和Pull Request来改进项目！

## 许可证

MIT License
