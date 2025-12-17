# Contributing to VANILLA Collection

Thank you for your interest in contributing to the VANILLA Collection! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Adding a New Game](#adding-a-new-game)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A modern web browser (Chrome, Firefox, Safari, or Edge)
- Git
- (Optional) Node.js for JavaScript linting

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/vanilla.git
   cd vanilla
   ```

## Development Setup

### Python Backend

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies (including dev tools):
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install dev dependencies from pyproject.toml
   ```

3. Run the server:
   ```bash
   python3 app.py
   ```

### JavaScript/Frontend

No build process is required - we use vanilla JavaScript! Just edit the files and refresh your browser.

For linting (optional):
```bash
npm install -g eslint
eslint *.js
```

## Code Style

### Python

We use the following tools for Python code quality:

- **black** - Code formatter (line length: 100)
- **ruff** - Fast Python linter
- **mypy** - Type checking

Run the formatters/linters:
```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy server.py backends/
```

### JavaScript

- Use 4-space indentation
- Use semicolons
- Prefer `const` and `let` over `var`
- Use meaningful variable names

Run ESLint:
```bash
eslint *.js
```

### CSS

- Use CSS custom properties (variables) defined in `styles.css`
- Follow the existing naming conventions
- Keep specificity low when possible

## Adding a New Game

To add a new game to the collection, follow these steps:

### 1. Create Game Directory

```bash
mkdir newgame
```

### 2. Create Intro Page (`newgame/intro.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Game — VANILLA</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link rel="manifest" href="../manifest.json">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../styles.css">
</head>
<body>
    <header>
        <a href="../index.html">
            <h1>VANILLA</h1>
            <p>Collection</p>
        </a>
        <a href="../games.html">← Back to Games</a>
    </header>
    
    <main>
        <h1>🎮 New Game</h1>
        <h2>Game Description</h2>
        <p>Brief description of how to play...</p>
        
        <div class="difficulty-buttons">
            <a href="game.html?difficulty=easy" class="difficulty-btn">Easy</a>
            <a href="game.html?difficulty=medium" class="difficulty-btn">Medium</a>
            <a href="game.html?difficulty=hard" class="difficulty-btn">Hard</a>
        </div>
    </main>
</body>
</html>
```

### 3. Create Game Page (`newgame/game.html`)

Use this template structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Game — Play | VANILLA</title>
    <link rel="icon" type="image/svg+xml" href="../favicon.svg">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Press+Start+2P&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="../game-common.css">
</head>
<body class="game-page">
    <!-- Header with back button and controls -->
    <header>
        <div class="header-left">
            <a class="pill-link" href="../games.html">← Games</a>
            <span class="crumb">New Game</span>
        </div>
        <div class="header-actions">
            <button class="action-btn ghost" id="soundBtn">🔊</button>
            <button class="action-btn ghost" id="pauseBtn">Pause</button>
            <button class="action-btn" id="restartBtn">Restart</button>
        </div>
    </header>

    <main>
        <!-- Game area -->
        <section class="glass-card">
            <div class="hud">
                <!-- HUD stats go here -->
            </div>
            <div class="board-shell">
                <canvas id="board"></canvas>
            </div>
        </section>
        
        <!-- Sidebar with tips -->
        <aside class="glass-card sidebar">
            <div id="scoreboardMount"></div>
            <!-- Tips and controls info -->
        </aside>
    </main>

    <!-- Game Over Overlay -->
    <div class="game-over-overlay" id="gameOverOverlay">
        <!-- Game over content -->
    </div>

    <script src="../sounds.js"></script>
    <script src="../scoreboard.js"></script>
    <script src="../engine.js"></script>
    <script>
        // Game implementation using VanillaEngine
        const { createGameEngine, createInputManager, Storage, MathUtils } = VanillaEngine;
        
        // Difficulty configuration
        const CONFIG = {
            easy: { /* ... */ },
            medium: { /* ... */ },
            hard: { /* ... */ }
        };
        
        // Get difficulty from URL
        const params = new URLSearchParams(window.location.search);
        const difficulty = params.get('difficulty') || 'medium';
        const settings = CONFIG[difficulty] || CONFIG.medium;
        
        // Create game engine
        const canvas = document.getElementById('board');
        const engine = createGameEngine({
            canvas,
            onUpdate: (tickScale, dt) => {
                // Game update logic
            },
            onRender: (ctx, width, height) => {
                // Rendering logic
            }
        });
        
        // Initialize and start
        engine.resize({ aspectRatio: 4/3 });
        engine.start();
    </script>
</body>
</html>
```

### 4. Add Backend Module (Optional)

If your game needs server-side logic, create `backends/newgame.py`:

```python
"""
Backend module for New Game.
"""

def some_game_logic(params):
    """
    Procedural generation or AI logic.
    
    Args:
        params: Dictionary of game parameters
        
    Returns:
        Dictionary with generated data
    """
    return {"result": "data"}
```

Register in `server.py`:
```python
from backends import newgame as newgame_backend

# In _register_routes():
@app.route("/api/newgame/endpoint", methods=["POST", "OPTIONS"])
def newgame_endpoint():
    if request.method == "OPTIONS":
        return ("", 204)
    payload = request.get_json(silent=True) or {}
    return jsonify(newgame_backend.some_game_logic(payload))
```

### 5. Add to Games Page

Edit `games.html` to add your game card:

```html
<a href="newgame/intro.html" class="game-card">
    <h2>🎮 New Game</h2>
    <p>Description of the game in a few sentences.</p>
    <div class="difficulty-badges">
        <span class="badge">Easy</span>
        <span class="badge">Medium</span>
        <span class="badge">Hard</span>
    </div>
</a>
```

### 6. Update Constants

Add your game to `server.py`:
```python
VALID_GAMES = {..., "newgame"}
DEFAULT_SCORES = {..., "newgame": []}
```

Update `sw.js` to cache the new pages:
```javascript
const STATIC_ASSETS = [
    // ...
    '/newgame/intro.html',
    '/newgame/game.html',
];
```

### Game Requirements

- **State Machine**: Use `ready`, `running`, `paused`, `over` states
- **Game Loop**: Use fixed-step simulation (120Hz recommended)
- **Responsive Canvas**: Handle window resize
- **Sound**: Use `sounds.js` for audio
- **Persistence**: Save high scores with `localStorage`
- **Difficulty**: Support at least Easy/Medium/Hard

## Testing

### Running Python Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test class
pytest tests/test_server.py::TestScoreStore -v
```

### Manual Testing Checklist

Before submitting, verify:

- [ ] Game loads without console errors
- [ ] All difficulty levels work
- [ ] Pause/Resume functions correctly
- [ ] Sound can be toggled
- [ ] High scores are saved
- [ ] Game works on mobile (responsive)
- [ ] Back to menu button works
- [ ] Game over screen displays correctly

## Submitting Changes

### Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Open a Pull Request on GitHub

### Commit Message Guidelines

Use conventional commit prefixes:
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Improvement to existing feature
- `Docs:` - Documentation changes
- `Style:` - Code style/formatting
- `Refactor:` - Code restructuring
- `Test:` - Adding/updating tests

### What to Include

- Clear description of changes
- Screenshots for UI changes
- Any breaking changes noted
- Related issue numbers (if applicable)

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Check existing issues for similar questions
- Review the codebase for examples

Thank you for contributing! 🎮
