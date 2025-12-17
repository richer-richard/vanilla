/**
 * VANILLA Game Engine
 * 
 * A shared game engine module providing common functionality for all games
 * in the Vanilla Collection. Includes fixed-step game loop, state management,
 * input handling, canvas utilities, and more.
 * 
 * @module engine
 * @version 1.0.0
 */

// ============================================================================
// GAME ENGINE CORE
// ============================================================================

/**
 * Creates a new game engine instance
 * @param {Object} config - Engine configuration
 * @param {HTMLCanvasElement} config.canvas - The canvas element
 * @param {number} [config.targetFPS=120] - Target simulation FPS
 * @param {number} [config.maxFrameMs=50] - Maximum frame time to prevent spiral of death
 * @param {Function} [config.onUpdate] - Called each simulation tick with delta time
 * @param {Function} [config.onRender] - Called each frame for rendering
 * @param {Function} [config.onStateChange] - Called when game state changes
 * @param {Function} [config.onResize] - Called when canvas is resized
 * @returns {Object} Game engine instance
 */
function createGameEngine(config) {
    const {
        canvas,
        targetFPS = 120,
        maxFrameMs = 50,
        onUpdate = () => {},
        onRender = () => {},
        onStateChange = () => {},
        onResize = () => {}
    } = config;

    // Constants
    const STEP_MS = 1000 / targetFPS;
    const MAX_STEPS_PER_FRAME = Math.ceil(maxFrameMs / STEP_MS);
    const BASE_FPS = 60;
    const FRAME_SCALE = targetFPS / BASE_FPS;
    const TICK_SCALE = BASE_FPS / targetFPS;

    // State
    let state = 'ready'; // ready | running | paused | over
    let lastTime = 0;
    let accumulator = 0;
    let rafId = null;
    let width = canvas.width;
    let height = canvas.height;

    // Context
    const ctx = canvas.getContext('2d', { alpha: false, desynchronized: true });

    /**
     * Main game loop
     * @private
     * @param {number} now - Current timestamp
     */
    function loop(now) {
        rafId = requestAnimationFrame(loop);
        
        if (!lastTime) lastTime = now;
        const frameDelta = Math.min(maxFrameMs, now - lastTime);
        lastTime = now;
        accumulator += frameDelta;

        let steps = 0;
        while (accumulator >= STEP_MS && steps < MAX_STEPS_PER_FRAME) {
            if (state === 'running') {
                onUpdate(TICK_SCALE, STEP_MS / 1000);
            }
            accumulator -= STEP_MS;
            steps += 1;
        }
        
        if (steps === MAX_STEPS_PER_FRAME) {
            accumulator = 0; // Prevent spiral of death
        }

        onRender(ctx, width, height);
    }

    /**
     * Resize the canvas to fit its container
     * @param {Object} [options] - Resize options
     * @param {number} [options.maxWidth] - Maximum canvas width
     * @param {number} [options.maxHeight] - Maximum canvas height
     * @param {number} [options.aspectRatio] - Desired aspect ratio (width/height)
     */
    function resize(options = {}) {
        const container = canvas.parentElement;
        const { maxWidth = 940, maxHeight = 800, aspectRatio = 4/3 } = options;
        
        width = Math.min(maxWidth, container.clientWidth);
        height = Math.round(width / aspectRatio);
        
        if (height > maxHeight) {
            height = maxHeight;
            width = Math.round(height * aspectRatio);
        }
        
        canvas.width = width;
        canvas.height = height;
        
        onResize(width, height);
    }

    /**
     * Set the game state
     * @param {string} newState - New state ('ready', 'running', 'paused', 'over')
     */
    function setState(newState) {
        const validStates = ['ready', 'running', 'paused', 'over'];
        if (validStates.includes(newState) && newState !== state) {
            const oldState = state;
            state = newState;
            onStateChange(newState, oldState);
        }
    }

    /**
     * Get the current game state
     * @returns {string} Current state
     */
    function getState() {
        return state;
    }

    /**
     * Start the game loop
     */
    function start() {
        if (!rafId) {
            lastTime = 0;
            accumulator = 0;
            rafId = requestAnimationFrame(loop);
        }
    }

    /**
     * Stop the game loop
     */
    function stop() {
        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    }

    /**
     * Toggle pause state
     */
    function togglePause() {
        if (state === 'running') {
            setState('paused');
        } else if (state === 'paused') {
            setState('running');
        }
    }

    // Public API
    return {
        // Core
        start,
        stop,
        resize,
        setState,
        getState,
        togglePause,
        
        // Getters
        get ctx() { return ctx; },
        get width() { return width; },
        get height() { return height; },
        get canvas() { return canvas; },
        
        // Constants (for external use)
        FRAME_SCALE,
        TICK_SCALE,
        BASE_FPS,
        TARGET_FPS: targetFPS
    };
}


