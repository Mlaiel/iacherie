/**
 * Prescription Viewer Component
 * Display and download electronic prescriptions
 */
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Download, 
  AlertCircle, 
  Clock, 
  CheckCircle2,
  Pill,
  Calendar
} from 'lucide-react';

interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  duration_days: number;
  instructions?: string;
}

interface Prescription {
  id: string;
  doctor_name: string;
  issued_date: string;
  expiry_date: string;
  medications: Medication[];
  instructions?: string;
  qr_code: string;
  dispensed: boolean;
}

export function PrescriptionViewer({ prescriptionId }: { prescriptionId?: string }) {
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [selectedPrescription, setSelectedPrescription] = useState<Prescription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const fetchPrescriptions = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/medcare/prescriptions/patient/current-user-id');
      
      if (!response.ok) {
        throw new Error('Failed to fetch prescriptions');
      }

      const data = await response.json();
      setPrescriptions(data);
      
      if (prescriptionId) {
        const selected = data.find((p: Prescription) => p.id === prescriptionId);
        setSelectedPrescription(selected || null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load prescriptions');
      console.error('Prescription fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async (prescriptionId: string) => {
    try {
      // TODO: Implement PDF download
      const response = await fetch(`/api/medcare/prescriptions/${prescriptionId}/pdf`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `prescription-${prescriptionId}.pdf`;
      a.click();
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Failed to download prescription PDF');
    }
  };

  const isExpired = (expiryDate: string) => {
    return new Date(expiryDate) < new Date();
  };

  if (loading) {
    return <div className="text-center p-8">Loading prescriptions...</div>;
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (prescriptions.length === 0) {
    return (
      <Card>
        <CardContent className="text-center p-8">
          <Pill className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-600">No prescriptions found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h2 className="text-2xl font-bold mb-4">Your Prescriptions</h2>
      
      {prescriptions.map((prescription) => (
        <Card key={prescription.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Pill className="h-5 w-5" />
                  Prescription from Dr. {prescription.doctor_name}
                </CardTitle>
                <CardDescription className="flex items-center gap-4 mt-2">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Issued: {new Date(prescription.issued_date).toLocaleDateString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    Valid until: {new Date(prescription.expiry_date).toLocaleDateString()}
                  </span>
                </CardDescription>
              </div>
              <div className="flex gap-2">
                {prescription.dispensed && (
                  <Badge variant="secondary">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Dispensed
                  </Badge>
                )}
                {isExpired(prescription.expiry_date) && (
                  <Badge variant="destructive">Expired</Badge>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Medications List */}
            <div>
              <h4 className="font-semibold mb-2">Medications:</h4>
              <div className="space-y-2">
                {prescription.medications.map((med, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{med.name}</p>
                        <p className="text-sm text-gray-600">{med.dosage}</p>
                      </div>
                      <Badge variant="outline">{med.duration_days} days</Badge>
                    </div>
                    <p className="text-sm mt-2">
                      <span className="font-medium">Frequency:</span> {med.frequency}
                    </p>
                    {med.instructions && (
                      <p className="text-sm text-gray-600 mt-1">
                        <span className="font-medium">Instructions:</span> {med.instructions}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* General Instructions */}
            {prescription.instructions && (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Doctor's Instructions:</strong> {prescription.instructions}
                </AlertDescription>
              </Alert>
            )}

            {/* QR Code */}
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="font-medium text-sm">Verification QR Code</p>
                <p className="text-xs text-gray-600">Show this to your pharmacist</p>
              </div>
              {/* TODO: Generate and display actual QR code */}
              <div className="w-24 h-24 bg-white border-2 border-gray-300 rounded flex items-center justify-center">
                <span className="text-xs text-gray-400">QR Code</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <Button 
                onClick={() => downloadPDF(prescription.id)}
                className="flex-1"
                variant="outline"
              >
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
              <Button 
                className="flex-1"
                disabled={prescription.dispensed || isExpired(prescription.expiry_date)}
              >
                View Details
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}

      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription className="text-xs">
          Keep your prescriptions secure. Only share the QR code with authorized pharmacies.
          Do not share prescription details on social media or with unauthorized persons.
        </AlertDescription>
      </Alert>
    </div>
  );
}
