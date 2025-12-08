/**
 * PONG GAME MODULE
 * Classic Pong implementation for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement), unload_game()
 */

import { GAME_WIDTH, GAME_HEIGHT, TARGET_FPS, COLORS } from '../../js/constants.js';

// ==============================
// GAME STATE
// ==============================
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    isRunning: true,
    
    // Game objects
    ball: {
        x: GAME_WIDTH / 2,
        y: GAME_HEIGHT / 2,
        width: 10,
        height: 10,
        speedX: 5,
        speedY: 5,
        maxSpeed: 8
    },
    
    paddle1: {
        x: 10,
        y: GAME_HEIGHT / 2 - 50,
        width: 10,
        height: 100,
        speed: 6,
        dy: 0
    },
    
    paddle2: {
        x: GAME_WIDTH - 20,
        y: GAME_HEIGHT / 2 - 50,
        width: 10,
        height: 100,
        speed: 6,
        dy: 0
    },
    
    score: {
        player1: 0,
        player2: 0
    },
    
    // Input state
    keys: {}
};

// ==============================
// EVENT LISTENERS
// ==============================
function handleKeyDown(e) {
    gameState.keys[e.key.toLowerCase()] = true;
}

function handleKeyUp(e) {
    gameState.keys[e.key.toLowerCase()] = false;
}

// ==============================
// GAME LOGIC
// ==============================
function updateGame() {
    const { ball, paddle1, paddle2, keys } = gameState;
    
    // Handle paddle 1 input (W/S keys)
    if (keys['w'] && paddle1.y > 0) {
        paddle1.y -= paddle1.speed;
    }
    if (keys['s'] && paddle1.y + paddle1.height < GAME_HEIGHT) {
        paddle1.y += paddle1.speed;
    }
    
    // Handle paddle 2 input (Up/Down arrow keys)
    if (keys['arrowup'] && paddle2.y > 0) {
        paddle2.y -= paddle2.speed;
    }
    if (keys['arrowdown'] && paddle2.y + paddle2.height < GAME_HEIGHT) {
        paddle2.y += paddle2.speed;
    }
    
    // Update ball position
    ball.x += ball.speedX;
    ball.y += ball.speedY;
    
    // Ball collision with top/bottom
    if (ball.y <= 0 || ball.y + ball.height >= GAME_HEIGHT) {
        ball.speedY *= -1;
        ball.y = Math.max(0, Math.min(GAME_HEIGHT - ball.height, ball.y));
    }
    
    // Ball collision with paddles
    if (
        ball.x < paddle1.x + paddle1.width &&
        ball.y + ball.height > paddle1.y &&
        ball.y < paddle1.y + paddle1.height
    ) {
        ball.speedX *= -1;
        ball.x = paddle1.x + paddle1.width;
        // Add spin based on paddle position
        const deltaY = (ball.y - (paddle1.y + paddle1.height / 2)) / (paddle1.height / 2);
        ball.speedY += deltaY * 3;
    }
    
    if (
        ball.x + ball.width > paddle2.x &&
        ball.y + ball.height > paddle2.y &&
        ball.y < paddle2.y + paddle2.height
    ) {
        ball.speedX *= -1;
        ball.x = paddle2.x - ball.width;
        // Add spin based on paddle position
        const deltaY = (ball.y - (paddle2.y + paddle2.height / 2)) / (paddle2.height / 2);
        ball.speedY += deltaY * 3;
    }
    
    // Limit ball speed
    const speed = Math.sqrt(ball.speedX ** 2 + ball.speedY ** 2);
    if (speed > ball.maxSpeed) {
        ball.speedX = (ball.speedX / speed) * ball.maxSpeed;
        ball.speedY = (ball.speedY / speed) * ball.maxSpeed;
    }
    
    // Ball out of bounds - scoring
    if (ball.x < 0) {
        gameState.score.player2++;
        resetBall();
    }
    if (ball.x > GAME_WIDTH) {
        gameState.score.player1++;
        resetBall();
    }
}

function resetBall() {
    const { ball } = gameState;
    ball.x = GAME_WIDTH / 2;
    ball.y = GAME_HEIGHT / 2;
    ball.speedX = (Math.random() > 0.5 ? 1 : -1) * 5;
    ball.speedY = (Math.random() - 0.5) * 5;
}

// ==============================
// RENDERING
// ==============================
function drawGame() {
    const { ctx, canvas, ball, paddle1, paddle2, score } = gameState;
    
    // Clear canvas
    ctx.fillStyle = COLORS.BLACK;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw center line
    ctx.strokeStyle = COLORS.PRIMARY;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(GAME_WIDTH / 2, 0);
    ctx.lineTo(GAME_WIDTH / 2, GAME_HEIGHT);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw paddles
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.fillRect(paddle1.x, paddle1.y, paddle1.width, paddle1.height);
    ctx.fillRect(paddle2.x, paddle2.y, paddle2.width, paddle2.height);
    
    // Draw ball
    ctx.fillStyle = COLORS.WHITE;
    ctx.fillRect(ball.x, ball.y, ball.width, ball.height);
    
    // Draw scores
    ctx.font = 'bold 32px Arial';
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.textAlign = 'center';
    ctx.fillText(score.player1, GAME_WIDTH / 4, 40);
    ctx.fillText(score.player2, (GAME_WIDTH * 3) / 4, 40);
    
    // Draw instructions
    ctx.font = '12px Arial';
    ctx.fillStyle = COLORS.SECONDARY;
    ctx.textAlign = 'center';
    ctx.fillText('P1: W/S | P2: UP/DOWN | Back: ESC', GAME_WIDTH / 2, GAME_HEIGHT - 10);
}

// ==============================
// GAME LOOP
// ==============================
function gameLoop() {
    if (!gameState.isRunning) return;
    
    updateGame();
    drawGame();
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
}

// ==============================
// PUBLIC FUNCTIONS (MODULE INTERFACE)
// ==============================

/**
 * Load and initialize the Pong game
 * @param {HTMLElement} containerElement - The container to render the game into
 */
export function load_game(containerElement) {
    console.log('Loading Pong game...');
    
    // Reset game state
    gameState.isRunning = true;
    gameState.score = { player1: 0, player2: 0 };
    gameState.keys = {};
    resetBall();
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = GAME_WIDTH;
    canvas.height = GAME_HEIGHT;
    canvas.style.background = COLORS.BLACK;
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
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    
    // Handle ESC key to return to menu
    const handleEsc = (e) => {
        if (e.key === 'Escape') {
            window.navigate('MENU');
        }
    };
    window.addEventListener('keydown', handleEsc);
    gameState.handleEsc = handleEsc;
    
    // Start game loop
    gameState.animationFrameId = requestAnimationFrame(gameLoop);
    
    console.log('Pong game loaded successfully');
}

/**
 * Unload and cleanup the Pong game
 */
export function unload_game() {
    console.log('Unloading Pong game...');
    
    // Stop the game loop
    gameState.isRunning = false;
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    // Remove event listeners
    window.removeEventListener('keydown', handleKeyDown);
    window.removeEventListener('keyup', handleKeyUp);
    if (gameState.handleEsc) {
        window.removeEventListener('keydown', gameState.handleEsc);
    }
    
    // Clear canvas reference
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Pong game unloaded');
}
