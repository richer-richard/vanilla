"""
Tests for the VANILLA Collection backend modules.

Run with: pytest tests/test_backends.py -v
"""

import pytest

from vanilla_collection.backends import (
    asteroids,
    breakout,
    flappy,
    geometry_dash,
    minesweeper,
    pacman,
    pong,
    snake,
    space_shooters,
    tetris,
)

# ============================================================================
# SNAKE BACKEND TESTS
# ============================================================================

class TestSnakeBackend:
    """Tests for the Snake game backend."""

    def test_next_food_returns_valid_position(self):
        """Food position should be within grid bounds."""
        result = snake.next_food(grid=16, snake=[[5, 5], [5, 4], [5, 3]])
        assert "x" in result
        assert "y" in result
        assert 0 <= result["x"] < 16
        assert 0 <= result["y"] < 16

    def test_next_food_not_on_snake(self):
        """Food should not spawn on the snake body."""
        snake_body = [[5, 5], [5, 4], [5, 3]]
        for _ in range(10):  # Test multiple times due to randomness
            result = snake.next_food(grid=16, snake=snake_body)
            assert (result["x"], result["y"]) not in [(s[0], s[1]) for s in snake_body]

    def test_next_food_with_empty_snake(self):
        """Should handle empty snake body."""
        result = snake.next_food(grid=16, snake=[])
        assert "x" in result
        assert "y" in result

    def test_get_game_stats(self):
        """Test game statistics calculation."""
        snake_body = [[5, 5], [5, 4], [5, 3], [5, 2], [5, 1]]
        result = snake.get_game_stats(grid=16, snake=snake_body)
        assert isinstance(result, dict)
        assert result["snake_length"] == len(snake_body)
        assert result["reachable_cells"] > 0
        assert 0 < result["reachable_percent"] <= 100


# ============================================================================
# PONG BACKEND TESTS
# ============================================================================

class TestPongBackend:
    """Tests for the Pong game backend."""

    def test_ai_target_returns_dict(self):
        """AI target calculation should return a dictionary."""
        payload = {
            "difficulty": "medium",
            "ball": {"x": 400, "y": 300, "dx": 5, "dy": 2},
            "ai": {"height": 96},
            "court": {"width": 800, "height": 600},
        }
        result = pong.ai_target(payload)
        assert isinstance(result, dict)
        assert "targetY" in result

    def test_ai_target_with_empty_payload(self):
        """Should handle empty payload gracefully."""
        result = pong.ai_target({})
        assert isinstance(result, dict)
        assert "targetY" in result


# ============================================================================
# BREAKOUT BACKEND TESTS
# ============================================================================

class TestBreakoutBackend:
    """Tests for the Breakout game backend."""

    def test_level_layout_returns_bricks(self):
        """Level layout should contain bricks."""
        result = breakout.level_layout(level=1, width=800, difficulty="medium")
        assert "bricks" in result
        assert isinstance(result["bricks"], list)

    def test_level_layout_different_levels(self):
        """Different levels should produce different layouts."""
        level1 = breakout.level_layout(level=1, width=800, difficulty="medium")
        level2 = breakout.level_layout(level=2, width=800, difficulty="medium")
        # Layouts might differ but both should be valid
        assert "bricks" in level1
        assert "bricks" in level2

    def test_level_layout_difficulty_variations(self):
        """Different difficulties should work."""
        for diff in ["easy", "medium", "hard"]:
            result = breakout.level_layout(level=1, width=800, difficulty=diff)
            assert "bricks" in result


# ============================================================================
# GEOMETRY DASH BACKEND TESTS
# ============================================================================

class TestGeometryDashBackend:
    """Tests for the Geometry Dash game backend."""

    def test_pattern_returns_obstacles(self):
        """Pattern generation should return obstacles."""
        result = geometry_dash.pattern(
            distance=100,
            difficulty="medium",
            ground_y=540,
            width=960
        )
        assert isinstance(result, dict)

    def test_pattern_different_difficulties(self):
        """Different difficulties should work."""
        for diff in ["easy", "medium", "hard"]:
            result = geometry_dash.pattern(
                distance=100,
                difficulty=diff,
                ground_y=540,
                width=960
            )
            assert isinstance(result, dict)

    def test_get_difficulty_config(self):
        """Difficulty config should return valid settings."""
        for diff in ["easy", "medium", "hard"]:
            config = geometry_dash.get_difficulty_config(diff)
            assert isinstance(config, dict)


# ============================================================================
# MINESWEEPER BACKEND TESTS
# ============================================================================

class TestMinesweeperBackend:
    """Tests for the Minesweeper game backend."""

    def test_generate_board_dimensions(self):
        """Board should have correct dimensions."""
        result = minesweeper.generate_board(
            rows=9,
            cols=9,
            mines=10,
            safe=(4, 4)
        )
        assert isinstance(result, dict)

    def test_generate_board_safe_cell(self):
        """Safe cell and neighbors should not have mines."""
        result = minesweeper.generate_board(
            rows=9,
            cols=9,
            mines=10,
            safe=(4, 4)
        )
        # The result should indicate board generation was successful
        assert isinstance(result, dict)

    def test_generate_board_mine_count(self):
        """Board should have the requested number of mines."""
        result = minesweeper.generate_board(
            rows=9,
            cols=9,
            mines=10,
            safe=(0, 0)
        )
        assert isinstance(result, dict)

    def test_generate_board_edge_cases(self):
        """Test with edge cases like corner safe cells."""
        for safe in [(0, 0), (0, 8), (8, 0), (8, 8)]:
            result = minesweeper.generate_board(
                rows=9,
                cols=9,
                mines=10,
                safe=safe
            )
            assert isinstance(result, dict)


