/**
 * VANILLA Achievement System
 * 
 * Provides achievement tracking, unlocking, and display for the Vanilla Collection.
 * Achievements are stored in localStorage and can be triggered from any game.
 * 
 * @module achievements
 * @version 1.0.0
 */

// ============================================================================
// ACHIEVEMENT DEFINITIONS
// ============================================================================

const ACHIEVEMENTS = {
    // ========== GENERAL ACHIEVEMENTS ==========
    first_game: {
        id: 'first_game',
        name: 'First Steps',
        description: 'Play your first game',
        icon: '🎮',
        category: 'general',
        secret: false,
        points: 10
    },
    five_games: {
        id: 'five_games',
        name: 'Getting Warmed Up',
        description: 'Play 5 games',
        icon: '🔥',
        category: 'general',
        secret: false,
        points: 25
    },
    twenty_games: {
        id: 'twenty_games',
        name: 'Dedicated Gamer',
        description: 'Play 20 games',
        icon: '⭐',
        category: 'general',
        secret: false,
        points: 50
    },
    hundred_games: {
        id: 'hundred_games',
        name: 'Arcade Legend',
        description: 'Play 100 games',
        icon: '🏆',
        category: 'general',
        secret: false,
        points: 100
    },
    all_games_played: {
        id: 'all_games_played',
        name: 'Explorer',
        description: 'Play every game at least once',
        icon: '🗺️',
        category: 'general',
        secret: false,
        points: 50
    },
    all_difficulties: {
        id: 'all_difficulties',
        name: 'Challenge Accepted',
        description: 'Complete a game on each difficulty',
        icon: '🎯',
        category: 'general',
        secret: false,
        points: 30
    },
    night_owl: {
        id: 'night_owl',
        name: 'Night Owl',
        description: 'Play a game after midnight',
        icon: '🦉',
        category: 'general',
        secret: true,
        points: 15
    },
    early_bird: {
        id: 'early_bird',
        name: 'Early Bird',
        description: 'Play a game before 6 AM',
        icon: '🐦',
        category: 'general',
        secret: true,
        points: 15
    },
    
    // ========== SNAKE ACHIEVEMENTS ==========
    snake_first_win: {
        id: 'snake_first_win',
        name: 'Snek Start',
        description: 'Score 50 points in Snake',
        icon: '🐍',
        category: 'snake',
        secret: false,
        points: 10
    },
    snake_centurion: {
        id: 'snake_centurion',
        name: 'Centurion',
        description: 'Score 100 points in Snake',
        icon: '💯',
        category: 'snake',
        secret: false,
        points: 25
    },
    snake_master: {
        id: 'snake_master',
        name: 'Snake Charmer',
        description: 'Score 200 points in Snake',
        icon: '🎭',
        category: 'snake',
        secret: false,
        points: 50
    },
    snake_hard_win: {
        id: 'snake_hard_win',
        name: 'Nimble Serpent',
        description: 'Score 100 points in Snake on Hard',
        icon: '⚡',
        category: 'snake',
        secret: false,
        points: 75
    },
    snake_perfect_10: {
        id: 'snake_perfect_10',
        name: 'Perfect Ten',
        description: 'Eat 10 food without hitting anything',
        icon: '🍎',
        category: 'snake',
        secret: false,
        points: 20
    },
    
    // ========== PONG ACHIEVEMENTS ==========
    pong_first_win: {
        id: 'pong_first_win',
        name: 'First Rally',
        description: 'Win a game of Pong',
        icon: '🎾',
        category: 'pong',
        secret: false,
        points: 10
    },
    pong_shutout: {
        id: 'pong_shutout',
        name: 'Shutout',
        description: 'Win a game without letting the AI score',
        icon: '🛡️',
        category: 'pong',
        secret: false,
        points: 50
    },
    pong_hard_win: {
        id: 'pong_hard_win',
        name: 'Paddle Master',
        description: 'Beat the AI on Hard difficulty',
        icon: '🏓',
        category: 'pong',
        secret: false,
        points: 75
    },
    pong_comeback: {
        id: 'pong_comeback',
        name: 'Comeback King',
        description: 'Win after being down 0-4',
        icon: '👑',
        category: 'pong',
        secret: true,
        points: 100
    },
    pong_rally_master: {
        id: 'pong_rally_master',
        name: 'Rally Master',
        description: 'Have a rally of 20+ hits',
        icon: '🔄',
        category: 'pong',
        secret: false,
        points: 30
    },
    
    // ========== BREAKOUT ACHIEVEMENTS ==========
    breakout_first_clear: {
        id: 'breakout_first_clear',
        name: 'Brick Breaker',
        description: 'Clear your first level in Breakout',
        icon: '🧱',
        category: 'breakout',
        secret: false,
        points: 10
    },
    breakout_level_5: {
        id: 'breakout_level_5',
        name: 'Breaking Through',
        description: 'Reach level 5 in Breakout',
        icon: '🔨',
        category: 'breakout',
        secret: false,
        points: 25
    },
    breakout_level_10: {
        id: 'breakout_level_10',
        name: 'Demolition Expert',
        description: 'Reach level 10 in Breakout',
        icon: '💥',
        category: 'breakout',
        secret: false,
        points: 50
    },
    breakout_no_miss: {
        id: 'breakout_no_miss',
        name: 'Perfect Reflexes',
        description: 'Clear a level without losing a life',
        icon: '✨',
        category: 'breakout',
        secret: false,
        points: 30
    },
    breakout_hard_5: {
        id: 'breakout_hard_5',
        name: 'Hardcore Breaker',
        description: 'Reach level 5 on Hard difficulty',
        icon: '💪',
        category: 'breakout',
        secret: false,
        points: 75
    },
    
    // ========== GEOMETRY DASH ACHIEVEMENTS ==========
    geometry_first_500: {
        id: 'geometry_first_500',
        name: 'Jumping Jack',
        description: 'Travel 500 distance in Geometry Dash',
        icon: '⬜',
        category: 'geometry_dash',
        secret: false,
        points: 10
    },
    geometry_2000: {
        id: 'geometry_2000',
        name: 'Sky Walker',
        description: 'Travel 2000 distance in Geometry Dash',
        icon: '☁️',
        category: 'geometry_dash',
        secret: false,
        points: 30
    },
    geometry_5000: {
        id: 'geometry_5000',
        name: 'Geometry Master',
        description: 'Travel 5000 distance in Geometry Dash',
        icon: '🌟',
        category: 'geometry_dash',
        secret: false,
        points: 75
    },
    geometry_portal_master: {
        id: 'geometry_portal_master',
        name: 'Portal Jumper',
        description: 'Pass through 10 portals in one run',
        icon: '🌀',
        category: 'geometry_dash',
        secret: false,
        points: 40
    },
    geometry_hard_2000: {
        id: 'geometry_hard_2000',
        name: 'Dash Demon',
        description: 'Travel 2000 distance on Hard difficulty',
        icon: '😈',
        category: 'geometry_dash',
        secret: false,
        points: 100
    },
    
    // ========== MINESWEEPER ACHIEVEMENTS ==========
    minesweeper_first_win: {
        id: 'minesweeper_first_win',
        name: 'Mine Finder',
        description: 'Win your first Minesweeper game',
        icon: '💣',
        category: 'minesweeper',
        secret: false,
        points: 15
    },
    minesweeper_speed_easy: {
        id: 'minesweeper_speed_easy',
        name: 'Quick Sweep',
        description: 'Win Easy Minesweeper in under 60 seconds',
        icon: '⏱️',
        category: 'minesweeper',
        secret: false,
        points: 30
    },
    minesweeper_speed_medium: {
        id: 'minesweeper_speed_medium',
        name: 'Swift Sweeper',
        description: 'Win Medium Minesweeper in under 120 seconds',
        icon: '⚡',
        category: 'minesweeper',
        secret: false,
        points: 50
    },
    minesweeper_hard_win: {
        id: 'minesweeper_hard_win',
        name: 'Bomb Disposal Expert',
        description: 'Win a Hard Minesweeper game',
        icon: '🎖️',
        category: 'minesweeper',
        secret: false,
        points: 75
    },
    minesweeper_no_flags: {
        id: 'minesweeper_no_flags',
        name: 'Flagless Victory',
        description: 'Win without using any flags',
        icon: '🏳️',
        category: 'minesweeper',
        secret: true,
        points: 50
    },
    
    // ========== SPACE SHOOTERS ACHIEVEMENTS ==========
    space_first_wave: {
        id: 'space_first_wave',
        name: 'Space Cadet',
        description: 'Clear your first wave in Space Shooters',
        icon: '🚀',
        category: 'space_shooters',
        secret: false,
        points: 10
    },
    space_wave_10: {
        id: 'space_wave_10',
        name: 'Wing Commander',
        description: 'Reach wave 10 in Space Shooters',
        icon: '🛸',
        category: 'space_shooters',
        secret: false,
        points: 40
    },
    space_wave_20: {
        id: 'space_wave_20',
        name: 'Star Admiral',
        description: 'Reach wave 20 in Space Shooters',
        icon: '⭐',
        category: 'space_shooters',
        secret: false,
        points: 75
    },
    space_powerup_collect: {
        id: 'space_powerup_collect',
        name: 'Power Collector',
        description: 'Collect 20 power-ups in one game',
        icon: '🔮',
        category: 'space_shooters',
        secret: false,
        points: 30
    },
    space_no_damage: {
        id: 'space_no_damage',
        name: 'Untouchable',
        description: 'Clear 3 waves without taking damage',
        icon: '💫',
        category: 'space_shooters',
        secret: false,
        points: 50
    },
    space_hard_10: {
        id: 'space_hard_10',
        name: 'Ace Pilot',
        description: 'Reach wave 10 on Hard difficulty',
        icon: '🎖️',
        category: 'space_shooters',
        secret: false,
        points: 100
    },
    
    // ========== TETRIS ACHIEVEMENTS ==========
    tetris_first_clear: {
        id: 'tetris_first_clear',
        name: 'Line Clearer',
        description: 'Clear your first line in Tetris',
        icon: '🧩',
        category: 'tetris',
        secret: false,
        points: 5
    },
    tetris_tetris: {
        id: 'tetris_tetris',
        name: 'TETRIS!',
        description: 'Clear 4 lines at once',
        icon: '4️⃣',
        category: 'tetris',
        secret: false,
        points: 25
    },
    tetris_1000: {
        id: 'tetris_1000',
        name: 'Block Stacker',
        description: 'Score 1000 points in Tetris',
        icon: '📦',
        category: 'tetris',
        secret: false,
        points: 20
    },
    tetris_5000: {
        id: 'tetris_5000',
        name: 'Tetris Master',
        description: 'Score 5000 points in Tetris',
        icon: '🏆',
        category: 'tetris',
        secret: false,
        points: 50
    },
    tetris_back_to_back: {
        id: 'tetris_back_to_back',
        name: 'Back to Back',
        description: 'Clear two Tetrises in a row',
        icon: '🔁',
        category: 'tetris',
        secret: false,
        points: 40
    },
    tetris_level_10: {
        id: 'tetris_level_10',
        name: 'Speed Demon',
        description: 'Reach level 10 in Tetris',
        icon: '🚄',
        category: 'tetris',
        secret: false,
        points: 75
    },
    tetris_hard_2000: {
        id: 'tetris_hard_2000',
        name: 'Tetris Virtuoso',
        description: 'Score 2000 points on Hard difficulty',
        icon: '🎹',
        category: 'tetris',
        secret: false,
        points: 100
    },
    
    // ========== FLAPPY BIRD ACHIEVEMENTS ==========
    flappy_first_pipe: {
        id: 'flappy_first_pipe',
        name: 'First Flight',
        description: 'Pass through your first pipe',
        icon: '🐦',
        category: 'flappy',
        secret: false,
        points: 10
    },
    flappy_10_pipes: {
        id: 'flappy_10_pipes',
        name: 'Bird Brain',
        description: 'Pass through 10 pipes',
        icon: '🪶',
        category: 'flappy',
        secret: false,
        points: 25
    },
    flappy_25_pipes: {
        id: 'flappy_25_pipes',
        name: 'Sky High',
        description: 'Pass through 25 pipes',
        icon: '☁️',
        category: 'flappy',
        secret: false,
        points: 50
    },
    flappy_50_pipes: {
        id: 'flappy_50_pipes',
        name: 'Flappy Legend',
        description: 'Pass through 50 pipes',
        icon: '🦅',
        category: 'flappy',
        secret: false,
        points: 100
    },
    
    // ========== PAC-MAN ACHIEVEMENTS ==========
    pacman_first_ghost: {
        id: 'pacman_first_ghost',
        name: 'Ghost Hunter',
        description: 'Eat your first ghost',
        icon: '👻',
        category: 'pacman',
        secret: false,
        points: 10
    },
    pacman_clear_level: {
        id: 'pacman_clear_level',
        name: 'Pellet Muncher',
        description: 'Clear your first level',
        icon: '🟡',
        category: 'pacman',
        secret: false,
        points: 20
    },
    pacman_4_ghosts: {
        id: 'pacman_4_ghosts',
        name: 'Ghost Combo',
        description: 'Eat all 4 ghosts in one power pellet',
        icon: '💀',
        category: 'pacman',
        secret: false,
        points: 50
    },
    pacman_level_5: {
        id: 'pacman_level_5',
        name: 'Pac-Master',
        description: 'Reach level 5',
        icon: '⭐',
        category: 'pacman',
        secret: false,
        points: 75
    },
    
    // ========== ASTEROIDS ACHIEVEMENTS ==========
    asteroids_first_destroy: {
        id: 'asteroids_first_destroy',
        name: 'Space Shooter',
        description: 'Destroy your first asteroid',
        icon: '☄️',
        category: 'asteroids',
        secret: false,
        points: 10
    },
    asteroids_1000: {
        id: 'asteroids_1000',
        name: 'Asteroid Miner',
        description: 'Score 1000 points in Asteroids',
        icon: '💎',
        category: 'asteroids',
        secret: false,
        points: 25
    },
    asteroids_5000: {
        id: 'asteroids_5000',
        name: 'Space Ace',
        description: 'Score 5000 points in Asteroids',
        icon: '🌟',
        category: 'asteroids',
        secret: false,
        points: 75
    },
    asteroids_hyperspace: {
        id: 'asteroids_hyperspace',
        name: 'Lucky Jump',
        description: 'Use hyperspace and survive',
        icon: '🌀',
        category: 'asteroids',
        secret: false,
        points: 15
    },
    
    // ========== SECRET/SPECIAL ACHIEVEMENTS ==========
    theme_changer: {
        id: 'theme_changer',
        name: 'Fashion Forward',
        description: 'Try all available themes',
        icon: '🎨',
        category: 'special',
        secret: true,
        points: 25
    },
    marathon_session: {
        id: 'marathon_session',
        name: 'Marathon Gamer',
        description: 'Play for 30 minutes straight',
        icon: '⏳',
        category: 'special',
        secret: true,
        points: 50
    },
    sound_master: {
        id: 'sound_master',
        name: 'Sound Master',
        description: 'Toggle sound 10 times in one session',
        icon: '🔊',
        category: 'special',
        secret: true,
        points: 10
    },
    perfectionist: {
        id: 'perfectionist',
        name: 'Perfectionist',
        description: 'Get a new high score in 5 different games',
        icon: '💯',
        category: 'special',
        secret: false,
        points: 100
    }
};

