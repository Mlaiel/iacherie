/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Plus, MapPin, Camera, Heart, Dog } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { useGeolocation, formatDistance } from '@/lib/geolocation';
import { CaseReport, Location } from '@/lib/types';
import { useKV } from '@/hooks/useKV';
import { VoiceControls } from './VoiceControls';
import { useTranslation } from '@/hooks/useTranslation';
import { FileUpload } from './FileUpload';

interface ReportCaseProps {
  onReportSubmitted: (report: CaseReport) => void;
}

export function ReportCase({ onReportSubmitted }: ReportCaseProps) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [type, setType] = useState<'homeless' | 'animal'>('homeless');
  const [description, setDescription] = useState('');
  const [urgency, setUrgency] = useState<'low' | 'medium' | 'high'>('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [cases, setCases] = useKV<CaseReport[]>('solidarity-cases', []);
  
  const { location, error, loading, getCurrentLocation } = useGeolocation();

  const handleFileUpload = (urls: string[]) => {
    setUploadedFiles((prev) => [...prev, ...urls]);
    toast.success(`${urls.length} fichier(s) téléchargé(s)`);
  };

  const handleSubmit = async () => {
    if (!description.trim()) {
      toast.error(t('report.placeholders.person'));
      return;
    }

    setIsSubmitting(true);
    
    try {
      let reportLocation = location;
      if (!reportLocation) {
        reportLocation = await getCurrentLocation();
      }

      const newReport: CaseReport = {
        id: `case-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type,
        location: reportLocation,
        description: description.trim(),
        urgency,
        status: 'open',
        reportedAt: new Date().toISOString(),
        tags: [],
        media: uploadedFiles.length > 0 ? uploadedFiles : undefined,
      };

      // Add to persistent storage
      setCases((currentCases) => [...(currentCases || []), newReport]);
      
      onReportSubmitted(newReport);
      
      // Reset form
      setDescription('');
      setUrgency('medium');
      setUploadedFiles([]);
      setIsOpen(false);
      
      toast.success(t(type === 'homeless' ? 'report.success.person' : 'report.success.animal'));
    } catch (err) {
      toast.error(t('common.error'));
      console.error('Report submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          size="default" 
          className="bg-primary hover:bg-primary/90 text-primary-foreground font-medium px-3 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap"
          aria-label={t('report.title')}
        >
          <Plus className="w-4 h-4" weight="bold" />
          <span className="hidden sm:inline">{t('report.buttonText')}</span>
          <span className="sm:hidden">{t('report.buttonTextShort')}</span>
        </Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto" aria-describedby="report-dialog-description">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Heart className="text-primary" weight="fill" />
            {t('report.title')}
          </DialogTitle>
          <p id="report-dialog-description" className="text-sm text-muted-foreground">
            {t('report.subtitle')}
          </p>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          {/* Location Status */}
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2">
              <MapPin className="text-primary" />
              <span className="text-sm font-medium">
                {loading ? t('report.location.getting') : location ? t('report.location.ready') : t('report.location.needed')}
              </span>
            </div>
            {!location && !loading && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={getCurrentLocation}
                disabled={loading}
              >
                {t('report.location.getLocation')}
              </Button>
            )}
          </div>

          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-lg">
              {error}
            </div>
          )}
          
          {/* Case Type */}
          <div className="space-y-2">
            <Label htmlFor="case-type">{t('report.whoNeedsHelp')}</Label>
            <Select value={type} onValueChange={(value: 'homeless' | 'animal') => setType(value)}>
              <SelectTrigger id="case-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="homeless">{t('report.personHomeless')}</SelectItem>
                <SelectItem value="animal">{t('report.strayAnimal')}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Description */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="description">{t('report.whatKindOfHelp')}</Label>
              <VoiceControls 
                onVoiceInput={(text) => setDescription(text)}
                disabled={isSubmitting}
              />
            </div>
            <Textarea
              id="description"
              placeholder={type === 'homeless' 
                ? t('report.placeholders.person')
                : t('report.placeholders.animal')
              }
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[80px]"
              maxLength={500}
            />
            <div className="text-xs text-muted-foreground text-right">
              {description.length}/500 characters
            </div>
          </div>
          
          {/* File Upload */}
          <div className="space-y-2">
            <Label>{t('report.attachMedia')}</Label>
            <FileUpload
              accept="image/jpeg,image/png,image/webp,video/mp4,video/webm"
              maxSize={10}
              onUploadComplete={handleFileUpload}
            />
            {uploadedFiles.length > 0 && (
              <p className="text-xs text-green-600">
                {uploadedFiles.length} fichier(s) attaché(s)
              </p>
            )}
          </div>

          {/* Urgency */}
          <div className="space-y-2">
            <Label htmlFor="urgency">{t('report.urgencyLevel')}</Label>
            <Select value={urgency} onValueChange={(value: 'low' | 'medium' | 'high') => setUrgency(value)}>
              <SelectTrigger id="urgency">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="w-2 h-2 p-0"></Badge>
                    <span>{t('report.urgencyDesc.low')}</span>
                  </div>
                </SelectItem>
                <SelectItem value="medium">
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="w-2 h-2 p-0 bg-yellow-500"></Badge>
                    <span>{t('report.urgencyDesc.medium')}</span>
                  </div>
                </SelectItem>
                <SelectItem value="high">
                  <div className="flex items-center gap-2">
                    <Badge variant="destructive" className="w-2 h-2 p-0"></Badge>
                    <span>{t('report.urgencyDesc.high')}</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Submit Button */}
          <Button 
            onClick={handleSubmit} 
            disabled={isSubmitting || !description.trim() || (!location && !loading)}
            className="w-full mt-6"
            size="lg"
          >
            {isSubmitting ? t('common.loading') : t('common.submit')}
          </Button>
          
          <p className="text-xs text-muted-foreground text-center">
            {t('report.disclaimer')}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}