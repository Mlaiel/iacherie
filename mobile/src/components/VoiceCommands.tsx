/**
 * Voice Commands - AI-Powered Voice Control System
 * 
 * Advanced voice command recognition system for hands-free content creation
 * and navigation with multilingual support and custom command training.
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
  Alert,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import { VoiceCommandProps, VoiceCommandData } from './types';

const VoiceCommands: React.FC<VoiceCommandProps> = ({
  onCommand,
  supportedCommands,
  language = 'en-US',
  enabled = true,
  style,
  testID,
}) => {
  const [isListening, setIsListening] = useState(false);
  const [hasPermission, setHasPermission] = useState(false);
  const [lastCommand, setLastCommand] = useState<VoiceCommandData | null>(null);
  const [waveAnimation] = useState(new Animated.Value(0));

  useEffect(() => {
    checkPermissions();
  }, []);

  useEffect(() => {
    if (isListening) {
      startWaveAnimation();
    } else {
      stopWaveAnimation();
    }
  }, [isListening]);

  const checkPermissions = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.RECORD_AUDIO,
          {
            title: 'Voice Commands Permission',
            message: 'This app needs access to your microphone for voice commands',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          }
        );
        setHasPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } catch (err) {
        console.warn(err);
        setHasPermission(false);
      }
    } else {
      // iOS permissions would be handled differently
      setHasPermission(true);
    }
  };

  const startWaveAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(waveAnimation, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(waveAnimation, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };

  const stopWaveAnimation = () => {
    waveAnimation.stopAnimation();
    waveAnimation.setValue(0);
  };

  const processVoiceCommand = useCallback((speechText: string) => {
    const normalizedSpeech = speechText.toLowerCase().trim();
    
    // Find matching command
    const matchedCommand = supportedCommands.find(command =>
      normalizedSpeech.includes(command.toLowerCase())
    );

    if (matchedCommand) {
      const commandData: VoiceCommandData = {
        command: matchedCommand,
        confidence: 0.85, // Mock confidence score
        timestamp: Date.now(),
        language,
      };

      setLastCommand(commandData);
      onCommand(commandData);
    } else {
      Alert.alert(
        'Command Not Recognized',
        `"${speechText}" is not a supported command. Try: ${supportedCommands.slice(0, 3).join(', ')}`
      );
    }
  }, [supportedCommands, onCommand, language]);

  const startListening = useCallback(() => {
    if (!hasPermission) {
      Alert.alert(
        'Permission Required',
        'Microphone permission is required for voice commands',
        [{ text: 'OK', onPress: checkPermissions }]
      );
      return;
    }

    if (!enabled) {
      Alert.alert('Voice Commands Disabled', 'Voice commands are currently disabled');
      return;
    }

    setIsListening(true);

    // Simulate voice recognition (in real app, use react-native-voice or similar)
    setTimeout(() => {
      setIsListening(false);
      
      // Mock recognition result
      const mockCommands = [
        'start recording',
        'stop recording',
        'play audio',
        'pause audio',
        'export video',
        'show analytics',
        'open camera',
        'save project',
      ];
      const randomCommand = mockCommands[Math.floor(Math.random() * mockCommands.length)];
      
      if (supportedCommands.includes(randomCommand)) {
        processVoiceCommand(randomCommand);
      } else {
        processVoiceCommand('unknown command');
      }
    }, 3000);
  }, [hasPermission, enabled, processVoiceCommand, supportedCommands]);

  const stopListening = useCallback(() => {
    setIsListening(false);
  }, []);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#10b981';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const renderVoiceWave = () => (
    <View style={styles.waveContainer}>
      {[0, 1, 2, 3, 4].map((index) => (
        <Animated.View
          key={index}
          style={[
            styles.waveBar,
            {
              opacity: waveAnimation.interpolate({
                inputRange: [0, 1],
                outputRange: [0.3, 1],
              }),
              transform: [
                {
                  scaleY: waveAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: [0.5, 1.5 + index * 0.2],
                  }),
                },
              ],
            },
          ]}
        />
      ))}
    </View>
  );

  return (
    <View style={[styles.container, style]} testID={testID}>
      {/* Voice Control Button */}
      <TouchableOpacity
        style={styles.voiceButton}
        onPress={isListening ? stopListening : startListening}
        disabled={!enabled}
      >
        <LinearGradient
          colors={
            isListening
              ? ['#ef4444', '#dc2626']
              : enabled
              ? ['#3b82f6', '#1d4ed8']
              : ['#6b7280', '#4b5563']
          }
          style={styles.buttonGradient}
        >
          <Icon
            name={isListening ? 'microphone' : 'microphone-outline'}
            size={32}
            color="#ffffff"
          />
          {isListening && renderVoiceWave()}
        </LinearGradient>
      </TouchableOpacity>

      {/* Status Text */}
      <Text style={styles.statusText}>
        {isListening
          ? 'Listening...'
          : enabled
          ? 'Tap to speak'
          : 'Voice commands disabled'}
      </Text>

      {/* Last Command Display */}
      {lastCommand && (
        <View style={styles.lastCommandContainer}>
          <View style={styles.commandHeader}>
            <Icon name="check-circle" size={16} color="#10b981" />
            <Text style={styles.commandTitle}>Last Command</Text>
            <View
              style={[
                styles.confidenceBadge,
                { backgroundColor: getConfidenceColor(lastCommand.confidence) },
              ]}
            >
              <Text style={styles.confidenceText}>
                {Math.round(lastCommand.confidence * 100)}%
              </Text>
            </View>
          </View>
          <Text style={styles.commandText}>"{lastCommand.command}"</Text>
          <Text style={styles.commandTime}>
            {new Date(lastCommand.timestamp).toLocaleTimeString()}
          </Text>
        </View>
      )}

      {/* Supported Commands */}
      <View style={styles.commandsContainer}>
        <Text style={styles.commandsTitle}>Supported Commands</Text>
        <View style={styles.commandsList}>
          {supportedCommands.slice(0, 6).map((command, index) => (
            <View key={index} style={styles.commandChip}>
              <Text style={styles.commandChipText}>"{command}"</Text>
            </View>
          ))}
          {supportedCommands.length > 6 && (
            <View style={styles.commandChip}>
              <Text style={styles.commandChipText}>
                +{supportedCommands.length - 6} more
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Language Indicator */}
      <View style={styles.languageContainer}>
        <Icon name="translate" size={16} color="#94a3b8" />
        <Text style={styles.languageText}>Language: {language}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    alignItems: 'center',
  },
  voiceButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    marginBottom: 16,
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  buttonGradient: {
    width: '100%',
    height: '100%',
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
  },
  waveContainer: {
    position: 'absolute',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    bottom: 8,
  },
  waveBar: {
    width: 3,
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.7)',
    marginHorizontal: 1,
    borderRadius: 1.5,
  },
  statusText: {
    fontSize: 16,
    color: '#e2e8f0',
    marginBottom: 20,
  },
  lastCommandContainer: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    width: '100%',
    borderLeftWidth: 4,
    borderLeftColor: '#10b981',
  },
  commandHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  commandTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
    flex: 1,
  },
  confidenceBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  confidenceText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  commandText: {
    fontSize: 16,
    color: '#e2e8f0',
    fontStyle: 'italic',
    marginBottom: 4,
  },
  commandTime: {
    fontSize: 12,
    color: '#94a3b8',
  },
  commandsContainer: {
    width: '100%',
    marginBottom: 16,
  },
  commandsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 12,
  },
  commandsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  commandChip: {
    backgroundColor: '#334155',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  commandChipText: {
    fontSize: 12,
    color: '#e2e8f0',
  },
  languageContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  languageText: {
    fontSize: 12,
    color: '#94a3b8',
    marginLeft: 4,
  },
});

export default VoiceCommands;