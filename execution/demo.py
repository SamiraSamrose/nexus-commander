"""
Nexus Commander - Comprehensive Demo Script
Demonstrates all four key components with real examples
"""

from nexus_commander import NexusCommander
from drafting_assistant import DraftState
import json


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_ai_coach(nexus: NexusCommander):
    """Demonstrate AI Assistant Coach capabilities"""
    print_section("COMPONENT A: AI ASSISTANT COACH")
    
    # Get first match for demo
    matches = nexus.get_match_list()
    if not matches:
        print("No matches available")
        return
    
    match = matches[0]
    teams = nexus.get_team_list()
    team = teams[0] if teams else None
    
    if not team:
        print("No teams available")
        return
    
    print(f"Analyzing team: {team['name']}")
    print(f"Team ID: {team['id']}")
    
    # Demo 1: Find signature patterns
    print("\n" + "-" * 80)
    print("Finding Signature Patterns...")
    print("-" * 80)
    
    patterns = nexus.find_team_patterns(team['id'], n_matches=5)
    
    print(f"\nConfidence: {patterns['confidence']:.0%}")
    print("\nSignature Moves Identified:")
    for i, move in enumerate(patterns['signature_moves'], 1):
        print(f"  {i}. {move}")
    
    # Demo 2: Strategic question
    print("\n" + "-" * 80)
    print("Strategic Analysis Query")
    print("-" * 80)
    
    print("\nQuestion: What are the team's strategic patterns?")
    
    response = nexus.ask_coach(
        "What are the strategic patterns for this team?",
        context={'team_id': team['id']}
    )
    
    print("\nCoach Response:")
    print(response)
    
    # Demo 3: Macro insights for a specific match
    if match:
        print("\n" + "-" * 80)
        print("Match-Specific Macro Analysis")
        print("-" * 80)
        
        print(f"\nAnalyzing: {match['team1']} vs {match['team2']}")
        
        # Find team ID from match
        for parsed_match in nexus.data['parsed_matches']:
            if parsed_match['metadata'].match_id == match['match_id']:
                team_id = parsed_match['team_stats'][0].team_id
                
                insights = nexus.get_macro_insights(match['match_id'], team_id)
                
                if insights:
                    print(f"\nFound {len(insights)} macro-level insights:")
                    for insight in insights[:3]:
                        print(f"\n  [{insight.priority.upper()}] {insight.title}")
                        print(f"  {insight.description}")
                        if insight.recommendations:
                            print(f"  Recommendation: {insight.recommendations[0]}")
                else:
                    print("\nNo critical macro issues identified - solid play!")
                
                break


def demo_scouting_report(nexus: NexusCommander):
    """Demonstrate Scouting Report Generator"""
    print_section("COMPONENT B: AUTOMATED SCOUTING REPORT GENERATOR")
    
    teams = nexus.get_team_list()
    if len(teams) < 2:
        print("Need at least 2 teams for scouting demo")
        return
    
    opponent = teams[0]
    your_team = teams[1] if len(teams) > 1 else None
    
    print(f"Generating scouting report for: {opponent['name']}")
    if your_team:
        print(f"Your team: {your_team['name']}")
    
    print("\nAnalyzing last 10 matches...")
    
    # Generate report
    report = nexus.generate_scouting_report(
        opponent['id'],
        n_recent_matches=10,
        your_team_id=your_team['id'] if your_team else None
    )
    
    if 'error' in report:
        print(f"Error: {report['error']}")
        return
    
    print(f"\n✓ Report generated successfully")
    print(f"  Matches analyzed: {report['matches_analyzed']}")
    print(f"  Sections: {len(report['sections'])}")
    print(f"  Confidence: {report['metadata']['confidence_level']}")
    
    # Display key sections
    print("\n" + "-" * 80)
    print("SCOUTING REPORT PREVIEW")
    print("-" * 80)
    
    for section in report['sections'][:4]:  # Show first 4 sections
        print(f"\n📋 {section.title}")
        print("-" * len(section.title))
        
        # Show first 300 chars of content
        content_preview = section.content[:300]
        if len(section.content) > 300:
            content_preview += "..."
        
        print(content_preview)
        
        if section.insights:
            print(f"\n  Key Insights:")
            for insight in section.insights[:2]:
                print(f"    • {insight}")
    
    # Save full report
    print("\n" + "-" * 80)
    print("Saving full report...")
    
    filename = f"scouting_report_{opponent['name'].replace(' ', '_')}.txt"
    report_path = nexus.save_scouting_report(report, filename)
    print(f"✓ Full report saved to: {report_path}")


