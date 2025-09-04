/**
 * Accessibility Utilities
 */

export const announceToScreenReader = (message: string): void => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.style.cssText = 'position:absolute;left:-10000px;width:1px;height:1px;overflow:hidden;';
  
  document.body.appendChild(announcement);
  announcement.textContent = message;
  
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

export const trapFocus = (container: HTMLElement): () => void => {
  const focusableElements = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  ) as NodeListOf<HTMLElement>;
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    }
  };

  container.addEventListener('keydown', handleTabKey);
  firstElement?.focus();

  return () => {
    container.removeEventListener('keydown', handleTabKey);
  };
};

export const getContrastRatio = (color1: string, color2: string): number => {
  const getLuminance = (color: string): number => {
    const rgb = color.match(/\d+/g);
    if (!rgb) return 0;
    
    const [r, g, b] = rgb.map(c => {
      const val = parseInt(c) / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
};

export const isColorAccessible = (foreground: string, background: string, level: 'AA' | 'AAA' = 'AA'): boolean => {
  const contrast = getContrastRatio(foreground, background);
  return level === 'AA' ? contrast >= 4.5 : contrast >= 7;
};

export const addAriaLabels = (element: HTMLElement, labels: Record<string, string>): void => {
  Object.entries(labels).forEach(([attr, value]) => {
    element.setAttribute(`aria-${attr}`, value);
  });
};

export const manageTabIndex = (elements: HTMLElement[], activeIndex: number): void => {
  elements.forEach((element, index) => {
    element.tabIndex = index === activeIndex ? 0 : -1;
  });
};
