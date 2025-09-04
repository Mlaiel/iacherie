/**
 * Browser Utilities
 */

export const getBrowserInfo = () => {
  const userAgent = navigator.userAgent;
  
  const browsers = [
    { name: 'Edge', regex: /Edge\/(\d+)/ },
    { name: 'Chrome', regex: /Chrome\/(\d+)/ },
    { name: 'Firefox', regex: /Firefox\/(\d+)/ },
    { name: 'Safari', regex: /Safari\/(\d+)/ },
    { name: 'Opera', regex: /Opera\/(\d+)/ },
  ];
  
  for (const browser of browsers) {
    const match = userAgent.match(browser.regex);
    if (match) {
      return {
        name: browser.name,
        version: parseInt(match[1]),
        userAgent,
      };
    }
  }
  
  return { name: 'Unknown', version: 0, userAgent };
};

export const supportsFeature = (feature: string): boolean => {
  const features: Record<string, () => boolean> = {
    webgl: () => {
      try {
        const canvas = document.createElement('canvas');
        return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
      } catch {
        return false;
      }
    },
    webrtc: () => !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    serviceWorker: () => 'serviceWorker' in navigator,
    webWorker: () => typeof Worker !== 'undefined',
    localStorage: () => {
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
        return true;
      } catch {
        return false;
      }
    },
    sessionStorage: () => {
      try {
        sessionStorage.setItem('test', 'test');
        sessionStorage.removeItem('test');
        return true;
      } catch {
        return false;
      }
    },
    indexedDB: () => 'indexedDB' in window,
    webAssembly: () => 'WebAssembly' in window,
    pushNotifications: () => 'Notification' in window && 'PushManager' in window,
  };
  
  return features[feature]?.() || false;
};

export const getConnectionInfo = () => {
  const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
  
  if (!connection) {
    return { type: 'unknown', speed: 'unknown' };
  }
  
  return {
    type: connection.effectiveType || 'unknown',
    speed: connection.downlink || 'unknown',
    rtt: connection.rtt || 'unknown',
  };
};

export const requestFullscreen = (element: HTMLElement = document.documentElement): Promise<void> => {
  const requestMethod = element.requestFullscreen ||
    (element as any).webkitRequestFullscreen ||
    (element as any).mozRequestFullScreen ||
    (element as any).msRequestFullscreen;
    
  if (requestMethod) {
    return requestMethod.call(element);
  }
  
  return Promise.reject(new Error('Fullscreen not supported'));
};

export const exitFullscreen = (): Promise<void> => {
  const exitMethod = document.exitFullscreen ||
    (document as any).webkitExitFullscreen ||
    (document as any).mozCancelFullScreen ||
    (document as any).msExitFullscreen;
    
  if (exitMethod) {
    return exitMethod.call(document);
  }
  
  return Promise.reject(new Error('Exit fullscreen not supported'));
};
