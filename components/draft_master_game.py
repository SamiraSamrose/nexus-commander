"""
Nexus Commander - Draft Master Mini-Game
Component D: Fan-facing game where users compete against AI in draft scenarios
"""

import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class GameState:
    """State of a Draft Master game"""
    game_id: str
    player_name: str
    difficulty: str  # 'easy', 'medium', 'hard', 'pro'
    
    # Match context (from historical data)
    historical_match_id: str
    tournament: str
    real_team1: str
    real_team2: str
    
    # Current draft state
    player_picks: List[str]
    player_bans: List[str]
    ai_picks: List[str]
    ai_bans: List[str]
    
    # Game state
    current_phase: int  # 0-19 (full draft sequence)
    player_turn: bool
    
    # Scoring
    score: int
    moves_evaluated: List[Dict[str, Any]]
    
    # Advanced features
    combo_count: int = 0
    streak_count: int = 0
    powerups_active: List[str] = None
    achievements: List[str] = None
    perfect_moves: int = 0
    
    # Metadata
    started_at: datetime
    completed_at: Optional[datetime] = None
    final_win_probability: float = 0.0
    
    def __post_init__(self):
        if self.powerups_active is None:
            self.powerups_active = []
        if self.achievements is None:
            self.achievements = []


@dataclass
class DraftMove:
    """A single draft move (pick or ban)"""
    phase: int
    action: str  # 'pick' or 'ban'
    champion: str
    player_made: bool
    
    # Scoring
    optimal_choice: str
    score_awarded: int
    reasoning: str


class DraftScorer:
    """Scores player draft decisions with advanced mechanics"""
    
    def __init__(self, drafting_assistant):
        self.assistant = drafting_assistant
        self.scoring_rules = {
            'optimal_pick': 100,
            'good_pick': 75,
            'acceptable_pick': 50,
            'suboptimal_pick': 25,
            'poor_pick': 0,
            'time_bonus': 10,
            'synergy_bonus': 50,
            'counter_bonus': 50,
            'combo_multiplier': 1.5,
            'streak_bonus': 25,
            'perfect_move_bonus': 100
        }
        
        self.achievements = {
            'first_blood': {'name': 'First Blood', 'desc': 'First optimal pick', 'bonus': 50},
            'combo_master': {'name': 'Combo Master', 'desc': '3 optimal picks in a row', 'bonus': 150},
            'synergy_king': {'name': 'Synergy King', 'desc': 'Build perfect synergy comp', 'bonus': 200},
            'counter_strike': {'name': 'Counter Strike', 'desc': 'Counter all enemy picks', 'bonus': 175},
            'speedster': {'name': 'Speedster', 'desc': 'All picks under 15s', 'bonus': 125},
            'flawless': {'name': 'Flawless Victory', 'desc': 'All optimal picks', 'bonus': 500},
            'comeback_kid': {'name': 'Comeback Kid', 'desc': 'Win from losing position', 'bonus': 250},
            'draft_god': {'name': 'Draft God', 'desc': '90%+ win probability', 'bonus': 300}
        }
    
    def score_pick(self, 
                   chosen_champion: str,
                   draft_state,
                   recommendations: List,
                   time_taken: float,
                   game_state) -> Tuple[int, str, Dict]:
        """Enhanced scoring with combos and bonuses"""
        
        chosen_rank = None
        for i, rec in enumerate(recommendations):
            if rec.champion == chosen_champion:
                chosen_rank = i
                break
        
        base_score = 0
        reasoning = ""
        bonuses = []
        
        if chosen_rank is None:
            base_score = self.scoring_rules['poor_pick']
            reasoning = "Unconventional choice"
            game_state.streak_count = 0
        elif chosen_rank == 0:
            base_score = self.scoring_rules['optimal_pick']
            reasoning = f"Optimal pick! {recommendations[0].reasoning[0] if recommendations[0].reasoning else ''}"
            game_state.streak_count += 1
            game_state.perfect_moves += 1
            
            if game_state.perfect_moves == 1:
                bonuses.append(('First Blood', self.achievements['first_blood']['bonus']))
            
            if game_state.streak_count >= 3:
                game_state.combo_count += 1
                combo_bonus = int(base_score * self.scoring_rules['combo_multiplier'])
                bonuses.append(('Combo x3', combo_bonus))
                
                if game_state.combo_count == 1:
                    bonuses.append(('Combo Master', self.achievements['combo_master']['bonus']))
        elif chosen_rank <= 2:
            base_score = self.scoring_rules['good_pick']
            reasoning = f"Good pick! Ranked #{chosen_rank + 1}"
            game_state.streak_count = max(0, game_state.streak_count - 1)
        elif chosen_rank <= 5:
            base_score = self.scoring_rules['acceptable_pick']
            reasoning = f"Acceptable pick"
            game_state.streak_count = 0
        else:
            base_score = self.scoring_rules['suboptimal_pick']
            reasoning = f"Suboptimal - better options available"
            game_state.streak_count = 0
        
        time_bonus = int(max(0, 30 - time_taken) * self.scoring_rules['time_bonus'])
        if time_bonus > 200:
            bonuses.append(('Speed Bonus', time_bonus))
        
        if game_state.streak_count > 0:
            streak_bonus = game_state.streak_count * self.scoring_rules['streak_bonus']
            bonuses.append(('Streak', streak_bonus))
        
        total_score = base_score + time_bonus + sum(b[1] for b in bonuses)
        
        if bonuses:
            bonus_text = " + " + " + ".join([f"{name} (+{val})" for name, val in bonuses])
            reasoning += bonus_text
        
        extras = {
            'bonuses': bonuses,
            'streak': game_state.streak_count,
            'combo': game_state.combo_count,
            'base': base_score,
            'time_bonus': time_bonus
        }
        
        return total_score, reasoning, extras
    
    def check_achievements(self, game_state: GameState) -> List[str]:
        """Check for newly unlocked achievements"""
        new_achievements = []
        
        if game_state.perfect_moves >= 10 and 'flawless' not in game_state.achievements:
            new_achievements.append('flawless')
            game_state.achievements.append('flawless')
        
        avg_time = sum([m.get('time_taken', 30) for m in game_state.moves_evaluated]) / max(1, len(game_state.moves_evaluated))
        if avg_time < 15 and len(game_state.moves_evaluated) >= 10 and 'speedster' not in game_state.achievements:
            new_achievements.append('speedster')
            game_state.achievements.append('speedster')
        
        if game_state.final_win_probability >= 0.9 and 'draft_god' not in game_state.achievements:
            new_achievements.append('draft_god')
            game_state.achievements.append('draft_god')
        
        return new_achievements
    
    def calculate_final_score(self, game_state: GameState) -> Dict[str, Any]:
        """Calculate final score with all achievements"""
        base_score = sum(move.get('score', 0) for move in game_state.moves_evaluated)
        
        wp_bonus = 0
        if game_state.final_win_probability > 0.75:
            wp_bonus = 800
        elif game_state.final_win_probability > 0.65:
            wp_bonus = 500
        elif game_state.final_win_probability > 0.55:
            wp_bonus = 300
        elif game_state.final_win_probability > 0.5:
            wp_bonus = 100
        
        achievement_bonus = sum(self.achievements[ach]['bonus'] for ach in game_state.achievements if ach in self.achievements)
        
        total_score = base_score + wp_bonus + achievement_bonus
        
        if total_score >= 3000:
            rating = "Legendary"
            rank = "S+"
        elif total_score >= 2000:
            rating = "Master"
            rank = "S"
        elif total_score >= 1500:
            rating = "Diamond"
            rank = "A"
        elif total_score >= 1000:
            rating = "Platinum"
            rank = "B"
        else:
            rating = "Gold"
            rank = "C"
        
        return {
            'base_score': base_score,
            'win_probability_bonus': wp_bonus,
            'achievement_bonus': achievement_bonus,
            'total_score': total_score,
            'rating': rating,
            'rank': rank,
            'moves_made': len(game_state.moves_evaluated),
            'average_move_score': base_score / len(game_state.moves_evaluated) if game_state.moves_evaluated else 0,
            'perfect_moves': game_state.perfect_moves,
            'combos': game_state.combo_count,
            'achievements': game_state.achievements
        }



