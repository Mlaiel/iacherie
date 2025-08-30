/**
 * Gesture Controls - Advanced Gesture Recognition System
 * 
 * Professional gesture control system for mobile content creation
 * with multi-touch support and customizable gesture handlers.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useCallback } from 'react';
import { View, StyleSheet } from 'react-native';
import {
  PanGestureHandler,
  PinchGestureHandler,
  RotationGestureHandler,
  TapGestureHandler,
  LongPressGestureHandler,
  State,
} from 'react-native-gesture-handler';
import { GestureControlProps, TouchGestureData } from './types';

const GestureControls: React.FC<GestureControlProps> = ({
  onGesture,
  enabledGestures,
  sensitivity = 1.0,
  children,
  style,
  testID,
}) => {
  const createGestureData = useCallback(
    (
      gestureType: TouchGestureData['gestureType'],
      x: number,
      y: number,
      additionalData?: Partial<TouchGestureData>
    ): TouchGestureData => ({
      x,
      y,
      timestamp: Date.now(),
      gestureType,
      ...additionalData,
    }),
    []
  );

  const handleTap = useCallback(
    (event: any) => {
      if (event.nativeEvent.state === State.ACTIVE && enabledGestures.includes('tap')) {
        const gestureData = createGestureData(
          'tap',
          event.nativeEvent.x,
          event.nativeEvent.y
        );
        onGesture(gestureData);
      }
    },
    [enabledGestures, onGesture, createGestureData]
  );

  const handleLongPress = useCallback(
    (event: any) => {
      if (event.nativeEvent.state === State.ACTIVE && enabledGestures.includes('long_press')) {
        const gestureData = createGestureData(
          'long_press',
          event.nativeEvent.x,
          event.nativeEvent.y
        );
        onGesture(gestureData);
      }
    },
    [enabledGestures, onGesture, createGestureData]
  );

  const handlePan = useCallback(
    (event: any) => {
      if (event.nativeEvent.state === State.ACTIVE && enabledGestures.includes('swipe')) {
        const { translationX, translationY, x, y, velocityX, velocityY } = event.nativeEvent;
        
        // Determine swipe direction based on velocity and translation
        let direction: TouchGestureData['direction'];
        if (Math.abs(velocityX) > Math.abs(velocityY)) {
          direction = velocityX > 0 ? 'right' : 'left';
        } else {
          direction = velocityY > 0 ? 'down' : 'up';
        }

        const gestureData = createGestureData('swipe', x, y, {
          direction,
          force: Math.sqrt(velocityX * velocityX + velocityY * velocityY) * sensitivity,
        });
        onGesture(gestureData);
      }
    },
    [enabledGestures, onGesture, createGestureData, sensitivity]
  );

  const handlePinch = useCallback(
    (event: any) => {
      if (event.nativeEvent.state === State.ACTIVE && enabledGestures.includes('pinch')) {
        const { scale, focalX, focalY } = event.nativeEvent;
        const gestureData = createGestureData('pinch', focalX, focalY, {
          force: scale * sensitivity,
        });
        onGesture(gestureData);
      }
    },
    [enabledGestures, onGesture, createGestureData, sensitivity]
  );

  const handleRotation = useCallback(
    (event: any) => {
      if (event.nativeEvent.state === State.ACTIVE && enabledGestures.includes('rotate')) {
        const { rotation, anchorX, anchorY } = event.nativeEvent;
        const gestureData = createGestureData('rotate', anchorX, anchorY, {
          force: Math.abs(rotation) * sensitivity,
        });
        onGesture(gestureData);
      }
    },
    [enabledGestures, onGesture, createGestureData, sensitivity]
  );

  const renderGestureHandlers = () => {
    let component = <View style={[styles.container, style]}>{children}</View>;

    // Wrap with enabled gesture handlers
    if (enabledGestures.includes('rotate')) {
      component = (
        <RotationGestureHandler onHandlerStateChange={handleRotation}>
          {component}
        </RotationGestureHandler>
      );
    }

    if (enabledGestures.includes('pinch')) {
      component = (
        <PinchGestureHandler onHandlerStateChange={handlePinch}>
          {component}
        </PinchGestureHandler>
      );
    }

    if (enabledGestures.includes('swipe')) {
      component = (
        <PanGestureHandler onHandlerStateChange={handlePan}>
          {component}
        </PanGestureHandler>
      );
    }

    if (enabledGestures.includes('long_press')) {
      component = (
        <LongPressGestureHandler
          onHandlerStateChange={handleLongPress}
          minDurationMs={500}
        >
          {component}
        </LongPressGestureHandler>
      );
    }

    if (enabledGestures.includes('tap')) {
      component = (
        <TapGestureHandler onHandlerStateChange={handleTap}>
          {component}
        </TapGestureHandler>
      );
    }

    return component;
  };

  return (
    <View style={styles.wrapper} testID={testID}>
      {renderGestureHandlers()}
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    flex: 1,
  },
  container: {
    flex: 1,
  },
});

export default GestureControls;