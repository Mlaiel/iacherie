import React, { useState, useCallback } from 'react';
// import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
// import { Button } from '@/components/ui/button';
// import { Badge } from '@/components/ui/badge';
import { Upload, Music, Video, Image, FileText, Check, AlertTriangle } from 'lucide-react';

interface FingerprintResult {
  id: string;
  filename: string;
  type: 'audio' | 'video' | 'image' | 'text';
  fingerprint: string;
  confidence: number;
  status: 'processing' | 'completed' | 'error';
  timestamp: Date;
}

interface FingerprintingInterfaceProps {
  onFingerprintGenerated?: (result: FingerprintResult) => void;
}

const FingerprintingInterface: React.FC<FingerprintingInterfaceProps> = ({
  onFingerprintGenerated
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [results, setResults] = useState<FingerprintResult[]>([]);
  const [_isProcessing, setIsProcessing] = useState(false);

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'audio': return <Music className="w-5 h-5" />;
      case 'video': return <Video className="w-5 h-5" />;
      case 'image': return <Image className="w-5 h-5" />;
      case 'text': return <FileText className="w-5 h-5" />;
      default: return <Upload className="w-5 h-5" />;
    }
  };

  const getFileType = (filename: string): FingerprintResult['type'] => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (['mp3', 'wav', 'flac', 'aac'].includes(ext || '')) return 'audio';
    if (['mp4', 'avi', 'mov', 'mkv'].includes(ext || '')) return 'video';
    if (['jpg', 'jpeg', 'png', 'gif'].includes(ext || '')) return 'image';
    return 'text';
  };

  const simulateFingerprinting = async (file: File): Promise<FingerprintResult> => {
    const result: FingerprintResult = {
      id: Math.random().toString(36).substr(2, 9),
      filename: file.name,
      type: getFileType(file.name),
      fingerprint: '',
      confidence: 0,
      status: 'processing',
      timestamp: new Date()
    };

    setResults(prev => [...prev, result]);

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));

    const finalResult: FingerprintResult = {
      ...result,
      fingerprint: `fp_${Math.random().toString(36).substr(2, 16)}`,
      confidence: 85 + Math.random() * 15,
      status: 'completed'
    };

    setResults(prev => prev.map(r => r.id === result.id ? finalResult : r));
    onFingerprintGenerated?.(finalResult);

    return finalResult;
  };

  const handleFileUpload = useCallback(async (files: FileList) => {
    setIsProcessing(true);
    
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
      await simulateFingerprinting(file);
    }
    
    setIsProcessing(false);
  }, [onFingerprintGenerated]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files);
    }
  }, [handleFileUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      handleFileUpload(files);
    }
  }, [handleFileUpload]);

  const getStatusColor = (status: FingerprintResult['status']) => {
    switch (status) {
      case 'processing': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: FingerprintResult['status']) => {
    switch (status) {
      case 'completed': return <Check className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Content Fingerprinting
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/25 hover:border-primary/50'
            }`}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
          >
            <Upload className={`mx-auto mb-4 w-12 h-12 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
            <h3 className="text-lg font-semibold mb-2">
              {isDragging ? 'Drop files here' : 'Upload Content for Fingerprinting'}
            </h3>
            <p className="text-muted-foreground mb-4">
              Drag and drop files or click to select. Supports audio, video, images, and text.
            </p>
            
            <input
              type="file"
              multiple
              accept="audio/*,video/*,image/*,.txt,.pdf,.doc,.docx"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <Button asChild>
              <label htmlFor="file-upload" className="cursor-pointer">
                Select Files
              </label>
            </Button>
          </div>

          {results.length > 0 && (
            <div className="mt-6">
              <h4 className="font-semibold mb-4">Fingerprinting Results</h4>
              <div className="space-y-3">
                {results.map((result) => (
                  <div key={result.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getFileIcon(result.type)}
                      <div>
                        <p className="font-medium">{result.filename}</p>
                        <p className="text-sm text-muted-foreground">
                          {result.type.charAt(0).toUpperCase() + result.type.slice(1)} • {result.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      {result.status === 'processing' && (
                        <div className="flex items-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                          <span className="text-sm">Processing...</span>
                        </div>
                      )}
                      
                      {result.status === 'completed' && (
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">
                            {result.confidence.toFixed(1)}% confidence
                          </Badge>
                          <span className="text-sm font-mono text-muted-foreground">
                            {result.fingerprint}
                          </span>
                        </div>
                      )}
                      
                      <Badge className={getStatusColor(result.status)}>
                        <span className="flex items-center gap-1">
                          {getStatusIcon(result.status)}
                          {result.status}
                        </span>
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default FingerprintingInterface;