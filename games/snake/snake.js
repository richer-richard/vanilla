/**
 * SNAKE GAME MODULE
 * Classic Snake implementation for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { COLORS } from '../../js/constants.js';

// Level configuration
const LEVEL_CONFIG = {
    1: { gridSize: 20, speed: 150, score: 10 },
    2: { gridSize: 20, speed: 100, score: 15 },
    3: { gridSize: 20, speed: 60, score: 20 }
};

// Game state
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    moveIntervalId: null,
    isRunning: true,
    gameOver: false,
    
    // Snake
    snake: [{ x: 10, y: 10 }],
    food: { x: 15, y: 15 },
    direction: { x: 1, y: 0 },
    nextDirection: { x: 1, y: 0 },
    
    // Score
    score: 0,
    level: 1,
    config: null,
    
    // Event handlers
    handleKeyDown: null
};

function initGame(level) {
    const config = LEVEL_CONFIG[level] || LEVEL_CONFIG[1];
    gameState.config = config;
    gameState.level = level;
    gameState.score = 0;
    gameState.gameOver = false;
    gameState.isRunning = true;
    gameState.snake = [{ x: 10, y: 10 }];
    gameState.direction = { x: 1, y: 0 };
    gameState.nextDirection = { x: 1, y: 0 };
    spawnFood();
}

function spawnFood() {
    const config = gameState.config;
    let food;
    let validPosition = false;
    
    while (!validPosition) {
        food = {
            x: Math.floor(Math.random() * config.gridSize),
            y: Math.floor(Math.random() * config.gridSize)
        };
        
        validPosition = !gameState.snake.some(segment => segment.x === food.x && segment.y === food.y);
    }
    
    gameState.food = food;
}

function handleKeyDown(e) {
    switch (e.key.toLowerCase()) {
        case 'arrowup':
            if (gameState.direction.y === 0) {
                gameState.nextDirection = { x: 0, y: -1 };
            }
            e.preventDefault();
            break;
        case 'arrowdown':
            if (gameState.direction.y === 0) {
                gameState.nextDirection = { x: 0, y: 1 };
            }
            e.preventDefault();
            break;
        case 'arrowleft':
            if (gameState.direction.x === 0) {
                gameState.nextDirection = { x: -1, y: 0 };
            }
            e.preventDefault();
            break;
        case 'arrowright':
            if (gameState.direction.x === 0) {
                gameState.nextDirection = { x: 1, y: 0 };
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
    
    gameState.direction = { ...gameState.nextDirection };
    
    const head = gameState.snake[0];
    const newHead = {
        x: head.x + gameState.direction.x,
        y: head.y + gameState.direction.y
    };
    
    const config = gameState.config;
    
    // Check wall collision
    if (newHead.x < 0 || newHead.x >= config.gridSize || 
        newHead.y < 0 || newHead.y >= config.gridSize) {
        gameState.gameOver = true;
        gameState.isRunning = false;
        return;
    }
    
    // Check self collision
    if (gameState.snake.some(segment => segment.x === newHead.x && segment.y === newHead.y)) {
        gameState.gameOver = true;
        gameState.isRunning = false;
        return;
    }
    
    gameState.snake.unshift(newHead);
    
    // Check food collision
    if (newHead.x === gameState.food.x && newHead.y === gameState.food.y) {
        gameState.score += gameState.config.score;
        spawnFood();
    } else {
        gameState.snake.pop();
    }
}

function drawGame() {
    const { ctx, canvas, config, snake, food } = gameState;
    const cellSize = canvas.width / config.gridSize;
    
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw grid
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 0.5;
    for (let i = 0; i <= config.gridSize; i++) {
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, canvas.height);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(canvas.width, i * cellSize);
        ctx.stroke();
    }
    
    // Draw snake
    snake.forEach((segment, index) => {
        if (index === 0) {
            ctx.fillStyle = '#10b981';
        } else {
            ctx.fillStyle = '#059669';
        }
        ctx.fillRect(segment.x * cellSize + 1, segment.y * cellSize + 1, cellSize - 2, cellSize - 2);
        ctx.strokeStyle = '#047857';
        ctx.lineWidth = 1;
        ctx.strokeRect(segment.x * cellSize + 1, segment.y * cellSize + 1, cellSize - 2, cellSize - 2);
    });
    
    // Draw food
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(food.x * cellSize + cellSize / 2, food.y * cellSize + cellSize / 2, cellSize / 2 - 2, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw stats
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Poppins';
    ctx.textAlign = 'left';
    ctx.fillText(`Score: ${gameState.score}`, 10, 20);
    ctx.fillText(`Level: ${gameState.level}`, 10, 40);
    
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
    drawGame();
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
}

export function load_game(containerElement, level = 1) {
    console.log(`Loading Snake (Level ${level})...`);
    
    initGame(level);
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = 500;
    canvas.height = 500;
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
    
    // Start move interval
    gameState.moveIntervalId = setInterval(() => {
        updateGame();
    }, gameState.config.speed);
    
    // Start game loop
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
    
    console.log('Snake game loaded');
}

export function unload_game() {
    console.log('Unloading Snake...');
    
    gameState.isRunning = false;
    
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    if (gameState.moveIntervalId) {
        clearInterval(gameState.moveIntervalId);
    }
    
    window.removeEventListener('keydown', gameState.handleKeyDown);
    
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Snake unloaded');
}
