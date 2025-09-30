/**
 * Touch Optimized Interface - Mobile-First Interface Framework
 * 
 * Professional touch-optimized interface system designed for mobile content creation
 * with gesture recognition, haptic feedback, and adaptive layouts.
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Team Specialties:
 * - Lead AI Developer + Backend Senior + ML Engineer
 * - Database Administrator + Security Expert
 * - Microservices Architect + Audio Processing Specialist
 * - DevOps Engineer + IA Prompt Engineer
 * 
 * ⚠️ STRICT COPYRIGHT NOTICE ⚠️
 * This code is proprietary and confidential to Fahed Mlaiel.
 * Any unauthorized use, copying, modification, or distribution
 * without explicit written permission is strictly prohibited.
 * Violations will result in legal action.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  StyleSheet,
  Dimensions,
  Platform,
  PanResponder,
  Animated,
  Vibration,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Haptics from 'expo-haptics';
import { Gesture, GestureDetector } from 'react-native-gesture-handler';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

interface TouchOptimizedInterfaceProps {
  children: React.ReactNode;
  enableGestures?: boolean;
  enableHapticFeedback?: boolean;
  adaptiveLayout?: boolean;
  touchTargetSize?: number;
  gestureThreshold?: number;
  onGesture?: (gesture: GestureEvent) => void;
  theme?: 'light' | 'dark';
}

interface GestureEvent {
  type: 'tap' | 'double-tap' | 'long-press' | 'swipe' | 'pinch' | 'pan';
  coordinates: { x: number; y: number };
  velocity?: { x: number; y: number };
  scale?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
}

const TouchOptimizedInterface: React.FC<TouchOptimizedInterfaceProps> = ({
  children,
  enableGestures = true,
  enableHapticFeedback = true,
  adaptiveLayout = true,
  touchTargetSize = 44,
  gestureThreshold = 10,
  onGesture,
  theme = 'dark'
}) => {
  const [layoutMetrics, setLayoutMetrics] = useState({
    width: screenWidth,
    height: screenHeight,
    orientation: 'portrait' as 'portrait' | 'landscape'
  });

  const insets = useSafeAreaInsets();
  const animatedScale = useRef(new Animated.Value(1)).current;
  const animatedOpacity = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const subscription = Dimensions.addEventListener('change', ({ window }) => {
      setLayoutMetrics({
        width: window.width,
        height: window.height,
        orientation: window.width > window.height ? 'landscape' : 'portrait'
      });
    });

    return () => subscription?.remove();
  }, []);

  const triggerHapticFeedback = (type: 'light' | 'medium' | 'heavy' = 'light') => {
    if (!enableHapticFeedback) return;

    if (Platform.OS === 'ios') {
      switch (type) {
        case 'light':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
          break;
        case 'medium':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
          break;
        case 'heavy':
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
          break;
      }
    } else {
      // Android fallback
      Vibration.vibrate(type === 'heavy' ? 100 : type === 'medium' ? 50 : 25);
    }
  };

  const handleGestureEvent = (gestureEvent: GestureEvent) => {
    triggerHapticFeedback('light');
    onGesture?.(gestureEvent);

    // Visual feedback animation
    Animated.sequence([
      Animated.timing(animatedScale, {
        toValue: 0.98,
        duration: 100,
        useNativeDriver: true,
      }),
      Animated.timing(animatedScale, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true,
      }),
    ]).start();
  };

  // Tap Gesture
  const tapGesture = Gesture.Tap()
    .onEnd((event) => {
      if (!enableGestures) return;
      
      handleGestureEvent({
        type: 'tap',
        coordinates: { x: event.x, y: event.y }
      });
    });

  // Double Tap Gesture
  const doubleTapGesture = Gesture.Tap()
    .numberOfTaps(2)
    .onEnd((event) => {
      if (!enableGestures) return;
      
      triggerHapticFeedback('medium');
      handleGestureEvent({
        type: 'double-tap',
        coordinates: { x: event.x, y: event.y }
      });
    });

  // Long Press Gesture
  const longPressGesture = Gesture.LongPress()
    .minDuration(500)
    .onStart((event) => {
      if (!enableGestures) return;
      
      triggerHapticFeedback('heavy');
      handleGestureEvent({
        type: 'long-press',
        coordinates: { x: event.x, y: event.y }
      });
    });

  // Pan Gesture
  const panGesture = Gesture.Pan()
    .onEnd((event) => {
      if (!enableGestures) return;
      
      const { translationX, translationY, velocityX, velocityY } = event;
      
      if (Math.abs(translationX) > gestureThreshold || Math.abs(translationY) > gestureThreshold) {
        let direction: 'up' | 'down' | 'left' | 'right';
        
        if (Math.abs(translationX) > Math.abs(translationY)) {
          direction = translationX > 0 ? 'right' : 'left';
        } else {
          direction = translationY > 0 ? 'down' : 'up';
        }

        handleGestureEvent({
          type: 'swipe',
          coordinates: { x: event.x, y: event.y },
          velocity: { x: velocityX, y: velocityY },
          direction
        });
      } else {
        handleGestureEvent({
          type: 'pan',
          coordinates: { x: event.x, y: event.y },
          velocity: { x: velocityX, y: velocityY }
        });
      }
    });

  // Pinch Gesture
  const pinchGesture = Gesture.Pinch()
    .onEnd((event) => {
      if (!enableGestures) return;
      
      handleGestureEvent({
        type: 'pinch',
        coordinates: { x: event.focalX, y: event.focalY },
        scale: event.scale
      });
    });

  // Compose all gestures
  const composedGestures = Gesture.Race(
    doubleTapGesture,
    longPressGesture,
    Gesture.Simultaneous(
      tapGesture,
      panGesture,
      pinchGesture
    )
  );

  const getAdaptiveStyles = () => {
    if (!adaptiveLayout) return {};

    const isLandscape = layoutMetrics.orientation === 'landscape';
    const isTablet = layoutMetrics.width > 768;

    return {
      paddingHorizontal: isTablet ? 40 : 20,
      paddingVertical: isLandscape ? 10 : 20,
      minHeight: touchTargetSize,
    };
  };

  const containerStyle = [
    styles.container,
    {
      backgroundColor: theme === 'dark' ? '#1a1a1a' : '#ffffff',
      paddingTop: insets.top,
      paddingBottom: insets.bottom,
      paddingLeft: insets.left,
      paddingRight: insets.right,
    },
    getAdaptiveStyles(),
  ];

  return (
    <GestureDetector gesture={composedGestures}>
      <Animated.View 
        style={[
          containerStyle,
          {
            transform: [{ scale: animatedScale }],
            opacity: animatedOpacity,
          }
        ]}
      >
        {children}
      </Animated.View>
    </GestureDetector>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});

export default TouchOptimizedInterface;