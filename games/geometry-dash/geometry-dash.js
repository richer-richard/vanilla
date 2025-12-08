/**
 * GEOMETRY DASH GAME MODULE
 * Fast-paced jumping game for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { COLORS } from '../../js/constants.js';

// Level configuration
const LEVEL_CONFIG = {
    1: { scrollSpeed: 6, obstacleFrequency: 0.08, platformSize: 40, score: 1 },
    2: { scrollSpeed: 9, obstacleFrequency: 0.12, platformSize: 35, score: 2 },
    3: { scrollSpeed: 12, obstacleFrequency: 0.15, platformSize: 30, score: 3 }
};

// Game state
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    isRunning: true,
    gameOver: false,
    
    // Player
    player: { x: 50, y: 0, size: 25, velocityY: 0, isJumping: false, jumpPower: 15 },
    gravity: 0.6,
    
    // World
    platforms: [],
    obstacles: [],
    scrollX: 0,
    
    // Score
    score: 0,
    level: 1,
    config: null,
    
    // Input
    spacePressedThisFrame: false,
    handleKeyDown: null,
    handleKeyUp: null
};

function initGame(level) {
    const config = LEVEL_CONFIG[level] || LEVEL_CONFIG[1];
    gameState.config = config;
    gameState.level = level;
    gameState.score = 0;
    gameState.gameOver = false;
    gameState.isRunning = true;
    gameState.scrollX = 0;
    gameState.platforms = [];
    gameState.obstacles = [];
    
    // Initialize player
    gameState.player.x = 50;
    gameState.player.y = 300;
    gameState.player.velocityY = 0;
    gameState.player.isJumping = false;
    
    // Create initial platforms
    for (let i = 0; i < 20; i++) {
        const x = i * 120;
        const y = 320 + Math.sin(i * 0.5) * 30;
        gameState.platforms.push({
            x: x,
            y: y,
            width: config.platformSize,
            height: 15,
            active: true
        });
    }
}

function handleKeyDown(e) {
    if (e.code === 'Space') {
        gameState.spacePressedThisFrame = true;
        e.preventDefault();
    }
    if (e.key === 'Escape') {
        window.navigate('MENU');
    }
}

function handleKeyUp(e) {
    if (e.code === 'Space') {
        gameState.spacePressedThisFrame = false;
    }
}

function updateGame(width, height) {
    if (!gameState.isRunning) return;
    
    const player = gameState.player;
    const config = gameState.config;
    
    // Jump
    if (gameState.spacePressedThisFrame && !player.isJumping) {
        player.velocityY = -player.jumpPower;
        player.isJumping = true;
    }
    
    // Apply gravity
    player.velocityY += gameState.gravity;
    player.y += player.velocityY;
    
    // Platform collision
    let onPlatform = false;
    for (let platform of gameState.platforms) {
        if (platform.active &&
            player.y + player.size >= platform.y &&
            player.y + player.size <= platform.y + platform.height + 5 &&
            player.velocityY >= 0 &&
            player.x + player.size > platform.x &&
            player.x < platform.x + platform.width) {
            
            player.velocityY = 0;
            player.y = platform.y - player.size;
            player.isJumping = false;
            onPlatform = true;
        }
    }
    
    // Scroll world
    gameState.scrollX += config.scrollSpeed;
    gameState.score += config.score;
    
    // Generate new platforms
    if (gameState.platforms[gameState.platforms.length - 1].x < gameState.scrollX + width) {
        const lastPlatform = gameState.platforms[gameState.platforms.length - 1];
        const newX = lastPlatform.x + 120 + Math.random() * 40;
        const newY = 250 + Math.sin(gameState.platforms.length * 0.5) * 50 + (Math.random() - 0.5) * 60;
        
        gameState.platforms.push({
            x: newX,
            y: newY,
            width: config.platformSize,
            height: 15,
            active: true
        });
    }
    
    // Generate obstacles
    if (Math.random() < config.obstacleFrequency) {
        const lastObstacle = gameState.obstacles[gameState.obstacles.length - 1];
        if (!lastObstacle || lastObstacle.x < gameState.scrollX + width - 200) {
            const newX = gameState.scrollX + width;
            const newY = 290 + Math.random() * 60;
            
            gameState.obstacles.push({
                x: newX,
                y: newY,
                width: 30,
                height: 30,
                active: true
            });
        }
    }
    
    // Obstacle collision
    for (let obstacle of gameState.obstacles) {
        if (obstacle.active &&
            player.x + player.size > obstacle.x &&
            player.x < obstacle.x + obstacle.width &&
            player.y + player.size > obstacle.y &&
            player.y < obstacle.y + obstacle.height) {
            
            gameState.gameOver = true;
            gameState.isRunning = false;
        }
    }
    
    // Remove off-screen platforms and obstacles
    gameState.platforms = gameState.platforms.filter(p => p.x > gameState.scrollX - 100);
    gameState.obstacles = gameState.obstacles.filter(o => o.x > gameState.scrollX - 100);
    
    // Fall off the world
    if (player.y > height) {
        gameState.gameOver = true;
        gameState.isRunning = false;
    }
}

function drawGame(width, height) {
    const { ctx, canvas, player, platforms, obstacles, score, scrollX } = gameState;
    
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw ground
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, height - 20, width, 20);
    
    // Draw platforms
    platforms.forEach(platform => {
        if (platform.active && platform.x > scrollX - 100 && platform.x < scrollX + width) {
            ctx.fillStyle = COLORS.PRIMARY;
            ctx.fillRect(platform.x - scrollX, platform.y, platform.width, platform.height);
            ctx.strokeStyle = COLORS.SECONDARY;
            ctx.lineWidth = 2;
            ctx.strokeRect(platform.x - scrollX, platform.y, platform.width, platform.height);
        }
    });
    
    // Draw obstacles
    obstacles.forEach(obstacle => {
        if (obstacle.active && obstacle.x > scrollX - 100 && obstacle.x < scrollX + width) {
            ctx.fillStyle = '#ef4444';
            ctx.beginPath();
            ctx.moveTo(obstacle.x - scrollX + obstacle.width / 2, obstacle.y);
            ctx.lineTo(obstacle.x - scrollX + obstacle.width, obstacle.y + obstacle.height / 2);
            ctx.lineTo(obstacle.x - scrollX + obstacle.width / 2, obstacle.y + obstacle.height);
            ctx.lineTo(obstacle.x - scrollX, obstacle.y + obstacle.height / 2);
            ctx.closePath();
            ctx.fill();
        }
    });
    
    // Draw player
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.fillRect(player.x, player.y, player.size, player.size);
    ctx.fillStyle = '#fff';
    ctx.fillRect(player.x + 5, player.y + 5, 6, 6);
    ctx.fillRect(player.x + 14, player.y + 5, 6, 6);
    
    // Draw score
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Poppins';
    ctx.textAlign = 'left';
    ctx.fillText(`Distance: ${gameState.score}`, 10, 25);
    ctx.fillText(`Level: ${gameState.level}`, 10, 45);
    
    // Draw game over
    if (gameState.gameOver) {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#ef4444';
        ctx.font = 'bold 24px Poppins';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER 💥', canvas.width / 2, canvas.height / 2 - 20);
        ctx.fillStyle = '#fff';
        ctx.font = '12px Poppins';
        ctx.fillText(`Distance: ${gameState.score}`, canvas.width / 2, canvas.height / 2 + 20);
    }
}

function gameLoop(width, height) {
    updateGame(width, height);
    drawGame(width, height);
    gameState.animationFrameId = requestAnimationFrame(() => gameLoop(width, height));
}

export function load_game(containerElement, level = 1) {
    console.log(`Loading Geometry Dash (Level ${level})...`);
    
    initGame(level);
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = 800;
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
    
    console.log('Geometry Dash loaded');
}

export function unload_game() {
    console.log('Unloading Geometry Dash...');
    
    gameState.isRunning = false;
    
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    window.removeEventListener('keydown', gameState.handleKeyDown);
    window.removeEventListener('keyup', gameState.handleKeyUp);
    
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Geometry Dash unloaded');
}