// ============================================================================
// INPUT MANAGER
// ============================================================================

/**
 * Creates an input manager for handling keyboard and touch input
 * @param {Object} [options] - Input manager options
 * @param {boolean} [options.preventDefaults=true] - Prevent default browser behavior for game keys
 * @param {string[]} [options.gameKeys] - Keys to prevent default on
 * @returns {Object} Input manager instance
 */
function createInputManager(options = {}) {
    const {
        preventDefaults = true,
        gameKeys = ['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' ', 'w', 'a', 's', 'd']
    } = options;

    const keys = {};
    const keyCallbacks = {};
    const touchState = {
        active: false,
        startX: 0,
        startY: 0,
        currentX: 0,
        currentY: 0,
        deltaX: 0,
        deltaY: 0
    };

    /**
     * Handle keydown events
     * @private
     */
    function handleKeyDown(e) {
        const key = e.key.toLowerCase();
        keys[key] = true;
        
        if (preventDefaults && (gameKeys.includes(key) || e.key === ' ')) {
            e.preventDefault();
        }
        
        if (keyCallbacks[key]) {
            keyCallbacks[key].forEach(cb => cb(e));
        }
        if (keyCallbacks['*']) {
            keyCallbacks['*'].forEach(cb => cb(e, key));
        }
    }

    /**
     * Handle keyup events
     * @private
     */
    function handleKeyUp(e) {
        const key = e.key.toLowerCase();
        keys[key] = false;
        
        if (preventDefaults && (gameKeys.includes(key) || e.key === ' ')) {
            e.preventDefault();
        }
    }

    /**
     * Handle touch start
     * @private
     */
    function handleTouchStart(e) {
        if (e.touches.length > 0) {
            const touch = e.touches[0];
            touchState.active = true;
            touchState.startX = touch.clientX;
            touchState.startY = touch.clientY;
            touchState.currentX = touch.clientX;
            touchState.currentY = touch.clientY;
            touchState.deltaX = 0;
            touchState.deltaY = 0;
        }
    }

    /**
     * Handle touch move
     * @private
     */
    function handleTouchMove(e) {
        if (e.touches.length > 0 && touchState.active) {
            const touch = e.touches[0];
            touchState.currentX = touch.clientX;
            touchState.currentY = touch.clientY;
            touchState.deltaX = touchState.currentX - touchState.startX;
            touchState.deltaY = touchState.currentY - touchState.startY;
        }
    }

    /**
     * Handle touch end
     * @private
     */
    function handleTouchEnd() {
        touchState.active = false;
    }

    /**
     * Check if a key is currently pressed
     * @param {string} key - Key to check (lowercase)
     * @returns {boolean} Whether the key is pressed
     */
    function isPressed(key) {
        return !!keys[key.toLowerCase()];
    }

    /**
     * Check if any of the given keys are pressed
     * @param {...string} keyList - Keys to check
     * @returns {boolean} Whether any key is pressed
     */
    function isAnyPressed(...keyList) {
        return keyList.some(k => keys[k.toLowerCase()]);
    }

    /**
     * Register a callback for a key press
     * @param {string} key - Key to listen for (use '*' for all keys)
     * @param {Function} callback - Callback function
     */
    function onKey(key, callback) {
        const normalizedKey = key.toLowerCase();
        if (!keyCallbacks[normalizedKey]) {
            keyCallbacks[normalizedKey] = [];
        }
        keyCallbacks[normalizedKey].push(callback);
    }

    /**
     * Remove a key callback
     * @param {string} key - Key to stop listening for
     * @param {Function} callback - Callback to remove
     */
    function offKey(key, callback) {
        const normalizedKey = key.toLowerCase();
        if (keyCallbacks[normalizedKey]) {
            keyCallbacks[normalizedKey] = keyCallbacks[normalizedKey].filter(cb => cb !== callback);
        }
    }

    /**
     * Get touch state
     * @returns {Object} Current touch state
     */
    function getTouch() {
        return { ...touchState };
    }

    /**
     * Initialize event listeners
     */
    function init() {
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);
        document.addEventListener('touchstart', handleTouchStart, { passive: true });
        document.addEventListener('touchmove', handleTouchMove, { passive: true });
        document.addEventListener('touchend', handleTouchEnd);
    }

    /**
     * Clean up event listeners
     */
    function destroy() {
        document.removeEventListener('keydown', handleKeyDown);
        document.removeEventListener('keyup', handleKeyUp);
        document.removeEventListener('touchstart', handleTouchStart);
        document.removeEventListener('touchmove', handleTouchMove);
        document.removeEventListener('touchend', handleTouchEnd);
    }

    return {
        init,
        destroy,
        isPressed,
        isAnyPressed,
        onKey,
        offKey,
        getTouch,
        get keys() { return { ...keys }; }
    };
}


