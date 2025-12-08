/**
 * MAIN MENU & HOMEPAGE MODULE
 * Handles homepage, game selection menu, and level selection
 */

import { getGameContainer } from './constants.js';
import { getAllGames, getGameLevels } from './router.js';

/**
 * Load and display the homepage
 */
export function loadHomepage() {
    const container = getGameContainer();
    
    // Create homepage structure
    const homepageDiv = document.createElement('div');
    homepageDiv.className = 'homepage';
    
    // Content wrapper
    const contentDiv = document.createElement('div');
    contentDiv.className = 'homepage-content';
    
    // Title
    const title = document.createElement('h1');
    title.textContent = 'VANILLA';
    contentDiv.appendChild(title);
    
    // Subtitle
    const subtitle = document.createElement('h2');
    subtitle.textContent = 'Classic Games Reimagined';
    contentDiv.appendChild(subtitle);
    
    // Introduction
    const introDiv = document.createElement('div');
    introDiv.className = 'homepage-intro';
    
    const introPara = document.createElement('p');
    introPara.textContent = 'Step into the world of classic arcade gaming. Experience timeless games with modern design and smooth gameplay. Relive the joy of retro gaming or discover them for the first time.';
    introDiv.appendChild(introPara);
    contentDiv.appendChild(introDiv);
    
    // CTA Button
    const ctaButton = document.createElement('button');
    ctaButton.className = 'cta-button';
    ctaButton.textContent = 'Play Now';
    ctaButton.addEventListener('click', () => {
        window.navigate('MENU');
    });
    contentDiv.appendChild(ctaButton);
    
    homepageDiv.appendChild(contentDiv);
    
    // Clear container and add homepage
    container.innerHTML = '';
    container.appendChild(homepageDiv);
    
    console.log('Homepage loaded');
}

/**
 * Load and display the game selection menu
 */
export function loadMenu() {
    const container = getGameContainer();
    
    // Create menu structure
    const menuDiv = document.createElement('div');
    menuDiv.className = 'games-menu';
    
    // Menu title
    const title = document.createElement('div');
    title.className = 'games-menu-title';
    title.textContent = 'Select Your Game';
    menuDiv.appendChild(title);
    
    // Games grid
    const gamesGrid = document.createElement('div');
    gamesGrid.className = 'games-grid';
    
    // Get all games from registry and create game cards
    const games = getAllGames();
    
    games.forEach(game => {
        const gameCard = document.createElement('div');
        gameCard.className = 'game-card';
        
        // Card content wrapper
        const cardContent = document.createElement('div');
        cardContent.className = 'game-card-content';
        
        // Game name
        const gameName = document.createElement('h3');
        gameName.textContent = game.name;
        cardContent.appendChild(gameName);
        
        // Game description
        const gameDesc = document.createElement('p');
        gameDesc.textContent = game.description;
        cardContent.appendChild(gameDesc);
        
        // Difficulty badges
        const badgesDiv = document.createElement('div');
        badgesDiv.className = 'difficulty-badges';
        
        game.levels.forEach(level => {
            const badge = document.createElement('span');
            badge.className = 'difficulty-badge';
            badge.textContent = level.name;
            badgesDiv.appendChild(badge);
        });
        
        cardContent.appendChild(badgesDiv);
        gameCard.appendChild(cardContent);
        
        // Add click handler to navigate to level selection
        gameCard.addEventListener('click', () => {
            window.goToLevels(game.key);
        });
        
        gamesGrid.appendChild(gameCard);
    });
    
    menuDiv.appendChild(gamesGrid);
    
    // Clear container and add menu
    container.innerHTML = '';
    container.appendChild(menuDiv);
    
    console.log('Game selection menu loaded');
}

/**
 * Load and display the level selection page
 */
export function loadLevelSelection(gameKey) {
    const container = getGameContainer();
    
    // Find game info
    const games = getAllGames();
    const game = games.find(g => g.key === gameKey);
    
    if (!game) {
        console.error(`Game not found: ${gameKey}`);
        return;
    }
    
    // Create level selection structure
    const levelDiv = document.createElement('div');
    levelDiv.className = 'level-selection';
    
    // Header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'level-header';
    
    const gameTitle = document.createElement('h2');
    gameTitle.textContent = game.name;
    headerDiv.appendChild(gameTitle);
    
    const gameSubtitle = document.createElement('p');
    gameSubtitle.textContent = 'Select your difficulty level';
    headerDiv.appendChild(gameSubtitle);
    
    levelDiv.appendChild(headerDiv);
    
    // Levels grid
    const levelsGrid = document.createElement('div');
    levelsGrid.className = 'levels-grid';
    
    game.levels.forEach(levelConfig => {
        const levelBtn = document.createElement('button');
        levelBtn.className = 'level-button';
        levelBtn.textContent = levelConfig.name;
        
        levelBtn.addEventListener('click', () => {
            window.startGame(gameKey, levelConfig.level);
        });
        
        levelsGrid.appendChild(levelBtn);
    });
    
    levelDiv.appendChild(levelsGrid);
    
    // Clear container and add level selection
    container.innerHTML = '';
    container.appendChild(levelDiv);
    
    console.log(`Level selection loaded for ${game.name}`);
}
