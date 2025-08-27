/**
 * Frontend Integration Tests for Ainflue Platform
 * Tests the main dashboard and upload functionality
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Dashboard } from '../components/dashboard/Dashboard';
import { UploadInterface } from '../components/upload/UploadInterface';

// Mock fetch for API calls
global.fetch = jest.fn();

describe('Dashboard Component', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  test('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText('Ainflue Dashboard')).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    render(<Dashboard />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('displays metric cards after loading', async () => {
    // Mock successful API response
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        totalContent: 1247,
        protectedFiles: 1198,
        monthlyRevenue: 24580,
        activeMonitoring: 892,
        totalViolations: 43,
        resolvedViolations: 38,
        revenueGrowth: 12.5,
        contentGrowth: 8.3,
      }),
    });

    render(<Dashboard />);

    // Wait for metrics to load
    await waitFor(() => {
      expect(screen.getByText('Total Content')).toBeInTheDocument();
      expect(screen.getByText('Protected Files')).toBeInTheDocument();
      expect(screen.getByText('Monthly Revenue')).toBeInTheDocument();
      expect(screen.getByText('Active Monitoring')).toBeInTheDocument();
    });
  });

  test('shows upload button', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Upload Content')).toBeInTheDocument();
    });
  });

  test('displays system status', async () => {
    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument();
      expect(screen.getByText('API Status')).toBeInTheDocument();
      expect(screen.getByText('Fingerprinting Engine')).toBeInTheDocument();
    });
  });
});

describe('Upload Interface Component', () => {
  test('renders upload interface', () => {
    render(<UploadInterface />);
    expect(screen.getByText('Upload Content')).toBeInTheDocument();
    expect(screen.getByText('Drag & drop files here, or click to select files')).toBeInTheDocument();
  });

  test('shows supported file types', () => {
    render(<UploadInterface />);
    expect(screen.getByText(/Supports: Audio.*Video.*Images.*Text/)).toBeInTheDocument();
  });

  test('displays feature information', () => {
    render(<UploadInterface />);
    
    expect(screen.getByText('Audio Fingerprinting')).toBeInTheDocument();
    expect(screen.getByText('Video Protection')).toBeInTheDocument();
    expect(screen.getByText('Image Recognition')).toBeInTheDocument();
    
    expect(screen.getByText(/Advanced audio analysis/)).toBeInTheDocument();
    expect(screen.getByText(/Frame-by-frame analysis/)).toBeInTheDocument();
    expect(screen.getByText(/CLIP embeddings/)).toBeInTheDocument();
  });

  test('handles file selection', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    
    // Create a mock file
    const file = new File(['test content'], 'test.mp3', { type: 'audio/mpeg' });
    
    // Simulate file selection
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    // Should display the uploaded file
    expect(screen.getByText('test.mp3')).toBeInTheDocument();
    expect(screen.getByText('audio')).toBeInTheDocument();
  });

  test('shows upload button when files are selected', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const file = new File(['test'], 'test.mp3', { type: 'audio/mpeg' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    expect(screen.getByText('Upload 1 File')).toBeInTheDocument();
  });

  test('allows file removal', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const file = new File(['test'], 'test.mp3', { type: 'audio/mpeg' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    // Find and click remove button
    const removeButton = screen.getByRole('button', { name: /remove/i });
    fireEvent.click(removeButton);
    
    // File should be removed
    expect(screen.queryByText('test.mp3')).not.toBeInTheDocument();
  });

  test('handles upload process', async () => {
    // Mock successful upload
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const file = new File(['test'], 'test.mp3', { type: 'audio/mpeg' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    const uploadButton = screen.getByText('Upload 1 File');
    fireEvent.click(uploadButton);
    
    // Should show uploading state
    expect(screen.getByText('Uploading...')).toBeInTheDocument();
    
    // Wait for upload to complete
    await waitFor(() => {
      expect(screen.queryByText('Uploading...')).not.toBeInTheDocument();
    });
  });
});

describe('Integration Tests', () => {
  test('dashboard shows proper metrics format', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      // Check that numbers are properly formatted
      expect(screen.getByText('1,247')).toBeInTheDocument(); // Total content
      expect(screen.getByText('1,198')).toBeInTheDocument(); // Protected files
      expect(screen.getByText('$24,580')).toBeInTheDocument(); // Revenue
    });
  });

  test('upload interface shows proper file size formatting', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    const file = new File(['x'.repeat(1024)], 'test.mp3', { type: 'audio/mpeg' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });
    
    fireEvent.change(fileInput);
    
    // Should show formatted file size
    expect(screen.getByText('1 KB')).toBeInTheDocument();
  });

  test('components render without crashing', () => {
    expect(() => render(<Dashboard />)).not.toThrow();
    expect(() => render(<UploadInterface />)).not.toThrow();
  });
});

// Performance tests
describe('Performance Tests', () => {
  test('dashboard renders within acceptable time', async () => {
    const startTime = performance.now();
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Ainflue Dashboard')).toBeInTheDocument();
    });
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within 100ms
    expect(renderTime).toBeLessThan(100);
  });

  test('upload interface handles multiple files efficiently', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true }) as HTMLInputElement;
    
    // Create multiple files
    const files = Array.from({ length: 10 }, (_, i) => 
      new File([`content ${i}`], `test${i}.mp3`, { type: 'audio/mpeg' })
    );
    
    Object.defineProperty(fileInput, 'files', {
      value: files,
      writable: false,
    });
    
    const startTime = performance.now();
    fireEvent.change(fileInput);
    const endTime = performance.now();
    
    // Should handle 10 files quickly
    expect(endTime - startTime).toBeLessThan(50);
    
    // All files should be displayed
    expect(screen.getByText('Upload 10 Files')).toBeInTheDocument();
  });
});

// Accessibility tests
describe('Accessibility Tests', () => {
  test('dashboard has proper heading structure', () => {
    render(<Dashboard />);
    
    const mainHeading = screen.getByRole('heading', { level: 1 });
    expect(mainHeading).toHaveTextContent('Ainflue Dashboard');
  });

  test('upload interface has proper labels', () => {
    render(<UploadInterface />);
    
    const fileInput = screen.getByRole('textbox', { hidden: true });
    expect(fileInput).toHaveAttribute('accept');
    expect(fileInput).toHaveAttribute('multiple');
  });

  test('buttons have proper accessibility attributes', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      const uploadButton = screen.getByText('Upload Content');
      expect(uploadButton).toHaveAttribute('type', 'button');
    });
  });
});

export {};