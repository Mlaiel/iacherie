/**
 * Ainflue Desktop - Drag and Drop Manager
 * 
 * Advanced drag and drop system for file uploads and content organization
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * @license Proprietary - Unauthorized use prohibited
 */

class DragDropManager {
    constructor(options = {}) {
        this.container = options.container || document.body;
        this.enableFileUpload = options.enableFileUpload !== false;
        this.enableReordering = options.enableReordering !== false;
        this.enableCrossContainer = options.enableCrossContainer !== false;
        
        this.acceptedFileTypes = options.acceptedFileTypes || [
            'image/*', 'video/*', 'audio/*', 'text/*', 'application/pdf'
        ];
        this.maxFileSize = options.maxFileSize || 100 * 1024 * 1024; // 100MB
        this.maxFiles = options.maxFiles || 50;
        
        this.dragZones = new Map();
        this.dropZones = new Map();
        this.draggedElements = new Set();
        this.uploadQueue = [];
        this.dragState = {
            isDragging: false,
            draggedElement: null,
            startPosition: null,
            currentDropZone: null
        };
        
        this.callbacks = {
            onDragStart: options.onDragStart || (() => {}),
            onDragEnd: options.onDragEnd || (() => {}),
            onDrop: options.onDrop || (() => {}),
            onFileUpload: options.onFileUpload || (() => {}),
            onError: options.onError || ((error) => console.error('Drag & Drop Error:', error))
        };
        
        this.initializeDragDrop();
    }

    /**
     * Initialize drag and drop system
     */
    initializeDragDrop() {
        this.setupGlobalDragListeners();
        this.createDefaultDropZones();
        this.setupStyles();
        
        console.log('🖱️ Drag & Drop Manager initialized');
    }

