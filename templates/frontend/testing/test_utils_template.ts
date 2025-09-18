/**
 * @fileoverview Enterprise Testing Utilities Collection
 * @version 1.0.0
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @copyright 2025 Fahed Mlaiel - All Rights Reserved
 * @license Proprietary - Unauthorized use prohibited
 * 
 * 🚨 INTELLECTUAL PROPERTY WARNING:
 * This code is the exclusive property of Fahed Mlaiel.
 * Unauthorized copying, modification, distribution, or commercial use
 * without explicit written permission is strictly prohibited.
 * Violation will result in immediate legal action.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from 'styled-components';
import React from 'react';

// ==================== TYPES & INTERFACES ====================

interface RenderOptions {
  theme?: any;
  wrapper?: React.ComponentType<any>;
  preloadedState?: any;
  store?: any;
}

interface WaitForOptions {
  timeout?: number;
  interval?: number;
  onTimeout?: (error: Error) => void;
}

interface MockFunction<T extends (...args: any[]) => any> {
  (...args: Parameters<T>): ReturnType<T>;
  mock: {
    calls: Parameters<T>[];
    results: Array<{ type: 'return' | 'throw'; value: ReturnType<T> }>;
    instances: any[];
  };
}

// ==================== CUSTOM RENDER FUNCTIONS ====================

/**
 * Enhanced render function with theme provider and custom options
 */
export const renderWithTheme = (
  ui: React.ReactElement,
  options: RenderOptions = {}
) => {
  const { theme = defaultTheme, wrapper, ...renderOptions } = options;

  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const Component = wrapper || React.Fragment;
    return (
      <ThemeProvider theme={theme}>
        <Component>{children}</Component>
      </ThemeProvider>
    );
  };

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

/**
 * Render function with Redux store provider
 */
export const renderWithStore = (
  ui: React.ReactElement,
  options: RenderOptions = {}
) => {
  const { preloadedState, store = createMockStore(preloadedState), ...renderOptions } = options;

  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Provider store={store}>
      <ThemeProvider theme={options.theme || defaultTheme}>
        {children}
      </ThemeProvider>
    </Provider>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...renderOptions }),
    store,
  };
};

/**
 * Render function for testing React Router components
 */
export const renderWithRouter = (
  ui: React.ReactElement,
  {
    initialEntries = ['/'],
    history = createMemoryHistory({ initialEntries }),
    ...options
  }: RenderOptions & {
    initialEntries?: string[];
    history?: any;
  } = {}
) => {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Router history={history}>
      <ThemeProvider theme={options.theme || defaultTheme}>
        {children}
      </ThemeProvider>
    </Router>
  );

  return {
    ...render(ui, { wrapper: Wrapper, ...options }),
    history,
  };
};

// ==================== DEFAULT THEME ====================

const defaultTheme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#6b7280',
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
    light: '#f9fafb',
    dark: '#111827',
    background: '#ffffff',
    surface: '#f9fafb',
    border: '#e5e7eb',
    text: '#111827',
    textSecondary: '#6b7280',
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem',
  },
  breakpoints: {
    mobile: '768px',
    tablet: '1024px',
    desktop: '1200px',
  },
};

// ==================== MOCK STORE CREATION ====================

/**
 * Creates a mock Redux store for testing
 */
export const createMockStore = (initialState: any = {}) => {
  const mockStore = {
    getState: jest.fn(() => initialState),
    dispatch: jest.fn(),
    subscribe: jest.fn(),
    replaceReducer: jest.fn(),
  };

  return mockStore;
};

// ==================== COMPONENT TESTING UTILITIES ====================

/**
 * Waits for an element to appear with custom options
 */
export const waitForElement = async (
  selector: string,
  options: WaitForOptions = {}
): Promise<HTMLElement> => {
  const { timeout = 5000, interval = 50, onTimeout } = options;

  try {
    return await waitFor(
      () => {
        const element = screen.getByTestId(selector) || screen.getByText(selector);
        if (!element) {
          throw new Error(`Element with selector "${selector}" not found`);
        }
        return element;
      },
      { timeout, interval }
    );
  } catch (error) {
    if (onTimeout) {
      onTimeout(error as Error);
    }
    throw error;
  }
};

/**
 * Waits for an element to disappear
 */
export const waitForElementToBeRemoved = async (
  selector: string,
  options: WaitForOptions = {}
): Promise<void> => {
  const { timeout = 5000 } = options;

  await waitFor(
    () => {
      const element = screen.queryByTestId(selector) || screen.queryByText(selector);
      if (element) {
        throw new Error(`Element with selector "${selector}" is still present`);
      }
    },
    { timeout }
  );
};

/**
 * Simulates user typing with realistic delays
 */
export const typeWithDelay = async (element: HTMLElement, text: string, delay = 50) => {
  const user = userEvent.setup({ delay });
  await user.type(element, text);
};

/**
 * Simulates user clicking with delay
 */
export const clickWithDelay = async (element: HTMLElement, delay = 100) => {
  const user = userEvent.setup({ delay });
  await user.click(element);
};

/**
 * Fills out a form with provided data
 */
export const fillForm = async (formData: Record<string, string>, delay = 50) => {
  const user = userEvent.setup({ delay });

  for (const [fieldName, value] of Object.entries(formData)) {
    const field = screen.getByLabelText(new RegExp(fieldName, 'i')) as HTMLInputElement;
    await user.clear(field);
    await user.type(field, value);
  }
};

/**
 * Submits a form and waits for response
 */
export const submitForm = async (formTestId = 'form', submitButtonTestId = 'submit-button') => {
  const submitButton = screen.getByTestId(submitButtonTestId);
  await clickWithDelay(submitButton);
  
  // Wait for form submission to complete
  await waitFor(() => {
    expect(submitButton).not.toBeDisabled();
  });
};

// ==================== ASSERTION HELPERS ====================

/**
 * Asserts that an element has specific styles
 */
export const expectElementToHaveStyles = (element: HTMLElement, styles: Record<string, string>) => {
  const computedStyles = window.getComputedStyle(element);
  
  Object.entries(styles).forEach(([property, value]) => {
    expect(computedStyles.getPropertyValue(property)).toBe(value);
  });
};

/**
 * Asserts that an element is visible
 */
export const expectElementToBeVisible = (selector: string) => {
  const element = screen.getByTestId(selector);
  expect(element).toBeVisible();
  expect(element).not.toHaveStyle('display: none');
  expect(element).not.toHaveStyle('visibility: hidden');
};

/**
 * Asserts that an element is accessible
 */
export const expectElementToBeAccessible = async (element: HTMLElement) => {
  // Check for proper ARIA attributes
  if (element.tagName === 'BUTTON') {
    expect(element).toHaveAttribute('type');
  }
  
  if (element.tagName === 'INPUT') {
    const id = element.getAttribute('id');
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      expect(label).toBeInTheDocument();
    }
  }
  
  // Check for keyboard accessibility
  expect(element).not.toHaveAttribute('tabindex', '-1');
};

/**
 * Asserts API call was made with correct parameters
 */
export const expectAPICallWith = (mockFn: jest.MockedFunction<any>, expectedCall: any) => {
  expect(mockFn).toHaveBeenCalledWith(
    expect.objectContaining(expectedCall)
  );
};

// ==================== MOCK HELPERS ====================

/**
 * Creates a mock function with better typing
 */
export const createMockFn = <T extends (...args: any[]) => any>(): MockFunction<T> => {
  return jest.fn() as MockFunction<T>;
};

/**
 * Mocks console methods for testing
 */
export const mockConsole = () => {
  const originalConsole = global.console;
  const mockMethods = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    info: jest.fn(),
    debug: jest.fn(),
  };

  global.console = { ...originalConsole, ...mockMethods };

  return {
    ...mockMethods,
    restore: () => {
      global.console = originalConsole;
    },
  };
};

/**
 * Mocks window.localStorage
 */
export const mockLocalStorage = () => {
  const store: Record<string, string> = {};

  const mockStorage = {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      Object.keys(store).forEach(key => delete store[key]);
    }),
    length: 0,
    key: jest.fn((index: number) => Object.keys(store)[index] || null),
  };

  Object.defineProperty(window, 'localStorage', {
    value: mockStorage,
    writable: true,
  });

  return {
    ...mockStorage,
    getStore: () => ({ ...store }),
    restore: () => {
      // Restore original localStorage if available
    },
  };
};

/**
 * Mocks window.fetch
 */
export const mockFetch = (responses: Array<{ url: string; response: any; status?: number }>) => {
  const originalFetch = global.fetch;

  global.fetch = jest.fn((url: string, options?: RequestInit) => {
    const matchedResponse = responses.find(r => url.includes(r.url));
    
    if (matchedResponse) {
      return Promise.resolve({
        ok: (matchedResponse.status || 200) < 400,
        status: matchedResponse.status || 200,
        json: () => Promise.resolve(matchedResponse.response),
        text: () => Promise.resolve(JSON.stringify(matchedResponse.response)),
      } as Response);
    }

    return Promise.reject(new Error(`No mock response for ${url}`));
  }) as jest.MockedFunction<typeof fetch>;

  return {
    restore: () => {
      global.fetch = originalFetch;
    },
  };
};

