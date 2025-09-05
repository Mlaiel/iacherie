/**
 * Ainflue Desktop - Professional Controls
 * Contrôles interface professionnels
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Professional controls for audio/video editing, content creation
 * Optimized for musicians, photographers, bloggers, influencers, comedians
 */

export class ProfessionalControls {
    constructor() {
        this.controls = new Map();
        this.activeControls = new Set();
        this.shortcuts = new Map();
        
        this.initializeControls();
        this.setupKeyboardShortcuts();
    }

    initializeControls() {
        // Audio controls for musicians and podcasters
        this.controls.set('audio', {
            play: { icon: '▶️', shortcut: 'Space', action: 'playPause' },
            record: { icon: '⏺️', shortcut: 'R', action: 'record' },
            stop: { icon: '⏹️', shortcut: 'S', action: 'stop' },
            loop: { icon: '🔄', shortcut: 'L', action: 'toggleLoop' },
            metronome: { icon: '🎵', shortcut: 'M', action: 'toggleMetronome' }
        });

        // Video controls for content creators
        this.controls.set('video', {
            preview: { icon: '📺', shortcut: 'P', action: 'togglePreview' },
            fullscreen: { icon: '🖥️', shortcut: 'F', action: 'toggleFullscreen' },
            split: { icon: '✂️', shortcut: 'Ctrl+B', action: 'splitClip' },
            trim: { icon: '📏', shortcut: 'T', action: 'trimMode' },
            keyframe: { icon: '💎', shortcut: 'K', action: 'addKeyframe' }
        });

        // Professional workflow controls
        this.controls.set('workflow', {
            save: { icon: '💾', shortcut: 'Ctrl+S', action: 'saveProject' },
            export: { icon: '📤', shortcut: 'Ctrl+E', action: 'exportProject' },
            undo: { icon: '↶', shortcut: 'Ctrl+Z', action: 'undo' },
            redo: { icon: '↷', shortcut: 'Ctrl+Y', action: 'redo' },
            timeline: { icon: '🎬', shortcut: 'Ctrl+Alt+T', action: 'toggleTimeline' }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            const key = this.getShortcutKey(event);
            const control = this.findControlByShortcut(key);
            
            if (control) {
                event.preventDefault();
                this.executeControlAction(control.action);
            }
        });
    }

    getShortcutKey(event) {
        const parts = [];
        if (event.ctrlKey) parts.push('Ctrl');
        if (event.altKey) parts.push('Alt');
        if (event.shiftKey) parts.push('Shift');
        if (event.key !== 'Control' && event.key !== 'Alt' && event.key !== 'Shift') {
            parts.push(event.key === ' ' ? 'Space' : event.key);
        }
        return parts.join('+');
    }

    findControlByShortcut(shortcut) {
        for (const [category, controls] of this.controls) {
            for (const [name, control] of Object.entries(controls)) {
                if (control.shortcut === shortcut) {
                    return { category, name, ...control };
                }
            }
        }
        return null;
    }

    executeControlAction(action) {
        console.log(`Executing action: ${action}`);
        this.dispatchControlEvent(action);
    }

    dispatchControlEvent(eventType, data = null) {
        const event = new CustomEvent('professionalControl', {
            detail: { type: eventType, data }
        });
        document.dispatchEvent(event);
    }

    createControlButton(category, name) {
        const control = this.controls.get(category)?.[name];
        if (!control) return null;

        const button = document.createElement('button');
        button.className = 'professional-control-btn';
        button.title = `${name} (${control.shortcut})`;
        button.innerHTML = `${control.icon} ${name}`;

        button.addEventListener('click', () => {
            this.executeControlAction(control.action);
        });

        return button;
    }

    getControls(category) {
        return this.controls.get(category);
    }
}

export default ProfessionalControls;