    /**
     * Setup global drag and drop event listeners
     */
    setupGlobalDragListeners() {
        // Prevent default drag behaviors
        document.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
        });

        document.addEventListener('drop', (e) => {
            e.preventDefault();
            this.handleGlobalDrop(e);
        });

        // Visual feedback for drag operations
        document.addEventListener('dragenter', (e) => {
            e.preventDefault();
            this.handleDragEnter(e);
        });

        document.addEventListener('dragleave', (e) => {
            this.handleDragLeave(e);
        });

        // Touch events for mobile support
        document.addEventListener('touchstart', (e) => {
            this.handleTouchStart(e);
        }, { passive: false });

        document.addEventListener('touchmove', (e) => {
            this.handleTouchMove(e);
        }, { passive: false });

        document.addEventListener('touchend', (e) => {
            this.handleTouchEnd(e);
        });
    }

    /**
     * Create drag zone for elements
     */
    createDragZone(element, options = {}) {
        const zoneId = options.id || this.generateZoneId();
        
        const dragZone = {
            id: zoneId,
            element,
            draggable: true,
            dragData: options.dragData || {},
            dragImage: options.dragImage || null,
            ghostElement: null,
            callbacks: {
                onStart: options.onDragStart || (() => {}),
                onEnd: options.onDragEnd || (() => {})
            }
        };

        // Make element draggable
        element.draggable = true;
        element.setAttribute('data-drag-zone', zoneId);

        // Add drag event listeners
        element.addEventListener('dragstart', (e) => {
            this.handleDragStart(e, dragZone);
        });

        element.addEventListener('dragend', (e) => {
            this.handleDragEnd(e, dragZone);
        });

        // Add visual indicators
        element.classList.add('drag-zone');
        
        // Store drag zone
        this.dragZones.set(zoneId, dragZone);
        
        return zoneId;
    }

    /**
     * Create drop zone for receiving drops
     */
    createDropZone(element, options = {}) {
        const zoneId = options.id || this.generateZoneId();
        
        const dropZone = {
            id: zoneId,
            element,
            acceptTypes: options.acceptTypes || ['*'],
            acceptFiles: options.acceptFiles !== false,
            acceptElements: options.acceptElements !== false,
            validation: options.validation || (() => true),
            callbacks: {
                onDrop: options.onDrop || (() => {}),
                onDragOver: options.onDragOver || (() => {}),
                onDragEnter: options.onDragEnter || (() => {}),
                onDragLeave: options.onDragLeave || (() => {})
            }
        };

        element.setAttribute('data-drop-zone', zoneId);

        // Add drop event listeners
        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.handleDragOver(e, dropZone);
        });

        element.addEventListener('drop', (e) => {
            e.preventDefault();
            this.handleDrop(e, dropZone);
        });

        element.addEventListener('dragenter', (e) => {
            e.preventDefault();
            this.handleDropZoneDragEnter(e, dropZone);
        });

        element.addEventListener('dragleave', (e) => {
            this.handleDropZoneDragLeave(e, dropZone);
        });

        // Add visual indicators
        element.classList.add('drop-zone');
        
        // Store drop zone
        this.dropZones.set(zoneId, dropZone);
        
        return zoneId;
    }

    /**
     * Handle drag start
     */
    handleDragStart(event, dragZone) {
        this.dragState.isDragging = true;
        this.dragState.draggedElement = dragZone;
        this.dragState.startPosition = {
            x: event.clientX,
            y: event.clientY
        };

        // Set drag data
        const dragData = JSON.stringify({
            zoneId: dragZone.id,
            type: 'element',
            data: dragZone.dragData
        });
        
        event.dataTransfer.setData('text/plain', dragData);
        event.dataTransfer.effectAllowed = 'all';

        // Set custom drag image if provided
        if (dragZone.dragImage) {
            event.dataTransfer.setDragImage(dragZone.dragImage, 0, 0);
        } else {
            // Create ghost element
            dragZone.ghostElement = this.createGhostElement(dragZone.element);
            event.dataTransfer.setDragImage(dragZone.ghostElement, 0, 0);
        }

        // Add dragging class
        dragZone.element.classList.add('dragging');
        document.body.classList.add('drag-active');

        // Execute callback
        dragZone.callbacks.onStart(event, dragZone);
        this.callbacks.onDragStart(event, dragZone);
    }

    /**
     * Handle drag end
     */
    handleDragEnd(event, dragZone) {
        this.dragState.isDragging = false;
        this.dragState.draggedElement = null;
        this.dragState.currentDropZone = null;

        // Remove dragging classes
        dragZone.element.classList.remove('dragging');
        document.body.classList.remove('drag-active');

        // Clean up ghost element
        if (dragZone.ghostElement) {
            document.body.removeChild(dragZone.ghostElement);
            dragZone.ghostElement = null;
        }

        // Remove drop zone highlights
        this.clearDropZoneHighlights();

        // Execute callback
        dragZone.callbacks.onEnd(event, dragZone);
        this.callbacks.onDragEnd(event, dragZone);
    }

    /**
     * Handle drag over drop zone
     */
    handleDragOver(event, dropZone) {
        event.preventDefault();
        
        // Determine drop effect
        const dragData = this.parseDragData(event.dataTransfer);
        const canDrop = this.canAcceptDrop(dropZone, dragData, event.dataTransfer);
        
        if (canDrop) {
            event.dataTransfer.dropEffect = 'copy';
            dropZone.element.classList.add('drag-over');
        } else {
            event.dataTransfer.dropEffect = 'none';
        }

        dropZone.callbacks.onDragOver(event, dropZone);
    }

    /**
     * Handle drop on drop zone
     */
    handleDrop(event, dropZone) {
        event.preventDefault();
        
        const files = Array.from(event.dataTransfer.files);
        const dragData = this.parseDragData(event.dataTransfer);
        
        // Remove visual feedback
        dropZone.element.classList.remove('drag-over');
        this.clearDropZoneHighlights();

        // Handle file drops
        if (files.length > 0 && dropZone.acceptFiles) {
            this.handleFileDrop(files, dropZone, event);
        }
        
        // Handle element drops
        if (dragData && dropZone.acceptElements) {
            this.handleElementDrop(dragData, dropZone, event);
        }

        // Execute callback
        dropZone.callbacks.onDrop(event, dropZone, { files, dragData });
        this.callbacks.onDrop(event, dropZone, { files, dragData });
    }

    /**
     * Handle file drops
     */
    async handleFileDrop(files, dropZone, event) {
        try {
            // Validate files
            const validFiles = [];
            const errors = [];

            for (const file of files) {
                const validation = this.validateFile(file);
                if (validation.valid) {
                    validFiles.push(file);
                } else {
                    errors.push({ file: file.name, error: validation.error });
                }
            }

            // Process valid files
            if (validFiles.length > 0) {
                const uploadResults = await this.processFileUploads(validFiles, dropZone);
                
                // Execute file upload callback
                this.callbacks.onFileUpload(validFiles, uploadResults, dropZone);
            }

            // Report errors
            if (errors.length > 0) {
                this.callbacks.onError(new Error(`File validation errors: ${JSON.stringify(errors)}`));
            }

        } catch (error) {
            this.callbacks.onError(error);
        }
    }

    /**
     * Handle element drops
     */
    handleElementDrop(dragData, dropZone, event) {
        try {
            // Validate drop
            if (!this.canAcceptDrop(dropZone, dragData)) {
                throw new Error('Drop not accepted by zone validation');
            }

            // Find source drag zone
            const sourceDragZone = this.dragZones.get(dragData.zoneId);
            
            if (sourceDragZone) {
                // Handle reordering or moving
                if (this.enableReordering || this.enableCrossContainer) {
                    this.handleElementMove(sourceDragZone, dropZone, dragData, event);
                }
            }

        } catch (error) {
            this.callbacks.onError(error);
        }
    }

    /**
     * Handle element movement between zones
     */
    handleElementMove(sourceDragZone, dropZone, dragData, event) {
        const moveOperation = {
            source: sourceDragZone,
            target: dropZone,
            data: dragData,
            event,
            timestamp: new Date().toISOString()
        };

        // Determine drop position
        const dropPosition = this.calculateDropPosition(event, dropZone);
        moveOperation.position = dropPosition;

        // Execute move if cross-container is enabled
        if (this.enableCrossContainer && sourceDragZone.element.parentNode !== dropZone.element) {
            this.executeCrossContainerMove(moveOperation);
        } else if (this.enableReordering && sourceDragZone.element.parentNode === dropZone.element) {
            this.executeReorderMove(moveOperation);
        }
    }

    /**
     * Validate file for upload
     */
    validateFile(file) {
        // Check file size
        if (file.size > this.maxFileSize) {
            return {
                valid: false,
                error: `File size ${this.formatFileSize(file.size)} exceeds maximum ${this.formatFileSize(this.maxFileSize)}`
            };
        }

        // Check file type
        const isAcceptedType = this.acceptedFileTypes.some(type => {
            if (type === '*/*') return true;
            if (type.endsWith('/*')) {
                return file.type.startsWith(type.slice(0, -1));
            }
            return file.type === type;
        });

        if (!isAcceptedType) {
            return {
                valid: false,
                error: `File type ${file.type} is not accepted`
            };
        }

        return { valid: true };
    }

    /**
     * Process file uploads
     */
    async processFileUploads(files, dropZone) {
        const uploadResults = [];

        for (const file of files) {
            try {
                const uploadId = this.generateUploadId();
                const uploadInfo = {
                    id: uploadId,
                    file,
                    progress: 0,
                    status: 'pending',
                    dropZone: dropZone.id,
                    startTime: Date.now()
                };

                this.uploadQueue.push(uploadInfo);

                // Simulate file processing
                const result = await this.simulateFileUpload(uploadInfo);
                uploadResults.push(result);

            } catch (error) {
                uploadResults.push({
                    file: file.name,
                    success: false,
                    error: error.message
                });
            }
        }

        return uploadResults;
    }

    /**
     * Simulate file upload process
     */
    async simulateFileUpload(uploadInfo) {
        return new Promise((resolve) => {
            const file = uploadInfo.file;
            let progress = 0;

            const progressInterval = setInterval(() => {
                progress += 10 + Math.random() * 20;
                uploadInfo.progress = Math.min(100, progress);

                if (uploadInfo.progress >= 100) {
                    clearInterval(progressInterval);
                    uploadInfo.status = 'completed';
                    
                    resolve({
                        file: file.name,
                        size: file.size,
                        type: file.type,
                        success: true,
                        uploadId: uploadInfo.id,
                        duration: Date.now() - uploadInfo.startTime,
                        url: `uploads/${uploadInfo.id}/${file.name}`
                    });
                }
            }, 100);
        });
    }

    /**
     * Utility methods
     */
    createGhostElement(element) {
        const ghost = element.cloneNode(true);
        ghost.style.position = 'absolute';
        ghost.style.top = '-1000px';
        ghost.style.left = '-1000px';
        ghost.style.opacity = '0.5';
        ghost.style.pointerEvents = 'none';
        ghost.style.transform = 'scale(0.8)';
        document.body.appendChild(ghost);
        return ghost;
    }

    createDefaultDropZones() {
        // Create main drop zone if container exists
        if (this.container) {
            this.createDropZone(this.container, {
                id: 'main-drop-zone',
                acceptFiles: true,
                acceptElements: true
            });
        }
    }

    setupStyles() {
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .drag-zone {
                cursor: grab;
                transition: transform 0.2s ease;
            }
            
            .drag-zone:hover {
                transform: scale(1.02);
            }
            
            .drag-zone.dragging {
                opacity: 0.5;
                transform: scale(0.95);
            }
            
            .drop-zone {
                transition: all 0.3s ease;
                border: 2px dashed transparent;
            }
            
            .drop-zone.drag-over {
                border-color: #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
                transform: scale(1.02);
            }
            
            .drop-zone.drag-active {
                border-color: #e5e7eb;
            }
            
            body.drag-active .drop-zone {
                border-style: dashed;
                border-color: #e5e7eb;
            }
            
            .upload-progress {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 16px;
                z-index: 1000;
            }
        `;
        
        document.head.appendChild(styleElement);
    }

    canAcceptDrop(dropZone, dragData, dataTransfer = null) {
        // Check if zone accepts the type
        if (dragData && dragData.type === 'element') {
            if (!dropZone.acceptElements) return false;
            
            // Check accept types
            if (dropZone.acceptTypes.includes('*') || 
                dropZone.acceptTypes.includes(dragData.type)) {
                return dropZone.validation(dragData);
            }
            return false;
        }

        // Check file types if dataTransfer has files
        if (dataTransfer && dataTransfer.files.length > 0) {
            return dropZone.acceptFiles;
        }

        return true;
    }

    parseDragData(dataTransfer) {
        try {
            const data = dataTransfer.getData('text/plain');
            return data ? JSON.parse(data) : null;
        } catch (error) {
            return null;
        }
    }

    clearDropZoneHighlights() {
        this.dropZones.forEach(zone => {
            zone.element.classList.remove('drag-over', 'drag-active');
        });
    }

    calculateDropPosition(event, dropZone) {
        const rect = dropZone.element.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
            relative: {
                x: (event.clientX - rect.left) / rect.width,
                y: (event.clientY - rect.top) / rect.height
            }
        };
    }

    executeCrossContainerMove(moveOperation) {
        // Implement cross-container move logic
        console.log('Cross-container move:', moveOperation);
    }

    executeReorderMove(moveOperation) {
        // Implement reorder logic
        console.log('Reorder move:', moveOperation);
    }

    /**
     * Touch event handlers for mobile support
     */
    handleTouchStart(event) {
        if (event.touches.length === 1) {
            const touch = event.touches[0];
            const element = document.elementFromPoint(touch.clientX, touch.clientY);
            
            if (element && element.classList.contains('drag-zone')) {
                this.touchDragState = {
                    element,
                    startX: touch.clientX,
                    startY: touch.clientY,
                    isDragging: false
                };
            }
        }
    }

    handleTouchMove(event) {
        if (this.touchDragState && event.touches.length === 1) {
            const touch = event.touches[0];
            const deltaX = touch.clientX - this.touchDragState.startX;
            const deltaY = touch.clientY - this.touchDragState.startY;
            
            if (!this.touchDragState.isDragging && 
                (Math.abs(deltaX) > 10 || Math.abs(deltaY) > 10)) {
                this.touchDragState.isDragging = true;
                this.touchDragState.element.classList.add('touch-dragging');
            }
            
            if (this.touchDragState.isDragging) {
                event.preventDefault();
                // Update element position for visual feedback
                this.touchDragState.element.style.transform = 
                    `translate(${deltaX}px, ${deltaY}px)`;
            }
        }
    }

    handleTouchEnd(event) {
        if (this.touchDragState) {
            if (this.touchDragState.isDragging) {
                // Find drop zone under final position
                const finalX = event.changedTouches[0].clientX;
                const finalY = event.changedTouches[0].clientY;
                const dropElement = document.elementFromPoint(finalX, finalY);
                
                // Handle drop if over valid drop zone
                if (dropElement && dropElement.classList.contains('drop-zone')) {
                    // Simulate drop event
                    const dropZoneId = dropElement.getAttribute('data-drop-zone');
                    const dropZone = this.dropZones.get(dropZoneId);
                    
                    if (dropZone) {
                        // Create simulated drop event
                        const dragZoneId = this.touchDragState.element.getAttribute('data-drag-zone');
                        const dragData = { zoneId: dragZoneId, type: 'element' };
                        
                        this.handleElementDrop(dragData, dropZone, {
                            clientX: finalX,
                            clientY: finalY
                        });
                    }
                }
            }
            
            // Reset element position and state
            this.touchDragState.element.style.transform = '';
            this.touchDragState.element.classList.remove('touch-dragging');
            this.touchDragState = null;
        }
    }

    handleDragEnter(event) {
        document.body.classList.add('drag-active');
        this.dropZones.forEach(zone => {
            zone.element.classList.add('drag-active');
        });
    }

    handleDragLeave(event) {
        // Only remove if leaving the document
        if (event.clientX === 0 && event.clientY === 0) {
            document.body.classList.remove('drag-active');
            this.clearDropZoneHighlights();
        }
    }

    handleDropZoneDragEnter(event, dropZone) {
        this.dragState.currentDropZone = dropZone;
        dropZone.callbacks.onDragEnter(event, dropZone);
    }

    handleDropZoneDragLeave(event, dropZone) {
        // Check if really leaving the zone
        const rect = dropZone.element.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right ||
            event.clientY < rect.top || event.clientY > rect.bottom) {
            this.dragState.currentDropZone = null;
            dropZone.callbacks.onDragLeave(event, dropZone);
        }
    }

    handleGlobalDrop(event) {
        // Handle drops outside of designated zones
        if (!this.dragState.currentDropZone && event.dataTransfer.files.length > 0) {
            // Could show upload modal or default handling
            console.log('Files dropped outside drop zones:', event.dataTransfer.files);
        }
    }

    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }

    generateZoneId() {
        return `zone_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    generateUploadId() {
        return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Public API methods
     */
    
    // Remove drag zone
    removeDragZone(zoneId) {
        const zone = this.dragZones.get(zoneId);
        if (zone) {
            zone.element.draggable = false;
            zone.element.classList.remove('drag-zone');
            zone.element.removeAttribute('data-drag-zone');
            this.dragZones.delete(zoneId);
            return true;
        }
        return false;
    }

    // Remove drop zone
    removeDropZone(zoneId) {
        const zone = this.dropZones.get(zoneId);
        if (zone) {
            zone.element.classList.remove('drop-zone');
            zone.element.removeAttribute('data-drop-zone');
            this.dropZones.delete(zoneId);
            return true;
        }
        return false;
    }

    // Get upload queue status
    getUploadStatus() {
        return {
            totalUploads: this.uploadQueue.length,
            pending: this.uploadQueue.filter(u => u.status === 'pending').length,
            inProgress: this.uploadQueue.filter(u => u.status === 'uploading').length,
            completed: this.uploadQueue.filter(u => u.status === 'completed').length,
            failed: this.uploadQueue.filter(u => u.status === 'failed').length
        };
    }

    // Clear upload queue
    clearUploadQueue() {
        this.uploadQueue = [];
    }

    // Get manager statistics
    getStats() {
        return {
            dragZones: this.dragZones.size,
            dropZones: this.dropZones.size,
            uploadsProcessed: this.uploadQueue.length,
            isDragging: this.dragState.isDragging,
            enabledFeatures: {
                fileUpload: this.enableFileUpload,
                reordering: this.enableReordering,
                crossContainer: this.enableCrossContainer
            }
        };
    }

    // Destroy manager
    destroy() {
        // Remove all zones
        this.dragZones.clear();
        this.dropZones.clear();
        
        // Clear upload queue
        this.uploadQueue = [];
        
        // Remove global listeners (would need to store references)
        document.body.classList.remove('drag-active');
        
        console.log('🖱️ Drag & Drop Manager destroyed');
    }
}

module.exports = DragDropManager;

/**
 * Copyright Notice:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized use, copying, or distribution is strictly prohibited.
 * Contact: mlaiel@live.de
 */