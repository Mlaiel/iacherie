import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, FileText, Link as LinkIcon, Video, Music, Loader2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export type ContentType = 'text' | 'url' | 'pdf' | 'video' | 'audio';
export type AcademicLevel = 'elementary' | 'high_school' | 'undergraduate' | 'graduate' | 'doctorate';

interface ContentUploadProps {
  onUpload: (content: ContentUploadData) => Promise<void>;
}

export interface ContentUploadData {
  title: string;
  content_type: ContentType;
  text?: string;
  file?: File;
  url?: string;
  subject?: string;
  academic_level?: AcademicLevel;
  language?: string;
}

export const ContentUpload: React.FC<ContentUploadProps> = ({ onUpload }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [formData, setFormData] = useState<ContentUploadData>({
    title: '',
    content_type: 'text',
    language: 'fr',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUploading(true);
    try {
      await onUpload(formData);
      // Reset form
      setFormData({
        title: '',
        content_type: 'text',
        language: 'fr',
      });
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFormData({ ...formData, file: e.target.files[0] });
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl">📤 Upload de Contenu Éducatif</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-lg">Titre *</Label>
            <Input
              id="title"
              placeholder="Ex: Cours de Photosynthèse"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              className="text-lg"
            />
          </div>

          {/* Subject & Level */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="subject">Matière</Label>
              <Input
                id="subject"
                placeholder="Ex: Biologie, Mathématiques"
                value={formData.subject || ''}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="academic-level">Niveau académique</Label>
              <Select
                value={formData.academic_level}
                onValueChange={(value: AcademicLevel) =>
                  setFormData({ ...formData, academic_level: value })
                }
              >
                <SelectTrigger id="academic-level">
                  <SelectValue placeholder="Sélectionner un niveau" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="elementary">Élémentaire</SelectItem>
                  <SelectItem value="high_school">Lycée</SelectItem>
                  <SelectItem value="undergraduate">Licence</SelectItem>
                  <SelectItem value="graduate">Master</SelectItem>
                  <SelectItem value="doctorate">Doctorat</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Language */}
          <div className="space-y-2">
            <Label htmlFor="language">Langue</Label>
            <Select
              value={formData.language}
              onValueChange={(value) => setFormData({ ...formData, language: value })}
            >
              <SelectTrigger id="language">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fr">Français</SelectItem>
                <SelectItem value="en">English</SelectItem>
                <SelectItem value="es">Español</SelectItem>
                <SelectItem value="de">Deutsch</SelectItem>
                <SelectItem value="ar">العربية</SelectItem>
                <SelectItem value="zh">中文</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Content Type Tabs */}
          <div className="space-y-2">
            <Label className="text-lg">Type de contenu *</Label>
            <Tabs
              value={formData.content_type}
              onValueChange={(value) =>
                setFormData({ ...formData, content_type: value as ContentType })
              }
            >
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="text">
                  <FileText className="w-4 h-4 mr-2" />
                  Texte
                </TabsTrigger>
                <TabsTrigger value="url">
                  <LinkIcon className="w-4 h-4 mr-2" />
                  URL
                </TabsTrigger>
                <TabsTrigger value="pdf">
                  <Upload className="w-4 h-4 mr-2" />
                  PDF
                </TabsTrigger>
                <TabsTrigger value="video">
                  <Video className="w-4 h-4 mr-2" />
                  Vidéo
                </TabsTrigger>
                <TabsTrigger value="audio">
                  <Music className="w-4 h-4 mr-2" />
                  Audio
                </TabsTrigger>
              </TabsList>

              <TabsContent value="text" className="mt-4">
                <Textarea
                  placeholder="Collez ou tapez votre texte ici..."
                  value={formData.text || ''}
                  onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                  className="min-h-[300px] text-base"
                  required
                />
                <p className="text-sm text-gray-500 mt-2">
                  Minimum 100 mots pour une analyse pertinente
                </p>
              </TabsContent>

              <TabsContent value="url" className="mt-4">
                <Input
                  type="url"
                  placeholder="https://exemple.com/article-educatif"
                  value={formData.url || ''}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  required
                />
                <p className="text-sm text-gray-500 mt-2">
                  Supporte: Articles web, vidéos YouTube, Wikipédia, etc.
                </p>
              </TabsContent>

              <TabsContent value="pdf" className="mt-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                  <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <Input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                    required
                  />
                  <Label htmlFor="file-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-700 font-medium">
                      Cliquez pour choisir un fichier
                    </span>
                    <span className="text-gray-600"> ou glissez-déposez</span>
                  </Label>
                  {formData.file && (
                    <p className="mt-2 text-sm text-gray-600">
                      Fichier sélectionné: {formData.file.name}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    PDF, DOC, DOCX, TXT (Max 50MB)
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="video" className="mt-4">
                <div className="space-y-4">
                  <Input
                    type="url"
                    placeholder="URL de la vidéo (YouTube, Vimeo, etc.)"
                    value={formData.url || ''}
                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  />
                  <p className="text-sm text-gray-500">Ou uploadez un fichier vidéo:</p>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                    <Video className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <Input
                      type="file"
                      accept="video/*"
                      onChange={handleFileChange}
                      className="hidden"
                      id="video-upload"
                    />
                    <Label htmlFor="video-upload" className="cursor-pointer">
                      <span className="text-blue-600 hover:text-blue-700 font-medium">
                        Choisir une vidéo
                      </span>
                    </Label>
                    {formData.file && (
                      <p className="mt-2 text-sm text-gray-600">{formData.file.name}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-2">MP4, AVI, MOV (Max 500MB)</p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="audio" className="mt-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <Music className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                  <Input
                    type="file"
                    accept="audio/*"
                    onChange={handleFileChange}
                    className="hidden"
                    id="audio-upload"
                    required
                  />
                  <Label htmlFor="audio-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-700 font-medium">
                      Choisir un fichier audio
                    </span>
                  </Label>
                  {formData.file && (
                    <p className="mt-2 text-sm text-gray-600">{formData.file.name}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">MP3, WAV, M4A (Max 200MB)</p>
                  <p className="text-sm text-gray-600 mt-4">
                    L'audio sera transcrit automatiquement
                  </p>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Submit Button */}
          <Button type="submit" size="lg" className="w-full" disabled={isUploading}>
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Traitement en cours...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Uploader et Analyser
              </>
            )}
          </Button>

          {isUploading && (
            <div className="text-center text-sm text-gray-600">
              <p>⏳ Traitement du contenu en cours...</p>
              <p className="mt-1">Extraction • Analyse IA • Génération de quiz</p>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
};
