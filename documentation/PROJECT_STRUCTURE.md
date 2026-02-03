# Nexus Commander - Project Structure

## Core Modules Description

### 1. config.py
**Purpose:** Central configuration management  
**Key Components:**
- API configurations (GRID, Anthropic, Gemini, AWS, Firebase)
- ML model parameters (XGBoost, TFT, GNN)
- File paths and directories
- Configuration validation

**Lines of Code:** ~200

### 2. nexus_commander.py
**Purpose:** Main application orchestrator  
**Key Components:**
- `NexusCommander` class - unified interface
- Integration of all four components
- Utility methods (team list, match list, statistics)
- Demo functionality

**Lines of Code:** ~350

**Main API:**
```python
nexus = NexusCommander()

# AI Coach
nexus.ask_coach(question, context)
nexus.find_team_patterns(team_id, n_matches)

# Scouting
report = nexus.generate_scouting_report(opponent_id)
nexus.export_scouting_report(report)

# Drafting
analysis = nexus.analyze_draft(draft_state)
probs = nexus.predict_draft_winner(picks1, picks2)

# Game
game = nexus.start_game(player, difficulty)
nexus.make_game_move(game_id, champion)
```

### 3. data_ingestion.py
**Purpose:** Load and parse GRID match data  
**Key Components:**
- `GridDataParser` - parse JSON files
- `MatchMetadata`, `DraftData`, `PlayerStats`, `TeamStats` - data structures
- DataFrame creation for analysis
- Timeline extraction

**Lines of Code:** ~450

**Output:** Structured match data with:
- Metadata (teams, duration, winner)
- Draft (picks, bans, sequence)
- Player statistics (KDA, CS, vision, damage)
- Team statistics (objectives, gold, vision)

### 4. ai_coach.py (Component A)
**Purpose:** AI-powered strategic coaching  
**Key Components:**
- `StrategicAnalyzer` - pattern recognition
- `AICoachingAssistant` - query interface with simulated RAG
- `CoachingInsight` - structured insights

**Lines of Code:** ~600

**Capabilities:**
- Gold deficit analysis
- Macro pattern recognition (Baron, Dragon, tower control)
- Micro mechanics evaluation (KDA, CS, vision)
- Signature pattern detection across matches

### 5. scouting_report.py (Component B)
**Purpose:** Automated scouting report generation  
**Key Components:**
- `ScoutingReportGenerator` - main generator
- `ScoutingSection` - report sections
- 10-section comprehensive reports

**Lines of Code:** ~550

**Report Sections:**
1. Executive Summary
2. Win/Loss Record & Trends
3. Draft Patterns & Champion Pool
4. Macro Strategy & Objective Control
5. Player Profiles & Strengths
6. Signature Plays & Patterns
7. Weaknesses & Exploitable Tendencies
8. Head-to-Head Analysis (if applicable)
9. Recommended Counter-Strategies
10. Key Takeaways & Pre-Match Checklist

### 6. drafting_assistant.py (Component C)
**Purpose:** GNN-based draft assistance  
**Key Components:**
- `ChampionGraph` - models champion relationships
- `DraftPredictor` - win probability and recommendations
- `DraftingAssistant` - main interface
- `DraftRecommendation` - structured recommendations

**Lines of Code:** ~600

**Features:**
- Champion synergy matrix
- Counter-matchup analysis
- Real-time win probability calculation
- Pick/ban recommendations with reasoning

### 7. draft_master_game.py (Component D)
**Purpose:** Fan engagement mini-game  
**Key Components:**
- `DraftMasterGame` - game engine
- `DraftScorer` - scoring system
- `GameState` - game state management
- Difficulty levels and leaderboards

**Lines of Code:** ~500

**Scoring:**
- Optimal pick: 100 points
- Good pick: 75 points
- Acceptable: 50 points
- Time bonuses
- Win probability bonuses

### 8. demo.py
**Purpose:** Interactive demonstration  
**Lines of Code:** ~350

**Demonstrations:**
- AI Coach queries and pattern analysis
- Scouting report generation
- Draft analysis and predictions
- Draft Master game simulation
- Complete workflow example

### 9. run_tests.py
**Purpose:** Comprehensive test suite  
**Lines of Code:** ~250

**Tests:**
1. Data ingestion validation
2. AI Coach functionality
3. Scouting report generation
4. Drafting assistant predictions
5. Draft Master game
6. Full platform integration

## Total Project Statistics

**Total Lines of Code:** ~3,850  
**Number of Modules:** 9  
**Number of Classes:** 25+  
**Number of Functions:** 100+

## Dependencies

**Core:**
- pandas, numpy, scipy (data processing)
- json (data loading)

**Machine Learning:**
- scikit-learn, xgboost (classical ML)
- torch, torch-geometric (deep learning)

**AI/LLM (Optional for extended features):**
- anthropic, google-generativeai
- langchain, langgraph
- pinecone-client, sentence-transformers

**Cloud (Optional for production):**
- google-cloud-bigquery
- boto3 (AWS)
- firebase-admin
- pulsar-client

## Data Requirements

**Input Format:** GRID Data API JSON files

**Minimum Data:** 
- At least 5-10 matches for basic functionality
- 20+ matches recommended for quality insights
- 50+ matches for optimal GNN training

**Data Structure:**
```json
{
  "seriesState": {
    "games": [{
      "id": "...",
      "teams": [...],
      "draftActions": [...],
      "clock": {...},
      ...
    }]
  }
}
```

## Execution Instructions

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Add Match Data
```bash
mkdir -p data/uploads
cp /path/to/match_*.json data/uploads/
```

### 3. Run Tests
```bash
python run_tests.py
```

### 4. Run Demo
```bash
python demo.py
```

### 5. Use Programmatically
```python
from nexus_commander import NexusCommander

nexus = NexusCommander()

# Your analysis here
teams = nexus.get_team_list()
report = nexus.generate_scouting_report(teams[0]['id'])
print(nexus.export_scouting_report(report))
```

## Architecture Highlights

### Design Patterns
- **Facade Pattern:** `NexusCommander` provides unified interface
- **Strategy Pattern:** Multiple analysis strategies (macro, micro, draft)
- **Factory Pattern:** Data structure creation from raw JSON
- **Observer Pattern:** Game state management

### Key Algorithms
1. **Champion Graph Construction:** O(n²) pairwise synergy calculation
2. **Pattern Recognition:** Sliding window over match history
3. **Win Probability:** Weighted combination of power, synergy, counters
4. **Scoring System:** Multi-factor evaluation with bonuses

### Scalability Considerations
- **Data Ingestion:** Batched processing of match files
- **Graph Building:** Incremental updates possible
- **Caching:** Match data cached after initial parse
- **Modular Design:** Components can run independently

## Future Enhancement Opportunities

1. **Real-time Integration:** Live match API streaming
2. **ML Model Training:** Fine-tune on larger datasets
3. **Web Dashboard:** React/Next.js frontend
4. **API Service:** RESTful endpoints
5. **Cloud Deployment:** AWS Lambda + Step Functions
6. **Database Integration:** PostgreSQL/BigQuery backend
7. **Video Analysis:** Computer vision for gameplay