/**
 * URL Utilities
 */

export const getQueryParams = (url: string = window.location.href): Record<string, string> => {
  const params: Record<string, string> = {};
  const urlObj = new URL(url);
  urlObj.searchParams.forEach((value, key) => {
    params[key] = value;
  });
  return params;
};

export const setQueryParam = (key: string, value: string): void => {
  const url = new URL(window.location.href);
  url.searchParams.set(key, value);
  window.history.replaceState({}, '', url.toString());
};

export const removeQueryParam = (key: string): void => {
  const url = new URL(window.location.href);
  url.searchParams.delete(key);
  window.history.replaceState({}, '', url.toString());
};

export const buildURL = (base: string, params: Record<string, string>): string => {
  const url = new URL(base);
  Object.entries(params).forEach(([key, value]) => {
    url.searchParams.set(key, value);
  });
  return url.toString();
};

export const isValidURL = (string: string): boolean => {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
};

export const getDomain = (url: string): string => {
  try {
    return new URL(url).hostname;
  } catch {
    return '';
  }
};
