# Nexus Commander - Quick Start Guide

## 🎯 Overview

Nexus Commander is a complete AI-powered esports intelligence platform with four main components:

1. **AI Assistant Coach** - Strategic analysis and coaching insights
2. **Scouting Report Generator** - Automated opponent analysis
3. **AI Drafting Assistant** - Champion draft predictions
4. **Draft Master Game** - Interactive fan engagement

## 📋 Prerequisites

- Python 3.10+
- GRID match JSON files in `/mnt/user-data/uploads/`
- (Optional) API keys for extended features

## ⚡ Quick Start (3 Steps)

### Step 1: Run Tests

```bash
python run_tests.py
```

Expected output:
```
Tests Passed: 6/6 (100%)
🎉 ALL TESTS PASSED - Nexus Commander is ready!
```

### Step 2: Run Demo

```bash
python demo.py
```

This demonstrates all four components with your data.

### Step 3: Use Programmatically

```python
from nexus_commander import NexusCommander

# Initialize
nexus = NexusCommander()

# Get teams
teams = nexus.get_team_list()
print(f"Found {len(teams)} teams")

# Generate scouting report
if teams:
    report = nexus.generate_scouting_report(teams[0]['id'])
    print(nexus.export_scouting_report(report))
```

## 📚 Common Use Cases

### Use Case 1: Pre-Match Preparation

```python
from nexus_commander import NexusCommander

nexus = NexusCommander()

# Scout the opponent
opponent_id = '47558'  # Example: Gen.G
report = nexus.generate_scouting_report(
    opponent_id,
    n_recent_matches=15
)

# Save report for coaching staff
path = nexus.save_scouting_report(
    report,
    'opponent_geng_week3.txt'
)

print(f"Scouting report saved to: {path}")
```

### Use Case 2: In-Game Draft Assistance

```python
from nexus_commander import NexusCommander
from drafting_assistant import DraftState

nexus = NexusCommander()

# Current draft state
draft = DraftState(
    team1_picks=['Ahri', 'Lee Sin'],
    team1_bans=['Zed', 'Yasuo'],
    team2_picks=['Jinx', 'Thresh'],
    team2_bans=['LeBlanc', 'Syndra'],
    current_phase='pick1',
    turn=1
)

# Get analysis
analysis = nexus.analyze_draft(draft)

# Show win probability
print(f"Win Probability: {analysis['win_probabilities']['team1']:.1%}")

# Show recommendations
print("\nTop 3 Picks:")
for i, rec in enumerate(analysis['recommendations'][:3], 1):
    print(f"{i}. {rec.champion} - {rec.priority.upper()}")
    if rec.reasoning:
        print(f"   {rec.reasoning[0]}")
```

### Use Case 3: Post-Match Analysis

```python
from nexus_commander import NexusCommander

nexus = NexusCommander()

# Get match
matches = nexus.get_match_list()
match = matches[0]

# Get your team ID from match
# (normally you'd know this)
teams = nexus.get_team_list()
your_team_id = teams[0]['id']

# Get macro insights
insights = nexus.get_macro_insights(
    match['match_id'],
    your_team_id
)

# Print critical issues
for insight in insights:
    if insight.priority in ['critical', 'high']:
        print(f"\n[{insight.priority.upper()}] {insight.title}")
        print(insight.description)
        print("\nRecommendations:")
        for rec in insight.recommendations:
            print(f"  • {rec}")
```

### Use Case 4: Fan Engagement Game

```python
from nexus_commander import NexusCommander

nexus = NexusCommander()

# Start game
game = nexus.start_game("ProPlayer123", difficulty="hard")

print(f"Game started!")
print(f"Historical Match: {game.real_team1} vs {game.real_team2}")

# Play first move
actions = nexus.get_game_actions(game.game_id)
print(f"Action: {actions['action_type']}")
print(f"Phase: {actions['phase_description']}")

# Show hints
if actions['recommendations']:
    print("\nRecommendations:")
    for rec in actions['recommendations'][:3]:
        print(f"  • {rec.champion}")

# Make move
result = nexus.make_game_move(
    game.game_id,
    actions['recommendations'][0].champion,
    time_taken=15.0
)

print(f"\nScore: {result['player_move']['score']} points")
print(f"Current Total: {result['current_score']}")
```

## 🔍 Component Deep Dive

### Component A: AI Assistant Coach

**Purpose:** Answer strategic questions and provide insights

**Example Questions:**
```python
# Gold analysis
answer = nexus.ask_coach(
    "Why did we fall behind in gold?",
    context={'team_id': '47961', 'match_id': 'game_123'}
)

# Pattern recognition  
answer = nexus.ask_coach(
    "What are this team's signature patterns?",
    context={'team_id': '47558'}
)

# Player performance
answer = nexus.ask_coach(
    "How can our mid laner improve?",
    context={'player_name': 'Chovy', 'match_id': 'game_123'}
)
```

### Component B: Scouting Report Generator

**Purpose:** Generate comprehensive opponent dossiers

**Report Contents:**
- Executive Summary
- Win/Loss Trends
- Draft Patterns
- Macro Strategy
- Player Profiles
- Weaknesses
- Counter-Strategies

**Export Options:**
```python
# Generate report
report = nexus.generate_scouting_report('47558')

# View in console
print(nexus.export_scouting_report(report))

# Save to file
nexus.save_scouting_report(report, 'geng_scouting.txt')
```

### Component C: AI Drafting Assistant

**Purpose:** Real-time draft analysis and predictions

**Features:**
- Win probability calculation
- Pick recommendations
- Ban recommendations
- Champion synergy analysis
- Counter-matchup evaluation

**Usage:**
```python
# Analyze current draft
analysis = nexus.analyze_draft(draft_state)

# Predict final outcome
probs = nexus.predict_draft_winner(
    ['Ahri', 'Lee Sin', 'Jinx', 'Thresh', 'Malphite'],
    ['Zed', 'Nidalee', 'Ezreal', 'Karma', 'Shen']
)
```

### Component D: Draft Master Game

**Purpose:** Interactive game for fans and training

**Difficulty Levels:**
- Easy: AI shows top 5 picks
- Medium: AI shows top 3 picks
- Hard: AI shows only best pick
- Pro: No hints, compete against optimal AI

**Scoring:**
- Optimal pick: 100 points
- Good pick: 75 points
- Acceptable: 50 points
- Time bonus: up to 300 points
- Win probability bonus: up to 500 points

**Full Game Flow:**
```python
# Start game
game = nexus.start_game("Player1", "medium")

# Play through draft
while not game_complete:
    actions = nexus.get_game_actions(game.game_id)
    # Make choice
    result = nexus.make_game_move(game_id, champion)
    if result.get('game_complete'):
        break

# View results
leaderboard = nexus.get_leaderboard()
```

## 🎮 Interactive Mode

Run the demo for an interactive walkthrough:

```bash
python demo.py
```

This will:
1. Load all match data
2. Demonstrate each component
3. Show example outputs
4. Run a complete workflow

## 📊 Data Requirements

**Minimum:**
- 5+ matches
- 2+ teams

**Recommended:**
- 20+ matches for quality insights
- 50+ matches for optimal predictions

**Format:**
- GRID Data API JSON files
- Place in `/mnt/user-data/uploads/`

## 🛠️ Troubleshooting

### No matches found
- Ensure JSON files are in `/mnt/user-data/uploads/`
- Check file naming: `matchID_*.json`

### Empty results
- Data may not have team statistics
- Try with different match files

### Low confidence
- Increase `n_recent_matches` parameter
- Add more historical data

## 📖 Full Documentation

See `README.md` for complete documentation including:
- Detailed API reference
- Architecture overview
- Advanced examples
- Deployment guides

## 💡 Tips

1. **Start Small:** Run quick test first
2. **Use Hints:** Medium difficulty is best for learning
3. **Read Reports:** Scouting reports contain valuable insights
4. **Iterate:** Try different draft combinations
5. **Save Work:** Export reports for offline review

## 🎯 Next Steps

After getting familiar with the basics:

1. Generate reports for all opponents
2. Analyze your team's patterns
3. Practice drafts in game mode
4. Integrate into workflow
5. Explore API customization

---

**Questions?** Refer to README.md or run `python run_tests.py --help`
