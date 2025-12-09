"""
Global constants and configuration for Vanilla Arcade Hub
"""

# Window dimensions
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

# Game canvas dimensions
GAME_WIDTH = 800
GAME_HEIGHT = 600

# Target FPS
TARGET_FPS = 60
FRAME_TIME = 1000 // TARGET_FPS  # milliseconds

# Color palette
class Colors:
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    DARK_BG = "#0a0e27"
    DARKER_BG = "#1a1a2e"
    MEDIUM_BG = "#16213e"
    WHITE = "#ffffff"
    BLACK = "#000000"
    LIGHT_GRAY = "#e0e0e0"
    MEDIUM_GRAY = "#b0b0b0"
    DARK_GRAY = "#333333"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    ACCENT = "#f093fb"
    
    SNAKE_HEAD = "#10b981"
    SNAKE_BODY = "#059669"
    SNAKE_BORDER = "#047857"
    SNAKE_FOOD = "#ef4444"

# Game levels configuration
LEVEL_CONFIG = {
    'SNAKE': {
        1: {'gridSize': 20, 'speed': 150, 'scorePerFood': 10},
        2: {'gridSize': 20, 'speed': 100, 'scorePerFood': 15},
        3: {'gridSize': 20, 'speed': 60, 'scorePerFood': 20}
    },
    'TETRIS': {
        1: {'gridWidth': 10, 'gridHeight': 20, 'dropSpeed': 1000, 'scorePerLine': 100},
        2: {'gridWidth': 10, 'gridHeight': 20, 'dropSpeed': 600, 'scorePerLine': 150},
        3: {'gridWidth': 10, 'gridHeight': 20, 'dropSpeed': 300, 'scorePerLine': 200}
    },
    'PONG': {
        1: {'ballSpeed': 5, 'paddleSpeed': 6, 'scoreToWin': 11},
        2: {'ballSpeed': 7, 'paddleSpeed': 7, 'scoreToWin': 11},
        3: {'ballSpeed': 9, 'paddleSpeed': 8, 'scoreToWin': 11}
    },
    'BREAKOUT': {
        1: {'ballSpeed': 4, 'paddleSpeed': 7, 'brickRows': 3},
        2: {'ballSpeed': 6, 'paddleSpeed': 8, 'brickRows': 4},
        3: {'ballSpeed': 8, 'paddleSpeed': 9, 'brickRows': 5}
    },
    'GEOMETRY_DASH': {
        1: {'speed': 5, 'gravity': 0.6, 'jumpPower': 15},
        2: {'speed': 7, 'gravity': 0.7, 'jumpPower': 14},
        3: {'speed': 9, 'gravity': 0.8, 'jumpPower': 13}
    },
    'MINESWEEPER': {
        1: {'gridSize': 8, 'mines': 10},
        2: {'gridSize': 10, 'mines': 30},
        3: {'gridSize': 12, 'mines': 60}
    },
    'SPACE_SHOOTERS': {
        1: {'enemySpeed': 3, 'spawnRate': 60, 'playerSpeed': 7},
        2: {'enemySpeed': 5, 'spawnRate': 45, 'playerSpeed': 8},
        3: {'enemySpeed': 7, 'spawnRate': 30, 'playerSpeed': 9}
    }
}

# Game registry
GAMES = {
    'SNAKE': {
        'name': 'Snake',
        'description': 'Guide your snake to eat food and grow longer without hitting yourself!',
        'icon': '🐍',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'TETRIS': {
        'name': 'Tetris',
        'description': 'Stack the falling pieces and complete rows to clear the board!',
        'icon': '🧩',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'PONG': {
        'name': 'Pong',
        'description': 'Classic two-player paddle game. Compete against the AI!',
        'icon': '🎾',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'BREAKOUT': {
        'name': 'Breakout',
        'description': 'Bounce the ball to break all the bricks with your paddle!',
        'icon': '🔨',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'GEOMETRY_DASH': {
        'name': 'Geometry Dash',
        'description': 'Jump your way through platforms and avoid obstacles!',
        'icon': '⬜',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'MINESWEEPER': {
        'name': 'Minesweeper',
        'description': 'Reveal safe tiles but avoid the hidden mines!',
        'icon': '💣',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    },
    'SPACE_SHOOTERS': {
        'name': 'Space Shooters',
        'description': 'Defend your ship from incoming enemies in outer space!',
        'icon': '🚀',
        'levels': [
            {'name': 'Easy', 'level': 1},
            {'name': 'Medium', 'level': 2},
            {'name': 'Hard', 'level': 3}
        ]
    }
}
