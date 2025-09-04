/**
 * Color Utilities
 */

export const hexToRgb = (hex: string): { r: number; g: number; b: number } | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

export const rgbToHex = (r: number, g: number, b: number): string => {
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
};

export const getContrastColor = (hex: string): string => {
  const rgb = hexToRgb(hex);
  if (!rgb) return '#000000';
  
  const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
  return brightness > 128 ? '#000000' : '#ffffff';
};

export const lightenColor = (hex: string, percent: number): string => {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  const factor = 1 + percent / 100;
  const r = Math.min(255, Math.floor(rgb.r * factor));
  const g = Math.min(255, Math.floor(rgb.g * factor));
  const b = Math.min(255, Math.floor(rgb.b * factor));
  
  return rgbToHex(r, g, b);
};

export const darkenColor = (hex: string, percent: number): string => {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  
  const factor = 1 - percent / 100;
  const r = Math.floor(rgb.r * factor);
  const g = Math.floor(rgb.g * factor);
  const b = Math.floor(rgb.b * factor);
  
  return rgbToHex(r, g, b);
};
