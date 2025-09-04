/**
 * Image Processing Library
 */

interface ImageProcessingOptions {
  quality?: number;
  format?: 'jpeg' | 'png' | 'webp';
  width?: number;
  height?: number;
  maintainAspectRatio?: boolean;
}

class ImageProcessor {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;

  constructor() {
    this.canvas = document.createElement('canvas');
    this.ctx = this.canvas.getContext('2d')!;
  }

  async resize(file: File, options: ImageProcessingOptions): Promise<Blob> {
    const image = await this.loadImage(file);
    const { width, height } = this.calculateDimensions(
      image.width,
      image.height,
      options.width,
      options.height,
      options.maintainAspectRatio ?? true
    );

    this.canvas.width = width;
    this.canvas.height = height;

    this.ctx.drawImage(image, 0, 0, width, height);

    return new Promise((resolve) => {
      this.canvas.toBlob(
        (blob) => resolve(blob!),
        `image/${options.format || 'jpeg'}`,
        options.quality || 0.8
      );
    });
  }

  async crop(file: File, x: number, y: number, width: number, height: number): Promise<Blob> {
    const image = await this.loadImage(file);
    
    this.canvas.width = width;
    this.canvas.height = height;

    this.ctx.drawImage(image, x, y, width, height, 0, 0, width, height);

    return new Promise((resolve) => {
      this.canvas.toBlob((blob) => resolve(blob!), 'image/png');
    });
  }

  async rotate(file: File, degrees: number): Promise<Blob> {
    const image = await this.loadImage(file);
    const radians = (degrees * Math.PI) / 180;
    
    // Calculate new canvas size after rotation
    const cos = Math.abs(Math.cos(radians));
    const sin = Math.abs(Math.sin(radians));
    const newWidth = image.width * cos + image.height * sin;
    const newHeight = image.width * sin + image.height * cos;

    this.canvas.width = newWidth;
    this.canvas.height = newHeight;

    // Translate to center and rotate
    this.ctx.translate(newWidth / 2, newHeight / 2);
    this.ctx.rotate(radians);
    this.ctx.drawImage(image, -image.width / 2, -image.height / 2);

    return new Promise((resolve) => {
      this.canvas.toBlob((blob) => resolve(blob!), 'image/png');
    });
  }

  async applyFilter(file: File, filter: 'grayscale' | 'sepia' | 'blur' | 'brightness' | 'contrast'): Promise<Blob> {
    const image = await this.loadImage(file);
    
    this.canvas.width = image.width;
    this.canvas.height = image.height;

    // Apply CSS filter
    switch (filter) {
      case 'grayscale':
        this.ctx.filter = 'grayscale(100%)';
        break;
      case 'sepia':
        this.ctx.filter = 'sepia(100%)';
        break;
      case 'blur':
        this.ctx.filter = 'blur(2px)';
        break;
      case 'brightness':
        this.ctx.filter = 'brightness(1.2)';
        break;
      case 'contrast':
        this.ctx.filter = 'contrast(1.2)';
        break;
    }

    this.ctx.drawImage(image, 0, 0);

    return new Promise((resolve) => {
      this.canvas.toBlob((blob) => resolve(blob!), 'image/png');
    });
  }

  private async loadImage(file: File): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = reject;
      image.src = URL.createObjectURL(file);
    });
  }

  private calculateDimensions(
    originalWidth: number,
    originalHeight: number,
    targetWidth?: number,
    targetHeight?: number,
    maintainAspectRatio = true
  ): { width: number; height: number } {
    if (!targetWidth && !targetHeight) {
      return { width: originalWidth, height: originalHeight };
    }

    if (!maintainAspectRatio) {
      return {
        width: targetWidth || originalWidth,
        height: targetHeight || originalHeight,
      };
    }

    const aspectRatio = originalWidth / originalHeight;

    if (targetWidth && targetHeight) {
      const targetAspectRatio = targetWidth / targetHeight;
      if (aspectRatio > targetAspectRatio) {
        return { width: targetWidth, height: targetWidth / aspectRatio };
      } else {
        return { width: targetHeight * aspectRatio, height: targetHeight };
      }
    }

    if (targetWidth) {
      return { width: targetWidth, height: targetWidth / aspectRatio };
    }

    if (targetHeight) {
      return { width: targetHeight * aspectRatio, height: targetHeight };
    }

    return { width: originalWidth, height: originalHeight };
  }
}

export { ImageProcessor };
export default ImageProcessor;
