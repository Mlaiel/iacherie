/**
 * DOM Utilities
 */

export const addClass = (element: Element, className: string): void => {
  element.classList.add(className);
};

export const removeClass = (element: Element, className: string): void => {
  element.classList.remove(className);
};

export const toggleClass = (element: Element, className: string): void => {
  element.classList.toggle(className);
};

export const hasClass = (element: Element, className: string): boolean => {
  return element.classList.contains(className);
};

export const getElementPosition = (element: Element): { top: number; left: number } => {
  const rect = element.getBoundingClientRect();
  return {
    top: rect.top + window.scrollY,
    left: rect.left + window.scrollX,
  };
};

export const isElementInViewport = (element: Element): boolean => {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
};

export const scrollToElement = (element: Element, offset = 0): void => {
  const position = getElementPosition(element);
  window.scrollTo({
    top: position.top - offset,
    behavior: 'smooth',
  });
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return true;
    } catch {
      document.body.removeChild(textArea);
      return false;
    }
  }
};
