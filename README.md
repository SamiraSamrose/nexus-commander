# Nexus Commander - The Unified AI-Esports Intelligence Platform

A comprehensive end-to-end platform for professional esports teams and fans, powered by AI and machine learning. Nexus Commander bridges the gap between raw telemetry data and high-level strategic insights.

Nexus Commander is a Python platform that ingests GRID Data API match JSON files and runs four analysis pipelines on the parsed data. The data layer reads 19 JSON files, parses `seriesState.games` into typed dataclasses (MatchMetadata, DraftData, PlayerStats, TeamStats), and builds a Pandas DataFrame. An orchestrator class (NexusCommander) initialises all components in a fixed sequence and exposes a unified interface.

It is designed to give professional esports teams and coaches a competitive edge through:

- **AI-Powered Analysis**: Strategic insights from match telemetry data
- **Automated Scouting**: Generate comprehensive opponent reports in seconds
- **Draft Assistance**: GNN-based champion draft predictions and recommendations
- **Fan Engagement**: Interactive mini-games for community engagement

## Target audience

Primary users: esports coaching staff and analysts who need to process opponent match data before a match. Secondary: esports content platforms adding interactive fan features. The system reads match JSON files at startup, builds internal data structures once, and serves queries and game sessions from those structures for the lifetime of the process.

---
## Key Features

 **Unified Data Pipeline**: Ingest and process GRID Data API match JSONs  
 **Strategic AI Coach**: Answers complex questions about team performance  
 **Scouting Reports**: 10-page professional opponent dossiers generated automatically  
 **Draft Predictor**: Real-time win probability and pick/ban recommendations  
 **Draft Master Game**: Fan-facing competitive mini-game  

## Links
- **Source Code**: https://github.com/SamiraSamrose/nexus-commander
- **Video Demo**: https://youtu.be/cs5RmbflGVM
---

##  Tech Stack

### Data & Infrastructure
- **Data Source**: GRID Data API (League of Legends match telemetry)
- **Data Streaming**: Apache Pulsar (for live game events)
- **Data Warehouse**: Google BigQuery (historical analysis)
- **Orchestration**: AWS Step Functions

### AI & Machine Learning
- **LLMs**: Claude 3.5 (Anthropic) & Gemini 1.5 Pro (Google)
- **ML Models**: XGBoost, PyTorch Temporal Fusion Transformers (TFT)
- **Graph Neural Networks**: PyTorch Geometric (champion relationships)
- **Vector Database**: Pinecone (for RAG)

### Application
- **Backend**: Python 3.10+
- **Data Processing**: Pandas, NumPy, SciPy
- **Frontend**: Next.js 16 + Tailwind CSS (separate repository)

---

##  Four Key Components

### Component A: AI Assistant Coach

**The Strategic Brain with Agentic RAG**

Merges micro-level telemetry with macro-level strategic review to answer complex coaching questions.

**Capabilities:**
- Analyze gold deficits and economic patterns
- Identify macro strategy issues (Baron/Dragon control)
- Evaluate player mechanics and positioning
- Find team signature patterns across multiple matches

**Example Questions:**
- "Why did our bot lane fall behind in gold at the 12-minute mark?"
- "What are this team's signature patterns?"
- "How can we improve our Baron control?"

### Component B: Automated Scouting Report Generator

**Professional Opponent Dossiers in Seconds**

Generates comprehensive 10-page scouting reports by analyzing an opponent's recent matches.

**Report Sections:**
1. Executive Summary
2. Win/Loss Record & Trends
3. Draft Patterns & Champion Pool
4. Macro Strategy & Objective Control
5. Player Profiles & Strengths
6. Signature Plays & Patterns
7. Weaknesses & Exploitable Tendencies
8. Head-to-Head Analysis
9. Recommended Counter-Strategies
10. Key Takeaways & Pre-Match Checklist

### Component C: AI Drafting Assistant & Predictor

**GNN-Based Draft Analysis**

Uses Graph Neural Networks to model champion relationships and predict draft outcomes.

**Features:**
- Real-time win probability calculation
- Pick/ban recommendations with reasoning
- Champion synergy analysis
- Counter-matchup evaluation
- Complete draft simulation

**Graph Model:**
- Nodes: Champions/Agents
- Edges: Synergies and counter relationships
- Predictions: P(Win | Draft) in real-time

### Component D: Draft Master Mini-Game

**Fan Engagement Through Gamification**

Interactive game where fans compete against AI to create optimal drafts.

**Game Modes:**
- Easy, Medium, Hard, Pro difficulty levels
- Historical match scenarios
- Global leaderboards
- Performance scoring and ratings

**Scoring System:**
- Optimal picks: 100 points
- Good picks: 75 points
- Time bonuses: up to 300 points
- Win probability bonuses: up to 500 points