// ============================================================================
// CANVAS UTILITIES
// ============================================================================

/**
 * Canvas drawing utilities
 */
const CanvasUtils = {
    /**
     * Clear the canvas with a gradient background
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} width - Canvas width
     * @param {number} height - Canvas height
     * @param {Object} [options] - Options
     */
    clearWithGradient(ctx, width, height, options = {}) {
        const { 
            colorTop = '#0c132b', 
            colorBottom = '#0a0f22' 
        } = options;
        
        const bg = ctx.createLinearGradient(0, 0, 0, height);
        bg.addColorStop(0, colorTop);
        bg.addColorStop(1, colorBottom);
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, width, height);
    },

    /**
     * Draw a rounded rectangle
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} x - X position
     * @param {number} y - Y position
     * @param {number} width - Rectangle width
     * @param {number} height - Rectangle height
     * @param {number} radius - Corner radius
     */
    roundRect(ctx, x, y, width, height, radius) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
    },

    /**
     * Draw centered text
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {string} text - Text to draw
     * @param {number} x - Center X position
     * @param {number} y - Y position
     * @param {Object} [options] - Text options
     */
    centeredText(ctx, text, x, y, options = {}) {
        const {
            font = 'bold 28px Poppins',
            color = '#f1f3ff',
            shadow = null
        } = options;
        
        ctx.font = font;
        ctx.textAlign = 'center';
        ctx.fillStyle = color;
        
        if (shadow) {
            ctx.shadowColor = shadow.color || 'rgba(0,0,0,0.5)';
            ctx.shadowBlur = shadow.blur || 10;
            ctx.shadowOffsetX = shadow.offsetX || 0;
            ctx.shadowOffsetY = shadow.offsetY || 2;
        }
        
        ctx.fillText(text, x, y);
        
        if (shadow) {
            ctx.shadowColor = 'transparent';
            ctx.shadowBlur = 0;
            ctx.shadowOffsetX = 0;
            ctx.shadowOffsetY = 0;
        }
    },

    /**
     * Draw a dashed line
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {number} x1 - Start X
     * @param {number} y1 - Start Y
     * @param {number} x2 - End X
     * @param {number} y2 - End Y
     * @param {Object} [options] - Line options
     */
    dashedLine(ctx, x1, y1, x2, y2, options = {}) {
        const {
            dash = [8, 10],
            color = 'rgba(255,255,255,0.18)',
            lineWidth = 2
        } = options;
        
        ctx.setLineDash(dash);
        ctx.strokeStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
        ctx.setLineDash([]);
    },

    /**
     * Draw a trail effect
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Array} trail - Array of {x, y} positions
     * @param {number} radius - Object radius
     * @param {Object} [options] - Trail options
     */
    drawTrail(ctx, trail, radius, options = {}) {
        const {
            color = 'rgba(110, 231, 255, 0.6)',
            radiusMultiplier = 0.8
        } = options;
        
        for (let i = 0; i < trail.length; i++) {
            const t = trail[i];
            const alpha = i / trail.length;
            
            // Parse color and apply alpha
            const baseColor = color.replace(/[\d.]+\)$/, `${alpha * parseFloat(color.match(/[\d.]+\)$/)?.[0] || 0.6)})`);
            
            ctx.fillStyle = baseColor;
            ctx.beginPath();
            ctx.arc(t.x, t.y, radius * radiusMultiplier, 0, Math.PI * 2);
            ctx.fill();
        }
    }
};


