/**
 * TETRIS GAME MODULE
 * Classic Tetris implementation for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { COLORS } from '../../js/constants.js';
import { getCurrentLevel } from '../../js/router.js';

// Game configuration based on level
const LEVEL_CONFIG = {
    1: { gridWidth: 10, gridHeight: 20, cellSize: 25, dropSpeed: 1000, score: 100 },
    2: { gridWidth: 10, gridHeight: 20, cellSize: 25, dropSpeed: 600, score: 150 },
    3: { gridWidth: 10, gridHeight: 20, cellSize: 25, dropSpeed: 300, score: 200 }
};

// Tetromino shapes
const TETROMINOES = [
    [[0, 0, 1], [1, 1, 1]], // L
    [[1, 0, 0], [1, 1, 1]], // J
    [[1, 1], [1, 1]],       // O
    [[0, 1, 1], [1, 1, 0]], // S
    [[1, 1, 0], [0, 1, 1]], // Z
    [[1, 1, 1, 1]],         // I
    [[1, 1, 1], [0, 1, 0]]  // T
];

const COLORS_TETRIS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BD7AF7'];

// Game state
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    dropIntervalId: null,
    isRunning: true,
    gameOver: false,
    
    // Game grid and current piece
    grid: [],
    currentPiece: null,
    nextPiece: null,
    currentX: 0,
    currentY: 0,
    currentRotation: 0,
    
    // Score and level
    score: 0,
    lines: 0,
    level: 1,
    
    // Configuration
    config: null,
    
    // Event handlers
    handleKeyDown: null,
    handleEsc: null
};

function initGame(level) {
    const config = LEVEL_CONFIG[level] || LEVEL_CONFIG[1];
    gameState.config = config;
    gameState.level = level;
    gameState.score = 0;
    gameState.lines = 0;
    gameState.gameOver = false;
    gameState.isRunning = true;
    
    // Initialize grid
    gameState.grid = Array(config.gridHeight).fill(null).map(() => Array(config.gridWidth).fill(0));
    
    // Set first piece
    spawnNewPiece();
}

function spawnNewPiece() {
    if (!gameState.nextPiece) {
        gameState.nextPiece = TETROMINOES[Math.floor(Math.random() * TETROMINOES.length)];
    }
    
    gameState.currentPiece = gameState.nextPiece;
    gameState.nextPiece = TETROMINOES[Math.floor(Math.random() * TETROMINOES.length)];
    gameState.currentX = Math.floor(gameState.config.gridWidth / 2) - 1;
    gameState.currentY = 0;
    gameState.currentRotation = 0;
    
    if (canPlace(gameState.currentPiece, gameState.currentX, gameState.currentY)) {
        return true;
    } else {
        gameState.gameOver = true;
        gameState.isRunning = false;
        return false;
    }
}

function rotatePiece(piece) {
    const n = piece.length;
    const rotated = Array(piece[0].length).fill(null).map(() => Array(n).fill(0));
    for (let i = 0; i < n; i++) {
        for (let j = 0; j < piece[0].length; j++) {
            rotated[j][n - 1 - i] = piece[i][j];
        }
    }
    return rotated;
}

function canPlace(piece, x, y) {
    for (let i = 0; i < piece.length; i++) {
        for (let j = 0; j < piece[i].length; j++) {
            if (piece[i][j]) {
                const newX = x + j;
                const newY = y + i;
                
                if (newX < 0 || newX >= gameState.config.gridWidth || 
                    newY >= gameState.config.gridHeight) {
                    return false;
                }
                
                if (newY >= 0 && gameState.grid[newY][newX]) {
                    return false;
                }
            }
        }
    }
    return true;
}

function placePiece() {
    const piece = gameState.currentPiece;
    const x = gameState.currentX;
    const y = gameState.currentY;
    const colorIndex = TETROMINOES.indexOf(piece) % COLORS_TETRIS.length;
    
    for (let i = 0; i < piece.length; i++) {
        for (let j = 0; j < piece[i].length; j++) {
            if (piece[i][j]) {
                const gridX = x + j;
                const gridY = y + i;
                if (gridY >= 0 && gridY < gameState.config.gridHeight && 
                    gridX >= 0 && gridX < gameState.config.gridWidth) {
                    gameState.grid[gridY][gridX] = colorIndex + 1;
                }
            }
        }
    }
    
    clearLines();
    spawnNewPiece();
}

function clearLines() {
    let linesCleared = 0;
    
    for (let i = gameState.grid.length - 1; i >= 0; i--) {
        if (gameState.grid[i].every(cell => cell !== 0)) {
            gameState.grid.splice(i, 1);
            gameState.grid.unshift(Array(gameState.config.gridWidth).fill(0));
            linesCleared++;
        }
    }
    
    if (linesCleared > 0) {
        gameState.lines += linesCleared;
        gameState.score += linesCleared * gameState.config.score;
    }
}

function handleKeyDown(e) {
    if (!gameState.isRunning) return;
    
    switch (e.key.toLowerCase()) {
        case 'arrowleft':
            if (canPlace(gameState.currentPiece, gameState.currentX - 1, gameState.currentY)) {
                gameState.currentX--;
            }
            e.preventDefault();
            break;
        case 'arrowright':
            if (canPlace(gameState.currentPiece, gameState.currentX + 1, gameState.currentY)) {
                gameState.currentX++;
            }
            e.preventDefault();
            break;
        case 'arrowdown':
            if (canPlace(gameState.currentPiece, gameState.currentX, gameState.currentY + 1)) {
                gameState.currentY++;
            }
            e.preventDefault();
            break;
        case ' ':
            const rotated = rotatePiece(gameState.currentPiece);
            if (canPlace(rotated, gameState.currentX, gameState.currentY)) {
                gameState.currentPiece = rotated;
            }
            e.preventDefault();
            break;
        case 'escape':
            window.navigate('MENU');
            break;
    }
}

function updateGame() {
    if (!gameState.isRunning) return;
    
    if (canPlace(gameState.currentPiece, gameState.currentX, gameState.currentY + 1)) {
        gameState.currentY++;
    } else {
        placePiece();
    }
}

function drawGame() {
    const { ctx, canvas, config, grid } = gameState;
    const { gridWidth, gridHeight, cellSize } = config;
    
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(10, 30, gridWidth * cellSize + 2, gridHeight * cellSize + 2);
    
    // Draw grid cells
    for (let i = 0; i < gridHeight; i++) {
        for (let j = 0; j < gridWidth; j++) {
            const cellValue = grid[i][j];
            if (cellValue > 0) {
                ctx.fillStyle = COLORS_TETRIS[cellValue - 1];
                ctx.fillRect(10 + j * cellSize + 1, 30 + i * cellSize + 1, cellSize - 2, cellSize - 2);
            }
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 1;
            ctx.strokeRect(10 + j * cellSize + 1, 30 + i * cellSize + 1, cellSize - 2, cellSize - 2);
        }
    }
    
    // Draw current piece
    if (gameState.currentPiece) {
        const piece = gameState.currentPiece;
        const colorIndex = TETROMINOES.indexOf(piece) % COLORS_TETRIS.length;
        ctx.fillStyle = COLORS_TETRIS[colorIndex];
        
        for (let i = 0; i < piece.length; i++) {
            for (let j = 0; j < piece[i].length; j++) {
                if (piece[i][j]) {
                    ctx.fillRect(
                        10 + (gameState.currentX + j) * cellSize + 1,
                        30 + (gameState.currentY + i) * cellSize + 1,
                        cellSize - 2,
                        cellSize - 2
                    );
                }
            }
        }
    }
    
    // Draw stats
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Poppins';
    ctx.textAlign = 'right';
    ctx.fillText(`Score: ${gameState.score}`, canvas.width - 10, 20);
    ctx.fillText(`Lines: ${gameState.lines}`, canvas.width - 10, 40);
    ctx.fillText(`Level: ${gameState.level}`, canvas.width - 10, 60);
    
    // Draw game over
    if (gameState.gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ef4444';
        ctx.font = 'bold 24px Poppins';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 20);
        ctx.fillStyle = '#fff';
        ctx.font = '12px Poppins';
        ctx.fillText(`Final Score: ${gameState.score}`, canvas.width / 2, canvas.height / 2 + 20);
    }
}

function gameLoop() {
    if (!gameState.isRunning) return;
    drawGame();
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
}

export function load_game(containerElement, level = 1) {
    console.log(`Loading Tetris (Level ${level})...`);
    
    initGame(level);
    
    // Create canvas
    const config = gameState.config;
    const canvas = document.createElement('canvas');
    canvas.width = 400;
    canvas.height = 600;
    canvas.style.background = '#000';
    canvas.style.border = `3px solid ${COLORS.PRIMARY}`;
    
    gameState.canvas = canvas;
    gameState.ctx = canvas.getContext('2d');
    
    // Create back button
    const backButton = document.createElement('button');
    backButton.className = 'back-button';
    backButton.textContent = '← Menu';
    backButton.addEventListener('click', () => window.navigate('MENU'));
    
    // Add to container
    containerElement.appendChild(canvas);
    containerElement.appendChild(backButton);
    
    // Add event listeners
    gameState.handleKeyDown = handleKeyDown;
    window.addEventListener('keydown', handleKeyDown);
    
    // Start drop interval
    gameState.dropIntervalId = setInterval(() => {
        updateGame();
    }, gameState.config.dropSpeed);
    
    // Start game loop
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
    
    console.log('Tetris game loaded');
}

export function unload_game() {
    console.log('Unloading Tetris...');
    
    gameState.isRunning = false;
    
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    if (gameState.dropIntervalId) {
        clearInterval(gameState.dropIntervalId);
    }
    
    window.removeEventListener('keydown', gameState.handleKeyDown);
    
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Tetris unloaded');
}
