/**
 * VANILLA Key Bindings System
 * 
 * Provides customizable key bindings for all games in the Vanilla Collection.
 * Bindings are stored in localStorage and can be modified via a settings UI.
 * 
 * @module keybindings
 * @version 1.0.0
 */

// ============================================================================
// DEFAULT KEY BINDINGS
// ============================================================================

const DEFAULT_BINDINGS = {
    // Movement
    move_up: ['w', 'arrowup'],
    move_down: ['s', 'arrowdown'],
    move_left: ['a', 'arrowleft'],
    move_right: ['d', 'arrowright'],
    
    // Actions
    action: [' '],           // Space - primary action (shoot, jump, etc.)
    action_alt: ['enter'],   // Alternative action
    pause: ['p', 'escape'],
    restart: ['r'],
    
    // Game-specific
    rotate_cw: ['arrowup', 'w', 'x'],    // Tetris: rotate clockwise
    rotate_ccw: ['z', 'control'],         // Tetris: rotate counter-clockwise
    hard_drop: [' '],                     // Tetris: hard drop
    soft_drop: ['arrowdown', 's'],        // Tetris: soft drop
    hold: ['c', 'shift'],                 // Tetris: hold piece
    
    // Flappy Bird
    flap: [' ', 'w', 'arrowup'],
    
    // Asteroids
    thrust: ['w', 'arrowup'],
    fire: [' '],
    hyperspace: ['shift', 'h'],
    
    // Pac-Man (uses standard movement)
};

// Action descriptions for UI
const ACTION_DESCRIPTIONS = {
    move_up: 'Move Up',
    move_down: 'Move Down',
    move_left: 'Move Left',
    move_right: 'Move Right',
    action: 'Primary Action (Jump/Shoot)',
    action_alt: 'Alternative Action',
    pause: 'Pause Game',
    restart: 'Restart Game',
    rotate_cw: 'Rotate Clockwise (Tetris)',
    rotate_ccw: 'Rotate Counter-Clockwise (Tetris)',
    hard_drop: 'Hard Drop (Tetris)',
    soft_drop: 'Soft Drop (Tetris)',
    hold: 'Hold Piece (Tetris)',
    flap: 'Flap (Flappy Bird)',
    thrust: 'Thrust (Asteroids)',
    fire: 'Fire (Asteroids)',
    hyperspace: 'Hyperspace (Asteroids)'
};

// Key display names
const KEY_DISPLAY_NAMES = {
    ' ': 'Space',
    'arrowup': '↑',
    'arrowdown': '↓',
    'arrowleft': '←',
    'arrowright': '→',
    'escape': 'Esc',
    'enter': 'Enter',
    'shift': 'Shift',
    'control': 'Ctrl',
    'alt': 'Alt',
    'tab': 'Tab',
    'backspace': 'Backspace'
};

// ============================================================================
// KEY BINDINGS MANAGER
// ============================================================================

