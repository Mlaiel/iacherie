/**
 * Image Analysis Component - Interface pour analyser des photos médicales
 * Glisser-déposer ou prendre une photo directement
 */
import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Camera, 
  Upload, 
  X, 
  Loader2,
  AlertCircle,
  CheckCircle2,
  Image as ImageIcon,
  FileImage
} from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface ImageAnalysisProps {
  userId: string;
}

type AnalysisType = 'skin' | 'xray' | 'document';

export function ImageAnalysis({ userId }: ImageAnalysisProps) {
  const [selectedType, setSelectedType] = useState<AnalysisType>('skin');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);

  // Gérer le glisser-déposer
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelection(files[0]);
    }
  };

  // Gérer la sélection de fichier
  const handleFileSelection = (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Veuillez sélectionner une image');
      return;
    }

    setImageFile(file);
    
    // Créer aperçu
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
    
    setAnalysisResult(null);
  };

  // Ouvrir la caméra
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' } // Caméra arrière par défaut
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Impossible d\'accéder à la caméra. Vérifiez les permissions.');
    }
  };

  // Prendre une photo
  const capturePhoto = () => {
    if (!videoRef.current) return;

    const canvas = document.createElement('canvas');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(videoRef.current, 0, 0);
      
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
          handleFileSelection(file);
          stopCamera();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  // Arrêter la caméra
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraActive(false);
    }
  };

  // Analyser l'image
  const handleAnalyze = async () => {
    if (!imageFile) return;

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('analysis_type', selectedType);
      formData.append('patient_id', userId);

      const endpoint = selectedType === 'skin' 
        ? '/api/medcare/image-analysis/skin'
        : selectedType === 'xray'
        ? '/api/medcare/image-analysis/xray'
        : '/api/medcare/medical-documents/upload';

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setAnalysisResult(data);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Erreur lors de l\'analyse. Veuillez réessayer.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Recommencer
  const handleReset = () => {
    setImageFile(null);
    setImagePreview(null);
    setAnalysisResult(null);
    stopCamera();
  };

  return (
    <div className="space-y-6">
      {/* Sélection du type d'analyse */}
      <Card>
        <CardHeader>
          <CardTitle>Type d'analyse</CardTitle>
          <CardDescription>Choisissez le type d'image que vous souhaitez analyser</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedType} onValueChange={(v) => setSelectedType(v as AnalysisType)}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="skin">
                <Camera className="h-4 w-4 mr-2" />
                Peau
              </TabsTrigger>
              <TabsTrigger value="xray">
                <FileImage className="h-4 w-4 mr-2" />
                Radiographie
              </TabsTrigger>
              <TabsTrigger value="document">
                <ImageIcon className="h-4 w-4 mr-2" />
                Document
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </CardContent>
      </Card>

      {/* Zone de capture/upload */}
      {!imagePreview && !isCameraActive && (
        <Card>
          <CardHeader>
            <CardTitle>Ajouter une image</CardTitle>
            <CardDescription>
              {selectedType === 'skin' && 'Photographiez la zone concernée avec une bonne lumière'}
              {selectedType === 'xray' && 'Photographiez votre radiographie ou scanner'}
              {selectedType === 'document' && 'Photographiez votre document médical (analyse, ordonnance)'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Zone glisser-déposer */}
            <div
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium mb-2">Glissez votre image ici</p>
              <p className="text-sm text-gray-500 mb-4">ou</p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileSelection(e.target.files[0]);
                  }
                }}
              />
              <div className="flex gap-3 justify-center">
                <Button
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Choisir un fichier
                </Button>
                <Button
                  variant="default"
                  onClick={startCamera}
                >
                  <Camera className="h-4 w-4 mr-2" />
                  Prendre une photo
                </Button>
              </div>
            </div>

            {/* Conseils */}
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>Conseils pour une meilleure analyse:</strong>
                <ul className="mt-2 ml-4 list-disc text-sm space-y-1">
                  <li>Utilisez un éclairage naturel ou une lumière blanche</li>
                  <li>Évitez les ombres et les reflets</li>
                  <li>Cadrez bien la zone concernée</li>
                  <li>Assurez-vous que l'image soit nette (pas floue)</li>
                </ul>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Caméra active */}
      {isCameraActive && (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <div className="relative bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full h-auto"
              />
              
              {/* Grille de guidage */}
              <div className="absolute inset-0 pointer-events-none">
                <div className="w-full h-full grid grid-cols-3 grid-rows-3">
                  {[...Array(9)].map((_, i) => (
                    <div key={i} className="border border-white opacity-30" />
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button
                variant="default"
                size="lg"
                className="flex-1"
                onClick={capturePhoto}
              >
                <Camera className="h-5 w-5 mr-2" />
                Prendre la photo
              </Button>
              <Button
                variant="outline"
                size="lg"
                onClick={stopCamera}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Aperçu et analyse */}
      {imagePreview && !analysisResult && (
        <Card>
          <CardHeader>
            <CardTitle>Image sélectionnée</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-auto rounded-lg border"
              />
              <Button
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={handleReset}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Vérifiez que l'image est claire et bien cadrée avant l'analyse
              </AlertDescription>
            </Alert>

            <Button
              className="w-full"
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                <>
                  🤖 Analyser avec l'IA
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Résultats */}
      {analysisResult && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Résultats de l'analyse</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Image analysée */}
              <img
                src={imagePreview || ''}
                alt="Analyzed"
                className="w-full h-auto rounded-lg border"
              />

              {/* Résultat principal */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-blue-900">
                      {analysisResult.detected_condition || analysisResult.detected_finding || 'Analyse terminée'}
                    </h3>
                    {analysisResult.confidence && (
                      <p className="text-sm text-blue-700 mt-1">
                        Confiance: {Math.round(analysisResult.confidence * 100)}%
                      </p>
                    )}
                  </div>
                  <Badge 
                    variant={analysisResult.risk_level === 'high' ? 'destructive' : 'secondary'}
                  >
                    {analysisResult.risk_level?.toUpperCase() || 'INFO'}
                  </Badge>
                </div>
              </div>

              {/* Détails */}
              {analysisResult.description && (
                <div className="space-y-2">
                  <h4 className="font-medium">Description:</h4>
                  <p className="text-sm text-gray-700">{analysisResult.description}</p>
                </div>
              )}

              {/* Recommandations */}
              {analysisResult.recommendations && (
                <div className="space-y-2">
                  <h4 className="font-medium">Recommandations:</h4>
                  <ul className="space-y-2">
                    {analysisResult.recommendations.map((rec: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Qualité de l'image */}
              {analysisResult.image_quality && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-sm">
                    <strong>Qualité de l'image:</strong> {analysisResult.image_quality.assessment}
                    {analysisResult.image_quality.warnings && analysisResult.image_quality.warnings.length > 0 && (
                      <ul className="mt-1 ml-4 list-disc">
                        {analysisResult.image_quality.warnings.map((warning: string, i: number) => (
                          <li key={i}>{warning}</li>
                        ))}
                      </ul>
                    )}
                  </AlertDescription>
                </Alert>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <Button
                  variant="default"
                  className="flex-1"
                  onClick={() => {
                    // Demander consultation
                    window.location.href = '/medcare/consultation';
                  }}
                >
                  Consulter un médecin
                </Button>
                <Button
                  variant="outline"
                  onClick={handleReset}
                >
                  Nouvelle analyse
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Disclaimer */}
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              ⚕️ Cette analyse IA est fournie à titre informatif uniquement. Elle ne remplace pas un diagnostic médical professionnel. 
              Consultez toujours un médecin pour un avis définitif, surtout si vous avez des préoccupations concernant votre santé.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
