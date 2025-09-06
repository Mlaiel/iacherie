/**
 * @fileoverview User interface constants
 * @author Fahed Mlaiel <mlaiel@live.de>
 */

// Theme constants
export const UI_CONSTANTS = {
  THEME: {
    COLORS: {
      PRIMARY: '#3b82f6',
      SECONDARY: '#10b981',
      ACCENT: '#f59e0b',
      ERROR: '#ef4444',
      WARNING: '#f59e0b',
      SUCCESS: '#10b981',
      INFO: '#3b82f6',
    },
    BREAKPOINTS: {
      MOBILE: '768px',
      TABLET: '1024px',
      DESKTOP: '1280px',
      WIDE: '1536px',
    },
    SPACING: {
      XS: '4px',
      SM: '8px',
      MD: '16px',
      LG: '24px',
      XL: '32px',
      XXL: '48px',
    },
    TYPOGRAPHY: {
      FONT_FAMILY: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      FONT_SIZES: {
        XS: '12px',
        SM: '14px',
        MD: '16px',
        LG: '18px',
        XL: '20px',
        '2XL': '24px',
        '3XL': '30px',
        '4XL': '36px',
      },
    },
  },
  
  ANIMATION: {
    DURATION: {
      FAST: '150ms',
      NORMAL: '300ms',
      SLOW: '500ms',
    },
    EASING: {
      EASE_IN: 'cubic-bezier(0.4, 0, 1, 1)',
      EASE_OUT: 'cubic-bezier(0, 0, 0.2, 1)',
      EASE_IN_OUT: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
  
  LAYOUT: {
    HEADER_HEIGHT: '64px',
    SIDEBAR_WIDTH: '256px',
    SIDEBAR_COLLAPSED_WIDTH: '64px',
    FOOTER_HEIGHT: '48px',
    CONTAINER_MAX_WIDTH: '1280px',
  },
  
  FORM: {
    INPUT_HEIGHT: '40px',
    BUTTON_HEIGHT: '40px',
    MAX_INPUT_LENGTH: 255,
    VALIDATION_DEBOUNCE: 300,
  },
  
  MODAL: {
    SIZES: {
      SM: '400px',
      MD: '600px',
      LG: '800px',
      XL: '1000px',
      FULL: '100vw',
    },
    Z_INDEX: 1000,
  },
  
  NOTIFICATION: {
    DURATION: {
      SHORT: 3000,
      MEDIUM: 5000,
      LONG: 8000,
    },
    MAX_VISIBLE: 5,
  },
} as const;

// Component constants
export const COMPONENT_CONSTANTS = {
  PAGINATION: {
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
    MAX_VISIBLE_PAGES: 7,
  },
  
  TABLE: {
    MIN_COLUMN_WIDTH: 80,
    DEFAULT_COLUMN_WIDTH: 150,
    MAX_ROWS_PER_PAGE: 100,
  },
  
  UPLOAD: {
    CHUNK_SIZE: 1024 * 1024, // 1MB chunks
    MAX_CONCURRENT_UPLOADS: 3,
    RETRY_ATTEMPTS: 3,
    PROGRESS_UPDATE_INTERVAL: 100,
  },
  
  SEARCH: {
    MIN_QUERY_LENGTH: 3,
    DEBOUNCE_DELAY: 300,
    MAX_SUGGESTIONS: 10,
  },
} as const;