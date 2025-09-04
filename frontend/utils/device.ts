/**
 * Device Detection Utilities
 */

export const isMobile = (): boolean => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
};

export const isTablet = (): boolean => {
  return /iPad|Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) && 
         window.innerWidth >= 768;
};

export const isDesktop = (): boolean => {
  return !isMobile() && !isTablet();
};

export const getOS = (): string => {
  const userAgent = navigator.userAgent;
  if (userAgent.indexOf('Win') !== -1) return 'Windows';
  if (userAgent.indexOf('Mac') !== -1) return 'macOS';
  if (userAgent.indexOf('Linux') !== -1) return 'Linux';
  if (userAgent.indexOf('Android') !== -1) return 'Android';
  if (userAgent.indexOf('iOS') !== -1) return 'iOS';
  return 'Unknown';
};

export const getBrowser = (): string => {
  const userAgent = navigator.userAgent;
  if (userAgent.indexOf('Chrome') !== -1) return 'Chrome';
  if (userAgent.indexOf('Firefox') !== -1) return 'Firefox';
  if (userAgent.indexOf('Safari') !== -1) return 'Safari';
  if (userAgent.indexOf('Edge') !== -1) return 'Edge';
  if (userAgent.indexOf('Opera') !== -1) return 'Opera';
  return 'Unknown';
};

export const getScreenSize = (): { width: number; height: number } => {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  };
};

export const getDevicePixelRatio = (): number => {
  return window.devicePixelRatio || 1;
};
