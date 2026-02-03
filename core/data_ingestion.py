"""
Nexus Commander - Data Ingestion Module
Handles loading, parsing, and preprocessing GRID match data
"""

import json
import glob
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path


@dataclass
class MatchMetadata:
    """Match metadata structure"""
    match_id: str
    series_id: Optional[str] = None
    tournament: str = "LCK Spring 2024"
    team1_id: str = ""
    team1_name: str = ""
    team2_id: str = ""
    team2_name: str = ""
    game_number: int = 1
    winner_team_id: Optional[str] = None
    duration_seconds: int = 0
    timestamp: Optional[datetime] = None


@dataclass
class DraftData:
    """Champion draft data"""
    bans: List[Dict[str, Any]] = field(default_factory=list)
    picks: List[Dict[str, Any]] = field(default_factory=list)
    sequence: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_team_bans(self, team_id: str) -> List[str]:
        """Get all bans for a specific team"""
        return [b['champion'] for b in self.bans if b['team_id'] == team_id]
    
    def get_team_picks(self, team_id: str) -> List[str]:
        """Get all picks for a specific team"""
        return [p['champion'] for p in self.picks if p['team_id'] == team_id]


@dataclass
class PlayerStats:
    """Player performance statistics"""
    player_id: str = ""
    player_name: str = ""
    team_id: str = ""
    champion: str = ""
    role: str = ""
    
    # Combat stats
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    damage_dealt: int = 0
    damage_taken: int = 0
    healing: int = 0
    
    # Economy
    gold_earned: int = 0
    cs: int = 0  # Creep score
    
    # Vision
    wards_placed: int = 0
    wards_destroyed: int = 0
    vision_score: int = 0
    
    # Objectives
    turret_kills: int = 0
    inhibitor_kills: int = 0
    
    @property
    def kda(self) -> float:
        """Calculate KDA ratio"""
        if self.deaths == 0:
            return float(self.kills + self.assists)
        return (self.kills + self.assists) / self.deaths


@dataclass
class TeamStats:
    """Team aggregate statistics"""
    team_id: str = ""
    team_name: str = ""
    
    # Combat
    total_kills: int = 0
    total_deaths: int = 0
    total_assists: int = 0
    
    # Objectives
    baron_kills: int = 0
    dragon_kills: int = 0
    herald_kills: int = 0
    tower_kills: int = 0
    inhibitor_kills: int = 0
    
    # Economy
    total_gold: int = 0
    gold_per_minute: float = 0.0
    
    # Vision
    wards_placed: int = 0
    wards_destroyed: int = 0
    
    # Result
    win: bool = False
    
    # Timeline data
    gold_timeline: List[int] = field(default_factory=list)
    kill_timeline: List[int] = field(default_factory=list)


