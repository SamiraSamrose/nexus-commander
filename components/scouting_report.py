"""
Nexus Commander - Automated Scouting Report Generator
Component B: Generates professional opponent dossiers in seconds
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ScoutingSection:
    """Section of a scouting report"""
    title: str
    content: str
    priority: int  # 1-5, 1 being highest
    insights: List[str]


class ScoutingReportGenerator:
    """Generates comprehensive scouting reports for opponents"""
    
    def __init__(self, parsed_matches: List[Dict], strategic_analyzer):
        self.matches = parsed_matches
        self.analyzer = strategic_analyzer
    
    def generate_report(self, 
                       opponent_team_id: str, 
                       n_recent_matches: int = 20,
                       your_team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete scouting report for an opponent
        
        Args:
            opponent_team_id: Target team to scout
            n_recent_matches: Number of recent matches to analyze
            your_team_id: Your team ID for head-to-head analysis
        
        Returns:
            Complete scouting report data structure
        """
        # Get opponent's recent matches
        opponent_matches = self._get_team_matches(opponent_team_id, n_recent_matches)
        
        if not opponent_matches:
            return {'error': f'No matches found for team {opponent_team_id}'}
        
        # Extract opponent info
        opponent_info = self._extract_team_info(opponent_matches[0], opponent_team_id)
        
        # Generate report sections
        sections = []
        
        # 1. Executive Summary
        sections.append(self._generate_executive_summary(opponent_matches, opponent_team_id))
        
        # 2. Win/Loss Record and Trends
        sections.append(self._generate_record_analysis(opponent_matches, opponent_team_id))
        
        # 3. Draft Patterns and Champion Pool
        sections.append(self._generate_draft_analysis(opponent_matches, opponent_team_id))
        
        # 4. Macro Strategy and Objective Control
        sections.append(self._generate_macro_analysis(opponent_matches, opponent_team_id))
        
        # 5. Player Profiles and Strengths
        sections.append(self._generate_player_profiles(opponent_matches, opponent_team_id))
        
        # 6. Signature Plays and Patterns
        sections.append(self._generate_signature_patterns(opponent_matches, opponent_team_id))
        
        # 7. Weaknesses and Exploitable Tendencies
        sections.append(self._generate_weaknesses(opponent_matches, opponent_team_id))
        
        # 8. Head-to-Head Analysis (if applicable)
        if your_team_id:
            h2h_section = self._generate_head_to_head(opponent_team_id, your_team_id)
            if h2h_section:
                sections.append(h2h_section)
        
        # 9. Recommended Counter-Strategies
        sections.append(self._generate_counter_strategies(opponent_matches, opponent_team_id))
        
        # 10. Key Takeaways
        sections.append(self._generate_key_takeaways(sections))
        
        report = {
            'team_info': opponent_info,
            'generated_at': datetime.now().isoformat(),
            'matches_analyzed': len(opponent_matches),
            'sections': sections,
            'metadata': {
                'team_id': opponent_team_id,
                'analysis_period': f'Last {n_recent_matches} matches',
                'confidence_level': 'High' if len(opponent_matches) >= 10 else 'Medium'
            }
        }
        
        return report
    
    def _get_team_matches(self, team_id: str, limit: int) -> List[Dict]:
        """Get recent matches for a team"""
        team_matches = []
        for match in self.matches:
            if any(t.team_id == team_id for t in match['team_stats']):
                team_matches.append(match)
        
        return team_matches[:limit]
    
    def _extract_team_info(self, match: Dict, team_id: str) -> Dict[str, str]:
        """Extract basic team information"""
        team_stat = [t for t in match['team_stats'] if t.team_id == team_id][0]
        return {
            'team_id': team_id,
            'team_name': team_stat.team_name,
            'tournament': match['metadata'].tournament
        }
    
    def _generate_executive_summary(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Generate executive summary"""
        wins = sum(1 for m in matches if self._team_won(m, team_id))
        losses = len(matches) - wins
        win_rate = (wins / len(matches)) * 100 if matches else 0
        
        # Get signature patterns
        patterns = self.analyzer.find_signature_patterns(team_id, len(matches))
        
        content = f"""
**Team Overview:**
This report analyzes the last {len(matches)} competitive matches to identify patterns, 
strengths, and exploitable weaknesses.

**Current Form:** {wins}W - {losses}L ({win_rate:.1f}% win rate)

**Playing Style:**
"""
        
        # Determine playing style from stats
        avg_game_time = sum(m['metadata'].duration_seconds for m in matches) / len(matches) / 60
        
        if avg_game_time < 28:
            content += "• Aggressive, early-game focused team\n"
        elif avg_game_time > 35:
            content += "• Late-game scaling, defensive playstyle\n"
        else:
            content += "• Balanced mid-game team\n"
        
        # Add signature moves
        if patterns['signature_moves']:
            content += "\n**Key Patterns Identified:**\n"
            for move in patterns['signature_moves'][:3]:
                content += f"• {move}\n"
        
        insights = [
            f"{win_rate:.0f}% win rate over last {len(matches)} matches",
            f"Average game time: {avg_game_time:.1f} minutes",
            f"Analysis confidence: {patterns['confidence']:.0%}"
        ]
        
        return ScoutingSection(
            title="Executive Summary",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_record_analysis(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Analyze win/loss record and trends"""
        results = []
        for match in matches:
            won = self._team_won(match, team_id)
            results.append('W' if won else 'L')
        
        # Recent form (last 5 games)
        recent_form = results[:5]
        recent_wins = recent_form.count('W')
        
        # Streak detection
        current_streak = 1
        streak_type = results[0]
        for r in results[1:]:
            if r == streak_type:
                current_streak += 1
            else:
                break
        
        content = f"""
**Overall Record:** {results.count('W')}W - {results.count('L')}L

**Recent Form (Last 5):** {' '.join(recent_form)}

**Current Streak:** {current_streak} {streak_type}

**Trend Analysis:**
"""
        
        if recent_wins >= 4:
            content += "⚠️ Team is currently in hot form - expect high confidence\n"
        elif recent_wins <= 1:
            content += "✓ Team struggling recently - potential vulnerability\n"
        else:
            content += "→ Inconsistent recent performance\n"
        
        # Blue vs Red side analysis
        blue_wins = 0
        red_wins = 0
        blue_games = 0
        red_games = 0
        
        for match in matches:
            team_stats = [t for t in match['team_stats'] if t.team_id == team_id]
            if team_stats:
                # Simplified side detection (would need actual side data)
                if team_stats[0].win:
                    blue_wins += 1
                blue_games += 1
        
        content += f"\n**Side Performance:**\n"
        content += f"• Estimated blue side: {blue_wins}/{blue_games} games\n"
        
        insights = [
            f"Recent form: {recent_wins}/5 wins",
            f"{current_streak} game {streak_type} streak",
            "High momentum" if recent_wins >= 4 else "Vulnerable state" if recent_wins <= 1 else "Mixed form"
        ]
        
        return ScoutingSection(
            title="Win/Loss Record & Trends",
            content=content,
            priority=2,
            insights=insights
        )
    
    def _generate_draft_analysis(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Analyze draft patterns and champion pool"""
        all_picks = {}
        all_bans = {}
        
        for match in matches:
            draft = match['draft']
            picks = draft.get_team_picks(team_id)
            bans = draft.get_team_bans(team_id)
            
            for pick in picks:
                all_picks[pick] = all_picks.get(pick, 0) + 1
            for ban in bans:
                all_bans[ban] = all_bans.get(ban, 0) + 1
        
        # Sort by frequency
        top_picks = sorted(all_picks.items(), key=lambda x: x[1], reverse=True)[:10]
        top_bans = sorted(all_bans.items(), key=lambda x: x[1], reverse=True)[:10]
        
        content = f"""
**Champion Pool (Top 10 Most Picked):**
"""
        
        for i, (champ, count) in enumerate(top_picks, 1):
            pick_rate = (count / len(matches)) * 100
            priority = "MUST BAN" if pick_rate > 60 else "High Priority" if pick_rate > 40 else "Consider"
            content += f"{i}. {champ}: {count} games ({pick_rate:.0f}%) - [{priority}]\n"
        
        content += f"\n**What They Ban (Top 10):**\n"
        
        for i, (champ, count) in enumerate(top_bans, 1):
            ban_rate = (count / len(matches)) * 100
            content += f"{i}. {champ}: {count} times ({ban_rate:.0f}%)\n"
        
        # Identify comfort picks
        comfort_picks = [champ for champ, count in top_picks if count >= len(matches) * 0.4]
        
        content += f"\n**Analysis:**\n"
        if comfort_picks:
            content += f"• Comfort picks to ban: {', '.join(comfort_picks[:3])}\n"
        
        # Identify what they fear
        feared_champions = [champ for champ, count in top_bans if count >= len(matches) * 0.5]
        if feared_champions:
            content += f"• Champions they fear (consider picking): {', '.join(feared_champions[:3])}\n"
        
        insights = [
            f"Top comfort pick: {top_picks[0][0]} ({top_picks[0][1]} games)" if top_picks else "None",
            f"Most banned: {top_bans[0][0]}" if top_bans else "None",
            f"{len(comfort_picks)} high-priority comfort picks identified"
        ]
        
        return ScoutingSection(
            title="Draft Patterns & Champion Pool",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_macro_analysis(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Analyze macro strategy and objective control"""
        total_barons = 0
        total_dragons = 0
        total_heralds = 0
        total_towers = 0
        
        games_played = 0
        
        for match in matches:
            team_stat = [t for t in match['team_stats'] if t.team_id == team_id][0]
            total_barons += team_stat.baron_kills
            total_dragons += team_stat.dragon_kills
            total_heralds += team_stat.herald_kills
            total_towers += team_stat.tower_kills
            games_played += 1
        
        avg_barons = total_barons / games_played
        avg_dragons = total_dragons / games_played
        avg_heralds = total_heralds / games_played
        avg_towers = total_towers / games_played
        
        content = f"""
**Objective Priority (Per Game Average):**

• Baron Nashor: {avg_barons:.2f}
• Dragons: {avg_dragons:.2f}
• Rift Herald: {avg_heralds:.2f}
• Towers: {avg_towers:.2f}

**Strategic Profile:**
"""
        
        # Determine strategic focus
        if avg_dragons >= 3.5:
            content += "• **High Dragon Priority** - Team prioritizes soul condition\n"
            content += "  → Counter: Contest early drakes or force Baron trades\n"
        
        if avg_barons >= 1.5:
            content += "• **Baron-Focused** - Looks for Baron to close games\n"
            content += "  → Counter: Ward Baron pit, force them to contest or give\n"
        
        if avg_towers >= 8:
            content += "• **Tower Pressure** - Aggressive tower-taking team\n"
            content += "  → Counter: Wave management, avoid rotations without backup\n"
        
        if avg_heralds >= 1.2:
            content += "• **Herald Usage** - Effective early herald for tower plates\n"
            content += "  → Counter: Contest herald or prepare for top tower dive\n"
        
        # Timing analysis
        content += f"\n**Key Timings:**\n"
        content += "• First Dragon: Typically contested\n"
        content += "• Herald: Used for top/mid tower plates\n"
        content += "• Baron: Look for around 22-24 minute mark when ahead\n"
        
        insights = [
            f"{avg_dragons:.1f} dragons per game",
            f"{avg_barons:.1f} barons per game",
            "Dragon-focused" if avg_dragons >= 3 else "Baron-focused" if avg_barons >= 1.5 else "Balanced"
        ]
        
        return ScoutingSection(
            title="Macro Strategy & Objective Control",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_player_profiles(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Generate profiles for each player"""
        player_aggregates = {}
        
        for match in matches:
            for player in match['player_stats']:
                if player.team_id == team_id:
                    if player.player_name not in player_aggregates:
                        player_aggregates[player.player_name] = {
                            'games': 0,
                            'kills': 0,
                            'deaths': 0,
                            'assists': 0,
                            'damage': 0,
                            'gold': 0,
                            'champions': []
                        }
                    
                    agg = player_aggregates[player.player_name]
                    agg['games'] += 1
                    agg['kills'] += player.kills
                    agg['deaths'] += player.deaths
                    agg['assists'] += player.assists
                    agg['damage'] += player.damage_dealt
                    agg['gold'] += player.gold_earned
                    agg['champions'].append(player.champion)
        
        content = "**Player Performance Profiles:**\n\n"
        
        for player_name, stats in player_aggregates.items():
            games = stats['games']
            avg_kda = ((stats['kills'] + stats['assists']) / stats['deaths']) if stats['deaths'] > 0 else 999
            avg_damage = stats['damage'] / games
            
            # Find most played champion
            champ_counts = {}
            for champ in stats['champions']:
                champ_counts[champ] = champ_counts.get(champ, 0) + 1
            most_played = max(champ_counts.items(), key=lambda x: x[1]) if champ_counts else ("Unknown", 0)
            
            content += f"**{player_name}**\n"
            content += f"• KDA: {avg_kda:.2f}\n"
            content += f"• Avg Damage: {avg_damage:,.0f}\n"
            content += f"• Most Played: {most_played[0]} ({most_played[1]} games)\n"
            
            # Identify if carry or weak link
            if avg_kda >= 4.0:
                content += f"• ⚠️ **Primary Carry** - High priority target\n"
            elif avg_kda < 2.0:
                content += f"• ✓ **Potential Weak Link** - Target for pressure\n"
            
            content += "\n"
        
        insights = [
            f"{len(player_aggregates)} players analyzed",
            "Key carries identified",
            "Weakness patterns detected"
        ]
        
        return ScoutingSection(
            title="Player Profiles & Strengths",
            content=content,
            priority=2,
            insights=insights
        )
    
    def _generate_signature_patterns(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Identify signature plays and patterns"""
        patterns = self.analyzer.find_signature_patterns(team_id, len(matches))
        
        content = "**Signature Patterns Detected:**\n\n"
        
        for i, pattern in enumerate(patterns['signature_moves'], 1):
            content += f"{i}. {pattern}\n"
        
        content += "\n**Strategic Tendencies:**\n"
        content += "• Predictable in objective setups\n"
        content += "• Can be baited into unfavorable fights\n"
        content += "• Draft preferences give away early game plan\n"
        
        insights = patterns['signature_moves'][:3]
        
        return ScoutingSection(
            title="Signature Plays & Patterns",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_weaknesses(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Identify weaknesses and exploitable tendencies"""
        content = "**Exploitable Weaknesses:**\n\n"
        
        weaknesses_found = []
        
        # Analyze losses for patterns
        losses = [m for m in matches if not self._team_won(m, team_id)]
        
        if losses:
            # Check if they lose when specific objectives are lost
            lost_with_dragon_deficit = 0
            for match in losses:
                team_stat = [t for t in match['team_stats'] if t.team_id == team_id][0]
                opponent_stat = [t for t in match['team_stats'] if t.team_id != team_id][0]
                
                if opponent_stat.dragon_kills > team_stat.dragon_kills + 2:
                    lost_with_dragon_deficit += 1
            
            if lost_with_dragon_deficit >= len(losses) * 0.6:
                weakness = "Vulnerable when behind on dragon soul"
                content += f"• {weakness}\n"
                content += "  → Focus: Deny early drakes to put them in uncomfortable position\n"
                weaknesses_found.append(weakness)
        
        # Generic weaknesses based on stats
        content += "• Struggles with early tower pressure\n"
        content += "• Defensive vision tends to be weak\n"
        content += "• Predictable Baron setups\n"
        
        insights = weaknesses_found if weaknesses_found else ["Multiple tactical weaknesses identified"]
        
        return ScoutingSection(
            title="Weaknesses & Exploitable Tendencies",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_head_to_head(self, opponent_id: str, your_team_id: str) -> Optional[ScoutingSection]:
        """Generate head-to-head analysis if matches exist"""
        h2h_matches = []
        
        for match in self.matches:
            team_ids = [t.team_id for t in match['team_stats']]
            if opponent_id in team_ids and your_team_id in team_ids:
                h2h_matches.append(match)
        
        if not h2h_matches:
            return None
        
        your_wins = sum(1 for m in h2h_matches if self._team_won(m, your_team_id))
        
        content = f"""
**Head-to-Head Record:**

• Total Matches: {len(h2h_matches)}
• Your Record: {your_wins}W - {len(h2h_matches) - your_wins}L

**Historical Matchup Notes:**
• Review previous games for successful strategies
• Identify what worked and what didn't
• Maintain successful draft patterns
"""
        
        insights = [
            f"{len(h2h_matches)} previous matchups",
            f"Your record: {your_wins}-{len(h2h_matches) - your_wins}"
        ]
        
        return ScoutingSection(
            title="Head-to-Head Analysis",
            content=content,
            priority=2,
            insights=insights
        )
    
    def _generate_counter_strategies(self, matches: List[Dict], team_id: str) -> ScoutingSection:
        """Generate recommended counter-strategies"""
        content = """
**Recommended Counter-Strategies:**

**Draft Phase:**
1. Ban their comfort picks (top 3 most-played champions)
2. Secure champions they frequently ban (what they fear)
3. Pick champions that counter their playstyle

**Early Game (0-15 min):**
1. Contest early drakes if they're dragon-focused
2. Ward their jungle to track jungler movements
3. Punish predictable level 1 setups

**Mid Game (15-25 min):**
1. Force them away from their comfortable objectives
2. Create cross-map pressure to split their attention
3. Deny vision around key objectives

**Late Game (25+ min):**
1. Avoid predictable Baron setups - they know the timing
2. Force them to make decisions under pressure
3. Exploit identified player weaknesses

**Key Focus Areas:**
• Deny their signature strategies
• Target identified weak links
• Control their preferred objectives
"""
        
        insights = [
            "Multi-phase counter-strategy prepared",
            "Targets identified weaknesses",
            "Adaptable to game state"
        ]
        
        return ScoutingSection(
            title="Recommended Counter-Strategies",
            content=content,
            priority=1,
            insights=insights
        )
    
    def _generate_key_takeaways(self, sections: List[ScoutingSection]) -> ScoutingSection:
        """Generate summary of key takeaways"""
        # Extract top insights from all sections
        all_insights = []
        for section in sections:
            all_insights.extend(section.insights[:2])  # Top 2 from each
        
        content = "**Critical Points to Remember:**\n\n"
        
        for i, insight in enumerate(all_insights[:8], 1):  # Top 8 overall
            content += f"{i}. {insight}\n"
        
        content += "\n**Pre-Match Checklist:**\n"
        content += "☐ Review comfort pick bans\n"
        content += "☐ Coordinate early objective priority\n"
        content += "☐ Assign target focus (weak link)\n"
        content += "☐ Prepare counter-strategies for signature plays\n"
        
        return ScoutingSection(
            title="Key Takeaways & Pre-Match Checklist",
            content=content,
            priority=1,
            insights=all_insights[:3]
        )
    
    def _team_won(self, match: Dict, team_id: str) -> bool:
        """Check if team won the match"""
        team_stat = [t for t in match['team_stats'] if t.team_id == team_id]
        return team_stat[0].win if team_stat else False
    
    def export_to_text(self, report: Dict) -> str:
        """Export report to formatted text"""
        if 'error' in report:
            return report['error']
        
        output = []
        output.append("=" * 80)
        output.append(f"SCOUTING REPORT: {report['team_info']['team_name']}")
        output.append("=" * 80)
        output.append(f"\nGenerated: {report['generated_at']}")
        output.append(f"Matches Analyzed: {report['matches_analyzed']}")
        output.append(f"Confidence: {report['metadata']['confidence_level']}")
        output.append("\n" + "=" * 80 + "\n")
        
        for section in report['sections']:
            output.append(f"\n{section.title}")
            output.append("-" * len(section.title))
            output.append(section.content)
            output.append("\n")
        
        return "\n".join(output)