const KeyBindingsManager = {
    STORAGE_KEY: 'vanilla-keybindings',
    bindings: {},
    isListening: false,
    listeningAction: null,
    listeningCallback: null,
    
    /**
     * Initialize the key bindings system
     */
    init() {
        this.load();
        this.injectStyles();
    },
    
    /**
     * Load key bindings from localStorage
     */
    load() {
        this.bindings = { ...DEFAULT_BINDINGS };
        
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                // Merge saved bindings with defaults
                for (const [action, keys] of Object.entries(parsed)) {
                    if (DEFAULT_BINDINGS[action]) {
                        this.bindings[action] = keys;
                    }
                }
            }
        } catch (e) {
            console.warn('Failed to load key bindings:', e);
        }
    },
    
    /**
     * Save key bindings to localStorage
     */
    save() {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(this.bindings));
        } catch (e) {
            console.warn('Failed to save key bindings:', e);
        }
    },
    
    /**
     * Get keys bound to an action
     * @param {string} action - Action name
     * @returns {string[]} Array of bound keys
     */
    getKeys(action) {
        return this.bindings[action] || DEFAULT_BINDINGS[action] || [];
    },
    
    /**
     * Check if a key is bound to an action
     * @param {string} key - Key to check (lowercase)
     * @param {string} action - Action name
     * @returns {boolean}
     */
    isKeyBound(key, action) {
        const keys = this.getKeys(action);
        return keys.includes(key.toLowerCase());
    },
    
    /**
     * Check if any of the keys for an action are pressed
     * @param {Object} keysState - Object with key states
     * @param {string} action - Action name
     * @returns {boolean}
     */
    isActionPressed(keysState, action) {
        const boundKeys = this.getKeys(action);
        return boundKeys.some(k => keysState[k]);
    },
    
    /**
     * Set keys for an action
     * @param {string} action - Action name
     * @param {string[]} keys - Array of keys
     */
    setKeys(action, keys) {
        if (DEFAULT_BINDINGS[action]) {
            this.bindings[action] = keys.map(k => k.toLowerCase());
            this.save();
        }
    },
    
    /**
     * Add a key to an action
     * @param {string} action - Action name
     * @param {string} key - Key to add
     */
    addKey(action, key) {
        const normalizedKey = key.toLowerCase();
        const keys = this.getKeys(action);
        if (!keys.includes(normalizedKey)) {
            keys.push(normalizedKey);
            this.setKeys(action, keys);
        }
    },
    
    /**
     * Remove a key from an action
     * @param {string} action - Action name
     * @param {string} key - Key to remove
     */
    removeKey(action, key) {
        const normalizedKey = key.toLowerCase();
        const keys = this.getKeys(action).filter(k => k !== normalizedKey);
        this.setKeys(action, keys);
    },
    
    /**
     * Reset an action to default bindings
     * @param {string} action - Action name
     */
    resetAction(action) {
        if (DEFAULT_BINDINGS[action]) {
            this.bindings[action] = [...DEFAULT_BINDINGS[action]];
            this.save();
        }
    },
    
    /**
     * Reset all bindings to defaults
     */
    resetAll() {
        this.bindings = { ...DEFAULT_BINDINGS };
        // Deep copy arrays
        for (const key of Object.keys(this.bindings)) {
            this.bindings[key] = [...DEFAULT_BINDINGS[key]];
        }
        this.save();
    },
    
    /**
     * Get display name for a key
     * @param {string} key - Key code
     * @returns {string} Display name
     */
    getKeyDisplayName(key) {
        const lower = key.toLowerCase();
        if (KEY_DISPLAY_NAMES[lower]) {
            return KEY_DISPLAY_NAMES[lower];
        }
        return key.toUpperCase();
    },
    
    /**
     * Start listening for a key press to bind
     * @param {string} action - Action to bind
     * @param {Function} callback - Called when key is captured
     */
    startListening(action, callback) {
        this.isListening = true;
        this.listeningAction = action;
        this.listeningCallback = callback;
        
        const handleKeyDown = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const key = e.key.toLowerCase();
            
            // Don't allow binding certain keys
            if (['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'].includes(key)) {
                return;
            }
            
            this.isListening = false;
            this.listeningAction = null;
            document.removeEventListener('keydown', handleKeyDown, true);
            
            if (callback) {
                callback(key);
            }
        };
        
        document.addEventListener('keydown', handleKeyDown, true);
        
        // Cancel on click outside
        setTimeout(() => {
            const handleClick = () => {
                if (this.isListening) {
                    this.isListening = false;
                    this.listeningAction = null;
                    document.removeEventListener('keydown', handleKeyDown, true);
                    if (callback) callback(null);
                }
                document.removeEventListener('click', handleClick);
            };
            document.addEventListener('click', handleClick);
        }, 100);
    },
    
    /**
     * Inject CSS styles
     */
    injectStyles() {
        if (document.getElementById('keybindings-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'keybindings-styles';
        style.textContent = `
            /* Key Bindings Button */
            .keybindings-btn {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-right: 8px;
            }
            
            .keybindings-btn:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: scale(1.05);
            }
            
            /* Key Bindings Modal */
            .keybindings-modal-overlay {
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
            
            .keybindings-modal {
                background: var(--bg-dark, #0a0e27);
                border: 1px solid var(--border-light, rgba(255,255,255,0.12));
                border-radius: 20px;
                max-width: 600px;
                width: 100%;
                animation: slideUp 0.3s ease;
            }
            
            .keybindings-modal-header {
                padding: 24px;
                border-bottom: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
            }
            
            .keybindings-modal-header h2 {
                font-family: 'Poppins', sans-serif;
                font-size: 24px;
                font-weight: 700;
                color: var(--text-light, #f2f4ff);
                margin: 0 0 8px;
            }
            
            .keybindings-modal-header p {
                font-size: 14px;
                color: var(--text-secondary, #b0b0b0);
                margin: 0;
            }
            
            .keybindings-modal-body {
                padding: 24px;
                max-height: 60vh;
                overflow-y: auto;
            }
            
            .keybindings-section {
                margin-bottom: 24px;
            }
            
            .keybindings-section:last-child {
                margin-bottom: 0;
            }
            
            .keybindings-section-title {
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: var(--text-secondary, #b0b0b0);
                margin-bottom: 12px;
            }
            
            .keybinding-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 12px 16px;
                background: var(--glass-bg, rgba(255,255,255,0.03));
                border: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
                border-radius: 10px;
                margin-bottom: 8px;
            }
            
            .keybinding-row:last-child {
                margin-bottom: 0;
            }
            
            .keybinding-label {
                font-size: 14px;
                color: var(--text-primary, #e0e0e0);
                font-weight: 500;
            }
            
            .keybinding-keys {
                display: flex;
                gap: 8px;
                align-items: center;
                flex-wrap: wrap;
            }
            
            .keybinding-key {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 10px;
                background: rgba(102, 126, 234, 0.15);
                border: 1px solid rgba(102, 126, 234, 0.3);
                border-radius: 6px;
                font-family: 'Press Start 2P', monospace;
                font-size: 10px;
                color: var(--text-light, #f2f4ff);
            }
            
            .keybinding-key-remove {
                background: none;
                border: none;
                color: var(--color-danger, #fb7185);
                cursor: pointer;
                padding: 0;
                font-size: 12px;
                opacity: 0.7;
                transition: opacity 0.2s;
            }
            
            .keybinding-key-remove:hover {
                opacity: 1;
            }
            
            .keybinding-add {
                padding: 6px 12px;
                background: var(--glass-bg, rgba(255,255,255,0.03));
                border: 1px dashed var(--border-light, rgba(255,255,255,0.12));
                border-radius: 6px;
                color: var(--text-muted, #808080);
                font-size: 12px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .keybinding-add:hover {
                background: var(--glass-bg-hover, rgba(255,255,255,0.05));
                border-color: var(--color-primary, #667eea);
                color: var(--text-primary, #e0e0e0);
            }
            
            .keybinding-add.listening {
                background: rgba(102, 126, 234, 0.2);
                border-color: var(--color-primary, #667eea);
                border-style: solid;
                animation: pulse 1s ease-in-out infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .keybindings-modal-footer {
                padding: 16px 24px;
                border-top: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
                display: flex;
                justify-content: space-between;
                gap: 12px;
            }
            
            .keybindings-reset {
                padding: 12px 20px;
                background: rgba(251, 113, 133, 0.1);
                border: 1px solid rgba(251, 113, 133, 0.3);
                border-radius: 8px;
                color: var(--color-danger, #fb7185);
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .keybindings-reset:hover {
                background: rgba(251, 113, 133, 0.2);
            }
            
            .keybindings-close {
                padding: 12px 24px;
                background: var(--glass-bg, rgba(255,255,255,0.03));
                border: 1px solid var(--border-light, rgba(255,255,255,0.12));
                border-radius: 8px;
                color: var(--text-primary, #e0e0e0);
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .keybindings-close:hover {
                background: var(--glass-bg-hover, rgba(255,255,255,0.05));
            }
        `;
        document.head.appendChild(style);
    },
    
    /**
     * Create key bindings button in header
     */
    createButton() {
        const header = document.querySelector('header');
        if (!header || document.getElementById('keybindingsBtn')) return;
        
        const btn = document.createElement('button');
        btn.id = 'keybindingsBtn';
        btn.className = 'keybindings-btn';
        btn.title = 'Key Bindings';
        btn.innerHTML = '⌨️';
        btn.onclick = () => this.showModal();
        
        // Insert near achievement button
        const achievementBtn = document.getElementById('achievementBtn');
        if (achievementBtn) {
            achievementBtn.parentNode.insertBefore(btn, achievementBtn);
        } else {
            const themeBtn = document.getElementById('themeBtn');
            if (themeBtn) {
                themeBtn.parentNode.insertBefore(btn, themeBtn);
            } else {
                header.appendChild(btn);
            }
        }
    },
    
    /**
     * Show key bindings modal
     */
    showModal() {
        // Remove existing
        const existing = document.getElementById('keybindingsModal');
        if (existing) existing.remove();
        
        const overlay = document.createElement('div');
        overlay.id = 'keybindingsModal';
        overlay.className = 'keybindings-modal-overlay';
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.remove();
        };
        
        // Group actions by category
        const categories = {
            'Movement': ['move_up', 'move_down', 'move_left', 'move_right'],
            'Actions': ['action', 'action_alt', 'pause', 'restart'],
            'Tetris': ['rotate_cw', 'rotate_ccw', 'hard_drop', 'soft_drop', 'hold'],
            'Flappy Bird': ['flap'],
            'Asteroids': ['thrust', 'fire', 'hyperspace']
        };
        
        let html = `
            <div class="keybindings-modal">
                <div class="keybindings-modal-header">
                    <h2>⌨️ Key Bindings</h2>
                    <p>Customize your controls. Click a key to remove it, or click "Add" to bind a new key.</p>
                </div>
                <div class="keybindings-modal-body">
        `;
        
        for (const [category, actions] of Object.entries(categories)) {
            html += `
                <div class="keybindings-section">
                    <div class="keybindings-section-title">${category}</div>
            `;
            
            for (const action of actions) {
                const keys = this.getKeys(action);
                const description = ACTION_DESCRIPTIONS[action] || action;
                
                html += `
                    <div class="keybinding-row" data-action="${action}">
                        <div class="keybinding-label">${description}</div>
                        <div class="keybinding-keys">
                `;
                
                for (const key of keys) {
                    html += `
                        <span class="keybinding-key" data-key="${key}">
                            ${this.getKeyDisplayName(key)}
                            <button class="keybinding-key-remove" data-action="${action}" data-key="${key}">×</button>
                        </span>
                    `;
                }
                
                html += `
                            <button class="keybinding-add" data-action="${action}">+ Add</button>
                        </div>
                    </div>
                `;
            }
            
            html += `</div>`;
        }
        
        html += `
                </div>
                <div class="keybindings-modal-footer">
                    <button class="keybindings-reset">Reset to Defaults</button>
                    <button class="keybindings-close">Close</button>
                </div>
            </div>
        `;
        
        overlay.innerHTML = html;
        document.body.appendChild(overlay);
        
        // Add event handlers
        overlay.querySelectorAll('.keybinding-key-remove').forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                const key = btn.dataset.key;
                this.removeKey(action, key);
                this.showModal(); // Refresh
            };
        });
        
        overlay.querySelectorAll('.keybinding-add').forEach(btn => {
            btn.onclick = (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                
                // Visual feedback
                btn.classList.add('listening');
                btn.textContent = 'Press a key...';
                
                this.startListening(action, (key) => {
                    if (key) {
                        this.addKey(action, key);
                    }
                    this.showModal(); // Refresh
                });
            };
        });
        
        overlay.querySelector('.keybindings-reset').onclick = () => {
            if (confirm('Reset all key bindings to defaults?')) {
                this.resetAll();
                this.showModal(); // Refresh
            }
        };
        
        overlay.querySelector('.keybindings-close').onclick = () => overlay.remove();
        
        // Close on Escape
        const handleEsc = (e) => {
            if (e.key === 'Escape' && !this.isListening) {
                overlay.remove();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }
};

