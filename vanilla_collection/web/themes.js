/**
 * VANILLA Theme System
 * 
 * Provides theme selection and management for the Vanilla Collection.
 * Themes are implemented using CSS custom properties for safe switching.
 * 
 * @module themes
 * @version 1.0.0
 */

// ============================================================================
// THEME DEFINITIONS
// ============================================================================

const THEMES = {
    default: {
        name: 'Cosmic Purple',
        description: 'The original purple-blue gradient theme',
        icon: '🌌',
        colors: {
            // Primary Colors
            '--color-primary': '#667eea',
            '--color-secondary': '#764ba2',
            '--color-accent': '#f093fb',
            '--color-cyan': '#6ee7ff',
            '--color-success': '#9de8c7',
            '--color-danger': '#fb7185',
            '--color-warning': '#fcd34d',
            
            // Background Colors
            '--bg-dark': '#0a0e27',
            '--bg-darker': '#050913',
            '--bg-medium': '#1a2451',
            '--bg-light': '#243d66',
            
            // Text Colors
            '--text-primary': '#e0e0e0',
            '--text-secondary': '#b0b0b0',
            '--text-muted': '#808080',
            '--text-light': '#f2f4ff',
            
            // Border Colors
            '--border-subtle': 'rgba(255, 255, 255, 0.08)',
            '--border-light': 'rgba(255, 255, 255, 0.12)',
            '--border-primary': 'rgba(102, 126, 234, 0.3)',
            '--border-primary-hover': 'rgba(102, 126, 234, 0.7)',
            
            // Glass Effects
            '--glass-bg': 'rgba(255, 255, 255, 0.03)',
            '--glass-bg-hover': 'rgba(255, 255, 255, 0.05)',
            '--glass-border': 'rgba(255, 255, 255, 0.08)',
        }
    },
    
    ocean: {
        name: 'Ocean Deep',
        description: 'Cool oceanic blues and teals',
        icon: '🌊',
        colors: {
            '--color-primary': '#0891b2',
            '--color-secondary': '#0e7490',
            '--color-accent': '#22d3ee',
            '--color-cyan': '#67e8f9',
            '--color-success': '#34d399',
            '--color-danger': '#f87171',
            '--color-warning': '#fbbf24',
            
            '--bg-dark': '#042f2e',
            '--bg-darker': '#022524',
            '--bg-medium': '#134e4a',
            '--bg-light': '#0f766e',
            
            '--text-primary': '#ccfbf1',
            '--text-secondary': '#99f6e4',
            '--text-muted': '#5eead4',
            '--text-light': '#f0fdfa',
            
            '--border-subtle': 'rgba(94, 234, 212, 0.08)',
            '--border-light': 'rgba(94, 234, 212, 0.12)',
            '--border-primary': 'rgba(8, 145, 178, 0.3)',
            '--border-primary-hover': 'rgba(8, 145, 178, 0.7)',
            
            '--glass-bg': 'rgba(94, 234, 212, 0.03)',
            '--glass-bg-hover': 'rgba(94, 234, 212, 0.05)',
            '--glass-border': 'rgba(94, 234, 212, 0.08)',
        }
    },
    
    sunset: {
        name: 'Sunset Glow',
        description: 'Warm oranges and pinks',
        icon: '🌅',
        colors: {
            '--color-primary': '#f97316',
            '--color-secondary': '#ea580c',
            '--color-accent': '#fb923c',
            '--color-cyan': '#fbbf24',
            '--color-success': '#84cc16',
            '--color-danger': '#ef4444',
            '--color-warning': '#eab308',
            
            '--bg-dark': '#1c1917',
            '--bg-darker': '#0c0a09',
            '--bg-medium': '#44403c',
            '--bg-light': '#57534e',
            
            '--text-primary': '#fef3c7',
            '--text-secondary': '#fde68a',
            '--text-muted': '#fcd34d',
            '--text-light': '#fffbeb',
            
            '--border-subtle': 'rgba(251, 191, 36, 0.08)',
            '--border-light': 'rgba(251, 191, 36, 0.12)',
            '--border-primary': 'rgba(249, 115, 22, 0.3)',
            '--border-primary-hover': 'rgba(249, 115, 22, 0.7)',
            
            '--glass-bg': 'rgba(251, 191, 36, 0.03)',
            '--glass-bg-hover': 'rgba(251, 191, 36, 0.05)',
            '--glass-border': 'rgba(251, 191, 36, 0.08)',
        }
    },
    
    forest: {
        name: 'Forest Night',
        description: 'Deep greens and earthy tones',
        icon: '🌲',
        colors: {
            '--color-primary': '#22c55e',
            '--color-secondary': '#16a34a',
            '--color-accent': '#4ade80',
            '--color-cyan': '#86efac',
            '--color-success': '#a3e635',
            '--color-danger': '#ef4444',
            '--color-warning': '#facc15',
            
            '--bg-dark': '#052e16',
            '--bg-darker': '#022c22',
            '--bg-medium': '#14532d',
            '--bg-light': '#166534',
            
            '--text-primary': '#dcfce7',
            '--text-secondary': '#bbf7d0',
            '--text-muted': '#86efac',
            '--text-light': '#f0fdf4',
            
            '--border-subtle': 'rgba(134, 239, 172, 0.08)',
            '--border-light': 'rgba(134, 239, 172, 0.12)',
            '--border-primary': 'rgba(34, 197, 94, 0.3)',
            '--border-primary-hover': 'rgba(34, 197, 94, 0.7)',
            
            '--glass-bg': 'rgba(134, 239, 172, 0.03)',
            '--glass-bg-hover': 'rgba(134, 239, 172, 0.05)',
            '--glass-border': 'rgba(134, 239, 172, 0.08)',
        }
    },
    
    midnight: {
        name: 'Midnight',
        description: 'Pure dark mode with subtle accents',
        icon: '🌙',
        colors: {
            '--color-primary': '#6366f1',
            '--color-secondary': '#4f46e5',
            '--color-accent': '#a5b4fc',
            '--color-cyan': '#c7d2fe',
            '--color-success': '#34d399',
            '--color-danger': '#f87171',
            '--color-warning': '#fbbf24',
            
            '--bg-dark': '#09090b',
            '--bg-darker': '#000000',
            '--bg-medium': '#18181b',
            '--bg-light': '#27272a',
            
            '--text-primary': '#e4e4e7',
            '--text-secondary': '#a1a1aa',
            '--text-muted': '#71717a',
            '--text-light': '#fafafa',
            
            '--border-subtle': 'rgba(161, 161, 170, 0.08)',
            '--border-light': 'rgba(161, 161, 170, 0.12)',
            '--border-primary': 'rgba(99, 102, 241, 0.3)',
            '--border-primary-hover': 'rgba(99, 102, 241, 0.7)',
            
            '--glass-bg': 'rgba(161, 161, 170, 0.03)',
            '--glass-bg-hover': 'rgba(161, 161, 170, 0.05)',
            '--glass-border': 'rgba(161, 161, 170, 0.08)',
        }
    },
    
    cherry: {
        name: 'Cherry Blossom',
        description: 'Soft pinks and elegant purples',
        icon: '🌸',
        colors: {
            '--color-primary': '#ec4899',
            '--color-secondary': '#db2777',
            '--color-accent': '#f472b6',
            '--color-cyan': '#f9a8d4',
            '--color-success': '#4ade80',
            '--color-danger': '#ef4444',
            '--color-warning': '#fbbf24',
            
            '--bg-dark': '#1a0a14',
            '--bg-darker': '#0d050a',
            '--bg-medium': '#3b1029',
            '--bg-light': '#5b1a3f',
            
            '--text-primary': '#fce7f3',
            '--text-secondary': '#fbcfe8',
            '--text-muted': '#f9a8d4',
            '--text-light': '#fdf2f8',
            
            '--border-subtle': 'rgba(249, 168, 212, 0.08)',
            '--border-light': 'rgba(249, 168, 212, 0.12)',
            '--border-primary': 'rgba(236, 72, 153, 0.3)',
            '--border-primary-hover': 'rgba(236, 72, 153, 0.7)',
            
            '--glass-bg': 'rgba(249, 168, 212, 0.03)',
            '--glass-bg-hover': 'rgba(249, 168, 212, 0.05)',
            '--glass-border': 'rgba(249, 168, 212, 0.08)',
        }
    },

    retro: {
        name: 'Retro Arcade',
        description: 'Classic arcade neon vibes',
        icon: '👾',
        colors: {
            '--color-primary': '#00ff00',
            '--color-secondary': '#00cc00',
            '--color-accent': '#ffff00',
            '--color-cyan': '#00ffff',
            '--color-success': '#00ff00',
            '--color-danger': '#ff0000',
            '--color-warning': '#ffff00',
            
            '--bg-dark': '#000000',
            '--bg-darker': '#000000',
            '--bg-medium': '#111111',
            '--bg-light': '#1a1a1a',
            
            '--text-primary': '#00ff00',
            '--text-secondary': '#00cc00',
            '--text-muted': '#008800',
            '--text-light': '#00ff00',
            
            '--border-subtle': 'rgba(0, 255, 0, 0.15)',
            '--border-light': 'rgba(0, 255, 0, 0.25)',
            '--border-primary': 'rgba(0, 255, 0, 0.4)',
            '--border-primary-hover': 'rgba(0, 255, 0, 0.8)',
            
            '--glass-bg': 'rgba(0, 255, 0, 0.03)',
            '--glass-bg-hover': 'rgba(0, 255, 0, 0.06)',
            '--glass-border': 'rgba(0, 255, 0, 0.15)',
        }
    }
};

