/**
 * Mobile Exporter - Advanced Content Export Manager
 * 
 * Professional mobile interface for exporting content in multiple formats
 * with quality optimization and batch processing capabilities.
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
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  Modal,
  Alert,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';

import { ExporterProps, ExportProgress, ExportOptions } from './types';

const { width } = Dimensions.get('window');

interface MobileExporterProps extends ExporterProps {
  storageQuota?: number;
  usedStorage?: number;
  onStorageManagement?: () => void;
  theme?: 'light' | 'dark';
}

const MobileExporter: React.FC<MobileExporterProps> = ({
  exports,
  onStartExport,
  onCancelExport,
  onRetryExport,
  storageQuota = 5000, // 5GB in MB
  usedStorage = 1250,   // 1.25GB in MB
  onStorageManagement,
  theme = 'dark',
  style,
  testID,
}) => {
  const [showExportModal, setShowExportModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [exportOptions, setExportOptions] = useState<ExportOptions>({
    format: 'mp4',
    quality: 'high',
    metadata: {
      title: '',
      description: '',
      tags: [],
    },
  });
  const [batchMode, setBatchMode] = useState(false);
  const [selectedExports, setSelectedExports] = useState<string[]>([]);
  const [animatedValues] = useState(
    exports.reduce((acc, exp) => {
      acc[exp.id] = new Animated.Value(0);
      return acc;
    }, {} as Record<string, Animated.Value>)
  );

  useEffect(() => {
    // Animate export items
    exports.forEach((exp, index) => {
      setTimeout(() => {
        Animated.spring(animatedValues[exp.id], {
          toValue: 1,
          tension: 100,
          friction: 8,
          useNativeDriver: true,
        }).start();
      }, index * 100);
    });
  }, [exports, animatedValues]);

  const getStatusColor = (status: ExportProgress['status']) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'processing': return '#3b82f6';
      case 'failed': return '#ef4444';
      case 'queued': return '#f59e0b';
      default: return '#6b7280';
    }
  };

  const getStatusIcon = (status: ExportProgress['status']) => {
    switch (status) {
      case 'completed': return 'check-circle';
      case 'processing': return 'loading';
      case 'failed': return 'alert-circle';
      case 'queued': return 'clock';
      default: return 'help-circle';
    }
  };

  const formatFileSize = (sizeInMB: number) => {
    if (sizeInMB >= 1000) {
      return `${(sizeInMB / 1000).toFixed(1)} GB`;
    }
    return `${sizeInMB.toFixed(0)} MB`;
  };

  const formatTimeRemaining = (progress: ExportProgress) => {
    if (!progress.estimatedCompletion || progress.status !== 'processing') return null;
    
    const now = new Date();
    const remaining = progress.estimatedCompletion.getTime() - now.getTime();
    const minutes = Math.floor(remaining / (1000 * 60));
    const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
    
    if (minutes > 0) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  };

  const handleExportStart = useCallback(() => {
    if (selectedItem) {
      onStartExport(selectedItem, exportOptions);
      setShowExportModal(false);
      setSelectedItem(null);
    }
  }, [selectedItem, exportOptions, onStartExport]);

  const handleBatchExport = useCallback(() => {
    if (selectedExports.length > 0) {
      selectedExports.forEach(exportId => {
        const exportItem = exports.find(exp => exp.id === exportId);
        if (exportItem) {
          onStartExport(exportItem, exportOptions);
        }
      });
      setSelectedExports([]);
      setBatchMode(false);
    }
  }, [selectedExports, exports, exportOptions, onStartExport]);

  const toggleExportSelection = useCallback((exportId: string) => {
    setSelectedExports(prev => 
      prev.includes(exportId)
        ? prev.filter(id => id !== exportId)
        : [...prev, exportId]
    );
  }, []);

  const getStoragePercentage = () => {
    return (usedStorage / storageQuota) * 100;
  };

  const renderStorageInfo = () => (
    <View style={styles.storageContainer}>
      <LinearGradient
        colors={getStoragePercentage() > 80 ? ['#ef4444', '#dc2626'] : ['#1e293b', '#334155']}
        style={styles.storageGradient}
      >
        <View style={styles.storageHeader}>
          <Icon name="harddisk" size={20} color="#ffffff" />
          <Text style={styles.storageTitle}>Storage</Text>
          <TouchableOpacity
            style={styles.manageButton}
            onPress={onStorageManagement}
          >
            <Text style={styles.manageButtonText}>Manage</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.storageBar}>
          <View
            style={[
              styles.storageUsed,
              { 
                width: `${Math.min(getStoragePercentage(), 100)}%`,
                backgroundColor: getStoragePercentage() > 80 ? '#ffffff' : '#3b82f6',
              },
            ]}
          />
        </View>
        
        <Text style={styles.storageText}>
          {formatFileSize(usedStorage)} of {formatFileSize(storageQuota)} used
        </Text>
      </LinearGradient>
    </View>
  );

  const renderExportItem = (exportItem: ExportProgress) => {
    const isSelected = selectedExports.includes(exportItem.id);
    
    return (
      <Animated.View
        key={exportItem.id}
        style={[
          styles.exportItem,
          {
            opacity: animatedValues[exportItem.id] || 1,
            transform: [
              {
                scale: animatedValues[exportItem.id]?.interpolate({
                  inputRange: [0, 1],
                  outputRange: [0.9, 1],
                }) || 1,
              },
            ],
          },
        ]}
      >
        <TouchableOpacity
          style={[
            styles.exportItemContent,
            isSelected && styles.selectedExportItem,
          ]}
          onPress={() => {
            if (batchMode) {
              toggleExportSelection(exportItem.id);
            }
          }}
          onLongPress={() => {
            setBatchMode(true);
            toggleExportSelection(exportItem.id);
          }}
        >
          {batchMode && (
            <View style={styles.selectionIndicator}>
              <Icon
                name={isSelected ? 'checkbox-marked' : 'checkbox-blank-outline'}
                size={20}
                color={isSelected ? '#3b82f6' : '#6b7280'}
              />
            </View>
          )}

          <View style={styles.exportInfo}>
            <View style={styles.exportHeader}>
              <Text style={styles.exportName} numberOfLines={1}>
                {exportItem.type.charAt(0).toUpperCase() + exportItem.type.slice(1)} Export
              </Text>
              <View style={styles.exportStatus}>
                <Icon
                  name={getStatusIcon(exportItem.status)}
                  size={16}
                  color={getStatusColor(exportItem.status)}
                />
                <Text
                  style={[
                    styles.statusText,
                    { color: getStatusColor(exportItem.status) },
                  ]}
                >
                  {exportItem.status.charAt(0).toUpperCase() + exportItem.status.slice(1)}
                </Text>
              </View>
            </View>

            {exportItem.status === 'processing' && (
              <View style={styles.progressContainer}>
                <View style={styles.progressBar}>
                  <View
                    style={[
                      styles.progressFill,
                      { width: `${exportItem.progress}%` },
                    ]}
                  />
                </View>
                <Text style={styles.progressText}>
                  {Math.round(exportItem.progress)}%
                </Text>
                {formatTimeRemaining(exportItem) && (
                  <Text style={styles.timeRemaining}>
                    {formatTimeRemaining(exportItem)} remaining
                  </Text>
                )}
              </View>
            )}

            {exportItem.error && (
              <Text style={styles.errorText} numberOfLines={2}>
                {exportItem.error}
              </Text>
            )}

            <View style={styles.exportMeta}>
              <Text style={styles.metaText}>
                Started: {exportItem.startTime.toLocaleTimeString()}
              </Text>
              {exportItem.outputUri && (
                <Text style={styles.metaText}>
                  Output ready
                </Text>
              )}
            </View>
          </View>

          <View style={styles.exportActions}>
            {exportItem.status === 'processing' && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => onCancelExport(exportItem.id)}
              >
                <Icon name="stop" size={16} color="#ef4444" />
              </TouchableOpacity>
            )}
            
            {exportItem.status === 'failed' && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => onRetryExport(exportItem.id)}
              >
                <Icon name="refresh" size={16} color="#3b82f6" />
              </TouchableOpacity>
            )}

            {exportItem.status === 'completed' && exportItem.outputUri && (
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => Alert.alert('Export Complete', 'File saved to device storage')}
              >
                <Icon name="download" size={16} color="#10b981" />
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => Alert.alert('Share', 'Sharing functionality coming soon')}
            >
              <Icon name="share" size={16} color="#6b7280" />
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Animated.View>
    );
  };

  const renderExportOptionsModal = () => (
    <Modal
      visible={showExportModal}
      animationType="slide"
      transparent
      onRequestClose={() => setShowExportModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Export Options</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowExportModal(false)}
            >
              <Icon name="close" size={24} color="#ffffff" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.modalContent}>
            <View style={styles.optionSection}>
              <Text style={styles.sectionTitle}>Format</Text>
              <View style={styles.optionGrid}>
                {['mp4', 'mov', 'avi', 'mp3', 'wav', 'jpg', 'png'].map((format) => (
                  <TouchableOpacity
                    key={format}
                    style={[
                      styles.optionButton,
                      exportOptions.format === format && styles.selectedOption,
                    ]}
                    onPress={() =>
                      setExportOptions(prev => ({ ...prev, format }))
                    }
                  >
                    <Text
                      style={[
                        styles.optionText,
                        exportOptions.format === format && styles.selectedOptionText,
                      ]}
                    >
                      {format.toUpperCase()}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            <View style={styles.optionSection}>
              <Text style={styles.sectionTitle}>Quality</Text>
              <View style={styles.optionGrid}>
                {(['low', 'medium', 'high', 'ultra'] as const).map((quality) => (
                  <TouchableOpacity
                    key={quality}
                    style={[
                      styles.optionButton,
                      exportOptions.quality === quality && styles.selectedOption,
                    ]}
                    onPress={() =>
                      setExportOptions(prev => ({ ...prev, quality }))
                    }
                  >
                    <Text
                      style={[
                        styles.optionText,
                        exportOptions.quality === quality && styles.selectedOptionText,
                      ]}
                    >
                      {quality.charAt(0).toUpperCase() + quality.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>

            {exportOptions.format.startsWith('mp4') && (
              <View style={styles.optionSection}>
                <Text style={styles.sectionTitle}>Resolution</Text>
                <View style={styles.optionGrid}>
                  {['720p', '1080p', '1440p', '4K'].map((resolution) => (
                    <TouchableOpacity
                      key={resolution}
                      style={[
                        styles.optionButton,
                        exportOptions.resolution === resolution && styles.selectedOption,
                      ]}
                      onPress={() =>
                        setExportOptions(prev => ({ ...prev, resolution }))
                      }
                    >
                      <Text
                        style={[
                          styles.optionText,
                          exportOptions.resolution === resolution && styles.selectedOptionText,
                        ]}
                      >
                        {resolution}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            )}
          </ScrollView>

          <View style={styles.modalActions}>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setShowExportModal(false)}
            >
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.exportButton}
              onPress={handleExportStart}
            >
              <Icon name="export" size={16} color="#ffffff" />
              <Text style={styles.exportButtonText}>Start Export</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  return (
    <SafeAreaView style={[styles.container, style]} testID={testID}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Exports</Text>
        <View style={styles.headerActions}>
          {batchMode ? (
            <>
              <TouchableOpacity
                style={styles.headerButton}
                onPress={() => {
                  setBatchMode(false);
                  setSelectedExports([]);
                }}
              >
                <Text style={styles.headerButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.headerButton,
                  selectedExports.length === 0 && styles.disabledButton,
                ]}
                onPress={handleBatchExport}
                disabled={selectedExports.length === 0}
              >
                <Text style={styles.headerButtonText}>
                  Export ({selectedExports.length})
                </Text>
              </TouchableOpacity>
            </>
          ) : (
            <TouchableOpacity
              style={styles.headerButton}
              onPress={() => {
                setSelectedItem({ type: 'content', id: 'new' });
                setShowExportModal(true);
              }}
            >
              <Icon name="plus" size={20} color="#ffffff" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Storage Info */}
      {renderStorageInfo()}

      {/* Batch Mode Toggle */}
      <View style={styles.batchModeContainer}>
        <Text style={styles.batchModeLabel}>Batch Selection</Text>
        <Switch
          value={batchMode}
          onValueChange={setBatchMode}
          trackColor={{ false: '#334155', true: '#3b82f6' }}
          thumbColor={batchMode ? '#ffffff' : '#94a3b8'}
        />
      </View>

      {/* Export List */}
      <ScrollView
        style={styles.exportList}
        showsVerticalScrollIndicator={false}
      >
        {exports.length === 0 ? (
          <View style={styles.emptyState}>
            <Icon name="export" size={64} color="#6b7280" />
            <Text style={styles.emptyStateTitle}>No Exports Yet</Text>
            <Text style={styles.emptyStateText}>
              Start exporting your content in various formats
            </Text>
            <TouchableOpacity
              style={styles.startExportButton}
              onPress={() => {
                setSelectedItem({ type: 'content', id: 'new' });
                setShowExportModal(true);
              }}
            >
              <Icon name="plus" size={20} color="#ffffff" />
              <Text style={styles.startExportButtonText}>Start Export</Text>
            </TouchableOpacity>
          </View>
        ) : (
          exports.map(renderExportItem)
        )}
      </ScrollView>

      {/* Export Options Modal */}
      {renderExportOptionsModal()}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#3b82f6',
    borderRadius: 16,
    marginLeft: 8,
  },
  disabledButton: {
    backgroundColor: '#6b7280',
  },
  headerButtonText: {
    fontSize: 14,
    color: '#ffffff',
    fontWeight: '600',
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
    paddingVertical: 4,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 12,
  },
  manageButtonText: {
    fontSize: 12,
    color: '#ffffff',
    fontWeight: '600',
  },
  storageBar: {
    height: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 4,
    marginBottom: 8,
  },
  storageUsed: {
    height: '100%',
    borderRadius: 4,
  },
  storageText: {
    fontSize: 12,
    color: '#e2e8f0',
  },
  batchModeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#1e293b',
  },
  batchModeLabel: {
    fontSize: 14,
    color: '#ffffff',
  },
  exportList: {
    flex: 1,
    paddingHorizontal: 16,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginTop: 16,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#94a3b8',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  startExportButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#3b82f6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 24,
  },
  startExportButtonText: {
    fontSize: 16,
    color: '#ffffff',
    fontWeight: '600',
    marginLeft: 8,
  },
  exportItem: {
    marginBottom: 12,
  },
  exportItemContent: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedExportItem: {
    borderColor: '#3b82f6',
  },
  selectionIndicator: {
    marginRight: 12,
    justifyContent: 'center',
  },
  exportInfo: {
    flex: 1,
  },
  exportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  exportName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    flex: 1,
  },
  exportStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4,
  },
  progressContainer: {
    marginBottom: 8,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#334155',
    borderRadius: 2,
    marginBottom: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    borderRadius: 2,
  },
  progressText: {
    fontSize: 12,
    color: '#94a3b8',
  },
  timeRemaining: {
    fontSize: 10,
    color: '#6b7280',
  },
  errorText: {
    fontSize: 12,
    color: '#ef4444',
    marginBottom: 8,
  },
  exportMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metaText: {
    fontSize: 10,
    color: '#6b7280',
  },
  exportActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    padding: 8,
    marginLeft: 4,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    backgroundColor: '#1e293b',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
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
  optionSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  optionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  optionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#334155',
    borderRadius: 20,
    marginRight: 8,
    marginBottom: 8,
  },
  selectedOption: {
    backgroundColor: '#3b82f6',
  },
  optionText: {
    fontSize: 14,
    color: '#94a3b8',
  },
  selectedOptionText: {
    color: '#ffffff',
  },
  modalActions: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#6b7280',
    borderRadius: 8,
    marginRight: 8,
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#6b7280',
  },
  exportButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    borderRadius: 8,
    marginLeft: 8,
  },
  exportButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
});

export default MobileExporter;