/**
 * MINESWEEPER GAME MODULE
 * Classic Minesweeper implementation for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { GAME_WIDTH, GAME_HEIGHT, COLORS } from '../../js/constants.js';

// ==============================
// GAME CONFIGURATION BY LEVEL
// ==============================
const LEVEL_CONFIG = {
    1: { gridSize: 8, mineCount: 10, cellSize: 30 },
    2: { gridSize: 10, mineCount: 15, cellSize: 25 },
    3: { gridSize: 12, mineCount: 30, cellSize: 20 }
};

const PADDING = 10;

// ==============================
// GAME STATE
// ==============================
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    isRunning: true,
    gameOver: false,
    isWon: false,
    
    // Grid
    grid: [],
    revealed: [],
    flagged: [],
    
    // Configuration
    gridSize: 10,
    mineCount: 15,
    cellSize: 30,
    level: 1,
    
    // Timing
    startTime: null,
    elapsedSeconds: 0,
    timerInterval: null,
    
    // UI Elements
    statsDiv: null,
    
    // Event handling
    handleEsc: null,
    handleMouseClick: null,
    handleMouseContext: null
};

// ==============================
// INITIALIZATION & SETUP
// ==============================
function initializeGrid() {
    const size = gameState.gridSize;
    const mines = gameState.mineCount;
    
    // Place mines randomly
    let minesPlaced = 0;
    while (minesPlaced < mines) {
        const row = Math.floor(Math.random() * size);
        const col = Math.floor(Math.random() * size);
        
        if (gameState.grid[row][col] !== 'M') {
            gameState.grid[row][col] = 'M';
            minesPlaced++;
        }
    }
    
    // Calculate numbers
    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            if (gameState.grid[row][col] !== 'M') {
                let count = 0;
                for (let dr = -1; dr <= 1; dr++) {
                    for (let dc = -1; dc <= 1; dc++) {
                        const nr = row + dr;
                        const nc = col + dc;
                        if (nr >= 0 && nr < size && nc >= 0 && nc < size &&
                            gameState.grid[nr][nc] === 'M') {
                            count++;
                        }
                    }
                }
                gameState.grid[row][col] = count;
            }
        }
    }
}

function resetGame() {
    gameState.gameOver = false;
    gameState.isWon = false;
    gameState.isRunning = true;
    gameState.startTime = Date.now();
    gameState.elapsedSeconds = 0;
    gameState.grid = Array(gameState.gridSize).fill(null).map(() => Array(gameState.gridSize).fill(0));
    gameState.revealed = Array(gameState.gridSize).fill(null).map(() => Array(gameState.gridSize).fill(false));
    gameState.flagged = Array(gameState.gridSize).fill(null).map(() => Array(gameState.gridSize).fill(false));
    initializeGrid();
}

// ==============================
// GAME LOGIC
// ==============================
function revealCell(row, col) {
    const size = gameState.gridSize;
    if (row < 0 || row >= size || col < 0 || col >= size) return;
    if (gameState.revealed[row][col] || gameState.flagged[row][col] || gameState.gameOver) return;
    
    gameState.revealed[row][col] = true;
    
    // Hit a mine - game over
    if (gameState.grid[row][col] === 'M') {
        gameState.gameOver = true;
        gameState.isRunning = false;
        revealAllMines();
        return;
    }
    
    // If no adjacent mines, reveal adjacent cells
    if (gameState.grid[row][col] === 0) {
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                revealCell(row + dr, col + dc);
            }
        }
    }
    
    // Check for win
    checkWinCondition();
}

function toggleFlag(row, col) {
    const size = gameState.gridSize;
    if (row < 0 || row >= size || col < 0 || col >= size) return;
    if (gameState.revealed[row][col] || gameState.gameOver) return;
    
    gameState.flagged[row][col] = !gameState.flagged[row][col];
}

function revealAllMines() {
    const size = gameState.gridSize;
    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            if (gameState.grid[row][col] === 'M') {
                gameState.revealed[row][col] = true;
            }
        }
    }
}

function checkWinCondition() {
    const size = gameState.gridSize;
    const mines = gameState.mineCount;
    let revealedCount = 0;
    
    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            if (gameState.revealed[row][col] && gameState.grid[row][col] !== 'M') {
                revealedCount++;
            }
        }
    }
    
    const nonMineCount = size * size - mines;
    if (revealedCount === nonMineCount) {
        gameState.gameOver = true;
        gameState.isWon = true;
        gameState.isRunning = false;
    }
}

function getCellPosition(row, col) {
    const x = PADDING + col * gameState.cellSize;
    const y = PADDING + 40 + row * gameState.cellSize; // 40 for stats
    return { x, y };
}

function getCellFromPosition(x, y) {
    const col = Math.floor((x - PADDING) / gameState.cellSize);
    const row = Math.floor((y - PADDING - 40) / gameState.cellSize);
    
    const size = gameState.gridSize;
    if (row >= 0 && row < size && col >= 0 && col < size) {
        return { row, col };
    }
    return null;
}

// ==============================
// RENDERING
// ==============================
function drawGame() {
    const { ctx, canvas } = gameState;
    const size = gameState.gridSize;
    
    // Clear canvas
    ctx.fillStyle = COLORS.DARKER_BG;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw stats
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'left';
    
    const mineCount = gameState.mineCount - gameState.flagged.flat().filter(f => f).length;
    ctx.fillText(`Mines: ${mineCount}`, PADDING, PADDING + 20);
    ctx.fillText(`Time: ${gameState.elapsedSeconds}s`, PADDING + 150, PADDING + 20);
    ctx.fillText(`Level: ${gameState.level}`, PADDING + 300, PADDING + 20);
    
    // Draw grid
    for (let row = 0; row < size; row++) {
        for (let col = 0; col < size; col++) {
            const pos = getCellPosition(row, col);
            drawCell(pos.x, pos.y, row, col);
        }
    }
    
    // Draw game status
    if (gameState.gameOver) {
        if (gameState.isWon) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = COLORS.SUCCESS;
            ctx.font = 'bold 24px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('YOU WIN! 🎉', canvas.width / 2, canvas.height / 2 - 10);
            
            ctx.fillStyle = COLORS.WHITE;
            ctx.font = '14px Arial';
            ctx.fillText('Click to return to menu or press ESC', canvas.width / 2, canvas.height / 2 + 20);
        } else {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = COLORS.ERROR;
            ctx.font = 'bold 24px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('GAME OVER 💥', canvas.width / 2, canvas.height / 2 - 10);
            
            ctx.fillStyle = COLORS.WHITE;
            ctx.font = '14px Arial';
            ctx.fillText('Click to return to menu or press ESC', canvas.width / 2, canvas.height / 2 + 20);
        }
    }
}

function drawCell(x, y, row, col) {
    const { ctx } = gameState;
    const cellSize = gameState.cellSize;
    const fontSize = Math.max(10, cellSize - 10);
    
    const isRevealed = gameState.revealed[row][col];
    const isFlagged = gameState.flagged[row][col];
    const value = gameState.grid[row][col];
    
    // Draw cell background
    if (isRevealed) {
        ctx.fillStyle = '#333333';
    } else {
        ctx.fillStyle = COLORS.PRIMARY;
    }
    ctx.fillRect(x, y, cellSize, cellSize);
    
    // Draw border
    ctx.strokeStyle = '#555555';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, cellSize, cellSize);
    
    // Draw content
    
    if (isRevealed) {
        if (value === 'M') {
            // Draw mine
            ctx.fillStyle = COLORS.ERROR;
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('💣', x + cellSize / 2, y + cellSize / 2);
        } else if (value > 0) {
            // Draw number
            ctx.fillStyle = getNumberColor(value);
            ctx.font = `bold ${fontSize}px Arial`;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(value, x + cellSize / 2, y + cellSize / 2);
        }
    } else if (isFlagged) {
        // Draw flag
        ctx.fillStyle = COLORS.WARNING;
        ctx.font = `bold ${fontSize}px Arial`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🚩', x + cellSize / 2, y + cellSize / 2);
    }
}

function getNumberColor(num) {
    const colors = [
        '#0000ff', // 1 - blue
        '#008000', // 2 - green
        '#ff0000', // 3 - red
        '#000080', // 4 - dark blue
        '#800000', // 5 - maroon
        '#008080', // 6 - teal
        '#000000', // 7 - black
        '#808080'  // 8 - gray
    ];
    return colors[num - 1] || '#ffffff';
}

// ==============================
// EVENT HANDLERS
// ==============================
function handleCanvasClick(e) {
    if (gameState.gameOver) {
        window.navigate('MENU');
        return;
    }
    
    const rect = gameState.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const cell = getCellFromPosition(x, y);
    if (cell) {
        revealCell(cell.row, cell.col);
    }
}

function handleCanvasContextMenu(e) {
    e.preventDefault();
    
    if (gameState.gameOver) return;
    
    const rect = gameState.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const cell = getCellFromPosition(x, y);
    if (cell) {
        toggleFlag(cell.row, cell.col);
    }
}

function handleKeyDown(e) {
    if (e.key === 'Escape') {
        window.navigate('MENU');
    }
}

function updateTimer() {
    if (gameState.isRunning && gameState.startTime) {
        gameState.elapsedSeconds = Math.floor((Date.now() - gameState.startTime) / 1000);
    }
}

// ==============================
// GAME LOOP
// ==============================
function gameLoop() {
    updateTimer();
    drawGame();
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
}

// ==============================
// PUBLIC FUNCTIONS (MODULE INTERFACE)
// ==============================

/**
 * Load and initialize the Minesweeper game
 * @param {HTMLElement} containerElement - The container to render the game into
 * @param {number} level - The difficulty level (1, 2, or 3)
 */
