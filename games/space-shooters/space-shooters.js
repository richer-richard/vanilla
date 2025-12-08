/**
 * SPACE SHOOTERS GAME MODULE
 * Classic space shooter for Vanilla.js Arcade Hub
 * Exports: load_game(containerElement, level), unload_game()
 */

import { COLORS } from '../../js/constants.js';

// Level configuration
const LEVEL_CONFIG = {
    1: { enemySpawn: 0.02, enemySpeed: 2, bulletSpeed: 7, score: 10 },
    2: { enemySpawn: 0.04, enemySpeed: 3, bulletSpeed: 8, score: 20 },
    3: { enemySpawn: 0.06, enemySpeed: 4, bulletSpeed: 9, score: 30 }
};

// Game state
let gameState = {
    canvas: null,
    ctx: null,
    animationFrameId: null,
    isRunning: true,
    gameOver: false,
    
    // Player
    player: { x: 0, y: 0, width: 30, height: 30, speed: 5 },
    bullets: [],
    
    // Enemies
    enemies: [],
    enemyBullets: [],
    
    // Score
    score: 0,
    health: 3,
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
    gameState.health = 3;
    gameState.gameOver = false;
    gameState.isRunning = true;
    gameState.bullets = [];
    gameState.enemies = [];
    gameState.enemyBullets = [];
    gameState.keys = {};
    
    // Initialize player
    gameState.player.x = 275;
    gameState.player.y = 550;
}

function handleKeyDown(e) {
    gameState.keys[e.key.toLowerCase()] = true;
    
    if (e.key === ' ' && gameState.isRunning) {
        // Shoot bullet
        gameState.bullets.push({
            x: gameState.player.x + gameState.player.width / 2 - 2,
            y: gameState.player.y - 5,
            width: 4,
            height: 15,
            speed: gameState.config.bulletSpeed
        });
        e.preventDefault();
    }
    
    if (e.key === 'Escape') {
        window.navigate('MENU');
    }
}

function handleKeyUp(e) {
    gameState.keys[e.key.toLowerCase()] = false;
}

function updateGame(width, height) {
    if (!gameState.isRunning) return;
    
    // Update player
    if (gameState.keys['arrowleft'] && gameState.player.x > 0) {
        gameState.player.x -= gameState.player.speed;
    }
    if (gameState.keys['arrowright'] && gameState.player.x + gameState.player.width < width) {
        gameState.player.x += gameState.player.speed;
    }
    if (gameState.keys['arrowup'] && gameState.player.y > height / 2) {
        gameState.player.y -= gameState.player.speed;
    }
    if (gameState.keys['arrowdown'] && gameState.player.y + gameState.player.height < height) {
        gameState.player.y += gameState.player.speed;
    }
    
    // Update bullets
    for (let i = gameState.bullets.length - 1; i >= 0; i--) {
        const bullet = gameState.bullets[i];
        bullet.y -= bullet.speed;
        
        if (bullet.y < 0) {
            gameState.bullets.splice(i, 1);
        }
    }
    
    // Update enemies
    for (let i = gameState.enemies.length - 1; i >= 0; i--) {
        const enemy = gameState.enemies[i];
        enemy.y += gameState.config.enemySpeed;
        
        // Random shooting
        if (Math.random() < 0.01) {
            gameState.enemyBullets.push({
                x: enemy.x + enemy.width / 2 - 2,
                y: enemy.y + enemy.height,
                width: 4,
                height: 15,
                speed: 4
            });
        }
        
        // Check if off-screen
        if (enemy.y > height) {
            gameState.enemies.splice(i, 1);
        }
    }
    
    // Update enemy bullets
    for (let i = gameState.enemyBullets.length - 1; i >= 0; i--) {
        const bullet = gameState.enemyBullets[i];
        bullet.y += bullet.speed;
        
        if (bullet.y > height) {
            gameState.enemyBullets.splice(i, 1);
        }
    }
    
    // Spawn enemies
    if (Math.random() < gameState.config.enemySpawn) {
        gameState.enemies.push({
            x: Math.random() * (width - 30),
            y: -30,
            width: 30,
            height: 30,
            active: true
        });
    }
    
    // Bullet-enemy collision
    for (let i = gameState.bullets.length - 1; i >= 0; i--) {
        const bullet = gameState.bullets[i];
        
        for (let j = gameState.enemies.length - 1; j >= 0; j--) {
            const enemy = gameState.enemies[j];
            
            if (bullet.x + bullet.width > enemy.x &&
                bullet.x < enemy.x + enemy.width &&
                bullet.y + bullet.height > enemy.y &&
                bullet.y < enemy.y + enemy.height) {
                
                gameState.bullets.splice(i, 1);
                gameState.enemies.splice(j, 1);
                gameState.score += gameState.config.score;
                break;
            }
        }
    }
    
    // Enemy bullet-player collision
    for (let i = gameState.enemyBullets.length - 1; i >= 0; i--) {
        const bullet = gameState.enemyBullets[i];
        
        if (bullet.x + bullet.width > gameState.player.x &&
            bullet.x < gameState.player.x + gameState.player.width &&
            bullet.y + bullet.height > gameState.player.y &&
            bullet.y < gameState.player.y + gameState.player.height) {
            
            gameState.health--;
            gameState.enemyBullets.splice(i, 1);
            
            if (gameState.health <= 0) {
                gameState.gameOver = true;
                gameState.isRunning = false;
            }
        }
    }
    
    // Enemy-player collision
    for (let i = gameState.enemies.length - 1; i >= 0; i--) {
        const enemy = gameState.enemies[i];
        
        if (enemy.x + enemy.width > gameState.player.x &&
            enemy.x < gameState.player.x + gameState.player.width &&
            enemy.y + enemy.height > gameState.player.y &&
            enemy.y < gameState.player.y + gameState.player.height) {
            
            gameState.health -= 2;
            gameState.enemies.splice(i, 1);
            
            if (gameState.health <= 0) {
                gameState.gameOver = true;
                gameState.isRunning = false;
            }
        }
    }
}

function drawGame(width, height) {
    const { ctx, canvas, player, bullets, enemies, enemyBullets, score, health, level } = gameState;
    
    // Clear canvas with space background
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw stars (background)
    ctx.fillStyle = '#fff';
    ctx.globalAlpha = 0.5;
    for (let i = 0; i < 50; i++) {
        const x = (i * 1234) % width;
        const y = (i * 5678 + Date.now() * 0.01) % height;
        ctx.beginPath();
        ctx.arc(x, y, 1, 0, Math.PI * 2);
        ctx.fill();
    }
    ctx.globalAlpha = 1;
    
    // Draw player
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.fillRect(player.x, player.y, player.width, player.height);
    ctx.fillStyle = '#fff';
    ctx.fillRect(player.x + 10, player.y + 5, 10, 15);
    
    // Draw bullets
    ctx.fillStyle = '#10b981';
    bullets.forEach(bullet => {
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
    });
    
    // Draw enemies
    ctx.fillStyle = '#ef4444';
    enemies.forEach(enemy => {
        ctx.fillRect(enemy.x, enemy.y, enemy.width, enemy.height);
        ctx.fillStyle = '#fca5a5';
        ctx.fillRect(enemy.x + 5, enemy.y + 5, 6, 6);
        ctx.fillRect(enemy.x + 19, enemy.y + 5, 6, 6);
        ctx.fillStyle = '#ef4444';
    });
    
    // Draw enemy bullets
    ctx.fillStyle = '#f59e0b';
    enemyBullets.forEach(bullet => {
        ctx.fillRect(bullet.x, bullet.y, bullet.width, bullet.height);
    });
    
    // Draw HUD
    ctx.fillStyle = COLORS.PRIMARY;
    ctx.font = 'bold 14px Poppins';
    ctx.textAlign = 'left';
    ctx.fillText(`Score: ${gameState.score}`, 10, 25);
    ctx.fillText(`Health: ${gameState.health}`, 10, 45);
    ctx.fillText(`Level: ${gameState.level}`, 10, 65);
    
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
        ctx.fillText(`Final Score: ${gameState.score}`, canvas.width / 2, canvas.height / 2 + 20);
    }
}

function gameLoop(width, height) {
    updateGame(width, height);
    drawGame(width, height);
    gameState.animationFrameId = requestAnimationFrame(() => gameLoop(width, height));
}

export function load_game(containerElement, level = 1) {
    console.log(`Loading Space Shooters (Level ${level})...`);
    
    initGame(level);
    
    // Create canvas
    const canvas = document.createElement('canvas');
    canvas.width = 600;
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
    gameState.handleKeyUp = handleKeyUp;
    window.addEventListener('keydown', gameState.handleKeyDown);
    window.addEventListener('keyup', gameState.handleKeyUp);
    
    // Start game loop
    const width = canvas.width;
    const height = canvas.height;
    gameState.animationFrameId = requestAnimationFrame(() => gameLoop(width, height));
    
    console.log('Space Shooters loaded');
}

export function unload_game() {
    console.log('Unloading Space Shooters...');
    
    gameState.isRunning = false;
    
    if (gameState.animationFrameId) {
        cancelAnimationFrame(gameState.animationFrameId);
    }
    
    window.removeEventListener('keydown', gameState.handleKeyDown);
    window.removeEventListener('keyup', gameState.handleKeyUp);
    
    gameState.canvas = null;
    gameState.ctx = null;
    
    console.log('Space Shooters unloaded');
}
