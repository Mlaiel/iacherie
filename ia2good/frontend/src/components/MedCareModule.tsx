/**
 * MedCare Module - Telemedicine & Diagnosis
 * Placeholder component integrating MedCare functionality
 */
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Stethoscope, 
  Calendar, 
  FileText, 
  Activity,
  Video,
  Image as ImageIcon,
  Pill,
  AlertCircle,
  Clock,
  CheckCircle2
} from 'lucide-react';
import { SymptomChecker } from '@/components/medcare/SymptomChecker';
import { PrescriptionViewer } from '@/components/medcare/PrescriptionViewer';
import { VideoCall } from '@/components/medcare/VideoCall';

export function MedCareModule() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="symptoms">Symptom Checker</TabsTrigger>
          <TabsTrigger value="consultations">Consultations</TabsTrigger>
          <TabsTrigger value="prescriptions">Prescriptions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Quick Stats */}
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="border-red-200">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Upcoming Consultations</CardTitle>
                <Calendar className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2</div>
                <p className="text-xs text-gray-500 mt-1">Next: Tomorrow at 10:00 AM</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Active Prescriptions</CardTitle>
                <Pill className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-gray-500 mt-1">1 expiring soon</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Medical Records</CardTitle>
                <FileText className="h-4 w-4 text-gray-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-gray-500 mt-1">Last updated 2 days ago</p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>Common telemedicine tasks</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button 
                  variant="outline" 
                  className="flex flex-col gap-2 h-auto py-6"
                  onClick={() => setActiveTab('symptoms')}
                >
                  <Activity className="h-6 w-6 text-red-600" />
                  <span className="text-sm">Check Symptoms</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="flex flex-col gap-2 h-auto py-6"
                  onClick={() => setActiveTab('consultations')}
                >
                  <Video className="h-6 w-6 text-blue-600" />
                  <span className="text-sm">Book Consultation</span>
                </Button>
                
                <Button variant="outline" className="flex flex-col gap-2 h-auto py-6">
                  <ImageIcon className="h-6 w-6 text-purple-600" />
                  <span className="text-sm">Upload Image</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="flex flex-col gap-2 h-auto py-6"
                  onClick={() => setActiveTab('prescriptions')}
                >
                  <Pill className="h-6 w-6 text-green-600" />
                  <span className="text-sm">View Prescriptions</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Appointments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Upcoming Appointments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                      <Stethoscope className="h-6 w-6 text-red-600" />
                    </div>
                    <div>
                      <p className="font-medium">Dr. Sarah Johnson</p>
                      <p className="text-sm text-gray-500">General Consultation</p>
                      <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                        <Clock className="h-3 w-3" />
                        Tomorrow, 10:00 AM
                      </p>
                    </div>
                  </div>
                  <Button size="sm">
                    <Video className="h-4 w-4 mr-1" />
                    Join
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <Stethoscope className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium">Dr. Michael Chen</p>
                      <p className="text-sm text-gray-500">Follow-up Consultation</p>
                      <p className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                        <Clock className="h-3 w-3" />
                        Friday, 2:30 PM
                      </p>
                    </div>
                  </div>
                  <Button size="sm" variant="outline">
                    Reschedule
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Health Alerts */}
          <Card className="border-yellow-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-800">
                <AlertCircle className="h-5 w-5" />
                Health Reminders
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-yellow-600" />
                  <span>Take Amoxicillin - 500mg at 8:00 PM</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-yellow-600" />
                  <span>Prescription expires in 5 days - Refill needed</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="symptoms">
          <SymptomChecker />
        </TabsContent>

        <TabsContent value="consultations">
          <Card>
            <CardHeader>
              <CardTitle>Telemedicine Consultations</CardTitle>
              <CardDescription>
                Connect with healthcare professionals via video call
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Experience telemedicine consultations with qualified doctors. Book a consultation
                  to discuss your health concerns, get prescriptions, and receive medical advice.
                </p>
                <VideoCall 
                  consultationId="demo-consultation-123"
                  patientName="John Doe"
                  doctorName="Dr. Sarah Johnson"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="prescriptions">
          <PrescriptionViewer />
        </TabsContent>
      </Tabs>
    </div>
  );
}
