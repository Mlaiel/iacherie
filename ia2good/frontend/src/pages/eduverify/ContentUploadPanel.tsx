/**
 * Content Upload Panel - Interface d'upload multi-format
 * Drag & Drop + Formulaire avec prévisualisation
 */
import React, { useState, useCallback } from 'react';
import { Upload, File, X, CheckCircle, AlertCircle, Loader2, FileText, Video, Music, Link as LinkIcon } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface UploadedContent {
  id: string;
  title: string;
  content_type: string;
  status: string;
  created_at: string;
}

const ContentUploadPanel: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<'file' | 'text' | 'url'>('file');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState<UploadedContent | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form data
  const [formData, setFormData] = useState({
    title: '',
    content_type: 'text',
    text: '',
    url: '',
    subject: '',
    topic: '',
    language: 'fr',
    dialect: ''
  });

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    setError(null);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const extension = droppedFile.name.split('.').pop()?.toLowerCase();
      
      // Validate file type
      const validExtensions = ['pdf', 'docx', 'txt', 'mp3', 'wav', 'ogg', 'mp4', 'avi', 'mov'];
      if (extension && validExtensions.includes(extension)) {
        setFile(droppedFile);
        setFormData(prev => ({
          ...prev,
          title: prev.title || droppedFile.name,
          content_type: getContentType(extension)
        }));
      } else {
        setError(`Type de fichier non supporté. Extensions valides: ${validExtensions.join(', ')}`);
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      const extension = selectedFile.name.split('.').pop()?.toLowerCase();
      setFormData(prev => ({
        ...prev,
        title: prev.title || selectedFile.name,
        content_type: extension ? getContentType(extension) : 'text'
      }));
    }
  };

  const getContentType = (extension: string): string => {
    if (['pdf', 'docx', 'txt'].includes(extension)) return 'pdf';
    if (['mp3', 'wav', 'ogg'].includes(extension)) return 'audio';
    if (['mp4', 'avi', 'mov'].includes(extension)) return 'video';
    return 'text';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setUploadSuccess(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('content_type', formData.content_type);
      formDataToSend.append('language', formData.language);
      
      if (formData.subject) formDataToSend.append('subject', formData.subject);
      if (formData.topic) formDataToSend.append('topic', formData.topic);
      if (formData.dialect) formDataToSend.append('dialect', formData.dialect);

      if (uploadMode === 'file' && file) {
        formDataToSend.append('file', file);
      } else if (uploadMode === 'text') {
        formDataToSend.append('text', formData.text);
      } else if (uploadMode === 'url') {
        formDataToSend.append('url', formData.url);
      }

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await fetch('http://localhost:8002/eduverify/content/upload', {
        method: 'POST',
        body: formDataToSend,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result = await response.json();
      setUploadSuccess(result);
      
      // Reset form
      setFile(null);
      setFormData({
        title: '',
        content_type: 'text',
        text: '',
        url: '',
        subject: '',
        topic: '',
        language: 'fr',
        dialect: ''
      });

      setTimeout(() => setUploadSuccess(null), 5000);
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de l\'upload');
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-6 w-6 text-blue-600" />
            <span>Upload de Contenu Éducatif</span>
          </CardTitle>
          <CardDescription>
            Formats supportés: PDF, DOCX, TXT, MP3, WAV, MP4, AVI, URLs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Upload Mode Selection */}
            <div className="flex space-x-2">
              <Button
                type="button"
                variant={uploadMode === 'file' ? 'default' : 'outline'}
                onClick={() => setUploadMode('file')}
                className="flex-1"
              >
                <File className="h-4 w-4 mr-2" />
                Fichier
              </Button>
              <Button
                type="button"
                variant={uploadMode === 'text' ? 'default' : 'outline'}
                onClick={() => setUploadMode('text')}
                className="flex-1"
              >
                <FileText className="h-4 w-4 mr-2" />
                Texte
              </Button>
              <Button
                type="button"
                variant={uploadMode === 'url' ? 'default' : 'outline'}
                onClick={() => setUploadMode('url')}
                className="flex-1"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                URL
              </Button>
            </div>

            {/* File Upload Area */}
            {uploadMode === 'file' && (
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-700 hover:border-gray-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.txt,.mp3,.wav,.ogg,.mp4,.avi,.mov"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  {file ? (
                    <div className="flex items-center justify-center space-x-4">
                      {formData.content_type === 'video' ? <Video className="h-12 w-12 text-blue-600" /> :
                       formData.content_type === 'audio' ? <Music className="h-12 w-12 text-purple-600" /> :
                       <FileText className="h-12 w-12 text-green-600" />}
                      <div className="text-left">
                        <p className="font-semibold text-gray-900 dark:text-white">{file.name}</p>
                        <p className="text-sm text-gray-600">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.preventDefault();
                          setFile(null);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                        Glissez-déposez votre fichier ici
                      </p>
                      <p className="text-sm text-gray-600 mb-4">
                        ou cliquez pour sélectionner
                      </p>
                      <Badge variant="outline">Max 50 MB</Badge>
                    </>
                  )}
                </label>
              </div>
            )}

            {/* Text Input */}
            {uploadMode === 'text' && (
              <div className="space-y-2">
                <Label htmlFor="text-content">Contenu Texte</Label>
                <Textarea
                  id="text-content"
                  placeholder="Entrez votre contenu éducatif ici..."
                  value={formData.text}
                  onChange={(e) => setFormData(prev => ({ ...prev, text: e.target.value }))}
                  rows={10}
                  className="font-mono"
                  required={uploadMode === 'text'}
                />
              </div>
            )}

            {/* URL Input */}
            {uploadMode === 'url' && (
              <div className="space-y-2">
                <Label htmlFor="url-input">URL du Contenu</Label>
                <Input
                  id="url-input"
                  type="url"
                  placeholder="https://example.com/article"
                  value={formData.url}
                  onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                  required={uploadMode === 'url'}
                />
                <p className="text-sm text-gray-600">Le contenu sera extrait automatiquement</p>
              </div>
            )}

            {/* Metadata Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Titre *</Label>
                <Input
                  id="title"
                  placeholder="Titre du contenu"
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="content-type">Type de Contenu</Label>
                <Select
                  value={formData.content_type}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, content_type: value }))}
                >
                  <SelectTrigger id="content-type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="text">Texte</SelectItem>
                    <SelectItem value="pdf">PDF</SelectItem>
                    <SelectItem value="video">Vidéo</SelectItem>
                    <SelectItem value="audio">Audio</SelectItem>
                    <SelectItem value="url">URL</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Matière</Label>
                <Input
                  id="subject"
                  placeholder="ex: Mathématiques, Histoire..."
                  value={formData.subject}
                  onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="topic">Sujet</Label>
                <Input
                  id="topic"
                  placeholder="ex: Algèbre, Révolution française..."
                  value={formData.topic}
                  onChange={(e) => setFormData(prev => ({ ...prev, topic: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="language">Langue</Label>
                <Select
                  value={formData.language}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, language: value }))}
                >
                  <SelectTrigger id="language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fr">Français</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="es">Español</SelectItem>
                    <SelectItem value="ar">العربية</SelectItem>
                    <SelectItem value="de">Deutsch</SelectItem>
                    <SelectItem value="zh">中文</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="dialect">Dialecte (optionnel)</Label>
                <Input
                  id="dialect"
                  placeholder="ex: Tunisien, Québécois..."
                  value={formData.dialect}
                  onChange={(e) => setFormData(prev => ({ ...prev, dialect: e.target.value }))}
                />
              </div>
            </div>

            {/* Upload Progress */}
            {isUploading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Upload en cours...</span>
                  <span className="font-semibold">{uploadProgress}%</span>
                </div>
                <Progress value={uploadProgress} className="h-2" />
              </div>
            )}

            {/* Success Alert */}
            {uploadSuccess && (
              <Alert className="bg-green-50 border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  <span className="font-semibold">Succès!</span> Contenu "{uploadSuccess.title}" uploadé avec l'ID: {uploadSuccess.id}
                </AlertDescription>
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full"
              disabled={isUploading || (!file && !formData.text && !formData.url) || !formData.title}
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Upload en cours...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Uploader le Contenu
                </>
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900 dark:text-blue-100 text-lg">
            📚 Formats Supportés
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="font-semibold">Documents</p>
              <p>PDF, DOCX, TXT</p>
            </div>
            <div>
              <p className="font-semibold">Audio</p>
              <p>MP3, WAV, OGG</p>
            </div>
            <div>
              <p className="font-semibold">Vidéo</p>
              <p>MP4, AVI, MOV</p>
            </div>
            <div>
              <p className="font-semibold">Web</p>
              <p>URL (extraction auto)</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ContentUploadPanel;
