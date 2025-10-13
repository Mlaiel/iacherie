/**
 * Unified Dashboard Component
 * Aggregates data from all 4 modules
 */
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Heart,
  Shield,
  GraduationCap,
  Stethoscope,
  TrendingUp,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  Star,
  Calendar,
  Activity
} from 'lucide-react';

interface DashboardStats {
  ia2good?: {
    activeCases: number;
    casesHelped: number;
    volunteersActive: number;
    impactPoints: number;
  };
  guardian?: {
    alertsSent: number;
    hazardsDetected: number;
    responseTime: string;
    uptime: string;
  };
  eduverify?: {
    quizzesCompleted: number;
    contentVerified: number;
    learningProgress: number;
    streak: number;
  };
  medcare?: {
    consultationsPending: number;
    consultationsCompleted: number;
    prescriptionsActive: number;
    nextAppointment?: string;
  };
}

interface UnifiedDashboardProps {
  stats: DashboardStats;
}

export function UnifiedDashboard({ stats }: UnifiedDashboardProps) {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome back!</h1>
        <p className="text-gray-500 mt-1">Here's what's happening across your modules</p>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* IA2GOOD Stats */}
        {stats.ia2good && (
          <Card className="border-l-4 border-l-blue-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">IA2GOOD</CardTitle>
              <Heart className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Cases</span>
                  <Badge variant="secondary">{stats.ia2good.activeCases}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Cases Helped</span>
                  <Badge variant="secondary">{stats.ia2good.casesHelped}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Impact Points</span>
                  <Badge className="bg-blue-500">
                    <Star className="h-3 w-3 mr-1" />
                    {stats.ia2good.impactPoints}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Guardian Stats */}
        {stats.guardian && (
          <Card className="border-l-4 border-l-green-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Guardian</CardTitle>
              <Shield className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Alerts Sent</span>
                  <Badge variant="secondary">{stats.guardian.alertsSent}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Hazards Detected</span>
                  <Badge variant="secondary">{stats.guardian.hazardsDetected}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Response Time</span>
                  <Badge className="bg-green-500">
                    <Clock className="h-3 w-3 mr-1" />
                    {stats.guardian.responseTime}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* EduVerify Stats */}
        {stats.eduverify && (
          <Card className="border-l-4 border-l-purple-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">EduVerify</CardTitle>
              <GraduationCap className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Quizzes Completed</span>
                  <Badge variant="secondary">{stats.eduverify.quizzesCompleted}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Learning Progress</span>
                  <Badge variant="secondary">{stats.eduverify.learningProgress}%</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Day Streak</span>
                  <Badge className="bg-purple-500">
                    <TrendingUp className="h-3 w-3 mr-1" />
                    {stats.eduverify.streak} days
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* MedCare Stats */}
        {stats.medcare && (
          <Card className="border-l-4 border-l-red-500">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">MedCare</CardTitle>
              <Stethoscope className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Pending Consultations</span>
                  <Badge variant="secondary">{stats.medcare.consultationsPending}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Completed</span>
                  <Badge variant="secondary">{stats.medcare.consultationsCompleted}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Prescriptions</span>
                  <Badge className="bg-red-500">
                    <Activity className="h-3 w-3 mr-1" />
                    {stats.medcare.prescriptionsActive}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent Activity Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Activity across all modules</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Placeholder activities - would be populated with real data */}
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <Heart className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">New case assigned in IA2GOOD</p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                <Stethoscope className="h-4 w-4 text-red-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Consultation scheduled for tomorrow</p>
                <p className="text-xs text-gray-500">5 hours ago</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <GraduationCap className="h-4 w-4 text-purple-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Quiz completed: Advanced Biology</p>
                <p className="text-xs text-gray-500">Yesterday</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks across modules</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="flex flex-col gap-2 h-auto py-4">
              <Heart className="h-5 w-5 text-blue-600" />
              <span className="text-xs">Report Case</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-auto py-4">
              <Shield className="h-5 w-5 text-green-600" />
              <span className="text-xs">SOS Alert</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-auto py-4">
              <GraduationCap className="h-5 w-5 text-purple-600" />
              <span className="text-xs">Take Quiz</span>
            </Button>
            <Button variant="outline" className="flex flex-col gap-2 h-auto py-4">
              <Stethoscope className="h-5 w-5 text-red-600" />
              <span className="text-xs">Book Consultation</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Platform Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Impact</CardTitle>
            <TrendingUp className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,234</div>
            <p className="text-xs text-gray-500 mt-1">People helped across all modules</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2,456</div>
            <p className="text-xs text-gray-500 mt-1">Currently online</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Response Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.5%</div>
            <p className="text-xs text-gray-500 mt-1">Average across all modules</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
