/**
 * Offline Mode UI - Intelligent Offline Management Interface
 * 
 * Professional offline mode interface for managing cached content,
 * sync queues, and storage optimization during connectivity issues.
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
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Switch,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import { OfflineModeProps, OfflineData } from './types';

const OfflineModeUI: React.FC<OfflineModeProps> = ({
  isOffline,
  offlineData,
  storageQuota,
  usedStorage,
  onDataManagement,
  style,
  testID,
}) => {
  const [autoSync, setAutoSync] = useState(true);
  const [downloadQuality, setDownloadQuality] = useState<'low' | 'medium' | 'high'>('medium');

  const formatFileSize = useCallback((sizeInBytes: number) => {
    const sizeInMB = sizeInBytes / (1024 * 1024);
    if (sizeInMB >= 1000) {
      return `${(sizeInMB / 1000).toFixed(1)} GB`;
    }
    return `${sizeInMB.toFixed(1)} MB`;
  }, []);

  const getStoragePercentage = () => {
    return (usedStorage / storageQuota) * 100;
  };

  const getDataByType = (type: OfflineData['type']) => {
    return offlineData.filter(item => item.type === type);
  };

  const getTotalSizeByType = (type: OfflineData['type']) => {
    return getDataByType(type).reduce((total, item) => total + item.size, 0);
  };

  const handleClearData = (type: OfflineData['type']) => {
    Alert.alert(
      'Clear Data',
      `Are you sure you want to clear all ${type} data? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: () => {
            // Implementation would clear data of specified type
            console.log(`Clearing ${type} data`);
          },
        },
      ]
    );
  };

  const renderStorageOverview = () => (
    <View style={styles.storageContainer}>
      <LinearGradient
        colors={
          getStoragePercentage() > 90
            ? ['#ef4444', '#dc2626']
            : getStoragePercentage() > 75
            ? ['#f59e0b', '#d97706']
            : ['#1e293b', '#334155']
        }
        style={styles.storageGradient}
      >
        <View style={styles.storageHeader}>
          <Icon name="harddisk" size={24} color="#ffffff" />
          <Text style={styles.storageTitle}>Offline Storage</Text>
          <TouchableOpacity
            style={styles.manageButton}
            onPress={onDataManagement}
          >
            <Text style={styles.manageButtonText}>Manage</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.storageProgressContainer}>
          <View style={styles.storageBar}>
            <View
              style={[
                styles.storageUsed,
                { width: `${Math.min(getStoragePercentage(), 100)}%` },
              ]}
            />
          </View>
          <Text style={styles.storageText}>
            {formatFileSize(usedStorage)} of {formatFileSize(storageQuota)} used
            ({Math.round(getStoragePercentage())}%)
          </Text>
        </View>
      </LinearGradient>
    </View>
  );

  const renderConnectionStatus = () => (
    <View style={styles.statusContainer}>
      <View style={[styles.statusCard, isOffline && styles.offlineCard]}>
        <View style={styles.statusHeader}>
          <Icon
            name={isOffline ? 'wifi-off' : 'wifi'}
            size={20}
            color={isOffline ? '#ef4444' : '#10b981'}
          />
          <Text style={[styles.statusTitle, isOffline && styles.offlineText]}>
            {isOffline ? 'Offline Mode' : 'Online'}
          </Text>
        </View>
        <Text style={styles.statusDescription}>
          {isOffline
            ? 'Working offline. Changes will sync when connection is restored.'
            : 'Connected to internet. All features available.'}
        </Text>
      </View>
    </View>
  );

  const renderDataCategories = () => (
    <View style={styles.categoriesContainer}>
      <Text style={styles.sectionTitle}>Offline Data</Text>
      
      {(['content', 'profile', 'settings', 'analytics'] as const).map((type) => {
        const typeData = getDataByType(type);
        const totalSize = getTotalSizeByType(type);
        
        return (
          <View key={type} style={styles.categoryCard}>
            <View style={styles.categoryHeader}>
              <View style={styles.categoryInfo}>
                <Icon
                  name={
                    type === 'content'
                      ? 'file-multiple'
                      : type === 'profile'
                      ? 'account'
                      : type === 'settings'
                      ? 'cog'
                      : 'chart-line'
                  }
                  size={20}
                  color="#3b82f6"
                />
                <Text style={styles.categoryTitle}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Text>
              </View>
              <View style={styles.categoryStats}>
                <Text style={styles.categoryCount}>{typeData.length} items</Text>
                <Text style={styles.categorySize}>{formatFileSize(totalSize)}</Text>
              </View>
            </View>
            
            <View style={styles.categoryActions}>
              <TouchableOpacity
                style={styles.categoryButton}
                onPress={() => handleClearData(type)}
                disabled={typeData.length === 0}
              >
                <Icon name="delete" size={16} color="#ef4444" />
                <Text style={styles.categoryButtonText}>Clear</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.categoryButton}
                onPress={() => Alert.alert('Sync', `Sync ${type} data when online`)}
              >
                <Icon name="sync" size={16} color="#3b82f6" />
                <Text style={styles.categoryButtonText}>Sync</Text>
              </TouchableOpacity>
            </View>
          </View>
        );
      })}
    </View>
  );

  const renderSettings = () => (
    <View style={styles.settingsContainer}>
      <Text style={styles.sectionTitle}>Offline Settings</Text>
      
      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>Auto Sync</Text>
          <Text style={styles.settingDescription}>
            Automatically sync data when connection is restored
          </Text>
        </View>
        <Switch
          value={autoSync}
          onValueChange={setAutoSync}
          trackColor={{ false: '#374151', true: '#3b82f6' }}
          thumbColor={autoSync ? '#ffffff' : '#9ca3af'}
        />
      </View>

      <View style={styles.settingItem}>
        <View style={styles.settingInfo}>
          <Text style={styles.settingTitle}>Download Quality</Text>
          <Text style={styles.settingDescription}>
            Quality for offline content downloads
          </Text>
        </View>
        <View style={styles.qualitySelector}>
          {(['low', 'medium', 'high'] as const).map((quality) => (
            <TouchableOpacity
              key={quality}
              style={[
                styles.qualityButton,
                downloadQuality === quality && styles.activeQualityButton,
              ]}
              onPress={() => setDownloadQuality(quality)}
            >
              <Text
                style={[
                  styles.qualityText,
                  downloadQuality === quality && styles.activeQualityText,
                ]}
              >
                {quality.charAt(0).toUpperCase() + quality.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </View>
  );

  const renderQuickActions = () => (
    <View style={styles.actionsContainer}>
      <Text style={styles.sectionTitle}>Quick Actions</Text>
      
      <View style={styles.actionGrid}>
        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => Alert.alert('Download', 'Download essential content for offline use')}
        >
          <Icon name="download" size={24} color="#10b981" />
          <Text style={styles.actionTitle}>Download</Text>
          <Text style={styles.actionSubtitle}>Essential content</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => Alert.alert('Cleanup', 'Remove old cached data')}
        >
          <Icon name="broom" size={24} color="#f59e0b" />
          <Text style={styles.actionTitle}>Cleanup</Text>
          <Text style={styles.actionSubtitle}>Free up space</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => Alert.alert('Backup', 'Create local backup of important data')}
        >
          <Icon name="backup-restore" size={24} color="#8b5cf6" />
          <Text style={styles.actionTitle}>Backup</Text>
          <Text style={styles.actionSubtitle}>Create backup</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionCard}
          onPress={() => Alert.alert('Export', 'Export offline data to external storage')}
        >
          <Icon name="export" size={24} color="#3b82f6" />
          <Text style={styles.actionTitle}>Export</Text>
          <Text style={styles.actionSubtitle}>To external</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <ScrollView
      style={[styles.container, style]}
      testID={testID}
      showsVerticalScrollIndicator={false}
    >
      {renderConnectionStatus()}
      {renderStorageOverview()}
      {renderDataCategories()}
      {renderSettings()}
      {renderQuickActions()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  storageContainer: {
    margin: 16,
    borderRadius: 12,
    overflow: 'hidden',
  },
  storageGradient: {
    padding: 16,
  },
  storageHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  storageTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginLeft: 8,
  },
  manageButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 12,
  },
  manageButtonText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '600',
  },
  storageProgressContainer: {
    marginTop: 8,
  },
  storageBar: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 4,
    marginBottom: 8,
  },
  storageUsed: {
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: 4,
  },
  storageText: {
    fontSize: 12,
    color: '#e2e8f0',
  },
  statusContainer: {
    padding: 16,
  },
  statusCard: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#10b981',
  },
  offlineCard: {
    borderLeftColor: '#ef4444',
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#10b981',
    marginLeft: 8,
  },
  offlineText: {
    color: '#ef4444',
  },
  statusDescription: {
    fontSize: 14,
    color: '#94a3b8',
    lineHeight: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  categoriesContainer: {
    padding: 16,
  },
  categoryCard: {
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  categoryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  categoryInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  categoryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
  categoryStats: {
    alignItems: 'flex-end',
  },
  categoryCount: {
    fontSize: 12,
    color: '#94a3b8',
  },
  categorySize: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
  },
  categoryActions: {
    flexDirection: 'row',
  },
  categoryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#334155',
    borderRadius: 16,
    marginRight: 8,
  },
  categoryButtonText: {
    fontSize: 12,
    color: '#e2e8f0',
    marginLeft: 4,
  },
  settingsContainer: {
    padding: 16,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#94a3b8',
  },
  qualitySelector: {
    flexDirection: 'row',
  },
  qualityButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#374151',
    borderRadius: 16,
    marginLeft: 4,
  },
  activeQualityButton: {
    backgroundColor: '#3b82f6',
  },
  qualityText: {
    fontSize: 12,
    color: '#94a3b8',
  },
  activeQualityText: {
    color: '#ffffff',
  },
  actionsContainer: {
    padding: 16,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionCard: {
    width: '48%',
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 8,
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 2,
    textAlign: 'center',
  },
});

export default OfflineModeUI;