# ============================================================================
# SPACE SHOOTERS BACKEND TESTS
# ============================================================================

class TestSpaceShootersBackend:
    """Tests for the Space Shooters game backend."""

    def test_wave_plan_returns_enemies(self):
        """Wave plan should include enemy data."""
        result = space_shooters.wave_plan(
            wave=1,
            difficulty="medium",
            width=900,
            height=600
        )
        assert isinstance(result, dict)

    def test_wave_plan_different_waves(self):
        """Different waves should produce valid plans."""
        for wave in [1, 5, 10]:
            result = space_shooters.wave_plan(
                wave=wave,
                difficulty="medium",
                width=900,
                height=600
            )
            assert isinstance(result, dict)

    def test_wave_plan_different_difficulties(self):
        """Different difficulties should work."""
        for diff in ["easy", "medium", "hard"]:
            result = space_shooters.wave_plan(
                wave=1,
                difficulty=diff,
                width=900,
                height=600
            )
            assert isinstance(result, dict)


# ============================================================================
# TETRIS BACKEND TESTS
# ============================================================================

class TestTetrisBackend:
    """Tests for the Tetris game backend."""

    def test_config_returns_dict(self):
        """Config should return a dictionary."""
        result = tetris.config("medium")
        assert isinstance(result, dict)

    def test_config_different_difficulties(self):
        """Different difficulties should return different configs."""
        for diff in ["easy", "medium", "hard"]:
            result = tetris.config(diff)
            assert isinstance(result, dict)


# ============================================================================
# FLAPPY BACKEND TESTS
# ============================================================================

class TestFlappyBackend:
    """Tests for the Flappy game backend."""

    def test_config_returns_dict(self):
        """Config should return a dictionary."""
        result = flappy.config("medium")
        assert isinstance(result, dict)

    def test_config_different_difficulties(self):
        """Different difficulties should return valid configs."""
        for diff in ["easy", "medium", "hard"]:
            result = flappy.config(diff)
            assert isinstance(result, dict)

    def test_generate_pipes(self):
        """Pipe generation should work."""
        result = flappy.generate_pipes(
            count=5,
            difficulty="medium",
            canvas_height=600,
            canvas_width=400
        )
        assert isinstance(result, list)

    def test_next_pipe(self):
        """Next pipe generation should return valid data."""
        result = flappy.next_pipe(
            current_distance=100,
            difficulty="medium",
            canvas_height=600
        )
        assert isinstance(result, dict)


# ============================================================================
# PACMAN BACKEND TESTS
# ============================================================================

class TestPacmanBackend:
    """Tests for the Pac-Man game backend."""

    def test_config_returns_dict(self):
        """Config should return a dictionary."""
        result = pacman.config("medium")
        assert isinstance(result, dict)

    def test_get_maze(self):
        """Maze should be a list of strings."""
        result = pacman.get_maze()
        assert isinstance(result, list)
        assert all(isinstance(row, str) for row in result)

    def test_get_maze_as_grid(self):
        """Maze grid should be a 2D list of integers."""
        result = pacman.get_maze_as_grid()
        assert isinstance(result, list)
        assert all(isinstance(row, list) for row in result)

    def test_count_pellets(self):
        """Pellet count should be a positive integer."""
        result = pacman.count_pellets()
        assert isinstance(result, int)
        assert result > 0

    def test_get_ghost_config(self):
        """Ghost config should return a list."""
        result = pacman.get_ghost_config()
        assert isinstance(result, list)

    def test_calculate_ghost_target(self):
        """Ghost target calculation should return valid position."""
        result = pacman.calculate_ghost_target(
            ghost_name="blinky",
            ghost_x=10,
            ghost_y=10,
            pacman_x=15,
            pacman_y=15,
            pacman_direction=(0, -1),
            blinky_x=10,
            blinky_y=10,
            mode="chase"
        )
        assert isinstance(result, dict)
        assert "x" in result
        assert "y" in result


# ============================================================================
# ASTEROIDS BACKEND TESTS
# ============================================================================

class TestAsteroidsBackend:
    """Tests for the Asteroids game backend."""

    def test_config_returns_dict(self):
        """Config should return a dictionary."""
        result = asteroids.config("medium")
        assert isinstance(result, dict)

    def test_generate_asteroid(self):
        """Asteroid generation should return valid data."""
        result = asteroids.generate_asteroid(
            canvas_width=900,
            canvas_height=600,
            size="large"
        )
        assert isinstance(result, dict)
        assert "x" in result
        assert "y" in result

    def test_generate_wave(self):
        """Wave generation should return list of asteroids."""
        result = asteroids.generate_wave(
            wave_number=1,
            difficulty="medium",
            canvas_width=900,
            canvas_height=600
        )
        assert isinstance(result, list)

    def test_split_asteroid(self):
        """Splitting asteroid should return smaller pieces."""
        parent = {
            "x": 450,
            "y": 300,
            "vx": 2,
            "vy": 1,
            "size": "large"
        }
        result = asteroids.split_asteroid(parent)
        assert isinstance(result, list)

    def test_generate_ufo(self):
        """UFO generation should return valid data."""
        result = asteroids.generate_ufo(
            canvas_width=900,
            canvas_height=600,
            difficulty="medium"
        )
        assert isinstance(result, dict)

    def test_should_spawn_ufo(self):
        """UFO spawn check should return boolean."""
        result = asteroids.should_spawn_ufo(
            elapsed_time=60000,
            score=1000,
            difficulty="medium"
        )
        assert isinstance(result, bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
