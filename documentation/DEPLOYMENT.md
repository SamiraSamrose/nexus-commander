# Nexus Commander - Full Stack Deployment Guide

## 📋 Overview

This guide shows how to run the complete Nexus Commander platform with:
- **Backend**: Python Flask API server
- **Frontend**: Interactive web demo
- **Data**: Actual LCK Spring 2024 match data

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Backend API Server

```bash
# Terminal 1: Start Flask backend
python flask_backend.py
```

Expected output:
```
NEXUS COMMANDER BACKEND API SERVER

Initializing Nexus Commander...
✓ Loaded 18 matches
✓ 11 unique teams identified
...

Backend is ready!
API available at: http://localhost:5000
```

### Step 2: Open the Web Demo

```bash
# Open web_demo.html in your browser
# For best experience, use:
# - Chrome, Firefox, Edge, or Safari
# - Modern browser with JavaScript enabled

# Option 1: Double-click web_demo.html
# Option 2: Start a simple HTTP server
python -m http.server 8000
# Then visit: http://localhost:8000/web_demo.html
```

### Step 3: Interact with the Platform

The web demo will connect to the backend API and provide full functionality:

✅ **AI Coach** - Ask strategic questions  
✅ **Scouting Reports** - Generate opponent analysis  
✅ **Draft Assistant** - Real-time draft predictions  
✅ **Draft Master Game** - Play the mini-game  


## 🔌 API Endpoints Reference

### Initialization
- `GET /api/initialize` - Get platform data (teams, champions, stats)
- `GET /api/health` - Health check

### AI Coach
- `POST /api/coach/ask` - Ask strategic question
  ```json
  {
    "question": "What are the team's patterns?",
    "context": {"team_id": "47558"}
  }
  ```

- `GET /api/coach/patterns/<team_id>` - Get team patterns
- `POST /api/coach/macro` - Get macro insights

### Scouting Reports
- `POST /api/scouting/generate` - Generate report
  ```json
  {
    "opponent_id": "47558",
    "n_matches": 20,
    "your_team_id": "47961"
  }
  ```

### Draft Assistant
- `POST /api/draft/analyze` - Analyze draft
  ```json
  {
    "team1_picks": ["Ahri", "Lee Sin"],
    "team1_bans": ["Zed"],
    "team2_picks": ["Jinx"],
    "team2_bans": ["Yasuo"],
    "current_phase": "pick",
    "turn": 1
  }
  ```

- `POST /api/draft/predict` - Predict win probability

### Draft Master Game
- `POST /api/game/start` - Start new game
- `GET /api/game/actions/<game_id>` - Get available actions
- `POST /api/game/move` - Make move
- `GET /api/game/leaderboard` - Get leaderboard

## 🎨 Web Demo Features

### Component A: AI Assistant Coach
- **Strategic Questions**: Select question type or enter custom
- **Team Analysis**: Pattern recognition across multiple matches
- **Real-time Responses**: Formatted insights and recommendations

### Component B: Scouting Reports
- **Comprehensive Analysis**: 10-section professional reports
- **Adjustable Scope**: 5/10/15/20 recent matches
- **Export Function**: Download as text file
- **All Sections**:
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

### Component C: AI Drafting Assistant
- **Interactive Champion Pool**: 62 champions with visual states
- **Live Draft Tracking**: Both teams' picks and bans
- **Win Probability**: Real-time calculation with visual bar
- **AI Recommendations**: Priority-based suggestions
  - CRITICAL (red border)
  - HIGH (orange border)
  - MEDIUM (yellow border)
  - LOW (green border)
- **Detailed Reasoning**: Synergies, counters, win rate impact

### Component D: Draft Master Game
- **4 Difficulty Levels**:
  - Easy: Top 5 hints
  - Medium: Top 3 hints
  - Hard: Only best hint
  - Pro: No hints
- **Real-time Scoring**: Points for each move
- **Phase Progression**: Exact ban/pick sequence
- **Final Rankings**: Legendary/Master/Diamond/Platinum/Challenger
- **Global Leaderboard**: Top 10 scores

## 🎯 Usage Examples

### Example 1: Generate Scouting Report

1. Go to "Scouting Reports" tab
2. Select opponent team (e.g., Gen.G Esports)
3. Choose number of matches (e.g., Last 10 Matches)
4. Click "Generate Report"
5. Wait ~2 seconds for analysis
6. Review comprehensive 10-section report
7. Click "Download Report" to save

### Example 2: Analyze Draft

1. Go to "Draft Assistant" tab
2. Click champions to add to Your Team picks
3. Switch to "Ban Phase" to add bans
4. Add Opponent picks/bans
5. Click "Analyze Draft"
6. View win probability and AI recommendations
7. Click recommended champions to add to draft

### Example 3: Play Draft Master Game

1. Go to "Draft Master Game" tab
2. Enter player name
3. Select difficulty (recommend Medium for first game)
4. Click "Start Game"
5. Read phase description and hints
6. Select champion from pool
7. View score and AI response
8. Continue for 10 moves
9. View final score and rating
10. Check leaderboard

## 🔧 Troubleshooting

### Backend Won't Start
```bash
# Install dependencies
pip install flask flask-cors

# Check if port 5000 is available
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>
```

### Frontend Can't Connect
- Ensure backend is running on port 5000
- Check browser console for errors
- Verify CORS is enabled in Flask

### No Data Showing
- Verify match JSON files are in `/mnt/user-data/uploads/`
- Check backend console for initialization errors
- Restart backend if data was added after startup

## 📊 Platform Statistics

From actual backend execution:
- **18 Matches** loaded
- **10 Teams** (NongShim REDFORCE, DRX, T1, Gen.G, etc.)
- **62 Champions** in pool
- **11 Unique teams** identified
- **4 AI Components** fully functional

## 🎮 Live Demo Flow

**Complete Workflow Example:**

1. **Start Backend**
   ```bash
   python flask_backend.py
   ```

2. **Open Frontend**
   ```
   Open web_demo.html in browser
   ```

3. **View Overview**
   - See 18 matches, 10 teams, 62 champions
   - Verify all systems operational

4. **Ask AI Coach**
   - Select team: "Gen.G Esports"
   - Question: "Team Signature Patterns"
   - Get instant analysis

5. **Generate Scout**
   - Select: "T1"
   - Matches: 10
   - View comprehensive report

6. **Analyze Draft**
   - Add picks: Ahri, Lee Sin
   - Add opponent: Jinx, Thresh
   - Get win probability: ~35%
   - View recommendations

7. **Play Game**
   - Name: "ProPlayer"
   - Difficulty: Medium
   - Complete 10 moves
   - Final score: ~600-800 points
   - Rating: Platinum/Diamond

## 🚀 Production Deployment

For production deployment:

1. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 flask_backend:app
   ```

2. **Deploy Frontend**
   - Host on CDN (Cloudflare, AWS S3)
   - Update API endpoint in web_demo.html
   - Enable HTTPS

3. **Database Integration**
   - Add PostgreSQL for persistent storage
   - Cache frequently accessed data
   - Store game leaderboards

4. **Monitoring**
   - Add logging (Python logging module)
   - Monitor API response times
   - Track user analytics
