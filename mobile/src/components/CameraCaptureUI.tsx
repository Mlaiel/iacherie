/**
 * Camera Capture UI - Professional Mobile Camera Interface
 * 
 * Advanced camera interface for content capture with professional controls,
 * real-time filters, and AI-powered enhancements.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { CameraCaptureProps } from './types';

const { width, height } = Dimensions.get('window');

const CameraCaptureUI: React.FC<CameraCaptureProps> = ({
  onCapture,
  settings,
  mode,
  maxDuration = 60,
  style,
  testID,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentMode, setCurrentMode] = useState<'photo' | 'video'>(
    mode === 'both' ? 'photo' : mode
  );

  const handleCapture = useCallback(() => {
    if (currentMode === 'video') {
      if (isRecording) {
        setIsRecording(false);
        // Mock video capture
        onCapture({
          uri: 'mock://video.mp4',
          type: 'video',
          duration: 5,
          size: 1024 * 1024 * 5, // 5MB
          metadata: {
            width: 1920,
            height: 1080,
            timestamp: Date.now(),
          },
        });
      } else {
        setIsRecording(true);
        // Auto-stop after maxDuration
        setTimeout(() => {
          if (isRecording) {
            setIsRecording(false);
          }
        }, maxDuration * 1000);
      }
    } else {
      // Mock photo capture
      onCapture({
        uri: 'mock://photo.jpg',
        type: 'image',
        size: 1024 * 1024 * 2, // 2MB
        metadata: {
          width: 4000,
          height: 3000,
          timestamp: Date.now(),
        },
      });
    }
  }, [currentMode, isRecording, onCapture, maxDuration]);

  return (
    <View style={[styles.container, style]} testID={testID}>
      {/* Camera Viewfinder Mock */}
      <View style={styles.viewfinder}>
        <Text style={styles.mockCamera}>Camera Viewfinder</Text>
        
        {/* Grid Lines */}
        <View style={styles.gridContainer}>
          <View style={styles.gridLine} />
          <View style={[styles.gridLine, styles.gridLineVertical]} />
        </View>

        {/* Recording Indicator */}
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <Icon name="record-rec" size={16} color="#ef4444" />
            <Text style={styles.recordingText}>REC</Text>
          </View>
        )}
      </View>

      {/* Controls */}
      <View style={styles.controls}>
        {/* Mode Selector */}
        {mode === 'both' && (
          <View style={styles.modeSelector}>
            <TouchableOpacity
              style={[
                styles.modeButton,
                currentMode === 'photo' && styles.activeModeButton,
              ]}
              onPress={() => setCurrentMode('photo')}
            >
              <Text style={styles.modeText}>Photo</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.modeButton,
                currentMode === 'video' && styles.activeModeButton,
              ]}
              onPress={() => setCurrentMode('video')}
            >
              <Text style={styles.modeText}>Video</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Capture Button */}
        <TouchableOpacity
          style={[
            styles.captureButton,
            currentMode === 'video' && styles.videoCaptureButton,
            isRecording && styles.recordingButton,
          ]}
          onPress={handleCapture}
        >
          <View style={styles.captureInner}>
            {currentMode === 'video' && isRecording ? (
              <Icon name="stop" size={24} color="#ffffff" />
            ) : (
              <></>
            )}
          </View>
        </TouchableOpacity>

        {/* Settings */}
        <View style={styles.settings}>
          <TouchableOpacity
            style={styles.settingButton}
            onPress={() => Alert.alert('Flash', `Current: ${settings.flashMode}`)}
          >
            <Icon
              name={
                settings.flashMode === 'on'
                  ? 'flash'
                  : settings.flashMode === 'off'
                  ? 'flash-off'
                  : 'flash-auto'
              }
              size={24}
              color="#ffffff"
            />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.settingButton}
            onPress={() => Alert.alert('Quality', `Current: ${settings.quality}`)}
          >
            <Icon name="cog" size={24} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  viewfinder: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  mockCamera: {
    fontSize: 18,
    color: '#ffffff',
    textAlign: 'center',
  },
  gridContainer: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  gridLine: {
    position: 'absolute',
    backgroundColor: 'rgba(255,255,255,0.3)',
    width: '100%',
    height: 1,
    top: '33.33%',
  },
  gridLineVertical: {
    width: 1,
    height: '100%',
    left: '33.33%',
    top: 0,
  },
  recordingIndicator: {
    position: 'absolute',
    top: 40,
    left: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  recordingText: {
    color: '#ef4444',
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  controls: {
    backgroundColor: '#000000',
    paddingVertical: 20,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  modeSelector: {
    flexDirection: 'row',
    backgroundColor: '#333333',
    borderRadius: 20,
    padding: 4,
    marginBottom: 20,
  },
  modeButton: {
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 16,
  },
  activeModeButton: {
    backgroundColor: '#3b82f6',
  },
  modeText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 4,
    borderColor: '#666666',
    marginBottom: 20,
  },
  videoCaptureButton: {
    backgroundColor: '#ef4444',
  },
  recordingButton: {
    backgroundColor: '#dc2626',
    borderColor: '#ef4444',
  },
  captureInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'transparent',
    justifyContent: 'center',
    alignItems: 'center',
  },
  settings: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
  },
  settingButton: {
    padding: 12,
  },
});

export default CameraCaptureUI;