// ============================================================================
// HELPER FUNCTIONS FOR GAMES
// ============================================================================

/**
 * Create an input helper for a game
 * @param {Object} inputManager - The input manager instance
 * @returns {Object} Helper object with action-based input checking
 */
function createGameInput(inputManager) {
    return {
        /**
         * Check if an action is currently pressed
         * @param {string} action - Action name
         * @returns {boolean}
         */
        isPressed(action) {
            const keys = KeyBindingsManager.getKeys(action);
            return keys.some(k => inputManager.isPressed(k));
        },
        
        /**
         * Check if any of the given actions are pressed
         * @param {...string} actions - Action names
         * @returns {boolean}
         */
        isAnyPressed(...actions) {
            return actions.some(action => this.isPressed(action));
        },
        
        /**
         * Register a callback for an action
         * @param {string} action - Action name
         * @param {Function} callback - Callback function
         */
        onAction(action, callback) {
            const keys = KeyBindingsManager.getKeys(action);
            keys.forEach(key => {
                inputManager.onKey(key, callback);
            });
        },
        
        /**
         * Get the keys bound to an action
         * @param {string} action - Action name
         * @returns {string[]}
         */
        getKeys(action) {
            return KeyBindingsManager.getKeys(action);
        },
        
        /**
         * Get display string for action keys
         * @param {string} action - Action name
         * @returns {string}
         */
        getKeysDisplay(action) {
            const keys = KeyBindingsManager.getKeys(action);
            return keys.map(k => KeyBindingsManager.getKeyDisplayName(k)).join(' / ');
        }
    };
}

// ============================================================================
// AUTO-INITIALIZE
// ============================================================================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        KeyBindingsManager.init();
        // Delay button creation slightly to ensure other buttons exist
        setTimeout(() => KeyBindingsManager.createButton(), 100);
    });
} else {
    KeyBindingsManager.init();
    setTimeout(() => KeyBindingsManager.createButton(), 100);
}

// Export for use in games
window.VanillaKeyBindings = KeyBindingsManager;
window.createGameInput = createGameInput;
