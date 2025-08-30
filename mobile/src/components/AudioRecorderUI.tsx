/**
 * Audio Recorder UI - Professional Audio Recording Interface
 * 
 * Advanced audio recording interface with waveform visualization,
 * professional controls, and real-time audio processing.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import { AudioRecorderProps } from './types';

const AudioRecorderUI: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  settings,
  maxDuration = 300,
  enablePauseResume = true,
  style,
  testID,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevels, setAudioLevels] = useState<number[]>([]);
  const [pulseAnimation] = useState(new Animated.Value(1));

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRecording && !isPaused) {
      interval = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= maxDuration) {
            handleStop();
            return prev;
          }
          return prev + 0.1;
        });
        
        // Mock audio level
        const level = Math.random() * 100;
        setAudioLevels(prev => [...prev.slice(-49), level]);
      }, 100);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRecording, isPaused, maxDuration]);

  useEffect(() => {
    if (isRecording) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.2,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnimation, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnimation.stopAnimation();
      pulseAnimation.setValue(1);
    }
  }, [isRecording, pulseAnimation]);

  const handleRecord = useCallback(() => {
    if (!isRecording) {
      setIsRecording(true);
      setIsPaused(false);
      setRecordingTime(0);
      setAudioLevels([]);
    } else if (enablePauseResume) {
      setIsPaused(!isPaused);
    }
  }, [isRecording, isPaused, enablePauseResume]);

  const handleStop = useCallback(() => {
    setIsRecording(false);
    setIsPaused(false);
    
    // Mock recording data
    onRecordingComplete({
      uri: 'mock://recording.wav',
      duration: recordingTime,
      size: Math.floor(recordingTime * 1000 * 44.1 * 2), // Rough calculation
      format: settings.format,
      metadata: {
        timestamp: Date.now(),
        peakLevel: Math.max(...audioLevels),
        averageLevel: audioLevels.reduce((a, b) => a + b, 0) / audioLevels.length,
      },
    });
    
    setRecordingTime(0);
    setAudioLevels([]);
  }, [recordingTime, audioLevels, settings.format, onRecordingComplete]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const centisecs = Math.floor((seconds % 1) * 100);
    return `${mins}:${secs.toString().padStart(2, '0')}.${centisecs.toString().padStart(2, '0')}`;
  };

  const renderWaveform = () => (
    <View style={styles.waveformContainer}>
      {audioLevels.map((level, index) => (
        <View
          key={index}
          style={[
            styles.waveformBar,
            {
              height: Math.max(2, (level / 100) * 60),
              opacity: 1 - (audioLevels.length - index) * 0.02,
            },
          ]}
        />
      ))}
    </View>
  );

  const getCurrentLevel = () => {
    return audioLevels.length > 0 ? audioLevels[audioLevels.length - 1] : 0;
  };

  return (
    <View style={[styles.container, style]} testID={testID}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Audio Recorder</Text>
        <Text style={styles.settings}>
          {settings.quality} • {settings.format.toUpperCase()} • {settings.sampleRate}Hz
        </Text>
      </View>

      {/* Audio Level Indicator */}
      <View style={styles.levelContainer}>
        <Text style={styles.levelLabel}>Level</Text>
        <View style={styles.levelMeter}>
          <LinearGradient
            colors={['#10b981', '#f59e0b', '#ef4444']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.levelGradient}
          >
            <View
              style={[
                styles.levelIndicator,
                { width: `${getCurrentLevel()}%` },
              ]}
            />
          </LinearGradient>
        </View>
        <Text style={styles.levelValue}>{Math.round(getCurrentLevel())}%</Text>
      </View>

      {/* Waveform Visualization */}
      <View style={styles.visualizationContainer}>
        <Text style={styles.waveformTitle}>Waveform</Text>
        {renderWaveform()}
      </View>

      {/* Recording Time */}
      <View style={styles.timeContainer}>
        <Text style={styles.timeDisplay}>{formatTime(recordingTime)}</Text>
        <Text style={styles.maxTime}>Max: {formatTime(maxDuration)}</Text>
      </View>

      {/* Controls */}
      <View style={styles.controls}>
        <TouchableOpacity
          style={[
            styles.controlButton,
            styles.stopButton,
            !isRecording && styles.disabledButton,
          ]}
          onPress={handleStop}
          disabled={!isRecording}
        >
          <Icon name="stop" size={24} color="#ffffff" />
        </TouchableOpacity>

        <Animated.View
          style={[
            styles.recordButtonContainer,
            {
              transform: [{ scale: pulseAnimation }],
            },
          ]}
        >
          <TouchableOpacity
            style={[
              styles.recordButton,
              isRecording && styles.recordingButton,
              isPaused && styles.pausedButton,
            ]}
            onPress={handleRecord}
          >
            <LinearGradient
              colors={
                isRecording
                  ? isPaused
                    ? ['#f59e0b', '#d97706']
                    : ['#ef4444', '#dc2626']
                  : ['#3b82f6', '#1d4ed8']
              }
              style={styles.recordButtonGradient}
            >
              <Icon
                name={
                  isRecording
                    ? isPaused
                      ? 'play'
                      : enablePauseResume
                      ? 'pause'
                      : 'stop'
                    : 'microphone'
                }
                size={32}
                color="#ffffff"
              />
            </LinearGradient>
          </TouchableOpacity>
        </Animated.View>

        <TouchableOpacity
          style={styles.controlButton}
          onPress={() => {
            // Settings would open a modal
            console.log('Open settings');
          }}
        >
          <Icon name="cog" size={24} color="#94a3b8" />
        </TouchableOpacity>
      </View>

      {/* Status */}
      <View style={styles.statusContainer}>
        <View style={styles.statusItem}>
          <Icon
            name={
              isRecording
                ? isPaused
                  ? 'pause-circle'
                  : 'record-circle'
                : 'stop-circle'
            }
            size={16}
            color={
              isRecording
                ? isPaused
                  ? '#f59e0b'
                  : '#ef4444'
                : '#6b7280'
            }
          />
          <Text style={styles.statusText}>
            {isRecording
              ? isPaused
                ? 'Paused'
                : 'Recording'
              : 'Ready'}
          </Text>
        </View>

        <View style={styles.statusItem}>
          <Icon name="file-music" size={16} color="#6b7280" />
          <Text style={styles.statusText}>
            {settings.bitRate}kbps • {settings.channels}ch
          </Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  settings: {
    fontSize: 14,
    color: '#94a3b8',
  },
  levelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 30,
  },
  levelLabel: {
    fontSize: 14,
    color: '#ffffff',
    width: 50,
  },
  levelMeter: {
    flex: 1,
    height: 8,
    backgroundColor: '#1e293b',
    borderRadius: 4,
    marginHorizontal: 12,
    overflow: 'hidden',
  },
  levelGradient: {
    flex: 1,
    opacity: 0.3,
  },
  levelIndicator: {
    height: '100%',
    backgroundColor: '#ffffff',
  },
  levelValue: {
    fontSize: 12,
    color: '#94a3b8',
    width: 35,
    textAlign: 'right',
  },
  visualizationContainer: {
    flex: 1,
    marginBottom: 30,
  },
  waveformTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 16,
    textAlign: 'center',
  },
  waveformContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  waveformBar: {
    width: 3,
    backgroundColor: '#3b82f6',
    marginHorizontal: 1,
    borderRadius: 1.5,
    minHeight: 2,
  },
  timeContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  timeDisplay: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    fontFamily: 'monospace',
  },
  maxTime: {
    fontSize: 14,
    color: '#6b7280',
    marginTop: 4,
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#1e293b',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 20,
  },
  disabledButton: {
    opacity: 0.5,
  },
  stopButton: {
    backgroundColor: '#374151',
  },
  recordButtonContainer: {
    marginHorizontal: 20,
  },
  recordButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
  },
  recordButtonGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingButton: {
    shadowColor: '#ef4444',
    shadowOffset: {
      width: 0,
      height: 0,
    },
    shadowOpacity: 0.8,
    shadowRadius: 10,
    elevation: 10,
  },
  pausedButton: {
    shadowColor: '#f59e0b',
  },
  statusContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 6,
  },
});

export default AudioRecorderUI;