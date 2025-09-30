/**
 * Settings Screen - User settings and preferences
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  StatusBar,
  SafeAreaView,
  Alert,
} from 'react-native';

interface UserProfile {
  name: string;
  email: string;
  plan: 'free' | 'pro' | 'enterprise';
  joinDate: string;
}

interface NotificationSettings {
  pushNotifications: boolean;
  emailAlerts: boolean;
  securityAlerts: boolean;
  marketingEmails: boolean;
  weeklyReports: boolean;
}

export const SettingsScreen: React.FC = () => {
  const [profile] = useState<UserProfile>({
    name: 'Fahed Mlaiel',
    email: 'mlaiel@live.de',
    plan: 'enterprise',
    joinDate: 'January 2024'
  });

  const [notifications, setNotifications] = useState<NotificationSettings>({
    pushNotifications: true,
    emailAlerts: true,
    securityAlerts: true,
    marketingEmails: false,
    weeklyReports: true,
  });

  const [biometricsEnabled, setBiometricsEnabled] = useState(true);
  const [autoSync, setAutoSync] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);

  const updateNotificationSetting = (key: keyof NotificationSettings, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: () => console.log('Logout') }
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. All your data will be permanently deleted.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => console.log('Delete account') }
      ]
    );
  };

  const SettingItem: React.FC<{
    title: string;
    subtitle?: string;
    value?: boolean;
    onValueChange?: (value: boolean) => void;
    onPress?: () => void;
    showArrow?: boolean;
    textColor?: string;
  }> = ({ title, subtitle, value, onValueChange, onPress, showArrow = false, textColor = '#111827' }) => (
    <TouchableOpacity 
      style={styles.settingItem} 
      onPress={onPress}
      disabled={!onPress && !onValueChange}
    >
      <View style={styles.settingContent}>
        <Text style={[styles.settingTitle, { color: textColor }]}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {onValueChange && (
        <Switch
          value={value}
          onValueChange={onValueChange}
          trackColor={{ false: '#D1D5DB', true: '#3B82F6' }}
          thumbColor={value ? '#FFFFFF' : '#F3F4F6'}
        />
      )}
      {showArrow && (
        <Text style={styles.arrow}>›</Text>
      )}
    </TouchableOpacity>
  );

  const SectionHeader: React.FC<{ title: string }> = ({ title }) => (
    <Text style={styles.sectionHeader}>{title}</Text>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#ffffff" />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* Profile Section */}
        <View style={styles.profileSection}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{profile.name.split(' ').map(n => n[0]).join('')}</Text>
          </View>
          <Text style={styles.profileName}>{profile.name}</Text>
          <Text style={styles.profileEmail}>{profile.email}</Text>
          <View style={styles.planBadge}>
            <Text style={styles.planText}>{profile.plan.toUpperCase()}</Text>
          </View>
        </View>

        {/* Account Settings */}
        <SectionHeader title="Account" />
        <View style={styles.section}>
          <SettingItem
            title="Edit Profile"
            subtitle="Update your personal information"
            onPress={() => console.log('Edit profile')}
            showArrow
          />
          <SettingItem
            title="Change Password"
            subtitle="Update your account password"
            onPress={() => console.log('Change password')}
            showArrow
          />
          <SettingItem
            title="Subscription"
            subtitle={`${profile.plan} plan • Joined ${profile.joinDate}`}
            onPress={() => console.log('Subscription')}
            showArrow
          />
        </View>

        {/* Security Settings */}
        <SectionHeader title="Security" />
        <View style={styles.section}>
          <SettingItem
            title="Biometric Authentication"
            subtitle="Use fingerprint or face recognition"
            value={biometricsEnabled}
            onValueChange={setBiometricsEnabled}
          />
          <SettingItem
            title="Two-Factor Authentication"
            subtitle="Add an extra layer of security"
            onPress={() => console.log('2FA settings')}
            showArrow
          />
          <SettingItem
            title="Active Sessions"
            subtitle="Manage your device sessions"
            onPress={() => console.log('Active sessions')}
            showArrow
          />
        </View>

        {/* Notifications */}
        <SectionHeader title="Notifications" />
        <View style={styles.section}>
          <SettingItem
            title="Push Notifications"
            subtitle="Receive notifications on this device"
            value={notifications.pushNotifications}
            onValueChange={(value) => updateNotificationSetting('pushNotifications', value)}
          />
          <SettingItem
            title="Email Alerts"
            subtitle="Get important updates via email"
            value={notifications.emailAlerts}
            onValueChange={(value) => updateNotificationSetting('emailAlerts', value)}
          />
          <SettingItem
            title="Security Alerts"
            subtitle="Notifications about account security"
            value={notifications.securityAlerts}
            onValueChange={(value) => updateNotificationSetting('securityAlerts', value)}
          />
          <SettingItem
            title="Weekly Reports"
            subtitle="Receive weekly analytics reports"
            value={notifications.weeklyReports}
            onValueChange={(value) => updateNotificationSetting('weeklyReports', value)}
          />
          <SettingItem
            title="Marketing Emails"
            subtitle="Product updates and promotions"
            value={notifications.marketingEmails}
            onValueChange={(value) => updateNotificationSetting('marketingEmails', value)}
          />
        </View>

        {/* App Settings */}
        <SectionHeader title="App Settings" />
        <View style={styles.section}>
          <SettingItem
            title="Auto Sync"
            subtitle="Automatically sync data in background"
            value={autoSync}
            onValueChange={setAutoSync}
          />
          <SettingItem
            title="Offline Mode"
            subtitle="Work without internet connection"
            value={offlineMode}
            onValueChange={setOfflineMode}
          />
          <SettingItem
            title="Storage"
            subtitle="Manage local storage usage"
            onPress={() => console.log('Storage settings')}
            showArrow
          />
          <SettingItem
            title="Data Export"
            subtitle="Download your data"
            onPress={() => console.log('Data export')}
            showArrow
          />
        </View>

        {/* Support */}
        <SectionHeader title="Support" />
        <View style={styles.section}>
          <SettingItem
            title="Help Center"
            subtitle="Get help and support"
            onPress={() => console.log('Help center')}
            showArrow
          />
          <SettingItem
            title="Contact Support"
            subtitle="Get in touch with our team"
            onPress={() => console.log('Contact support')}
            showArrow
          />
          <SettingItem
            title="Report a Bug"
            subtitle="Help us improve the app"
            onPress={() => console.log('Report bug')}
            showArrow
          />
          <SettingItem
            title="Privacy Policy"
            onPress={() => console.log('Privacy policy')}
            showArrow
          />
          <SettingItem
            title="Terms of Service"
            onPress={() => console.log('Terms of service')}
            showArrow
          />
        </View>

        {/* Account Actions */}
        <SectionHeader title="Account Actions" />
        <View style={styles.section}>
          <SettingItem
            title="Logout"
            onPress={handleLogout}
            textColor="#EF4444"
          />
          <SettingItem
            title="Delete Account"
            subtitle="Permanently delete your account"
            onPress={handleDeleteAccount}
            textColor="#EF4444"
          />
        </View>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Ainflue v1.0.0</Text>
          <Text style={styles.footerText}>© 2025 Fahed Mlaiel</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  scrollView: {
    flex: 1,
  },
  profileSection: {
    alignItems: 'center',
    paddingVertical: 32,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    marginBottom: 24,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#3B82F6',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  avatarText: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  profileName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  profileEmail: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 12,
  },
  planBadge: {
    backgroundColor: '#10B981',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 4,
  },
  planText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  sectionHeader: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginLeft: 16,
    marginTop: 16,
    marginBottom: 8,
  },
  section: {
    backgroundColor: '#FFFFFF',
    marginBottom: 16,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  settingContent: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  arrow: {
    fontSize: 18,
    color: '#D1D5DB',
    marginLeft: 8,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
});

export default SettingsScreen;