---

## Quick Start

### 1. Install Dependencies
```bash
cd nexus-commander
pip install -r documentation/requirements.txt
```

### 2. Add Match Data
```bash
# Copy your GRID match JSON files to:
cp /path/to/matchID_*.json /mnt/user-data/uploads/
```

### 3. Run Demo
```bash
cd execution
python demo.py
```

### 4. Start Backend API (Optional)
```bash
cd execution
python flask_backend.py
```

### 5. Open Web Interface
```
Open web_demo_advanced.html in your browser
```

## File Paths Reference

All imports use relative paths from the execution directory:

```python
# From execution/nexus_commander.py
from core.config import config
from core.data_ingestion import load_and_parse_all_data
from components.ai_coach import AICoachingAssistant
from components.scouting_report import ScoutingReportGenerator
from components.drafting_assistant import DraftingAssistant
from components.draft_master_game import DraftMasterGame
```

## Components

### Component A: AI Assistant Coach (components/ai_coach.py)
Strategic analysis with pattern recognition

### Component B: Scouting Reports (components/scouting_report.py)
10-section professional opponent analysis

### Component C: Drafting Assistant (components/drafting_assistant.py)
GNN-based draft predictions

### Component D: Draft Master Game (components/draft_master_game.py)
Interactive mini-game with achievements and combos

## Usage Examples

```python
from execution.nexus_commander import NexusCommander

# Initialize
nexus = NexusCommander()

# Component A
patterns = nexus.find_team_patterns('47558', 10)

# Component B
report = nexus.generate_scouting_report('47558')

# Component C
from components.drafting_assistant import DraftState
draft = DraftState(team1_picks=['Ahri'], team1_bans=[], team2_picks=[], team2_bans=[], current_phase='pick', turn=1)
analysis = nexus.analyze_draft(draft)

# Component D
game = nexus.start_game('Player1', 'medium')
```

## Running Tests

```bash
cd execution
python run_tests.py
```

Expected output: 6/6 tests passing

## API Endpoints

When running flask_backend.py:

- `GET /api/initialize` - Platform initialization
- `POST /api/coach/ask` - AI Coach queries
- `POST /api/scouting/generate` - Scouting reports
- `POST /api/draft/analyze` - Draft analysis
- `POST /api/game/start` - Start game
- `GET /api/health` - Health check

## Functionality

- JSON file discovery and parsing — reads `matchID_*.json` via glob, parses `seriesState.games[0]`
- Draft sequence extraction — parses `draftActions[]` into bans and picks keyed by team_id and sequenceNumber
- Player stat extraction — kills, deaths, assists, gold, CS, wards, vision_score, damage per player per match
- Team objective extraction — baron_kills, dragon_kills, herald_kills, tower_kills per team per match
- DataFrame creation — Pandas DataFrame with one row per team per match, picks and bans as comma-joined strings
- Gold deficit analysis — compares bot-lane CS, deaths, gold; returns root-cause list
- Macro pattern flagging — compares objective counts between teams; returns CoachingInsight with priority
- Player micro analysis — evaluates KDA and death count for a named player in a given match
- Signature pattern detection — counts pick and ban frequency across last N matches for a team
- 10-section scouting report — executive summary, record, draft pool, macro, player profiles, signatures, weaknesses, head-to-head, counter-strategies, takeaways
- Scouting report text export — writes formatted text file
- Champion graph construction — synergy and counter matrices from match histories, ≥3 co-occurrence threshold
- Win probability prediction — weighted sum of champion power, team synergy, counter advantage
- Pick/ban recommendations — ranks available champions by power + synergy × 0.3 + counter × 0.4
- 20-phase draft game — player vs AI turn loop with phase descriptions
- Difficulty-filtered hints — easy (5), medium (3), hard (1), pro (0) recommendations shown
- AI opponent — picks from its own recommendation list, randomness scope set by difficulty
- Move scoring — ranks player's choice against recommendations, applies time bonus and streak/combo mechanics
- Achievement system — 8 conditions checked: first_blood, combo_master, synergy_king, counter_strike, speedster, flawless, comeback_kid, draft_god
- Final rating — Legendary / Master / Diamond / Platinum / Gold based on total score
- Leaderboard — in-memory, sorted by total score, returns top N completed games
- Flask REST API — 17 routes, CORS enabled, JSON request/response
- Standalone web interface — single HTML file, all game and draft logic in JavaScript, no server required
- Test suite — 6 tests: data loading, AI coach, scouting report, drafting assistant, draft master game, full integration

## Advanced Features

The Draft Master Game includes:
- Combo system with multipliers
- Streak tracking
- 8 achievements to unlock
- Visual celebrations (fireworks, popups)
- Real-time scoring with bonuses

