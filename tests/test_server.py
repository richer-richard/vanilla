"""
Tests for the VANILLA Collection server.

Run with: pytest tests/ -v
"""

import json
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from server import (
    GameServer,
    ScoreStore,
    sanitize_string,
    validate_player_name,
    validate_game,
    validate_difficulty,
    validate_score,
    MAX_PLAYER_NAME_LENGTH,
    VALID_GAMES,
    VALID_DIFFICULTIES,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_scores_file():
    """Create a temporary scores file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        return Path(f.name)


@pytest.fixture
def score_store(temp_scores_file):
    """Create a ScoreStore instance with a temporary file."""
    return ScoreStore(temp_scores_file)


@pytest.fixture
def app(temp_scores_file):
    """Create a Flask test client."""
    server = GameServer(temp_scores_file)
    server.app.config['TESTING'] = True
    return server.app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestSanitizeString:
    """Tests for the sanitize_string function."""
    
    def test_basic_string(self):
        assert sanitize_string("hello") == "hello"
    
    def test_strips_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"
    
    def test_escapes_html(self):
        result = sanitize_string("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result
    
    def test_removes_control_characters(self):
        result = sanitize_string("hello\x00world\x1f")
        assert "\x00" not in result
        assert "\x1f" not in result
    
    def test_truncates_to_max_length(self):
        long_string = "a" * 200
        result = sanitize_string(long_string, max_length=50)
        assert len(result) == 50
    
    def test_handles_none(self):
        assert sanitize_string(None) == ""
    
    def test_handles_numbers(self):
        assert sanitize_string(123) == "123"


class TestValidatePlayerName:
    """Tests for player name validation."""
    
    def test_valid_name(self):
        valid, error = validate_player_name("Alice")
        assert valid is True
        assert error == ""
    
    def test_empty_name(self):
        valid, error = validate_player_name("")
        assert valid is False
        assert "required" in error.lower()
    
    def test_whitespace_only(self):
        valid, error = validate_player_name("   ")
        assert valid is False
    
    def test_too_long(self):
        long_name = "a" * (MAX_PLAYER_NAME_LENGTH + 10)
        valid, error = validate_player_name(long_name)
        assert valid is False
        assert "at most" in error.lower()
    
    def test_special_characters_allowed(self):
        valid, error = validate_player_name("Player_123")
        assert valid is True


class TestValidateGame:
    """Tests for game name validation."""
    
    def test_valid_games(self):
        for game in VALID_GAMES:
            valid, error = validate_game(game)
            assert valid is True, f"Game '{game}' should be valid"
    
    def test_empty_game(self):
        valid, error = validate_game("")
        assert valid is False
        assert "required" in error.lower()
    
    def test_invalid_game(self):
        valid, error = validate_game("not_a_real_game")
        assert valid is False
        assert "invalid" in error.lower()


class TestValidateDifficulty:
    """Tests for difficulty validation."""
    
    def test_valid_difficulties(self):
        for diff in VALID_DIFFICULTIES:
            valid, error = validate_difficulty(diff)
            assert valid is True, f"Difficulty '{diff}' should be valid"
    
    def test_empty_difficulty_allowed(self):
        # Empty string defaults to "unknown" in the API
        valid, error = validate_difficulty("")
        assert valid is True
    
    def test_invalid_difficulty(self):
        valid, error = validate_difficulty("impossible")
        assert valid is False


class TestValidateScore:
    """Tests for score validation."""
    
    def test_valid_score(self):
        valid, error, value = validate_score(100)
        assert valid is True
        assert value == 100
    
    def test_string_score(self):
        valid, error, value = validate_score("500")
        assert valid is True
        assert value == 500
    
    def test_negative_score(self):
        valid, error, value = validate_score(-10)
        assert valid is False
    
    def test_too_large_score(self):
        valid, error, value = validate_score(10**15)
        assert valid is False
    
    def test_invalid_score(self):
        valid, error, value = validate_score("not a number")
        assert valid is False
    
    def test_none_score(self):
        valid, error, value = validate_score(None)
        assert valid is False


# ============================================================================
# SCORE STORE TESTS
# ============================================================================

class TestScoreStore:
    """Tests for the ScoreStore class."""
    
    def test_empty_leaderboard(self, score_store):
        scores = score_store.leaderboard("snake")
        assert scores == []
    
    def test_add_score(self, score_store):
        entry = score_store.add_score("snake", "Alice", 100, "medium")
        assert entry["player"] == "Alice"
        assert entry["score"] == 100
        assert entry["difficulty"] == "medium"
        assert "timestamp" in entry
    
    def test_leaderboard_sorted_descending(self, score_store):
        score_store.add_score("snake", "Alice", 100, "medium")
        score_store.add_score("snake", "Bob", 200, "medium")
        score_store.add_score("snake", "Charlie", 150, "medium")
        
        scores = score_store.leaderboard("snake")
        assert len(scores) == 3
        assert scores[0]["player"] == "Bob"
        assert scores[1]["player"] == "Charlie"
        assert scores[2]["player"] == "Alice"
    
    def test_minesweeper_sorted_ascending(self, score_store):
        # Minesweeper scores are time-based (lower is better)
        score_store.add_score("minesweeper", "Alice", 100, "medium")
        score_store.add_score("minesweeper", "Bob", 50, "medium")
        score_store.add_score("minesweeper", "Charlie", 75, "medium")
        
        scores = score_store.leaderboard("minesweeper")
        assert scores[0]["player"] == "Bob"  # Lowest time first
    
    def test_max_entries_limit(self, score_store):
        # Add more than MAX_ENTRIES scores
        for i in range(20):
            score_store.add_score("snake", f"Player{i}", i * 10, "medium")
        
        scores = score_store.leaderboard("snake")
        assert len(scores) <= 15  # MAX_ENTRIES
    
    def test_games_returns_all(self, score_store):
        score_store.add_score("snake", "Alice", 100, "medium")
        score_store.add_score("pong", "Bob", 200, "hard")
        
        all_games = score_store.games()
        assert "snake" in all_games
        assert "pong" in all_games


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

class TestHealthEndpoint:
    """Tests for health check endpoints."""
    
    def test_health(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"
    
    def test_api_health(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_v1_health(self, client):
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["api_version"] == "v1"


class TestScoreEndpoints:
    """Tests for score-related endpoints."""
    
    def test_get_scores(self, client):
        response = client.get('/scores')
        assert response.status_code == 200
    
    def test_get_leaderboard(self, client):
        response = client.get('/leaderboard/snake')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["game"] == "snake"
    
    def test_post_score(self, client):
        response = client.post('/score',
            data=json.dumps({
                "game": "snake",
                "player": "TestPlayer",
                "score": 100,
                "difficulty": "medium"
            }),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["ok"] is True
    
    def test_post_score_missing_game(self, client):
        response = client.post('/score',
            data=json.dumps({
                "player": "TestPlayer",
                "score": 100
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_post_score_missing_player(self, client):
        response = client.post('/score',
            data=json.dumps({
                "game": "snake",
                "score": 100
            }),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestV1Endpoints:
    """Tests for v1 API endpoints with validation."""
    
    def test_v1_scores(self, client):
        response = client.get('/api/v1/scores')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["api_version"] == "v1"
    
    def test_v1_leaderboard_valid_game(self, client):
        response = client.get('/api/v1/leaderboard/snake')
        assert response.status_code == 200
    
    def test_v1_leaderboard_invalid_game(self, client):
        response = client.get('/api/v1/leaderboard/invalid_game')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_v1_post_score_valid(self, client):
        response = client.post('/api/v1/score',
            data=json.dumps({
                "game": "pong",
                "player": "ValidPlayer",
                "score": 500,
                "difficulty": "hard"
            }),
            content_type='application/json'
        )
        assert response.status_code == 201
    
    def test_v1_post_score_invalid_game(self, client):
        response = client.post('/api/v1/score',
            data=json.dumps({
                "game": "invalid_game",
                "player": "ValidPlayer",
                "score": 500
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_v1_post_score_xss_sanitization(self, client):
        response = client.post('/api/v1/score',
            data=json.dumps({
                "game": "snake",
                "player": "<script>alert('xss')</script>",
                "score": 100
            }),
            content_type='application/json'
        )
        # Should succeed but sanitize the name
        assert response.status_code == 201
        data = json.loads(response.data)
        assert "<script>" not in data["entry"]["player"]


class TestGameEndpoints:
    """Tests for game-specific API endpoints."""
    
    def test_snake_food(self, client):
        response = client.post('/api/snake/food',
            data=json.dumps({"grid": 16, "snake": [[5, 5], [5, 4]]}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "x" in data
        assert "y" in data
    
    def test_breakout_level(self, client):
        response = client.post('/api/breakout/level',
            data=json.dumps({"level": 1, "width": 800, "difficulty": "medium"}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "bricks" in data
    
    def test_minesweeper_board(self, client):
        response = client.post('/api/minesweeper/board',
            data=json.dumps({
                "rows": 9,
                "cols": 9,
                "mines": 10,
                "safe_row": 4,
                "safe_col": 4
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "board" in data
    
    def test_tetris_config(self, client):
        response = client.post('/api/tetris/config',
            data=json.dumps({"difficulty": "hard"}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["difficulty"] == "hard"
        assert "config" in data


# ============================================================================
# CORS TESTS
# ============================================================================

class TestCORS:
    """Tests for CORS headers."""
    
    def test_cors_headers_present(self, client):
        response = client.get('/health')
        assert response.headers.get('Access-Control-Allow-Origin') == '*'
    
    def test_options_request(self, client):
        response = client.options('/score')
        assert response.status_code == 204


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
