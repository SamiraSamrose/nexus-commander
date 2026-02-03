"""
Nexus Commander - AI Assistant Coach
Component A: Strategic Brain with Agentic RAG
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime


@dataclass
class CoachingInsight:
    """Structured coaching insight"""
    category: str  # 'macro', 'micro', 'draft', 'vision', 'economy'
    priority: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    evidence: List[str]
    recommendations: List[str]
    affected_players: List[str] = None
    timestamp_range: Optional[Tuple[int, int]] = None
    confidence: float = 0.0


class StrategicAnalyzer:
    """Analyzes match data for strategic patterns"""
    
    def __init__(self, parsed_matches: List[Dict]):
        self.matches = parsed_matches
        self.insights_cache = {}
    
    def analyze_gold_deficit(self, match: Dict, team_id: str, minute: int = 12) -> Dict[str, Any]:
        """
        Analyze gold deficit at a specific time point
        
        Answers: "Why did our bot lane fall behind in gold at the 12-minute mark?"
        """
        try:
            player_stats = match['player_stats']
            team_stats = match['team_stats']
            
            # Filter players by team
            team_players = [p for p in player_stats if p.team_id == team_id]
            opponent_players = [p for p in player_stats if p.team_id != team_id]
            
            # Identify bot lane (ADC + Support)
            bot_roles = ['bottom', 'adc', 'support', 'utility']
            team_bot = [p for p in team_players if p.role.lower() in bot_roles]
            opp_bot = [p for p in opponent_players if p.role.lower() in bot_roles]
            
            team_bot_gold = sum(p.gold_earned for p in team_bot)
            opp_bot_gold = sum(p.gold_earned for p in opp_bot)
            gold_diff = team_bot_gold - opp_bot_gold
            
            # Analyze reasons
            reasons = []
            
            # CS differential
            team_cs = sum(p.cs for p in team_bot)
            opp_cs = sum(p.cs for p in opp_bot)
            cs_diff = team_cs - opp_cs
            
            if cs_diff < -20:
                reasons.append(f"CS deficit: {abs(cs_diff)} creeps behind ({abs(cs_diff * 20)} estimated gold)")
            
            # Death differential
            team_deaths = sum(p.deaths for p in team_bot)
            opp_deaths = sum(p.deaths for p in opp_bot)
            
            if team_deaths > opp_deaths:
                death_diff = team_deaths - opp_deaths
                reasons.append(f"{death_diff} extra deaths in bot lane (~{death_diff * 300} gold)")
            
            # Kill participation
            team_kills = sum(p.kills + p.assists for p in team_bot)
            if team_kills < 2:
                reasons.append("Low kill participation - bot lane isolated from team fights")
            
            analysis = {
                'gold_differential': gold_diff,
                'team_bot_gold': team_bot_gold,
                'opponent_bot_gold': opp_bot_gold,
                'cs_differential': cs_diff,
                'death_differential': team_deaths - opp_deaths,
                'reasons': reasons,
                'players_affected': [p.player_name for p in team_bot]
            }
            
            return analysis
        
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_macro_patterns(self, match: Dict, team_id: str) -> List[CoachingInsight]:
        """Analyze macro-level strategic patterns"""
        insights = []
        
        team_stats = [t for t in match['team_stats'] if t.team_id == team_id][0]
        opponent_stats = [t for t in match['team_stats'] if t.team_id != team_id][0]
        
        # Baron control analysis
        if opponent_stats.baron_kills > team_stats.baron_kills + 1:
            insight = CoachingInsight(
                category='macro',
                priority='critical',
                title='Baron Control Deficit',
                description=f"Opponent secured {opponent_stats.baron_kills} Barons vs our {team_stats.baron_kills}",
                evidence=[
                    f"Baron differential: -{opponent_stats.baron_kills - team_stats.baron_kills}",
                    "Each Baron provides ~4000 gold and map pressure"
                ],
                recommendations=[
                    "Ward Baron pit 90 seconds before spawn",
                    "Contest with full team or force cross-map objective",
                    "Review Baron setup timings in VOD"
                ],
                confidence=0.9
            )
            insights.append(insight)
        
        # Dragon soul control
        if opponent_stats.dragon_kills >= 4 and team_stats.dragon_kills < 2:
            insight = CoachingInsight(
                category='macro',
                priority='high',
                title='Dragon Priority Issue',
                description=f"Opponent secured soul ({opponent_stats.dragon_kills} dragons) while we only took {team_stats.dragon_kills}",
                evidence=[
                    f"Dragon differential: -{opponent_stats.dragon_kills - team_stats.dragon_kills}",
                    "Soul provides permanent team-wide buff"
                ],
                recommendations=[
                    "Prioritize early drake control in draft",
                    "Track jungle pathing to predict drake timing",
                    "Consider giving top priority to secure drakes"
                ],
                confidence=0.95
            )
            insights.append(insight)
        
        # Tower pressure
        if opponent_stats.tower_kills > team_stats.tower_kills + 3:
            insight = CoachingInsight(
                category='macro',
                priority='high',
                title='Tower Pressure Deficit',
                description=f"Lost {opponent_stats.tower_kills - team_stats.tower_kills} more towers than opponent",
                evidence=[
                    f"Tower differential: -{opponent_stats.tower_kills - team_stats.tower_kills}",
                    "Each tower = 550 gold + map control"
                ],
                recommendations=[
                    "Improve wave management to create slow pushes",
                    "Rotate faster to defend tower dives",
                    "Use Herald more effectively for tower plates"
                ],
                confidence=0.85
            )
            insights.append(insight)
        
        return insights
    
    def analyze_micro_mechanics(self, match: Dict, player_name: str) -> List[CoachingInsight]:
        """Analyze individual player mechanics"""
        insights = []
        
        player_stats = [p for p in match['player_stats'] if p.player_name == player_name]
        if not player_stats:
            return insights
        
        player = player_stats[0]
        
        # KDA analysis
        if player.kda < 2.0 and player.deaths > 5:
            insight = CoachingInsight(
                category='micro',
                priority='high',
                title=f'{player_name} - Positioning Issues',
                description=f"KDA of {player.kda:.2f} with {player.deaths} deaths suggests positioning errors",
                evidence=[
                    f"Deaths: {player.deaths} (avg should be <4 for {player.role})",
                    f"Damage taken: {player.damage_taken:,}",
                    f"KDA: {player.kda:.2f}"
                ],
                recommendations=[
                    "Review team fight positioning in replays",
                    "Practice champion-specific escape combos",
                    "Improve map awareness and vision placement"
                ],
                affected_players=[player_name],
                confidence=0.8
            )
            insights.append(insight)
        
        # CS efficiency
        duration_minutes = match['metadata'].duration_seconds / 60
        cs_per_min = player.cs / duration_minutes if duration_minutes > 0 else 0
        
        expected_cs_per_min = 8.0 if player.role in ['adc', 'mid', 'top'] else 5.0
        
        if cs_per_min < expected_cs_per_min - 1.5:
            insight = CoachingInsight(
                category='micro',
                priority='medium',
                title=f'{player_name} - CS Efficiency',
                description=f"CS/min of {cs_per_min:.1f} below expected {expected_cs_per_min} for {player.role}",
                evidence=[
                    f"Total CS: {player.cs}",
                    f"CS/min: {cs_per_min:.1f}",
                    f"Expected: {expected_cs_per_min} for {player.role}"
                ],
                recommendations=[
                    "Practice last-hitting in training mode",
                    "Improve wave management and freeze timing",
                    "Balance roaming with farm efficiency"
                ],
                affected_players=[player_name],
                confidence=0.75
            )
            insights.append(insight)
        
        # Vision control
        if player.role in ['support', 'jungle'] and player.vision_score < 30:
            insight = CoachingInsight(
                category='vision',
                priority='high',
                title=f'{player_name} - Vision Control',
                description=f"Vision score of {player.vision_score} too low for {player.role}",
                evidence=[
                    f"Wards placed: {player.wards_placed}",
                    f"Wards destroyed: {player.wards_destroyed}",
                    f"Vision score: {player.vision_score}"
                ],
                recommendations=[
                    "Place wards on cooldown throughout the game",
                    "Buy control wards every back (minimum 2 per game)",
                    "Coordinate with team to deny enemy vision before objectives"
                ],
                affected_players=[player_name],
                confidence=0.9
            )
            insights.append(insight)
        
        return insights
    
    def find_signature_patterns(self, team_id: str, n_matches: int = 5) -> Dict[str, Any]:
        """
        Identify signature patterns across multiple matches
        
        For scouting reports: "This team always forces Baron at 22:00 if they have 2k gold lead"
        """
        team_matches = [m for m in self.matches if 
                       any(t.team_id == team_id for t in m['team_stats'])][:n_matches]
        
        patterns = {
            'baron_timing': [],
            'dragon_priority': [],
            'early_aggression': [],
            'draft_preferences': {
                'frequent_picks': {},
                'frequent_bans': {}
            }
        }
        
        for match in team_matches:
            # Get team stats
            team_stat = [t for t in match['team_stats'] if t.team_id == team_id][0]
            
            # Baron patterns
            if team_stat.baron_kills > 0:
                duration = match['metadata'].duration_seconds
                avg_baron_time = duration * 0.6  # Approximate (22 min in a 35 min game)
                patterns['baron_timing'].append(avg_baron_time)
            
            # Dragon priority
            patterns['dragon_priority'].append(team_stat.dragon_kills)
            
            # Draft preferences
            draft = match['draft']
            team_picks = draft.get_team_picks(team_id)
            team_bans = draft.get_team_bans(team_id)
            
            for pick in team_picks:
                patterns['draft_preferences']['frequent_picks'][pick] = \
                    patterns['draft_preferences']['frequent_picks'].get(pick, 0) + 1
            
            for ban in team_bans:
                patterns['draft_preferences']['frequent_bans'][ban] = \
                    patterns['draft_preferences']['frequent_bans'].get(ban, 0) + 1
        
        # Calculate signature moves
        signature_moves = []
        
        # Baron timing pattern
        if len(patterns['baron_timing']) >= 3:
            avg_baron = np.mean(patterns['baron_timing'])
            signature_moves.append(
                f"Forces Baron around {int(avg_baron // 60)} minutes when ahead"
            )
        
        # Dragon priority
        avg_drakes = np.mean(patterns['dragon_priority'])
        if avg_drakes >= 3:
            signature_moves.append(
                f"High dragon priority - averages {avg_drakes:.1f} drakes per game"
            )
        
        # Most picked champions
        top_picks = sorted(patterns['draft_preferences']['frequent_picks'].items(), 
                          key=lambda x: x[1], reverse=True)[:3]
        if top_picks:
            signature_moves.append(
                f"Comfort picks: {', '.join([champ for champ, _ in top_picks])}"
            )
        
        # Most banned champions (what they fear)
        top_bans = sorted(patterns['draft_preferences']['frequent_bans'].items(),
                         key=lambda x: x[1], reverse=True)[:3]
        if top_bans:
            signature_moves.append(
                f"Frequent bans: {', '.join([champ for champ, _ in top_bans])}"
            )
        
        return {
            'raw_patterns': patterns,
            'signature_moves': signature_moves,
            'confidence': len(team_matches) / n_matches
        }


class AICoachingAssistant:
    """
    Main AI Coaching Assistant using RAG
    Simulates LangGraph agentic workflow
    """
    
    def __init__(self, parsed_matches: List[Dict]):
        self.matches = parsed_matches
        self.analyzer = StrategicAnalyzer(parsed_matches)
        self.knowledge_base = self._build_knowledge_base()
    
    def _build_knowledge_base(self) -> Dict[str, Any]:
        """Build a searchable knowledge base from matches"""
        kb = {
            'matches_by_team': {},
            'player_performances': {},
            'meta_trends': {}
        }
        
        for match in self.matches:
            for team_stat in match['team_stats']:
                team_id = team_stat.team_id
                if team_id not in kb['matches_by_team']:
                    kb['matches_by_team'][team_id] = []
                kb['matches_by_team'][team_id].append(match)
        
        return kb
    
    def query(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Main query interface - simulates agentic RAG
        
        Args:
            question: Natural language question
            context: Optional context (team_id, match_id, player_name, etc.)
        
        Returns:
            Detailed answer with evidence
        """
        question_lower = question.lower()
        
        # Route to appropriate analyzer based on question
        
        # Gold deficit analysis
        if 'gold' in question_lower and 'behind' in question_lower:
            if context and 'team_id' in context and 'match_id' in context:
                match = self._find_match(context['match_id'])
                if match:
                    analysis = self.analyzer.analyze_gold_deficit(
                        match, context['team_id']
                    )
                    return self._format_gold_analysis(analysis, question)
        
        # Pattern recognition
        if 'pattern' in question_lower or 'always' in question_lower:
            if context and 'team_id' in context:
                patterns = self.analyzer.find_signature_patterns(context['team_id'])
                return self._format_pattern_analysis(patterns, question)
        
        # Player performance
        if 'player' in question_lower or context and 'player_name' in context:
            if context and 'match_id' in context:
                match = self._find_match(context['match_id'])
                player_name = context.get('player_name', '')
                if match and player_name:
                    insights = self.analyzer.analyze_micro_mechanics(match, player_name)
                    return self._format_player_analysis(insights, question)
        
        # Macro strategy
        if any(word in question_lower for word in ['baron', 'dragon', 'macro', 'strategy']):
            if context and 'team_id' in context and 'match_id' in context:
                match = self._find_match(context['match_id'])
                if match:
                    insights = self.analyzer.analyze_macro_patterns(match, context['team_id'])
                    return self._format_macro_analysis(insights, question)
        
        # Default: General analysis
        return self._general_analysis(question, context)
    
    def _find_match(self, match_id: str) -> Optional[Dict]:
        """Find match by ID"""
        for match in self.matches:
            if match['metadata'].match_id == match_id:
                return match
        return None
    
    def _format_gold_analysis(self, analysis: Dict, question: str) -> str:
        """Format gold deficit analysis response"""
        if 'error' in analysis:
            return f"Unable to analyze: {analysis['error']}"
        
        response = f"**Gold Deficit Analysis**\n\n"
        response += f"Gold Differential: {analysis['gold_differential']:+,} gold\n"
        response += f"Your Bot Lane: {analysis['team_bot_gold']:,} gold\n"
        response += f"Opponent Bot Lane: {analysis['opponent_bot_gold']:,} gold\n\n"
        
        if analysis['reasons']:
            response += "**Root Causes:**\n"
            for i, reason in enumerate(analysis['reasons'], 1):
                response += f"{i}. {reason}\n"
        
        response += f"\n**Players Affected:** {', '.join(analysis['players_affected'])}\n"
        
        return response
    
    def _format_pattern_analysis(self, patterns: Dict, question: str) -> str:
        """Format pattern recognition response"""
        response = "**Signature Patterns Identified:**\n\n"
        
        for i, move in enumerate(patterns['signature_moves'], 1):
            response += f"{i}. {move}\n"
        
        response += f"\n*Confidence: {patterns['confidence']:.0%} (based on sample size)*\n"
        
        return response
    
    def _format_player_analysis(self, insights: List[CoachingInsight], question: str) -> str:
        """Format player performance analysis"""
        if not insights:
            return "No significant issues identified for this player."
        
        response = "**Player Performance Analysis:**\n\n"
        
        for insight in insights:
            response += f"**{insight.title}** [{insight.priority.upper()}]\n"
            response += f"{insight.description}\n\n"
            
            response += "Evidence:\n"
            for evidence in insight.evidence:
                response += f"  • {evidence}\n"
            
            response += "\nRecommendations:\n"
            for rec in insight.recommendations:
                response += f"  ✓ {rec}\n"
            
            response += "\n---\n\n"
        
        return response
    
    def _format_macro_analysis(self, insights: List[CoachingInsight], question: str) -> str:
        """Format macro strategy analysis"""
        if not insights:
            return "Macro play looks solid - no critical issues identified."
        
        response = "**Macro Strategy Analysis:**\n\n"
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        insights.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        for insight in insights:
            response += f"🔴 **{insight.title}** [{insight.priority.upper()}]\n"
            response += f"{insight.description}\n\n"
            
            response += "Evidence:\n"
            for evidence in insight.evidence:
                response += f"  • {evidence}\n"
            
            response += "\nAction Items:\n"
            for rec in insight.recommendations:
                response += f"  → {rec}\n"
            
            response += "\n" + "="*50 + "\n\n"
        
        return response
    
    def _general_analysis(self, question: str, context: Dict) -> str:
        """Fallback general analysis"""
        return f"Question: {question}\n\nI can help you analyze:\n" + \
               "• Gold deficits and economic patterns\n" + \
               "• Team signature moves and tendencies\n" + \
               "• Player performance and mechanics\n" + \
               "• Macro strategy and objective control\n\n" + \
               "Please provide context like team_id, match_id, or player_name."
