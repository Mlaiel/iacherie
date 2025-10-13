/**
 * Consultation History - Historique des consultations passées
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Calendar, 
  Clock, 
  User, 
  FileText,
  Download,
  Eye,
  Loader2 
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface ConsultationHistoryProps {
  userId: string;
}

export function ConsultationHistory({ userId }: ConsultationHistoryProps) {
  const [consultations, setConsultations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedConsultation, setSelectedConsultation] = useState<any>(null);

  useEffect(() => {
    fetchConsultations();
  }, [userId]);

  const fetchConsultations = async () => {
    try {
      const response = await fetch(`/api/medcare/consultations/history/${userId}`);
      const data = await response.json();
      setConsultations(data.consultations || []);
    } catch (error) {
      console.error('Error fetching consultations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (consultations.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune consultation
          </h3>
          <p className="text-gray-600">
            Vous n'avez pas encore de consultations enregistrées
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {consultations.map((consultation) => (
        <Card key={consultation.id} className="hover:shadow-lg transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1 space-y-3">
                {/* En-tête */}
                <div className="flex items-center gap-4">
                  <div className="bg-blue-100 p-2 rounded-lg">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">
                      Dr. {consultation.doctor_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {consultation.specialty}
                    </p>
                  </div>
                  <Badge 
                    variant={
                      consultation.status === 'completed' ? 'default' :
                      consultation.status === 'in_progress' ? 'secondary' :
                      'outline'
                    }
                  >
                    {consultation.status === 'completed' ? 'Terminée' :
                     consultation.status === 'in_progress' ? 'En cours' :
                     'Annulée'}
                  </Badge>
                </div>

                {/* Détails */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="h-4 w-4" />
                    <span>
                      {format(new Date(consultation.date), 'dd MMMM yyyy', { locale: fr })}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="h-4 w-4" />
                    <span>Durée: {consultation.duration || 15} min</span>
                  </div>
                </div>

                {/* Motif */}
                {consultation.reason && (
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    <strong>Motif:</strong> {consultation.reason}
                  </p>
                )}

                {/* Diagnostic */}
                {consultation.diagnosis && (
                  <p className="text-sm text-gray-700">
                    <strong>Diagnostic:</strong> {consultation.diagnosis}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2 ml-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedConsultation(consultation)}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  Détails
                </Button>
                {consultation.prescription_id && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      window.open(`/api/medcare/prescriptions/${consultation.prescription_id}/pdf`, '_blank');
                    }}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Ordonnance
                  </Button>
                )}
                {consultation.medical_report && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      window.open(consultation.medical_report, '_blank');
                    }}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Rapport
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Modal détails (simplifié) */}
      {selectedConsultation && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedConsultation(null)}
        >
          <Card 
            className="max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <CardTitle>Détails de la consultation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Informations générales</h4>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <dt className="text-gray-600">Médecin:</dt>
                  <dd className="font-medium">Dr. {selectedConsultation.doctor_name}</dd>
                  <dt className="text-gray-600">Date:</dt>
                  <dd>{format(new Date(selectedConsultation.date), 'PPP', { locale: fr })}</dd>
                  <dt className="text-gray-600">Durée:</dt>
                  <dd>{selectedConsultation.duration} minutes</dd>
                </dl>
              </div>

              {selectedConsultation.symptoms && (
                <div>
                  <h4 className="font-semibold mb-2">Symptômes rapportés</h4>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">
                    {selectedConsultation.symptoms}
                  </p>
                </div>
              )}

              {selectedConsultation.diagnosis && (
                <div>
                  <h4 className="font-semibold mb-2">Diagnostic</h4>
                  <p className="text-sm text-gray-700">{selectedConsultation.diagnosis}</p>
                </div>
              )}

              {selectedConsultation.treatment && (
                <div>
                  <h4 className="font-semibold mb-2">Traitement prescrit</h4>
                  <p className="text-sm text-gray-700">{selectedConsultation.treatment}</p>
                </div>
              )}

              {selectedConsultation.notes && (
                <div>
                  <h4 className="font-semibold mb-2">Notes du médecin</h4>
                  <p className="text-sm text-gray-700 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                    {selectedConsultation.notes}
                  </p>
                </div>
              )}

              <Button 
                onClick={() => setSelectedConsultation(null)}
                className="w-full"
              >
                Fermer
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
