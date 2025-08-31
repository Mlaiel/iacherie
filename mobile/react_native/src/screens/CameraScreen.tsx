/**
 * Advanced Camera Screen - Professional Camera Interface
 * 
 * Enterprise-grade camera interface with AI enhancement,
 * professional controls, and content protection integration.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Alert,
  SafeAreaView,
  StatusBar,
  Animated,
  PanGestureHandler,
  State
} from 'react-native';
import { Camera, CameraType } from 'expo-camera';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import CameraService from '../services/CameraService';
import { useTheme } from '../hooks/useTheme';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface CameraMode {
  id: string;
  name: string;
  icon: string;
  description: string;
}

interface CameraSettings {
  quality: 'low' | 'medium' | 'high' | 'ultra';
  flash: 'auto' | 'on' | 'off';
  hdr: boolean;
  stabilization: boolean;
  aiEnhancement: boolean;
  timer: number;
}

const CameraScreen: React.FC = () => {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();
  const cameraRef = useRef<Camera>(null);
  const cameraService = CameraService.getInstance();
  
  // State management
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [type, setType] = useState(CameraType.back);
  const [isRecording, setIsRecording] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [currentMode, setCurrentMode] = useState<CameraMode>({
    id: 'photo',
    name: 'Photo',
    icon: 'camera',
    description: 'High-quality photo capture'
  });
  const [settings, setSettings] = useState<CameraSettings>({
    quality: 'high',
    flash: 'auto',
    hdr: true,
    stabilization: true,
    aiEnhancement: true,
    timer: 0
  });
  const [showSettings, setShowSettings] = useState(false);
  const [showModes, setShowModes] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [captureHistory, setCaptureHistory] = useState<any[]>([]);

  // Animation values
  const captureButtonScale = useRef(new Animated.Value(1)).current;
  const settingsOpacity = useRef(new Animated.Value(0)).current;
  const modesTranslateY = useRef(new Animated.Value(100)).current;

  // Camera modes
  const cameraModes: CameraMode[] = [
    { id: 'photo', name: 'Photo', icon: 'camera', description: 'High-quality photo capture' },
    { id: 'video', name: 'Video', icon: 'videocam', description: '4K video recording' },
    { id: 'portrait', name: 'Portrait', icon: 'person', description: 'AI-powered portrait mode' },
    { id: 'night', name: 'Night', icon: 'moon', description: 'Enhanced low-light capture' },
    { id: 'burst', name: 'Burst', icon: 'camera-burst', description: 'Multiple shots in sequence' },
    { id: 'panorama', name: 'Pano', icon: 'panorama', description: 'Wide panoramic shots' }
  ];

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  useEffect(() => {
    initializeCameraSession();
    loadCaptureHistory();
  }, [currentMode]);

  const initializeCameraSession = async () => {
    try {
      const sessionResult = await cameraService.startCaptureSession(
        currentMode.id === 'video' ? 'video' : 'photo',
        {
          quality: settings.quality,
          enableLocation: true,
          enableAI: settings.aiEnhancement,
          watermark: true
        }
      );

      if (sessionResult.success) {
        setActiveSession(sessionResult.data);
      }
    } catch (error) {
      console.error('Failed to initialize camera session:', error);
    }
  };

  const loadCaptureHistory = async () => {
    try {
      const historyResult = await cameraService.getCaptureHistory({
        limit: 10,
        type: currentMode.id === 'video' ? 'video' : 'photo'
      });

      if (historyResult.success) {
        setCaptureHistory(historyResult.data.captures);
      }
    } catch (error) {
      console.error('Failed to load capture history:', error);
    }
  };

  const handleCapture = async () => {
    if (!activeSession || isCapturing) return;

    setIsCapturing(true);
    animateCaptureButton();

    try {
      if (currentMode.id === 'video') {
        if (isRecording) {
          // Stop recording
          const result = await cameraService.stopVideoRecording(activeSession);
          if (result.success) {
            setIsRecording(false);
            await loadCaptureHistory();
            Alert.alert('Success', 'Video recorded successfully!');
          }
        } else {
          // Start recording
          const result = await cameraService.startVideoRecording({
            maxDuration: 300000, // 5 minutes
            stabilization: settings.stabilization,
            audioEnabled: true
          });
          if (result.success) {
            setIsRecording(true);
          }
        }
      } else {
        // Photo capture
        const captureOptions = {
          flash: settings.flash,
          timer: settings.timer,
          burst: currentMode.id === 'burst',
          burstCount: currentMode.id === 'burst' ? 5 : 1
        };

        const result = await cameraService.capturePhoto(captureOptions);
        if (result.success) {
          await loadCaptureHistory();
          Alert.alert('Success', 'Photo captured successfully!');
        }
      }
    } catch (error) {
      console.error('Capture failed:', error);
      Alert.alert('Error', 'Failed to capture. Please try again.');
    } finally {
      setIsCapturing(false);
    }
  };

  const animateCaptureButton = () => {
    Animated.sequence([
      Animated.timing(captureButtonScale, {
        toValue: 0.8,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(captureButtonScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const toggleSettings = () => {
    setShowSettings(!showSettings);
    Animated.timing(settingsOpacity, {
      toValue: showSettings ? 0 : 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const toggleModes = () => {
    setShowModes(!showModes);
    Animated.timing(modesTranslateY, {
      toValue: showModes ? 100 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const switchCamera = () => {
    setType(type === CameraType.back ? CameraType.front : CameraType.back);
  };

  const handleZoom = (event: any) => {
    const { translationY } = event.nativeEvent;
    const newZoom = Math.max(1, Math.min(10, zoomLevel - translationY / 100));
    setZoomLevel(newZoom);
  };

  const updateSetting = (key: keyof CameraSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  if (hasPermission === null) {
    return (
      <View style={[styles.container, { backgroundColor: theme.background }]}>
        <Text style={[styles.text, { color: theme.text }]}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={[styles.container, { backgroundColor: theme.background }]}>
        <Text style={[styles.text, { color: theme.text }]}>No access to camera</Text>
        <TouchableOpacity
          style={[styles.permissionButton, { backgroundColor: theme.primary }]}
          onPress={() => Camera.requestCameraPermissionsAsync()}
        >
          <Text style={[styles.permissionButtonText, { color: theme.white }]}>
            Grant Permission
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.black }]}>
      <StatusBar barStyle="light-content" backgroundColor={theme.black} />
      
      {/* Camera View */}
      <PanGestureHandler
        onGestureEvent={handleZoom}
        onHandlerStateChange={(event) => {
          if (event.nativeEvent.state === State.END) {
            // Zoom gesture ended
          }
        }}
      >
        <View style={styles.cameraContainer}>
          <Camera
            ref={cameraRef}
            style={styles.camera}
            type={type}
            zoom={zoomLevel}
            flashMode={settings.flash as any}
            videoStabilizationMode={settings.stabilization ? 'auto' : 'off'}
          >
            {/* Top Controls */}
            <View style={[styles.topControls, { paddingTop: insets.top }]}>
              <TouchableOpacity
                style={styles.topButton}
                onPress={() => {/* Navigate back */}}
              >
                <Ionicons name="arrow-back" size={24} color={theme.white} />
              </TouchableOpacity>

              <View style={styles.topCenterControls}>
                <TouchableOpacity
                  style={[styles.topButton, settings.hdr && styles.activeButton]}
                  onPress={() => updateSetting('hdr', !settings.hdr)}
                >
                  <Text style={[styles.topButtonText, { color: theme.white }]}>HDR</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.topButton, settings.aiEnhancement && styles.activeButton]}
                  onPress={() => updateSetting('aiEnhancement', !settings.aiEnhancement)}
                >
                  <MaterialIcons name="auto-awesome" size={20} color={theme.white} />
                </TouchableOpacity>
              </View>

              <TouchableOpacity
                style={styles.topButton}
                onPress={toggleSettings}
              >
                <Ionicons name="settings-outline" size={24} color={theme.white} />
              </TouchableOpacity>
            </View>

            {/* Zoom Indicator */}
            {zoomLevel > 1 && (
              <View style={styles.zoomIndicator}>
                <Text style={[styles.zoomText, { color: theme.white }]}>
                  {zoomLevel.toFixed(1)}x
                </Text>
              </View>
            )}

            {/* Recording Indicator */}
            {isRecording && (
              <View style={styles.recordingIndicator}>
                <View style={styles.recordingDot} />
                <Text style={[styles.recordingText, { color: theme.white }]}>REC</Text>
              </View>
            )}

            {/* Bottom Controls */}
            <View style={[styles.bottomControls, { paddingBottom: insets.bottom }]}>
              {/* Camera Modes */}
              <TouchableOpacity
                style={styles.modesButton}
                onPress={toggleModes}
              >
                <Text style={[styles.modeText, { color: theme.white }]}>
                  {currentMode.name}
                </Text>
                <Ionicons name="chevron-up" size={16} color={theme.white} />
              </TouchableOpacity>

              {/* Capture Controls */}
              <View style={styles.captureControls}>
                {/* Flash */}
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={() => {
                    const flashModes = ['auto', 'on', 'off'] as const;
                    const currentIndex = flashModes.indexOf(settings.flash);
                    const nextIndex = (currentIndex + 1) % flashModes.length;
                    updateSetting('flash', flashModes[nextIndex]);
                  }}
                >
                  <Ionicons
                    name={
                      settings.flash === 'on' ? 'flash' :
                      settings.flash === 'off' ? 'flash-off' : 'flash-outline'
                    }
                    size={24}
                    color={theme.white}
                  />
                </TouchableOpacity>

                {/* Capture Button */}
                <Animated.View style={{ transform: [{ scale: captureButtonScale }] }}>
                  <TouchableOpacity
                    style={[
                      styles.captureButton,
                      isRecording && styles.recordingButton,
                      { borderColor: theme.white }
                    ]}
                    onPress={handleCapture}
                    disabled={isCapturing}
                  >
                    <View style={[
                      styles.captureButtonInner,
                      isRecording ? styles.recordingButtonInner : { backgroundColor: theme.white }
                    ]} />
                  </TouchableOpacity>
                </Animated.View>

                {/* Switch Camera */}
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={switchCamera}
                >
                  <Ionicons name="camera-reverse-outline" size={24} color={theme.white} />
                </TouchableOpacity>
              </View>

              {/* Capture History Preview */}
              <TouchableOpacity style={styles.historyButton}>
                {captureHistory.length > 0 && (
                  <View style={styles.historyPreview}>
                    <Text style={[styles.historyCount, { color: theme.white }]}>
                      {captureHistory.length}
                    </Text>
                  </View>
                )}
                <Ionicons name="images-outline" size={24} color={theme.white} />
              </TouchableOpacity>
            </View>
          </Camera>
        </View>
      </PanGestureHandler>

      {/* Settings Panel */}
      <Animated.View
        style={[
          styles.settingsPanel,
          { 
            backgroundColor: theme.darkGray,
            opacity: settingsOpacity,
            right: showSettings ? 0 : -300
          }
        ]}
        pointerEvents={showSettings ? 'auto' : 'none'}
      >
        <Text style={[styles.settingsTitle, { color: theme.white }]}>Camera Settings</Text>
        
        <View style={styles.settingItem}>
          <Text style={[styles.settingLabel, { color: theme.lightGray }]}>Quality</Text>
          <View style={styles.settingButtons}>
            {['low', 'medium', 'high', 'ultra'].map((quality) => (
              <TouchableOpacity
                key={quality}
                style={[
                  styles.settingButton,
                  settings.quality === quality && { backgroundColor: theme.primary }
                ]}
                onPress={() => updateSetting('quality', quality)}
              >
                <Text style={[
                  styles.settingButtonText,
                  { color: settings.quality === quality ? theme.white : theme.lightGray }
                ]}>
                  {quality.toUpperCase()}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.settingItem}>
          <Text style={[styles.settingLabel, { color: theme.lightGray }]}>Timer</Text>
          <View style={styles.settingButtons}>
            {[0, 3, 5, 10].map((timer) => (
              <TouchableOpacity
                key={timer}
                style={[
                  styles.settingButton,
                  settings.timer === timer && { backgroundColor: theme.primary }
                ]}
                onPress={() => updateSetting('timer', timer)}
              >
                <Text style={[
                  styles.settingButtonText,
                  { color: settings.timer === timer ? theme.white : theme.lightGray }
                ]}>
                  {timer === 0 ? 'OFF' : `${timer}s`}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.settingItem}>
          <TouchableOpacity
            style={styles.settingToggle}
            onPress={() => updateSetting('stabilization', !settings.stabilization)}
          >
            <Text style={[styles.settingLabel, { color: theme.lightGray }]}>
              Image Stabilization
            </Text>
            <View style={[
              styles.toggle,
              { backgroundColor: settings.stabilization ? theme.primary : theme.gray }
            ]}>
              <View style={[
                styles.toggleDot,
                { transform: [{ translateX: settings.stabilization ? 20 : 2 }] }
              ]} />
            </View>
          </TouchableOpacity>
        </View>
      </Animated.View>

      {/* Camera Modes */}
      <Animated.View
        style={[
          styles.modesPanel,
          {
            backgroundColor: theme.darkGray,
            transform: [{ translateY: modesTranslateY }]
          }
        ]}
        pointerEvents={showModes ? 'auto' : 'none'}
      >
        <View style={styles.modesList}>
          {cameraModes.map((mode) => (
            <TouchableOpacity
              key={mode.id}
              style={[
                styles.modeItem,
                currentMode.id === mode.id && { backgroundColor: theme.primary }
              ]}
              onPress={() => {
                setCurrentMode(mode);
                toggleModes();
              }}
            >
              <Ionicons
                name={mode.icon as any}
                size={24}
                color={currentMode.id === mode.id ? theme.white : theme.lightGray}
              />
              <Text style={[
                styles.modeItemText,
                { color: currentMode.id === mode.id ? theme.white : theme.lightGray }
              ]}>
                {mode.name}
              </Text>
              <Text style={[
                styles.modeItemDescription,
                { color: currentMode.id === mode.id ? theme.white : theme.gray }
              ]}>
                {mode.description}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  text: {
    fontSize: 16,
    textAlign: 'center',
  },
  permissionButton: {
    marginTop: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  permissionButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
  topControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  topCenterControls: {
    flexDirection: 'row',
    gap: 15,
  },
  topButton: {
    padding: 8,
    borderRadius: 20,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  activeButton: {
    backgroundColor: 'rgba(255,255,255,0.3)',
  },
  topButtonText: {
    fontSize: 12,
    fontWeight: '600',
  },
  zoomIndicator: {
    position: 'absolute',
    top: 100,
    alignSelf: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  zoomText: {
    fontSize: 14,
    fontWeight: '600',
  },
  recordingIndicator: {
    position: 'absolute',
    top: 100,
    left: 20,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,0,0,0.8)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#fff',
    marginRight: 6,
  },
  recordingText: {
    fontSize: 12,
    fontWeight: '600',
  },
  bottomControls: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 20,
    paddingVertical: 30,
  },
  modesButton: {
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginBottom: 20,
  },
  modeText: {
    fontSize: 14,
    fontWeight: '600',
    marginRight: 5,
  },
  captureControls: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  controlButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordingButton: {
    borderColor: '#ff0000',
  },
  captureButtonInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
  },
  recordingButtonInner: {
    width: 30,
    height: 30,
    borderRadius: 4,
    backgroundColor: '#ff0000',
  },
  historyButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  historyPreview: {
    position: 'absolute',
    top: -5,
    right: -5,
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#ff6b6b',
    justifyContent: 'center',
    alignItems: 'center',
  },
  historyCount: {
    fontSize: 10,
    fontWeight: '600',
  },
  settingsPanel: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: 300,
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  settingsTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 30,
  },
  settingItem: {
    marginBottom: 25,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 10,
  },
  settingButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  settingButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  settingButtonText: {
    fontSize: 12,
    fontWeight: '500',
    textAlign: 'center',
  },
  settingToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  toggle: {
    width: 50,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
  },
  toggleDot: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: '#fff',
  },
  modesPanel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingTop: 20,
  },
  modesList: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  modeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 15,
    borderRadius: 12,
    marginBottom: 10,
  },
  modeItemText: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 15,
    flex: 1,
  },
  modeItemDescription: {
    fontSize: 12,
    marginLeft: 10,
  },
});

export default CameraScreen;