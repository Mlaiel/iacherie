/**
 * Upload Screen - Mobile content upload interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  PermissionsAndroid,
  Platform,
} from 'react-native';
import { launchImageLibrary, launchCamera, ImagePickerResponse } from 'react-native-image-picker';
import DocumentPicker from 'react-native-document-picker';
import Icon from 'react-native-vector-icons/MaterialIcons';

const UploadScreen: React.FC = () => {
  const [uploads, setUploads] = React.useState<Array<{
    id: string;
    name: string;
    type: string;
    size: string;
    progress: number;
    status: 'uploading' | 'completed' | 'failed';
  }>>([]);

  const requestCameraPermission = async () => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
          {
            title: 'Camera Permission',
            message: 'Ainflue needs access to camera to capture content',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          },
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }
    return true;
  };

  const handleCameraCapture = async () => {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) {
      Alert.alert('Permission denied', 'Camera permission is required to capture content');
      return;
    }

    launchCamera({ mediaType: 'mixed', quality: 0.8 }, (response: ImagePickerResponse) => {
      if (response.assets && response.assets[0]) {
        const asset = response.assets[0];
        simulateUpload({
          name: asset.fileName || 'Camera_Capture',
          type: asset.type || 'image/jpeg',
          size: formatFileSize(asset.fileSize || 0),
        });
      }
    });
  };

  const handleGalleryPicker = () => {
    launchImageLibrary({ mediaType: 'mixed', quality: 0.8 }, (response: ImagePickerResponse) => {
      if (response.assets && response.assets[0]) {
        const asset = response.assets[0];
        simulateUpload({
          name: asset.fileName || 'Gallery_Image',
          type: asset.type || 'image/jpeg',
          size: formatFileSize(asset.fileSize || 0),
        });
      }
    });
  };

  const handleDocumentPicker = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });
      
      if (result[0]) {
        simulateUpload({
          name: result[0].name,
          type: result[0].type || 'application/octet-stream',
          size: formatFileSize(result[0].size || 0),
        });
      }
    } catch (err) {
      if (DocumentPicker.isCancel(err)) {
        console.log('User cancelled document picker');
      } else {
        console.error('Error picking document:', err);
      }
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const simulateUpload = (file: { name: string; type: string; size: string }) => {
    const newUpload = {
      id: Date.now().toString(),
      name: file.name,
      type: file.type,
      size: file.size,
      progress: 0,
      status: 'uploading' as const,
    };

    setUploads(prev => [newUpload, ...prev]);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploads(prev => prev.map(upload => {
        if (upload.id === newUpload.id) {
          const newProgress = upload.progress + Math.random() * 20;
          if (newProgress >= 100) {
            clearInterval(interval);
            return { ...upload, progress: 100, status: 'completed' };
          }
          return { ...upload, progress: newProgress };
        }
        return upload;
      }));
    }, 300);
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return 'image';
    if (type.startsWith('video/')) return 'videocam';
    if (type.startsWith('audio/')) return 'audiotrack';
    return 'insert-drive-file';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#10B981';
      case 'failed': return '#EF4444';
      default: return '#3B82F6';
    }
  };

  const UploadOption = ({ title, description, icon, color, onPress }: {
    title: string;
    description: string;
    icon: string;
    color: string;
    onPress: () => void;
  }) => (
    <TouchableOpacity style={styles.uploadOption} onPress={onPress}>
      <View style={[styles.uploadIcon, { backgroundColor: color }]}>
        <Icon name={icon} size={32} color="#fff" />
      </View>
      <View style={styles.uploadContent}>
        <Text style={styles.uploadTitle}>{title}</Text>
        <Text style={styles.uploadDescription}>{description}</Text>
      </View>
      <Icon name="chevron-right" size={24} color="#9CA3AF" />
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Upload Content</Text>
        <Text style={styles.headerSubtitle}>Add content to your library</Text>
      </View>

      {/* Upload Options */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Choose Upload Method</Text>
        
        <UploadOption
          title="Camera"
          description="Capture photo or video"
          icon="camera-alt"
          color="#3B82F6"
          onPress={handleCameraCapture}
        />
        
        <UploadOption
          title="Gallery"
          description="Select from photo library"
          icon="photo-library"
          color="#10B981"
          onPress={handleGalleryPicker}
        />
        
        <UploadOption
          title="Files"
          description="Browse and select files"
          icon="folder-open"
          color="#F59E0B"
          onPress={handleDocumentPicker}
        />
      </View>

      {/* Upload Queue */}
      {uploads.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Upload Queue</Text>
          <View style={styles.uploadQueue}>
            {uploads.map(upload => (
              <View key={upload.id} style={styles.uploadItem}>
                <View style={styles.uploadFileInfo}>
                  <Icon 
                    name={getFileIcon(upload.type)} 
                    size={24} 
                    color="#6B7280" 
                    style={styles.fileIcon}
                  />
                  <View style={styles.fileDetails}>
                    <Text style={styles.fileName}>{upload.name}</Text>
                    <Text style={styles.fileSize}>{upload.size}</Text>
                  </View>
                </View>
                
                <View style={styles.uploadStatus}>
                  <Text style={[styles.statusText, { color: getStatusColor(upload.status) }]}>
                    {upload.status === 'uploading' 
                      ? `${Math.round(upload.progress)}%` 
                      : upload.status.toUpperCase()
                    }
                  </Text>
                  {upload.status === 'uploading' && (
                    <View style={styles.progressBar}>
                      <View 
                        style={[
                          styles.progressFill, 
                          { width: `${upload.progress}%` }
                        ]} 
                      />
                    </View>
                  )}
                </View>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Upload Tips */}
      <View style={styles.section}>
        <View style={styles.tipsCard}>
          <Icon name="lightbulb-outline" size={24} color="#F59E0B" />
          <View style={styles.tipsContent}>
            <Text style={styles.tipsTitle}>Upload Tips</Text>
            <Text style={styles.tipsText}>
              • High-quality content gets better protection{'\n'}
              • Add metadata for better organization{'\n'}
              • Large files may take longer to process{'\n'}
              • Supported formats: JPG, PNG, MP4, MP3, PDF
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  uploadOption: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 3,
    elevation: 2,
  },
  uploadIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  uploadContent: {
    flex: 1,
  },
  uploadTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  uploadDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  uploadQueue: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  uploadItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  uploadFileInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  fileIcon: {
    marginRight: 12,
  },
  fileDetails: {
    flex: 1,
  },
  fileName: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937',
  },
  fileSize: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  uploadStatus: {
    alignItems: 'flex-end',
    minWidth: 80,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
  },
  progressBar: {
    width: 60,
    height: 4,
    backgroundColor: '#E5E7EB',
    borderRadius: 2,
    marginTop: 4,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3B82F6',
    borderRadius: 2,
  },
  tipsCard: {
    backgroundColor: '#FFFBEB',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  tipsContent: {
    marginLeft: 12,
    flex: 1,
  },
  tipsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8,
  },
  tipsText: {
    fontSize: 14,
    color: '#92400E',
    lineHeight: 20,
  },
});

export default UploadScreen;