class DraftMasterGame:
    """Main game engine for Draft Master"""
    
    def __init__(self, parsed_matches: List[Dict], drafting_assistant):
        self.matches = parsed_matches
        self.assistant = drafting_assistant
        self.scorer = DraftScorer(drafting_assistant)
        self.active_games = {}
    
    def start_new_game(self, 
                       player_name: str,
                       difficulty: str = 'medium') -> GameState:
        """
        Start a new Draft Master game
        
        Picks a random historical match and lets player try to draft better
        """
        # Select random match
        match = random.choice(self.matches)
        
        game_id = f"game_{datetime.now().timestamp()}"
        
        game_state = GameState(
            game_id=game_id,
            player_name=player_name,
            difficulty=difficulty,
            historical_match_id=match['metadata'].match_id,
            tournament=match['metadata'].tournament,
            real_team1=match['metadata'].team1_name,
            real_team2=match['metadata'].team2_name,
            player_picks=[],
            player_bans=[],
            ai_picks=[],
            ai_bans=[],
            current_phase=0,
            player_turn=True,
            score=0,
            moves_evaluated=[],
            started_at=datetime.now()
        )
        
        self.active_games[game_id] = game_state
        
        return game_state
    
    def get_available_actions(self, game_id: str) -> Dict[str, Any]:
        """
        Get available actions for current phase
        
        Returns:
            - action_type: 'pick' or 'ban'
            - available_champions: list of valid choices
            - recommendations: AI suggestions (if enabled)
            - time_limit: seconds to make choice
        """
        game_state = self.active_games[game_id]
        
        # Determine action type from phase
        phase = game_state.current_phase
        
        # Simplified draft order (standard League of Legends)
        # Phases: 0-2 bans, 3-4 picks, 5-6 bans, 7-10 picks, 11-12 bans, 13 pick
        ban_phases = list(range(0, 3)) + list(range(5, 7)) + list(range(11, 13))
        
        is_ban = phase in ban_phases
        action_type = 'ban' if is_ban else 'pick'
        
        # Get available champions
        all_picked = set(game_state.player_picks + game_state.ai_picks)
        all_banned = set(game_state.player_bans + game_state.ai_bans)
        available = [c for c in self.assistant.all_champions 
                    if c not in all_picked and c not in all_banned]
        
        # Get AI recommendations
        from drafting_assistant import DraftState
        
        draft_state = DraftState(
            team1_picks=game_state.player_picks,
            team1_bans=game_state.player_bans,
            team2_picks=game_state.ai_picks,
            team2_bans=game_state.ai_bans,
            current_phase=action_type,
            turn=1 if game_state.player_turn else 2
        )
        
        if is_ban:
            recommendations = self.assistant.predictor.recommend_ban(
                draft_state, 1, available
            )
        else:
            recommendations = self.assistant.predictor.recommend_pick(
                draft_state, 1, available
            )
        
        # Difficulty-based hint system
        hints = []
        if game_state.difficulty == 'easy':
            hints = recommendations[:5]  # Show top 5
        elif game_state.difficulty == 'medium':
            hints = recommendations[:3]  # Show top 3
        elif game_state.difficulty == 'hard':
            hints = [recommendations[0]]  # Show only best
        # 'pro' mode: no hints
        
        return {
            'action_type': action_type,
            'available_champions': available[:50],  # Limit for UI
            'recommendations': hints if game_state.difficulty != 'pro' else [],
            'time_limit': 30,
            'phase': phase,
            'phase_description': self._get_phase_description(phase)
        }
    
    def make_move(self, 
                  game_id: str, 
                  champion: str,
                  time_taken: float = 30.0) -> Dict[str, Any]:
        """
        Player makes a move (pick or ban)
        
        Returns:
            - move_result: scoring and feedback
            - ai_response: AI's countermove
            - game_continues: whether game is ongoing
        """
        game_state = self.active_games[game_id]
        
        # Get current action context
        actions = self.get_available_actions(game_id)
        
        # Validate move
        if champion not in actions['available_champions']:
            return {'error': 'Invalid champion choice'}
        
        # Score the move with enhanced system
        score, reasoning, extras = self.scorer.score_pick(
            champion,
            None,
            actions['recommendations'],
            time_taken,
            game_state
        )
        
        # Record move
        move_record = {
            'phase': game_state.current_phase,
            'action': actions['action_type'],
            'champion': champion,
            'score': score,
            'reasoning': reasoning,
            'time_taken': time_taken,
            'extras': extras
        }
        
        game_state.moves_evaluated.append(move_record)
        game_state.score += score
        
        # Update game state
        if actions['action_type'] == 'ban':
            game_state.player_bans.append(champion)
        else:
            game_state.player_picks.append(champion)
        
        # AI's turn
        ai_move = self._ai_make_move(game_state, actions['action_type'])
        
        # Advance phase
        game_state.current_phase += 1
        
        # Check if game complete
        game_complete = game_state.current_phase >= 20
        
        result = {
            'player_move': move_record,
            'ai_move': ai_move,
            'current_score': game_state.score,
            'game_complete': game_complete,
            'streak': game_state.streak_count,
            'combo': game_state.combo_count,
            'perfect_moves': game_state.perfect_moves
        }
        
        if game_complete:
            final_results = self._complete_game(game_state)
            result['final_results'] = final_results
        
        return result
    
    def _ai_make_move(self, game_state: GameState, action_type: str) -> Dict[str, str]:
        """AI makes its move"""
        from drafting_assistant import DraftState
        
        # Get AI recommendations
        draft_state = DraftState(
            team1_picks=game_state.ai_picks,
            team1_bans=game_state.ai_bans,
            team2_picks=game_state.player_picks,
            team2_bans=game_state.player_bans,
            current_phase=action_type,
            turn=2
        )
        
        all_picked = set(game_state.player_picks + game_state.ai_picks)
        all_banned = set(game_state.player_bans + game_state.ai_bans)
        available = [c for c in self.assistant.all_champions 
                    if c not in all_picked and c not in all_banned]
        
        if action_type == 'ban':
            recommendations = self.assistant.predictor.recommend_ban(
                draft_state, 2, available
            )
        else:
            recommendations = self.assistant.predictor.recommend_pick(
                draft_state, 2, available
            )
        
        # AI difficulty determines how optimal the choice is
        if game_state.difficulty == 'easy':
            # AI picks from top 10
            chosen = random.choice(recommendations[:10])
        elif game_state.difficulty == 'medium':
            # AI picks from top 5
            chosen = random.choice(recommendations[:5])
        elif game_state.difficulty in ['hard', 'pro']:
            # AI picks optimal
            chosen = recommendations[0]
        
        # Update AI state
        if action_type == 'ban':
            game_state.ai_bans.append(chosen.champion)
        else:
            game_state.ai_picks.append(chosen.champion)
        
        return {
            'champion': chosen.champion,
            'reasoning': chosen.reasoning[0] if chosen.reasoning else "Strategic choice"
        }
    
    def _complete_game(self, game_state: GameState) -> Dict[str, Any]:
        """Complete the game and calculate final scores with celebration"""
        from drafting_assistant import DraftState
        
        # Calculate final win probability
        final_draft = DraftState(
            team1_picks=game_state.player_picks,
            team1_bans=game_state.player_bans,
            team2_picks=game_state.ai_picks,
            team2_bans=game_state.ai_bans,
            current_phase='complete',
            turn=1
        )
        
        win_probs = self.assistant.predictor.predict_win_probability(final_draft)
        game_state.final_win_probability = win_probs['team1']
        
        # Check for new achievements
        new_achievements = self.scorer.check_achievements(game_state)
        
        # Calculate final score
        final_score = self.scorer.calculate_final_score(game_state)
        
        game_state.completed_at = datetime.now()
        
        # Determine celebration level
        celebration = self._get_celebration(final_score, new_achievements)
        
        return {
            'final_score': final_score,
            'win_probability': win_probs['team1'],
            'player_draft': {
                'picks': game_state.player_picks,
                'bans': game_state.player_bans
            },
            'ai_draft': {
                'picks': game_state.ai_picks,
                'bans': game_state.ai_bans
            },
            'comparison': self._compare_to_real_match(game_state),
            'new_achievements': new_achievements,
            'celebration': celebration,
            'stats_breakdown': {
                'perfect_moves': game_state.perfect_moves,
                'combo_count': game_state.combo_count,
                'streak_best': max([m.get('extras', {}).get('streak', 0) for m in game_state.moves_evaluated]),
                'avg_time': sum([m.get('time_taken', 30) for m in game_state.moves_evaluated]) / len(game_state.moves_evaluated)
            }
        }
    
    def _get_celebration(self, final_score: Dict, new_achievements: List[str]) -> Dict[str, Any]:
        """Generate celebration effects based on performance"""
        score = final_score['total_score']
        rank = final_score['rank']
        
        effects = []
        message = ""
        
        if score >= 3000:
            effects = ['fireworks', 'gold_rain', 'epic_sound']
            message = "LEGENDARY PERFORMANCE! You are a Draft Master!"
        elif score >= 2000:
            effects = ['confetti', 'sparkles', 'victory_sound']
            message = "OUTSTANDING! Master-level drafting!"
        elif score >= 1500:
            effects = ['stars', 'shimmer']
            message = "Excellent work! Diamond-tier performance!"
        elif score >= 1000:
            effects = ['glow']
            message = "Well played! Solid drafting!"
        else:
            effects = []
            message = "Good effort! Keep practicing!"
        
        if 'flawless' in new_achievements:
            effects.append('rainbow_burst')
            message = "FLAWLESS VICTORY! Perfect draft!"
        
        if 'draft_god' in new_achievements:
            effects.append('lightning')
            message = "DRAFT GOD! 90%+ win probability achieved!"
        
        return {
            'effects': effects,
            'message': message,
            'rank': rank,
            'title': final_score['rating']
        }
    
    def _compare_to_real_match(self, game_state: GameState) -> Dict[str, Any]:
        """Compare player's draft to what happened in the real match"""
        # Find the historical match
        real_match = None
        for match in self.matches:
            if match['metadata'].match_id == game_state.historical_match_id:
                real_match = match
                break
        
        if not real_match:
            return {}
        
        real_draft = real_match['draft']
        real_team1_picks = real_draft.get_team_picks(real_match['metadata'].team1_id)
        
        # Calculate similarity
        common_picks = set(game_state.player_picks) & set(real_team1_picks)
        
        return {
            'real_team_picks': real_team1_picks,
            'similarity': len(common_picks) / 5 * 100,
            'shared_champions': list(common_picks),
            'real_team_won': real_match['team_stats'][0].win
        }
    
    def _get_phase_description(self, phase: int) -> str:
        """Get human-readable phase description"""
        descriptions = {
            0: "First Ban Phase - Ban 1",
            1: "First Ban Phase - Ban 2", 
            2: "First Ban Phase - Ban 3",
            3: "First Pick Phase - Pick 1",
            4: "First Pick Phase - Pick 2",
            5: "Second Ban Phase - Ban 1",
            6: "Second Ban Phase - Ban 2",
            7: "Second Pick Phase - Pick 1",
            8: "Second Pick Phase - Pick 2",
            9: "Second Pick Phase - Pick 3",
            10: "Second Pick Phase - Pick 4",
            11: "Final Ban Phase - Ban 1",
            12: "Final Ban Phase - Ban 2",
            13: "Final Pick Phase"
        }
        return descriptions.get(phase, f"Phase {phase}")
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scores from all completed games"""
        completed_games = [
            g for g in self.active_games.values() 
            if g.completed_at is not None
        ]
        
        # Sort by score
        completed_games.sort(
            key=lambda g: self.scorer.calculate_final_score(g)['total_score'],
            reverse=True
        )
        
        leaderboard = []
        for game in completed_games[:limit]:
            final_score = self.scorer.calculate_final_score(game)
            leaderboard.append({
                'rank': len(leaderboard) + 1,
                'player_name': game.player_name,
                'score': final_score['total_score'],
                'rating': final_score['rating'],
                'difficulty': game.difficulty,
                'win_probability': game.final_win_probability,
                'completed_at': game.completed_at.isoformat()
            })
        
        return leaderboard
