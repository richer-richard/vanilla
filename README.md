# VANILLA - Arcade Hub

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![HTML5](https://img.shields.io/badge/HTML5-Canvas-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-yellow.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

A modern web-based arcade hub featuring 6 classic games reimagined with HTML5 Canvas, vanilla JavaScript, and a Python Flask backend. Experience timeless arcade gameplay with smooth 60 FPS rendering, responsive controls, and polished modern UI.

## 🎮 Games Included

1. **Snake** 🐍 - Navigate your growing snake through the grid. Eat food without hitting yourself or walls.
2. **Pong** 🎾 - Classic two-player paddle game with adaptive AI opponent and realistic ball physics.
3. **Breakout** 🔨 - Break colorful bricks with your paddle. Clear levels as speed ramps up.
4. **Geometry Dash** ⬜ - Jump through procedurally generated obstacles with double-jump mechanics.
5. **Minesweeper** 💣 - Logic puzzle classic. Reveal safe tiles and flag mines using deduction.
6. **Space Shooters** 🚀 - Defend your ship against alien waves. Collect power-ups and survive!

## ✨ Features

- **Modern Web Interface**: Beautiful gradient backgrounds, smooth animations, and glass-morphism UI
- **Multiple Difficulty Levels**: Easy, Medium, and Hard modes for each game
- **Responsive Design**: Adaptive canvas scaling for different screen sizes
- **Persistent High Scores**: LocalStorage for client-side best scores, backend for global leaderboards
- **Python Backend**: Flask server for procedural generation, AI logic, and score persistence
- **Smooth Gameplay**: 60 FPS target with optimized rendering and efficient game loops
- **Full Controls**: Keyboard, mouse, and touch support with pause/restart functionality

## 📋 Project Structure

```
vanilla/
├── index.html                   # Homepage
├── games.html                   # Game selection page
├── about.html                   # About/introduction page
├── styles.css                   # Global styles
├── server.py                    # Flask backend server
├── scores.json                  # Persistent score storage
├── backends/                    # Python backend modules
│   ├── __init__.py
│   ├── snake.py                 # Snake food placement logic
│   ├── pong.py                  # Pong AI targeting logic
│   ├── breakout.py              # Breakout level generation
│   ├── geometry_dash.py         # Geometry Dash pattern generation
│   ├── minesweeper.py           # Minesweeper board generation
│   └── space_shooters.py        # Space Shooters wave planning
├── snake/                       # Snake game files
│   ├── intro.html               # Game introduction page
│   └── game.html                # Main game page
├── pong/                        # Pong game files
│   ├── intro.html
│   └── game.html
├── breakout/                    # Breakout game files
│   ├── intro.html
│   └── game.html
├── geometry_dash/               # Geometry Dash game files
│   ├── intro.html
│   └── game.html
├── minesweeper/                 # Minesweeper game files
│   ├── intro.html
│   └── game.html
└── space_shooters/              # Space Shooters game files
    ├── intro.html
    └── game.html
```

## 🔧 Installation

### Requirements
- Python 3.8 or higher
- Flask 2.0+

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/vanilla.git
cd vanilla
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install flask
```

## ▶️ Running the Application

### Start the Flask server:
```bash
python server.py
```

The server will start on `http://localhost:5000` by default. Open this URL in your web browser to access the arcade hub.

### Environment Variables (Optional)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)
- `DEBUG` - Enable debug mode (default: False)

```bash
# Example
HOST=127.0.0.1 PORT=8080 DEBUG=1 python server.py
```

## 🎮 Game Controls

### Snake
- **Arrow Keys** or **WASD** - Move the snake
- **Space** - Pause/Resume
- **R** - Restart

### Pong
- **W/S** or **↑/↓** - Move paddle up/down
- **Space** - Serve ball
- **P** - Pause/Resume

### Breakout
- **A/D** or **←/→** - Move paddle left/right
- **Space** - Launch ball
- **P** - Pause/Resume

### Geometry Dash
- **Space/W/↑** - Jump (hold for longer jump, can double-jump)
- **P** - Pause/Resume
- **R** - Restart

### Minesweeper
- **Left Click** - Reveal cell
- **Right Click** - Place/remove flag
- **Double Click** - Chord (auto-reveal adjacent cells)

### Space Shooters
- **A/D** or **←/→** - Move ship left/right
- **Space** - Shoot (or enable autofire with Shift)
- **Shift** - Toggle autofire
- **P** - Pause/Resume

## 🏗️ Architecture

### Frontend
- **HTML5 Canvas** - All game rendering using native Canvas API
- **Vanilla JavaScript** - No frameworks, pure JavaScript for all game logic
- **CSS3** - Modern styling with gradients, animations, and responsive design
- **LocalStorage** - Client-side high score persistence per game/difficulty

### Backend (Python Flask)
- **REST API** - JSON endpoints for game data and leaderboards
- **Procedural Generation** - Server-side generation of game content (obstacles, patterns, levels)
- **AI Logic** - Pong AI targeting calculations
- **Score Management** - Persistent JSON-based score storage with thread-safe operations

### API Endpoints

```
GET  /                           # Serve homepage
GET  /health                     # Health check
GET  /scores                     # Get all scores
GET  /leaderboard/<game>         # Get leaderboard for specific game
POST /score                      # Submit a new score

POST /api/snake/food             # Generate optimal food placement
POST /api/pong/ai-target         # Calculate AI paddle target
POST /api/breakout/level         # Generate breakout level layout
POST /api/geometry/pattern       # Generate obstacle patterns
POST /api/minesweeper/board      # Generate minesweeper board
POST /api/space/wave             # Generate enemy wave configuration
```

## 🎨 Design Highlights

- **Gradient Backgrounds**: Purple-blue gradient theme throughout
- **Glass-morphism Effects**: Modern translucent card designs
- **Smooth Animations**: CSS transitions and JavaScript-based game animations
- **Responsive Layouts**: Mobile-friendly with adaptive canvas sizing
- **Consistent Color Scheme**: Professional purple/blue/green palette
- **Typography**: Poppins and Press Start 2P fonts for modern/retro contrast

## 🔧 Customization

### Changing Colors
Edit the color values in `styles.css` or individual game HTML files:
```css
/* Example gradient */
background: linear-gradient(90deg, #667eea, #764ba2);
```

### Adjusting Game Difficulty
Each game has a `CONFIG` object in its game.html file:
```javascript
const CONFIG = {
    easy: { /* parameters */ },
    medium: { /* parameters */ },
    hard: { /* parameters */ }
};
```

### Adding New Games
1. Create a new directory: `newgame/`
2. Add `intro.html` and `game.html` files
3. Implement game logic using Canvas API
4. Add backend module in `backends/newgame.py` if needed
5. Register API endpoint in `server.py`
6. Add game card to `games.html`

## 📊 Performance

- **FPS**: 60 frames per second target with requestAnimationFrame
- **Memory**: Efficient state management with minimal memory footprint
- **CPU**: Optimized rendering with minimal CPU usage
- **Responsive**: Instant UI responsiveness across all interactions
- **Network**: Optional backend features gracefully degrade when offline

## 🐛 Troubleshooting

### Games not loading
- Ensure Flask server is running on port 5000
- Check browser console for JavaScript errors
- Verify all HTML files are in correct directories

### Backend features not working
- Check that Flask server is running: `python server.py`
- Verify Python dependencies are installed: `pip install flask`
- Check server console for error messages
- Games will use fallback client-side logic if backend is unavailable

### Performance issues
- Close other browser tabs to free resources
- Disable browser extensions that might interfere
- Try a different browser (Chrome/Firefox recommended)
- Check that hardware acceleration is enabled in browser settings

## 🌐 Browser Compatibility

Tested and working on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 📝 Technical Details

### Game Loop Pattern
All games use a consistent pattern:
```javascript
function loop(timestamp) {
    requestAnimationFrame(loop);
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    if (state === 'running') {
        update(deltaTime);
    }
    render();
}
```

### Collision Detection
- **AABB (Axis-Aligned Bounding Box)** - For rectangular collision
- **Circle-Rectangle** - For round objects vs rectangles
- **Grid-based** - For Minesweeper tile logic
- **Precise triangle collision** - For Geometry Dash spike detection

### State Management
Each game maintains a state machine:
- `ready` - Initial state, waiting to start
- `running` - Active gameplay
- `paused` - Game paused
- `over` - Game ended

## 🎯 Future Enhancements

- [ ] Sound effects and background music
- [ ] Global online leaderboards with user accounts
- [ ] Additional games (Pac-Man, Asteroids, Tetris, etc.)
- [ ] Multiplayer network support
- [ ] Achievement system and statistics
- [ ] Customizable key bindings
- [ ] Theme selection (dark/light/custom)
- [ ] Mobile app (PWA) version
- [ ] Game replays and sharing

## 📄 License

This project is provided for educational and entertainment purposes.

## 👨‍💻 Development

Built with:
- **HTML5 Canvas** - Hardware-accelerated 2D graphics
- **Vanilla JavaScript** - Clean, readable, maintainable code
- **CSS3** - Modern responsive design
- **Python Flask** - Lightweight backend framework
- **No external game libraries** - Pure web technologies

## 🙏 Acknowledgments

VANILLA Arcade Hub is a modern reimplementation of classic arcade games, created to showcase web development with vanilla technologies and demonstrate how timeless game mechanics can be brought into the modern web era.

---

**Enjoy playing! 🎮**

Visit `/about.html` for more information about the project.
