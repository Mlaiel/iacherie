/**
 * Ainflue Desktop - Professional Image Editor
 * 
 * Advanced image editing and manipulation tools for content creators
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

const { EventEmitter } = require('events');

class ImageEditor extends EventEmitter {
  constructor() {
    super();
    this.canvasInstance = null;
    this.currentImage = null;
    this.history = [];
    this.historyIndex = -1;
    this.filters = new Map();
    this.tools = new Map();
    
    this.initializeFilters();
    this.initializeTools();
  }

  /**
   * Initialize image filters
   */
  initializeFilters() {
    this.filters.set('brightness', {
      name: 'Brightness',
      apply: (imageData, value) => this.applyBrightness(imageData, value),
      range: { min: -100, max: 100, default: 0 }
    });

    this.filters.set('contrast', {
      name: 'Contrast',
      apply: (imageData, value) => this.applyContrast(imageData, value),
      range: { min: -100, max: 100, default: 0 }
    });

    this.filters.set('saturation', {
      name: 'Saturation',
      apply: (imageData, value) => this.applySaturation(imageData, value),
      range: { min: -100, max: 100, default: 0 }
    });

    this.filters.set('blur', {
      name: 'Gaussian Blur',
      apply: (imageData, value) => this.applyGaussianBlur(imageData, value),
      range: { min: 0, max: 20, default: 0 }
    });

    this.filters.set('sharpen', {
      name: 'Sharpen',
      apply: (imageData, value) => this.applySharpen(imageData, value),
      range: { min: 0, max: 100, default: 0 }
    });
  }

  /**
   * Initialize editing tools
   */
  initializeTools() {
    this.tools.set('crop', {
      name: 'Crop Tool',
      cursor: 'crosshair',
      onMouseDown: (e) => this.startCrop(e),
      onMouseMove: (e) => this.updateCrop(e),
      onMouseUp: (e) => this.completeCrop(e)
    });

    this.tools.set('brush', {
      name: 'Brush Tool',
      cursor: 'crosshair',
      onMouseDown: (e) => this.startBrush(e),
      onMouseMove: (e) => this.updateBrush(e),
      onMouseUp: (e) => this.completeBrush(e)
    });

    this.tools.set('eraser', {
      name: 'Eraser Tool',
      cursor: 'crosshair',
      onMouseDown: (e) => this.startErase(e),
      onMouseMove: (e) => this.updateErase(e),
      onMouseUp: (e) => this.completeErase(e)
    });

    this.tools.set('text', {
      name: 'Text Tool',
      cursor: 'text',
      onMouseDown: (e) => this.startText(e),
      onKeyDown: (e) => this.updateText(e)
    });
  }

  /**
   * Load image for editing
   */
  async loadImage(imagePath) {
    try {
      // Create canvas and load image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = imagePath;
      });

      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      this.canvasInstance = canvas;
      this.currentImage = img;
      this.saveState();

      this.emit('imageLoaded', {
        width: img.width,
        height: img.height,
        path: imagePath
      });

      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to load image: ${error.message}`));
      return false;
    }
  }

  /**
   * Apply brightness filter
   */
  applyBrightness(imageData, value) {
    const data = imageData.data;
    const adjustment = value * 2.55; // Convert percentage to 0-255 range

    for (let i = 0; i < data.length; i += 4) {
      data[i] = Math.max(0, Math.min(255, data[i] + adjustment));     // Red
      data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + adjustment)); // Green
      data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + adjustment)); // Blue
    }

    return imageData;
  }

  /**
   * Apply contrast filter
   */
  applyContrast(imageData, value) {
    const data = imageData.data;
    const factor = (259 * (value + 255)) / (255 * (259 - value));

    for (let i = 0; i < data.length; i += 4) {
      data[i] = Math.max(0, Math.min(255, factor * (data[i] - 128) + 128));
      data[i + 1] = Math.max(0, Math.min(255, factor * (data[i + 1] - 128) + 128));
      data[i + 2] = Math.max(0, Math.min(255, factor * (data[i + 2] - 128) + 128));
    }

    return imageData;
  }

  /**
   * Apply saturation filter
   */
  applySaturation(imageData, value) {
    const data = imageData.data;
    const factor = (value + 100) / 100;

    for (let i = 0; i < data.length; i += 4) {
      const gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      
      data[i] = Math.max(0, Math.min(255, gray + factor * (data[i] - gray)));
      data[i + 1] = Math.max(0, Math.min(255, gray + factor * (data[i + 1] - gray)));
      data[i + 2] = Math.max(0, Math.min(255, gray + factor * (data[i + 2] - gray)));
    }

    return imageData;
  }

  /**
   * Apply gaussian blur filter
   */
  applyGaussianBlur(imageData, radius) {
    if (radius === 0) return imageData;

    const width = imageData.width;
    const height = imageData.height;
    const data = new Uint8ClampedArray(imageData.data);

    // Horizontal pass
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4;
        let r = 0, g = 0, b = 0, weight = 0;

        for (let dx = -radius; dx <= radius; dx++) {
          const nx = Math.max(0, Math.min(width - 1, x + dx));
          const nidx = (y * width + nx) * 4;
          const w = Math.exp(-(dx * dx) / (2 * radius * radius));

          r += data[nidx] * w;
          g += data[nidx + 1] * w;
          b += data[nidx + 2] * w;
          weight += w;
        }

        imageData.data[idx] = r / weight;
        imageData.data[idx + 1] = g / weight;
        imageData.data[idx + 2] = b / weight;
      }
    }

    return imageData;
  }

  /**
   * Apply sharpen filter
   */
  applySharpen(imageData, amount) {
    if (amount === 0) return imageData;

    const width = imageData.width;
    const height = imageData.height;
    const data = new Uint8ClampedArray(imageData.data);
    const factor = amount / 100;

    const kernel = [
      0, -factor, 0,
      -factor, 1 + 4 * factor, -factor,
      0, -factor, 0
    ];

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const idx = (y * width + x) * 4;
        let r = 0, g = 0, b = 0;

        for (let ky = 0; ky < 3; ky++) {
          for (let kx = 0; kx < 3; kx++) {
            const nidx = ((y + ky - 1) * width + (x + kx - 1)) * 4;
            const k = kernel[ky * 3 + kx];

            r += data[nidx] * k;
            g += data[nidx + 1] * k;
            b += data[nidx + 2] * k;
          }
        }

        imageData.data[idx] = Math.max(0, Math.min(255, r));
        imageData.data[idx + 1] = Math.max(0, Math.min(255, g));
        imageData.data[idx + 2] = Math.max(0, Math.min(255, b));
      }
    }

    return imageData;
  }

  /**
   * Crop image to specified dimensions
   */
  cropImage(x, y, width, height) {
    if (!this.canvasInstance) return false;

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = width;
    canvas.height = height;

    ctx.drawImage(this.canvasInstance, x, y, width, height, 0, 0, width, height);
    
    this.canvasInstance = canvas;
    this.saveState();
    
    this.emit('imageCropped', { x, y, width, height });
    return true;
  }

  /**
   * Resize image
   */
  resizeImage(newWidth, newHeight, maintainAspectRatio = true) {
    if (!this.canvasInstance) return false;

    const currentWidth = this.canvasInstance.width;
    const currentHeight = this.canvasInstance.height;

    if (maintainAspectRatio) {
      const aspectRatio = currentWidth / currentHeight;
      if (newWidth / newHeight > aspectRatio) {
        newWidth = newHeight * aspectRatio;
      } else {
        newHeight = newWidth / aspectRatio;
      }
    }

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = newWidth;
    canvas.height = newHeight;

    // Use high-quality scaling
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    ctx.drawImage(this.canvasInstance, 0, 0, newWidth, newHeight);
    
    this.canvasInstance = canvas;
    this.saveState();
    
    this.emit('imageResized', { width: newWidth, height: newHeight });
    return true;
  }

  /**
   * Save current state for undo/redo
   */
  saveState() {
    if (!this.canvasInstance) return;

    // Remove future history if we're not at the end
    if (this.historyIndex < this.history.length - 1) {
      this.history = this.history.slice(0, this.historyIndex + 1);
    }

    // Add current state
    this.history.push(this.canvasInstance.toDataURL());
    this.historyIndex++;

    // Limit history size
    if (this.history.length > 50) {
      this.history.shift();
      this.historyIndex--;
    }

    this.emit('stateChanged', {
      canUndo: this.canUndo(),
      canRedo: this.canRedo()
    });
  }

  /**
   * Undo last action
   */
  undo() {
    if (!this.canUndo()) return false;

    this.historyIndex--;
    return this.restoreState(this.history[this.historyIndex]);
  }

  /**
   * Redo last undone action
   */
  redo() {
    if (!this.canRedo()) return false;

    this.historyIndex++;
    return this.restoreState(this.history[this.historyIndex]);
  }

  /**
   * Check if undo is possible
   */
  canUndo() {
    return this.historyIndex > 0;
  }

  /**
   * Check if redo is possible
   */
  canRedo() {
    return this.historyIndex < this.history.length - 1;
  }

  /**
   * Restore state from history
   */
  async restoreState(dataUrl) {
    try {
      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = dataUrl;
      });

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      
      this.canvasInstance = canvas;
      
      this.emit('stateRestored', {
        canUndo: this.canUndo(),
        canRedo: this.canRedo()
      });

      return true;
    } catch (error) {
      this.emit('error', new Error(`Failed to restore state: ${error.message}`));
      return false;
    }
  }

  /**
   * Export image
   */
  exportImage(format = 'png', quality = 0.9) {
    if (!this.canvasInstance) return null;

    try {
      const mimeType = `image/${format}`;
      const dataUrl = this.canvasInstance.toDataURL(mimeType, quality);
      
      this.emit('imageExported', { format, quality, dataUrl });
      return dataUrl;
    } catch (error) {
      this.emit('error', new Error(`Failed to export image: ${error.message}`));
      return null;
    }
  }

  /**
   * Get available filters
   */
  getAvailableFilters() {
    return Array.from(this.filters.entries()).map(([key, filter]) => ({
      id: key,
      name: filter.name,
      range: filter.range
    }));
  }

  /**
   * Get available tools
   */
  getAvailableTools() {
    return Array.from(this.tools.entries()).map(([key, tool]) => ({
      id: key,
      name: tool.name,
      cursor: tool.cursor
    }));
  }

  /**
   * Apply filter to current image
   */
  applyFilter(filterId, value) {
    if (!this.canvasInstance || !this.filters.has(filterId)) return false;

    const ctx = this.canvasInstance.getContext('2d');
    const imageData = ctx.getImageData(0, 0, this.canvasInstance.width, this.canvasInstance.height);
    
    const filter = this.filters.get(filterId);
    filter.apply(imageData, value);
    
    ctx.putImageData(imageData, 0, 0);
    this.saveState();
    
    this.emit('filterApplied', { filterId, value });
    return true;
  }
}

module.exports = ImageEditor;