def demo_drafting_assistant(nexus: NexusCommander):
    """Demonstrate AI Drafting Assistant"""
    print_section("COMPONENT C: AI DRAFTING ASSISTANT & PREDICTOR")
    
    # Get champion pool
    all_champions = list(nexus.drafting_assistant.all_champions)
    
    if len(all_champions) < 20:
        print("Insufficient champion data")
        return
    
    print("Champion Pool Size:", len(all_champions))
    
    # Demo 1: Early draft analysis
    print("\n" + "-" * 80)
    print("SCENARIO 1: Early Draft Phase")
    print("-" * 80)
    
    draft_state_early = DraftState(
        team1_picks=['Ahri', 'Lee Sin'],
        team1_bans=['Zed', 'Yasuo', 'Syndra'],
        team2_picks=['Jinx', 'Thresh'],
        team2_bans=['LeBlanc', 'Akali', 'Katarina'],
        current_phase='pick1',
        turn=1
    )
    
    print("\nCurrent Draft:")
    print(f"  Your Picks: {', '.join(draft_state_early.team1_picks)}")
    print(f"  Your Bans: {', '.join(draft_state_early.team1_bans)}")
    print(f"  Opponent Picks: {', '.join(draft_state_early.team2_picks)}")
    print(f"  Opponent Bans: {', '.join(draft_state_early.team2_bans)}")
    
    analysis_early = nexus.analyze_draft(draft_state_early)
    
    print(f"\n📊 Win Probability Analysis:")
    print(f"  Your Team: {analysis_early['win_probabilities']['team1']:.1%}")
    print(f"  Opponent: {analysis_early['win_probabilities']['team2']:.1%}")
    
    print(f"\n🎯 Top 5 Recommended Picks:")
    for i, rec in enumerate(analysis_early['recommendations'][:5], 1):
        print(f"\n  {i}. {rec.champion.upper()} [{rec.priority.upper()}]")
        print(f"     Win Rate Impact: {rec.win_rate_impact:+.1%}")
        if rec.reasoning:
            for reason in rec.reasoning[:2]:
                print(f"     • {reason}")
    
    # Demo 2: Complete draft comparison
    print("\n" + "-" * 80)
    print("SCENARIO 2: Complete Draft Comparison")
    print("-" * 80)
    
    # Two complete drafts
    draft_a = {
        'name': 'Composition A (Poke)',
        'picks': ['Jayce', 'Nidalee', 'Xerath', 'Ezreal', 'Karma']
    }
    
    draft_b = {
        'name': 'Composition B (Engage)',
        'picks': ['Malphite', 'Jarvan IV', 'Orianna', 'Ashe', 'Leona']
    }
    
    print(f"\n{draft_a['name']}: {', '.join(draft_a['picks'])}")
    print(f"{draft_b['name']}: {', '.join(draft_b['picks'])}")
    
    prediction = nexus.predict_draft_winner(draft_a['picks'], draft_b['picks'])
    
    print(f"\n📊 Predicted Win Probabilities:")
    print(f"  {draft_a['name']}: {prediction['team1']:.1%}")
    print(f"  {draft_b['name']}: {prediction['team2']:.1%}")
    
    winner = draft_a['name'] if prediction['team1'] > prediction['team2'] else draft_b['name']
    confidence = abs(prediction['team1'] - prediction['team2'])
    
    print(f"\n🏆 Predicted Winner: {winner}")
    print(f"  Confidence: {confidence:.1%}")


def demo_draft_master_game(nexus: NexusCommander):
    """Demonstrate Draft Master Mini-Game"""
    print_section("COMPONENT D: DRAFT MASTER MINI-GAME")
    
    # Start a game
    print("Starting new Draft Master game...")
    
    game = nexus.start_game("Demo Player", difficulty="medium")
    
    print(f"\n✓ Game Created: {game.game_id}")
    print(f"  Player: {game.player_name}")
    print(f"  Difficulty: {game.difficulty.upper()}")
    print(f"  Historical Match: {game.real_team1} vs {game.real_team2}")
    print(f"  Tournament: {game.tournament}")
    
    # Play first few moves
    print("\n" + "-" * 80)
    print("GAME SIMULATION - First 3 Moves")
    print("-" * 80)
    
    for move_num in range(3):
        print(f"\n--- Move {move_num + 1} ---")
        
        # Get available actions
        actions = nexus.get_game_actions(game.game_id)
        
        print(f"Phase: {actions['phase_description']}")
        print(f"Action: {actions['action_type'].upper()}")
        print(f"Time Limit: {actions['time_limit']} seconds")
        
        # Show hints
        if actions['recommendations']:
            print(f"\n💡 Hints (Top {len(actions['recommendations'])}):")
            for i, rec in enumerate(actions['recommendations'], 1):
                print(f"  {i}. {rec.champion}")
                if rec.reasoning:
                    print(f"     → {rec.reasoning[0][:50]}...")
        
        # Make a move (choose first recommendation or random)
        if actions['recommendations']:
            chosen = actions['recommendations'][0].champion
        elif actions['available_champions']:
            import random
            chosen = random.choice(actions['available_champions'][:10])
        else:
            print("No available champions!")
            break
        
        print(f"\n✅ Player chooses: {chosen}")
        
        # Submit move
        result = nexus.make_game_move(game.game_id, chosen, time_taken=15.0)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            break
        
        # Show result
        print(f"\n📊 Move Score: {result['player_move']['score']} points")
        print(f"   Reasoning: {result['player_move']['reasoning']}")
        
        print(f"\n🤖 AI Response: {result['ai_move']['champion']}")
        print(f"   {result['ai_move']['reasoning']}")
        
        print(f"\n📈 Current Total Score: {result['current_score']}")
        
        if result.get('game_complete'):
            print("\n" + "-" * 80)
            print("GAME COMPLETE!")
            print("-" * 80)
            
            final = result['final_results']
            
            print(f"\n🏆 Final Score: {final['final_score']['total_score']}")
            print(f"   Rating: {final['final_score']['rating']}")
            print(f"   Rank: {final['final_score']['rank']}")
            print(f"\n📊 Win Probability: {final['win_probability']:.1%}")
            
            print(f"\nYour Draft:")
            for pick in final['player_draft']['picks']:
                print(f"  • {pick}")
            
            break
    
    # Show leaderboard
    print("\n" + "-" * 80)
    print("LEADERBOARD (Top 5)")
    print("-" * 80)
    
    leaderboard = nexus.get_leaderboard(5)
    
    if leaderboard:
        print(f"\n{'Rank':<6} {'Player':<20} {'Score':<10} {'Rating':<15} {'Difficulty'}")
        print("-" * 70)
        for entry in leaderboard:
            print(f"{entry['rank']:<6} {entry['player_name']:<20} "
                  f"{entry['score']:<10} {entry['rating']:<15} {entry['difficulty']}")
    else:
        print("No completed games yet")