// ============================================================================
// COLLISION DETECTION
// ============================================================================

/**
 * Collision detection utilities
 */
const Collision = {
    /**
     * Check AABB (Axis-Aligned Bounding Box) collision
     * @param {Object} a - First rectangle {x, y, width, height}
     * @param {Object} b - Second rectangle {x, y, width, height}
     * @returns {boolean} Whether collision occurred
     */
    rectRect(a, b) {
        return a.x < b.x + b.width &&
               a.x + a.width > b.x &&
               a.y < b.y + b.height &&
               a.y + a.height > b.y;
    },

    /**
     * Check circle-circle collision
     * @param {Object} a - First circle {x, y, r}
     * @param {Object} b - Second circle {x, y, r}
     * @returns {boolean} Whether collision occurred
     */
    circleCircle(a, b) {
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        return dist < a.r + b.r;
    },

    /**
     * Check circle-rectangle collision
     * @param {Object} circle - Circle {x, y, r}
     * @param {Object} rect - Rectangle {x, y, width, height}
     * @returns {boolean} Whether collision occurred
     */
    circleRect(circle, rect) {
        const closestX = Math.max(rect.x, Math.min(circle.x, rect.x + rect.width));
        const closestY = Math.max(rect.y, Math.min(circle.y, rect.y + rect.height));
        const dx = circle.x - closestX;
        const dy = circle.y - closestY;
        return (dx * dx + dy * dy) < (circle.r * circle.r);
    },

    /**
     * Check point-rectangle collision
     * @param {Object} point - Point {x, y}
     * @param {Object} rect - Rectangle {x, y, width, height}
     * @returns {boolean} Whether point is inside rectangle
     */
    pointRect(point, rect) {
        return point.x >= rect.x &&
               point.x <= rect.x + rect.width &&
               point.y >= rect.y &&
               point.y <= rect.y + rect.height;
    },

    /**
     * Check point-circle collision
     * @param {Object} point - Point {x, y}
     * @param {Object} circle - Circle {x, y, r}
     * @returns {boolean} Whether point is inside circle
     */
    pointCircle(point, circle) {
        const dx = point.x - circle.x;
        const dy = point.y - circle.y;
        return (dx * dx + dy * dy) < (circle.r * circle.r);
    }
};


// ============================================================================
// MATH UTILITIES
// ============================================================================

/**
 * Math utilities
 */
