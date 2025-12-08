/**
 * GLOBAL CONSTANTS
 * Central configuration file for the Vanilla.js Arcade Hub
 */

// Screen dimensions (standard size for all games)
export const GAME_WIDTH = 800;
export const GAME_HEIGHT = 500; // Accounting for header (600 - 100 for header/margins)

// Target FPS (requestAnimationFrame will be used, but setInterval can use this)
export const TARGET_FPS = 60;
export const FRAME_TIME = 1000 / TARGET_FPS; // ~16.67ms per frame

// Game container reference
export const getGameContainer = () => document.getElementById('game-container');

// Application states
export const APP_STATES = {
    MENU: 'MENU',
    PONG: 'PONG',
    MINESWEEPER: 'MINESWEEPER'
};

// Color palette
export const COLORS = {
    PRIMARY: '#667eea',
    SECONDARY: '#764ba2',
    DARK_BG: '#1a1a1a',
    DARKER_BG: '#0f0f0f',
    WHITE: '#ffffff',
    BLACK: '#000000',
    SUCCESS: '#10b981',
    WARNING: '#f59e0b',
    ERROR: '#ef4444'
};

// Standard game padding/margins
export const PADDING = 20;
export const MARGIN = 10;