// ============================================================================
// THEME MANAGER
// ============================================================================

const ThemeManager = {
    STORAGE_KEY: 'vanilla-theme',
    currentTheme: 'default',
    
    /**
     * Initialize the theme system
     * Loads saved theme from localStorage
     */
    init() {
        try {
            const saved = localStorage.getItem(this.STORAGE_KEY);
            if (saved && THEMES[saved]) {
                this.currentTheme = saved;
            }
        } catch (e) {
            console.warn('Failed to load theme preference:', e);
        }
        
        this.apply(this.currentTheme);
        this.createToggleButton();
    },
    
    /**
     * Apply a theme
     * @param {string} themeId - Theme identifier
     */
    apply(themeId) {
        const theme = THEMES[themeId];
        if (!theme) {
            console.warn(`Theme "${themeId}" not found`);
            return;
        }
        
        const root = document.documentElement;
        
        // Apply all color variables
        for (const [property, value] of Object.entries(theme.colors)) {
            root.style.setProperty(property, value);
        }
        
        // Update body background gradient
        const bgDark = theme.colors['--bg-dark'];
        const bgMedium = theme.colors['--bg-medium'];
        const bgLight = theme.colors['--bg-light'];
        document.body.style.background = `linear-gradient(180deg, ${bgDark} 0%, ${bgMedium} 50%, ${bgLight} 100%)`;
        
        // Update current theme
        this.currentTheme = themeId;
        
        // Persist preference
        try {
            localStorage.setItem(this.STORAGE_KEY, themeId);
        } catch (e) {
            console.warn('Failed to save theme preference:', e);
        }
        
        // Dispatch event for components that need to react
        document.dispatchEvent(new CustomEvent('themechange', { 
            detail: { theme: themeId, colors: theme.colors } 
        }));
    },
    
    /**
     * Get list of available themes
     * @returns {Array} Array of theme objects with id, name, description, icon
     */
    getThemes() {
        return Object.entries(THEMES).map(([id, theme]) => ({
            id,
            name: theme.name,
            description: theme.description,
            icon: theme.icon
        }));
    },
    
    /**
     * Get current theme info
     * @returns {Object} Current theme object
     */
    getCurrentTheme() {
        return {
            id: this.currentTheme,
            ...THEMES[this.currentTheme]
        };
    },
    
    /**
     * Cycle to next theme
     */
    nextTheme() {
        const themeIds = Object.keys(THEMES);
        const currentIndex = themeIds.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeIds.length;
        this.apply(themeIds[nextIndex]);
    },
    
    /**
     * Create a theme toggle button in the header
     */
    createToggleButton() {
        // Only create if header exists and button doesn't already exist
        const header = document.querySelector('header');
        if (!header || document.getElementById('themeBtn')) return;
        
        const btn = document.createElement('button');
        btn.id = 'themeBtn';
        btn.className = 'theme-btn';
        btn.title = 'Change Theme';
        btn.innerHTML = THEMES[this.currentTheme].icon;
        btn.onclick = () => this.showSelector();
        
        // Add styles if not present
        if (!document.getElementById('theme-btn-styles')) {
            const style = document.createElement('style');
            style.id = 'theme-btn-styles';
            style.textContent = `
                .theme-btn {
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 18px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    margin-left: auto;
                    margin-right: 16px;
                }
                .theme-btn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    transform: scale(1.05);
                }
                
                /* Theme Selector Modal */
                .theme-selector-overlay {
                    position: fixed;
                    inset: 0;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(8px);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    z-index: 10000;
                    padding: 20px;
                    animation: fadeIn 0.2s ease;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                .theme-selector {
                    background: var(--bg-dark);
                    border: 1px solid var(--border-light);
                    border-radius: 16px;
                    padding: 24px;
                    max-width: 600px;
                    width: 100%;
                    max-height: 80vh;
                    overflow-y: auto;
                    animation: slideUp 0.3s ease;
                }
                
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .theme-selector h2 {
                    font-family: 'Poppins', sans-serif;
                    font-size: 24px;
                    font-weight: 700;
                    margin-bottom: 8px;
                    color: var(--text-light);
                }
                
                .theme-selector p {
                    font-size: 14px;
                    color: var(--text-secondary);
                    margin-bottom: 20px;
                }
                
                .theme-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                    gap: 12px;
                }
                
                .theme-option {
                    background: var(--glass-bg);
                    border: 2px solid var(--border-subtle);
                    border-radius: 12px;
                    padding: 16px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    text-align: center;
                }
                
                .theme-option:hover {
                    background: var(--glass-bg-hover);
                    border-color: var(--border-primary);
                    transform: translateY(-2px);
                }
                
                .theme-option.active {
                    border-color: var(--color-primary);
                    background: rgba(102, 126, 234, 0.1);
                }
                
                .theme-option-icon {
                    font-size: 32px;
                    margin-bottom: 8px;
                }
                
                .theme-option-name {
                    font-weight: 600;
                    font-size: 14px;
                    color: var(--text-primary);
                    margin-bottom: 4px;
                }
                
                .theme-option-desc {
                    font-size: 11px;
                    color: var(--text-muted);
                    line-height: 1.4;
                }
                
                .theme-selector-close {
                    margin-top: 20px;
                    width: 100%;
                    padding: 12px;
                    background: var(--glass-bg);
                    border: 1px solid var(--border-light);
                    border-radius: 8px;
                    color: var(--text-primary);
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .theme-selector-close:hover {
                    background: var(--glass-bg-hover);
                }
            `;
            document.head.appendChild(style);
        }
        
        // Try to insert before back link or at the end
        const headerActions = header.querySelector('.header-actions');
        if (headerActions) {
            headerActions.insertBefore(btn, headerActions.firstChild);
        } else {
            // Insert after the first element (usually brand/nav)
            const firstChild = header.firstElementChild;
            if (firstChild && firstChild.nextSibling) {
                header.insertBefore(btn, firstChild.nextSibling);
            } else {
                header.appendChild(btn);
            }
        }
    },
    
    /**
     * Show theme selector modal
     */
    showSelector() {
        // Remove existing if present
        const existing = document.getElementById('themeSelector');
        if (existing) existing.remove();
        
        const overlay = document.createElement('div');
        overlay.id = 'themeSelector';
        overlay.className = 'theme-selector-overlay';
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.remove();
        };
        
        const modal = document.createElement('div');
        modal.className = 'theme-selector';
        
        let html = `
            <h2>🎨 Choose Theme</h2>
            <p>Select a color theme for your gaming experience</p>
            <div class="theme-grid">
        `;
        
        for (const [id, theme] of Object.entries(THEMES)) {
            const isActive = id === this.currentTheme;
            html += `
                <div class="theme-option ${isActive ? 'active' : ''}" data-theme="${id}">
                    <div class="theme-option-icon">${theme.icon}</div>
                    <div class="theme-option-name">${theme.name}</div>
                    <div class="theme-option-desc">${theme.description}</div>
                </div>
            `;
        }
        
        html += `
            </div>
            <button class="theme-selector-close">Close</button>
        `;
        
        modal.innerHTML = html;
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // Add click handlers
        modal.querySelectorAll('.theme-option').forEach(opt => {
            opt.onclick = () => {
                const themeId = opt.getAttribute('data-theme');
                this.apply(themeId);
                
                // Update button icon
                const btn = document.getElementById('themeBtn');
                if (btn) btn.innerHTML = THEMES[themeId].icon;
                
                // Update active state
                modal.querySelectorAll('.theme-option').forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
            };
        });
        
        modal.querySelector('.theme-selector-close').onclick = () => overlay.remove();
        
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
    document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
} else {
    ThemeManager.init();
}

// Export for use in modules
window.VanillaTheme = ThemeManager;
window.VANILLA_THEMES = THEMES;
