/**
 * Storage Utilities
 */

export const setItem = (key: string, value: any): boolean => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    return false;
  }
};

export const getItem = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch {
    return defaultValue;
  }
};

export const removeItem = (key: string): boolean => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
};

export const clearStorage = (): boolean => {
  try {
    localStorage.clear();
    return true;
  } catch {
    return false;
  }
};

export const getStorageSize = (): number => {
  let total = 0;
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length;
    }
  }
  return total;
};
