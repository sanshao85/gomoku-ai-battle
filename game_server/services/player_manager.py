"""
玩家管理服务
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..models.player import Player, PlayerStatus


class PlayerManager:
    """玩家管理器"""
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.cleanup_interval = timedelta(hours=24)  # 清理间隔
    
    def create_player(self, player_id: str, name: str) -> Player:
        """
        创建新玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称
            
        Returns:
            Player: 创建的玩家对象
        """
        player = Player(player_id=player_id, name=name)
        self.players[player_id] = player
        return player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """获取玩家"""
        return self.players.get(player_id)
    
    def get_or_create_player(self, player_id: str, name: Optional[str] = None) -> Player:
        """
        获取或创建玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称（如果需要创建）
            
        Returns:
            Player: 玩家对象
        """
        player = self.get_player(player_id)
        if not player:
            player_name = name or f"Player_{player_id[:8]}"
            player = self.create_player(player_id, player_name)
        return player
    
    def delete_player(self, player_id: str) -> bool:
        """删除玩家"""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def list_players(self, status: Optional[PlayerStatus] = None) -> List[Player]:
        """
        获取玩家列表
        
        Args:
            status: 过滤玩家状态
            
        Returns:
            List[Player]: 玩家列表
        """
        players = list(self.players.values())
        
        if status:
            players = [player for player in players if player.status == status]
        
        # 按最后在线时间排序
        players.sort(key=lambda p: p.last_seen, reverse=True)
        return players
    
    def set_player_online(self, player_id: str) -> bool:
        """设置玩家在线"""
        player = self.get_player(player_id)
        if player:
            player.set_online()
            return True
        return False
    
    def set_player_offline(self, player_id: str) -> bool:
        """设置玩家离线"""
        player = self.get_player(player_id)
        if player:
            player.set_offline()
            return True
        return False
    
    def player_join_room(self, player_id: str, room_id: str) -> bool:
        """玩家加入房间"""
        player = self.get_player(player_id)
        if player:
            player.join_room(room_id)
            return True
        return False
    
    def player_leave_room(self, player_id: str) -> bool:
        """玩家离开房间"""
        player = self.get_player(player_id)
        if player:
            player.leave_room()
            return True
        return False
    
    def player_start_game(self, player_id: str, game_id: str) -> bool:
        """玩家开始游戏"""
        player = self.get_player(player_id)
        if player:
            player.start_game(game_id)
            return True
        return False
    
    def player_finish_game(self, player_id: str, won: bool = False, draw: bool = False, 
                          moves: int = 0, game_time: float = 0.0) -> bool:
        """玩家结束游戏"""
        player = self.get_player(player_id)
        if player:
            player.finish_game(won, draw, moves, game_time)
            return True
        return False
    
    def player_make_move(self, player_id: str) -> bool:
        """记录玩家下棋"""
        player = self.get_player(player_id)
        if player:
            player.make_move()
            return True
        return False
    
    def get_online_players(self) -> List[Player]:
        """获取在线玩家列表"""
        return [player for player in self.players.values() 
                if player.status in [PlayerStatus.ONLINE, PlayerStatus.IN_GAME, PlayerStatus.SPECTATING]]
    
    def get_available_players(self) -> List[Player]:
        """获取可用玩家列表（在线且不在房间中）"""
        return [player for player in self.players.values() if player.is_available()]
    
    def get_players_in_room(self, room_id: str) -> List[Player]:
        """获取指定房间中的玩家"""
        return [player for player in self.players.values() 
                if player.current_room_id == room_id]
    
    def get_players_in_game(self, game_id: str) -> List[Player]:
        """获取指定游戏中的玩家"""
        return [player for player in self.players.values() 
                if player.current_game_id == game_id]
    
    def update_player_preferences(self, player_id: str, preferences: dict) -> bool:
        """更新玩家偏好设置"""
        player = self.get_player(player_id)
        if player:
            player.preferences.update(preferences)
            return True
        return False
    
    def get_player_stats(self, player_id: str) -> Optional[dict]:
        """获取玩家统计信息"""
        player = self.get_player(player_id)
        if player:
            return player.get_detailed_stats()
        return None
    
    def get_leaderboard(self, limit: int = 10, sort_by: str = "win_rate") -> List[dict]:
        """
        获取排行榜
        
        Args:
            limit: 返回数量限制
            sort_by: 排序字段 (win_rate, games_played, games_won)
            
        Returns:
            List[dict]: 排行榜数据
        """
        players = [player for player in self.players.values() 
                  if player.stats.games_played > 0]
        
        # 根据排序字段排序
        if sort_by == "win_rate":
            players.sort(key=lambda p: p.stats.win_rate, reverse=True)
        elif sort_by == "games_played":
            players.sort(key=lambda p: p.stats.games_played, reverse=True)
        elif sort_by == "games_won":
            players.sort(key=lambda p: p.stats.games_won, reverse=True)
        else:
            players.sort(key=lambda p: p.stats.win_rate, reverse=True)
        
        # 构建排行榜数据
        leaderboard = []
        for i, player in enumerate(players[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "player_id": player.player_id,
                "name": player.name,
                "win_rate": player.stats.win_rate,
                "games_played": player.stats.games_played,
                "games_won": player.stats.games_won,
                "games_lost": player.stats.games_lost
            })
        
        return leaderboard
    
    def cleanup_inactive_players(self):
        """清理长时间不活跃的玩家"""
        current_time = datetime.now()
        players_to_delete = []
        
        for player_id, player in self.players.items():
            # 删除长时间离线且无游戏记录的玩家
            if (player.status == PlayerStatus.OFFLINE and 
                player.stats.games_played == 0 and
                current_time - player.last_seen > self.cleanup_interval):
                players_to_delete.append(player_id)
        
        for player_id in players_to_delete:
            self.delete_player(player_id)
    
    def get_statistics(self) -> dict:
        """获取玩家管理统计信息"""
        total_players = len(self.players)
        online_players = len(self.get_online_players())
        available_players = len(self.get_available_players())
        
        # 统计游戏数据
        total_games = sum(player.stats.games_played for player in self.players.values())
        active_players = len([p for p in self.players.values() if p.stats.games_played > 0])
        
        return {
            "total_players": total_players,
            "online_players": online_players,
            "available_players": available_players,
            "active_players": active_players,
            "total_games": total_games
        }
