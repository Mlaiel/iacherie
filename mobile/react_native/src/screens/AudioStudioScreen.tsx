/**
 * Advanced Audio Studio Screen - Professional Audio Recording Interface
 * 
 * Enterprise-grade audio recording interface with real-time processing,
 * professional mixing controls, and AI-powered enhancement.
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
  ScrollView,
  Slider
} from 'react-native';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';
import AudioService from '../services/AudioService';
import { useTheme } from '../hooks/useTheme';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface AudioQuality {
  id: string;
  name: string;
  sampleRate: number;
  bitRate: number;
  description: string;
}

interface AudioEffect {
  type: string;
  enabled: boolean;
  parameters: Record<string, number>;
}

interface RecordingSession {
  id: string;
  startTime: number;
  duration: number;
  isActive: boolean;
  quality: AudioQuality;
}

const AudioStudioScreen: React.FC = () => {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();
  const audioService = AudioService.getInstance();
  
  // State management
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [activeSession, setActiveSession] = useState<RecordingSession | null>(null);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [peakLevel, setPeakLevel] = useState(0);
  const [selectedQuality, setSelectedQuality] = useState<AudioQuality>({
    id: 'high',
    name: 'High Quality',
    sampleRate: 44100,
    bitRate: 256000,
    description: '44.1kHz / 256kbps'
  });
  const [effects, setEffects] = useState<AudioEffect[]>([
    { type: 'noise_reduction', enabled: true, parameters: { intensity: 0.7 } },
    { type: 'auto_gain', enabled: true, parameters: { level: 0.8 } },
    { type: 'compressor', enabled: false, parameters: { ratio: 4, threshold: -12 } },
    { type: 'reverb', enabled: false, parameters: { size: 0.5, damping: 0.7 } },
    { type: 'echo', enabled: false, parameters: { delay: 300, feedback: 0.3 } }
  ]);
  const [recordingHistory, setRecordingHistory] = useState<any[]>([]);
  const [showEffects, setShowEffects] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Animation values
  const recordButtonScale = useRef(new Animated.Value(1)).current;
  const levelMeterHeight = useRef(new Animated.Value(0)).current;
  const peakMeterHeight = useRef(new Animated.Value(0)).current;
  const effectsPanelTranslateX = useRef(new Animated.Value(300)).current;
  const historyPanelTranslateX = useRef(new Animated.Value(-300)).current;

  // Timer ref
  const durationTimer = useRef<NodeJS.Timeout | null>(null);

  // Audio quality presets
  const audioQualities: AudioQuality[] = [
    {
      id: 'ultra',
      name: 'Ultra Quality',
      sampleRate: 96000,
      bitRate: 320000,
      description: '96kHz / 320kbps'
    },
    {
      id: 'high',
      name: 'High Quality',
      sampleRate: 44100,
      bitRate: 256000,
      description: '44.1kHz / 256kbps'
    },
    {
      id: 'medium',
      name: 'Medium Quality',
      sampleRate: 44100,
      bitRate: 128000,
      description: '44.1kHz / 128kbps'
    },
    {
      id: 'low',
      name: 'Low Quality',
      sampleRate: 22050,
      bitRate: 64000,
      description: '22kHz / 64kbps'
    }
  ];

  useEffect(() => {
    initializeAudioService();
    loadRecordingHistory();
    
    return () => {
      if (durationTimer.current) {
        clearInterval(durationTimer.current);
      }
    };
  }, []);

  useEffect(() => {
    // Animate audio level meters
    Animated.timing(levelMeterHeight, {
      toValue: audioLevel * 100,
      duration: 100,
      useNativeDriver: false,
    }).start();

    Animated.timing(peakMeterHeight, {
      toValue: peakLevel * 100,
      duration: 100,
      useNativeDriver: false,
    }).start();
  }, [audioLevel, peakLevel]);

  const initializeAudioService = async () => {
    try {
      const capabilities = await audioService.getCapabilities();
      if (capabilities.success) {
        console.log('Audio capabilities:', capabilities.data);
      }
    } catch (error) {
      console.error('Failed to initialize audio service:', error);
    }
  };

  const loadRecordingHistory = async () => {
    try {
      const historyResult = await audioService.getRecordingHistory({ limit: 20 });
      if (historyResult.success) {
        setRecordingHistory(historyResult.data.recordings);
      }
    } catch (error) {
      console.error('Failed to load recording history:', error);
    }
  };

  const startRecording = async () => {
    try {
      // Start recording session
      const sessionResult = await audioService.startRecordingSession({
        quality: selectedQuality.id as any,
        enableLocation: true,
        enableRealTimeProcessing: true,
        maxDuration: 3600000 // 1 hour
      });

      if (!sessionResult.success) {
        Alert.alert('Error', 'Failed to start recording session');
        return;
      }

      // Start actual recording
      const recordingResult = await audioService.startRecording();
      if (recordingResult.success) {
        setIsRecording(true);
        setIsPaused(false);
        setActiveSession({
          id: recordingResult.data,
          startTime: Date.now(),
          duration: 0,
          isActive: true,
          quality: selectedQuality
        });

        // Start duration timer
        durationTimer.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
          // Simulate audio level changes
          setAudioLevel(Math.random() * 0.8 + 0.1);
          setPeakLevel(Math.max(peakLevel, Math.random() * 0.9 + 0.1));
        }, 1000);

        animateRecordButton();
      } else {
        Alert.alert('Error', 'Failed to start recording');
      }
    } catch (error) {
      console.error('Recording start failed:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      if (durationTimer.current) {
        clearInterval(durationTimer.current);
        durationTimer.current = null;
      }

      const result = await audioService.stopRecording();
      if (result.success) {
        setIsRecording(false);
        setIsPaused(false);
        setRecordingDuration(0);
        setAudioLevel(0);
        setPeakLevel(0);
        setActiveSession(null);
        
        await loadRecordingHistory();
        Alert.alert('Success', 'Recording saved successfully!');
      } else {
        Alert.alert('Error', 'Failed to stop recording');
      }
    } catch (error) {
      console.error('Recording stop failed:', error);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const pauseRecording = async () => {
    try {
      const result = await audioService.pauseRecording();
      if (result.success) {
        setIsPaused(true);
        if (durationTimer.current) {
          clearInterval(durationTimer.current);
          durationTimer.current = null;
        }
      }
    } catch (error) {
      console.error('Recording pause failed:', error);
    }
  };

  const resumeRecording = async () => {
    try {
      const result = await audioService.resumeRecording();
      if (result.success) {
        setIsPaused(false);
        
        // Resume duration timer
        durationTimer.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
          setAudioLevel(Math.random() * 0.8 + 0.1);
          setPeakLevel(Math.max(peakLevel, Math.random() * 0.9 + 0.1));
        }, 1000);
      }
    } catch (error) {
      console.error('Recording resume failed:', error);
    }
  };

  const animateRecordButton = () => {
    Animated.sequence([
      Animated.timing(recordButtonScale, {
        toValue: 1.1,
        duration: 150,
        useNativeDriver: true,
      }),
      Animated.timing(recordButtonScale, {
        toValue: 1,
        duration: 150,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const toggleEffects = () => {
    setShowEffects(!showEffects);
    Animated.timing(effectsPanelTranslateX, {
      toValue: showEffects ? 300 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const toggleHistory = () => {
    setShowHistory(!showHistory);
    Animated.timing(historyPanelTranslateX, {
      toValue: showHistory ? -300 : 0,
      duration: 300,
      useNativeDriver: true,
    }).start();
  };

  const updateEffect = (index: number, enabled: boolean) => {
    const updatedEffects = [...effects];
    updatedEffects[index].enabled = enabled;
    setEffects(updatedEffects);
  };

  const updateEffectParameter = (effectIndex: number, parameter: string, value: number) => {
    const updatedEffects = [...effects];
    updatedEffects[effectIndex].parameters[parameter] = value;
    setEffects(updatedEffects);
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getEffectIcon = (type: string): string => {
    switch (type) {
      case 'noise_reduction': return 'volume-mute';
      case 'auto_gain': return 'volume-medium';
      case 'compressor': return 'options';
      case 'reverb': return 'musical-notes';
      case 'echo': return 'repeat';
      default: return 'cog';
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.black }]}>
      <StatusBar barStyle="light-content" backgroundColor={theme.black} />
      
      {/* Header */}
      <View style={[styles.header, { paddingTop: insets.top }]}>
        <TouchableOpacity onPress={() => {/* Navigate back */}}>
          <Ionicons name="arrow-back" size={24} color={theme.white} />
        </TouchableOpacity>
        
        <Text style={[styles.headerTitle, { color: theme.white }]}>Audio Studio</Text>
        
        <TouchableOpacity onPress={toggleHistory}>
          <Ionicons name="list" size={24} color={theme.white} />
        </TouchableOpacity>
      </View>

      {/* Main Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Quality Selector */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.white }]}>Recording Quality</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.qualitySelector}>
            {audioQualities.map((quality) => (
              <TouchableOpacity
                key={quality.id}
                style={[
                  styles.qualityCard,
                  {
                    backgroundColor: selectedQuality.id === quality.id ? theme.primary : theme.darkGray,
                    borderColor: selectedQuality.id === quality.id ? theme.primary : theme.gray
                  }
                ]}
                onPress={() => setSelectedQuality(quality)}
                disabled={isRecording}
              >
                <Text style={[
                  styles.qualityName,
                  { color: selectedQuality.id === quality.id ? theme.white : theme.lightGray }
                ]}>
                  {quality.name}
                </Text>
                <Text style={[
                  styles.qualityDescription,
                  { color: selectedQuality.id === quality.id ? theme.white : theme.gray }
                ]}>
                  {quality.description}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Audio Level Meters */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.white }]}>Audio Levels</Text>
          <View style={styles.meterContainer}>
            <View style={styles.meterChannel}>
              <Text style={[styles.channelLabel, { color: theme.lightGray }]}>L</Text>
              <View style={[styles.meterTrack, { backgroundColor: theme.darkGray }]}>
                <Animated.View
                  style={[
                    styles.meterLevel,
                    {
                      height: levelMeterHeight,
                      backgroundColor: audioLevel > 0.8 ? '#ff4757' : audioLevel > 0.6 ? '#ffa502' : '#2ed573'
                    }
                  ]}
                />
                <Animated.View
                  style={[
                    styles.meterPeak,
                    {
                      bottom: peakMeterHeight,
                      backgroundColor: '#ff6b6b'
                    }
                  ]}
                />
              </View>
              <Text style={[styles.meterValue, { color: theme.lightGray }]}>
                {Math.round(audioLevel * 100)}
              </Text>
            </View>
            
            <View style={styles.meterChannel}>
              <Text style={[styles.channelLabel, { color: theme.lightGray }]}>R</Text>
              <View style={[styles.meterTrack, { backgroundColor: theme.darkGray }]}>
                <Animated.View
                  style={[
                    styles.meterLevel,
                    {
                      height: levelMeterHeight,
                      backgroundColor: audioLevel > 0.8 ? '#ff4757' : audioLevel > 0.6 ? '#ffa502' : '#2ed573'
                    }
                  ]}
                />
                <Animated.View
                  style={[
                    styles.meterPeak,
                    {
                      bottom: peakMeterHeight,
                      backgroundColor: '#ff6b6b'
                    }
                  ]}
                />
              </View>
              <Text style={[styles.meterValue, { color: theme.lightGray }]}>
                {Math.round(audioLevel * 100)}
              </Text>
            </View>
          </View>
        </View>

        {/* Recording Controls */}
        <View style={styles.section}>
          <View style={styles.recordingInfo}>
            <View style={styles.durationContainer}>
              <Text style={[styles.durationLabel, { color: theme.lightGray }]}>Duration</Text>
              <Text style={[styles.durationValue, { color: theme.white }]}>
                {formatDuration(recordingDuration)}
              </Text>
            </View>
            
            {activeSession && (
              <View style={styles.sessionInfo}>
                <Text style={[styles.sessionLabel, { color: theme.lightGray }]}>
                  {activeSession.quality.name}
                </Text>
                <View style={styles.recordingStatus}>
                  {isRecording && !isPaused && (
                    <View style={styles.recordingDot} />
                  )}
                  <Text style={[
                    styles.statusText,
                    { color: isRecording ? (isPaused ? theme.orange : theme.red) : theme.gray }
                  ]}>
                    {isRecording ? (isPaused ? 'PAUSED' : 'RECORDING') : 'READY'}
                  </Text>
                </View>
              </View>
            )}
          </View>

          {/* Record Button */}
          <View style={styles.recordButtonContainer}>
            <Animated.View style={{ transform: [{ scale: recordButtonScale }] }}>
              <TouchableOpacity
                style={[
                  styles.recordButton,
                  { borderColor: isRecording ? theme.red : theme.white }
                ]}
                onPress={isRecording ? stopRecording : startRecording}
              >
                <LinearGradient
                  colors={isRecording ? ['#ff4757', '#ff3742'] : [theme.primary, theme.primaryDark]}
                  style={styles.recordButtonGradient}
                >
                  <Ionicons
                    name={isRecording ? 'stop' : 'mic'}
                    size={32}
                    color={theme.white}
                  />
                </LinearGradient>
              </TouchableOpacity>
            </Animated.View>

            {/* Pause/Resume Button */}
            {isRecording && (
              <TouchableOpacity
                style={[styles.controlButton, { backgroundColor: theme.orange }]}
                onPress={isPaused ? resumeRecording : pauseRecording}
              >
                <Ionicons
                  name={isPaused ? 'play' : 'pause'}
                  size={20}
                  color={theme.white}
                />
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Effects Quick Access */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.white }]}>Audio Effects</Text>
            <TouchableOpacity onPress={toggleEffects}>
              <Text style={[styles.sectionAction, { color: theme.primary }]}>Customize</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.effectsQuickAccess}>
            {effects.slice(0, 3).map((effect, index) => (
              <TouchableOpacity
                key={effect.type}
                style={[
                  styles.effectQuickButton,
                  {
                    backgroundColor: effect.enabled ? theme.primary : theme.darkGray,
                    borderColor: effect.enabled ? theme.primary : theme.gray
                  }
                ]}
                onPress={() => updateEffect(index, !effect.enabled)}
              >
                <Ionicons
                  name={getEffectIcon(effect.type) as any}
                  size={20}
                  color={effect.enabled ? theme.white : theme.lightGray}
                />
                <Text style={[
                  styles.effectQuickLabel,
                  { color: effect.enabled ? theme.white : theme.lightGray }
                ]}>
                  {effect.type.replace('_', ' ').toUpperCase()}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Effects Panel */}
      <Animated.View
        style={[
          styles.effectsPanel,
          {
            backgroundColor: theme.darkGray,
            transform: [{ translateX: effectsPanelTranslateX }]
          }
        ]}
        pointerEvents={showEffects ? 'auto' : 'none'}
      >
        <View style={styles.panelHeader}>
          <Text style={[styles.panelTitle, { color: theme.white }]}>Audio Effects</Text>
          <TouchableOpacity onPress={toggleEffects}>
            <Ionicons name="close" size={24} color={theme.white} />
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.panelContent}>
          {effects.map((effect, index) => (
            <View key={effect.type} style={styles.effectItem}>
              <View style={styles.effectHeader}>
                <View style={styles.effectInfo}>
                  <Ionicons
                    name={getEffectIcon(effect.type) as any}
                    size={20}
                    color={theme.lightGray}
                  />
                  <Text style={[styles.effectName, { color: theme.white }]}>
                    {effect.type.replace('_', ' ').toUpperCase()}
                  </Text>
                </View>
                <TouchableOpacity
                  style={[
                    styles.effectToggle,
                    { backgroundColor: effect.enabled ? theme.primary : theme.gray }
                  ]}
                  onPress={() => updateEffect(index, !effect.enabled)}
                >
                  <View style={[
                    styles.effectToggleDot,
                    { transform: [{ translateX: effect.enabled ? 20 : 2 }] }
                  ]} />
                </TouchableOpacity>
              </View>
              
              {effect.enabled && (
                <View style={styles.effectParameters}>
                  {Object.entries(effect.parameters).map(([param, value]) => (
                    <View key={param} style={styles.parameterItem}>
                      <Text style={[styles.parameterLabel, { color: theme.lightGray }]}>
                        {param.charAt(0).toUpperCase() + param.slice(1)}
                      </Text>
                      <Slider
                        style={styles.parameterSlider}
                        minimumValue={0}
                        maximumValue={1}
                        value={value as number}
                        onValueChange={(newValue) => updateEffectParameter(index, param, newValue)}
                        minimumTrackTintColor={theme.primary}
                        maximumTrackTintColor={theme.gray}
                        thumbStyle={{ backgroundColor: theme.primary }}
                      />
                      <Text style={[styles.parameterValue, { color: theme.white }]}>
                        {Math.round((value as number) * 100)}%
                      </Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          ))}
        </ScrollView>
      </Animated.View>

      {/* History Panel */}
      <Animated.View
        style={[
          styles.historyPanel,
          {
            backgroundColor: theme.darkGray,
            transform: [{ translateX: historyPanelTranslateX }]
          }
        ]}
        pointerEvents={showHistory ? 'auto' : 'none'}
      >
        <View style={styles.panelHeader}>
          <Text style={[styles.panelTitle, { color: theme.white }]}>Recording History</Text>
          <TouchableOpacity onPress={toggleHistory}>
            <Ionicons name="close" size={24} color={theme.white} />
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.panelContent}>
          {recordingHistory.map((recording, index) => (
            <TouchableOpacity key={recording.id} style={styles.historyItem}>
              <View style={styles.historyInfo}>
                <Text style={[styles.historyTitle, { color: theme.white }]}>
                  Recording {index + 1}
                </Text>
                <Text style={[styles.historyDetails, { color: theme.lightGray }]}>
                  {formatDuration(Math.floor(recording.duration / 1000))} • {recording.format.toUpperCase()}
                </Text>
                <Text style={[styles.historyDate, { color: theme.gray }]}>
                  {new Date(recording.metadata.timestamp).toLocaleDateString()}
                </Text>
              </View>
              <TouchableOpacity style={styles.historyAction}>
                <Ionicons name="play" size={16} color={theme.primary} />
              </TouchableOpacity>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </Animated.View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginBottom: 30,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 15,
  },
  sectionAction: {
    fontSize: 14,
    fontWeight: '500',
  },
  qualitySelector: {
    paddingVertical: 5,
  },
  qualityCard: {
    paddingHorizontal: 15,
    paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1,
    marginRight: 10,
    minWidth: 120,
  },
  qualityName: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  qualityDescription: {
    fontSize: 12,
  },
  meterContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
  },
  meterChannel: {
    alignItems: 'center',
  },
  channelLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 8,
  },
  meterTrack: {
    width: 20,
    height: 100,
    borderRadius: 10,
    position: 'relative',
    overflow: 'hidden',
  },
  meterLevel: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderRadius: 10,
  },
  meterPeak: {
    position: 'absolute',
    left: 0,
    right: 0,
    height: 2,
  },
  meterValue: {
    fontSize: 10,
    marginTop: 8,
  },
  recordingInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  durationContainer: {
    alignItems: 'flex-start',
  },
  durationLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  durationValue: {
    fontSize: 24,
    fontWeight: '600',
    fontFamily: 'monospace',
  },
  sessionInfo: {
    alignItems: 'flex-end',
  },
  sessionLabel: {
    fontSize: 12,
    marginBottom: 4,
  },
  recordingStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#ff4757',
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  recordButtonContainer: {
    alignItems: 'center',
    gap: 15,
  },
  recordButton: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 3,
    justifyContent: 'center',
    alignItems: 'center',
  },
  recordButtonGradient: {
    width: 88,
    height: 88,
    borderRadius: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  controlButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
  effectsQuickAccess: {
    flexDirection: 'row',
    gap: 10,
  },
  effectQuickButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
  },
  effectQuickLabel: {
    fontSize: 10,
    fontWeight: '600',
    marginTop: 4,
    textAlign: 'center',
  },
  effectsPanel: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 0,
    width: 300,
  },
  historyPanel: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    left: 0,
    width: 300,
  },
  panelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 20,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
  },
  panelTitle: {
    fontSize: 16,
    fontWeight: '600',
  },
  panelContent: {
    flex: 1,
    paddingHorizontal: 20,
  },
  effectItem: {
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  effectHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  effectInfo: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  effectName: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 10,
  },
  effectToggle: {
    width: 50,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
  },
  effectToggleDot: {
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: '#fff',
  },
  effectParameters: {
    marginTop: 15,
  },
  parameterItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  parameterLabel: {
    fontSize: 12,
    width: 60,
  },
  parameterSlider: {
    flex: 1,
    marginHorizontal: 10,
  },
  parameterValue: {
    fontSize: 12,
    width: 40,
    textAlign: 'right',
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.05)',
  },
  historyInfo: {
    flex: 1,
  },
  historyTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
  },
  historyDetails: {
    fontSize: 12,
    marginBottom: 2,
  },
  historyDate: {
    fontSize: 11,
  },
  historyAction: {
    width: 30,
    height: 30,
    borderRadius: 15,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
});

export default AudioStudioScreen;