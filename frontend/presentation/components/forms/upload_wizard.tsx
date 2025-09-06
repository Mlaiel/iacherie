/**
 * Upload Wizard - Multi-step content upload interface
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  CloudArrowUpIcon, 
  DocumentIcon,
  MusicalNoteIcon,
  VideoCameraIcon,
  PhotoIcon,
  CheckCircleIcon,
  XMarkIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

interface UploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

interface UploadSettings {
  protection: boolean;
  watermark: boolean;
  autoDistribute: boolean;
  platforms: string[];
  visibility: 'public' | 'private' | 'unlisted';
}

const UploadWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = React.useState(1);
  const [files, setFiles] = React.useState<UploadFile[]>([]);
  const [settings, setSettings] = React.useState<UploadSettings>({
    protection: true,
    watermark: false,
    autoDistribute: false,
    platforms: [],
    visibility: 'private'
  });
  const [dragActive, setDragActive] = React.useState(false);

  const steps = [
    { number: 1, title: 'Upload Files', description: 'Select and upload your content' },
    { number: 2, title: 'Configure Settings', description: 'Set protection and distribution options' },
    { number: 3, title: 'Review & Submit', description: 'Review your uploads and submit' }
  ];

  const platforms = ['YouTube', 'Spotify', 'SoundCloud', 'Apple Music', 'Instagram', 'TikTok'];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    handleFiles(selectedFiles);
  };

  const handleFiles = (fileList: File[]) => {
    const newFiles: UploadFile[] = fileList.map((file, index) => ({
      id: `file-${Date.now()}-${index}`,
      name: file.name,
      size: file.size,
      type: file.type,
      progress: 0,
      status: 'pending'
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
    
    // Simulate upload progress
    newFiles.forEach((file, index) => {
      setTimeout(() => {
        simulateUpload(file.id);
      }, index * 500);
    });
  };

  const simulateUpload = (fileId: string) => {
    let progress = 0;
    
    setFiles(prev => prev.map(file => 
      file.id === fileId ? { ...file, status: 'uploading' as const } : file
    ));

    const interval = setInterval(() => {
      progress += Math.random() * 20;
      
      if (progress >= 100) {
        clearInterval(interval);
        setFiles(prev => prev.map(file => 
          file.id === fileId ? { 
            ...file, 
            progress: 100, 
            status: Math.random() > 0.1 ? 'completed' : 'error',
            error: Math.random() > 0.1 ? undefined : 'Upload failed'
          } : file
        ));
      } else {
        setFiles(prev => prev.map(file => 
          file.id === fileId ? { ...file, progress: Math.round(progress) } : file
        ));
      }
    }, 200);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('audio/')) return <MusicalNoteIcon className="h-8 w-8 text-green-500" />;
    if (type.startsWith('video/')) return <VideoCameraIcon className="h-8 w-8 text-red-500" />;
    if (type.startsWith('image/')) return <PhotoIcon className="h-8 w-8 text-blue-500" />;
    return <DocumentIcon className="h-8 w-8 text-gray-500" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'uploading': return 'text-blue-600';
      case 'processing': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const canProceed = () => {
    if (currentStep === 1) return files.some(f => f.status === 'completed');
    if (currentStep === 2) return true;
    return true;
  };

  const nextStep = () => {
    if (canProceed() && currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Wizard</h1>
        <p className="text-gray-600">Upload and protect your content in just a few steps</p>
      </div>

      {/* Step Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                currentStep >= step.number 
                  ? 'bg-blue-600 border-blue-600 text-white' 
                  : 'border-gray-300 text-gray-500'
              }`}>
                {currentStep > step.number ? (
                  <CheckCircleIcon className="h-6 w-6" />
                ) : (
                  step.number
                )}
              </div>
              <div className="ml-3">
                <div className={`text-sm font-medium ${
                  currentStep >= step.number ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
              {index < steps.length - 1 && (
                <ArrowRightIcon className="h-5 w-5 text-gray-400 mx-6" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {currentStep === 1 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Upload Your Files</h2>
            
            {/* Upload Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <CloudArrowUpIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Drop files here or click to browse
              </h3>
              <p className="text-gray-600 mb-4">
                Support for audio, video, images, and documents
              </p>
              <input
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                id="file-upload"
                accept="audio/*,video/*,image/*,.pdf,.doc,.docx"
              />
              <label
                htmlFor="file-upload"
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors cursor-pointer inline-block"
              >
                Select Files
              </label>
            </div>

            {/* File List */}
            {files.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Uploaded Files</h3>
                <div className="space-y-4">
                  {files.map((file) => (
                    <div key={file.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          {getFileIcon(file.type)}
                          <div>
                            <div className="font-medium text-gray-900">{file.name}</div>
                            <div className="text-sm text-gray-500">{formatFileSize(file.size)}</div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`text-sm font-medium ${getStatusColor(file.status)}`}>
                            {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                          </span>
                          <button
                            onClick={() => removeFile(file.id)}
                            className="text-gray-400 hover:text-red-600"
                          >
                            <XMarkIcon className="h-5 w-5" />
                          </button>
                        </div>
                      </div>

                      {file.status === 'uploading' && (
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${file.progress}%` }}
                          ></div>
                        </div>
                      )}

                      {file.error && (
                        <div className="text-sm text-red-600 mt-2">{file.error}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Configure Settings</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Protection Settings */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Protection Options</h3>
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Enable Content Protection</span>
                      <p className="text-xs text-gray-500">Apply fingerprinting and monitoring</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.protection}
                      onChange={(e) => setSettings(prev => ({ ...prev, protection: e.target.checked }))}
                      className="toggle"
                    />
                  </label>

                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Add Watermark</span>
                      <p className="text-xs text-gray-500">Add visible watermark to content</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.watermark}
                      onChange={(e) => setSettings(prev => ({ ...prev, watermark: e.target.checked }))}
                      className="toggle"
                    />
                  </label>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Visibility</label>
                    <select
                      value={settings.visibility}
                      onChange={(e) => setSettings(prev => ({ ...prev, visibility: e.target.value as 'private' | 'unlisted' | 'public' }))}
                      className="w-full border border-gray-300 rounded-md px-3 py-2"
                    >
                      <option value="private">Private</option>
                      <option value="unlisted">Unlisted</option>
                      <option value="public">Public</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Distribution Settings */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Distribution Options</h3>
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Auto-Distribute</span>
                      <p className="text-xs text-gray-500">Automatically distribute to selected platforms</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.autoDistribute}
                      onChange={(e) => setSettings(prev => ({ ...prev, autoDistribute: e.target.checked }))}
                      className="toggle"
                    />
                  </label>

                  {settings.autoDistribute && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Select Platforms</label>
                      <div className="space-y-2">
                        {platforms.map((platform) => (
                          <label key={platform} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={settings.platforms.includes(platform)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSettings(prev => ({
                                    ...prev,
                                    platforms: [...prev.platforms, platform]
                                  }));
                                } else {
                                  setSettings(prev => ({
                                    ...prev,
                                    platforms: prev.platforms.filter(p => p !== platform)
                                  }));
                                }
                              }}
                              className="mr-2"
                            />
                            <span className="text-sm text-gray-700">{platform}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Review & Submit</h2>
            
            <div className="space-y-6">
              {/* Files Summary */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Files to Upload</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600">
                    {files.filter(f => f.status === 'completed').length} files ready for processing
                  </div>
                </div>
              </div>

              {/* Settings Summary */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Summary</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <div className="text-sm">
                    <span className="font-medium">Protection:</span> {settings.protection ? 'Enabled' : 'Disabled'}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Watermark:</span> {settings.watermark ? 'Enabled' : 'Disabled'}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Visibility:</span> {settings.visibility}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Auto-Distribution:</span> {settings.autoDistribute ? 'Enabled' : 'Disabled'}
                  </div>
                  {settings.autoDistribute && settings.platforms.length > 0 && (
                    <div className="text-sm">
                      <span className="font-medium">Platforms:</span> {settings.platforms.join(', ')}
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  Ready to submit! Your files will be processed and protected according to your settings.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8 pt-6 border-t">
          <button
            onClick={prevStep}
            disabled={currentStep === 1}
            className={`flex items-center px-4 py-2 rounded-md transition-colors ${
              currentStep === 1
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Previous
          </button>

          {currentStep < 3 ? (
            <button
              onClick={nextStep}
              disabled={!canProceed()}
              className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                canProceed()
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 text-gray-400 cursor-not-allowed'
              }`}
            >
              Next
              <ArrowRightIcon className="h-5 w-5 ml-2" />
            </button>
          ) : (
            <button className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors">
              Submit Upload
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadWizard;