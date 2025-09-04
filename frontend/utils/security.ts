/**
 * Security Utilities
 */

export const sanitizeHtml = (html: string): string => {
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
};

export const escapeHtml = (text: string): string => {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
};

export const validateCSRFToken = (token: string, expected: string): boolean => {
  if (token.length !== expected.length) return false;
  
  let result = 0;
  for (let i = 0; i < token.length; i++) {
    result |= token.charCodeAt(i) ^ expected.charCodeAt(i);
  }
  return result === 0;
};

export const generateNonce = (length = 16): string => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

export const isValidBase64 = (str: string): boolean => {
  try {
    return btoa(atob(str)) === str;
  } catch {
    return false;
  }
};

export const sanitizeFilename = (filename: string): string => {
  return filename
    .replace(/[^a-zA-Z0-9.-]/g, '_')
    .replace(/_{2,}/g, '_')
    .replace(/^_|_$/g, '');
};

export const validateOrigin = (origin: string, allowedOrigins: string[]): boolean => {
  return allowedOrigins.includes(origin);
};

export const maskSensitiveData = (data: string, visibleChars = 4): string => {
  if (data.length <= visibleChars) return '*'.repeat(data.length);
  
  const visible = data.slice(-visibleChars);
  const masked = '*'.repeat(data.length - visibleChars);
  return masked + visible;
};
