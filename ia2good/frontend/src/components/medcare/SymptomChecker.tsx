/**
 * Symptom Checker Component
 * Interactive symptom questionnaire with AI analysis
 */
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

interface Symptom {
  name: string;
  severity: number;
  duration_hours: number;
  body_parts: string[];
}

export function SymptomChecker() {
  const [symptom, setSymptom] = useState<Symptom>({
    name: '',
    severity: 5,
    duration_hours: 0,
    body_parts: []
  });
  const [loading, setLoading] = useState(false);
  const [diagnosis, setDiagnosis] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/medcare/symptoms/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_id: 'current-user-id', // TODO: Get from auth context
          symptoms: { [symptom.name]: { severity: symptom.severity } },
          severity: symptom.severity,
          duration_hours: symptom.duration_hours,
          body_parts: symptom.body_parts,
          images: []
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze symptoms');
      }

      const data = await response.json();
      setDiagnosis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Symptom analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'emergency': return 'text-red-600';
      case 'urgent': return 'text-orange-600';
      case 'routine': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-6 w-6" />
            Symptom Checker
          </CardTitle>
          <CardDescription>
            Describe your symptoms for AI-powered preliminary analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!diagnosis ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="symptom">What are you experiencing?</Label>
                <Input
                  id="symptom"
                  placeholder="e.g., headache, fever, cough"
                  value={symptom.name}
                  onChange={(e) => setSymptom({ ...symptom, name: e.target.value })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="severity">
                  Severity: {symptom.severity}/10
                </Label>
                <Slider
                  id="severity"
                  min={1}
                  max={10}
                  step={1}
                  value={[symptom.severity]}
                  onValueChange={(value) => setSymptom({ ...symptom, severity: value[0] })}
                  className="mt-2"
                />
              </div>

              <div>
                <Label htmlFor="duration">How long (hours)?</Label>
                <Input
                  id="duration"
                  type="number"
                  min={0}
                  placeholder="Duration in hours"
                  value={symptom.duration_hours || ''}
                  onChange={(e) => setSymptom({ ...symptom, duration_hours: parseInt(e.target.value) || 0 })}
                  required
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  This is a preliminary AI analysis and NOT a substitute for professional medical advice.
                  Always consult with a qualified healthcare provider.
                </AlertDescription>
              </Alert>

              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  'Analyze Symptoms'
                )}
              </Button>
            </form>
          ) : (
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Analysis complete. Review the results below.
                </AlertDescription>
              </Alert>

              <div className="border-l-4 border-blue-500 pl-4">
                <h3 className="font-semibold text-lg">Preliminary Analysis</h3>
                <p className={`text-sm font-medium ${getUrgencyColor(diagnosis.urgency)}`}>
                  Urgency: {diagnosis.urgency?.toUpperCase()}
                </p>
              </div>

              {diagnosis.top_conditions && (
                <div>
                  <h4 className="font-semibold mb-2">Possible Conditions:</h4>
                  <ul className="space-y-2">
                    {diagnosis.top_conditions.map((condition: any, index: number) => (
                      <li key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span>{condition.name}</span>
                        <span className="text-sm text-gray-600">
                          {(condition.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {diagnosis.recommendations && (
                <div>
                  <h4 className="font-semibold mb-2">Recommendations:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {diagnosis.recommendations.map((rec: string, index: number) => (
                      <li key={index} className="text-sm">{rec}</li>
                    ))}
                  </ul>
                </div>
              )}

              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-xs">
                  {diagnosis.medical_disclaimer}
                </AlertDescription>
              </Alert>

              <div className="flex gap-2">
                <Button onClick={() => setDiagnosis(null)} variant="outline" className="flex-1">
                  Check Another Symptom
                </Button>
                <Button className="flex-1">
                  Request Consultation
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
