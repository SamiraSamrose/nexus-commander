"""
Nexus Commander - Main Application
Orchestrates all four key components
"""

import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import all components
from config import config
from data_ingestion import load_and_parse_all_data, GridDataParser
from ai_coach import AICoachingAssistant, StrategicAnalyzer
from scouting_report import ScoutingReportGenerator
from drafting_assistant import DraftingAssistant, DraftState
from draft_master_game import DraftMasterGame


class NexusCommander:
    """
    Main orchestrator for the Nexus Commander platform
    
    Provides unified interface to all four key components:
    - AI Assistant Coach
    - Scouting Report Generator
    - Drafting Assistant
    - Draft Master Game
    """
    
    def __init__(self, data_directory: str = "/mnt/user-data/uploads"):
        """
        Initialize Nexus Commander
        
        Args:
            data_directory: Path to directory containing match JSON files
        """
        print("=" * 80)
        print("Initializing Nexus Commander")
        print("The Unified AI-Esports Intelligence & Management Platform")
        print("=" * 80)
        
        # Validate configuration
        config.validate()
        config.create_directories()
        
        # Load and parse all match data
        print("\n[1/5] Loading match data...")
        self.data = load_and_parse_all_data(data_directory)
        print(f"✓ Loaded {self.data['statistics']['total_matches']} matches")
        print(f"✓ {self.data['statistics']['unique_teams']} unique teams identified")
        
        # Initialize Component A: AI Assistant Coach
        print("\n[2/5] Initializing AI Assistant Coach...")
        self.ai_coach = AICoachingAssistant(self.data['parsed_matches'])
        print("✓ AI Coach ready with strategic analysis capabilities")
        
        # Initialize Component B: Scouting Report Generator
        print("\n[3/5] Initializing Scouting Report Generator...")
        self.scouting_generator = ScoutingReportGenerator(
            self.data['parsed_matches'],
            self.ai_coach.analyzer
        )
        print("✓ Scouting Report Generator ready")
        
        # Initialize Component C: Drafting Assistant
        print("\n[4/5] Initializing AI Drafting Assistant...")
        self.drafting_assistant = DraftingAssistant(self.data['parsed_matches'])
        print("✓ Drafting Assistant ready with GNN-based predictions")
        print(f"✓ Champion graph built with {len(self.drafting_assistant.all_champions)} champions")
        
        # Initialize Component D: Draft Master Game
        print("\n[5/5] Initializing Draft Master Game...")
        self.draft_master = DraftMasterGame(
            self.data['parsed_matches'],
            self.drafting_assistant
        )
        print("✓ Draft Master Game ready for players")
        
        print("\n" + "=" * 80)
        print("Nexus Commander initialization complete!")
        print("=" * 80)
        
        self.is_ready = True
    
    # ========================================================================
    # Component A: AI Assistant Coach Interface
    # ========================================================================
    
    def ask_coach(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Ask the AI Coach a strategic question
        
        Args:
            question: Natural language question
            context: Optional context (team_id, match_id, player_name, etc.)
        
        Returns:
            Detailed analysis and recommendations
        
        Example:
            >>> nexus.ask_coach(
            ...     "Why did our bot lane fall behind in gold at 12 minutes?",
            ...     context={'team_id': '47961', 'match_id': 'match_123'}
            ... )
        """
        return self.ai_coach.query(question, context or {})
    
    def get_macro_insights(self, match_id: str, team_id: str) -> List[Any]:
        """Get macro-level strategic insights for a match"""
        match = self._find_match(match_id)
        if not match:
            return []
        return self.ai_coach.analyzer.analyze_macro_patterns(match, team_id)
    
    def get_player_insights(self, match_id: str, player_name: str) -> List[Any]:
        """Get player performance insights"""
        match = self._find_match(match_id)
        if not match:
            return []
        return self.ai_coach.analyzer.analyze_micro_mechanics(match, player_name)
    
    def find_team_patterns(self, team_id: str, n_matches: int = 10) -> Dict[str, Any]:
        """Identify signature patterns for a team"""
        return self.ai_coach.analyzer.find_signature_patterns(team_id, n_matches)
    
    # ========================================================================
    # Component B: Scouting Report Interface
    # ========================================================================
    
    def generate_scouting_report(self,
                                opponent_team_id: str,
                                n_recent_matches: int = 20,
                                your_team_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive scouting report for an opponent
        
        Args:
            opponent_team_id: Team ID to scout
            n_recent_matches: Number of recent matches to analyze
            your_team_id: Your team ID for head-to-head analysis
        
        Returns:
            Complete scouting report
        
        Example:
            >>> report = nexus.generate_scouting_report('47558')  # GenG
            >>> print(nexus.export_scouting_report(report))
        """
        return self.scouting_generator.generate_report(
            opponent_team_id,
            n_recent_matches,
            your_team_id
        )
    
    def export_scouting_report(self, report: Dict[str, Any]) -> str:
        """Export scouting report to formatted text"""
        return self.scouting_generator.export_to_text(report)
    
    def save_scouting_report(self, report: Dict[str, Any], filename: str):
        """Save scouting report to file"""
        text = self.export_scouting_report(report)
        output_path = Path(config.paths.reports_dir) / filename
        with open(output_path, 'w') as f:
            f.write(text)
        return str(output_path)
    
    # ========================================================================
    # Component C: Drafting Assistant Interface
    # ========================================================================
    
    def analyze_draft(self, draft_state: DraftState) -> Dict[str, Any]:
        """
        Analyze a draft in progress
        
        Args:
            draft_state: Current draft state
        
        Returns:
            Analysis including win probabilities and recommendations
        
        Example:
            >>> state = DraftState(
            ...     team1_picks=['Ahri', 'Lee Sin'],
            ...     team1_bans=['Zed'],
            ...     team2_picks=['Jinx'],
            ...     team2_bans=['Yasuo'],
            ...     current_phase='pick1',
            ...     turn=1
            ... )
            >>> analysis = nexus.analyze_draft(state)
        """
        return self.drafting_assistant.analyze_draft(draft_state)
    
    def predict_draft_winner(self, 
                            team1_picks: List[str],
                            team2_picks: List[str]) -> Dict[str, float]:
        """
        Predict win probability based on completed drafts
        
        Returns:
            {'team1': probability, 'team2': probability}
        """
        draft_state = DraftState(
            team1_picks=team1_picks,
            team1_bans=[],
            team2_picks=team2_picks,
            team2_bans=[],
            current_phase='complete',
            turn=1
        )
        return self.drafting_assistant.predictor.predict_win_probability(draft_state)
    
    def get_pick_recommendations(self,
                                current_picks: List[str],
                                current_bans: List[str],
                                opponent_picks: List[str]) -> List[Any]:
        """Get champion pick recommendations"""
        draft_state = DraftState(
            team1_picks=current_picks,
            team1_bans=current_bans,
            team2_picks=opponent_picks,
            team2_bans=[],
            current_phase='pick',
            turn=1
        )
        available = [c for c in self.drafting_assistant.all_champions
                    if c not in current_picks + opponent_picks + current_bans]
        
        return self.drafting_assistant.predictor.recommend_pick(
            draft_state, 1, available
        )
    
    # ========================================================================
    # Component D: Draft Master Game Interface
    # ========================================================================
    
    def start_game(self, player_name: str, difficulty: str = 'medium'):
        """
        Start a new Draft Master game
        
        Args:
            player_name: Player's name
            difficulty: 'easy', 'medium', 'hard', or 'pro'
        
        Returns:
            Game state
        """
        return self.draft_master.start_new_game(player_name, difficulty)
    
    def get_game_actions(self, game_id: str) -> Dict[str, Any]:
        """Get available actions for current game phase"""
        return self.draft_master.get_available_actions(game_id)
    
    def make_game_move(self, 
                      game_id: str,
                      champion: str,
                      time_taken: float = 30.0) -> Dict[str, Any]:
        """Make a move in the game"""
        return self.draft_master.make_move(game_id, champion, time_taken)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Draft Master leaderboard"""
        return self.draft_master.get_leaderboard(limit)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_team_list(self) -> List[Dict[str, str]]:
        """Get list of all teams in the dataset"""
        teams = {}
        for match in self.data['parsed_matches']:
            for team_stat in match['team_stats']:
                teams[team_stat.team_id] = team_stat.team_name
        
        return [{'id': tid, 'name': name} for tid, name in teams.items()]
    
    def get_match_list(self) -> List[Dict[str, Any]]:
        """Get list of all matches"""
        matches = []
        for match in self.data['parsed_matches']:
            metadata = match['metadata']
            matches.append({
                'match_id': metadata.match_id,
                'team1': metadata.team1_name,
                'team2': metadata.team2_name,
                'duration': metadata.duration_seconds,
                'winner': metadata.winner_team_id
            })
        return matches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall dataset statistics"""
        return self.data['statistics']
    
    def _find_match(self, match_id: str):
        """Find match by ID"""
        for match in self.data['parsed_matches']:
            if match['metadata'].match_id == match_id:
                return match
        return None
    
    # ========================================================================
    # Interactive Demo Methods
    # ========================================================================
    
    def demo_all_features(self):
        """Run a demonstration of all features"""
        print("\n" + "=" * 80)
        print("NEXUS COMMANDER - FEATURE DEMONSTRATION")
        print("=" * 80)
        
        # Get a sample team and match
        teams = self.get_team_list()
        if not teams:
            print("No teams found in dataset")
            return
        
        sample_team = teams[0]
        matches = self.get_match_list()
        sample_match = matches[0] if matches else None
        
        print(f"\nUsing sample team: {sample_team['name']} (ID: {sample_team['id']})")
        if sample_match:
            print(f"Using sample match: {sample_match['team1']} vs {sample_match['team2']}")
        
        # Demo 1: AI Coach
        print("\n" + "-" * 80)
        print("DEMO 1: AI ASSISTANT COACH")
        print("-" * 80)
        
        patterns = self.find_team_patterns(sample_team['id'], 5)
        print("\nTeam Signature Patterns:")
        for pattern in patterns['signature_moves']:
            print(f"  • {pattern}")
        
        # Demo 2: Scouting Report
        print("\n" + "-" * 80)
        print("DEMO 2: SCOUTING REPORT GENERATOR")
        print("-" * 80)
        
        print(f"\nGenerating scouting report for {sample_team['name']}...")
        report = self.generate_scouting_report(sample_team['id'], n_recent_matches=5)
        
        if 'error' not in report:
            print(f"\nReport generated with {len(report['sections'])} sections")
            print(f"Confidence: {report['metadata']['confidence_level']}")
            
            # Show executive summary
            if report['sections']:
                summary = report['sections'][0]
                print(f"\n{summary.title}:")
                print(summary.content[:500] + "...")
        
        # Demo 3: Drafting Assistant
        print("\n" + "-" * 80)
        print("DEMO 3: AI DRAFTING ASSISTANT")
        print("-" * 80)
        
        # Simulate a draft state
        sample_draft = DraftState(
            team1_picks=['Ahri', 'Lee Sin'],
            team1_bans=['Zed', 'Yasuo'],
            team2_picks=['Jinx', 'Thresh'],
            team2_bans=['LeBlanc', 'Syndra'],
            current_phase='pick1',
            turn=1
        )
        
        print("\nCurrent Draft State:")
        print(f"  Your picks: {', '.join(sample_draft.team1_picks)}")
        print(f"  Opponent picks: {', '.join(sample_draft.team2_picks)}")
        
        analysis = self.analyze_draft(sample_draft)
        
        print(f"\nWin Probability: {analysis['win_probabilities']['team1']:.1%}")
        
        print("\nTop 3 Recommended Picks:")
        for i, rec in enumerate(analysis['recommendations'][:3], 1):
            print(f"  {i}. {rec.champion} - {rec.priority.upper()}")
            if rec.reasoning:
                print(f"     {rec.reasoning[0]}")
        
        # Demo 4: Draft Master Game
        print("\n" + "-" * 80)
        print("DEMO 4: DRAFT MASTER MINI-GAME")
        print("-" * 80)
        
        game = self.start_game("Demo Player", "medium")
        print(f"\nGame started: {game.game_id}")
        print(f"Historical match: {game.real_team1} vs {game.real_team2}")
        print(f"Difficulty: {game.difficulty}")
        
        actions = self.get_game_actions(game.game_id)
        print(f"\nCurrent phase: {actions['phase_description']}")
        print(f"Action required: {actions['action_type'].upper()}")
        
        if actions['recommendations']:
            print(f"\nHints available ({len(actions['recommendations'])}):")
            for i, rec in enumerate(actions['recommendations'][:3], 1):
                print(f"  {i}. {rec.champion}")
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)


def main():
    """Main entry point"""
    try:
        # Initialize Nexus Commander
        nexus = NexusCommander()
        
        # Run demonstration
        nexus.demo_all_features()
        
        # Show statistics
        print("\n" + "=" * 80)
        print("DATASET STATISTICS")
        print("=" * 80)
        stats = nexus.get_statistics()
        for key, value in stats.items():
            if key != 'team_win_rates':
                print(f"{key}: {value}")
        
        print("\n✓ Nexus Commander ready for use")
        
        return nexus
        
    except Exception as e:
        print(f"\n❌ Error initializing Nexus Commander: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    nexus = main()
