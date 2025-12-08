/**
 * ROUTER & GAME MANAGER
 * Central routing logic and Game Registry for the Vanilla.js Arcade Hub
 * Handles all state transitions and dynamic game loading/unloading
 */

import { getGameContainer } from './constants.js';
import { loadHomepage, loadMenu, loadLevelSelection } from './menu.js';

// Navigation states
const NAV_STATES = {
    HOME: 'HOME',
    MENU: 'MENU',
    LEVELS: 'LEVELS',
    GAME: 'GAME'
};

// ==============================
// GAME REGISTRY WITH LEVELS
// ==============================
const GAME_REGISTRY = {
    GEOMETRY_DASH: {
        name: 'Geometry Dash',
        description: 'Jump your way through platforms and avoid obstacles in this fast-paced adventure!',
        modulePath: './games/geometry-dash/geometry-dash.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    },
    TETRIS: {
        name: 'Tetris',
        description: 'Stack the falling pieces and complete rows to clear the board!',
        modulePath: './games/tetris/tetris.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    },
    SNAKE: {
        name: 'Snake',
        description: 'Guide your snake to eat food and grow longer without hitting yourself!',
        modulePath: './games/snake/snake.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    },
    BREAKOUT: {
        name: 'Breakout',
        description: 'Bounce the ball to break all the bricks with your paddle!',
        modulePath: './games/breakout/breakout.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    },
    SPACE_SHOOTERS: {
        name: 'Space Shooters',
        description: 'Defend your ship from incoming enemies in outer space!',
        modulePath: './games/space-shooters/space-shooters.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    },
    MINESWEEPER: {
        name: 'Minesweeper',
        description: 'Reveal safe tiles but avoid the hidden mines!',
        modulePath: './games/minesweeper/minesweeper.js',
        module: null,
        levels: [
            { name: 'Easy', level: 1 },
            { name: 'Medium', level: 2 },
            { name: 'Hard', level: 3 }
        ]
    }
};

// ==============================
// GLOBAL STATE
// ==============================
let currentState = NAV_STATES.HOME;
let currentGameKey = null;
let currentModule = null;
let currentLevel = 1;

// ==============================
// HEADER VISIBILITY MANAGEMENT
// ==============================
function updateHeaderVisibility() {
    const logoButton = document.getElementById('logoButton');
    
    if (currentState === NAV_STATES.HOME) {
        logoButton.classList.add('hidden');
    } else {
        logoButton.classList.remove('hidden');
    }
}

// ==============================
// NAVIGATION FUNCTION
// Core function for all state transitions
// ==============================
export async function navigate(targetState, gameKey = null, level = 1) {
    const container = getGameContainer();
    
    console.log(`Navigating to ${targetState}${gameKey ? ` - ${gameKey}` : ''}${level ? ` Level ${level}` : ''}`);

    // Step 1: Unload current game if one is running
    if (currentModule && typeof currentModule.unload_game === 'function') {
        console.log(`Unloading game: ${currentGameKey}`);
        currentModule.unload_game();
        currentModule = null;
    }

    // Step 2: Update global state
    currentState = targetState;
    currentGameKey = gameKey;
    currentLevel = level;

    // Step 3: Clear the container and load new content
    container.innerHTML = '';

    try {
        if (targetState === NAV_STATES.HOME) {
            loadHomepage();
        } else if (targetState === NAV_STATES.MENU) {
            loadMenu();
        } else if (targetState === NAV_STATES.LEVELS) {
            loadLevelSelection(gameKey);
        } else if (targetState === NAV_STATES.GAME) {
            // Load the game dynamically
            const gameConfig = GAME_REGISTRY[gameKey];
            
            if (!gameConfig) {
                throw new Error(`Game not found: ${gameKey}`);
            }
            
            console.log(`Dynamically importing: ${gameConfig.modulePath}`);
            const importedModule = await import(gameConfig.modulePath);
            
            // Store module reference
            currentModule = importedModule;
            gameConfig.module = importedModule;

            // Create game page wrapper
            const gamePageDiv = document.createElement('div');
            gamePageDiv.className = 'game-page';

            // Initialize the game
            if (typeof importedModule.load_game === 'function') {
                console.log(`Loading game: ${gameKey} at level ${level}`);
                importedModule.load_game(gamePageDiv, level);
            } else {
                throw new Error(`Game module ${gameKey} does not export load_game function`);
            }

            container.appendChild(gamePageDiv);
        }
        
        // Update header visibility
        updateHeaderVisibility();
    } catch (error) {
        console.error(`Navigation error:`, error);
        // Fallback to home on error
        setTimeout(() => navigate(NAV_STATES.HOME), 500);
    }
}

// ==============================
// HELPER FUNCTIONS
// ==============================
export function returnToHome() {
    navigate(NAV_STATES.HOME);
}

export function returnToMenu() {
    navigate(NAV_STATES.MENU);
}

export function goToLevels(gameKey) {
    navigate(NAV_STATES.LEVELS, gameKey);
}

export function startGame(gameKey, level = 1) {
    navigate(NAV_STATES.GAME, gameKey, level);
}

export function getAllGames() {
    return Object.entries(GAME_REGISTRY).map(([key, config]) => ({
        key,
        name: config.name,
        description: config.description,
        levels: config.levels
    }));
}

export function getGameLevels(gameKey) {
    const game = GAME_REGISTRY[gameKey];
    return game ? game.levels : [];
}

export function getCurrentLevel() {
    return currentLevel;
}

export function getCurrentState() {
    return currentState;
}

// ==============================
// INITIALIZE ROUTER
// Called on app startup - shows homepage
// ==============================
export function initRouter() {
    // Make navigate function globally accessible
    window.navigate = navigate;
    window.returnToHome = returnToHome;
    window.returnToMenu = returnToMenu;
    window.goToLevels = goToLevels;
    window.startGame = startGame;
    
    // Setup logo button to go home
    const logoButton = document.getElementById('logoButton');
    logoButton.addEventListener('click', returnToHome);
    
    console.log('Router initialized. Available games:', Object.keys(GAME_REGISTRY));
    
    // Show the homepage on startup
    navigate(NAV_STATES.HOME);
}
