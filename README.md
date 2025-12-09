# VANILLA - Arcade Hub

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)

A complete Python GUI arcade game collection featuring 7 classic games with polished modern UI. Built with PyQt6 for cross-platform desktop application support.

## 🎮 Games Included

1. **Snake** 🐍 - Guide your snake to eat food and grow longer without hitting yourself
2. **Tetris** 🧩 - Stack falling pieces and complete rows to clear the board
3. **Pong** 🎾 - Classic two-player paddle game with AI opponent
4. **Breakout** 🔨 - Bounce the ball to break all bricks with your paddle
5. **Geometry Dash** ⬜ - Jump through platforms and avoid obstacles with double-jump mechanics
6. **Minesweeper** 💣 - Reveal safe tiles but avoid the hidden mines
7. **Space Shooters** 🚀 - Defend your ship from incoming enemies in outer space

## 🚀 Features

- **Modern GUI**: Beautiful gradient backgrounds, smooth animations, and polished UI
- **Multiple Difficulty Levels**: Easy, Medium, and Hard modes for each game
- **Responsive Design**: Adaptive canvas scaling for different screen sizes
- **Clean Architecture**: Multi-file structure with separated game logic and UI components
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Professional Rendering**: Using PyQt6's sophisticated graphics system for high-quality visuals

## 📋 Project Structure

```
vanilla/
├── main.py                      # Main application entry point
├── constants.py                 # Global constants and configuration
├── base_game.py                 # Base game widget class
├── games_snake.py               # Snake game implementation
├── games_tetris.py              # Tetris game implementation
├── games_pong.py                # Pong game implementation
├── games_breakout.py            # Breakout game implementation
├── games_geometry_dash.py       # Geometry Dash implementation
├── games_minesweeper.py         # Minesweeper implementation
├── games_space_shooters.py      # Space Shooters implementation
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Installation

### Requirements
- Python 3.8 or higher
- PyQt6 6.6.0 or higher

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/vanilla.git
cd vanilla
```

2. **Create a virtual environment (optional but recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## ▶️ Running the Application

```bash
python main.py
```

The application will launch with the homepage. Click "PLAY NOW" to browse available games, select one, choose a difficulty level, and start playing!

## 🎮 Game Controls

### Snake
- **Arrow Keys** or **WASD** - Move the snake
- **ESC** - Return to menu

### Tetris
- **Arrow Keys** - Move pieces left/right
- **Arrow Down** - Drop piece faster
- **Space/Up Arrow/W** - Rotate piece
- **ESC** - Return to menu

### Pong
- **Arrow Up/W** - Move paddle up
- **Arrow Down/S** - Move paddle down
- **ESC** - Return to menu

### Breakout
- **Arrow Left/A** - Move paddle left
- **Arrow Right/D** - Move paddle right
- **ESC** - Return to menu

### Geometry Dash
- **Space/Up Arrow/W** - Jump (can double-jump mid-air)
- **ESC** - Return to menu

### Minesweeper
- **Left Mouse Click** - Reveal cell
- **Right Mouse Click** - Place/remove flag

### Space Shooters
- **Arrow Left/A** - Move left
- **Arrow Right/D** - Move right
- **Space** - Shoot
- **ESC** - Return to menu

## 🏗️ Architecture

### Constants (`constants.py`)
- Global color palette with theme colors
- Game configuration for each difficulty level
- Game registry with metadata

### Base Game Widget (`base_game.py`)
- Abstract base class for all games
- Handles common UI elements
- Provides game loop management

### Game Implementations
Each game is implemented as a separate module with:
- Game logic and state management
- Collision detection (where applicable)
- Score tracking
- Custom rendering with QPainter
- Keyboard/mouse input handling

### Main Application (`main.py`)
- Window management and layout
- Navigation between homepage, menu, level selection, and games
- Game instantiation and lifecycle management
- Consistent styling and theming across all screens

## 🎨 Design Highlights

- **Gradient Backgrounds**: Linear gradients create depth and visual appeal
- **Responsive Layouts**: All games adapt to different window sizes
- **Smooth Animations**: Game loops at 60 FPS for smooth gameplay
- **Consistent Color Scheme**: Professional purple/blue gradient theme
- **Typography**: Clear hierarchy with varied font sizes and weights

## 🔧 Customization

### Changing Colors
Edit the `Colors` class in `constants.py`:
```python
class Colors:
    PRIMARY = "#667eea"
    SECONDARY = "#764ba2"
    # ... other colors
```

### Adjusting Game Difficulty
Modify `LEVEL_CONFIG` in `constants.py` to adjust game parameters for each difficulty level.

### Adding New Games
1. Create a new file `games_newgame.py`
2. Implement a class inheriting from or similar to existing game widgets
3. Add the game to `GAMES` in `constants.py`
4. Import and register the game in `main.py`'s `start_game()` method

## 📊 Performance

- **FPS**: 60 frames per second target
- **Memory**: Efficient state management with minimal memory footprint
- **CPU**: Optimized rendering with minimal CPU usage
- **Responsive**: Instant UI responsiveness across all interactions

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Run `pip install -r requirements.txt` to install dependencies
- Check Python version: `python --version`

### Games lag or stutter
- Close other applications to free up system resources
- Ensure your graphics drivers are up to date
- Try running in fullscreen mode for better performance

### Input not working
- Ensure the game window is in focus
- Try different keyboard inputs (some keys may be mapped differently)
- Check if NumLock or other modifiers are active

## 📝 Technical Details

### Game Loop
- Games use QTimer for consistent frame timing (16.67ms per frame at 60 FPS)
- update_game() handles logic updates
- paintEvent() handles rendering
- Separate timers for different update frequencies (e.g., move_timer for Snake)

### Collision Detection
- Simple AABB (Axis-Aligned Bounding Box) collision detection
- Circle-Rectangle collision for round objects
- Grid-based collision for grid games (Tetris, Minesweeper)

### Rendering
- QPainter for all 2D graphics
- No external graphics libraries needed
- Direct pixel drawing for custom shapes

## 🎯 Future Enhancements

- [ ] Sound effects and background music
- [ ] High score persistence
- [ ] Multiplayer network support
- [ ] Additional games (Pac-Man, Asteroids, etc.)
- [ ] Game statistics and achievements
- [ ] Customizable key bindings
- [ ] Theme selection (dark/light/custom)

## 📄 License

This project is provided as-is for educational and entertainment purposes.

## 👨‍💻 Development

Built with:
- **PyQt6** - Modern cross-platform GUI framework
- **Python** - Clean, readable, maintainable code
- **QPainter** - Hardware-accelerated 2D graphics

## 🙏 Credits

Vanilla Arcade Hub is a modern reimplementation of classic arcade games, created to showcase Python GUI development with PyQt6.

---

**Enjoy playing! 🎮**
