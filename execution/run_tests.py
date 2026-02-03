#!/usr/bin/env python3
"""
Nexus Commander - Main Execution Script
Run comprehensive tests and demonstrations
"""

import sys
import traceback
from pathlib import Path


def check_dependencies():
    """Check if required packages are available"""
    required = [
        'pandas',
        'numpy',
        'json'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True


def test_data_loading():
    """Test data ingestion"""
    print("\n" + "=" * 80)
    print("TEST 1: Data Ingestion")
    print("=" * 80)
    
    try:
        from data_ingestion import load_and_parse_all_data
        
        print("Loading match data...")
        data = load_and_parse_all_data()
        
        print(f"✓ Successfully loaded {data['statistics']['total_matches']} matches")
        print(f"✓ Found {data['statistics']['unique_teams']} unique teams")
        print(f"✓ Average game duration: {data['statistics']['avg_duration']:.1f} seconds")
        
        return True, data
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        traceback.print_exc()
        return False, None


def test_ai_coach(data):
    """Test AI Coach component"""
    print("\n" + "=" * 80)
    print("TEST 2: AI Assistant Coach")
    print("=" * 80)
    
    try:
        from ai_coach import AICoachingAssistant
        
        print("Initializing AI Coach...")
        coach = AICoachingAssistant(data['parsed_matches'])
        
        print("✓ AI Coach initialized")
        
        # Test pattern recognition
        teams = set()
        for match in data['parsed_matches']:
            for team in match['team_stats']:
                teams.add(team.team_id)
        
        if teams:
            test_team = list(teams)[0]
            print(f"\nTesting pattern recognition for team: {test_team}")
            
            patterns = coach.analyzer.find_signature_patterns(test_team, 5)
            
            print(f"✓ Found {len(patterns['signature_moves'])} signature moves")
            for i, move in enumerate(patterns['signature_moves'][:3], 1):
                print(f"  {i}. {move}")
        
        return True, coach
        
    except Exception as e:
        print(f"❌ AI Coach test failed: {e}")
        traceback.print_exc()
        return False, None


def test_scouting_report(data, coach):
    """Test Scouting Report Generator"""
    print("\n" + "=" * 80)
    print("TEST 3: Scouting Report Generator")
    print("=" * 80)
    
    try:
        from scouting_report import ScoutingReportGenerator
        
        print("Initializing Scouting Report Generator...")
        generator = ScoutingReportGenerator(data['parsed_matches'], coach.analyzer)
        
        print("✓ Generator initialized")
        
        # Get a team to scout
        teams = set()
        for match in data['parsed_matches']:
            for team in match['team_stats']:
                teams.add((team.team_id, team.team_name))
        
        if teams:
            team_id, team_name = list(teams)[0]
            print(f"\nGenerating report for: {team_name}")
            
            report = generator.generate_report(team_id, n_recent_matches=5)
            
            if 'error' not in report:
                print(f"✓ Report generated with {len(report['sections'])} sections")
                print(f"  Matches analyzed: {report['matches_analyzed']}")
                print(f"  Confidence: {report['metadata']['confidence_level']}")
            else:
                print(f"⚠️  {report['error']}")
        
        return True, generator
        
    except Exception as e:
        print(f"❌ Scouting report test failed: {e}")
        traceback.print_exc()
        return False, None


def test_drafting_assistant(data):
    """Test Drafting Assistant"""
    print("\n" + "=" * 80)
    print("TEST 4: AI Drafting Assistant")
    print("=" * 80)
    
    try:
        from drafting_assistant import DraftingAssistant, DraftState
        
        print("Initializing Drafting Assistant...")
        assistant = DraftingAssistant(data['parsed_matches'])
        
        print(f"✓ Assistant initialized")
        print(f"  Champion pool size: {len(assistant.all_champions)}")
        
        # Test draft prediction
        print("\nTesting draft analysis...")
        
        # Get some champions from data
        all_champs = list(assistant.all_champions)[:10]
        
        test_state = DraftState(
            team1_picks=all_champs[:2],
            team1_bans=all_champs[2:4],
            team2_picks=all_champs[4:6],
            team2_bans=all_champs[6:8],
            current_phase='pick1',
            turn=1
        )
        
        analysis = assistant.analyze_draft(test_state)
        
        print(f"✓ Draft analysis complete")
        print(f"  Team 1 Win Probability: {analysis['win_probabilities']['team1']:.1%}")
        print(f"  Team 2 Win Probability: {analysis['win_probabilities']['team2']:.1%}")
        
        if analysis['recommendations']:
            print(f"\nTop 3 Recommendations:")
            for i, rec in enumerate(analysis['recommendations'][:3], 1):
                print(f"  {i}. {rec.champion} ({rec.priority})")
        
        return True, assistant
        
    except Exception as e:
        print(f"❌ Drafting assistant test failed: {e}")
        traceback.print_exc()
        return False, None


def test_draft_master_game(data, assistant):
    """Test Draft Master Game"""
    print("\n" + "=" * 80)
    print("TEST 5: Draft Master Mini-Game")
    print("=" * 80)
    
    try:
        from draft_master_game import DraftMasterGame
        
        print("Initializing Draft Master Game...")
        game_engine = DraftMasterGame(data['parsed_matches'], assistant)
        
        print("✓ Game engine initialized")
        
        # Start a test game
        print("\nStarting test game...")
        game = game_engine.start_new_game("Test Player", "medium")
        
        print(f"✓ Game created: {game.game_id}")
        print(f"  Difficulty: {game.difficulty}")
        print(f"  Match: {game.real_team1} vs {game.real_team2}")
        
        # Get first action
        actions = game_engine.get_available_actions(game.game_id)
        
        print(f"\nFirst action:")
        print(f"  Phase: {actions['phase_description']}")
        print(f"  Action: {actions['action_type']}")
        print(f"  Recommendations: {len(actions['recommendations'])}")
        
        return True, game_engine
        
    except Exception as e:
        print(f"❌ Draft Master test failed: {e}")
        traceback.print_exc()
        return False, None


def test_integration():
    """Test full platform integration"""
    print("\n" + "=" * 80)
    print("TEST 6: Full Platform Integration")
    print("=" * 80)
    
    try:
        from nexus_commander import NexusCommander
        
        print("Initializing Nexus Commander (full platform)...")
        nexus = NexusCommander()
        
        if nexus.is_ready:
            print("✓ Platform fully initialized and ready")
            
            # Quick functionality test
            teams = nexus.get_team_list()
            matches = nexus.get_match_list()
            
            print(f"\n  Teams available: {len(teams)}")
            print(f"  Matches available: {len(matches)}")
            
            # Test one query
            if teams:
                test_team = teams[0]
                patterns = nexus.find_team_patterns(test_team['id'], 3)
                print(f"  Pattern analysis working: ✓")
            
            return True, nexus
        else:
            print("⚠️  Platform initialized with warnings")
            return False, None
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        traceback.print_exc()
        return False, None


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "=" * 80)
    print("NEXUS COMMANDER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return False
    
    print("✓ All dependencies available")
    
    # Run tests
    results = {}
    
    # Test 1: Data Loading
    success, data = test_data_loading()
    results['data_loading'] = success
    
    if not success or not data:
        print("\n❌ Cannot continue without data")
        return False
    
    # Test 2: AI Coach
    success, coach = test_ai_coach(data)
    results['ai_coach'] = success
    
    # Test 3: Scouting Report
    success, generator = test_scouting_report(data, coach) if coach else (False, None)
    results['scouting'] = success
    
    # Test 4: Drafting Assistant
    success, assistant = test_drafting_assistant(data)
    results['drafting'] = success
    
    # Test 5: Draft Master Game
    success, game_engine = test_draft_master_game(data, assistant) if assistant else (False, None)
    results['game'] = success
    
    # Test 6: Integration
    success, nexus = test_integration()
    results['integration'] = success
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name.upper():<20} {status}")
    
    print("\n" + "-" * 80)
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Nexus Commander is ready!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Nexus Commander Test Suite')
    parser.add_argument('--demo', action='store_true', 
                       help='Run interactive demo instead of tests')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick test (data loading only)')
    
    args = parser.parse_args()
    
    if args.demo:
        # Run the demo
        print("Running interactive demo...")
        from demo import main as demo_main
        demo_main()
    elif args.quick:
        # Quick test
        print("Running quick test...")
        check_dependencies()
        test_data_loading()
    else:
        # Full test suite
        success = run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
