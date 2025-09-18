/**
 * 🧪 REACT TESTING LIBRARY TEMPLATE - ENTERPRISE TESTING
 * =======================================================
 * 
 * Comprehensive testing templates for React components with:
 * - React Testing Library best practices
 * - Accessibility testing
 * - User interaction testing
 * - Performance testing
 * - Creator Economy component testing
 * 
 * © 2025 Fahed Mlaiel <mlaiel@live.de>
 * TOUS DROITS RÉSERVÉS
 */

import React from 'react';
import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  act,
  cleanup,
  RenderOptions,
  RenderResult
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider } from 'styled-components';

// Extend Jest matchers
expect.extend(toHaveNoViolations);

// Types
export interface TestWrapperProps {
  children: React.ReactNode;
  theme?: any;
  initialState?: any;
  route?: string;
}

export interface ComponentTestSuite<T = any> {
  component: React.ComponentType<T>;
  props: T;
  variants?: Partial<T>[];
  accessibility?: boolean;
  performance?: boolean;
  interactions?: boolean;
}

// Default theme for testing
const defaultTheme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745',
    danger: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8'
  },
  spacing: {
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem'
  }
};

// Test wrapper component
const TestWrapper: React.FC<TestWrapperProps> = ({ 
  children, 
  theme = defaultTheme,
  initialState,
  route = '/'
}) => {
  return (
    <ThemeProvider theme={theme}>
      {children}
    </ThemeProvider>
  );
};

