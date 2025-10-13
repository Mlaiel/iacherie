/**
 * Composant d'upload de fichiers avec drag & drop
 * Support: Images, Vidéos, Documents
 */
import React, { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  X, 
  Image as ImageIcon, 
  Video, 
  File, 
  Check,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface FileUploadProps {
  accept?: string;
  maxSize?: number; // en MB
  maxFiles?: number;
  onUploadComplete?: (urls: string[]) => void;
  onError?: (error: string) => void;
}

interface UploadedFile {
  id: string;
  file: File;
  preview?: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  url?: string;
  error?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  accept = 'image/*,video/*',
  maxSize = 10, // 10MB par défaut
  maxFiles = 5,
  onUploadComplete,
  onError
}) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Valider un fichier
  const validateFile = (file: File): string | null => {
    // Taille
    if (file.size > maxSize * 1024 * 1024) {
      return `Le fichier ${file.name} dépasse ${maxSize}MB`;
    }

    // Type
    const acceptedTypes = accept.split(',').map(t => t.trim());
    const fileType = file.type;
    const isAccepted = acceptedTypes.some(type => {
      if (type.endsWith('/*')) {
        return fileType.startsWith(type.replace('/*', ''));
      }
      return fileType === type;
    });

    if (!isAccepted) {
      return `Le type de fichier ${file.type} n'est pas accepté`;
    }

    return null;
  };

  // Créer une prévisualisation
  const createPreview = (file: File): Promise<string | undefined> => {
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.onerror = () => resolve(undefined);
        reader.readAsDataURL(file);
      } else {
        resolve(undefined);
      }
    });
  };

  // Compresser une image
  const compressImage = async (file: File): Promise<File> => {
    if (!file.type.startsWith('image/')) return file;

    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          let width = img.width;
          let height = img.height;

          // Redimensionner si trop grand
          const maxDimension = 1920;
          if (width > maxDimension || height > maxDimension) {
            if (width > height) {
              height = (height / width) * maxDimension;
              width = maxDimension;
            } else {
              width = (width / height) * maxDimension;
              height = maxDimension;
            }
          }

          canvas.width = width;
          canvas.height = height;

          const ctx = canvas.getContext('2d');
          ctx?.drawImage(img, 0, 0, width, height);

          canvas.toBlob(
            (blob) => {
              if (blob) {
                // Workaround pour TypeScript - utiliser Object.assign pour créer un File
                const fileProps = { name: file.name, lastModified: Date.now(), type: 'image/jpeg' };
                const compressedFile = Object.assign(blob, fileProps) as File;
                resolve(compressedFile);
              } else {
                resolve(file);
              }
            },
            'image/jpeg',
            0.8
          );
        };
        img.src = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    });
  };

  // Upload un fichier vers le backend
  const uploadFile = async (uploadedFile: UploadedFile) => {
    try {
      // Compresser si c'est une image
      let fileToUpload = uploadedFile.file;
      if (uploadedFile.file.type.startsWith('image/')) {
        fileToUpload = await compressImage(uploadedFile.file);
      }

      const formData = new FormData();
      formData.append('file', fileToUpload);

      // Simuler l'upload avec progress
      const xhr = new XMLHttpRequest();

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadedFile.id
                ? { ...f, progress, status: 'uploading' }
                : f
            )
          );
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200 || xhr.status === 201) {
          const response = JSON.parse(xhr.responseText);
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadedFile.id
                ? { ...f, progress: 100, status: 'success', url: response.url }
                : f
            )
          );
        } else {
          throw new Error('Upload failed');
        }
      };

      xhr.onerror = () => {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadedFile.id
              ? { ...f, status: 'error', error: 'Erreur réseau' }
              : f
          )
        );
      };

      xhr.open('POST', '/api/v1/ia2good/media/upload');
      xhr.send(formData);
    } catch (error) {
      setFiles((prev) =>
        prev.map((f) =>
          f.id === uploadedFile.id
            ? { ...f, status: 'error', error: 'Erreur d\'upload' }
            : f
        )
      );
    }
  };

  // Ajouter des fichiers
  const handleFiles = useCallback(async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;

    const newFiles: UploadedFile[] = [];

    for (let i = 0; i < fileList.length && newFiles.length < maxFiles; i++) {
      const file = fileList[i];
      const error = validateFile(file);

      if (error) {
        onError?.(error);
        continue;
      }

      const preview = await createPreview(file);

      const uploadedFile: UploadedFile = {
        id: `${Date.now()}-${i}`,
        file,
        preview,
        progress: 0,
        status: 'pending',
      };

      newFiles.push(uploadedFile);
    }

    if (files.length + newFiles.length > maxFiles) {
      onError?.(`Maximum ${maxFiles} fichiers autorisés`);
      return;
    }

    setFiles((prev) => [...prev, ...newFiles]);

    // Commencer l'upload automatiquement
    newFiles.forEach((file) => uploadFile(file));
  }, [files.length, maxFiles]);

  // Drag & Drop
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  }, [handleFiles]);

  // Supprimer un fichier
  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  // Retry upload
  const retryUpload = (file: UploadedFile) => {
    setFiles((prev) =>
      prev.map((f) =>
        f.id === file.id ? { ...f, status: 'pending', progress: 0, error: undefined } : f
      )
    );
    uploadFile(file);
  };

  // Get file icon
  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return <ImageIcon className="h-6 w-6" />;
    if (file.type.startsWith('video/')) return <Video className="h-6 w-6" />;
    return <File className="h-6 w-6" />;
  };

  return (
    <div className="space-y-4">
      {/* Zone de drop */}
      <Card
        className={`border-2 border-dashed transition-colors ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-muted-foreground/25 hover:border-primary/50'
        }`}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Upload className={`h-12 w-12 mb-4 ${isDragging ? 'text-primary' : 'text-muted-foreground'}`} />
          <h3 className="text-lg font-semibold mb-2">
            {isDragging ? 'Déposez vos fichiers ici' : 'Glissez-déposez vos fichiers'}
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            ou cliquez pour sélectionner
          </p>
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="h-4 w-4 mr-2" />
            Choisir des fichiers
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            multiple
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          <p className="text-xs text-muted-foreground mt-4">
            Max {maxFiles} fichiers, {maxSize}MB chacun
          </p>
        </CardContent>
      </Card>

      {/* Liste des fichiers */}
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file) => (
            <Card key={file.id}>
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  {/* Prévisualisation */}
                  <div className="flex-shrink-0">
                    {file.preview ? (
                      <img
                        src={file.preview}
                        alt={file.file.name}
                        className="w-16 h-16 object-cover rounded"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-muted rounded flex items-center justify-center">
                        {getFileIcon(file.file)}
                      </div>
                    )}
                  </div>

                  {/* Infos */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {file.file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {(file.file.size / 1024 / 1024).toFixed(2)} MB
                    </p>

                    {/* Progress bar */}
                    {(file.status === 'uploading' || file.status === 'pending') && (
                      <Progress value={file.progress} className="mt-2" />
                    )}

                    {/* Error */}
                    {file.status === 'error' && (
                      <Alert variant="destructive" className="mt-2">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{file.error}</AlertDescription>
                      </Alert>
                    )}
                  </div>

                  {/* Status */}
                  <div className="flex-shrink-0 flex items-center gap-2">
                    {file.status === 'uploading' && (
                      <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    )}
                    {file.status === 'success' && (
                      <Check className="h-5 w-5 text-green-600" />
                    )}
                    {file.status === 'error' && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => retryUpload(file)}
                      >
                        Réessayer
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeFile(file.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