export function load_game(containerElement, level = 1) {
    console.log(`Loading Minesweeper (Level ${level})...`);
    
    const config = LEVEL_CONFIG[level] || LEVEL_CONFIG[1];
    
    // Update game state config
    gameState.gridSize = config.gridSize;
    gameState.mineCount = config.mineCount;
    gameState.cellSize = config.cellSize;
    gameState.level = level;
    
    // Reset game state
    resetGame();
    
    // Create canvas
    const canvas = document.createElement('canvas');
    const gridWidth = PADDING * 2 + gameState.gridSize * gameState.cellSize;
    const gridHeight = PADDING * 2 + 40 + gameState.gridSize * gameState.cellSize;
    canvas.width = Math.max(gridWidth, 450);
    canvas.height = Math.max(gridHeight, 350);
    canvas.style.background = COLORS.DARKER_BG;
    canvas.style.border = `3px solid ${COLORS.PRIMARY}`;
    canvas.style.cursor = 'pointer';
    canvas.style.borderRadius = '8px';
    
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
    
    // Store event handlers for cleanup
    gameState.handleMouseClick = handleCanvasClick;
    gameState.handleMouseContext = handleCanvasContextMenu;
    gameState.handleEsc = handleKeyDown;
    
    // Add event listeners
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('contextmenu', handleCanvasContextMenu);
    window.addEventListener('keydown', handleKeyDown);
    
    // Start timer
    gameState.timerInterval = setInterval(() => {
        updateTimer();
    }, 100);
    
    // Start game loop
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
    
    console.log('Minesweeper game loaded successfully');
}

/**
 * Unload and cleanup the Minesweeper game
 */
export function unload_game() {
    console.log('Unloading Minesweeper game...');
    
    // Stop the game loop
    gameState.isRunning = false;
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    // Stop timer
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
    }
    
    // Remove event listeners
    if (gameState.canvas) {
        gameState.canvas.removeEventListener('click', gameState.handleMouseClick);
        gameState.canvas.removeEventListener('contextmenu', gameState.handleMouseContext);
    }
    window.removeEventListener('keydown', gameState.handleEsc);
    
    // Clear references
    gameState.canvas = null;
    gameState.ctx = null;
    gameState.handleMouseClick = null;
    gameState.handleMouseContext = null;
    gameState.handleEsc = null;
    
    console.log('Minesweeper game unloaded');
}