// ==================== PERFORMANCE TESTING ====================

/**
 * Measures rendering performance
 */
export const measureRenderTime = async (renderFn: () => void) => {
  const start = performance.now();
  
  await act(async () => {
    renderFn();
  });
  
  const end = performance.now();
  return end - start;
};

/**
 * Tests component re-render count
 */
export const countRerenders = (Component: React.ComponentType<any>, props: any) => {
  let renderCount = 0;
  
  const WrappedComponent: React.FC = (componentProps) => {
    renderCount++;
    return <Component {...props} {...componentProps} />;
  };

  return {
    Component: WrappedComponent,
    getRenderCount: () => renderCount,
    resetCount: () => { renderCount = 0; },
  };
};

// ==================== ASYNC TESTING HELPERS ====================

/**
 * Waits for next tick
 */
export const waitForNextTick = () => new Promise(resolve => setTimeout(resolve, 0));

/**
 * Waits for multiple async operations
 */
export const waitForAll = async (promises: Promise<any>[]) => {
  return Promise.all(promises);
};

/**
 * Creates a deferred promise for testing
 */
export const createDeferred = <T>() => {
  let resolve: (value: T) => void;
  let reject: (reason: any) => void;
  
  const promise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return {
    promise,
    resolve: resolve!,
    reject: reject!,
  };
};

// ==================== ERROR BOUNDARY TESTING ====================

/**
 * Tests error boundaries
 */
export const TestErrorBoundary: React.FC<{
  children: React.ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
}> = ({ children, onError }) => {
  const [hasError, setHasError] = React.useState(false);

  React.useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      setHasError(true);
      onError?.(error.error, {});
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, [onError]);

  if (hasError) {
    return <div data-testid="error-boundary">Something went wrong.</div>;
  }

  return <>{children}</>;
};

/**
 * Triggers an error in component for testing error boundaries
 */
export const ThrowError: React.FC<{ shouldThrow?: boolean; message?: string }> = ({ 
  shouldThrow = true, 
  message = 'Test error' 
}) => {
  if (shouldThrow) {
    throw new Error(message);
  }
  return <div>No error</div>;
};

// ==================== TEST DATA GENERATORS ====================

/**
 * Generates test user data
 */
export const generateTestUser = (overrides: any = {}) => ({
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  displayName: 'Test User',
  avatar: '/test-avatar.jpg',
  verified: false,
  createdAt: new Date().toISOString(),
  ...overrides,
});

/**
 * Generates test content data
 */
export const generateTestContent = (overrides: any = {}) => ({
  id: '1',
  title: 'Test Content',
  description: 'This is test content',
  type: 'audio',
  url: '/test-content.mp3',
  thumbnailUrl: '/test-thumbnail.jpg',
  duration: 180,
  fileSize: 1024000,
  status: 'published',
  createdAt: new Date().toISOString(),
  performance: {
    views: 1000,
    likes: 100,
    shares: 50,
    revenue: 25.50,
  },
  ...overrides,
});

// ==================== VIEWPORT TESTING ====================

/**
 * Tests component at different viewport sizes
 */
export const testResponsive = (
  component: React.ReactElement,
  viewports: Array<{ width: number; height: number; name: string }>
) => {
  return viewports.map(viewport => ({
    name: viewport.name,
    test: () => {
      // Mock viewport size
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: viewport.width,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: viewport.height,
      });

      // Trigger resize event
      window.dispatchEvent(new Event('resize'));

      return renderWithTheme(component);
    },
  }));
};

// ==================== EXPORTS ====================

export default {
  // Render functions
  renderWithTheme,
  renderWithStore,
  renderWithRouter,
  
  // Testing utilities
  waitForElement,
  waitForElementToBeRemoved,
  typeWithDelay,
  clickWithDelay,
  fillForm,
  submitForm,
  
  // Assertions
  expectElementToHaveStyles,
  expectElementToBeVisible,
  expectElementToBeAccessible,
  expectAPICallWith,
  
  // Mocks
  createMockFn,
  mockConsole,
  mockLocalStorage,
  mockFetch,
  createMockStore,
  
  // Performance
  measureRenderTime,
  countRerenders,
  
  // Async helpers
  waitForNextTick,
  waitForAll,
  createDeferred,
  
  // Error testing
  TestErrorBoundary,
  ThrowError,
  
  // Data generators
  generateTestUser,
  generateTestContent,
  
  // Responsive testing
  testResponsive,
  
  // Theme
  defaultTheme,
};

// Type exports
export type {
  RenderOptions,
  WaitForOptions,
  MockFunction,
};