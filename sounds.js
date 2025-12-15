/**
 * VANILLA Collection - Sound System
 * 
 * A lightweight sound engine using Web Audio API to generate retro arcade-style sounds.
 * All sounds are procedurally generated - no audio files needed!
 */

class SoundEngine {
    constructor() {
        this.context = null;
        this.masterGain = null;
        this.enabled = true;
        this.volume = 0.3; // Default volume (0-1)
        this.initialized = false;
        
        // Load sound preferences from localStorage
        const savedEnabled = localStorage.getItem('vanilla-sound-enabled');
        const savedVolume = localStorage.getItem('vanilla-sound-volume');
        
        if (savedEnabled !== null) {
            this.enabled = savedEnabled === 'true';
        }
        if (savedVolume !== null) {
            this.volume = parseFloat(savedVolume);
        }
    }

    /**
     * Initialize the audio context (must be called after user interaction)
     */
    init() {
        if (this.initialized) return;
        
        try {
            this.context = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.context.createGain();
            this.masterGain.connect(this.context.destination);
            this.masterGain.gain.value = this.enabled ? this.volume : 0;
            this.initialized = true;
        } catch (e) {
            console.warn('Web Audio API not supported:', e);
        }
    }

    /**
     * Create an oscillator node with specified parameters
     */
    createOscillator(frequency, type = 'sine') {
        if (!this.context) return null;
        const osc = this.context.createOscillator();
        osc.type = type;
        osc.frequency.value = frequency;
        return osc;
    }

    /**
     * Create a gain node
     */
    createGain(initialValue = 1) {
        if (!this.context) return null;
        const gain = this.context.createGain();
        gain.gain.value = initialValue;
        return gain;
    }

    /**
     * Get current audio context time
     */
    now() {
        return this.context ? this.context.currentTime : 0;
    }

    /**
     * Play a simple beep sound
     */
    beep(frequency = 440, duration = 0.1, volume = 0.3) {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(frequency, 'square');
        const gain = this.createGain(volume);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        osc.start(now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + duration);
        osc.stop(now + duration);
    }

    /**
     * Play a coin/collect sound
     */
    coin() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(800, 'square');
        const gain = this.createGain(0.3);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        
        osc.start(now);
        osc.stop(now + 0.15);
    }

    /**
     * Play a hit/bounce sound
     */
    hit() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(150, 'sawtooth');
        const gain = this.createGain(0.4);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        osc.frequency.exponentialRampToValueAtTime(50, now + 0.08);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
        
        osc.start(now);
        osc.stop(now + 0.08);
    }

    /**
     * Play a jump sound
     */
    jump() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(300, 'square');
        const gain = this.createGain(0.25);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        osc.frequency.exponentialRampToValueAtTime(600, now + 0.1);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        
        osc.start(now);
        osc.stop(now + 0.15);
    }

    /**
     * Play an explosion sound
     */
    explode() {
        if (!this.enabled || !this.context) return;
        this.init();

        const noise = this.context.createBufferSource();
        const buffer = this.context.createBuffer(1, this.context.sampleRate * 0.3, this.context.sampleRate);
        const data = buffer.getChannelData(0);
        
        for (let i = 0; i < data.length; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        
        noise.buffer = buffer;
        
        const filter = this.context.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = 800;
        
        const gain = this.createGain(0.4);
        
        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        filter.frequency.exponentialRampToValueAtTime(50, now + 0.25);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        
        noise.start(now);
    }

    /**
     * Play a game over sound
     */
    gameOver() {
        if (!this.enabled || !this.context) return;
        this.init();

        const frequencies = [440, 392, 349, 294, 262];
        frequencies.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.createOscillator(freq, 'triangle');
                const gain = this.createGain(0.2);
                
                osc.connect(gain);
                gain.connect(this.masterGain);
                
                const now = this.now();
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                
                osc.start(now);
                osc.stop(now + 0.3);
            }, i * 100);
        });
    }

    /**
     * Play a victory sound
     */
    victory() {
        if (!this.enabled || !this.context) return;
        this.init();

        const frequencies = [523, 659, 784, 1047];
        frequencies.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.createOscillator(freq, 'sine');
                const gain = this.createGain(0.25);
                
                osc.connect(gain);
                gain.connect(this.masterGain);
                
                const now = this.now();
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                
                osc.start(now);
                osc.stop(now + 0.2);
            }, i * 80);
        });
    }

    /**
     * Play a shoot/fire sound
     */
    shoot() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(800, 'sawtooth');
        const gain = this.createGain(0.2);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        osc.frequency.exponentialRampToValueAtTime(100, now + 0.08);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
        
        osc.start(now);
        osc.stop(now + 0.08);
    }

    /**
     * Play a powerup sound
     */
    powerup() {
        if (!this.enabled || !this.context) return;
        this.init();

        const notes = [523, 659, 784, 1047, 1319];
        notes.forEach((freq, i) => {
            setTimeout(() => {
                const osc = this.createOscillator(freq, 'square');
                const gain = this.createGain(0.15);
                
                osc.connect(gain);
                gain.connect(this.masterGain);
                
                const now = this.now();
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
                
                osc.start(now);
                osc.stop(now + 0.1);
            }, i * 40);
        });
    }

    /**
     * Play a menu select sound
     */
    menuSelect() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(600, 'sine');
        const gain = this.createGain(0.2);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.1);
        
        osc.start(now);
        osc.stop(now + 0.1);
    }

    /**
     * Play a click sound
     */
    click() {
        if (!this.enabled || !this.context) return;
        this.init();

        const osc = this.createOscillator(800, 'square');
        const gain = this.createGain(0.15);
        
        osc.connect(gain);
        gain.connect(this.masterGain);
        
        const now = this.now();
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
        
        osc.start(now);
        osc.stop(now + 0.05);
    }

    /**
     * Toggle sound on/off
     */
    toggle() {
        this.enabled = !this.enabled;
        if (this.masterGain) {
            this.masterGain.gain.value = this.enabled ? this.volume : 0;
        }
        localStorage.setItem('vanilla-sound-enabled', this.enabled);
        return this.enabled;
    }

    /**
     * Set volume (0-1)
     */
    setVolume(value) {
        this.volume = Math.max(0, Math.min(1, value));
        if (this.masterGain && this.enabled) {
            this.masterGain.gain.value = this.volume;
        }
        localStorage.setItem('vanilla-sound-volume', this.volume);
    }

    /**
     * Get current enabled state
     */
    isEnabled() {
        return this.enabled;
    }

    /**
     * Get current volume
     */
    getVolume() {
        return this.volume;
    }
}

// Create global sound engine instance
const soundEngine = new SoundEngine();

// Export for use in games
if (typeof module !== 'undefined' && module.exports) {
    module.exports = soundEngine;
}
