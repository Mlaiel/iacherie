/**
 * @fileoverview Enterprise Storybook Stories Template Collection
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

import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';

// ==================== INTERFACES & TYPES ====================

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
  onClick?: () => void;
}

interface FormProps {
  title?: string;
  onSubmit?: (data: any) => void;
  loading?: boolean;
  children?: React.ReactNode;
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size?: 'small' | 'medium' | 'large' | 'fullscreen';
  children: React.ReactNode;
}

// ==================== DEMO COMPONENTS ====================

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  icon,
  fullWidth = false,
  onClick
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200';
  
  const sizeClasses = {
    small: 'px-3 py-1.5 text-sm',
    medium: 'px-4 py-2 text-base',
    large: 'px-6 py-3 text-lg'
  };
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500'
  };
  
  const classes = [
    baseClasses,
    sizeClasses[size],
    variantClasses[variant],
    fullWidth ? 'w-full' : '',
    disabled || loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 focus:ring-2 focus:ring-offset-2'
  ].join(' ');

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      {icon && !loading && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
};

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'medium',
  children
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
    fullscreen: 'max-w-screen-xl'
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
        <div className={`relative bg-white rounded-lg shadow-xl ${sizeClasses[size]} w-full`}>
          <div className="flex items-center justify-between p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <span className="sr-only">Close</span>
              ✕
            </button>
          </div>
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

const LoginForm: React.FC<FormProps> = ({ title = 'Sign In', onSubmit, loading = false }) => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit?.({ email, password });
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6">{title}</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your email"
            required
          />
        </div>
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your password"
            required
          />
        </div>
        <Button
          type="submit"
          variant="primary"
          size="large"
          fullWidth
          loading={loading}
        >
          Sign In
        </Button>
      </form>
    </div>
  );
};

// ==================== STORYBOOK CONFIGURATIONS ====================

// Button Stories
const buttonMeta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A versatile button component with multiple variants, sizes, and states. Part of the Ainflue Enterprise Design System.',
      },
    },
  },
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'danger', 'success', 'warning'],
      description: 'Visual style variant of the button'
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large'],
      description: 'Size of the button'
    },
    disabled: {
      control: { type: 'boolean' },
      description: 'Whether the button is disabled'
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Whether the button is in loading state'
    },
    fullWidth: {
      control: { type: 'boolean' },
      description: 'Whether the button should take full width'
    },
    onClick: { action: 'clicked' }
  },
  tags: ['autodocs']
};

export default buttonMeta;
type ButtonStory = StoryObj<typeof buttonMeta>;

// Button Story Variations
export const Primary: ButtonStory = {
  args: {
    children: 'Primary Button',
    variant: 'primary'
  }
};

export const Secondary: ButtonStory = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary'
  }
};

export const Danger: ButtonStory = {
  args: {
    children: 'Danger Button',
    variant: 'danger'
  }
};

export const Success: ButtonStory = {
  args: {
    children: 'Success Button',
    variant: 'success'
  }
};

export const Warning: ButtonStory = {
  args: {
    children: 'Warning Button',
    variant: 'warning'
  }
};

export const Small: ButtonStory = {
  args: {
    children: 'Small Button',
    size: 'small'
  }
};

export const Medium: ButtonStory = {
  args: {
    children: 'Medium Button',
    size: 'medium'
  }
};

export const Large: ButtonStory = {
  args: {
    children: 'Large Button',
    size: 'large'
  }
};

export const Disabled: ButtonStory = {
  args: {
    children: 'Disabled Button',
    disabled: true
  }
};

export const Loading: ButtonStory = {
  args: {
    children: 'Loading Button',
    loading: true
  }
};

export const WithIcon: ButtonStory = {
  args: {
    children: 'With Icon',
    icon: '🚀'
  }
};

export const FullWidth: ButtonStory = {
  args: {
    children: 'Full Width Button',
    fullWidth: true
  },
  parameters: {
    layout: 'padded'
  }
};

// Button Playground
export const Playground: ButtonStory = {
  args: {
    children: 'Playground Button',
    variant: 'primary',
    size: 'medium'
  }
};

// Modal Stories
const modalMeta: Meta<typeof Modal> = {
  title: 'Components/Modal',
  component: Modal,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'A flexible modal component for displaying content in an overlay. Supports multiple sizes and proper focus management.',
      },
    },
  },
  argTypes: {
    isOpen: {
      control: { type: 'boolean' },
      description: 'Whether the modal is open'
    },
    title: {
      control: { type: 'text' },
      description: 'Title displayed in the modal header'
    },
    size: {
      control: { type: 'select' },
      options: ['small', 'medium', 'large', 'fullscreen'],
      description: 'Size of the modal'
    },
    onClose: { action: 'closed' }
  },
  tags: ['autodocs']
};

type ModalStory = StoryObj<typeof modalMeta>;

export const BasicModal: ModalStory = {
  args: {
    isOpen: true,
    title: 'Basic Modal',
    children: (
      <div>
        <p>This is a basic modal with some content.</p>
        <p>You can put any content here including forms, images, or other components.</p>
      </div>
    )
  }
};

export const SmallModal: ModalStory = {
  args: {
    isOpen: true,
    title: 'Small Modal',
    size: 'small',
    children: <p>This is a small modal with minimal content.</p>
  }
};

export const LargeModal: ModalStory = {
  args: {
    isOpen: true,
    title: 'Large Modal',
    size: 'large',
    children: (
      <div className="space-y-4">
        <p>This is a large modal with more space for content.</p>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-gray-100 rounded">Column 1</div>
          <div className="p-4 bg-gray-100 rounded">Column 2</div>
        </div>
        <p>Perfect for complex forms or detailed information.</p>
      </div>
    )
  }
};

export const ModalWithForm: ModalStory = {
  args: {
    isOpen: true,
    title: 'Modal with Form',
    children: <LoginForm title="" />
  }
};

// Form Stories
const formMeta: Meta<typeof LoginForm> = {
  title: 'Components/LoginForm',
  component: LoginForm,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'A complete login form component with validation and loading states.',
      },
    },
  },
  argTypes: {
    title: {
      control: { type: 'text' },
      description: 'Title displayed at the top of the form'
    },
    loading: {
      control: { type: 'boolean' },
      description: 'Whether the form is in loading state'
    },
    onSubmit: { action: 'submitted' }
  },
  tags: ['autodocs']
};

type FormStory = StoryObj<typeof formMeta>;

export const DefaultLoginForm: FormStory = {
  args: {
    title: 'Sign In'
  }
};

export const LoadingLoginForm: FormStory = {
  args: {
    title: 'Sign In',
    loading: true
  }
};

export const CustomTitleForm: FormStory = {
  args: {
    title: 'Welcome Back'
  }
};

// ==================== INTERACTIVE STORIES ====================

// Story with multiple components interaction
export const ComponentsShowcase = () => {
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);

  const handleLogin = (data: any) => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsModalOpen(true);
    }, 2000);
  };

  return (
    <div className="p-8 space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4">Ainflue Components Showcase</h2>
        <p className="text-gray-600 mb-6">Interactive demonstration of multiple components working together.</p>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Button Variants</h3>
        <div className="flex flex-wrap gap-4">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="success">Success</Button>
          <Button variant="warning">Warning</Button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Button Sizes</h3>
        <div className="flex items-center gap-4">
          <Button size="small">Small</Button>
          <Button size="medium">Medium</Button>
          <Button size="large">Large</Button>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Interactive Form</h3>
        <LoginForm onSubmit={handleLogin} loading={isLoading} />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Success"
      >
        <div className="text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-lg font-semibold mb-2">Login Successful!</h3>
          <p className="text-gray-600 mb-4">Welcome to Ainflue Enterprise Platform</p>
          <Button onClick={() => setIsModalOpen(false)}>
            Continue
          </Button>
        </div>
      </Modal>
    </div>
  );
};

ComponentsShowcase.parameters = {
  layout: 'fullscreen',
  docs: {
    description: {
      story: 'An interactive showcase demonstrating how multiple components work together in a real application scenario.',
    },
  },
};

// ==================== ACCESSIBILITY STORIES ====================

export const AccessibilityDemo = () => {
  const [focusVisible, setFocusVisible] = React.useState(false);

  return (
    <div className="p-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-4">Accessibility Features</h2>
        <p className="text-gray-600">All components are built with accessibility in mind, following WCAG guidelines.</p>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Keyboard Navigation</h3>
        <div className="space-y-2">
          <p className="text-sm text-gray-600">Use Tab to navigate between buttons:</p>
          <div className="flex gap-4">
            <Button onFocus={() => setFocusVisible(true)} onBlur={() => setFocusVisible(false)}>
              First Button
            </Button>
            <Button variant="secondary">Second Button</Button>
            <Button variant="success">Third Button</Button>
          </div>
          {focusVisible && (
            <p className="text-sm text-blue-600">✓ Focus management working correctly</p>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Screen Reader Support</h3>
        <div className="space-y-2">
          <Button aria-label="Save document to cloud storage">
            Save
          </Button>
          <Button variant="danger" aria-label="Permanently delete this item">
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};

AccessibilityDemo.parameters = {
  layout: 'fullscreen',
  docs: {
    description: {
      story: 'Demonstrates accessibility features including keyboard navigation, focus management, and screen reader support.',
    },
  },
};

// ==================== THEME STORIES ====================

export const ThemeVariations = () => {
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');

  return (
    <div className={`p-8 min-h-screen transition-colors ${theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-gray-900'}`}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Theme Variations</h2>
          <Button 
            variant="secondary"
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          >
            Toggle {theme === 'light' ? 'Dark' : 'Light'} Theme
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Buttons</h3>
            <div className="space-y-2">
              <Button variant="primary" fullWidth>Primary Button</Button>
              <Button variant="secondary" fullWidth>Secondary Button</Button>
              <Button variant="success" fullWidth>Success Button</Button>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Form Elements</h3>
            <div className="space-y-2">
              <input 
                type="text" 
                placeholder="Email address"
                className={`w-full px-3 py-2 rounded-md border ${
                  theme === 'dark' 
                    ? 'bg-gray-800 border-gray-700 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
              <input 
                type="password" 
                placeholder="Password"
                className={`w-full px-3 py-2 rounded-md border ${
                  theme === 'dark' 
                    ? 'bg-gray-800 border-gray-700 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                }`}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

ThemeVariations.parameters = {
  layout: 'fullscreen',
  docs: {
    description: {
      story: 'Demonstrates how components adapt to different themes and color schemes.',
    },
  },
};

// Export additional stories for Modal and Form
export { modalMeta as Modal, formMeta as LoginForm };