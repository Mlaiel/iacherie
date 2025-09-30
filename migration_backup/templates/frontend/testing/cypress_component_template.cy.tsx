/**
 * @fileoverview Enterprise Cypress Component Testing Template
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

/// <reference types="cypress" />

import { mount } from 'cypress/react18';
import React from 'react';

// ==================== EXAMPLE COMPONENTS FOR TESTING ====================

// Simple Button Component for demonstration
const Button: React.FC<{
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  loading?: boolean;
  'data-testid'?: string;
}> = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  disabled = false, 
  loading = false,
  'data-testid': testId
}) => {
  const baseStyles = 'px-4 py-2 rounded font-medium transition-colors';
  const variantStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      onClick={onClick}
      disabled={disabled || loading}
      data-testid={testId}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
};

// Form Component for demonstration
const LoginForm: React.FC<{
  onSubmit?: (data: { email: string; password: string }) => void;
  loading?: boolean;
}> = ({ onSubmit, loading = false }) => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [errors, setErrors] = React.useState<{ email?: string; password?: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: { email?: string; password?: string } = {};
    
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';
    if (password.length < 6) newErrors.password = 'Password must be at least 6 characters';
    
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit?.({ email, password });
    }
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form">
      <div className="mb-4">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email
        </label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          data-testid="email-input"
        />
        {errors.email && (
          <span className="text-red-500 text-sm" data-testid="email-error">
            {errors.email}
          </span>
        )}
      </div>
      
      <div className="mb-4">
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
          data-testid="password-input"
        />
        {errors.password && (
          <span className="text-red-500 text-sm" data-testid="password-error">
            {errors.password}
          </span>
        )}
      </div>
      
      <Button
        type="submit"
        variant="primary"
        loading={loading}
        data-testid="submit-button"
      >
        Sign In
      </Button>
    </form>
  );
};

// Modal Component for demonstration
const Modal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}> = ({ isOpen, onClose, title, children }) => {
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      data-testid="modal-overlay"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div 
        className="bg-white rounded-lg p-6 max-w-md w-full mx-4"
        data-testid="modal-content"
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold" data-testid="modal-title">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
            data-testid="modal-close"
          >
            ✕
          </button>
        </div>
        <div data-testid="modal-body">
          {children}
        </div>
      </div>
    </div>
  );
};

// ==================== CYPRESS COMMAND EXTENSIONS ====================

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to mount React components
       */
      mountComponent(component: React.ReactElement): Chainable<Element>;
      
      /**
       * Custom command to test accessibility
       */
      checkA11y(): Chainable<Element>;
      
      /**
       * Custom command to test responsive design
       */
      testResponsive(viewports: string[]): Chainable<Element>;
      
      /**
       * Custom command to wait for element to be stable
       */
      waitForStable(selector: string): Chainable<Element>;
      
      /**
       * Custom command to test file upload
       */
      uploadFile(selector: string, fileName: string, fileType?: string): Chainable<Element>;
      
      /**
       * Custom command to test drag and drop
       */
      dragAndDrop(sourceSelector: string, targetSelector: string): Chainable<Element>;
    }
  }
}

// Implement custom commands
Cypress.Commands.add('mountComponent', (component) => {
  return mount(component);
});

Cypress.Commands.add('checkA11y', () => {
  // Basic accessibility checks
  cy.get('[data-testid]').should('be.visible');
  cy.get('button').should('not.have.attr', 'disabled').should('be.visible');
  cy.get('input').each($el => {
    cy.wrap($el).should('have.attr', 'id');
    cy.wrap($el).then($input => {
      const id = $input.attr('id');
      cy.get(`label[for="${id}"]`).should('exist');
    });
  });
});

Cypress.Commands.add('testResponsive', (viewports) => {
  viewports.forEach(viewport => {
    cy.viewport(viewport as any);
    cy.wait(100); // Allow time for responsive changes
    cy.get('[data-testid]').should('be.visible');
  });
});

Cypress.Commands.add('waitForStable', (selector) => {
  let previousPosition: { x: number; y: number } | null = null;
  
  return cy.get(selector).then($el => {
    const checkStability = () => {
      const rect = $el[0].getBoundingClientRect();
      const currentPosition = { x: rect.left, y: rect.top };
      
      if (previousPosition && 
          previousPosition.x === currentPosition.x && 
          previousPosition.y === currentPosition.y) {
        return Promise.resolve();
      }
      
      previousPosition = currentPosition;
      return new Promise(resolve => setTimeout(resolve, 50)).then(checkStability);
    };
    
    return checkStability();
  });
});

Cypress.Commands.add('uploadFile', (selector, fileName, fileType = 'text/plain') => {
  cy.get(selector).selectFile({
    contents: Cypress.Buffer.from('file content'),
    fileName,
    mimeType: fileType
  });
});

Cypress.Commands.add('dragAndDrop', (sourceSelector, targetSelector) => {
  cy.get(sourceSelector)
    .trigger('mousedown', { button: 0 })
    .wait(100);
  
  cy.get(targetSelector)
    .trigger('mousemove')
    .trigger('mouseup');
});

// ==================== TEST SUITES ====================

describe('Button Component Tests', () => {
  beforeEach(() => {
    // Setup before each test
  });

  it('should render button with default props', () => {
    cy.mountComponent(<Button>Click me</Button>);
    
    cy.get('button')
      .should('be.visible')
      .should('contain.text', 'Click me')
      .should('have.class', 'bg-blue-600');
  });

  it('should handle click events', () => {
    const onClickSpy = cy.stub().as('onClickSpy');
    
    cy.mountComponent(
      <Button onClick={onClickSpy} data-testid="test-button">
        Click me
      </Button>
    );
    
    cy.get('[data-testid="test-button"]').click();
    cy.get('@onClickSpy').should('have.been.called');
  });

  it('should show loading state', () => {
    cy.mountComponent(<Button loading>Click me</Button>);
    
    cy.get('button')
      .should('contain.text', 'Loading...')
      .should('be.disabled');
  });

  it('should handle different variants', () => {
    const variants = ['primary', 'secondary', 'danger'] as const;
    
    variants.forEach(variant => {
      cy.mountComponent(<Button variant={variant}>Button</Button>);
      
      const expectedClass = {
        primary: 'bg-blue-600',
        secondary: 'bg-gray-600',
        danger: 'bg-red-600'
      }[variant];
      
      cy.get('button').should('have.class', expectedClass);
    });
  });

  it('should be accessible', () => {
    cy.mountComponent(
      <Button data-testid="accessible-button">Accessible Button</Button>
    );
    
    cy.checkA11y();
    
    // Test keyboard navigation
    cy.get('button').focus().should('be.focused');
    cy.get('button').type('{enter}');
  });

  it('should work on different screen sizes', () => {
    cy.mountComponent(<Button>Responsive Button</Button>);
    
    cy.testResponsive(['iphone-6', 'ipad-2', 'macbook-15']);
  });
});

describe('Login Form Component Tests', () => {
  it('should render form fields', () => {
    cy.mountComponent(<LoginForm />);
    
    cy.get('[data-testid="login-form"]').should('be.visible');
    cy.get('[data-testid="email-input"]').should('be.visible');
    cy.get('[data-testid="password-input"]').should('be.visible');
    cy.get('[data-testid="submit-button"]').should('be.visible');
  });

  it('should validate required fields', () => {
    cy.mountComponent(<LoginForm />);
    
    cy.get('[data-testid="submit-button"]').click();
    
    cy.get('[data-testid="email-error"]')
      .should('be.visible')
      .should('contain.text', 'Email is required');
    
    cy.get('[data-testid="password-error"]')
      .should('be.visible')
      .should('contain.text', 'Password is required');
  });

  it('should validate password length', () => {
    cy.mountComponent(<LoginForm />);
    
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('123');
    cy.get('[data-testid="submit-button"]').click();
    
    cy.get('[data-testid="password-error"]')
      .should('be.visible')
      .should('contain.text', 'Password must be at least 6 characters');
  });

  it('should submit valid form', () => {
    const onSubmitSpy = cy.stub().as('onSubmitSpy');
    
    cy.mountComponent(<LoginForm onSubmit={onSubmitSpy} />);
    
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    cy.get('[data-testid="submit-button"]').click();
    
    cy.get('@onSubmitSpy').should('have.been.calledWith', {
      email: 'test@example.com',
      password: 'password123'
    });
  });

  it('should show loading state', () => {
    cy.mountComponent(<LoginForm loading />);
    
    cy.get('[data-testid="submit-button"]')
      .should('contain.text', 'Loading...')
      .should('be.disabled');
  });

  it('should be keyboard accessible', () => {
    cy.mountComponent(<LoginForm />);
    
    // Test tab navigation
    cy.get('[data-testid="email-input"]').focus();
    cy.focused().tab();
    cy.focused().should('have.attr', 'data-testid', 'password-input');
    
    cy.focused().tab();
    cy.focused().should('have.attr', 'data-testid', 'submit-button');
  });
});

