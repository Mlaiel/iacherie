/**
 * @fileoverview Watermark Engine - Advanced Content Watermarking System
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 * @module services/watermark_engine
 * @description Professional watermarking system with visible and invisible watermarks for content protection
 */

class WatermarkEngine {
  constructor() {
    this.watermarkTemplates = new Map();
    this.processingQueue = new Map();
    this.watermarkHistory = new Map();
    
    this.config = {
      enableVisibleWatermarks: true,
      enableInvisibleWatermarks: true,
      enableSteganography: true,
      defaultOpacity: 0.3,
      defaultPosition: 'bottom-right',
      defaultSize: 'medium',
      qualityPreservation: 'high',
      compressionResistance: true,
      batchProcessing: true
    };

    this.watermarkTypes = {
      text: 'text_watermark',
      logo: 'logo_watermark',
      invisible: 'invisible_watermark',
      steganographic: 'steganographic_watermark',
      frequency: 'frequency_watermark',
      digital: 'digital_signature'
    };

    this.positions = {
      'top-left': { x: 0.05, y: 0.05 },
      'top-center': { x: 0.5, y: 0.05 },
      'top-right': { x: 0.95, y: 0.05 },
      'center-left': { x: 0.05, y: 0.5 },
      'center': { x: 0.5, y: 0.5 },
      'center-right': { x: 0.95, y: 0.5 },
      'bottom-left': { x: 0.05, y: 0.95 },
      'bottom-center': { x: 0.5, y: 0.95 },
      'bottom-right': { x: 0.95, y: 0.95 }
    };

    this.sizes = {
      small: 0.1,
      medium: 0.15,
      large: 0.2,
      xlarge: 0.25
    };

    this.initializeEngine();
    console.log('Watermark Engine initialized');
  }

  /**
   * Initialize watermark engine
   */
  initializeEngine() {
    this.setupDefaultTemplates();
    this.setupCanvasProcessor();
    this.setupAudioProcessor();
    this.setupVideoProcessor();
    this.setupSteganography();
  }

  /**
   * Setup default watermark templates
   */
  setupDefaultTemplates() {
    // Text watermark templates
    this.registerTemplate('copyright_text', {
      type: 'text',
      text: '© {year} {owner}. All rights reserved.',
      font: 'Arial, sans-serif',
      fontSize: 16,
      color: '#ffffff',
      backgroundColor: 'rgba(0, 0, 0, 0.7)',
      padding: 8,
      borderRadius: 4
    });

    this.registerTemplate('creator_text', {
      type: 'text',
      text: 'Created by {creator}',
      font: 'Arial, sans-serif',
      fontSize: 14,
      color: '#ffffff',
      style: 'bold'
    });

    this.registerTemplate('website_text', {
      type: 'text',
      text: '{website}',
      font: 'Arial, sans-serif',
      fontSize: 12,
      color: '#cccccc'
    });

    // Logo watermark template
    this.registerTemplate('logo_standard', {
      type: 'logo',
      logoPath: null, // To be set by user
      size: 'medium',
      opacity: 0.7,
      blendMode: 'overlay'
    });

    // Invisible watermark template
    this.registerTemplate('invisible_standard', {
      type: 'invisible',
      algorithm: 'lsb',
      strength: 'medium',
      redundancy: 3,
      errorCorrection: true
    });
  }

  /**
   * Setup canvas processor for image/video watermarking
   */
  setupCanvasProcessor() {
    this.canvasProcessor = {
      createCanvas: (width, height) => {
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        return canvas;
      },
      
      getContext: (canvas) => {
        return canvas.getContext('2d');
      },
      
      loadImage: (src) => {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = src;
        });
      }
    };
  }

  /**
   * Setup audio processor for audio watermarking
   */
  setupAudioProcessor() {
    this.audioProcessor = {
      context: null,
      
      initialize: () => {
        try {
          this.audioProcessor.context = new (window.AudioContext || window.webkitAudioContext)();
          return true;
        } catch (error) {
          console.warn('Audio context not available:', error);
          return false;
        }
      },
      
      processBuffer: async (audioBuffer, watermarkData) => {
        // Audio watermarking implementation would go here
        return audioBuffer;
      }
    };
    
    this.audioProcessor.initialize();
  }

  /**
   * Setup video processor
   */
  setupVideoProcessor() {
    this.videoProcessor = {
      processFrame: async (imageData, watermarkOptions) => {
        // Video frame watermarking
        return this.applyImageWatermark(imageData, watermarkOptions);
      },
      
      processVideo: async (videoElement, watermarkOptions) => {
        // Video watermarking implementation
        return videoElement;
      }
    };
  }

  /**
   * Setup steganography capabilities
   */
  setupSteganography() {
    this.steganography = {
      // LSB (Least Significant Bit) steganography
      embedLSB: (imageData, message) => {
        const data = imageData.data;
        const messageBytes = new TextEncoder().encode(message);
        const messageBits = this.bytesToBits(messageBytes);
        
        // Embed message length first
        const lengthBits = this.numberToBits(messageBits.length, 32);
        const allBits = [...lengthBits, ...messageBits];
        
        // Embed bits into LSB of red channel
        for (let i = 0; i < allBits.length && i * 4 < data.length; i++) {
          data[i * 4] = (data[i * 4] & 0xFE) | allBits[i];
        }
        
        return imageData;
      },
      
      extractLSB: (imageData) => {
        const data = imageData.data;
        
        // Extract message length
        const lengthBits = [];
        for (let i = 0; i < 32 && i * 4 < data.length; i++) {
          lengthBits.push(data[i * 4] & 1);
        }
        const messageLength = this.bitsToNumber(lengthBits);
        
        if (messageLength <= 0 || messageLength > data.length / 4) {
          throw new Error('Invalid message length');
        }
        
        // Extract message bits
        const messageBits = [];
        for (let i = 32; i < 32 + messageLength && i * 4 < data.length; i++) {
          messageBits.push(data[i * 4] & 1);
        }
        
        const messageBytes = this.bitsToBytes(messageBits);
        return new TextDecoder().decode(new Uint8Array(messageBytes));
      }
    };
  }

  /**
   * Apply watermark to content
   */
  async applyWatermark(file, watermarkOptions = {}) {
    const watermarkId = this.generateWatermarkId();
    const startTime = Date.now();

    try {
      // Determine content type
      const contentType = this.getContentType(file);
      if (!contentType) {
        throw new Error('Unsupported content type');
      }

      // Normalize options
      const options = this.normalizeWatermarkOptions(watermarkOptions);

      // Create processing job
      const job = {
        id: watermarkId,
        file,
        contentType,
        options,
        startTime,
        status: 'processing'
      };

      this.processingQueue.set(watermarkId, job);

      // Apply appropriate watermarking method
      let result;
      switch (contentType) {
        case 'image':
          result = await this.applyImageWatermark(file, options);
          break;
        case 'video':
          result = await this.applyVideoWatermark(file, options);
          break;
        case 'audio':
          result = await this.applyAudioWatermark(file, options);
          break;
        default:
          throw new Error(`Watermarking not supported for ${contentType}`);
      }

      // Store watermark history
      this.watermarkHistory.set(watermarkId, {
        originalFile: file.name,
        watermarkType: options.type,
        timestamp: Date.now(),
        options: options
      });

      job.status = 'completed';
      job.result = result;
      job.processingTime = Date.now() - startTime;

      return {
        success: true,
        watermarkId,
        result,
        processingTime: job.processingTime
      };

    } catch (error) {
      console.error('Watermarking failed:', error);
      return {
        success: false,
        watermarkId,
        error: error.message,
        processingTime: Date.now() - startTime
      };
    } finally {
      this.processingQueue.delete(watermarkId);
    }
  }

  /**
   * Apply watermark to image
   */
  async applyImageWatermark(file, options) {
    const img = await this.loadImage(file);
    const canvas = this.canvasProcessor.createCanvas(img.width, img.height);
    const ctx = this.canvasProcessor.getContext(canvas);

    // Draw original image
    ctx.drawImage(img, 0, 0);

    // Apply watermark based on type
    switch (options.type) {
      case 'text':
        await this.applyTextWatermark(ctx, canvas.width, canvas.height, options);
        break;
      case 'logo':
        await this.applyLogoWatermark(ctx, canvas.width, canvas.height, options);
        break;
      case 'invisible':
        await this.applyInvisibleWatermark(ctx, canvas, options);
        break;
    }

    // Convert to blob
    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob);
      }, file.type || 'image/png', options.quality || 0.9);
    });
  }

  /**
   * Apply text watermark
   */
  async applyTextWatermark(ctx, width, height, options) {
    const template = this.watermarkTemplates.get(options.template) || {};
    const text = this.interpolateText(options.text || template.text || '', options.variables || {});
    
    // Configure text style
    ctx.save();
    ctx.globalAlpha = options.opacity || this.config.defaultOpacity;
    ctx.font = `${options.fontSize || template.fontSize || 16}px ${options.font || template.font || 'Arial'}`;
    ctx.fillStyle = options.color || template.color || '#ffffff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // Add background if specified
    if (options.backgroundColor || template.backgroundColor) {
      const metrics = ctx.measureText(text);
      const padding = options.padding || template.padding || 8;
      const position = this.calculatePosition(width, height, options.position);
      
      ctx.fillStyle = options.backgroundColor || template.backgroundColor;
      ctx.fillRect(
        position.x - metrics.width / 2 - padding,
        position.y - parseInt(ctx.font) / 2 - padding,
        metrics.width + padding * 2,
        parseInt(ctx.font) + padding * 2
      );
    }

    // Draw text
    const position = this.calculatePosition(width, height, options.position);
    ctx.fillStyle = options.color || template.color || '#ffffff';
    ctx.fillText(text, position.x, position.y);
    
    ctx.restore();
  }

  /**
   * Apply logo watermark
   */
  async applyLogoWatermark(ctx, width, height, options) {
    if (!options.logoFile && !options.logoUrl) {
      throw new Error('Logo file or URL required for logo watermark');
    }

    const logo = await this.loadImage(options.logoFile || options.logoUrl);
    const size = this.sizes[options.size] || this.sizes.medium;
    const logoSize = Math.min(width, height) * size;
    const aspectRatio = logo.width / logo.height;
    
    let logoWidth, logoHeight;
    if (aspectRatio > 1) {
      logoWidth = logoSize;
      logoHeight = logoSize / aspectRatio;
    } else {
      logoWidth = logoSize * aspectRatio;
      logoHeight = logoSize;
    }

    const position = this.calculatePosition(width, height, options.position);
    
    ctx.save();
    ctx.globalAlpha = options.opacity || this.config.defaultOpacity;
    ctx.globalCompositeOperation = options.blendMode || 'source-over';
    
    ctx.drawImage(
      logo,
      position.x - logoWidth / 2,
      position.y - logoHeight / 2,
      logoWidth,
      logoHeight
    );
    
    ctx.restore();
  }

  /**
   * Apply invisible watermark using steganography
   */
  async applyInvisibleWatermark(ctx, canvas, options) {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const message = options.message || options.text || `Watermarked by ${options.owner || 'Ainflue'} at ${new Date().toISOString()}`;
    
    const watermarkedData = this.steganography.embedLSB(imageData, message);
    ctx.putImageData(watermarkedData, 0, 0);
  }

  /**
   * Apply watermark to video
   */
  async applyVideoWatermark(file, options) {
    // Video watermarking is more complex and would typically require:
    // 1. Frame extraction
    // 2. Watermark application to each frame
    // 3. Video reconstruction
    // For now, return a placeholder
    
    console.log('Video watermarking initiated for:', file.name);
    return file; // Placeholder
  }

  /**
   * Apply watermark to audio
   */
  async applyAudioWatermark(file, options) {
    if (!this.audioProcessor.context) {
      throw new Error('Audio processing not available');
    }

    // Audio watermarking implementation would go here
    // This could include:
    // 1. Frequency domain watermarking
    // 2. Time domain watermarking
    // 3. Spread spectrum techniques
    
    console.log('Audio watermarking initiated for:', file.name);
    return file; // Placeholder
  }

  /**
   * Extract watermark from content
   */
  async extractWatermark(file, extractionOptions = {}) {
    try {
      const contentType = this.getContentType(file);
      
      switch (contentType) {
        case 'image':
          return await this.extractImageWatermark(file, extractionOptions);
        case 'video':
          return await this.extractVideoWatermark(file, extractionOptions);
        case 'audio':
          return await this.extractAudioWatermark(file, extractionOptions);
        default:
          throw new Error(`Watermark extraction not supported for ${contentType}`);
      }
    } catch (error) {
      console.error('Watermark extraction failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Extract watermark from image
   */
  async extractImageWatermark(file, options) {
    const img = await this.loadImage(file);
    const canvas = this.canvasProcessor.createCanvas(img.width, img.height);
    const ctx = this.canvasProcessor.getContext(canvas);
    
    ctx.drawImage(img, 0, 0);
    
    try {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const extractedMessage = this.steganography.extractLSB(imageData);
      
      return {
        success: true,
        type: 'invisible',
        message: extractedMessage,
        extractedAt: new Date().toISOString()
      };
    } catch (error) {
      return {
        success: false,
        error: 'No watermark found or extraction failed'
      };
    }
  }

  /**
   * Extract watermark from video
   */
  async extractVideoWatermark(file, options) {
    // Video watermark extraction placeholder
    return {
      success: false,
      error: 'Video watermark extraction not yet implemented'
    };
  }

  /**
   * Extract watermark from audio
   */
  async extractAudioWatermark(file, options) {
    // Audio watermark extraction placeholder
    return {
      success: false,
      error: 'Audio watermark extraction not yet implemented'
    };
  }

  /**
   * Helper methods
   */
  getContentType(file) {
    const mimeType = file.type;
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    return null;
  }

  async loadImage(file) {
    const url = file instanceof File ? URL.createObjectURL(file) : file;
    
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        if (file instanceof File) {
          URL.revokeObjectURL(url);
        }
        resolve(img);
      };
      img.onerror = () => {
        if (file instanceof File) {
          URL.revokeObjectURL(url);
        }
        reject(new Error('Failed to load image'));
      };
      img.src = url;
    });
  }

  normalizeWatermarkOptions(options) {
    return {
      type: options.type || 'text',
      position: options.position || this.config.defaultPosition,
      size: options.size || this.config.defaultSize,
      opacity: options.opacity || this.config.defaultOpacity,
      template: options.template || 'copyright_text',
      variables: options.variables || {},
      ...options
    };
  }

  calculatePosition(width, height, position) {
    const pos = this.positions[position] || this.positions['bottom-right'];
    return {
      x: width * pos.x,
      y: height * pos.y
    };
  }

  interpolateText(text, variables) {
    let interpolated = text;
    
    // Default variables
    const defaultVars = {
      year: new Date().getFullYear(),
      date: new Date().toLocaleDateString(),
      time: new Date().toLocaleTimeString()
    };
    
    const allVars = { ...defaultVars, ...variables };
    
    for (const [key, value] of Object.entries(allVars)) {
      interpolated = interpolated.replace(new RegExp(`{${key}}`, 'g'), value);
    }
    
    return interpolated;
  }

  // Steganography helper methods
  bytesToBits(bytes) {
    const bits = [];
    for (const byte of bytes) {
      for (let i = 7; i >= 0; i--) {
        bits.push((byte >> i) & 1);
      }
    }
    return bits;
  }

  bitsToBytes(bits) {
    const bytes = [];
    for (let i = 0; i < bits.length; i += 8) {
      let byte = 0;
      for (let j = 0; j < 8 && i + j < bits.length; j++) {
        byte = (byte << 1) | bits[i + j];
      }
      bytes.push(byte);
    }
    return bytes;
  }

  numberToBits(number, bitCount) {
    const bits = [];
    for (let i = bitCount - 1; i >= 0; i--) {
      bits.push((number >> i) & 1);
    }
    return bits;
  }

  bitsToNumber(bits) {
    let number = 0;
    for (const bit of bits) {
      number = (number << 1) | bit;
    }
    return number;
  }

  /**
   * Register watermark template
   */
  registerTemplate(name, template) {
    this.watermarkTemplates.set(name, template);
  }

  /**
   * Get watermark template
   */
  getTemplate(name) {
    return this.watermarkTemplates.get(name);
  }

  /**
   * Generate watermark ID
   */
  generateWatermarkId() {
    return `wm_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get watermark history
   */
  getWatermarkHistory(limit = 50) {
    const entries = Array.from(this.watermarkHistory.entries());
    return entries
      .sort((a, b) => b[1].timestamp - a[1].timestamp)
      .slice(0, limit)
      .map(([id, data]) => ({ id, ...data }));
  }

  /**
   * Get processing statistics
   */
  getStatistics() {
    return {
      templatesRegistered: this.watermarkTemplates.size,
      activeJobs: this.processingQueue.size,
      historyEntries: this.watermarkHistory.size,
      supportedTypes: Object.keys(this.watermarkTypes),
      availablePositions: Object.keys(this.positions),
      availableSizes: Object.keys(this.sizes)
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * Cleanup resources
   */
  cleanup() {
    this.processingQueue.clear();
    this.watermarkHistory.clear();
    
    if (this.audioProcessor.context) {
      this.audioProcessor.context.close();
    }
    
    console.log('Watermark Engine cleaned up');
  }
}

// Create and export singleton instance
const watermarkEngine = new WatermarkEngine();

// Export both class and instance
window.WatermarkEngine = WatermarkEngine;
window.watermarkEngine = watermarkEngine;

export { WatermarkEngine, watermarkEngine };
export default watermarkEngine;