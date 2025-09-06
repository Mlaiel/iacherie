/**
 * Upload Wizard - Guided content upload process
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 */

import React from 'react';
import { 
  CloudArrowUpIcon,
  DocumentIcon,
  MusicalNoteIcon,
  PhotoIcon,
  VideoCameraIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

interface UploadFile {
  id: string;
  file: File;
  type: 'audio' | 'video' | 'image' | 'document';
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  fingerprint?: string;
}

interface UploadStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

const UploadWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = React.useState(0);
  const [files, setFiles] = React.useState<UploadFile[]>([]);
  const [isUploading, setIsUploading] = React.useState(false);
  const [dragActive, setDragActive] = React.useState(false);

  const steps: UploadStep[] = [
    { id: 0, title: 'Select Files', description: 'Choose your content files', completed: false },
    { id: 1, title: 'Configure', description: 'Set protection settings', completed: false },
    { id: 2, title: 'Upload', description: 'Upload and process files', completed: false },
    { id: 3, title: 'Complete', description: 'Review and finalize', completed: false }
  ];

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const getFileType = (file: File): 'audio' | 'video' | 'image' | 'document' => {
    if (file.type.startsWith('audio/')) return 'audio';
    if (file.type.startsWith('video/')) return 'video';
    if (file.type.startsWith('image/')) return 'image';
    return 'document';
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'audio': return <MusicalNoteIcon className="h-8 w-8 text-purple-500" />;
      case 'video': return <VideoCameraIcon className="h-8 w-8 text-red-500" />;
      case 'image': return <PhotoIcon className="h-8 w-8 text-blue-500" />;
      default: return <DocumentIcon className="h-8 w-8 text-gray-500" />;
    }
  };

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return;

    const newFiles: UploadFile[] = Array.from(selectedFiles).map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      type: getFileType(file),
      progress: 0,
      status: 'pending'
    }));

    setFiles(prev => [...prev, ...newFiles]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const startUpload = async () => {
    setIsUploading(true);
    
    for (const file of files) {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 100));
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, progress, status: progress === 100 ? 'processing' : 'uploading' } : f
        ));
      }

      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 1000));
      setFiles(prev => prev.map(f => 
        f.id === file.id 
          ? { ...f, status: 'completed', fingerprint: `fp_${Math.random().toString(36).substr(2, 8)}` }
          : f
      ));
    }
    
    setIsUploading(false);
    setCurrentStep(3);
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Wizard</h1>
        <p className="text-gray-600">Upload and protect your content with AI-powered fingerprinting</p>
      </div>

      {/* Step Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                index <= currentStep ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                {index < currentStep ? (
                  <CheckCircleIcon className="h-6 w-6" />
                ) : (
                  <span>{step.id + 1}</span>
                )}
              </div>
              <div className="ml-3">
                <div className={`text-sm font-medium ${
                  index <= currentStep ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500">{step.description}</div>
              </div>
              {index < steps.length - 1 && (
                <div className={`mx-4 h-0.5 w-16 ${
                  index < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {currentStep === 0 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Select Your Files</h2>
            
            {/* File Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
            >
              <CloudArrowUpIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Drag & drop files here, or click to select files
              </h3>
              <p className="text-gray-600 mb-4">
                Supports: Audio (MP3, WAV, FLAC), Video (MP4, AVI, MOV), Images (JPG, PNG, GIF), Documents (PDF, TXT)
              </p>
              <p className="text-sm text-gray-500">Maximum file size: 100MB per file</p>
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="audio/*,video/*,image/*,.pdf,.txt"
                onChange={(e) => handleFileSelect(e.target.files)}
                className="hidden"
              />
            </div>

            {/* Selected Files */}
            {files.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Selected Files ({files.length})</h3>
                <div className="space-y-3">
                  {files.map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getFileIcon(file.type)}
                        <div>
                          <div className="font-medium text-gray-900">{file.file.name}</div>
                          <div className="text-sm text-gray-500">
                            {file.type} • {formatFileSize(file.file.size)}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(file.id)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Configure Protection Settings</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Protection Level
                </label>
                <select className="w-full border border-gray-300 rounded-md px-3 py-2">
                  <option value="standard">Standard Protection</option>
                  <option value="enhanced">Enhanced Protection</option>
                  <option value="maximum">Maximum Protection</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Monitoring Platforms
                </label>
                <div className="space-y-2">
                  {['YouTube', 'SoundCloud', 'Spotify', 'Instagram', 'TikTok'].map((platform) => (
                    <label key={platform} className="flex items-center">
                      <input type="checkbox" defaultChecked className="mr-2" />
                      <span className="text-sm text-gray-700">{platform}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Auto-DMCA
                </label>
                <label className="flex items-center">
                  <input type="checkbox" defaultChecked className="mr-2" />
                  <span className="text-sm text-gray-700">
                    Automatically send DMCA takedown notices for violations
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Upload Progress</h2>
            
            <div className="space-y-4">
              {files.map((file) => (
                <div key={file.id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      {getFileIcon(file.type)}
                      <div>
                        <div className="font-medium text-gray-900">{file.file.name}</div>
                        <div className="text-sm text-gray-500">Status: {file.status}</div>
                      </div>
                    </div>
                    {file.status === 'completed' && (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    )}
                    {file.status === 'error' && (
                      <ExclamationCircleIcon className="h-6 w-6 text-red-500" />
                    )}
                  </div>
                  
                  {(file.status === 'uploading' || file.status === 'processing') && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      ></div>
                    </div>
                  )}
                  
                  {file.fingerprint && (
                    <div className="mt-2 text-xs text-gray-500">
                      Fingerprint: {file.fingerprint}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {!isUploading && files.length > 0 && (
              <button
                onClick={startUpload}
                className="mt-6 w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Start Upload & Processing
              </button>
            )}
          </div>
        )}

        {currentStep === 3 && (
          <div className="text-center">
            <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Upload Complete!</h2>
            <p className="text-gray-600 mb-6">
              All {files.length} files have been successfully uploaded and protected.
            </p>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="text-sm text-green-800">
                <strong>Protection activated:</strong> Your content is now being monitored across selected platforms.
              </div>
            </div>

            <div className="flex space-x-4 justify-center">
              <button className="bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 transition-colors">
                View Dashboard
              </button>
              <button 
                onClick={() => {
                  setCurrentStep(0);
                  setFiles([]);
                }}
                className="bg-gray-600 text-white py-2 px-6 rounded-md hover:bg-gray-700 transition-colors"
              >
                Upload More
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      {currentStep < 3 && (
        <div className="flex justify-between mt-8">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className={`flex items-center px-6 py-2 rounded-md transition-colors ${
              currentStep === 0
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Previous
          </button>

          <button
            onClick={nextStep}
            disabled={currentStep === 0 && files.length === 0}
            className={`flex items-center px-6 py-2 rounded-md transition-colors ${
              (currentStep === 0 && files.length === 0)
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            Next
            <ArrowRightIcon className="h-5 w-5 ml-2" />
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadWizard;