# Nexus Commander

**The Unified AI-Esports Intelligence & Management Platform**

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- 8GB+ RAM recommended
- (Optional) CUDA-compatible GPU for ML acceleration

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/nexus-commander.git
cd nexus-commander
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create a `.env` file:

```env
# API Keys (optional - for extended features)
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
GRID_API_KEY=your_key_here

# Cloud Services (optional)
GCP_PROJECT_ID=your_project
PINECONE_API_KEY=your_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Configuration
USE_GPU=false
```

### Step 4: Prepare Data

Place your GRID match JSON files in the `data/uploads/` directory:

```bash
mkdir -p data/uploads
cp /path/to/your/match_files/*.json data/uploads/
```

---

## Quick Start

### Basic Usage

```python
from nexus_commander import NexusCommander

# Initialize platform
nexus = NexusCommander(data_directory="data/uploads")

# Component A: Ask the AI Coach
response = nexus.ask_coach(
    "What are the team's strategic patterns?",
    context={'team_id': '47558'}
)
print(response)

# Component B: Generate Scouting Report
report = nexus.generate_scouting_report(
    opponent_team_id='47558',
    n_recent_matches=20
)
print(nexus.export_scouting_report(report))

# Component C: Analyze Draft
from drafting_assistant import DraftState

state = DraftState(
    team1_picks=['Ahri', 'Lee Sin'],
    team1_bans=['Zed'],
    team2_picks=['Jinx'],
    team2_bans=['Yasuo'],
    current_phase='pick1',
    turn=1
)

analysis = nexus.analyze_draft(state)
print(f"Win Probability: {analysis['win_probabilities']['team1']:.1%}")

# Component D: Start Draft Master Game
game = nexus.start_game("Player1", difficulty="medium")
actions = nexus.get_game_actions(game.game_id)
```

### Run Complete Demo

```bash
python demo.py
```

This will demonstrate all four components with example data.

---

## Component Documentation

### AI Assistant Coach API

#### `ask_coach(question, context)`

Ask the AI coach a strategic question.

**Parameters:**
- `question` (str): Natural language question
- `context` (dict): Context with keys like `team_id`, `match_id`, `player_name`

**Returns:** String with detailed analysis

**Example:**
```python
answer = nexus.ask_coach(
    "Why did we lose Baron control?",
    context={'team_id': '47961', 'match_id': 'match_123'}
)
```

#### `find_team_patterns(team_id, n_matches)`

Identify signature patterns for a team.

**Parameters:**
- `team_id` (str): Team identifier
- `n_matches` (int): Number of recent matches to analyze

**Returns:** Dictionary with patterns and confidence

### Scouting Report API

#### `generate_scouting_report(opponent_team_id, n_recent_matches, your_team_id)`

Generate comprehensive scouting report.

**Parameters:**
- `opponent_team_id` (str): Target opponent ID
- `n_recent_matches` (int): Number of matches to analyze (default: 20)
- `your_team_id` (str, optional): Your team ID for H2H analysis

**Returns:** Dictionary containing full report structure

#### `export_scouting_report(report)`

Convert report to formatted text.

**Returns:** String containing formatted report

#### `save_scouting_report(report, filename)`

Save report to file in outputs directory.

### Drafting Assistant API

#### `analyze_draft(draft_state)`

Analyze current draft state.

**Parameters:**
- `draft_state` (DraftState): Current draft configuration

**Returns:** Dictionary with probabilities and recommendations

#### `predict_draft_winner(team1_picks, team2_picks)`

Predict winner from complete drafts.

**Parameters:**
- `team1_picks` (List[str]): Team 1 champion picks
- `team2_picks` (List[str]): Team 2 champion picks

**Returns:** Dictionary with win probabilities

### Draft Master Game API

#### `start_game(player_name, difficulty)`

Start new Draft Master game.

**Parameters:**
- `player_name` (str): Player identifier
- `difficulty` (str): 'easy', 'medium', 'hard', or 'pro'

**Returns:** GameState object

#### `make_game_move(game_id, champion, time_taken)`

Submit a draft move.

**Parameters:**
- `game_id` (str): Game identifier
- `champion` (str): Chosen champion
- `time_taken` (float): Seconds taken to decide

**Returns:** Move result with scoring

---

## Examples

### Example 1: Complete Match Analysis

```python
from nexus_commander import NexusCommander

nexus = NexusCommander()

# Get match list
matches = nexus.get_match_list()
match = matches[0]

# Analyze from both teams' perspectives
for team_stat in match['team_stats']:
    insights = nexus.get_macro_insights(
        match['metadata'].match_id,
        team_stat.team_id
    )
    
    print(f"\n{team_stat.team_name} Analysis:")
    for insight in insights:
        print(f"  [{insight.priority}] {insight.title}")
```

### Example 2: Pre-Match Preparation Workflow

```python
# 1. Scout the opponent
opponent_id = '47558'
report = nexus.generate_scouting_report(opponent_id, n_recent_matches=15)

# 2. Identify their patterns
patterns = nexus.find_team_patterns(opponent_id, 10)

# 3. Prepare draft strategy
draft_state = DraftState(
    team1_picks=[],
    team1_bans=[],
    team2_picks=[],
    team2_bans=[],
    current_phase='ban1',
    turn=1
)

analysis = nexus.analyze_draft(draft_state)

print("Recommended Priority Bans:")
for rec in analysis['recommendations'][:5]:
    print(f"  • {rec.champion}: {rec.reasoning[0]}")

# 4. Save preparation materials
nexus.save_scouting_report(report, f"opponent_{opponent_id}_scouting.txt")
```

### Example 3: Interactive Draft Session

```python
# Simulate a full draft
current_draft = DraftState(
    team1_picks=[],
    team1_bans=[],
    team2_picks=[],
    team2_bans=[],
    current_phase='ban1',
    turn=1
)

phases = ['ban'] * 6 + ['pick'] * 5

for i, phase in enumerate(phases):
    current_draft.current_phase = phase
    current_draft.turn = 1 if i % 2 == 0 else 2
    
    analysis = nexus.analyze_draft(current_draft)
    
    print(f"\nPhase {i+1}: {phase.upper()}")
    print(f"Top recommendation: {analysis['recommendations'][0].champion}")
    
    # Simulate choice
    chosen = analysis['recommendations'][0].champion
    
    if phase == 'ban':
        if current_draft.turn == 1:
            current_draft.team1_bans.append(chosen)
        else:
            current_draft.team2_bans.append(chosen)
    else:
        if current_draft.turn == 1:
            current_draft.team1_picks.append(chosen)
        else:
            current_draft.team2_picks.append(chosen)

# Final prediction
final_probs = nexus.predict_draft_winner(
    current_draft.team1_picks,
    current_draft.team2_picks
)

print(f"\nFinal Win Probability: {final_probs['team1']:.1%}")
```

---

## Data Format

### Input: GRID Match JSON Structure

Expected format from GRID Data API:

```json
{
  "seriesState": {
    "games": [{
      "draftActions": [...],
      "playerStates": [...],
      "teamStates": [...],
      "clock": {...},
      "snapshots": [...]
    }]
  }
}
```

### Output: Parsed Match Structure

Internal representation:

```python
{
    'metadata': MatchMetadata(...),
    'draft': DraftData(...),
    'player_stats': [PlayerStats(...)],
    'team_stats': [TeamStats(...)],
    'timeline': {...}
}
```

See `data_ingestion.py` for complete schema definitions.

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│                 Nexus Commander                      │
│                                                      │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ AI Coach   │  │  Scouting    │  │  Drafting   │ │
│  │ (RAG)      │  │  Generator   │  │  Assistant  │ │
│  └────────────┘  └──────────────┘  └─────────────┘ │
│         │               │                  │        │
│         └───────────────┴──────────────────┘        │
│                         │                           │
│              ┌──────────▼──────────┐                │
│              │   Data Ingestion    │                │
│              │   & Processing      │                │
│              └──────────┬──────────┘                │
│                         │                           │
│              ┌──────────▼──────────┐                │
│              │  GRID Match JSONs   │                │
│              └─────────────────────┘                │
└─────────────────────────────────────────────────────┘
```

### Data Flow

1. **Ingestion**: Load GRID JSON files → Parse into structured format
2. **Processing**: Extract features → Build champion graph → Train models
3. **Analysis**: Query AI coach → Generate reports → Predict drafts
4. **Output**: Text reports → JSON responses → Game states

---

## Future Enhancements

### Planned Features

- [ ] **Real-time Live Match Analysis**: Integration with live game streams
- [ ] **Multimodal AI**: Video analysis of gameplay with computer vision
- [ ] **Temporal Fusion Transformers**: Time-series prediction for next team fight
- [ ] **Web Dashboard**: Next.js frontend with interactive visualizations
- [ ] **API Endpoints**: RESTful API for external integrations
- [ ] **Cloud Deployment**: AWS Lambda + Step Functions orchestration
- [ ] **Mobile App**: React Native companion app
- [ ] **Voice Assistant**: Audio-based coaching interface

### ML Model Improvements

- [ ] Fine-tune GNN on larger champion pool
- [ ] Implement Monte Carlo Tree Search for draft simulation
- [ ] Add player-specific performance models
- [ ] Integrate external meta data sources
- [ ] Build recommendation system for team composition

---


