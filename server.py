#!/usr/bin/env python3
"""
VANILLA Arcade Hub - Game Backend Server
Simple Flask-based backend for game state management and scoring
"""

import json
import os
from datetime import datetime

# This is a placeholder backend structure
# It can be expanded to include Flask, database integration, etc.

class GameServer:
    """Backend server for managing game state and scores"""
    
    def __init__(self):
        self.scores_file = os.path.join(os.path.dirname(__file__), 'scores.json')
        self.initialize_scores()
    
    def initialize_scores(self):
        """Initialize scores file if it doesn't exist"""
        if not os.path.exists(self.scores_file):
            default_scores = {
                "snake": [],
                "tetris": [],
                "pong": [],
                "breakout": [],
                "geometry_dash": [],
                "minesweeper": [],
                "space_shooters": []
            }
            self.save_scores(default_scores)
    
    def save_scores(self, scores):
        """Save scores to file"""
        with open(self.scores_file, 'w') as f:
            json.dump(scores, f, indent=4)
    
    def load_scores(self):
        """Load scores from file"""
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def add_score(self, game_name, player_name, score, difficulty):
        """Add a new score for a game"""
        scores = self.load_scores()
        if game_name not in scores:
            scores[game_name] = []
        
        scores[game_name].append({
            "player": player_name,
            "score": score,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        })
        
        # Sort by score descending
        scores[game_name] = sorted(
            scores[game_name], 
            key=lambda x: x['score'], 
            reverse=True
        )[:10]  # Keep top 10
        
        self.save_scores(scores)
    
    def get_leaderboard(self, game_name):
        """Get leaderboard for a specific game"""
        scores = self.load_scores()
        return scores.get(game_name, [])

if __name__ == '__main__':
    server = GameServer()
    print("VANILLA Game Backend Server initialized")
    print(f"Scores file: {server.scores_file}")
