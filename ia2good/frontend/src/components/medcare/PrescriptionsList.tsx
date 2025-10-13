/**
 * Prescriptions List - Liste des ordonnances
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Download, 
  QrCode,
  Calendar,
  Pill,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

interface PrescriptionsListProps {
  userId: string;
}

export function PrescriptionsList({ userId }: PrescriptionsListProps) {
  const [prescriptions, setPrescriptions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedPrescription, setSelectedPrescription] = useState<any>(null);

  useEffect(() => {
    fetchPrescriptions();
  }, [userId]);

  const fetchPrescriptions = async () => {
    try {
      const response = await fetch(`/api/medcare/prescriptions/patient/${userId}`);
      const data = await response.json();
      setPrescriptions(data.prescriptions || []);
    } catch (error) {
      console.error('Error fetching prescriptions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadPDF = (prescriptionId: string) => {
    window.open(`/api/medcare/prescriptions/${prescriptionId}/pdf`, '_blank');
  };

  const showQRCode = (prescription: any) => {
    setSelectedPrescription(prescription);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (prescriptions.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Aucune ordonnance
          </h3>
          <p className="text-gray-600">
            Vous n'avez pas encore d'ordonnances enregistrées
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {prescriptions.map((prescription) => (
        <Card key={prescription.id} className="hover:shadow-lg transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1 space-y-3">
                {/* En-tête */}
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 p-2 rounded-lg">
                    <Pill className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">
                      Ordonnance #{prescription.id.slice(0, 8)}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Dr. {prescription.doctor_name}
                    </p>
                  </div>
                  <Badge 
                    variant={
                      prescription.status === 'active' ? 'default' :
                      prescription.status === 'expired' ? 'secondary' :
                      'outline'
                    }
                  >
                    {prescription.status === 'active' ? 'Active' :
                     prescription.status === 'expired' ? 'Expirée' :
                     'Utilisée'}
                  </Badge>
                </div>

                {/* Dates */}
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    <span>
                      Émise le {format(new Date(prescription.date), 'dd/MM/yyyy', { locale: fr })}
                    </span>
                  </div>
                  {prescription.expiry_date && (
                    <div className="flex items-center gap-1">
                      <AlertCircle className="h-4 w-4" />
                      <span>
                        Expire le {format(new Date(prescription.expiry_date), 'dd/MM/yyyy', { locale: fr })}
                      </span>
                    </div>
                  )}
                </div>

                {/* Médicaments */}
                {prescription.medications && prescription.medications.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Médicaments prescrits:</h4>
                    <div className="space-y-2">
                      {prescription.medications.map((med: any, index: number) => (
                        <div key={index} className="bg-gray-50 p-3 rounded-lg">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-medium">{med.name}</p>
                              <p className="text-sm text-gray-600">{med.dosage}</p>
                              <p className="text-xs text-gray-500 mt-1">
                                {med.frequency} - {med.duration}
                              </p>
                            </div>
                            {med.quantity && (
                              <Badge variant="outline">
                                Qté: {med.quantity}
                              </Badge>
                            )}
                          </div>
                          {med.instructions && (
                            <p className="text-xs text-gray-600 mt-2 italic">
                              📋 {med.instructions}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Notes */}
                {prescription.notes && (
                  <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                    <p className="text-sm text-yellow-900">
                      <strong>Note du médecin:</strong> {prescription.notes}
                    </p>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2 ml-4">
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => downloadPDF(prescription.id)}
                >
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => showQRCode(prescription)}
                >
                  <QrCode className="h-4 w-4 mr-2" />
                  QR Code
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}

      {/* Modal QR Code */}
      {selectedPrescription && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedPrescription(null)}
        >
          <Card 
            className="max-w-md w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <CardHeader>
              <CardTitle className="text-center">QR Code de l'ordonnance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-white p-6 rounded-lg border-2 border-dashed">
                <div className="bg-gray-200 w-full aspect-square flex items-center justify-center rounded-lg">
                  <QrCode className="h-32 w-32 text-gray-400" />
                  <span className="absolute text-xs text-gray-500">QR Code généré ici</span>
                </div>
              </div>

              <div className="text-center space-y-2">
                <p className="text-sm text-gray-600">
                  Présentez ce QR code à votre pharmacien
                </p>
                <p className="text-xs text-gray-500">
                  Ordonnance #{selectedPrescription.id.slice(0, 8)}
                </p>
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="outline"
                  onClick={() => downloadPDF(selectedPrescription.id)}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Télécharger PDF
                </Button>
                <Button 
                  onClick={() => setSelectedPrescription(null)}
                  className="flex-1"
                >
                  Fermer
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
