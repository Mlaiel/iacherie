/**
 * 🧪 Toast Provider Tests - Comprehensive Testing Suite
 * 
 * @fileoverview Complete test suite for ToastProvider component
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Testing Expert + Lead Dev IA
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import '@testing-library/jest-dom';
import { ToastProvider, useToast, useToastHelpers } from '../../../components/notifications/ToastProvider';

// Mock the hooks module
jest.mock('../../../core/api/hooks', () => ({
  useNotifications: jest.fn(() => ({
    notifications: [],
    isConnected: true,
    unreadCount: 0,
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn()
  }))
}));

// Test component to use the toast context
function TestComponent() {
  const { showToast, dismissToast, dismissAll } = useToast();
  const { showSuccess, showError, showWarning, showInfo } = useToastHelpers();

  return (
    <div>
      <button 
        onClick={() => showToast({ 
          type: 'info', 
          title: 'Test Toast', 
          message: 'Test message' 
        })}
        data-testid="show-toast"
      >
        Show Toast
      </button>
      
      <button 
        onClick={() => showSuccess('Success!', 'Operation completed')}
        data-testid="show-success"
      >
        Show Success
      </button>
      
      <button 
        onClick={() => showError('Error!', 'Something went wrong')}
        data-testid="show-error"
      >
        Show Error
      </button>
      
      <button 
        onClick={() => showWarning('Warning!', 'Please be careful')}
        data-testid="show-warning"
      >
        Show Warning
      </button>
      
      <button 
        onClick={() => showInfo('Info', 'Useful information')}
        data-testid="show-info"
      >
        Show Info
      </button>
      
      <button onClick={dismissAll} data-testid="dismiss-all">
        Dismiss All
      </button>
    </div>
  );
}

describe('ToastProvider', () => {
  beforeEach(() => {
    jest.clearAllTimers();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  const renderWithProvider = (children: React.ReactNode) => {
    return render(
      <ToastProvider maxToasts={5} defaultDuration={5000}>
        {children}
      </ToastProvider>
    );
  };

  describe('Basic Toast Functionality', () => {
    test('should render without crashing', () => {
      renderWithProvider(<TestComponent />);
      expect(screen.getByTestId('show-toast')).toBeInTheDocument();
    });

    test('should show toast when showToast is called', async () => {
      renderWithProvider(<TestComponent />);
      
      fireEvent.click(screen.getByTestId('show-toast'));
      
      await waitFor(() => {
        expect(screen.getByText('Test Toast')).toBeInTheDocument();
        expect(screen.getByText('Test message')).toBeInTheDocument();
      });
    });

    test('should show different types of toasts', async () => {
      renderWithProvider(<TestComponent />);
      
      // Test success toast
      fireEvent.click(screen.getByTestId('show-success'));
      await waitFor(() => {
        expect(screen.getByText('Success!')).toBeInTheDocument();
        expect(screen.getByText('Operation completed')).toBeInTheDocument();
      });

      // Test error toast
      fireEvent.click(screen.getByTestId('show-error'));
      await waitFor(() => {
        expect(screen.getByText('Error!')).toBeInTheDocument();
        expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      });

      // Test warning toast
      fireEvent.click(screen.getByTestId('show-warning'));
      await waitFor(() => {
        expect(screen.getByText('Warning!')).toBeInTheDocument();
        expect(screen.getByText('Please be careful')).toBeInTheDocument();
      });

      // Test info toast
      fireEvent.click(screen.getByTestId('show-info'));
      await waitFor(() => {
        expect(screen.getByText('Info')).toBeInTheDocument();
        expect(screen.getByText('Useful information')).toBeInTheDocument();
      });
    });

    test('should auto-dismiss toast after specified duration', async () => {
      renderWithProvider(<TestComponent />);
      
      fireEvent.click(screen.getByTestId('show-toast'));
      
      await waitFor(() => {
        expect(screen.getByText('Test Toast')).toBeInTheDocument();
      });

      // Fast-forward time
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(screen.queryByText('Test Toast')).not.toBeInTheDocument();
      });
    });

    test('should limit number of visible toasts', async () => {
      renderWithProvider(<TestComponent />);
      
      // Show 6 toasts (more than maxToasts = 5)
      for (let i = 0; i < 6; i++) {
        fireEvent.click(screen.getByTestId('show-toast'));
      }

      await waitFor(() => {
        const toasts = screen.getAllByText('Test Toast');
        expect(toasts).toHaveLength(5); // Should only show 5 toasts
      });
    });

    test('should dismiss all toasts when dismissAll is called', async () => {
      renderWithProvider(<TestComponent />);
      
      // Show multiple toasts
      fireEvent.click(screen.getByTestId('show-success'));
      fireEvent.click(screen.getByTestId('show-error'));
      fireEvent.click(screen.getByTestId('show-warning'));

      await waitFor(() => {
        expect(screen.getByText('Success!')).toBeInTheDocument();
        expect(screen.getByText('Error!')).toBeInTheDocument();
        expect(screen.getByText('Warning!')).toBeInTheDocument();
      });

      // Dismiss all
      fireEvent.click(screen.getByTestId('dismiss-all'));

      await waitFor(() => {
        expect(screen.queryByText('Success!')).not.toBeInTheDocument();
        expect(screen.queryByText('Error!')).not.toBeInTheDocument();
        expect(screen.queryByText('Warning!')).not.toBeInTheDocument();
      });
    });
  });

  describe('WebSocket Integration', () => {
    test('should handle WebSocket notifications', async () => {
      const mockUseNotifications = require('../../../core/api/hooks').useNotifications;
      
      // Mock WebSocket notification
      mockUseNotifications.mockReturnValue({
        notifications: [{
          id: 'test-1',
          type: 'info',
          title: 'WebSocket Notification',
          message: 'From WebSocket',
          timestamp: new Date().toISOString(),
          isRead: false
        }],
        isConnected: true,
        unreadCount: 1,
        markAsRead: jest.fn(),
        markAllAsRead: jest.fn()
      });

      renderWithProvider(<TestComponent />);

      // The toast should appear automatically from WebSocket
      await waitFor(() => {
        expect(screen.getByText('WebSocket Notification')).toBeInTheDocument();
        expect(screen.getByText('From WebSocket')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    test('should handle rapid toast creation without performance issues', async () => {
      renderWithProvider(<TestComponent />);
      
      const startTime = performance.now();
      
      // Rapidly create many toasts
      for (let i = 0; i < 50; i++) {
        fireEvent.click(screen.getByTestId('show-toast'));
      }
      
      const endTime = performance.now();
      
      // Should complete quickly (less than 1 second)
      expect(endTime - startTime).toBeLessThan(1000);
      
      // Should still only show max toasts
      await waitFor(() => {
        const toasts = screen.getAllByText('Test Toast');
        expect(toasts).toHaveLength(5);
      });
    });
  });
});

// Export for use in other test files
export { TestComponent };