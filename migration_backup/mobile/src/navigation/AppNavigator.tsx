/**
 * Mobile App Navigator - Main navigation for React Native app
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { View, Text, StyleSheet } from 'react-native';

// Import actual screen components
import {
  HomeScreen,
  DashboardScreen,
  UploadScreen,
  AnalyticsScreen,
  SettingsScreen,
  type ScreenParams
} from '../screens';

// Icon imports (would normally use react-native-vector-icons)
const Tab = createBottomTabNavigator<ScreenParams>();
const Stack = createStackNavigator<ScreenParams>();

// Placeholder screens for missing screens
const LibraryScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>Library</Text>
    <Text style={styles.subtitle}>Browse your content library</Text>
  </View>
);

const ProtectionScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>Protection</Text>
    <Text style={styles.subtitle}>Monitor copyright protection</Text>
  </View>
);

const MonetizationScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>Monetization</Text>
    <Text style={styles.subtitle}>Revenue streams and payments</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={styles.screen}>
    <Text style={styles.title}>Settings</Text>
    <Text style={styles.subtitle}>App settings and preferences</Text>
  </View>
);

// Tab Navigator
const TabNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#3B82F6',
        tabBarInactiveTintColor: '#6B7280',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E5E7EB',
          borderTopWidth: 1,
          paddingTop: 5,
          paddingBottom: 5,
          height: 60,
        },
        headerStyle: {
          backgroundColor: '#1F2937',
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: 'Home',
          headerTitle: 'Ainflue',
          // tabBarIcon: ({ color, size }) => <HomeIcon color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Upload" 
        component={UploadScreen}
        options={{
          tabBarLabel: 'Upload',
          // tabBarIcon: ({ color, size }) => <UploadIcon color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Analytics" 
        component={AnalyticsScreen}
        options={{
          tabBarLabel: 'Analytics',
          // tabBarIcon: ({ color, size }) => <AnalyticsIcon color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarLabel: 'Dashboard',
          // tabBarIcon: ({ color, size }) => <DashboardIcon color={color} size={size} />
        }}
      />
      <Tab.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{
          tabBarLabel: 'Settings',
          // tabBarIcon: ({ color, size }) => <SettingsIcon color={color} size={size} />
        }}
      />
    </Tab.Navigator>
  );
};

// Main App Navigator with Stack for modals and detailed screens
const AppNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: '#1F2937',
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen 
        name="Main" 
        component={TabNavigator} 
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="Settings" 
        component={SettingsScreen}
        options={{ 
          presentation: 'modal',
          title: 'Settings'
        }}
      />
    </Stack.Navigator>
  );
};

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
});

export default AppNavigator;