/**
 * Mobile Remix Studio - AI-Powered Content Creation Studio
 * 
 * Advanced mobile studio for remixing, editing, and enhancing content
 * with AI-powered tools and professional-grade features.
 * 
 * Author: Fahed Mlaiel <mlaiel@live.de>
 * Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️  CRITICAL LEGAL NOTICE:
 * This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
 * Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
 * Contact: mlaiel@live.de for licensing inquiries.
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Animated,
  PanGestureHandler,
  State,
  Alert,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import LinearGradient from 'react-native-linear-gradient';
import Slider from '@react-native-community/slider';

import { RemixProject, RemixModification, ExportOptions, RemixStudioProps } from './types';

const { width, height } = Dimensions.get('window');

interface MobileRemixStudioProps extends RemixStudioProps {
  onSaveProject?: () => void;
  onShareProject?: () => void;
  onCollaborate?: () => void;
  theme?: 'light' | 'dark';
}

const MobileRemixStudio: React.FC<MobileRemixStudioProps> = ({
  project,
  onProjectUpdate,
  onExport,
  availableEffects,
  isProcessing = false,
  onSaveProject,
  onShareProject,
  onCollaborate,
  theme = 'dark',
  style,
  testID,
}) => {
  const [selectedTrack, setSelectedTrack] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(300); // 5 minutes default
  const [isPlaying, setIsPlaying] = useState(false);
  const [showEffectsPanel, setShowEffectsPanel] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [selectedEffect, setSelectedEffect] = useState<string | null>(null);
  const [effectParameters, setEffectParameters] = useState<Record<string, number>>({});
  const [zoomLevel, setZoomLevel] = useState(1);
  const [playheadPosition] = useState(new Animated.Value(0));

  const timelineRef = useRef<ScrollView>(null);

  useEffect(() => {
    // Simulate playhead movement
    if (isPlaying) {
      const interval = setInterval(() => {
        setCurrentTime((prev) => {
          const newTime = prev + 0.1;
          if (newTime >= duration) {
            setIsPlaying(false);
            return 0;
          }
          return newTime;
        });
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isPlaying, duration]);

  useEffect(() => {
    // Update playhead position animation
    Animated.timing(playheadPosition, {
      toValue: (currentTime / duration) * width * zoomLevel,
      duration: 100,
      useNativeDriver: false,
    }).start();
  }, [currentTime, duration, zoomLevel, playheadPosition]);

  const handlePlayPause = useCallback(() => {
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  const handleStop = useCallback(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, []);

  const handleTimelineSeek = useCallback((position: number) => {
    const newTime = (position / (width * zoomLevel)) * duration;
    setCurrentTime(Math.max(0, Math.min(newTime, duration)));
  }, [duration, zoomLevel]);

  const applyEffect = useCallback((effectType: string, parameters: Record<string, number>) => {
    const modification: RemixModification = {
      id: Date.now().toString(),
      type: 'effect',
      parameters: { effectType, ...parameters },
      timestamp: new Date(),
    };

    const updatedProject = {
      ...project,
      modifications: [...project.modifications, modification],
      updatedAt: new Date(),
    };

    onProjectUpdate(updatedProject);
    setShowEffectsPanel(false);
  }, [project, onProjectUpdate]);

  const removeModification = useCallback((modificationId: string) => {
    const updatedProject = {
      ...project,
      modifications: project.modifications.filter(mod => mod.id !== modificationId),
      updatedAt: new Date(),
    };

    onProjectUpdate(updatedProject);
  }, [project, onProjectUpdate]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderTimeline = () => (
    <View style={styles.timelineContainer}>
      {/* Timeline Header */}
      <View style={styles.timelineHeader}>
        <Text style={styles.timelineTitle}>Timeline</Text>
        <View style={styles.timelineControls}>
          <TouchableOpacity
            style={styles.zoomButton}
            onPress={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.5))}
          >
            <Icon name="magnify-minus" size={20} color="#ffffff" />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.zoomButton}
            onPress={() => setZoomLevel(Math.min(3, zoomLevel + 0.5))}
          >
            <Icon name="magnify-plus" size={20} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Time Ruler */}
      <View style={styles.timeRuler}>
        {Array.from({ length: Math.ceil(duration / 10) }, (_, i) => (
          <View key={i} style={styles.timeMarker}>
            <Text style={styles.timeMarkerText}>{formatTime(i * 10)}</Text>
            <View style={styles.timeMarkerLine} />
          </View>
        ))}
      </View>

      {/* Timeline Tracks */}
      <ScrollView
        ref={timelineRef}
        horizontal
        style={styles.timelineTracks}
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ width: width * zoomLevel }}
      >
        <View style={styles.tracksContainer}>
          {/* Main Track */}
          <TouchableOpacity
            style={[
              styles.track,
              selectedTrack === 0 && styles.selectedTrack,
            ]}
            onPress={() => setSelectedTrack(0)}
          >
            <Text style={styles.trackLabel}>Main</Text>
            <View style={styles.trackContent}>
              <LinearGradient
                colors={['#3b82f6', '#1d4ed8']}
                style={styles.audioWaveform}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
              >
                {/* Simulated waveform */}
                {Array.from({ length: 50 }, (_, i) => (
                  <View
                    key={i}
                    style={[
                      styles.waveformBar,
                      { height: Math.random() * 40 + 10 },
                    ]}
                  />
                ))}
              </LinearGradient>
            </View>
          </TouchableOpacity>

          {/* Effect Layers */}
          {project.modifications.map((modification, index) => (
            <TouchableOpacity
              key={modification.id}
              style={[
                styles.track,
                styles.effectTrack,
                selectedTrack === index + 1 && styles.selectedTrack,
              ]}
              onPress={() => setSelectedTrack(index + 1)}
            >
              <Text style={styles.trackLabel}>
                {modification.type.charAt(0).toUpperCase() + modification.type.slice(1)}
              </Text>
              <View style={styles.trackContent}>
                <View style={styles.effectBlock}>
                  <Text style={styles.effectBlockText}>
                    {modification.parameters.effectType || modification.type}
                  </Text>
                  <TouchableOpacity
                    style={styles.removeEffectButton}
                    onPress={() => removeModification(modification.id)}
                  >
                    <Icon name="close" size={12} color="#ffffff" />
                  </TouchableOpacity>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Playhead */}
        <Animated.View
          style={[
            styles.playhead,
            { left: playheadPosition },
          ]}
        />
      </ScrollView>
    </View>
  );

  const renderTransportControls = () => (
    <View style={styles.transportContainer}>
      <LinearGradient
        colors={['#1e293b', '#334155']}
        style={styles.transportGradient}
      >
        <View style={styles.transportControls}>
          <TouchableOpacity style={styles.transportButton} onPress={handleStop}>
            <Icon name="stop" size={24} color="#ffffff" />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.transportButton, styles.playButton]}
            onPress={handlePlayPause}
          >
            <Icon
              name={isPlaying ? 'pause' : 'play'}
              size={28}
              color="#ffffff"
            />
          </TouchableOpacity>

          <TouchableOpacity style={styles.transportButton}>
            <Icon name="record" size={24} color="#ef4444" />
          </TouchableOpacity>
        </View>

        <View style={styles.timeDisplay}>
          <Text style={styles.currentTimeText}>{formatTime(currentTime)}</Text>
          <Text style={styles.separatorText}>/</Text>
          <Text style={styles.durationText}>{formatTime(duration)}</Text>
        </View>

        <View style={styles.additionalControls}>
          <TouchableOpacity
            style={styles.controlButton}
            onPress={() => setShowEffectsPanel(true)}
          >
            <Icon name="tune" size={20} color="#ffffff" />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.controlButton}
            onPress={() => setShowExportModal(true)}
          >
            <Icon name="export" size={20} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </LinearGradient>
    </View>
  );

  const renderEffectsPanel = () => (
    <Modal
      visible={showEffectsPanel}
      animationType="slide"
      transparent
      onRequestClose={() => setShowEffectsPanel(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.effectsPanelContainer}>
          <View style={styles.effectsPanelHeader}>
            <Text style={styles.effectsPanelTitle}>Effects</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowEffectsPanel(false)}
            >
              <Icon name="close" size={24} color="#ffffff" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.effectsList}>
            {availableEffects.map((effect) => (
              <TouchableOpacity
                key={effect}
                style={[
                  styles.effectItem,
                  selectedEffect === effect && styles.selectedEffectItem,
                ]}
                onPress={() => setSelectedEffect(effect)}
              >
                <Icon name="auto-fix" size={24} color="#3b82f6" />
                <Text style={styles.effectItemText}>{effect}</Text>
                <Icon name="chevron-right" size={20} color="#94a3b8" />
              </TouchableOpacity>
            ))}
          </ScrollView>

          {selectedEffect && (
            <View style={styles.effectParameters}>
              <Text style={styles.parametersTitle}>Parameters</Text>
              
              {/* Example parameters for demonstration */}
              <View style={styles.parameterControl}>
                <Text style={styles.parameterLabel}>Intensity</Text>
                <Slider
                  style={styles.parameterSlider}
                  minimumValue={0}
                  maximumValue={100}
                  value={effectParameters.intensity || 50}
                  onValueChange={(value) =>
                    setEffectParameters(prev => ({ ...prev, intensity: value }))
                  }
                  thumbStyle={styles.sliderThumb}
                  trackStyle={styles.sliderTrack}
                  minimumTrackTintColor="#3b82f6"
                  maximumTrackTintColor="#334155"
                />
                <Text style={styles.parameterValue}>
                  {Math.round(effectParameters.intensity || 50)}%
                </Text>
              </View>

              <View style={styles.parameterControl}>
                <Text style={styles.parameterLabel}>Mix</Text>
                <Slider
                  style={styles.parameterSlider}
                  minimumValue={0}
                  maximumValue={100}
                  value={effectParameters.mix || 30}
                  onValueChange={(value) =>
                    setEffectParameters(prev => ({ ...prev, mix: value }))
                  }
                  thumbStyle={styles.sliderThumb}
                  trackStyle={styles.sliderTrack}
                  minimumTrackTintColor="#3b82f6"
                  maximumTrackTintColor="#334155"
                />
                <Text style={styles.parameterValue}>
                  {Math.round(effectParameters.mix || 30)}%
                </Text>
              </View>

              <TouchableOpacity
                style={styles.applyEffectButton}
                onPress={() => applyEffect(selectedEffect, effectParameters)}
              >
                <Text style={styles.applyEffectButtonText}>Apply Effect</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>
      </View>
    </Modal>
  );

  const renderExportModal = () => (
    <Modal
      visible={showExportModal}
      animationType="slide"
      transparent
      onRequestClose={() => setShowExportModal(false)}
    >
      <View style={styles.modalOverlay}>
        <View style={styles.exportModalContainer}>
          <View style={styles.exportModalHeader}>
            <Text style={styles.exportModalTitle}>Export Project</Text>
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowExportModal(false)}
            >
              <Icon name="close" size={24} color="#ffffff" />
            </TouchableOpacity>
          </View>

          <ScrollView style={styles.exportOptions}>
            <View style={styles.exportSection}>
              <Text style={styles.exportSectionTitle}>Format</Text>
              {['mp3', 'wav', 'flac', 'aac'].map((format) => (
                <TouchableOpacity
                  key={format}
                  style={styles.exportOption}
                  onPress={() =>
                    onExport({
                      ...project.exportOptions,
                      format,
                    })
                  }
                >
                  <Text style={styles.exportOptionText}>
                    {format.toUpperCase()}
                  </Text>
                  <Icon name="chevron-right" size={20} color="#94a3b8" />
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.exportSection}>
              <Text style={styles.exportSectionTitle}>Quality</Text>
              {(['low', 'medium', 'high', 'ultra'] as const).map((quality) => (
                <TouchableOpacity
                  key={quality}
                  style={styles.exportOption}
                  onPress={() =>
                    onExport({
                      ...project.exportOptions,
                      quality,
                    })
                  }
                >
                  <Text style={styles.exportOptionText}>
                    {quality.charAt(0).toUpperCase() + quality.slice(1)}
                  </Text>
                  <Icon name="chevron-right" size={20} color="#94a3b8" />
                </TouchableOpacity>
              ))}
            </View>
          </ScrollView>

          <View style={styles.exportActions}>
            <TouchableOpacity
              style={styles.exportButton}
              onPress={() => {
                onExport(project.exportOptions);
                setShowExportModal(false);
              }}
            >
              <Icon name="download" size={20} color="#ffffff" />
              <Text style={styles.exportButtonText}>Export</Text>
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
        <TouchableOpacity style={styles.backButton}>
          <Icon name="arrow-left" size={24} color="#ffffff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>{project.name}</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity style={styles.headerButton} onPress={onSaveProject}>
            <Icon name="content-save" size={20} color="#ffffff" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton} onPress={onShareProject}>
            <Icon name="share" size={20} color="#ffffff" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton} onPress={onCollaborate}>
            <Icon name="account-group" size={20} color="#ffffff" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Studio Content */}
      <View style={styles.studioContent}>
        {/* Timeline */}
        {renderTimeline()}

        {/* Transport Controls */}
        {renderTransportControls()}
      </View>

      {/* Processing Indicator */}
      {isProcessing && (
        <View style={styles.processingOverlay}>
          <View style={styles.processingContainer}>
            <Icon name="loading" size={32} color="#3b82f6" />
            <Text style={styles.processingText}>Processing...</Text>
          </View>
        </View>
      )}

      {/* Effects Panel */}
      {renderEffectsPanel()}

      {/* Export Modal */}
      {renderExportModal()}
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
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#1e293b',
  },
  backButton: {
    padding: 4,
    marginRight: 12,
  },
  headerTitle: {
    flex: 1,
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  headerActions: {
    flexDirection: 'row',
  },
  headerButton: {
    padding: 8,
    marginLeft: 8,
  },
  studioContent: {
    flex: 1,
  },
  timelineContainer: {
    flex: 1,
    backgroundColor: '#1e293b',
    margin: 16,
    borderRadius: 12,
  },
  timelineHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  timelineTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  timelineControls: {
    flexDirection: 'row',
  },
  zoomButton: {
    padding: 8,
    marginLeft: 8,
  },
  timeRuler: {
    flexDirection: 'row',
    height: 30,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  timeMarker: {
    width: 80,
    alignItems: 'center',
  },
  timeMarkerText: {
    fontSize: 10,
    color: '#94a3b8',
    marginBottom: 4,
  },
  timeMarkerLine: {
    width: 1,
    height: 10,
    backgroundColor: '#94a3b8',
  },
  timelineTracks: {
    flex: 1,
  },
  tracksContainer: {
    paddingHorizontal: 16,
  },
  track: {
    height: 60,
    marginBottom: 8,
    borderRadius: 8,
    backgroundColor: '#334155',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedTrack: {
    borderColor: '#3b82f6',
  },
  effectTrack: {
    height: 40,
  },
  trackLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
    padding: 8,
  },
  trackContent: {
    flex: 1,
    marginHorizontal: 8,
    marginBottom: 8,
  },
  audioWaveform: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 4,
    borderRadius: 4,
  },
  waveformBar: {
    width: 2,
    backgroundColor: 'rgba(255,255,255,0.7)',
    marginHorizontal: 1,
  },
  effectBlock: {
    flex: 1,
    backgroundColor: '#8b5cf6',
    borderRadius: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  effectBlockText: {
    fontSize: 10,
    color: '#ffffff',
    fontWeight: '600',
  },
  removeEffectButton: {
    padding: 2,
  },
  playhead: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    width: 2,
    backgroundColor: '#ef4444',
    zIndex: 10,
  },
  transportContainer: {
    borderRadius: 12,
    margin: 16,
    overflow: 'hidden',
  },
  transportGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  transportControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  transportButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  playButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#3b82f6',
  },
  timeDisplay: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  currentTimeText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  separatorText: {
    fontSize: 16,
    color: '#94a3b8',
    marginHorizontal: 8,
  },
  durationText: {
    fontSize: 16,
    color: '#94a3b8',
  },
  additionalControls: {
    flexDirection: 'row',
  },
  controlButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#334155',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: 8,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'flex-end',
  },
  effectsPanelContainer: {
    backgroundColor: '#1e293b',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%',
  },
  effectsPanelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  effectsPanelTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  closeButton: {
    padding: 4,
  },
  effectsList: {
    maxHeight: 200,
    padding: 16,
  },
  effectItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#334155',
    borderRadius: 8,
    marginBottom: 8,
  },
  selectedEffectItem: {
    backgroundColor: '#3b82f6',
  },
  effectItemText: {
    flex: 1,
    fontSize: 16,
    color: '#ffffff',
    marginLeft: 12,
  },
  effectParameters: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  parametersTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  parameterControl: {
    marginBottom: 16,
  },
  parameterLabel: {
    fontSize: 14,
    color: '#94a3b8',
    marginBottom: 8,
  },
  parameterSlider: {
    height: 40,
    marginBottom: 4,
  },
  sliderThumb: {
    backgroundColor: '#3b82f6',
    width: 20,
    height: 20,
  },
  sliderTrack: {
    height: 4,
    borderRadius: 2,
  },
  parameterValue: {
    fontSize: 12,
    color: '#ffffff',
    textAlign: 'right',
  },
  applyEffectButton: {
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  applyEffectButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  exportModalContainer: {
    backgroundColor: '#1e293b',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '70%',
  },
  exportModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  exportModalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  exportOptions: {
    padding: 16,
  },
  exportSection: {
    marginBottom: 24,
  },
  exportSectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  exportOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#334155',
    borderRadius: 8,
    marginBottom: 8,
  },
  exportOptionText: {
    fontSize: 14,
    color: '#ffffff',
  },
  exportActions: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  exportButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#3b82f6',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
  },
  exportButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginLeft: 8,
  },
  processingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  processingContainer: {
    backgroundColor: '#1e293b',
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  processingText: {
    fontSize: 16,
    color: '#ffffff',
    marginTop: 12,
  },
});

export default MobileRemixStudio;