const MathUtils = {
    /**
     * Clamp a value between min and max
     * @param {number} value - Value to clamp
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     * @returns {number} Clamped value
     */
    clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    },

    /**
     * Linear interpolation
     * @param {number} a - Start value
     * @param {number} b - End value
     * @param {number} t - Interpolation factor (0-1)
     * @returns {number} Interpolated value
     */
    lerp(a, b, t) {
        return a + (b - a) * t;
    },

    /**
     * Map a value from one range to another
     * @param {number} value - Value to map
     * @param {number} inMin - Input range min
     * @param {number} inMax - Input range max
     * @param {number} outMin - Output range min
     * @param {number} outMax - Output range max
     * @returns {number} Mapped value
     */
    map(value, inMin, inMax, outMin, outMax) {
        return outMin + (outMax - outMin) * ((value - inMin) / (inMax - inMin));
    },

    /**
     * Get random number in range
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     * @returns {number} Random number
     */
    random(min, max) {
        return Math.random() * (max - min) + min;
    },

    /**
     * Get random integer in range (inclusive)
     * @param {number} min - Minimum value
     * @param {number} max - Maximum value
     * @returns {number} Random integer
     */
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    /**
     * Calculate distance between two points
     * @param {number} x1 - First point X
     * @param {number} y1 - First point Y
     * @param {number} x2 - Second point X
     * @param {number} y2 - Second point Y
     * @returns {number} Distance
     */
    distance(x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        return Math.sqrt(dx * dx + dy * dy);
    },

    /**
     * Calculate angle between two points
     * @param {number} x1 - First point X
     * @param {number} y1 - First point Y
     * @param {number} x2 - Second point X
     * @param {number} y2 - Second point Y
     * @returns {number} Angle in radians
     */
    angle(x1, y1, x2, y2) {
        return Math.atan2(y2 - y1, x2 - x1);
    },

    /**
     * Convert degrees to radians
     * @param {number} degrees - Angle in degrees
     * @returns {number} Angle in radians
     */
    degToRad(degrees) {
        return degrees * (Math.PI / 180);
    },

    /**
     * Convert radians to degrees
     * @param {number} radians - Angle in radians
     * @returns {number} Angle in degrees
     */
    radToDeg(radians) {
        return radians * (180 / Math.PI);
    }
};


// ============================================================================
// HUD MANAGER
// ============================================================================

/**
 * Creates a HUD manager for efficient DOM updates
 * @returns {Object} HUD manager instance
 */
function createHudManager() {
    const cache = {};
    const elements = {};

    /**
     * Register an element for HUD updates
     * @param {string} id - Element ID
     * @param {HTMLElement} [element] - Element (will query by ID if not provided)
     */
    function register(id, element = null) {
        elements[id] = element || document.getElementById(id);
        cache[id] = null;
    }

    /**
     * Update an element's text content (with caching)
     * @param {string} id - Element ID
     * @param {string|number} value - New value
     */
    function update(id, value) {
        const stringValue = String(value);
        if (cache[id] !== stringValue && elements[id]) {
            cache[id] = stringValue;
            elements[id].textContent = stringValue;
        }
    }

    /**
     * Batch update multiple elements
     * @param {Object} updates - Object with id: value pairs
     */
    function batchUpdate(updates) {
        for (const [id, value] of Object.entries(updates)) {
            update(id, value);
        }
    }

    /**
     * Force update an element (bypass cache)
     * @param {string} id - Element ID
     * @param {string|number} value - New value
     */
    function forceUpdate(id, value) {
        cache[id] = null;
        update(id, value);
    }

    /**
     * Clear the cache
     */
    function clearCache() {
        for (const key in cache) {
            cache[key] = null;
        }
    }

    return {
        register,
        update,
        batchUpdate,
        forceUpdate,
        clearCache
    };
}


// ============================================================================
// STORAGE UTILITIES
// ============================================================================

/**
 * LocalStorage utilities with error handling
 */
const Storage = {
    /**
     * Get a value from localStorage
     * @param {string} key - Storage key
     * @param {*} [defaultValue=null] - Default value if not found
     * @returns {*} Stored value or default
     */
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item !== null ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn(`Failed to get ${key} from localStorage:`, e);
            return defaultValue;
        }
    },

    /**
     * Set a value in localStorage
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     * @returns {boolean} Success status
     */
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.warn(`Failed to set ${key} in localStorage:`, e);
            return false;
        }
    },

    /**
     * Remove a value from localStorage
     * @param {string} key - Storage key
     */
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn(`Failed to remove ${key} from localStorage:`, e);
        }
    },

    /**
     * Get a high score
     * @param {string} game - Game identifier
     * @param {string} [difficulty='medium'] - Difficulty level
     * @returns {number} High score
     */
    getHighScore(game, difficulty = 'medium') {
        return this.get(`vanilla-${game}-${difficulty}-best`, 0);
    },

    /**
     * Set a high score (only if higher)
     * @param {string} game - Game identifier
     * @param {string} difficulty - Difficulty level
     * @param {number} score - Score to save
     * @returns {boolean} Whether score was a new record
     */
    setHighScore(game, difficulty, score) {
        const key = `vanilla-${game}-${difficulty}-best`;
        const current = this.get(key, 0);
        if (score > current) {
            this.set(key, score);
            return true;
        }
        return false;
    }
};


// ============================================================================
// DIFFICULTY MANAGER
// ============================================================================

/**
 * Creates a difficulty manager
 * @param {Object} configs - Difficulty configurations { easy: {...}, medium: {...}, hard: {...} }
 * @param {string} [defaultDifficulty='medium'] - Default difficulty
 * @returns {Object} Difficulty manager instance
 */
function createDifficultyManager(configs, defaultDifficulty = 'medium') {
    // Get difficulty from URL params
    const params = new URLSearchParams(window.location.search);
    const requestedDifficulty = (params.get('difficulty') || defaultDifficulty).toLowerCase();
    
    // Validate difficulty
    const difficulty = configs[requestedDifficulty] ? requestedDifficulty : defaultDifficulty;
    const config = configs[difficulty];

    return {
        difficulty,
        config,
        configs,
        
        /**
         * Get a config value
         * @param {string} key - Config key
         * @param {*} [defaultValue] - Default if not found
         * @returns {*} Config value
         */
        get(key, defaultValue) {
            return config[key] !== undefined ? config[key] : defaultValue;
        },
        
        /**
         * Get the label for current difficulty
         * @returns {string} Difficulty label
         */
        getLabel() {
            return config.label || difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
        }
    };
}


// ============================================================================
// TOUCH CONTROLS
// ============================================================================

/**
 * Creates touch control buttons for mobile play
 * @param {HTMLElement} container - Container element for touch controls
 * @param {Object} [options] - Options
 * @returns {Object} Touch controls instance
 */
