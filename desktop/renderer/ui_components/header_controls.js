/**
 * Ainflue Desktop - Header Controls
 * Contrôles header multi-fonctions
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

export class HeaderControls {
    constructor() {
        this.controls = new Map();
        this.header = null;
        this.currentProject = null;
        
        this.initializeControls();
        this.createHeader();
    }

    initializeControls() {
        this.controls.set('workspace', {
            timeline: { icon: '🎬', title: 'Timeline Window (Ctrl+Alt+T)' },
            mixer: { icon: '🎛️', title: 'Audio Mixer (Ctrl+Alt+M)' },
            preview: { icon: '📺', title: 'Preview Monitor (Ctrl+Alt+P)' },
            layout: { icon: '🏗️', title: 'Create Workspace (Ctrl+Shift+W)' }
        });

        this.controls.set('project', {
            new: { icon: '📄', label: 'New Project', shortcut: 'Ctrl+N' },
            open: { icon: '📂', label: 'Open', shortcut: 'Ctrl+O' },
            save: { icon: '💾', label: 'Save', shortcut: 'Ctrl+S' },
            export: { icon: '📤', label: 'Export', shortcut: 'Ctrl+E' }
        });

        this.controls.set('view', {
            fullscreen: { icon: '🖥️', title: 'Toggle Fullscreen (F11)' },
            zoom: { icon: '🔍', title: 'Zoom Controls' },
            grid: { icon: '⊞', title: 'Toggle Grid' },
            rulers: { icon: '📏', title: 'Toggle Rulers' }
        });
    }

    createHeader() {
        let header = document.querySelector('.header');
        if (!header) {
            header = document.createElement('div');
            header.className = 'header';
            header.style.cssText = `
                height: 60px;
                background: rgba(31, 41, 55, 0.9);
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(75, 85, 99, 0.3);
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 20px;
                -webkit-app-region: drag;
                z-index: 1000;
            `;
            
            const container = document.querySelector('.app-container') || document.body;
            container.insertBefore(header, container.firstChild);
        }

        this.header = header;
        this.renderHeader();
    }

    renderHeader() {
        this.header.innerHTML = `
            <div class="header-left" style="
                display: flex;
                align-items: center;
                gap: 20px;
                -webkit-app-region: no-drag;
            ">
                <div class="header-title" style="
                    font-size: 1.2rem;
                    font-weight: 600;
                    color: white;
                ">Professional AI Content Studio</div>
                <div class="project-info" style="
                    font-size: 0.9rem;
                    color: #9CA3AF;
                ">${this.getProjectInfo()}</div>
            </div>

            <div class="header-center" style="
                flex: 1;
                display: flex;
                justify-content: center;
                -webkit-app-region: no-drag;
            ">
                ${this.renderWorkspaceControls()}
            </div>

            <div class="header-right" style="
                display: flex;
                align-items: center;
                gap: 10px;
                -webkit-app-region: no-drag;
            ">
                ${this.renderProjectControls()}
                ${this.renderViewControls()}
            </div>
        `;

        this.setupEventListeners();
    }

    renderWorkspaceControls() {
        const workspaceControls = this.controls.get('workspace');
        return `
            <div class="workspace-controls" style="
                display: flex;
                gap: 8px;
                background: rgba(55, 65, 81, 0.8);
                padding: 6px;
                border-radius: 8px;
                border: 1px solid rgba(75, 85, 99, 0.3);
            ">
                ${Object.entries(workspaceControls).map(([key, control]) => `
                    <button class="control-btn workspace-btn" 
                            data-action="workspace-${key}"
                            title="${control.title}"
                            style="
                        background: transparent;
                        border: none;
                        color: #9CA3AF;
                        padding: 6px 10px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                        transition: all 0.2s;
                    ">${control.icon}</button>
                `).join('')}
            </div>
        `;
    }

    renderProjectControls() {
        const projectControls = this.controls.get('project');
        return `
            <div class="project-controls" style="display: flex; gap: 8px;">
                ${Object.entries(projectControls).map(([key, control]) => `
                    <button class="control-btn project-btn" 
                            data-action="project-${key}"
                            title="${control.label} (${control.shortcut})"
                            style="
                        background: ${key === 'new' ? '#3B82F6' : 'rgba(107, 114, 128, 0.2)'};
                        border: 1px solid ${key === 'new' ? '#3B82F6' : 'rgba(107, 114, 128, 0.3)'};
                        color: white;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 0.9rem;
                        transition: all 0.2s;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    ">
                        <span>${control.icon}</span>
                        <span>${control.label}</span>
                    </button>
                `).join('')}
            </div>
        `;
    }

    renderViewControls() {
        return `
            <div class="view-controls" style="
                display: flex;
                gap: 4px;
                margin-left: 10px;
                padding-left: 10px;
                border-left: 1px solid rgba(75, 85, 99, 0.3);
            ">
                <button class="control-btn view-btn" 
                        data-action="view-fullscreen"
                        title="Toggle Fullscreen (F11)"
                        style="
                    background: transparent;
                    border: none;
                    color: #9CA3AF;
                    padding: 6px 8px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                ">🖥️</button>
                <button class="control-btn view-btn" 
                        data-action="view-settings"
                        title="Settings"
                        style="
                    background: transparent;
                    border: none;
                    color: #9CA3AF;
                    padding: 6px 8px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                ">⚙️</button>
            </div>
        `;
    }

    setupEventListeners() {
        // Workspace controls
        this.header.querySelectorAll('.workspace-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleWorkspaceAction(action);
            });

            btn.addEventListener('mouseenter', () => {
                btn.style.background = 'rgba(59, 130, 246, 0.1)';
                btn.style.color = '#3B82F6';
            });

            btn.addEventListener('mouseleave', () => {
                if (!btn.classList.contains('active')) {
                    btn.style.background = 'transparent';
                    btn.style.color = '#9CA3AF';
                }
            });
        });

        // Project controls
        this.header.querySelectorAll('.project-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleProjectAction(action);
            });

            btn.addEventListener('mouseenter', () => {
                btn.style.transform = 'translateY(-1px)';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.transform = 'translateY(0)';
            });
        });

        // View controls
        this.header.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const action = btn.getAttribute('data-action');
                this.handleViewAction(action);
            });

            btn.addEventListener('mouseenter', () => {
                btn.style.background = 'rgba(59, 130, 246, 0.1)';
                btn.style.color = '#3B82F6';
            });

            btn.addEventListener('mouseleave', () => {
                btn.style.background = 'transparent';
                btn.style.color = '#9CA3AF';
            });
        });
    }

    handleWorkspaceAction(action) {
        const actionType = action.replace('workspace-', '');
        
        switch (actionType) {
            case 'timeline':
                this.toggleWorkspaceButton(action);
                this.dispatchHeaderEvent('toggleTimeline');
                break;
            case 'mixer':
                this.toggleWorkspaceButton(action);
                this.dispatchHeaderEvent('toggleMixer');
                break;
            case 'preview':
                this.toggleWorkspaceButton(action);
                this.dispatchHeaderEvent('togglePreview');
                break;
            case 'layout':
                this.dispatchHeaderEvent('createWorkspaceLayout');
                break;
        }
    }

    handleProjectAction(action) {
        const actionType = action.replace('project-', '');
        
        switch (actionType) {
            case 'new':
                this.dispatchHeaderEvent('newProject');
                break;
            case 'open':
                this.dispatchHeaderEvent('openProject');
                break;
            case 'save':
                this.dispatchHeaderEvent('saveProject');
                break;
            case 'export':
                this.dispatchHeaderEvent('exportProject');
                break;
        }
    }

    handleViewAction(action) {
        const actionType = action.replace('view-', '');
        
        switch (actionType) {
            case 'fullscreen':
                this.toggleFullscreen();
                break;
            case 'settings':
                this.dispatchHeaderEvent('showSettings');
                break;
        }
    }

    toggleWorkspaceButton(action) {
        const btn = this.header.querySelector(`[data-action="${action}"]`);
        if (btn) {
            const isActive = btn.classList.contains('active');
            btn.classList.toggle('active');
            
            if (btn.classList.contains('active')) {
                btn.style.background = '#3B82F6';
                btn.style.color = 'white';
            } else {
                btn.style.background = 'transparent';
                btn.style.color = '#9CA3AF';
            }
        }
    }

    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            document.documentElement.requestFullscreen();
        }
    }

    getProjectInfo() {
        if (this.currentProject) {
            return `Project: ${this.currentProject.name} • Last saved: ${this.formatTime(this.currentProject.lastSaved)}`;
        }
        return 'No project loaded';
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Never';
        const date = new Date(timestamp);
        return date.toLocaleTimeString();
    }

    updateProjectInfo(project) {
        this.currentProject = project;
        const projectInfo = this.header.querySelector('.project-info');
        if (projectInfo) {
            projectInfo.textContent = this.getProjectInfo();
        }
    }

    setTitle(title) {
        const headerTitle = this.header.querySelector('.header-title');
        if (headerTitle) {
            headerTitle.textContent = title;
        }
    }

    showProgress(message) {
        const existingProgress = this.header.querySelector('.progress-indicator');
        if (existingProgress) {
            existingProgress.remove();
        }

        const progress = document.createElement('div');
        progress.className = 'progress-indicator';
        progress.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(59, 130, 246, 0.1);
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #3B82F6;
        `;
        
        progress.innerHTML = `
            <div class="spinner" style="
                width: 12px;
                height: 12px;
                border: 2px solid transparent;
                border-top: 2px solid #3B82F6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
            <span>${message}</span>
        `;

        const headerCenter = this.header.querySelector('.header-center');
        headerCenter.appendChild(progress);
    }

    hideProgress() {
        const progress = this.header.querySelector('.progress-indicator');
        if (progress) {
            progress.remove();
        }
    }

    dispatchHeaderEvent(eventType, data = null) {
        const event = new CustomEvent('headerControl', {
            detail: { type: eventType, data }
        });
        document.dispatchEvent(event);
    }

    // Professional status methods
    showSaving() {
        this.showProgress('Saving project...');
    }

    showExporting() {
        this.showProgress('Exporting content...');
    }

    showProcessing() {
        this.showProgress('Processing...');
    }

    updateWorkspaceState(states) {
        Object.entries(states).forEach(([workspace, active]) => {
            const btn = this.header.querySelector(`[data-action="workspace-${workspace}"]`);
            if (btn) {
                if (active) {
                    btn.classList.add('active');
                    btn.style.background = '#3B82F6';
                    btn.style.color = 'white';
                } else {
                    btn.classList.remove('active');
                    btn.style.background = 'transparent';
                    btn.style.color = '#9CA3AF';
                }
            }
        });
    }
}

// Add spinner animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

export default HeaderControls;