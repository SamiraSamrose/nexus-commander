"""
Nexus Commander - Flask Backend API Server
Provides REST API endpoints for the web demo
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_commander import NexusCommander
from drafting_assistant import DraftState

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize Nexus Commander on startup
print("Initializing Nexus Commander backend...")
nexus = NexusCommander()

@app.route('/api/initialize', methods=['GET'])
def initialize():
    """Get initialization data"""
    stats = nexus.get_statistics()
    teams = nexus.get_team_list()
    
    return jsonify({
        'status': 'ready',
        'statistics': stats,
        'teams': teams,
        'champions': list(nexus.drafting_assistant.all_champions)
    })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get list of all teams"""
    return jsonify(nexus.get_team_list())

@app.route('/api/matches', methods=['GET'])
def get_matches():
    """Get list of all matches"""
    return jsonify(nexus.get_match_list())

@app.route('/api/champions', methods=['GET'])
def get_champions():
    """Get list of all champions"""
    return jsonify(list(nexus.drafting_assistant.all_champions))

# ========================================================================
# AI COACH ENDPOINTS
# ========================================================================

@app.route('/api/coach/ask', methods=['POST'])
def ask_coach():
    """Ask the AI coach a question"""
    data = request.json
    question = data.get('question', '')
    context = data.get('context', {})
    
    response = nexus.ask_coach(question, context)
    
    return jsonify({
        'response': response
    })

@app.route('/api/coach/patterns/<team_id>', methods=['GET'])
def get_team_patterns(team_id):
    """Get team signature patterns"""
    n_matches = request.args.get('n_matches', 10, type=int)
    
    patterns = nexus.find_team_patterns(team_id, n_matches)
    
    return jsonify(patterns)

@app.route('/api/coach/macro', methods=['POST'])
def get_macro_insights():
    """Get macro insights for a match"""
    data = request.json
    match_id = data.get('match_id')
    team_id = data.get('team_id')
    
    insights = nexus.get_macro_insights(match_id, team_id)
    
    # Convert CoachingInsight objects to dicts
    insights_data = []
    for insight in insights:
        insights_data.append({
            'category': insight.category,
            'priority': insight.priority,
            'title': insight.title,
            'description': insight.description,
            'evidence': insight.evidence,
            'recommendations': insight.recommendations,
            'confidence': insight.confidence
        })
    
    return jsonify(insights_data)

# ========================================================================
# SCOUTING REPORT ENDPOINTS
# ========================================================================

@app.route('/api/scouting/generate', methods=['POST'])
def generate_scouting_report():
    """Generate scouting report for opponent"""
    data = request.json
    opponent_id = data.get('opponent_id')
    n_matches = data.get('n_matches', 20)
    your_team_id = data.get('your_team_id')
    
    report = nexus.generate_scouting_report(
        opponent_id,
        n_matches,
        your_team_id
    )
    
    # Convert report sections to serializable format
    if 'error' not in report:
        sections_data = []
        for section in report['sections']:
            sections_data.append({
                'title': section.title,
                'content': section.content,
                'priority': section.priority,
                'insights': section.insights
            })
        report['sections'] = sections_data
    
    return jsonify(report)

@app.route('/api/scouting/export', methods=['POST'])
def export_scouting_report():
    """Export scouting report as text"""
    data = request.json
    report = data.get('report')
    
    # Reconstruct report for export
    text = nexus.scouting_generator.export_to_text(report)
    
    return jsonify({
        'text': text
    })

# ========================================================================
# DRAFTING ASSISTANT ENDPOINTS
# ========================================================================

@app.route('/api/draft/analyze', methods=['POST'])
def analyze_draft():
    """Analyze current draft state"""
    data = request.json
    
    draft_state = DraftState(
        team1_picks=data.get('team1_picks', []),
        team1_bans=data.get('team1_bans', []),
        team2_picks=data.get('team2_picks', []),
        team2_bans=data.get('team2_bans', []),
        current_phase=data.get('current_phase', 'pick'),
        turn=data.get('turn', 1)
    )
    
    analysis = nexus.analyze_draft(draft_state)
    
    # Convert recommendations to serializable format
    recommendations_data = []
    for rec in analysis['recommendations']:
        recommendations_data.append({
            'champion': rec.champion,
            'win_rate_impact': rec.win_rate_impact,
            'reasoning': rec.reasoning,
            'synergies': rec.synergies,
            'counters': rec.counters,
            'priority': rec.priority,
            'confidence': rec.confidence
        })
    
    analysis['recommendations'] = recommendations_data
    
    return jsonify(analysis)

@app.route('/api/draft/predict', methods=['POST'])
def predict_draft():
    """Predict win probability for complete drafts"""
    data = request.json
    
    team1_picks = data.get('team1_picks', [])
    team2_picks = data.get('team2_picks', [])
    
    prediction = nexus.predict_draft_winner(team1_picks, team2_picks)
    
    return jsonify(prediction)

# ========================================================================
# DRAFT MASTER GAME ENDPOINTS
# ========================================================================

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new Draft Master game"""
    data = request.json
    player_name = data.get('player_name', 'Player')
    difficulty = data.get('difficulty', 'medium')
    
    game_state = nexus.start_game(player_name, difficulty)
    
    # Convert to serializable format
    return jsonify({
        'game_id': game_state.game_id,
        'player_name': game_state.player_name,
        'difficulty': game_state.difficulty,
        'historical_match_id': game_state.historical_match_id,
        'tournament': game_state.tournament,
        'real_team1': game_state.real_team1,
        'real_team2': game_state.real_team2,
        'current_phase': game_state.current_phase,
        'score': game_state.score
    })

@app.route('/api/game/actions/<game_id>', methods=['GET'])
def get_game_actions(game_id):
    """Get available actions for game phase"""
    actions = nexus.get_game_actions(game_id)
    
    # Convert recommendations
    if 'recommendations' in actions:
        recs_data = []
        for rec in actions['recommendations']:
            recs_data.append({
                'champion': rec.champion,
                'reasoning': rec.reasoning,
                'priority': rec.priority
            })
        actions['recommendations'] = recs_data
    
    return jsonify(actions)

@app.route('/api/game/move', methods=['POST'])
def make_game_move():
    """Make a move in the game"""
    data = request.json
    game_id = data.get('game_id')
    champion = data.get('champion')
    time_taken = data.get('time_taken', 30.0)
    
    result = nexus.make_game_move(game_id, champion, time_taken)
    
    return jsonify(result)

@app.route('/api/game/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get game leaderboard"""
    limit = request.args.get('limit', 10, type=int)
    
    leaderboard = nexus.get_leaderboard(limit)
    
    return jsonify(leaderboard)

# ========================================================================
# UTILITY ENDPOINTS
# ========================================================================

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get platform statistics"""
    return jsonify(nexus.get_statistics())

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'platform': 'Nexus Commander',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("NEXUS COMMANDER BACKEND API SERVER")
    print("=" * 80)
    print("\nBackend is ready!")
    print("API available at: http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /api/initialize      - Get initialization data")
    print("  GET  /api/teams            - Get teams list")
    print("  POST /api/coach/ask        - Ask AI coach")
    print("  POST /api/scouting/generate - Generate scouting report")
    print("  POST /api/draft/analyze    - Analyze draft")
    print("  POST /api/game/start       - Start game")
    print("  GET  /api/health           - Health check")
    print("\n" + "=" * 80 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
