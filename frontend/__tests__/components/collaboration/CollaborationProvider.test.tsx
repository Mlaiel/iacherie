/**
 * 🧪 Collaboration Provider Tests - Real-time Collaboration Testing
 * 
 * @fileoverview Test suite for CollaborationProvider component
 * @author Fahed Mlaiel <mlaiel@live.de>
 * @role Testing Expert + Collaboration Specialist
 * @copyright 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import '@testing-library/jest-dom';
import { CollaborationProvider, useCollaboration } from '../../../components/collaboration/CollaborationProvider';

// Mock WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  readyState: WebSocket.OPEN,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

// Mock the hooks module
jest.mock('../../../core/api/hooks', () => ({
  useWebSocket: jest.fn(() => ({
    isConnected: true,
    lastMessage: null,
    sendMessage: jest.fn(),
    connect: jest.fn(),
    disconnect: jest.fn()
  }))
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Test component using collaboration
function TestCollaborationComponent() {
  const { 
    activeUsers, 
    currentUser, 
    isConnected, 
    updatePresence, 
    sendCursorUpdate,
    setTypingStatus,
    joinRoom,
    leaveRoom,
    currentRoom 
  } = useCollaboration();

  return (
    <div>
      <div data-testid="connection-status">
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      
      <div data-testid="current-user">
        {currentUser?.userName || 'No user'}
      </div>
      
      <div data-testid="active-users-count">
        {Object.keys(activeUsers).length}
      </div>
      
      <div data-testid="current-room">
        {currentRoom || 'No room'}
      </div>
      
      <button 
        onClick={() => updatePresence({ status: 'busy' })}
        data-testid="update-presence"
      >
        Update Presence
      </button>
      
      <button 
        onClick={() => sendCursorUpdate(100, 200)}
        data-testid="send-cursor"
      >
        Send Cursor
      </button>
      
      <button 
        onClick={() => setTypingStatus(true)}
        data-testid="start-typing"
      >
        Start Typing
      </button>
      
      <button 
        onClick={() => setTypingStatus(false)}
        data-testid="stop-typing"
      >
        Stop Typing
      </button>
      
      <button 
        onClick={() => joinRoom('test-room')}
        data-testid="join-room"
      >
        Join Room
      </button>
      
      <button 
        onClick={() => leaveRoom()}
        data-testid="leave-room"
      >
        Leave Room
      </button>
    </div>
  );
}

describe('CollaborationProvider', () => {
  const mockProps = {
    userId: 'user-123',
    userName: 'Test User',
    userAvatar: 'https://example.com/avatar.jpg'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: { pathname: '/test-page' },
      writable: true
    });
  });

  const renderWithProvider = (children: React.ReactNode) => {
    return render(
      <CollaborationProvider {...mockProps}>
        {children}
      </CollaborationProvider>
    );
  };

  describe('Basic Functionality', () => {
    test('should render without crashing', () => {
      renderWithProvider(<TestCollaborationComponent />);
      expect(screen.getByTestId('connection-status')).toBeInTheDocument();
    });

    test('should initialize with current user', async () => {
      renderWithProvider(<TestCollaborationComponent />);
      
      await waitFor(() => {
        expect(screen.getByTestId('current-user')).toHaveTextContent('Test User');
        expect(screen.getByTestId('active-users-count')).toHaveTextContent('1');
      });
    });

    test('should show connection status', () => {
      renderWithProvider(<TestCollaborationComponent />);
      expect(screen.getByTestId('connection-status')).toHaveTextContent('Connected');
    });
  });

  describe('Presence Management', () => {
    test('should update presence when updatePresence is called', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      fireEvent.click(screen.getByTestId('update-presence'));
      
      await waitFor(() => {
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'presence_update',
          userId: 'user-123',
          data: { status: 'busy' }
        });
      });
    });

    test('should send cursor updates', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      // First join a room to enable cursor updates
      fireEvent.click(screen.getByTestId('join-room'));
      
      await waitFor(() => {
        expect(screen.getByTestId('current-room')).toHaveTextContent('test-room');
      });

      fireEvent.click(screen.getByTestId('send-cursor'));
      
      await waitFor(() => {
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'cursor_move',
          userId: 'user-123',
          data: { cursor: { x: 100, y: 200 } }
        });
      });
    });

    test('should handle typing status', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      // Join room first
      fireEvent.click(screen.getByTestId('join-room'));
      
      // Start typing
      fireEvent.click(screen.getByTestId('start-typing'));
      
      await waitFor(() => {
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'typing_start',
          userId: 'user-123',
          data: { isTyping: true }
        });
      });

      // Stop typing
      fireEvent.click(screen.getByTestId('stop-typing'));
      
      await waitFor(() => {
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'typing_stop',
          userId: 'user-123',
          data: { isTyping: false }
        });
      });
    });
  });

  describe('Room Management', () => {
    test('should join room', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      fireEvent.click(screen.getByTestId('join-room'));
      
      await waitFor(() => {
        expect(screen.getByTestId('current-room')).toHaveTextContent('test-room');
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'user_join',
          userId: 'user-123',
          data: expect.objectContaining({
            userName: 'Test User',
            roomId: 'test-room'
          })
        });
      });
    });

    test('should leave room', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      // Join room first
      fireEvent.click(screen.getByTestId('join-room'));
      
      await waitFor(() => {
        expect(screen.getByTestId('current-room')).toHaveTextContent('test-room');
      });

      // Leave room
      fireEvent.click(screen.getByTestId('leave-room'));
      
      await waitFor(() => {
        expect(screen.getByTestId('current-room')).toHaveTextContent('No room');
        expect(mockSendMessage).toHaveBeenCalledWith({
          type: 'user_leave',
          userId: 'user-123',
          data: { roomId: 'test-room' }
        });
      });
    });
  });

  describe('WebSocket Message Handling', () => {
    test('should handle user_join messages', async () => {
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      
      // Start with no message
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: jest.fn()
      });

      const { rerender } = renderWithProvider(<TestCollaborationComponent />);
      
      // Simulate receiving a user_join message
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: {
          type: 'user_join',
          userId: 'user-456',
          timestamp: new Date().toISOString(),
          data: {
            userId: 'user-456',
            userName: 'New User',
            status: 'online'
          }
        },
        sendMessage: jest.fn()
      });

      rerender(
        <CollaborationProvider {...mockProps}>
          <TestCollaborationComponent />
        </CollaborationProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('active-users-count')).toHaveTextContent('2');
      });
    });

    test('should handle user_leave messages', async () => {
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      
      // Start with a user present
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: {
          type: 'user_join',
          userId: 'user-456',
          timestamp: new Date().toISOString(),
          data: {
            userId: 'user-456',
            userName: 'New User',
            status: 'online'
          }
        },
        sendMessage: jest.fn()
      });

      const { rerender } = renderWithProvider(<TestCollaborationComponent />);
      
      await waitFor(() => {
        expect(screen.getByTestId('active-users-count')).toHaveTextContent('2');
      });

      // Simulate user leaving
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: {
          type: 'user_leave',
          userId: 'user-456',
          timestamp: new Date().toISOString(),
          data: {}
        },
        sendMessage: jest.fn()
      });

      rerender(
        <CollaborationProvider {...mockProps}>
          <TestCollaborationComponent />
        </CollaborationProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('active-users-count')).toHaveTextContent('1');
      });
    });
  });

  describe('Context Error Handling', () => {
    test('should throw error when useCollaboration is used outside provider', () => {
      const originalError = console.error;
      console.error = jest.fn();

      expect(() => {
        render(<TestCollaborationComponent />);
      }).toThrow('useCollaboration must be used within a CollaborationProvider');

      console.error = originalError;
    });
  });

  describe('Performance', () => {
    test('should handle rapid presence updates efficiently', async () => {
      const mockSendMessage = jest.fn();
      const mockUseWebSocket = require('../../../core/api/hooks').useWebSocket;
      mockUseWebSocket.mockReturnValue({
        isConnected: true,
        lastMessage: null,
        sendMessage: mockSendMessage
      });

      renderWithProvider(<TestCollaborationComponent />);
      
      const startTime = performance.now();
      
      // Rapidly update presence
      for (let i = 0; i < 50; i++) {
        fireEvent.click(screen.getByTestId('update-presence'));
      }
      
      const endTime = performance.now();
      
      // Should complete quickly
      expect(endTime - startTime).toBeLessThan(1000);
      
      // Should have sent all messages
      expect(mockSendMessage).toHaveBeenCalledTimes(50);
    });
  });
});

export { TestCollaborationComponent };