// Category metadata
const CATEGORIES = {
    general: { name: 'General', icon: '🎮', order: 0 },
    snake: { name: 'Snake', icon: '🐍', order: 1 },
    pong: { name: 'Pong', icon: '🎾', order: 2 },
    breakout: { name: 'Breakout', icon: '🧱', order: 3 },
    geometry_dash: { name: 'Geometry Dash', icon: '⬜', order: 4 },
    minesweeper: { name: 'Minesweeper', icon: '💣', order: 5 },
    space_shooters: { name: 'Space Shooters', icon: '🚀', order: 6 },
    tetris: { name: 'Tetris', icon: '🧩', order: 7 },
    flappy: { name: 'Flappy Bird', icon: '🐦', order: 8 },
    pacman: { name: 'Pac-Man', icon: '👻', order: 9 },
    asteroids: { name: 'Asteroids', icon: '☄️', order: 10 },
    special: { name: 'Special', icon: '✨', order: 99 }
};

// ============================================================================
// ACHIEVEMENT MANAGER
// ============================================================================

const AchievementManager = {
    STORAGE_KEY: 'vanilla-achievements',
    STATS_KEY: 'vanilla-achievement-stats',
    unlocked: new Set(),
    stats: {},
    notificationQueue: [],
    isShowingNotification: false,
    
    /**
     * Initialize the achievement system
     */
    init() {
        this.load();
        this.injectStyles();
        this.createAchievementButton();
        
        // Check time-based achievements
        this.checkTimeAchievements();
        
        // Track session start for marathon achievement
        this.sessionStart = Date.now();
        setInterval(() => this.checkMarathon(), 60000); // Check every minute
    },
    
    /**
     * Load unlocked achievements from localStorage
     */
    load() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (saved) {
                const arr = JSON.parse(saved);
                this.unlocked = new Set(arr);
            }
            
            const stats = localStorage.getItem(this.STATS_KEY);
            if (stats) {
                this.stats = JSON.parse(stats);
            }
        } catch (e) {
            console.warn('Failed to load achievements:', e);
        }
        
        // Initialize stats
        this.stats.gamesPlayed = this.stats.gamesPlayed || 0;
        this.stats.gamesPlayedByType = this.stats.gamesPlayedByType || {};
        this.stats.highScoreGames = this.stats.highScoreGames || new Set();
        this.stats.difficultiesPlayed = this.stats.difficultiesPlayed || new Set();
        this.stats.themesUsed = this.stats.themesUsed || new Set();
        this.stats.soundToggles = this.stats.soundToggles || 0;
        
        // Convert arrays back to Sets if needed
        if (Array.isArray(this.stats.highScoreGames)) {
            this.stats.highScoreGames = new Set(this.stats.highScoreGames);
        }
        if (Array.isArray(this.stats.difficultiesPlayed)) {
            this.stats.difficultiesPlayed = new Set(this.stats.difficultiesPlayed);
        }
        if (Array.isArray(this.stats.themesUsed)) {
            this.stats.themesUsed = new Set(this.stats.themesUsed);
        }
    },
    
    /**
     * Save achievements to localStorage
     */
    save() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify([...this.unlocked]));
            
            // Convert Sets to arrays for JSON
            const statsToSave = {
                ...this.stats,
                highScoreGames: [...(this.stats.highScoreGames || [])],
                difficultiesPlayed: [...(this.stats.difficultiesPlayed || [])],
                themesUsed: [...(this.stats.themesUsed || [])]
            };
            localStorage.setItem(this.STATS_KEY, JSON.stringify(statsToSave));
        } catch (e) {
            console.warn('Failed to save achievements:', e);
        }
    },
    
    /**
     * Unlock an achievement
     * @param {string} id - Achievement ID
     * @returns {boolean} Whether the achievement was newly unlocked
     */
    unlock(id) {
        if (!ACHIEVEMENTS[id]) {
            console.warn(`Unknown achievement: ${id}`);
            return false;
        }
        
        if (this.unlocked.has(id)) {
            return false; // Already unlocked
        }
        
        this.unlocked.add(id);
        this.save();
        this.showNotification(ACHIEVEMENTS[id]);
        
        // Play sound if available
        if (window.soundEngine && typeof window.soundEngine.play === 'function') {
            window.soundEngine.play('achievement');
        }
        
        return true;
    },
    
    /**
     * Check if an achievement is unlocked
     * @param {string} id - Achievement ID
     * @returns {boolean}
     */
    isUnlocked(id) {
        return this.unlocked.has(id);
    },
    
    /**
     * Track game played
     * @param {string} game - Game identifier
     * @param {string} difficulty - Difficulty level
     */
    trackGamePlayed(game, difficulty = 'medium') {
        this.stats.gamesPlayed = (this.stats.gamesPlayed || 0) + 1;
        this.stats.gamesPlayedByType = this.stats.gamesPlayedByType || {};
        this.stats.gamesPlayedByType[game] = (this.stats.gamesPlayedByType[game] || 0) + 1;
        
        this.stats.difficultiesPlayed = this.stats.difficultiesPlayed || new Set();
        this.stats.difficultiesPlayed.add(difficulty);
        
        this.save();
        
        // Check general achievements
        if (this.stats.gamesPlayed >= 1) this.unlock('first_game');
        if (this.stats.gamesPlayed >= 5) this.unlock('five_games');
        if (this.stats.gamesPlayed >= 20) this.unlock('twenty_games');
        if (this.stats.gamesPlayed >= 100) this.unlock('hundred_games');
        
        // Check if all games played
        const allGames = ['snake', 'pong', 'breakout', 'geometry_dash', 'minesweeper', 'space_shooters', 'tetris', 'flappy', 'pacman', 'asteroids'];
        const playedGames = Object.keys(this.stats.gamesPlayedByType || {});
        if (allGames.every(g => playedGames.includes(g))) {
            this.unlock('all_games_played');
        }
        
        // Check difficulties
        if (this.stats.difficultiesPlayed && this.stats.difficultiesPlayed.size >= 3) {
            this.unlock('all_difficulties');
        }
    },
    
    /**
     * Track high score
     * @param {string} game - Game identifier
     */
    trackHighScore(game) {
        this.stats.highScoreGames = this.stats.highScoreGames || new Set();
        this.stats.highScoreGames.add(game);
        this.save();
        
        if (this.stats.highScoreGames.size >= 5) {
            this.unlock('perfectionist');
        }
    },
    
    /**
     * Track theme change
     * @param {string} theme - Theme ID
     */
    trackTheme(theme) {
        this.stats.themesUsed = this.stats.themesUsed || new Set();
        this.stats.themesUsed.add(theme);
        this.save();
        
        // Check if all themes used (assuming 7 themes)
        if (this.stats.themesUsed.size >= 7) {
            this.unlock('theme_changer');
        }
    },
    
    /**
     * Track sound toggle
     */
    trackSoundToggle() {
        this.stats.soundToggles = (this.stats.soundToggles || 0) + 1;
        this.save();
        
        if (this.stats.soundToggles >= 10) {
            this.unlock('sound_master');
        }
    },
    
    /**
     * Check time-based achievements
     */
    checkTimeAchievements() {
        const hour = new Date().getHours();
        if (hour >= 0 && hour < 6) {
            this.unlock('night_owl');
            if (hour < 6) this.unlock('early_bird');
        }
    },
    
    /**
     * Check marathon achievement
     */
    checkMarathon() {
        const elapsed = Date.now() - this.sessionStart;
        if (elapsed >= 30 * 60 * 1000) { // 30 minutes
            this.unlock('marathon_session');
        }
    },
    
    /**
     * Show notification for unlocked achievement
     * @param {Object} achievement - Achievement object
     */
    showNotification(achievement) {
        this.notificationQueue.push(achievement);
        if (!this.isShowingNotification) {
            this.processNotificationQueue();
        }
    },
    
    /**
     * Process notification queue
     */
    processNotificationQueue() {
        if (this.notificationQueue.length === 0) {
            this.isShowingNotification = false;
            return;
        }
        
        this.isShowingNotification = true;
        const achievement = this.notificationQueue.shift();
        
        // Create notification element
        const notif = document.createElement('div');
        notif.className = 'achievement-notification';
        notif.innerHTML = `
            <div class="achievement-notif-icon">${achievement.icon}</div>
            <div class="achievement-notif-content">
                <div class="achievement-notif-title">Achievement Unlocked!</div>
                <div class="achievement-notif-name">${achievement.name}</div>
                <div class="achievement-notif-desc">${achievement.description}</div>
            </div>
            <div class="achievement-notif-points">+${achievement.points}</div>
        `;
        
        document.body.appendChild(notif);
        
        // Trigger animation
        requestAnimationFrame(() => {
            notif.classList.add('show');
        });
        
        // Remove after delay
        setTimeout(() => {
            notif.classList.remove('show');
            setTimeout(() => {
                notif.remove();
                this.processNotificationQueue();
            }, 300);
        }, 4000);
    },
    
    /**
     * Get all achievements grouped by category
     * @returns {Object}
     */
    getByCategory() {
        const grouped = {};
        
        for (const [id, achievement] of Object.entries(ACHIEVEMENTS)) {
            const cat = achievement.category;
            if (!grouped[cat]) {
                grouped[cat] = [];
            }
            grouped[cat].push({
                ...achievement,
                unlocked: this.unlocked.has(id)
            });
        }
        
        return grouped;
    },
    
    /**
     * Get progress stats
     * @returns {Object}
     */
    getProgress() {
        const total = Object.keys(ACHIEVEMENTS).length;
        const unlocked = this.unlocked.size;
        const totalPoints = Object.values(ACHIEVEMENTS).reduce((sum, a) => sum + a.points, 0);
        const earnedPoints = [...this.unlocked]
            .filter(id => ACHIEVEMENTS[id])
            .reduce((sum, id) => sum + ACHIEVEMENTS[id].points, 0);
        
        return {
            total,
            unlocked,
            percentage: Math.round((unlocked / total) * 100),
            totalPoints,
            earnedPoints
        };
    },
    
    /**
     * Inject CSS styles
     */
    injectStyles() {
        if (document.getElementById('achievement-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'achievement-styles';
        style.textContent = `
            /* Achievement Notification */
            .achievement-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.95), rgba(118, 75, 162, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 16px;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
                z-index: 10001;
                transform: translateX(120%);
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                max-width: 380px;
            }
            
            .achievement-notification.show {
                transform: translateX(0);
            }
            
            .achievement-notif-icon {
                font-size: 40px;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
            }
            
            .achievement-notif-content {
                flex: 1;
            }
            
            .achievement-notif-title {
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: rgba(255, 255, 255, 0.8);
                margin-bottom: 4px;
            }
            
            .achievement-notif-name {
                font-size: 16px;
                font-weight: 700;
                color: #fff;
                margin-bottom: 2px;
            }
            
            .achievement-notif-desc {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7);
            }
            
            .achievement-notif-points {
                font-family: 'Press Start 2P', monospace;
                font-size: 14px;
                color: #fcd34d;
                text-shadow: 0 0 10px rgba(252, 211, 77, 0.5);
            }
            
            /* Achievement Button */
            .achievement-btn {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-right: 8px;
                position: relative;
            }
            
            .achievement-btn:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: scale(1.05);
            }
            
            .achievement-btn-badge {
                position: absolute;
                top: -6px;
                right: -6px;
                background: var(--color-primary, #667eea);
                color: #fff;
                font-size: 10px;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 10px;
                min-width: 18px;
                text-align: center;
            }
            
            /* Achievement Modal */
            .achievement-modal-overlay {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.85);
                backdrop-filter: blur(8px);
                display: flex;
                justify-content: center;
                align-items: flex-start;
                padding: 40px 20px;
                z-index: 10000;
                overflow-y: auto;
                animation: fadeIn 0.2s ease;
            }
            
            .achievement-modal {
                background: var(--bg-dark, #0a0e27);
                border: 1px solid var(--border-light, rgba(255,255,255,0.12));
                border-radius: 20px;
                max-width: 800px;
                width: 100%;
                animation: slideUp 0.3s ease;
            }
            
            .achievement-modal-header {
                padding: 24px;
                border-bottom: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
            }
            
            .achievement-modal-header h2 {
                font-family: 'Poppins', sans-serif;
                font-size: 24px;
                font-weight: 700;
                color: var(--text-light, #f2f4ff);
                margin: 0 0 8px;
            }
            
            .achievement-progress {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-top: 16px;
            }
            
            .achievement-progress-bar {
                flex: 1;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                overflow: hidden;
            }
            
            .achievement-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--color-primary, #667eea), var(--color-secondary, #764ba2));
                border-radius: 4px;
                transition: width 0.5s ease;
            }
            
            .achievement-progress-text {
                font-size: 14px;
                color: var(--text-secondary, #b0b0b0);
                white-space: nowrap;
            }
            
            .achievement-points-display {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 12px 16px;
                background: rgba(252, 211, 77, 0.1);
                border: 1px solid rgba(252, 211, 77, 0.3);
                border-radius: 12px;
                margin-top: 16px;
            }
            
            .achievement-points-display span {
                font-family: 'Press Start 2P', monospace;
                font-size: 16px;
                color: #fcd34d;
            }
            
            .achievement-modal-body {
                padding: 24px;
                max-height: 60vh;
                overflow-y: auto;
            }
            
            .achievement-category {
                margin-bottom: 24px;
            }
            
            .achievement-category:last-child {
                margin-bottom: 0;
            }
            
            .achievement-category-title {
                font-size: 14px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: var(--text-secondary, #b0b0b0);
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .achievement-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 12px;
            }
            
            .achievement-card {
                background: var(--glass-bg, rgba(255,255,255,0.03));
                border: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
                border-radius: 12px;
                padding: 16px;
                transition: all 0.2s ease;
            }
            
            .achievement-card:hover {
                background: var(--glass-bg-hover, rgba(255,255,255,0.05));
                border-color: var(--border-primary, rgba(102,126,234,0.3));
            }
            
            .achievement-card.locked {
                opacity: 0.5;
            }
            
            .achievement-card.secret.locked {
                filter: blur(2px);
            }
            
            .achievement-card-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 8px;
            }
            
            .achievement-card-icon {
                font-size: 28px;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(255,255,255,0.05);
                border-radius: 10px;
            }
            
            .achievement-card.locked .achievement-card-icon {
                filter: grayscale(1);
            }
            
            .achievement-card-name {
                font-weight: 700;
                font-size: 14px;
                color: var(--text-light, #f2f4ff);
            }
            
            .achievement-card-desc {
                font-size: 12px;
                color: var(--text-muted, #808080);
                line-height: 1.4;
            }
            
            .achievement-card.secret.locked .achievement-card-name,
            .achievement-card.secret.locked .achievement-card-desc {
                color: transparent;
                text-shadow: 0 0 8px var(--text-muted, #808080);
            }
            
            .achievement-card-points {
                display: inline-block;
                margin-top: 8px;
                font-size: 11px;
                font-weight: 700;
                color: #fcd34d;
                padding: 4px 8px;
                background: rgba(252, 211, 77, 0.1);
                border-radius: 6px;
            }
            
            .achievement-modal-footer {
                padding: 16px 24px;
                border-top: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
                display: flex;
                justify-content: flex-end;
            }
            
            .achievement-modal-close {
                padding: 12px 24px;
                background: var(--glass-bg, rgba(255,255,255,0.03));
                border: 1px solid var(--border-light, rgba(255,255,255,0.12));
                border-radius: 8px;
                color: var(--text-primary, #e0e0e0);
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .achievement-modal-close:hover {
                background: var(--glass-bg-hover, rgba(255,255,255,0.05));
            }
        `;
        document.head.appendChild(style);
    },
    
    /**
     * Create achievement button in header
     */
    createAchievementButton() {
        const header = document.querySelector('header');
        if (!header || document.getElementById('achievementBtn')) return;
        
        const progress = this.getProgress();
        
        const btn = document.createElement('button');
        btn.id = 'achievementBtn';
        btn.className = 'achievement-btn';
        btn.title = 'Achievements';
        btn.innerHTML = `🏆`;
        
        if (progress.unlocked > 0) {
            const badge = document.createElement('span');
            badge.className = 'achievement-btn-badge';
            badge.textContent = progress.unlocked;
            btn.appendChild(badge);
        }
        
        btn.onclick = () => this.showModal();
        
        // Insert near theme button
        const themeBtn = document.getElementById('themeBtn');
        if (themeBtn) {
            themeBtn.parentNode.insertBefore(btn, themeBtn);
        } else {
            const headerActions = header.querySelector('.header-actions');
            if (headerActions) {
                headerActions.insertBefore(btn, headerActions.firstChild);
            } else {
                header.appendChild(btn);
            }
        }
    },
    
    /**
     * Show achievements modal
     */
    showModal() {
        // Remove existing
        const existing = document.getElementById('achievementModal');
        if (existing) existing.remove();
        
        const progress = this.getProgress();
        const byCategory = this.getByCategory();
        
        const overlay = document.createElement('div');
        overlay.id = 'achievementModal';
        overlay.className = 'achievement-modal-overlay';
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.remove();
        };
        
        let html = `
            <div class="achievement-modal">
                <div class="achievement-modal-header">
                    <h2>🏆 Achievements</h2>
                    <div class="achievement-progress">
                        <div class="achievement-progress-bar">
                            <div class="achievement-progress-fill" style="width: ${progress.percentage}%"></div>
                        </div>
                        <div class="achievement-progress-text">${progress.unlocked} / ${progress.total}</div>
                    </div>
                    <div class="achievement-points-display">
                        <span>⭐ ${progress.earnedPoints} / ${progress.totalPoints}</span>
                        <span style="font-family: Poppins; font-size: 12px; color: var(--text-muted);">points earned</span>
                    </div>
                </div>
                <div class="achievement-modal-body">
        `;
        
        // Sort categories
        const sortedCategories = Object.entries(byCategory).sort((a, b) => {
            const orderA = CATEGORIES[a[0]]?.order ?? 50;
            const orderB = CATEGORIES[b[0]]?.order ?? 50;
            return orderA - orderB;
        });
        
        for (const [catId, achievements] of sortedCategories) {
            const cat = CATEGORIES[catId] || { name: catId, icon: '📁' };
            const unlockedInCat = achievements.filter(a => a.unlocked).length;
            
            html += `
                <div class="achievement-category">
                    <div class="achievement-category-title">
                        ${cat.icon} ${cat.name}
                        <span style="font-weight: 400; color: var(--text-muted)">(${unlockedInCat}/${achievements.length})</span>
                    </div>
                    <div class="achievement-grid">
            `;
            
            for (const ach of achievements) {
                const lockedClass = ach.unlocked ? '' : 'locked';
                const secretClass = ach.secret ? 'secret' : '';
                
                html += `
                    <div class="achievement-card ${lockedClass} ${secretClass}">
                        <div class="achievement-card-header">
                            <div class="achievement-card-icon">${ach.unlocked || !ach.secret ? ach.icon : '❓'}</div>
                            <div class="achievement-card-name">${ach.unlocked || !ach.secret ? ach.name : '???'}</div>
                        </div>
                        <div class="achievement-card-desc">${ach.unlocked || !ach.secret ? ach.description : 'Secret achievement'}</div>
                        <div class="achievement-card-points">${ach.unlocked ? '✓' : ''} ${ach.points} pts</div>
                    </div>
                `;
            }
            
            html += `
                    </div>
                </div>
            `;
        }
        
        html += `
                </div>
                <div class="achievement-modal-footer">
                    <button class="achievement-modal-close">Close</button>
                </div>
            </div>
        `;
        
        overlay.innerHTML = html;
        document.body.appendChild(overlay);
        
        overlay.querySelector('.achievement-modal-close').onclick = () => overlay.remove();
        
        // Close on Escape
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }
};

// ============================================================================
// AUTO-INITIALIZE
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AchievementManager.init());
} else {
    AchievementManager.init();
}

// Listen for theme changes to track
document.addEventListener('themechange', (e) => {
    if (e.detail && e.detail.theme) {
        AchievementManager.trackTheme(e.detail.theme);
    }
});

// Export for use in games
window.VanillaAchievements = AchievementManager;
window.VANILLA_ACHIEVEMENTS = ACHIEVEMENTS;