class GridDataParser:
    """Parser for GRID match JSON data"""
    
    def __init__(self, data_dir: str = "/mnt/user-data/uploads"):
        self.data_dir = Path(data_dir)
    
    def load_all_matches(self) -> List[Dict[str, Any]]:
        """Load all match JSON files"""
        json_files = sorted(self.data_dir.glob("matchID_*.json"))
        matches = []
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    matches.append(data)
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
        
        return matches
    
    def parse_match(self, match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a single match into structured format"""
        try:
            series_state = match_data.get('seriesState', {})
            games = series_state.get('games', [])
            
            if not games:
                return None
            
            # Parse first game (main game)
            game = games[0]
            
            # Extract metadata
            metadata = self._extract_metadata(match_data, game)
            
            # Extract draft data
            draft = self._extract_draft(game)
            
            # Extract player stats
            player_stats = self._extract_player_stats(game)
            
            # Extract team stats
            team_stats = self._extract_team_stats(game, metadata)
            
            # Extract timeline events
            timeline = self._extract_timeline(game)
            
            return {
                'metadata': metadata,
                'draft': draft,
                'player_stats': player_stats,
                'team_stats': team_stats,
                'timeline': timeline,
                'raw_data': game
            }
        
        except Exception as e:
            print(f"Error parsing match: {e}")
            return None
    
    def _extract_metadata(self, match_data: Dict, game: Dict) -> MatchMetadata:
        """Extract match metadata"""
        # Parse team info from filename or data
        series_state = match_data.get('seriesState', {})
        
        # Try to extract from teams
        teams = game.get('teams', [])
        
        team1_id, team1_name = "", ""
        team2_id, team2_name = "", ""
        winner_id = None
        
        if len(teams) >= 2:
            team1 = teams[0]
            team2 = teams[1]
            
            team1_id = str(team1.get('id', ''))
            team1_name = team1.get('name', 'Team 1')
            team2_id = str(team2.get('id', ''))
            team2_name = team2.get('name', 'Team 2')
            
            # Determine winner from segments or finished state
            # For now, extract from first available source
            if 'win' in team1:
                if team1.get('win', False):
                    winner_id = team1_id
                elif team2.get('win', False):
                    winner_id = team2_id
        
        # Get duration
        clock = game.get('clock', {})
        duration = clock.get('currentSeconds', 0)
        
        return MatchMetadata(
            match_id=game.get('id', 'unknown'),
            team1_id=team1_id,
            team1_name=team1_name,
            team2_id=team2_id,
            team2_name=team2_name,
            winner_team_id=winner_id,
            duration_seconds=duration
        )
    
    def _extract_draft(self, game: Dict) -> DraftData:
        """Extract draft/pick-ban data"""
        draft_actions = game.get('draftActions', [])
        
        bans = []
        picks = []
        sequence = []
        
        for action in draft_actions:
            champion_name = action.get('draftable', {}).get('name', '')
            team_id = action.get('drafter', {}).get('id', '')
            action_type = action.get('type', '')
            seq_num = action.get('sequenceNumber', 0)
            
            entry = {
                'champion': champion_name,
                'team_id': team_id,
                'sequence': int(seq_num),
                'type': action_type
            }
            
            sequence.append(entry)
            
            if action_type == 'ban':
                bans.append(entry)
            elif action_type == 'pick':
                picks.append(entry)
        
        return DraftData(bans=bans, picks=picks, sequence=sequence)
    
    def _extract_player_stats(self, game: Dict) -> List[PlayerStats]:
        """Extract player statistics"""
        player_states = game.get('playerStates', [])
        players = []
        
        for pstate in player_states:
            stats = PlayerStats()
            
            # Basic info
            stats.player_id = pstate.get('id', '')
            stats.player_name = pstate.get('name', '')
            stats.team_id = pstate.get('teamId', '')
            
            # Champion
            champion = pstate.get('championState', {})
            stats.champion = champion.get('name', '')
            
            # Role (inferred from position)
            stats.role = pstate.get('role', 'unknown')
            
            # Combat stats
            stats.kills = pstate.get('kills', 0)
            stats.deaths = pstate.get('deaths', 0)
            stats.assists = pstate.get('assists', 0)
            stats.damage_dealt = pstate.get('totalDamageDealtToChampions', 0)
            stats.damage_taken = pstate.get('totalDamageTaken', 0)
            
            # Economy
            stats.gold_earned = pstate.get('goldEarned', 0)
            stats.cs = pstate.get('creepScore', 0)
            
            # Vision
            stats.wards_placed = pstate.get('wardsPlaced', 0)
            stats.wards_destroyed = pstate.get('wardsDestroyed', 0)
            stats.vision_score = pstate.get('visionScore', 0)
            
            players.append(stats)
        
        return players
    
    def _extract_team_stats(self, game: Dict, metadata: MatchMetadata) -> List[TeamStats]:
        """Extract team statistics"""
        teams = game.get('teams', [])
        team_stats_list = []
        
        for team_data in teams:
            stats = TeamStats()
            
            stats.team_id = str(team_data.get('id', ''))
            stats.team_name = team_data.get('name', '')
            
            # Get statistics from the team data
            # GRID API structure may have stats nested differently
            team_stats = team_data.get('stats', {})
            
            # Objectives - try different possible field names
            stats.baron_kills = team_stats.get('baronKills', team_data.get('baronKills', 0))
            stats.dragon_kills = team_stats.get('dragonKills', team_data.get('dragonKills', 0))
            stats.herald_kills = team_stats.get('heraldKills', team_data.get('riftHeraldKills', 0))
            stats.tower_kills = team_stats.get('towerKills', team_data.get('turretKills', 0))
            stats.inhibitor_kills = team_stats.get('inhibitorKills', team_data.get('inhibitorKills', 0))
            
            # Result - check for winner
            if metadata.winner_team_id:
                stats.win = (stats.team_id == metadata.winner_team_id)
            
            team_stats_list.append(stats)
        
        return team_stats_list
    
    def _extract_timeline(self, game: Dict) -> Dict[str, Any]:
        """Extract timeline events"""
        snapshots = game.get('snapshots', [])
        
        timeline = {
            'gold_diff': [],
            'kill_events': [],
            'objective_events': [],
            'snapshots': []
        }
        
        for snapshot in snapshots:
            timestamp = snapshot.get('timestamp', 0)
            
            # Store snapshot
            timeline['snapshots'].append({
                'timestamp': timestamp,
                'data': snapshot
            })
        
        return timeline
    
    def create_dataframe(self, parsed_matches: List[Dict]) -> pd.DataFrame:
        """Create a pandas DataFrame from parsed matches"""
        rows = []
        
        for match in parsed_matches:
            if not match:
                continue
            
            try:
                metadata = match['metadata']
                draft = match['draft']
                team_stats = match['team_stats']
                
                # Create row for each team
                for i, team in enumerate(team_stats):
                    row = {
                        'match_id': metadata.match_id,
                        'team_id': team.team_id,
                        'team_name': team.team_name,
                        'opponent_id': metadata.team2_id if i == 0 else metadata.team1_id,
                        'opponent_name': metadata.team2_name if i == 0 else metadata.team1_name,
                        'win': team.win,
                        'duration': metadata.duration_seconds,
                        'baron_kills': team.baron_kills,
                        'dragon_kills': team.dragon_kills,
                        'herald_kills': team.herald_kills,
                        'tower_kills': team.tower_kills,
                        'inhibitor_kills': team.inhibitor_kills,
                        'picks': ','.join(draft.get_team_picks(team.team_id)),
                        'bans': ','.join(draft.get_team_bans(team.team_id))
                    }
                    
                    rows.append(row)
            except Exception as e:
                print(f"Warning: Skipping match row due to error: {e}")
                continue
        
        if not rows:
            # Return empty dataframe with correct schema
            return pd.DataFrame(columns=[
                'match_id', 'team_id', 'team_name', 'opponent_id', 'opponent_name',
                'win', 'duration', 'baron_kills', 'dragon_kills', 'herald_kills',
                'tower_kills', 'inhibitor_kills', 'picks', 'bans'
            ])
        
        return pd.DataFrame(rows)


def load_and_parse_all_data(data_dir: str = "/mnt/user-data/uploads") -> Dict[str, Any]:
    """
    Main function to load and parse all match data
    
    Returns:
        Dictionary containing:
        - parsed_matches: List of parsed match dictionaries
        - dataframe: Pandas DataFrame of all matches
        - statistics: Summary statistics
    """
    parser = GridDataParser(data_dir)
    
    print("Loading match files...")
    raw_matches = parser.load_all_matches()
    print(f"Loaded {len(raw_matches)} match files")
    
    print("Parsing matches...")
    parsed_matches = []
    for match in raw_matches:
        parsed = parser.parse_match(match)
        if parsed:
            parsed_matches.append(parsed)
    
    print(f"Successfully parsed {len(parsed_matches)} matches")
    
    # Create DataFrame
    df = parser.create_dataframe(parsed_matches)
    
    # Calculate statistics
    statistics = {
        'total_matches': len(parsed_matches),
        'total_games': len(df) // 2 if len(df) > 0 else 0,  # Each match has 2 rows (one per team)
        'unique_teams': df['team_name'].nunique() if len(df) > 0 else 0,
        'avg_duration': df['duration'].mean() if len(df) > 0 else 0,
        'team_win_rates': df.groupby('team_name')['win'].mean().to_dict() if len(df) > 0 else {}
    }
    
    return {
        'parsed_matches': parsed_matches,
        'dataframe': df,
        'statistics': statistics,
        'parser': parser
    }
