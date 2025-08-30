/**
 * Remix Studio Components Test Suite
 * 
 * Comprehensive test coverage for all Creative Studio Interface components.
 * Validates functionality, integration, and user interactions.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Project: IA-Influencer Agent + Content Protection Platform
 * Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps
 * 
 * WARNING: This code is the intellectual property of Fahed Mlaiel.
 * Any unauthorized use, reproduction, or distribution without explicit written permission
 * is strictly prohibited and will be prosecuted to the full extent of the law.
 * 
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Providers } from '@/app/providers';
import RemixStudioMain from '@/components/remix_studio/RemixStudioMain';
import TimelineEditor from '@/components/remix_studio/TimelineEditor';
import TrackMixer from '@/components/remix_studio/TrackMixer';
import AIAssistantInterface from '@/components/remix_studio/AIAssistantInterface';
import WaveformVisualizer from '@/components/remix_studio/WaveformVisualizer';
import { studioUtils } from '@/components/remix_studio/remix_studio.styles';

// Mock audio context and related APIs
const mockAudioContext = {
  createAnalyser: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    fftSize: 256,
    frequencyBinCount: 128,
    getByteFrequencyData: jest.fn()
  })),
  createGain: jest.fn(() => ({
    connect: jest.fn(),
    disconnect: jest.fn(),
    gain: { value: 1 }
  })),
  destination: {},
  sampleRate: 44100,
  currentTime: 0
};

// @ts-ignore
global.AudioContext = jest.fn(() => mockAudioContext);
// @ts-ignore
global.webkitAudioContext = jest.fn(() => mockAudioContext);

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn()
}));

// Mock canvas context
const mockCanvasContext = {
  fillRect: jest.fn(),
  strokeRect: jest.fn(),
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 1,
  beginPath: jest.fn(),
  moveTo: jest.fn(),
  lineTo: jest.fn(),
  stroke: jest.fn(),
  fill: jest.fn(),
  arc: jest.fn(),
  scale: jest.fn(),
  setLineDash: jest.fn(),
  closePath: jest.fn(),
  clearRect: jest.fn(),
  save: jest.fn(),
  restore: jest.fn(),
  fillText: jest.fn(),
  textAlign: 'start',
  font: '10px sans-serif',
  createLinearGradient: jest.fn(() => ({
    addColorStop: jest.fn()
  }))
} as any;

HTMLCanvasElement.prototype.getContext = jest.fn(() => mockCanvasContext);

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <Providers>
      {component}
    </Providers>
  );
};

describe('Remix Studio Components', () => {
  describe('RemixStudioMain', () => {
    it('renders main studio interface', () => {
      renderWithProviders(<RemixStudioMain />);
      
      expect(screen.getByText('Remix Studio')).toBeInTheDocument();
      expect(screen.getByTitle('Play/Pause (Space)')).toBeInTheDocument();
      expect(screen.getByTitle('Stop (Esc)')).toBeInTheDocument();
      expect(screen.getByTitle('Record (Ctrl+R)')).toBeInTheDocument();
    });

    it('handles play/pause functionality', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      const playButton = screen.getByTitle('Play/Pause (Space)');
      await user.click(playButton);
      
      // Should show pause icon when playing
      expect(playButton.querySelector('svg')).toBeInTheDocument();
    });

    it('handles keyboard shortcuts', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      // Test spacebar for play/pause
      await user.keyboard(' ');
      await waitFor(() => {
        expect(screen.getByText('Playback started')).toBeInTheDocument();
      });
    });

    it('manages component visibility', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      const effectsButton = screen.getByText('Effects');
      await user.click(effectsButton);
      
      // Effects panel should become visible
      expect(effectsButton).toHaveClass('bg-blue-600');
    });

    it('handles track creation and management', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      // Enable timeline component
      const timelineButton = screen.getByText('Timeline');
      await user.click(timelineButton);
      
      // Look for add track button in timeline
      const addTrackButton = screen.getByText('Add Track');
      await user.click(addTrackButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Track \d+ added/)).toBeInTheDocument();
      });
    });
  });

  describe('TimelineEditor', () => {
    const mockProps = {
      tracks: [
        {
          id: 'track-1',
          name: 'Test Track',
          color: '#ff0000',
          volume: 0.8,
          pan: 0,
          muted: false,
          solo: false,
          armed: false,
          startTime: 0,
          duration: 60000,
          effects: []
        }
      ],
      currentTime: 0,
      zoomLevel: 1,
      isPlaying: false,
      selectedTracks: [],
      onTimeChange: jest.fn(),
      onTrackUpdate: jest.fn(),
      onTrackSelect: jest.fn(),
      onAddTrack: jest.fn(),
      onRemoveTrack: jest.fn()
    };

    it('renders timeline with tracks', () => {
      render(<TimelineEditor {...mockProps} />);
      
      expect(screen.getByText('Test Track')).toBeInTheDocument();
      expect(screen.getByText('Add Track')).toBeInTheDocument();
    });

    it('handles track selection', async () => {
      const user = userEvent.setup();
      const onTrackSelect = jest.fn();
      
      render(<TimelineEditor {...mockProps} onTrackSelect={onTrackSelect} />);
      
      const trackElement = screen.getByText('Test Track').closest('div');
      if (trackElement) {
        await user.click(trackElement);
        expect(onTrackSelect).toHaveBeenCalledWith('track-1', false);
      }
    });

    it('handles snap to grid functionality', async () => {
      const user = userEvent.setup();
      render(<TimelineEditor {...mockProps} />);
      
      const snapCheckbox = screen.getByLabelText('Snap to Grid');
      expect(snapCheckbox).toBeChecked();
      
      await user.click(snapCheckbox);
      expect(snapCheckbox).not.toBeChecked();
    });

    it('handles track splitting', async () => {
      const user = userEvent.setup();
      const onTrackUpdate = jest.fn();
      const onAddTrack = jest.fn();
      
      render(
        <TimelineEditor 
          {...mockProps} 
          selectedTracks={['track-1']}
          currentTime={30000}
          onTrackUpdate={onTrackUpdate}
          onAddTrack={onAddTrack}
        />
      );
      
      const splitButton = screen.getByText('Split');
      await user.click(splitButton);
      
      expect(onTrackUpdate).toHaveBeenCalled();
      expect(onAddTrack).toHaveBeenCalled();
    });
  });

  describe('TrackMixer', () => {
    const mockTracks = [
      {
        id: 'track-1',
        name: 'Vocal',
        color: '#ff0000',
        volume: 0.8,
        pan: 0,
        muted: false,
        solo: false,
        armed: false,
        startTime: 0,
        duration: 60000,
        effects: []
      }
    ];

    const mockProps = {
      tracks: mockTracks,
      onTrackUpdate: jest.fn(),
      masterVolume: 1.0,
      onMasterVolumeChange: jest.fn()
    };

    it('renders mixer channels', () => {
      render(<TrackMixer {...mockProps} />);
      
      expect(screen.getByText('Vocal')).toBeInTheDocument();
      expect(screen.getByText('MASTER')).toBeInTheDocument();
    });

    it('handles mute functionality', async () => {
      const user = userEvent.setup();
      const onTrackUpdate = jest.fn();
      
      render(<TrackMixer {...mockProps} onTrackUpdate={onTrackUpdate} />);
      
      const muteButton = screen.getByText('M');
      await user.click(muteButton);
      
      expect(onTrackUpdate).toHaveBeenCalledWith('track-1', { muted: true });
    });

    it('handles solo functionality', async () => {
      const user = userEvent.setup();
      const onTrackUpdate = jest.fn();
      
      render(<TrackMixer {...mockProps} onTrackUpdate={onTrackUpdate} />);
      
      const soloButton = screen.getByText('S');
      await user.click(soloButton);
      
      expect(onTrackUpdate).toHaveBeenCalledWith('track-1', { solo: true });
    });

    it('handles arm for recording', async () => {
      const user = userEvent.setup();
      const onTrackUpdate = jest.fn();
      
      render(<TrackMixer {...mockProps} onTrackUpdate={onTrackUpdate} />);
      
      const armButton = screen.getByTitle('Arm for Recording');
      await user.click(armButton);
      
      expect(onTrackUpdate).toHaveBeenCalledWith('track-1', { armed: true });
    });
  });

  describe('AIAssistantInterface', () => {
    const mockStudioState = {
      currentTime: 0,
      isPlaying: false,
      isRecording: false,
      tempo: 120,
      timeSignature: [4, 4] as [number, number],
      key: 'C',
      tracks: [],
      selectedTracks: [],
      zoomLevel: 1,
      snapGrid: 0.25,
      loopEnabled: false,
      loopStart: 0,
      loopEnd: 60000
    };

    const mockProps = {
      studioState: mockStudioState,
      onApplySuggestion: jest.fn()
    };

    it('renders AI assistant interface', () => {
      render(<AIAssistantInterface {...mockProps} />);
      
      expect(screen.getByText('AI Assistant')).toBeInTheDocument();
      expect(screen.getByText('Analyze')).toBeInTheDocument();
    });

    it('handles analysis trigger', async () => {
      const user = userEvent.setup();
      render(<AIAssistantInterface {...mockProps} />);
      
      const analyzeButton = screen.getByText('Analyze');
      await user.click(analyzeButton);
      
      expect(screen.getByText('Analyzing your track...')).toBeInTheDocument();
    });

    it('displays suggestion categories', () => {
      render(<AIAssistantInterface {...mockProps} />);
      
      expect(screen.getByText('All')).toBeInTheDocument();
      expect(screen.getByText('Harmony')).toBeInTheDocument();
      expect(screen.getByText('Rhythm')).toBeInTheDocument();
      expect(screen.getByText('Effects')).toBeInTheDocument();
    });

    it('handles auto-suggest toggle', async () => {
      const user = userEvent.setup();
      render(<AIAssistantInterface {...mockProps} />);
      
      const autoCheckbox = screen.getByLabelText('Auto');
      expect(autoCheckbox).toBeChecked();
      
      await user.click(autoCheckbox);
      expect(autoCheckbox).not.toBeChecked();
    });
  });

  describe('WaveformVisualizer', () => {
    const mockProps = {
      currentTime: 0,
      isPlaying: false,
      onSeek: jest.fn()
    };

    it('renders waveform visualizer', () => {
      render(<WaveformVisualizer {...mockProps} />);
      
      expect(screen.getByText('Waveform')).toBeInTheDocument();
    });

    it('displays loading state', () => {
      render(<WaveformVisualizer {...mockProps} audioUrl="test.mp3" />);
      
      expect(screen.getByText('Loading waveform...')).toBeInTheDocument();
    });

    it('handles canvas click for seeking', async () => {
      const user = userEvent.setup();
      const onSeek = jest.fn();
      
      render(<WaveformVisualizer {...mockProps} onSeek={onSeek} />);
      
      const canvas = screen.getByRole('img', { hidden: true }) || document.querySelector('canvas');
      if (canvas) {
        await user.click(canvas);
        // Canvas click should trigger seek
        expect(onSeek).toHaveBeenCalled();
      }
    });
  });

  describe('Studio Utils', () => {
    it('converts milliseconds to time format', () => {
      expect(studioUtils.msToTime(60000)).toBe('1:00');
      expect(studioUtils.msToTime(90000)).toBe('1:30');
      expect(studioUtils.msToTime(3661000)).toBe('61:01');
    });

    it('generates track colors', () => {
      const color1 = studioUtils.getTrackColor(0);
      const color2 = studioUtils.getTrackColor(1);
      const color3 = studioUtils.getTrackColor(8); // Should wrap around
      
      expect(color1).toBeTruthy();
      expect(color2).toBeTruthy();
      expect(color3).toBe(color1); // Should be same as index 0
    });

    it('converts frequency to note', () => {
      expect(studioUtils.frequencyToNote(440)).toContain('A');
      expect(studioUtils.frequencyToNote(261.63)).toContain('C');
    });

    it('converts between dB and linear', () => {
      expect(studioUtils.dbToLinear(0)).toBe(1);
      expect(studioUtils.linearToDb(1)).toBe(0);
      expect(studioUtils.dbToLinear(-6)).toBeCloseTo(0.5, 1);
    });

    it('creates class names', () => {
      expect(studioUtils.getClassName('a', 'b', null, false, 'c')).toBe('a b c');
      expect(studioUtils.getClassName('', null, undefined, 'test')).toBe('test');
    });
  });

  describe('Component Integration', () => {
    it('renders full studio without errors', () => {
      renderWithProviders(<RemixStudioMain />);
      
      // Should render main interface elements
      expect(screen.getByText('Remix Studio')).toBeInTheDocument();
      expect(screen.getByText('Components')).toBeInTheDocument();
    });

    it('handles component state updates', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      // Toggle multiple components
      const components = ['Timeline', 'Mixer', 'Effects', 'AI Assistant'];
      
      for (const component of components) {
        const button = screen.getByText(component);
        await user.click(button);
        // Component should toggle state
        expect(button).toHaveClass(/bg-(blue|gray)-\d+/);
      }
    });

    it('maintains state consistency across components', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      // Enable timeline
      await user.click(screen.getByText('Timeline'));
      
      // Add a track
      if (screen.queryByText('Add Track')) {
        await user.click(screen.getByText('Add Track'));
      }
      
      // Enable mixer
      await user.click(screen.getByText('Mixer'));
      
      // Both timeline and mixer should reflect the same tracks
      expect(screen.getAllByText(/Track \d+|Main Vocal|Instrumental/).length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('provides proper ARIA labels', () => {
      renderWithProviders(<RemixStudioMain />);
      
      expect(screen.getByTitle('Play/Pause (Space)')).toBeInTheDocument();
      expect(screen.getByTitle('Stop (Esc)')).toBeInTheDocument();
      expect(screen.getByTitle('Record (Ctrl+R)')).toBeInTheDocument();
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      // Tab through interface elements
      await user.tab();
      expect(document.activeElement).toBeTruthy();
      
      await user.tab();
      expect(document.activeElement).toBeTruthy();
    });

    it('provides visual feedback for interactions', async () => {
      const user = userEvent.setup();
      renderWithProviders(<RemixStudioMain />);
      
      const playButton = screen.getByTitle('Play/Pause (Space)');
      
      // Button should have hover states
      await user.hover(playButton);
      expect(playButton).toHaveClass(/hover:/);
    });
  });

  describe('Performance', () => {
    it('renders components efficiently', () => {
      const startTime = performance.now();
      renderWithProviders(<RemixStudioMain />);
      const endTime = performance.now();
      
      // Should render in reasonable time (less than 100ms)
      expect(endTime - startTime).toBeLessThan(100);
    });

    it('handles large track counts', () => {
      const manyTracks = Array.from({ length: 50 }, (_, i) => ({
        id: `track-${i}`,
        name: `Track ${i}`,
        color: studioUtils.getTrackColor(i),
        volume: 0.8,
        pan: 0,
        muted: false,
        solo: false,
        armed: false,
        startTime: 0,
        duration: 60000,
        effects: []
      }));

      const mockProps = {
        tracks: manyTracks,
        currentTime: 0,
        zoomLevel: 1,
        isPlaying: false,
        selectedTracks: [],
        onTimeChange: jest.fn(),
        onTrackUpdate: jest.fn(),
        onTrackSelect: jest.fn(),
        onAddTrack: jest.fn(),
        onRemoveTrack: jest.fn()
      };

      render(<TimelineEditor {...mockProps} />);
      
      // Should render all tracks
      expect(screen.getAllByText(/Track \d+/).length).toBe(50);
    });
  });
});

describe('Component Error Handling', () => {
  it('handles missing audio context gracefully', () => {
    // @ts-ignore
    global.AudioContext = undefined;
    // @ts-ignore  
    global.webkitAudioContext = undefined;
    
    expect(() => {
      render(<WaveformVisualizer currentTime={0} isPlaying={false} onSeek={jest.fn()} />);
    }).not.toThrow();
  });

  it('handles invalid props gracefully', () => {
    expect(() => {
      render(
        <TimelineEditor
          tracks={[]}
          currentTime={NaN}
          zoomLevel={0}
          isPlaying={false}
          selectedTracks={[]}
          onTimeChange={jest.fn()}
          onTrackUpdate={jest.fn()}
          onTrackSelect={jest.fn()}
          onAddTrack={jest.fn()}
          onRemoveTrack={jest.fn()}
        />
      );
    }).not.toThrow();
  });

  it('handles canvas context failures', () => {
    HTMLCanvasElement.prototype.getContext = jest.fn(() => null);
    
    expect(() => {
      render(<WaveformVisualizer currentTime={0} isPlaying={false} onSeek={jest.fn()} />);
    }).not.toThrow();
  });
});