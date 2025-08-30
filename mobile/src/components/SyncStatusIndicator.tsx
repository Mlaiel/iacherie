/**
 * Sync Status Indicator - Real-time Synchronization Monitor
 * 
 * Professional sync status indicator providing real-time feedback
 * on data synchronization, connectivity, and background processes.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Modal,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import { SyncStatusProps, SyncStatus } from './types';

const SyncStatusIndicator: React.FC<SyncStatusProps> = ({
  status,
  onRetrySync,
  showDetails = false,
  style,
  testID,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [pulseAnimation] = useState(new Animated.Value(1));
  const [rotateAnimation] = useState(new Animated.Value(0));

  useEffect(() => {
    if (status.isSyncing) {
      // Pulse animation for syncing
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnimation, {
            toValue: 1.2,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnimation, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Rotation animation for syncing icon
      Animated.loop(
        Animated.timing(rotateAnimation, {
          toValue: 1,
          duration: 2000,
          useNativeDriver: true,
        })
      ).start();
    } else {
      pulseAnimation.stopAnimation();
      rotateAnimation.stopAnimation();
      pulseAnimation.setValue(1);
      rotateAnimation.setValue(0);
    }
  }, [status.isSyncing, pulseAnimation, rotateAnimation]);

  const getStatusColor = () => {
    if (!status.isOnline) return '#ef4444';
    if (status.isSyncing) return '#3b82f6';
    if (status.failedItems > 0) return '#f59e0b';
    return '#10b981';
  };

  const getStatusIcon = () => {
    if (!status.isOnline) return 'cloud-off-outline';
    if (status.isSyncing) return 'sync';
    if (status.failedItems > 0) return 'alert-circle';
    return 'check-circle';
  };

  const getStatusText = () => {
    if (!status.isOnline) return 'Offline';
    if (status.isSyncing) return 'Syncing...';
    if (status.failedItems > 0) return 'Sync Issues';
    return 'Up to date';
  };

  const formatLastSync = () => {
    if (!status.lastSyncTime) return 'Never synced';
    
    const now = new Date();
    const diff = now.getTime() - status.lastSyncTime.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const renderCompactIndicator = () => (
    <TouchableOpacity
      style={[styles.compactContainer, style]}
      onPress={() => setShowModal(true)}
      testID={testID}
    >
      <Animated.View
        style={[
          styles.statusIndicator,
          {
            backgroundColor: getStatusColor(),
            transform: [{ scale: pulseAnimation }],
          },
        ]}
      >
        <Animated.View
          style={{
            transform: [
              {
                rotate: rotateAnimation.interpolate({
                  inputRange: [0, 1],
                  outputRange: ['0deg', '360deg'],
                }),
              },
            ],
          }}
        >
          <Icon
            name={getStatusIcon()}
            size={12}
            color="#ffffff"
          />
        </Animated.View>
      </Animated.View>
      
      {status.pendingItems > 0 && (
        <View style={styles.pendingBadge}>
          <Text style={styles.pendingText}>{status.pendingItems}</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderExpandedIndicator = () => (
    <TouchableOpacity
      style={[styles.expandedContainer, style]}
      onPress={() => setShowModal(true)}
      testID={testID}
    >
      <LinearGradient
        colors={[getStatusColor(), `${getStatusColor()}80`]}
        style={styles.expandedGradient}
      >
        <View style={styles.expandedContent}>
          <Animated.View
            style={{
              transform: [
                {
                  rotate: rotateAnimation.interpolate({
                    inputRange: [0, 1],
                    outputRange: ['0deg', '360deg'],
                  }),
                },
                { scale: pulseAnimation },
              ],
            }}
          >
            <Icon
              name={getStatusIcon()}
              size={16}
              color="#ffffff"
            />
          </Animated.View>
          
          <View style={styles.statusTextContainer}>
            <Text style={styles.statusMainText}>{getStatusText()}</Text>
            <Text style={styles.statusSubText}>{formatLastSync()}</Text>
          </View>
          
          {status.isSyncing && status.syncProgress !== undefined && (
            <View style={styles.progressContainer}>
              <Text style={styles.progressText}>{Math.round(status.syncProgress)}%</Text>
            </View>
          )}
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const renderDetailModal = () => (
    <Modal
      visible={showModal}
      animationType="slide"
      transparent
      onRequestClose={() => setShowModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Sync Status</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowModal(false)}
            >
              <Icon name="close" size={24} color="#ffffff" />
            </TouchableOpacity>
          </View>

          <View style={styles.modalContent}>
            {/* Connection Status */}
            <View style={styles.detailSection}>
              <View style={styles.detailHeader}>
                <Icon
                  name={status.isOnline ? 'wifi' : 'wifi-off'}
                  size={20}
                  color={status.isOnline ? '#10b981' : '#ef4444'}
                />
                <Text style={styles.detailTitle}>Connection</Text>
              </View>
              <Text style={styles.detailValue}>
                {status.isOnline ? 'Online' : 'Offline'}
              </Text>
            </View>

            {/* Sync Status */}
            <View style={styles.detailSection}>
              <View style={styles.detailHeader}>
                <Icon
                  name="sync"
                  size={20}
                  color={status.isSyncing ? '#3b82f6' : '#6b7280'}
                />
                <Text style={styles.detailTitle}>Synchronization</Text>
              </View>
              <Text style={styles.detailValue}>
                {status.isSyncing ? 'In Progress' : 'Idle'}
              </Text>
              {status.isSyncing && status.syncProgress !== undefined && (
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${status.syncProgress}%` },
                    ]}
                  />
                </View>
              )}
            </View>

            {/* Pending Items */}
            <View style={styles.detailSection}>
              <View style={styles.detailHeader}>
                <Icon
                  name="clock-outline"
                  size={20}
                  color={status.pendingItems > 0 ? '#f59e0b' : '#6b7280'}
                />
                <Text style={styles.detailTitle}>Pending Items</Text>
              </View>
              <Text style={styles.detailValue}>
                {status.pendingItems} items waiting to sync
              </Text>
            </View>

            {/* Failed Items */}
            <View style={styles.detailSection}>
              <View style={styles.detailHeader}>
                <Icon
                  name="alert-circle"
                  size={20}
                  color={status.failedItems > 0 ? '#ef4444' : '#6b7280'}
                />
                <Text style={styles.detailTitle}>Failed Items</Text>
              </View>
              <Text style={styles.detailValue}>
                {status.failedItems} items failed to sync
              </Text>
              {status.failedItems > 0 && onRetrySync && (
                <TouchableOpacity
                  style={styles.retryButton}
                  onPress={() => {
                    onRetrySync();
                    setShowModal(false);
                  }}
                >
                  <Icon name="refresh" size={16} color="#ffffff" />
                  <Text style={styles.retryButtonText}>Retry Failed</Text>
                </TouchableOpacity>
              )}
            </View>

            {/* Last Sync */}
            <View style={styles.detailSection}>
              <View style={styles.detailHeader}>
                <Icon name="history" size={20} color="#6b7280" />
                <Text style={styles.detailTitle}>Last Sync</Text>
              </View>
              <Text style={styles.detailValue}>
                {status.lastSyncTime
                  ? status.lastSyncTime.toLocaleString()
                  : 'Never'}
              </Text>
            </View>
          </View>

          <View style={styles.modalActions}>
            <TouchableOpacity
              style={styles.modalButton}
              onPress={() => setShowModal(false)}
            >
              <Text style={styles.modalButtonText}>Close</Text>
            </TouchableOpacity>
            
            {onRetrySync && (
              <TouchableOpacity
                style={[styles.modalButton, styles.primaryButton]}
                onPress={() => {
                  onRetrySync();
                  setShowModal(false);
                }}
              >
                <Icon name="sync" size={16} color="#ffffff" />
                <Text style={[styles.modalButtonText, styles.primaryButtonText]}>
                  Sync Now
                </Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </View>
    </Modal>
  );

  return (
    <>
      {showDetails ? renderExpandedIndicator() : renderCompactIndicator()}
      {renderDetailModal()}
    </>
  );
};

const styles = StyleSheet.create({
  compactContainer: {
    position: 'relative',
  },
  statusIndicator: {
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pendingBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: '#ef4444',
    borderRadius: 8,
    minWidth: 16,
    height: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pendingText: {
    fontSize: 8,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  expandedContainer: {
    borderRadius: 8,
    overflow: 'hidden',
  },
  expandedGradient: {
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  expandedContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusTextContainer: {
    flex: 1,
    marginLeft: 8,
  },
  statusMainText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
  },
  statusSubText: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.8)',
  },
  progressContainer: {
    marginLeft: 8,
  },
  progressText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    width: '90%',
    maxWidth: 400,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    padding: 4,
  },
  modalContent: {
    padding: 16,
  },
  detailSection: {
    marginBottom: 16,
  },
  detailHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
  detailValue: {
    fontSize: 14,
    color: '#94a3b8',
    marginLeft: 28,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#374151',
    borderRadius: 2,
    marginLeft: 28,
    marginTop: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    borderRadius: 2,
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ef4444',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginLeft: 28,
    marginTop: 8,
    alignSelf: 'flex-start',
  },
  retryButtonText: {
    fontSize: 12,
    color: '#ffffff',
    marginLeft: 4,
    fontWeight: '600',
  },
  modalActions: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#6b7280',
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    borderColor: '#3b82f6',
    flexDirection: 'row',
  },
  modalButtonText: {
    fontSize: 16,
    color: '#6b7280',
  },
  primaryButtonText: {
    color: '#ffffff',
    marginLeft: 4,
  },
});

export default SyncStatusIndicator;