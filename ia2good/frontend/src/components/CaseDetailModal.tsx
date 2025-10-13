/**
 * Modal détaillé pour un cas avec chat intégré
 */
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import {
  MapPin,
  Clock,
  User,
  Heart,
  ChatCircle,
  Info,
  Images,
} from '@phosphor-icons/react';
import { CaseReport } from '@/lib/types';
import { ChatInterface } from './ChatInterface';
import { format } from 'date-fns';

interface CaseDetailModalProps {
  case: CaseReport | null;
  isOpen: boolean;
  onClose: () => void;
  currentUserId: string;
  currentUserName: string;
  onTakeAction?: (caseId: string) => void;
}

export const CaseDetailModal: React.FC<CaseDetailModalProps> = ({
  case: selectedCase,
  isOpen,
  onClose,
  currentUserId,
  currentUserName,
  onTakeAction,
}) => {
  if (!selectedCase) return null;

  const getUrgencyColor = (urgency: string) => {
    const colors = {
      critical: 'destructive',
      high: 'destructive',
      medium: 'default',
      low: 'secondary',
    };
    return colors[urgency as keyof typeof colors] || 'secondary';
  };

  const getStatusColor = (status: string) => {
    const colors = {
      open: 'destructive',
      'in-progress': 'default',
      helped: 'secondary',
      closed: 'outline',
    };
    return colors[status as keyof typeof colors] || 'outline';
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      open: 'Ouvert',
      'in-progress': 'En cours',
      helped: 'Aidé',
      closed: 'Fermé',
    };
    return labels[status as keyof typeof labels] || status;
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <DialogTitle className="text-xl mb-2">
                Cas #{selectedCase.id.substring(0, 8)}
              </DialogTitle>
              <DialogDescription>{selectedCase.description}</DialogDescription>
            </div>
            <div className="flex flex-col gap-2">
              <Badge variant={getUrgencyColor(selectedCase.urgency) as any}>
                {selectedCase.urgency}
              </Badge>
              <Badge variant={getStatusColor(selectedCase.status) as any}>
                {getStatusLabel(selectedCase.status)}
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="details" className="flex items-center gap-2">
              <Info className="w-4 h-4" />
              Détails
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <ChatCircle className="w-4 h-4" />
              Discussion
            </TabsTrigger>
            <TabsTrigger value="media" className="flex items-center gap-2">
              <Images className="w-4 h-4" />
              Médias
            </TabsTrigger>
          </TabsList>

          {/* Onglet Détails */}
          <TabsContent value="details" className="space-y-4">
            <Card>
              <CardContent className="pt-6 space-y-4">
                {/* Type de cas */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-600 mb-2">Type de cas</h4>
                  <Badge variant="outline">{selectedCase.type}</Badge>
                </div>

                {/* Localisation */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    Localisation
                  </h4>
                  <p className="text-sm">
                    Lat: {selectedCase.location.lat.toFixed(6)}, Lng:{' '}
                    {selectedCase.location.lng.toFixed(6)}
                  </p>
                  {selectedCase.address && (
                    <p className="text-sm text-gray-600 mt-1">{selectedCase.address}</p>
                  )}
                </div>

                {/* Date */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Date de signalement
                  </h4>
                  <p className="text-sm">
                    {format(new Date(selectedCase.reportedAt), 'dd/MM/yyyy à HH:mm')}
                  </p>
                </div>

                {/* Volontaire assigné */}
                {selectedCase.volunteerId && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-600 mb-2 flex items-center gap-2">
                      <User className="w-4 h-4" />
                      Volontaire assigné
                    </h4>
                    <p className="text-sm">{selectedCase.volunteerId}</p>
                  </div>
                )}

                {/* Tags */}
                {selectedCase.tags && selectedCase.tags.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-600 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedCase.tags.map((tag, idx) => (
                        <Badge key={idx} variant="secondary">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                {selectedCase.status === 'open' && onTakeAction && (
                  <div className="pt-4 border-t">
                    <Button
                      onClick={() => onTakeAction(selectedCase.id)}
                      className="w-full"
                      size="lg"
                    >
                      <Heart className="w-5 h-5 mr-2" />
                      Proposer mon aide
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Chat */}
          <TabsContent value="chat" className="space-y-4">
            <Card>
              <CardContent className="p-0">
                <div className="h-[500px]">
                  <ChatInterface
                    caseId={selectedCase.id}
                    currentUserId={currentUserId}
                    currentUserName={currentUserName}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Onglet Médias */}
          <TabsContent value="media" className="space-y-4">
            <Card>
              <CardContent className="pt-6">
                {selectedCase.media && selectedCase.media.length > 0 ? (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {selectedCase.media.map((url, idx) => (
                      <div key={idx} className="relative aspect-square rounded-lg overflow-hidden">
                        <img
                          src={url}
                          alt={`Media ${idx + 1}`}
                          className="w-full h-full object-cover hover:scale-105 transition-transform cursor-pointer"
                          onClick={() => window.open(url, '_blank')}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Images className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Aucun média attaché à ce cas</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default CaseDetailModal;
