/**
 * Media Context - Media player and processing context
 */

import { createContext, useContext, ReactNode, useState } from 'react';

interface MediaItem {
  id: string;
  url: string;
  type: 'audio' | 'video';
  duration: number;
  title: string;
}

interface MediaContextType {
  currentMedia: MediaItem | null;
  isPlaying: boolean;
  currentTime: number;
  volume: number;
  playMedia: (media: MediaItem) => void;
  pauseMedia: () => void;
  stopMedia: () => void;
  seekTo: (time: number) => void;
  setVolume: (volume: number) => void;
}

const MediaContext = createContext<MediaContextType | undefined>(undefined);

export function MediaProvider({ children }: { children: ReactNode }) {
  const [currentMedia, setCurrentMedia] = useState<MediaItem | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [volume, setVolumeState] = useState(1);

  const playMedia = (media: MediaItem) => {
    setCurrentMedia(media);
    setIsPlaying(true);
  };

  const pauseMedia = () => {
    setIsPlaying(false);
  };

  const stopMedia = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    setCurrentMedia(null);
  };

  const seekTo = (time: number) => {
    setCurrentTime(time);
  };

  const setVolume = (newVolume: number) => {
    setVolumeState(Math.max(0, Math.min(1, newVolume)));
  };

  return (
    <MediaContext.Provider value={{
      currentMedia,
      isPlaying,
      currentTime,
      volume,
      playMedia,
      pauseMedia,
      stopMedia,
      seekTo,
      setVolume,
    }}>
      {children}
    </MediaContext.Provider>
  );
}

export const useMedia = () => {
  const context = useContext(MediaContext);
  if (!context) {
    throw new Error('useMedia must be used within a MediaProvider');
  }
  return context;
};
