/**
 * Volunteer Main Dashboard - Interface principale pour les bénévoles
 * Navigation claire et intuitive avec accès à toutes les fonctionnalités
 */
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Heart, 
  Users, 
  MapPin, 
  Calendar, 
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Bell,
  Award,
  Activity,
  Eye,
  FileText,
  Handshake
} from 'lucide-react';

import { VolunteerDashboard } from './VolunteerDashboard';
import { CaseList } from './CaseList';
import { ReportCase } from './ReportCase';
import { VolunteerProfile } from './VolunteerProfile';
import { VolunteerDirectory } from './VolunteerDirectory';
import { VolunteerSettings } from './VolunteerSettings';

interface VolunteerMainDashboardProps {
  volunteerId: string;
  volunteerName: string;
}

type ViewType = 'home' | 'cases' | 'report' | 'stats' | 'profile' | 'directory' | 'settings';

export function VolunteerMainDashboard({ volunteerId, volunteerName }: VolunteerMainDashboardProps) {
  const [activeView, setActiveView] = useState<ViewType>('home');
  const [urgentCases, setUrgentCases] = useState<number>(3);
  const [activeMissions, setActiveMissions] = useState<number>(2);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec navigation */}
      <header className="bg-white border-b sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-green-600 p-2 rounded-lg">
                <Heart className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">IA2Good Volunteer</h1>
                <p className="text-sm text-gray-500">Bonjour, {volunteerName}</p>
              </div>
            </div>

            {/* Indicateurs de statut */}
            <div className="flex items-center gap-4">
              {urgentCases > 0 && (
                <Badge variant="destructive" className="animate-pulse">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  {urgentCases} cas urgents
                </Badge>
              )}
              {activeMissions > 0 && (
                <Badge variant="default" className="bg-blue-500">
                  <Activity className="h-3 w-3 mr-1" />
                  {activeMissions} missions actives
                </Badge>
              )}
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Vue principale */}
      {activeView === 'home' && (
        <HomeView 
          onNavigate={setActiveView}
          urgentCases={urgentCases}
          activeMissions={activeMissions}
        />
      )}

      {activeView === 'cases' && (
        <CasesView 
          volunteerId={volunteerId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'report' && (
        <ReportView 
          volunteerId={volunteerId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'stats' && (
        <StatsView 
          volunteerId={volunteerId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'profile' && (
        <ProfileView 
          volunteerId={volunteerId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'directory' && (
        <DirectoryView 
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'settings' && (
        <SettingsView 
          volunteerId={volunteerId}
          onBack={() => setActiveView('home')}
        />
      )}
    </div>
  );
}

/**
 * Vue d'accueil - Point d'entrée principal
 */
function HomeView({ 
  onNavigate, 
  urgentCases,
  activeMissions 
}: { 
  onNavigate: (view: ViewType) => void;
  urgentCases: number;
  activeMissions: number;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Alertes cas urgents */}
      {urgentCases > 0 && (
        <Card className="mb-6 border-red-500 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-red-500 p-3 rounded-full animate-pulse">
                  <AlertCircle className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-red-900">
                    {urgentCases} cas urgent{urgentCases > 1 ? 's' : ''} !
                  </h3>
                  <p className="text-sm text-red-700">
                    Des personnes ont besoin d'aide immédiate dans votre zone
                  </p>
                </div>
              </div>
              <Button size="lg" className="bg-red-600 hover:bg-red-700" onClick={() => onNavigate('cases')}>
                <Eye className="h-5 w-5 mr-2" />
                Voir les cas
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions principales - Design en grille */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Voir les cas */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-500"
          onClick={() => onNavigate('cases')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-blue-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <Eye className="h-10 w-10 text-blue-600" />
            </div>
            <CardTitle className="text-xl">Voir les cas</CardTitle>
            <CardDescription>
              Découvrez qui a besoin d'aide près de vous
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Cas filtrés par zone</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Urgences en priorité</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Détails complets</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="default">
              Explorer les cas
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Signaler un cas */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-green-500"
          onClick={() => onNavigate('report')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-green-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <FileText className="h-10 w-10 text-green-600" />
            </div>
            <CardTitle className="text-xl">Signaler un cas</CardTitle>
            <CardDescription>
              Aidez quelqu'un que vous avez rencontré
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Formulaire simple</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Photo et localisation</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Alerte communauté</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="default">
              Créer un signalement
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Mes statistiques */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-purple-500"
          onClick={() => onNavigate('stats')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-purple-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <TrendingUp className="h-10 w-10 text-purple-600" />
            </div>
            <CardTitle className="text-xl">Mon impact</CardTitle>
            <CardDescription>
              Suivez vos actions et votre contribution
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Personnes aidées</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Objectifs hebdo</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Badges & récompenses</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="default">
              Voir mes stats
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Actions secondaires */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Annuaire des bénévoles */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onNavigate('directory')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-yellow-100 p-3 rounded-lg">
                <Users className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Annuaire bénévoles</h3>
                <p className="text-sm text-gray-600">Trouvez de l'aide locale</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        {/* Mon profil */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onNavigate('profile')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Award className="h-6 w-6 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Mon profil</h3>
                <p className="text-sm text-gray-600">Compétences & badges</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        {/* Paramètres */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onNavigate('settings')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-gray-100 p-3 rounded-lg">
                <Activity className="h-6 w-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Paramètres</h3>
                <p className="text-sm text-gray-600">Zone, notifications</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Missions actives */}
      {activeMissions > 0 && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Handshake className="h-5 w-5 text-blue-600" />
              Mes missions actives
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {/* Mock missions */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold">Aide alimentaire - Famille Martin</h4>
                    <p className="text-sm text-gray-600 mt-1">📍 5 rue Victor Hugo, Paris 15ème</p>
                    <Badge variant="secondary" className="mt-2">En cours</Badge>
                  </div>
                  <Button size="sm" variant="outline">
                    Détails
                  </Button>
                </div>
              </div>

              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold">Cours de français - Mohamed</h4>
                    <p className="text-sm text-gray-600 mt-1">📍 Bibliothèque municipale</p>
                    <Badge variant="secondary" className="mt-2">Planifié demain 14h</Badge>
                  </div>
                  <Button size="sm" variant="outline">
                    Détails
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Statistiques globales */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Impact communautaire cette semaine</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">127</div>
              <div className="text-sm text-gray-600 mt-1">Cas actifs</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">43</div>
              <div className="text-sm text-gray-600 mt-1">Résolus cette semaine</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">89</div>
              <div className="text-sm text-gray-600 mt-1">Bénévoles actifs</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-3xl font-bold text-yellow-600">2.3h</div>
              <div className="text-sm text-gray-600 mt-1">Temps moyen réponse</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Vue Cas
 */
function CasesView({ 
  volunteerId, 
  onBack 
}: { 
  volunteerId: string;
  onBack: () => void;
}) {
  const [cases, setCases] = useState<any[]>([]);

  const handleCaseUpdate = (updatedCase: any) => {
    setCases(prevCases => 
      prevCases.map(c => c.id === updatedCase.id ? updatedCase : c)
    );
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <CaseList cases={cases} onCaseUpdate={handleCaseUpdate} />
    </div>
  );
}

/**
 * Vue Signalement
 */
function ReportView({ 
  volunteerId, 
  onBack 
}: { 
  volunteerId: string;
  onBack: () => void;
}) {
  const handleReportSubmit = (newReport: any) => {
    console.log('New report:', newReport);
    onBack(); // Retour après soumission
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <ReportCase onReportSubmitted={handleReportSubmit} />
    </div>
  );
}

/**
 * Vue Statistiques
 */
function StatsView({ 
  volunteerId, 
  onBack 
}: { 
  volunteerId: string;
  onBack: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <VolunteerDashboard cases={[]} activities={[]} />
    </div>
  );
}

/**
 * Vue Profil
 */
function ProfileView({ 
  volunteerId, 
  onBack 
}: { 
  volunteerId: string;
  onBack: () => void;
}) {
  // Mock profile data - dans une vraie app, charger depuis l'API
  const mockProfile = {
    id: volunteerId,
    name: 'Bénévole Actif',
    email: 'volunteer@ia2good.org',
    avatarUrl: undefined,
    joinedAt: new Date().toISOString(),
    bio: 'Bénévole passionné par l\'aide humanitaire',
    skills: ['Premier secours', 'Traduction', 'Distribution alimentaire'],
    availableHours: {
      days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
      startTime: '09:00',
      endTime: '17:00'
    },
    preferences: {
      maxDistance: 10,
      preferredCategories: ['homeless' as const, 'animal' as const],
      notificationSettings: {
        enabled: true,
        radius: 10,
        categories: ['homeless' as const, 'animal' as const],
        urgencyLevels: ['low' as const, 'medium' as const, 'high' as const],
        quietHours: {
          enabled: false,
          start: '22:00',
          end: '08:00'
        }
      }
    },
    verification: {
      isVerified: true,
      verifiedAt: new Date().toISOString(),
      verificationMethod: 'email' as const
    },
    stats: {
      totalCasesHelped: 42,
      totalReports: 15,
      totalHoursVolunteered: 120,
      peopleHelped: 38,
      animalsHelped: 4,
      activeStreakDays: 7,
      averageResponseTime: 15,
      mostActiveCategory: 'homeless' as const,
      badges: [
        {
          id: 'badge-1',
          name: 'Premier Répondeur',
          description: 'A aidé 10 personnes',
          icon: '🚀',
          earnedAt: new Date().toISOString(),
          category: 'milestone' as const
        }
      ],
      rating: 4.8,
      reviewCount: 12
    }
  };

  const mockActivities: any[] = [];
  const mockCases: any[] = [];

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <VolunteerProfile 
        profile={mockProfile}
        activities={mockActivities}
        cases={mockCases}
        isOwnProfile={true}
      />
    </div>
  );
}

/**
 * Vue Annuaire
 */
function DirectoryView({ 
  onBack 
}: { 
  onBack: () => void;
}) {
  const [volunteers] = useState<any[]>([]);

  const handleViewProfile = (volunteerId: string) => {
    console.log('View profile:', volunteerId);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <VolunteerDirectory volunteers={volunteers} onViewProfile={handleViewProfile} />
    </div>
  );
}

/**
 * Vue Paramètres
 */
function SettingsView({ 
  volunteerId, 
  onBack 
}: { 
  volunteerId: string;
  onBack: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <VolunteerSettings />
    </div>
  );
}
