/**
 * Touch Optimized Interface - Enhanced Touch Experience
 * 
 * Professional touch-optimized wrapper component providing haptic feedback,
 * gesture recognition, and accessibility enhancements for mobile interfaces.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useCallback, useRef } from 'react';
import {
  TouchableOpacity,
  Animated,
  StyleSheet,
  Vibration,
  Platform,
} from 'react-native';
import { TouchOptimizedProps } from './types';

const TouchOptimizedInterface: React.FC<TouchOptimizedProps> = ({
  children,
  hapticFeedback = true,
  gestureEnabled = true,
  touchableOpacity = 0.7,
  minimumHitArea = 44,
  style,
  testID,
  accessibilityLabel,
  ...touchableProps
}) => {
  const scaleValue = useRef(new Animated.Value(1)).current;

  const handlePressIn = useCallback(() => {
    // Haptic feedback
    if (hapticFeedback && Platform.OS === 'ios') {
      // iOS haptic feedback
      const ReactNativeHapticFeedback = require('react-native-haptic-feedback');
      ReactNativeHapticFeedback.trigger('impactLight');
    } else if (hapticFeedback && Platform.OS === 'android') {
      // Android vibration
      Vibration.vibrate(10);
    }

    // Scale animation
    Animated.spring(scaleValue, {
      toValue: 0.95,
      tension: 300,
      friction: 10,
      useNativeDriver: true,
    }).start();
  }, [hapticFeedback, scaleValue]);

  const handlePressOut = useCallback(() => {
    Animated.spring(scaleValue, {
      toValue: 1,
      tension: 300,
      friction: 10,
      useNativeDriver: true,
    }).start();
  }, [scaleValue]);

  return (
    <TouchableOpacity
      style={[
        styles.container,
        {
          minWidth: minimumHitArea,
          minHeight: minimumHitArea,
        },
        style,
      ]}
      activeOpacity={touchableOpacity}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      testID={testID}
      accessibilityLabel={accessibilityLabel}
      accessibilityRole="button"
      {...touchableProps}
    >
      <Animated.View
        style={[
          styles.content,
          {
            transform: [{ scale: scaleValue }],
          },
        ]}
      >
        {children}
      </Animated.View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default TouchOptimizedInterface;