// Custom render function
export const renderWithProviders = (
  ui: React.ReactElement,
  options: Omit<RenderOptions, 'wrapper'> & {
    theme?: any;
    initialState?: any;
    route?: string;
  } = {}
): RenderResult => {
  const { theme, initialState, route, ...renderOptions } = options;

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <TestWrapper theme={theme} initialState={initialState} route={route}>
      {children}
    </TestWrapper>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

// Button Component Test Suite
export const buttonTestSuite = {
  'renders with default props': async () => {
    const { Button } = await import('../components/button_component_template');
    
    renderWithProviders(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Click me');
  },

  'renders all variants correctly': async () => {
    const { Button } = await import('../components/button_component_template');
    
    const variants = ['primary', 'secondary', 'success', 'danger', 'creator-gradient'];
    
    variants.forEach(variant => {
      const { rerender } = renderWithProviders(
        <Button variant={variant as any} data-testid={`button-${variant}`}>
          {variant} Button
        </Button>
      );
      
      const button = screen.getByTestId(`button-${variant}`);
      expect(button).toBeInTheDocument();
      expect(button).toHaveAttribute('data-testid', `button-${variant}`);
    });
  },

  'handles click events': async () => {
    const { Button } = await import('../components/button_component_template');
    const handleClick = jest.fn();
    
    renderWithProviders(
      <Button onClick={handleClick}>Click me</Button>
    );
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  },

  'shows loading state': async () => {
    const { Button } = await import('../components/button_component_template');
    
    renderWithProviders(
      <Button loading loadingText="Loading...">
        Submit
      </Button>
    );
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  },

  'is accessible': async () => {
    const { Button } = await import('../components/button_component_template');
    
    const { container } = renderWithProviders(
      <Button aria-label="Submit form">Submit</Button>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  },

  'supports keyboard navigation': async () => {
    const { Button } = await import('../components/button_component_template');
    const user = userEvent.setup();
    const handleClick = jest.fn();
    
    renderWithProviders(
      <Button onClick={handleClick}>Click me</Button>
    );
    
    const button = screen.getByRole('button');
    await user.tab();
    expect(button).toHaveFocus();
    
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalledTimes(1);
    
    await user.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  }
};

// Input Component Test Suite
export const inputTestSuite = {
  'renders with label': async () => {
    const { Input } = await import('../components/input_component_template');
    
    renderWithProviders(
      <Input label="Email" id="email" />
    );
    
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
  },

  'handles input changes': async () => {
    const { Input } = await import('../components/input_component_template');
    const user = userEvent.setup();
    const handleChange = jest.fn();
    
    renderWithProviders(
      <Input label="Name" onChange={handleChange} />
    );
    
    const input = screen.getByLabelText('Name');
    await user.type(input, 'John Doe');
    
    expect(input).toHaveValue('John Doe');
    expect(handleChange).toHaveBeenCalled();
  },

  'shows validation errors': async () => {
    const { Input } = await import('../components/input_component_template');
    
    renderWithProviders(
      <Input 
        label="Email" 
        error="Invalid email format"
        id="email"
      />
    );
    
    expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveAttribute('aria-invalid', 'true');
  },

  'supports floating labels': async () => {
    const { Input } = await import('../components/input_component_template');
    const user = userEvent.setup();
    
    renderWithProviders(
      <Input label="Email" floatingLabel id="email" />
    );
    
    const input = screen.getByRole('textbox');
    await user.click(input);
    
    expect(screen.getByTestId('floating-label')).toBeInTheDocument();
  },

  'validates input with custom validator': async () => {
    const { Input } = await import('../components/input_component_template');
    const user = userEvent.setup();
    
    const validate = jest.fn((value: string) => 
      value.length < 3 ? 'Too short' : null
    );
    
    renderWithProviders(
      <Input label="Username" validate={validate} />
    );
    
    const input = screen.getByLabelText('Username');
    await user.type(input, 'ab');
    
    await waitFor(() => {
      expect(validate).toHaveBeenCalledWith('ab');
    });
  }
};

// Modal Component Test Suite
export const modalTestSuite = {
  'renders when open': async () => {
    const { Modal } = await import('../components/modal_component_template');
    
    renderWithProviders(
      <Modal open={true} onClose={() => {}}>
        <div>Modal content</div>
      </Modal>
    );
    
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  },

  'does not render when closed': async () => {
    const { Modal } = await import('../components/modal_component_template');
    
    renderWithProviders(
      <Modal open={false} onClose={() => {}}>
        <div>Modal content</div>
      </Modal>
    );
    
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  },

  'closes on backdrop click': async () => {
    const { Modal } = await import('../components/modal_component_template');
    const user = userEvent.setup();
    const handleClose = jest.fn();
    
    renderWithProviders(
      <Modal open={true} onClose={handleClose} closeOnBackdrop>
        <div>Modal content</div>
      </Modal>
    );
    
    const backdrop = screen.getByTestId('modal-backdrop');
    await user.click(backdrop);
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  },

  'closes on escape key': async () => {
    const { Modal } = await import('../components/modal_component_template');
    const user = userEvent.setup();
    const handleClose = jest.fn();
    
    renderWithProviders(
      <Modal open={true} onClose={handleClose} closeOnEscape>
        <div>Modal content</div>
      </Modal>
    );
    
    await user.keyboard('{Escape}');
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  },

  'prevents closing when preventClose is true': async () => {
    const { Modal } = await import('../components/modal_component_template');
    const user = userEvent.setup();
    const handleClose = jest.fn();
    
    renderWithProviders(
      <Modal open={true} onClose={handleClose} preventClose>
        <div>Modal content</div>
      </Modal>
    );
    
    await user.keyboard('{Escape}');
    
    expect(handleClose).not.toHaveBeenCalled();
  },

  'manages focus correctly': async () => {
    const { Modal } = await import('../components/modal_component_template');
    
    renderWithProviders(
      <div>
        <button>Outside button</button>
        <Modal open={true} onClose={() => {}}>
          <button>Inside button</button>
        </Modal>
      </div>
    );
    
    const modal = screen.getByRole('dialog');
    expect(modal).toHaveFocus();
  }
};

// Creator Dashboard Test Suite
export const creatorDashboardTestSuite = {
  'renders creator information': async () => {
    const { CreatorDashboard } = await import('../creator/creator_dashboard_template');
    
    const mockCreatorData = {
      id: '1',
      name: 'John Creator',
      tier: 'pro' as const,
      verified: true,
      joinDate: new Date('2023-01-01'),
      stats: {
        totalContent: 50,
        totalViews: 100000,
        totalRevenue: 5000,
        subscribers: 1250,
        engagement: 85,
        monthlyViews: 25000,
        monthlyRevenue: 1200
      },
      recentContent: [],
      analytics: {
        viewsChart: [],
        revenueChart: [],
        engagementChart: [],
        topContent: [],
        demographics: { age: {}, location: {}, devices: {} }
      },
      collaborations: [],
      notifications: []
    };
    
    renderWithProviders(
      <CreatorDashboard creatorData={mockCreatorData} />
    );
    
    expect(screen.getByText('John Creator')).toBeInTheDocument();
    expect(screen.getByText('pro')).toBeInTheDocument();
    expect(screen.getByText('✓')).toBeInTheDocument();
  },

  'displays stats correctly': async () => {
    const { CreatorDashboard } = await import('../creator/creator_dashboard_template');
    
    const mockCreatorData = {
      id: '1',
      name: 'John Creator',
      tier: 'pro' as const,
      verified: true,
      joinDate: new Date('2023-01-01'),
      stats: {
        totalContent: 50,
        totalViews: 100000,
        totalRevenue: 5000,
        subscribers: 1250,
        engagement: 85,
        monthlyViews: 25000,
        monthlyRevenue: 1200
      },
      recentContent: [],
      analytics: {
        viewsChart: [],
        revenueChart: [],
        engagementChart: [],
        topContent: [],
        demographics: { age: {}, location: {}, devices: {} }
      },
      collaborations: [],
      notifications: []
    };
    
    renderWithProviders(
      <CreatorDashboard creatorData={mockCreatorData} />
    );
    
    expect(screen.getByText('$5,000.00')).toBeInTheDocument();
    expect(screen.getByText('1.3K')).toBeInTheDocument();
    expect(screen.getByText('100.0K')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  },

  'handles create content click': async () => {
    const { CreatorDashboard } = await import('../creator/creator_dashboard_template');
    const user = userEvent.setup();
    const handleCreateContent = jest.fn();
    
    const mockCreatorData = {
      id: '1',
      name: 'John Creator',
      tier: 'pro' as const,
      verified: true,
      joinDate: new Date('2023-01-01'),
      stats: {
        totalContent: 50,
        totalViews: 100000,
        totalRevenue: 5000,
        subscribers: 1250,
        engagement: 85,
        monthlyViews: 25000,
        monthlyRevenue: 1200
      },
      recentContent: [],
      analytics: {
        viewsChart: [],
        revenueChart: [],
        engagementChart: [],
        topContent: [],
        demographics: { age: {}, location: {}, devices: {} }
      },
      collaborations: [],
      notifications: []
    };
    
    renderWithProviders(
      <CreatorDashboard 
        creatorData={mockCreatorData}
        onCreateContent={handleCreateContent}
      />
    );
    
    const createButton = screen.getByText('Create Content');
    await user.click(createButton);
    
    expect(handleCreateContent).toHaveBeenCalledTimes(1);
  }
};

// Performance Testing Utilities
export const performanceTestUtils = {
  measureRenderTime: async (component: React.ReactElement) => {
    const start = performance.now();
    renderWithProviders(component);
    const end = performance.now();
    return end - start;
  },

  measureReRenderTime: async (component: React.ReactElement, newProps: any) => {
    const { rerender } = renderWithProviders(component);
    
    const start = performance.now();
    rerender(React.cloneElement(component, newProps));
    const end = performance.now();
    
    return end - start;
  },

  checkMemoryLeaks: async (component: React.ReactElement) => {
    const initialMemory = performance.memory?.usedJSHeapSize || 0;
    
    for (let i = 0; i < 100; i++) {
      const { unmount } = renderWithProviders(component);
      unmount();
    }
    
    const finalMemory = performance.memory?.usedJSHeapSize || 0;
    return finalMemory - initialMemory;
  }
};

// Accessibility Testing Utilities
export const a11yTestUtils = {
  checkKeyboardNavigation: async (component: React.ReactElement) => {
    const user = userEvent.setup();
    renderWithProviders(component);
    
    // Test tab navigation
    await user.tab();
    const focusedElement = document.activeElement;
    
    return focusedElement && focusedElement !== document.body;
  },

  checkAriaLabels: async (component: React.ReactElement) => {
    const { container } = renderWithProviders(component);
    
    const elementsWithAriaLabel = container.querySelectorAll('[aria-label]');
    const elementsWithAriaLabelledBy = container.querySelectorAll('[aria-labelledby]');
    
    return {
      hasAriaLabels: elementsWithAriaLabel.length > 0,
      hasAriaLabelledBy: elementsWithAriaLabelledBy.length > 0
    };
  },

  checkColorContrast: async (component: React.ReactElement) => {
    const { container } = renderWithProviders(component);
    const results = await axe(container);
    
    const contrastViolations = results.violations.filter(
      violation => violation.id === 'color-contrast'
    );
    
    return contrastViolations.length === 0;
  }
};

// Test Runner
export const runComponentTestSuite = async <T>(suite: ComponentTestSuite<T>) => {
  const { component: Component, props, variants = [], accessibility = true, performance = true } = suite;
  
  // Basic rendering test
  const renderResult = renderWithProviders(<Component {...props} />);
  expect(renderResult.container).toBeInTheDocument();
  
  // Variant tests
  for (const variant of variants) {
    const variantProps = { ...props, ...variant };
    const { rerender } = renderResult;
    rerender(<Component {...variantProps} />);
    expect(renderResult.container).toBeInTheDocument();
  }
  
  // Accessibility tests
  if (accessibility) {
    const { container } = renderWithProviders(<Component {...props} />);
    const a11yResults = await axe(container);
    expect(a11yResults).toHaveNoViolations();
  }
  
  // Performance tests
  if (performance) {
    const renderTime = await performanceTestUtils.measureRenderTime(<Component {...props} />);
    expect(renderTime).toBeLessThan(100); // 100ms threshold
  }
  
  cleanup();
};

// Export all test utilities
export {
  renderWithProviders as render,
  screen,
  fireEvent,
  waitFor,
  userEvent,
  axe,
  within,
  act,
  cleanup
};

export default {
  renderWithProviders,
  buttonTestSuite,
  inputTestSuite,
  modalTestSuite,
  creatorDashboardTestSuite,
  performanceTestUtils,
  a11yTestUtils,
  runComponentTestSuite
};