describe('Modal Component Tests', () => {
  it('should not render when closed', () => {
    cy.mountComponent(
      <Modal isOpen={false} onClose={() => {}} title="Test Modal">
        Modal content
      </Modal>
    );
    
    cy.get('[data-testid="modal-overlay"]').should('not.exist');
  });

  it('should render when open', () => {
    cy.mountComponent(
      <Modal isOpen={true} onClose={() => {}} title="Test Modal">
        Modal content
      </Modal>
    );
    
    cy.get('[data-testid="modal-overlay"]').should('be.visible');
    cy.get('[data-testid="modal-content"]').should('be.visible');
    cy.get('[data-testid="modal-title"]').should('contain.text', 'Test Modal');
    cy.get('[data-testid="modal-body"]').should('contain.text', 'Modal content');
  });

  it('should close when clicking overlay', () => {
    const onCloseSpy = cy.stub().as('onCloseSpy');
    
    cy.mountComponent(
      <Modal isOpen={true} onClose={onCloseSpy} title="Test Modal">
        Modal content
      </Modal>
    );
    
    cy.get('[data-testid="modal-overlay"]').click();
    cy.get('@onCloseSpy').should('have.been.called');
  });

  it('should close when clicking close button', () => {
    const onCloseSpy = cy.stub().as('onCloseSpy');
    
    cy.mountComponent(
      <Modal isOpen={true} onClose={onCloseSpy} title="Test Modal">
        Modal content
      </Modal>
    );
    
    cy.get('[data-testid="modal-close"]').click();
    cy.get('@onCloseSpy').should('have.been.called');
  });

  it('should close when pressing Escape key', () => {
    const onCloseSpy = cy.stub().as('onCloseSpy');
    
    cy.mountComponent(
      <Modal isOpen={true} onClose={onCloseSpy} title="Test Modal">
        Modal content
      </Modal>
    );
    
    cy.get('body').type('{esc}');
    cy.get('@onCloseSpy').should('have.been.called');
  });

  it('should trap focus within modal', () => {
    cy.mountComponent(
      <Modal isOpen={true} onClose={() => {}} title="Test Modal">
        <input data-testid="modal-input" placeholder="Test input" />
        <button data-testid="modal-button">Test button</button>
      </Modal>
    );
    
    // Focus should be trapped within modal
    cy.get('[data-testid="modal-close"]').focus();
    cy.focused().tab();
    cy.focused().should('have.attr', 'data-testid', 'modal-input');
    
    cy.focused().tab();
    cy.focused().should('have.attr', 'data-testid', 'modal-button');
  });
});

// ==================== INTEGRATION TESTS ====================

describe('Component Integration Tests', () => {
  it('should integrate button with form submission', () => {
    const App = () => {
      const [isModalOpen, setIsModalOpen] = React.useState(false);
      const [isLoading, setIsLoading] = React.useState(false);
      
      const handleSubmit = (data: any) => {
        setIsLoading(true);
        setTimeout(() => {
          setIsLoading(false);
          setIsModalOpen(true);
        }, 1000);
      };
      
      return (
        <div>
          <LoginForm onSubmit={handleSubmit} loading={isLoading} />
          <Modal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            title="Success"
          >
            Login successful!
          </Modal>
        </div>
      );
    };
    
    cy.mountComponent(<App />);
    
    // Fill form
    cy.get('[data-testid="email-input"]').type('test@example.com');
    cy.get('[data-testid="password-input"]').type('password123');
    
    // Submit form
    cy.get('[data-testid="submit-button"]').click();
    
    // Check loading state
    cy.get('[data-testid="submit-button"]').should('contain.text', 'Loading...');
    
    // Wait for modal to appear
    cy.get('[data-testid="modal-overlay"]', { timeout: 2000 }).should('be.visible');
    cy.get('[data-testid="modal-title"]').should('contain.text', 'Success');
  });
});

// ==================== PERFORMANCE TESTS ====================

describe('Performance Tests', () => {
  it('should render components within acceptable time', () => {
    const startTime = performance.now();
    
    cy.mountComponent(
      <div>
        {Array.from({ length: 100 }, (_, i) => (
          <Button key={i} data-testid={`button-${i}`}>
            Button {i}
          </Button>
        ))}
      </div>
    );
    
    cy.get('[data-testid="button-0"]').should('be.visible').then(() => {
      const endTime = performance.now();
      const renderTime = endTime - startTime;
      
      // Assert render time is reasonable (less than 1 second)
      expect(renderTime).to.be.lessThan(1000);
    });
  });

  it('should handle rapid interactions', () => {
    let clickCount = 0;
    const handleClick = () => { clickCount++; };
    
    cy.mountComponent(
      <Button onClick={handleClick} data-testid="rapid-click-button">
        Rapid Click Test
      </Button>
    );
    
    // Perform rapid clicks
    for (let i = 0; i < 10; i++) {
      cy.get('[data-testid="rapid-click-button"]').click();
    }
    
    // Verify all clicks were handled
    cy.then(() => {
      expect(clickCount).to.equal(10);
    });
  });
});

// ==================== VISUAL TESTING ====================

describe('Visual Testing', () => {
  it('should match visual snapshots', () => {
    cy.mountComponent(
      <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
        <h1>Component Showcase</h1>
        <div style={{ marginBottom: '20px' }}>
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary" style={{ marginLeft: '10px' }}>Secondary Button</Button>
          <Button variant="danger" style={{ marginLeft: '10px' }}>Danger Button</Button>
        </div>
        <LoginForm />
      </div>
    );
    
    // Take screenshot for visual comparison
    cy.screenshot('component-showcase');
    
    // Ensure components are visually stable
    cy.waitForStable('[data-testid="submit-button"]');
    cy.screenshot('component-showcase-stable');
  });
});

// ==================== EXPORT CONFIGURATION ====================

export default {
  Button,
  LoginForm,
  Modal
};

// Export types for external use
export type ButtonProps = React.ComponentProps<typeof Button>;
export type LoginFormProps = React.ComponentProps<typeof LoginForm>;
export type ModalProps = React.ComponentProps<typeof Modal>;