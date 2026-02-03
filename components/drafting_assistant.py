"""
Nexus Commander - AI Drafting Assistant & Predictor
Component C: GNN-based draft analysis and win probability prediction
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class DraftState:
    """Current state of a draft"""
    team1_picks: List[str]
    team1_bans: List[str]
    team2_picks: List[str]
    team2_bans: List[str]
    current_phase: str  # 'ban1', 'pick1', 'ban2', 'pick2', 'ban3', 'pick3'
    turn: int  # Which team's turn (1 or 2)


@dataclass
class DraftRecommendation:
    """Recommended pick/ban with reasoning"""
    champion: str
    win_rate_impact: float  # Expected win rate change
    reasoning: List[str]
    synergies: List[str]
    counters: List[str]
    priority: str  # 'critical', 'high', 'medium', 'low'
    confidence: float


class ChampionGraph:
    """
    Graph representation of champion relationships
    Simulates GNN functionality without PyTorch Geometric dependency
    """
    
    def __init__(self):
        # Champion synergy matrix (champion -> champion -> synergy score)
        self.synergies = defaultdict(lambda: defaultdict(float))
        
        # Champion counter matrix (champion -> champion -> counter score)
        self.counters = defaultdict(lambda: defaultdict(float))
        
        # Champion win rates
        self.win_rates = defaultdict(lambda: 0.5)
        
        # Champion pick rates
        self.pick_rates = defaultdict(lambda: 0.0)
        
        # Role assignments
        self.roles = {}
    
    def build_from_matches(self, parsed_matches: List[Dict]):
        """Build graph from historical match data"""
        # Track champion pairs (teammates)
        teammate_pairs = defaultdict(int)
        teammate_wins = defaultdict(int)
        
        # Track champion vs champion matchups
        matchup_counts = defaultdict(int)
        matchup_wins = defaultdict(int)
        
        # Track individual champion performance
        champion_games = defaultdict(int)
        champion_wins = defaultdict(int)
        
        for match in parsed_matches:
            draft = match['draft']
            
            for team_stat in match['team_stats']:
                team_id = team_stat.team_id
                team_picks = draft.get_team_picks(team_id)
                won = team_stat.win
                
                # Update win rates
                for champ in team_picks:
                    champion_games[champ] += 1
                    if won:
                        champion_wins[champ] += 1
                
                # Track teammate synergies
                for i, champ1 in enumerate(team_picks):
                    for champ2 in team_picks[i+1:]:
                        pair = tuple(sorted([champ1, champ2]))
                        teammate_pairs[pair] += 1
                        if won:
                            teammate_wins[pair] += 1
                
                # Track matchups against opponents
                opponent_picks = [p for p in draft.picks 
                                if p['team_id'] != team_id and p['type'] == 'pick']
                opponent_champs = [p['champion'] for p in opponent_picks]
                
                for my_champ in team_picks:
                    for opp_champ in opponent_champs:
                        matchup = (my_champ, opp_champ)
                        matchup_counts[matchup] += 1
                        if won:
                            matchup_wins[matchup] += 1
        
        # Calculate synergy scores
        for (champ1, champ2), count in teammate_pairs.items():
            if count >= 3:  # Minimum sample size
                win_rate = teammate_wins[(champ1, champ2)] / count
                # Synergy score: deviation from expected win rate
                expected = (self.win_rates[champ1] + self.win_rates[champ2]) / 2
                synergy = win_rate - expected
                
                self.synergies[champ1][champ2] = synergy
                self.synergies[champ2][champ1] = synergy
        
        # Calculate counter scores
        for (my_champ, opp_champ), count in matchup_counts.items():
            if count >= 3:
                win_rate = matchup_wins[(my_champ, opp_champ)] / count
                # Counter score: >0.5 means we counter them, <0.5 means they counter us
                self.counters[my_champ][opp_champ] = win_rate
        
        # Calculate win rates
        for champ, games in champion_games.items():
            if games > 0:
                self.win_rates[champ] = champion_wins[champ] / games
        
        # Calculate pick rates
        total_games = len(parsed_matches)
        for champ, games in champion_games.items():
            self.pick_rates[champ] = games / total_games
    
    def get_champion_power(self, champion: str) -> float:
        """Get overall champion power level"""
        base_power = self.win_rates[champion]
        popularity_bonus = min(self.pick_rates[champion] * 0.2, 0.1)  # Up to +10%
        return base_power + popularity_bonus
    
    def get_team_synergy(self, champions: List[str]) -> float:
        """Calculate total team synergy"""
        if len(champions) <= 1:
            return 0.0
        
        total_synergy = 0.0
        pairs = 0
        
        for i, champ1 in enumerate(champions):
            for champ2 in champions[i+1:]:
                total_synergy += self.synergies[champ1][champ2]
                pairs += 1
        
        return total_synergy / pairs if pairs > 0 else 0.0
    
    def get_counter_score(self, my_champions: List[str], 
                         opponent_champions: List[str]) -> float:
        """
        Calculate how well our team counters opponent
        Positive = we counter them, Negative = they counter us
        """
        if not my_champions or not opponent_champions:
            return 0.0
        
        total_score = 0.0
        matchups = 0
        
        for my_champ in my_champions:
            for opp_champ in opponent_champions:
                counter_value = self.counters[my_champ].get(opp_champ, 0.5)
                # Convert to -0.5 to +0.5 scale
                total_score += (counter_value - 0.5)
                matchups += 1
        
        return total_score / matchups if matchups > 0 else 0.0


class DraftPredictor:
    """Predicts draft outcomes and recommends picks/bans"""
    
    def __init__(self, champion_graph: ChampionGraph):
        self.graph = champion_graph
        self.draft_phases = [
            'ban1', 'ban1', 'ban1',  # 3 bans per team
            'pick1', 'pick1',  # First rotation picks
            'ban2', 'ban2',  # Second ban phase
            'pick2', 'pick2', 'pick2', 'pick2',  # Second rotation picks
            'ban3', 'ban3',  # Final bans
            'pick3'  # Final pick
        ]
    
    def predict_win_probability(self, draft_state: DraftState) -> Dict[str, float]:
        """
        Predict win probability for both teams based on current draft
        
        Returns:
            {'team1': probability, 'team2': probability}
        """
        # Base probability from champion power
        team1_power = np.mean([self.graph.get_champion_power(c) 
                              for c in draft_state.team1_picks]) if draft_state.team1_picks else 0.5
        team2_power = np.mean([self.graph.get_champion_power(c) 
                              for c in draft_state.team2_picks]) if draft_state.team2_picks else 0.5
        
        # Team synergy bonus
        team1_synergy = self.graph.get_team_synergy(draft_state.team1_picks)
        team2_synergy = self.graph.get_team_synergy(draft_state.team2_picks)
        
        # Counter matchup evaluation
        counter_advantage = self.graph.get_counter_score(
            draft_state.team1_picks, draft_state.team2_picks
        )
        
        # Combine factors
        team1_score = team1_power + team1_synergy + counter_advantage
        team2_score = team2_power + team2_synergy - counter_advantage
        
        # Normalize to probabilities
        total = team1_score + team2_score
        if total > 0:
            team1_prob = team1_score / total
            team2_prob = team2_score / total
        else:
            team1_prob = team2_prob = 0.5
        
        return {
            'team1': team1_prob,
            'team2': team2_prob,
            'factors': {
                'team1_power': team1_power,
                'team2_power': team2_power,
                'team1_synergy': team1_synergy,
                'team2_synergy': team2_synergy,
                'counter_advantage': counter_advantage
            }
        }
    
    def recommend_pick(self, draft_state: DraftState, 
                      team: int, available_champions: List[str]) -> List[DraftRecommendation]:
        """
        Recommend next pick for a team
        
        Args:
            draft_state: Current draft state
            team: Which team (1 or 2)
            available_champions: List of unpicked/unbanned champions
        
        Returns:
            List of recommendations sorted by priority
        """
        recommendations = []
        
        my_picks = draft_state.team1_picks if team == 1 else draft_state.team2_picks
        opp_picks = draft_state.team2_picks if team == 1 else draft_state.team1_picks
        
        for champion in available_champions[:30]:  # Evaluate top 30 most viable
            # Simulate picking this champion
            test_picks = my_picks + [champion]
            
            # Calculate impact
            synergy_score = self.graph.get_team_synergy(test_picks)
            counter_score = self.graph.get_counter_score(test_picks, opp_picks)
            champion_power = self.graph.get_champion_power(champion)
            
            # Overall score
            total_score = champion_power + synergy_score * 0.3 + counter_score * 0.4
            
            # Build reasoning
            reasoning = []
            synergies = []
            counters = []
            
            # Check synergies with current picks
            for my_champ in my_picks:
                synergy_value = self.graph.synergies[champion].get(my_champ, 0)
                if synergy_value > 0.05:
                    synergies.append(f"{my_champ} (+{synergy_value:.1%})")
            
            if synergies:
                reasoning.append(f"Strong synergy with {', '.join(synergies[:2])}")
            
            # Check counters to opponent
            for opp_champ in opp_picks:
                counter_value = self.graph.counters[champion].get(opp_champ, 0.5)
                if counter_value > 0.6:
                    counters.append(f"{opp_champ} ({counter_value:.0%} WR)")
            
            if counters:
                reasoning.append(f"Counters {', '.join(counters[:2])}")
            
            # Add champion strength
            if champion_power > 0.52:
                reasoning.append(f"Strong meta pick ({champion_power:.1%} WR)")
            
            # Determine priority
            if total_score > 0.65:
                priority = 'critical'
            elif total_score > 0.55:
                priority = 'high'
            elif total_score > 0.50:
                priority = 'medium'
            else:
                priority = 'low'
            
            recommendation = DraftRecommendation(
                champion=champion,
                win_rate_impact=total_score - 0.5,  # Impact relative to average
                reasoning=reasoning if reasoning else ["Solid option"],
                synergies=synergies,
                counters=counters,
                priority=priority,
                confidence=min(champion_power * 2, 1.0)  # Based on data quality
            )
            
            recommendations.append(recommendation)
        
        # Sort by impact
        recommendations.sort(key=lambda x: x.win_rate_impact, reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def recommend_ban(self, draft_state: DraftState, 
                     team: int, available_champions: List[str]) -> List[DraftRecommendation]:
        """
        Recommend next ban for a team
        
        Strategy: Ban opponent's strongest options
        """
        recommendations = []
        
        my_picks = draft_state.team1_picks if team == 1 else draft_state.team2_picks
        
        for champion in available_champions[:30]:
            # Evaluate threat level
            champion_power = self.graph.get_champion_power(champion)
            pick_rate = self.graph.pick_rates[champion]
            
            # Check if it counters our current picks
            threat_to_us = 0.0
            if my_picks:
                threat_scores = [self.graph.counters[champion].get(my_champ, 0.5) 
                               for my_champ in my_picks]
                threat_to_us = np.mean(threat_scores) - 0.5
            
            # Total threat score
            threat_score = champion_power * 0.5 + threat_to_us * 0.3 + pick_rate * 0.2
            
            reasoning = []
            if champion_power > 0.53:
                reasoning.append(f"High win rate ({champion_power:.1%})")
            
            if pick_rate > 0.3:
                reasoning.append(f"Commonly picked ({pick_rate:.1%} pick rate)")
            
            if threat_to_us > 0.05:
                reasoning.append(f"Counters our composition")
            
            # Priority based on threat
            if threat_score > 0.6:
                priority = 'critical'
            elif threat_score > 0.55:
                priority = 'high'
            else:
                priority = 'medium'
            
            recommendation = DraftRecommendation(
                champion=champion,
                win_rate_impact=threat_score,
                reasoning=reasoning if reasoning else ["Standard ban"],
                synergies=[],
                counters=[],
                priority=priority,
                confidence=min(pick_rate * 3, 1.0)
            )
            
            recommendations.append(recommendation)
        
        # Sort by threat (highest first)
        recommendations.sort(key=lambda x: x.win_rate_impact, reverse=True)
        
        return recommendations[:10]


class DraftingAssistant:
    """Main interface for drafting assistance"""
    
    def __init__(self, parsed_matches: List[Dict]):
        self.matches = parsed_matches
        self.graph = ChampionGraph()
        self.graph.build_from_matches(parsed_matches)
        self.predictor = DraftPredictor(self.graph)
        
        # Extract all unique champions
        self.all_champions = set()
        for match in parsed_matches:
            for action in match['draft'].sequence:
                self.all_champions.add(action['champion'])
    
    def analyze_draft(self, draft_state: DraftState) -> Dict[str, Any]:
        """
        Comprehensive draft analysis
        
        Returns analysis including:
        - Current win probabilities
        - Next recommended action
        - Draft strengths/weaknesses
        """
        # Get current win probability
        win_probs = self.predictor.predict_win_probability(draft_state)
        
        # Determine next action (pick or ban)
        current_phase = draft_state.current_phase
        is_ban_phase = 'ban' in current_phase
        
        # Get available champions
        all_picked = set(draft_state.team1_picks + draft_state.team2_picks)
        all_banned = set(draft_state.team1_bans + draft_state.team2_bans)
        available = [c for c in self.all_champions if c not in all_picked and c not in all_banned]
        
        # Get recommendations
        if is_ban_phase:
            recommendations = self.predictor.recommend_ban(
                draft_state, draft_state.turn, available
            )
        else:
            recommendations = self.predictor.recommend_pick(
                draft_state, draft_state.turn, available
            )
        
        # Analyze team compositions
        team1_analysis = self._analyze_team_comp(draft_state.team1_picks, draft_state.team2_picks)
        team2_analysis = self._analyze_team_comp(draft_state.team2_picks, draft_state.team1_picks)
        
        return {
            'win_probabilities': win_probs,
            'recommendations': recommendations,
            'team1_analysis': team1_analysis,
            'team2_analysis': team2_analysis,
            'phase': current_phase,
            'turn': draft_state.turn
        }
    
    def _analyze_team_comp(self, team_picks: List[str], opponent_picks: List[str]) -> Dict[str, Any]:
        """Analyze a team composition"""
        if not team_picks:
            return {'status': 'No picks yet'}
        
        synergy = self.graph.get_team_synergy(team_picks)
        counter_score = self.graph.get_counter_score(team_picks, opponent_picks)
        
        strengths = []
        weaknesses = []
        
        if synergy > 0.05:
            strengths.append(f"Strong team synergy (+{synergy:.1%})")
        elif synergy < -0.05:
            weaknesses.append(f"Poor team synergy ({synergy:.1%})")
        
        if counter_score > 0.05:
            strengths.append(f"Favorable matchup (+{counter_score:.1%})")
        elif counter_score < -0.05:
            weaknesses.append(f"Unfavorable matchup ({counter_score:.1%})")
        
        return {
            'champions': team_picks,
            'synergy_score': synergy,
            'counter_score': counter_score,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
    
    def simulate_draft_to_completion(self, initial_state: DraftState) -> Dict[str, Any]:
        """
        Simulate a complete draft from current state
        Returns final win probability and optimal picks
        """
        # This would use Monte Carlo Tree Search or similar
        # Simplified version: just recommend best picks for each remaining slot
        pass