function createTouchControls(container, options = {}) {
    const {
        layout = 'horizontal', // 'horizontal', 'vertical', 'dpad'
        buttons = ['left', 'right'],
        onPress = () => {},
        onRelease = () => {}
    } = options;

    const controlsEl = document.createElement('div');
    controlsEl.className = 'touch-controls';
    controlsEl.setAttribute('data-layout', layout);
    
    const buttonEls = {};
    const activeButtons = new Set();

    // Button icons/labels
    const buttonConfig = {
        left: { icon: '←', label: 'Left' },
        right: { icon: '→', label: 'Right' },
        up: { icon: '↑', label: 'Up' },
        down: { icon: '↓', label: 'Down' },
        action: { icon: '●', label: 'Action' },
        jump: { icon: '↥', label: 'Jump' },
        pause: { icon: '⏸', label: 'Pause' }
    };

    // Create buttons
    buttons.forEach(btn => {
        const config = buttonConfig[btn] || { icon: btn, label: btn };
        const el = document.createElement('button');
        el.className = `touch-btn touch-btn-${btn}`;
        el.innerHTML = config.icon;
        el.setAttribute('data-action', btn);
        el.setAttribute('aria-label', config.label);
        
        buttonEls[btn] = el;
        controlsEl.appendChild(el);
    });

    // Handle touch events
    function handleTouchStart(e) {
        const btn = e.target.getAttribute('data-action');
        if (btn && !activeButtons.has(btn)) {
            activeButtons.add(btn);
            e.target.classList.add('active');
            onPress(btn);
        }
        e.preventDefault();
    }

    function handleTouchEnd(e) {
        const btn = e.target.getAttribute('data-action');
        if (btn && activeButtons.has(btn)) {
            activeButtons.delete(btn);
            e.target.classList.remove('active');
            onRelease(btn);
        }
        e.preventDefault();
    }

    // Attach events
    controlsEl.addEventListener('touchstart', handleTouchStart, { passive: false });
    controlsEl.addEventListener('touchend', handleTouchEnd, { passive: false });
    controlsEl.addEventListener('touchcancel', handleTouchEnd, { passive: false });

    // Prevent context menu on long press
    controlsEl.addEventListener('contextmenu', e => e.preventDefault());

    // Add to container
    container.appendChild(controlsEl);

    // Add styles if not present
    if (!document.getElementById('touch-controls-styles')) {
        const style = document.createElement('style');
        style.id = 'touch-controls-styles';
        style.textContent = `
            .touch-controls {
                display: none;
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 100;
                gap: 12px;
                user-select: none;
                -webkit-user-select: none;
            }
            
            @media (pointer: coarse) {
                .touch-controls {
                    display: flex;
                }
            }
            
            .touch-controls[data-layout="vertical"] {
                flex-direction: column;
            }
            
            .touch-controls[data-layout="dpad"] {
                display: grid;
                grid-template-areas: 
                    ". up ."
                    "left . right"
                    ". down .";
                gap: 8px;
            }
            
            .touch-btn {
                width: 64px;
                height: 64px;
                border-radius: 50%;
                border: 2px solid rgba(102, 126, 234, 0.5);
                background: rgba(102, 126, 234, 0.2);
                color: #f2f4ff;
                font-size: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.1s ease;
                backdrop-filter: blur(4px);
            }
            
            .touch-btn:active,
            .touch-btn.active {
                background: rgba(102, 126, 234, 0.5);
                border-color: rgba(102, 126, 234, 0.8);
                transform: scale(0.95);
            }
            
            .touch-btn-up { grid-area: up; }
            .touch-btn-down { grid-area: down; }
            .touch-btn-left { grid-area: left; }
            .touch-btn-right { grid-area: right; }
            
            .touch-btn-action {
                width: 80px;
                height: 80px;
                font-size: 32px;
            }
        `;
        document.head.appendChild(style);
    }

    return {
        /**
         * Show touch controls
         */
        show() {
            controlsEl.style.display = 'flex';
        },
        
        /**
         * Hide touch controls
         */
        hide() {
            controlsEl.style.display = 'none';
        },
        
        /**
         * Check if a button is currently pressed
         * @param {string} btn - Button name
         * @returns {boolean} Whether button is pressed
         */
        isPressed(btn) {
            return activeButtons.has(btn);
        },
        
        /**
         * Destroy touch controls
         */
        destroy() {
            controlsEl.remove();
        }
    };
}


// ============================================================================
// EXPORTS
// ============================================================================

// Make available globally for non-module usage
window.VanillaEngine = {
    createGameEngine,
    createInputManager,
    createHudManager,
    createDifficultyManager,
    createTouchControls,
    CanvasUtils,
    Collision,
    MathUtils,
    Storage
};

// Also export for ES modules if supported
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.VanillaEngine;
}