def demo_complete_workflow(nexus: NexusCommander):
    """Demonstrate a complete workflow using all components"""
    print_section("COMPLETE WORKFLOW: PREPARING FOR A MATCH")
    
    teams = nexus.get_team_list()
    if len(teams) < 2:
        print("Need at least 2 teams")
        return
    
    your_team = teams[0]
    opponent = teams[1]
    
    print(f"Scenario: {your_team['name']} preparing to face {opponent['name']}")
    
    # Step 1: Generate scouting report
    print("\n📋 STEP 1: Generate Opponent Scouting Report")
    print("-" * 80)
    
    report = nexus.generate_scouting_report(opponent['id'], n_recent_matches=10)
    
    if 'error' not in report:
        print(f"✓ Scouting report generated ({report['matches_analyzed']} matches analyzed)")
        
        # Extract key insights
        for section in report['sections'][:2]:
            print(f"\n{section.title}:")
            for insight in section.insights[:2]:
                print(f"  • {insight}")
    
    # Step 2: Analyze historical matchup
    print("\n📊 STEP 2: Review Team Patterns")
    print("-" * 80)
    
    patterns = nexus.find_team_patterns(opponent['id'], 5)
    
    print("Opponent's Signature Moves:")
    for move in patterns['signature_moves'][:3]:
        print(f"  • {move}")
    
    # Step 3: Draft preparation
    print("\n🎯 STEP 3: Draft Strategy Preparation")
    print("-" * 80)
    
    print("\nRecommended ban targets based on scouting:")
    
    # Get draft recommendations for ban phase
    draft_state = DraftState(
        team1_picks=[],
        team1_bans=[],
        team2_picks=[],
        team2_bans=[],
        current_phase='ban1',
        turn=1
    )
    
    analysis = nexus.analyze_draft(draft_state)
    
    print("\nTop priority bans:")
    for i, rec in enumerate(analysis['recommendations'][:5], 1):
        print(f"  {i}. {rec.champion} - {rec.priority.upper()}")
    
    # Step 4: In-game coaching
    print("\n🎓 STEP 4: In-Game Coaching Focus")
    print("-" * 80)
    
    print("\nKey coaching points for this matchup:")
    print("  • Focus on early dragon control (opponent prioritizes soul)")
    print("  • Ward Baron pit around 22-minute mark")
    print("  • Target identified weak link in opponent's roster")
    print("  • Maintain vision control in jungle")
    
    print("\n✓ Team is prepared for the match!")


def main():
    """Main demo execution"""
    print("\n" + "=" * 80)
    print(" " * 20 + "NEXUS COMMANDER")
    print(" " * 10 + "The Unified AI-Esports Intelligence Platform")
    print("=" * 80)
    
    # Initialize
    print("\nInitializing platform...")
    nexus = NexusCommander()
    
    if not nexus or not nexus.is_ready:
        print("Failed to initialize Nexus Commander")
        return
    
    # Run individual component demos
    demo_ai_coach(nexus)
    demo_scouting_report(nexus)
    demo_drafting_assistant(nexus)
    demo_draft_master_game(nexus)
    
    # Run complete workflow
    demo_complete_workflow(nexus)
    
    # Summary
    print_section("DEMONSTRATION COMPLETE")
    
    print("All four components demonstrated:")
    print("  ✓ Component A: AI Assistant Coach")
    print("  ✓ Component B: Automated Scouting Reports")
    print("  ✓ Component C: AI Drafting Assistant")
    print("  ✓ Component D: Draft Master Mini-Game")
    
    print("\nNexus Commander is ready for production use!")
    print("\nFor more information, see README.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
