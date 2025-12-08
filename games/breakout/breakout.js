/**
 * BREAKOUT GAME MODULE
 * Classic Breakout implementation for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { COLORS } from '../../js/constants.js';

// Level configuration
const LEVEL_CONFIG = {
    1: { brickRows: 3, ballSpeed: 4, paddleSpeed: 6, score: 10 },
    2: { brickRows: 4, ballSpeed: 6, paddleSpeed: 6, score: 20 },
    3: { brickRows: 5, ballSpeed: 8, paddleSpeed: 6, score: 30 }
};

// Game state
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    isRunning: true,
    gameOver: false,
    isWon: false,
    
    // Ball
    ball: { x: 0, y: 0, radius: 6, speedX: 5, speedY: -5 },
    
    // Paddle
    paddle: { x: 0, y: 0, width: 80, height: 12, speed: 6 },
    
    // Bricks
    bricks: [],
    
    // Score
    score: 0,
    level: 1,
    config: null,
    
    // Input
    keys: {},
    handleKeyDown: null,
    handleKeyUp: null
};

function initGame(level) {
    const config = LEVEL_CONFIG[level] || LEVEL_CONFIG[1];
    gameState.config = config;
    gameState.level = level;
    gameState.score = 0;
    gameState.gameOver = false;
    gameState.isWon = false;
    gameState.isRunning = true;
    gameState.keys = {};
    
    const width = 600;
    const height = 400;
    
    // Initialize ball
    gameState.ball.x = width / 2;
    gameState.ball.y = height - 80;
    gameState.ball.speedX = config.ballSpeed;
    gameState.ball.speedY = -config.ballSpeed;
    
    // Initialize paddle
    gameState.paddle.x = width / 2 - gameState.paddle.width / 2;
    gameState.paddle.y = height - 20;
    gameState.paddle.speed = config.paddleSpeed;
    
    // Initialize bricks
    const brickCols = 6;
    const brickWidth = (width - 20) / brickCols;
    const brickHeight = 15;
    gameState.bricks = [];
    
    for (let row = 0; row < config.brickRows; row++) {
        for (let col = 0; col < brickCols; col++) {
            gameState.bricks.push({
                x: 10 + col * brickWidth,
                y: 30 + row * (brickHeight + 5),
                width: brickWidth - 2,
                height: brickHeight,
                active: true
            });
        }
    }
}

function handleKeyDown(e) {
    gameState.keys[e.key.toLowerCase()] = true;
    if (e.key === 'Escape') {
        window.navigate('MENU');
    }
}

function handleKeyUp(e) {
    gameState.keys[e.key.toLowerCase()] = false;
}

function updateGame(width, height) {
    if (!gameState.isRunning) return;
    
    // Update paddle position
    if (gameState.keys['arrowleft'] && gameState.paddle.x > 0) {
        gameState.paddle.x -= gameState.paddle.speed;
    }
    if (gameState.keys['arrowright'] && gameState.paddle.x + gameState.paddle.width < width) {
        gameState.paddle.x += gameState.paddle.speed;
    }
    
    const ball = gameState.ball;
    const paddle = gameState.paddle;
    
    // Update ball position
    ball.x += ball.speedX;
    ball.y += ball.speedY;
    
    // Ball collision with walls
    if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= width) {
        ball.speedX *= -1;
        ball.x = Math.max(ball.radius, Math.min(width - ball.radius, ball.x));
    }
    
    if (ball.y - ball.radius <= 0) {
        ball.speedY *= -1;
        ball.y = ball.radius;
    }
    
    // Ball collision with paddle
    if (ball.speedY > 0 &&
        ball.y + ball.radius >= paddle.y &&
        ball.y - ball.radius <= paddle.y + paddle.height &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width) {
        ball.speedY *= -1;
        ball.y = paddle.y - ball.radius;
        
        // Add spin based on paddle contact
        const contactPoint = (ball.x - paddle.x) / paddle.width;
        ball.speedX = (contactPoint - 0.5) * 6 + (contactPoint - 0.5) * 3;
    }
    
    // Ball collision with bricks
    for (let i = 0; i < gameState.bricks.length; i++) {
        const brick = gameState.bricks[i];
        if (!brick.active) continue;
        
        if (ball.x + ball.radius >= brick.x &&
            ball.x - ball.radius <= brick.x + brick.width &&
            ball.y + ball.radius >= brick.y &&
            ball.y - ball.radius <= brick.y + brick.height) {
            brick.active = false;
            gameState.score += gameState.config.score;
            
            // Determine collision side
            const overlapLeft = (ball.x + ball.radius) - brick.x;
            const overlapRight = (brick.x + brick.width) - (ball.x - ball.radius);
            const overlapTop = (ball.y + ball.radius) - brick.y;
            const overlapBottom = (brick.y + brick.height) - (ball.y - ball.radius);
            
            const minOverlap = Math.min(overlapLeft, overlapRight, overlapTop, overlapBottom);
            
            if (minOverlap === overlapLeft || minOverlap === overlapRight) {
                ball.speedX *= -1;
            } else {
                ball.speedY *= -1;
            }
            break;
        }
    }
    
    // Check win condition
    if (gameState.bricks.every(brick => !brick.active)) {
        gameState.isWon = true;
        gameState.gameOver = true;
        gameState.isRunning = false;
    }
    
    // Ball out of bounds - game over
    if (ball.y - ball.radius > height) {
        gameState.gameOver = true;
        gameState.isRunning = false;
    }
}

function drawGame(width, height) {
    const { ctx, canvas, ball, paddle, bricks, score } = gameState;
    
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw paddle
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    
    // Draw ball
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw bricks
    bricks.forEach(brick => {
        if (brick.active) {
            ctx.fillStyle = COLORS.SECONDARY;
            ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
            ctx.strokeStyle = COLORS.PRIMARY;
            ctx.lineWidth = 1;
            ctx.strokeRect(brick.x, brick.y, brick.width, brick.height);
        }
    });
    
    // Draw score
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Poppins';
    ctx.textAlign = 'left';
    ctx.fillText(`Score: ${gameState.score}`, 10, 20);
    ctx.fillText(`Level: ${gameState.level}`, 10, 40);
    
    // Draw game status
    if (gameState.gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        if (gameState.isWon) {
            ctx.fillStyle = '#10b981';
            ctx.font = 'bold 24px Poppins';
            ctx.textAlign = 'center';
            ctx.fillText('YOU WIN! 🎉', canvas.width / 2, canvas.height / 2 - 20);
        } else {
            ctx.fillStyle = '#ef4444';
            ctx.font = 'bold 24px Poppins';
            ctx.textAlign = 'center';
            ctx.fillText('GAME OVER 💥', canvas.width / 2, canvas.height / 2 - 20);
        }
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Poppins';
        ctx.fillText(`Final Score: ${gameState.score}`, canvas.width / 2, canvas.height / 2 + 20);
    }
}

function gameLoop(width, height) {
    updateGame(width, height);
    drawGame(width, height);
    gameState.animationFrameId = requestAnimationFrame(() => gameLoop(width, height));
}

export function load_game(containerElement, level = 1) {
    console.log(`Loading Breakout (Level ${level})...`);
    
    initGame(level);
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = 600;
    canvas.height = 400;
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
    gameState.handleKeyUp = handleKeyUp;
    window.addEventListener('keydown', gameState.handleKeyDown);
    window.addEventListener('keyup', gameState.handleKeyUp);
    
    // Start game loop
    const width = canvas.width;
    const height = canvas.height;
    gameState.animationFrameId = requestAnimationFrame(() => gameLoop(width, height));
    
    console.log('Breakout loaded');
}

export function unload_game() {
    console.log('Unloading Breakout...');
    
    gameState.isRunning = false;
    
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    window.removeEventListener('keydown', gameState.handleKeyDown);
    window.removeEventListener('keyup', gameState.handleKeyUp);
    
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Breakout unloaded');
}
