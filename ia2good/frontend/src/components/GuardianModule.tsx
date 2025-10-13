/**
 * Guardian Module - Emergency SOS & Safety
 * Placeholder component for Guardian functionality
 */
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Shield, 
  AlertTriangle, 
  Phone, 
  MapPin, 
  Clock,
  CheckCircle,
  Camera,
  Mic
} from 'lucide-react';

export function GuardianModule() {
  return (
    <div className="space-y-6">
      {/* SOS Quick Action */}
      <Card className="border-red-500 border-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangle className="h-6 w-6" />
            Emergency SOS
          </CardTitle>
          <CardDescription>
            Quick access to emergency services and contacts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button size="lg" className="w-full bg-red-600 hover:bg-red-700 text-lg py-6">
            <Phone className="h-6 w-6 mr-2" />
            SEND SOS ALERT
          </Button>
        </CardContent>
      </Card>

      {/* Active Monitoring */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-green-600" />
            Active Monitoring
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm">Location Services</span>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm">Hazard Detection</span>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800">Active</Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm">Emergency Contacts</span>
              </div>
              <Badge variant="secondary">3 contacts</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Camera className="h-4 w-4" />
              Visual Hazard Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              AI-powered hazard detection using your camera to identify dangerous situations.
            </p>
            <Button variant="outline" className="w-full mt-4">
              Enable Camera
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Mic className="h-4 w-4" />
              Voice Commands
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600">
              Activate SOS and other features using voice commands for hands-free operation.
            </p>
            <Button variant="outline" className="w-full mt-4">
              Enable Voice
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <Shield className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>No recent alerts</p>
            <p className="text-sm">Your Guardian is actively monitoring your safety</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
