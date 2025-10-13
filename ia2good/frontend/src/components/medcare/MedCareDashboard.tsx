/**
 * MedCare Dashboard - Interface principale pour les patients
 * Navigation simple et claire avec accès à toutes les fonctionnalités
 */
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  Stethoscope, 
  Video, 
  Camera, 
  FileText, 
  Clock, 
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  MessageSquare,
  Users,
  Heart,
  Activity
} from 'lucide-react';

// Import des composants (à créer ou adapter)
// import { SymptomChecker } from './SymptomChecker';
// import { VideoCall } from './VideoCall';
// import { ImageAnalysis } from './ImageAnalysis';
// import { ConsultationHistory } from './ConsultationHistory';
// import { PrescriptionsList } from './PrescriptionsList';
// import { CommunityForum } from './CommunityForum';

interface DashboardProps {
  userId: string;
  userName: string;
}

export function MedCareDashboard({ userId, userName }: DashboardProps) {
  const [activeView, setActiveView] = useState<'home' | 'symptoms' | 'video' | 'image' | 'history' | 'community'>('home');
  const [currentConsultationId, setCurrentConsultationId] = useState<string | null>(null);

  // État des consultations en cours
  const [pendingConsultation, setPendingConsultation] = useState<any>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header avec navigation */}
      <header className="bg-white border-b sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Stethoscope className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">MedCare AI</h1>
                <p className="text-sm text-gray-500">Bonjour, {userName}</p>
              </div>
            </div>

            {/* Indicateur de statut */}
            <div className="flex items-center gap-4">
              {pendingConsultation && (
                <Badge variant="default" className="bg-green-500 text-white animate-pulse">
                  <Activity className="h-3 w-3 mr-1" />
                  Consultation en attente
                </Badge>
              )}
              <Button variant="outline" size="sm">
                <AlertCircle className="h-4 w-4 mr-2" />
                Aide
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Vue principale */}
      {activeView === 'home' && (
        <HomeView 
          onNavigate={setActiveView}
          pendingConsultation={pendingConsultation}
          onStartConsultation={() => setActiveView('video')}
        />
      )}

      {activeView === 'symptoms' && (
        <SymptomCheckerView 
          userId={userId}
          onBack={() => setActiveView('home')}
          onConsultationRequested={(consultation) => {
            setPendingConsultation(consultation);
            setCurrentConsultationId(consultation.id);
          }}
        />
      )}

      {activeView === 'video' && currentConsultationId && (
        <VideoConsultationView
          consultationId={currentConsultationId}
          onEnd={() => {
            setActiveView('home');
            setPendingConsultation(null);
            setCurrentConsultationId(null);
          }}
        />
      )}

      {activeView === 'image' && (
        <ImageAnalysisView
          userId={userId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'history' && (
        <HistoryView
          userId={userId}
          onBack={() => setActiveView('home')}
        />
      )}

      {activeView === 'community' && (
        <CommunityView
          userId={userId}
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
  pendingConsultation,
  onStartConsultation 
}: { 
  onNavigate: (view: any) => void;
  pendingConsultation: any;
  onStartConsultation: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Alerte consultation en attente */}
      {pendingConsultation && (
        <Card className="mb-6 border-green-500 bg-green-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-green-500 p-3 rounded-full">
                  <Video className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Médecin trouvé !</h3>
                  <p className="text-sm text-gray-600">
                    Dr. {pendingConsultation.doctorName} est prêt pour votre consultation
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    Temps d'attente estimé : {pendingConsultation.estimatedWait}
                  </p>
                </div>
              </div>
              <Button size="lg" className="bg-green-600 hover:bg-green-700" onClick={onStartConsultation}>
                <Video className="h-5 w-5 mr-2" />
                Démarrer la consultation
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions principales - Design en grille */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Décrire symptômes */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-blue-500"
          onClick={() => onNavigate('symptoms')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-blue-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <MessageSquare className="h-10 w-10 text-blue-600" />
            </div>
            <CardTitle className="text-xl">Décrire mes symptômes</CardTitle>
            <CardDescription>
              Décrivez vos symptômes et l'IA vous aidera
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Analyse instantanée</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Détection urgence</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Médecin si besoin</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="default">
              Commencer
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Analyse d'image */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-purple-500"
          onClick={() => onNavigate('image')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-purple-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <Camera className="h-10 w-10 text-purple-600" />
            </div>
            <CardTitle className="text-xl">Analyser une image</CardTitle>
            <CardDescription>
              Photo de peau, radiographie, résultat d'analyse
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>IA dermatologie</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Analyse radiographie</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Résultat en 5 sec</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="default">
              Prendre une photo
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Consultation vidéo */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow border-2 hover:border-red-500"
          onClick={() => onNavigate('video')}
        >
          <CardHeader className="text-center pb-4">
            <div className="mx-auto bg-red-100 p-4 rounded-full w-20 h-20 flex items-center justify-center mb-4">
              <Video className="h-10 w-10 text-red-600" />
            </div>
            <CardTitle className="text-xl">Consultation urgente</CardTitle>
            <CardDescription>
              Parler avec un médecin maintenant
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Vidéo HD sécurisée</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Attente &lt; 5 min</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <span>Ordonnance immédiate</span>
              </div>
            </div>
            <Button className="w-full mt-4 bg-red-600 hover:bg-red-700">
              Démarrer
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Actions secondaires */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Historique */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onNavigate('history')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-gray-100 p-3 rounded-lg">
                <Clock className="h-6 w-6 text-gray-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Mes consultations</h3>
                <p className="text-sm text-gray-600">Historique et ordonnances</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        {/* Communauté */}
        <Card 
          className="cursor-pointer hover:shadow-lg transition-shadow"
          onClick={() => onNavigate('community')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="bg-yellow-100 p-3 rounded-lg">
                <Users className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Forum santé</h3>
                <p className="text-sm text-gray-600">Partager et s'entraider</p>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Statistiques personnelles */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Votre santé en un coup d'œil</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">12</div>
              <div className="text-sm text-gray-600 mt-1">Consultations</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-3xl font-bold text-green-600">5</div>
              <div className="text-sm text-gray-600 mt-1">Ordonnances</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">8</div>
              <div className="text-sm text-gray-600 mt-1">Analyses</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-3xl font-bold text-yellow-600">98%</div>
              <div className="text-sm text-gray-600 mt-1">Satisfaction</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Vue Vérification des Symptômes
 */
function SymptomCheckerView({ 
  userId, 
  onBack,
  onConsultationRequested 
}: { 
  userId: string;
  onBack: () => void;
  onConsultationRequested: (consultation: any) => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <Card>
        <CardHeader>
          <CardTitle>Vérification des symptômes</CardTitle>
          <CardDescription>
            Cette fonctionnalité sera disponible prochainement
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Le composant SymptomChecker sera intégré ici.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Vue Consultation Vidéo
 */
function VideoConsultationView({ 
  consultationId, 
  onEnd 
}: { 
  consultationId: string;
  onEnd: () => void;
}) {
  return (
    <div className="h-screen bg-gray-900 flex items-center justify-center">
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Consultation Vidéo</CardTitle>
          <CardDescription>
            Le composant VideoCall sera intégré ici
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            Consultation ID: {consultationId}
          </p>
          <Button onClick={onEnd} variant="destructive" className="w-full">
            Terminer la consultation
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Vue Analyse d'Image
 */
function ImageAnalysisView({ 
  userId, 
  onBack 
}: { 
  userId: string;
  onBack: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <Card>
        <CardHeader>
          <CardTitle>Analyse d'image médicale</CardTitle>
          <CardDescription>
            Analysez vos photos médicales avec l'IA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Le composant ImageAnalysis sera intégré ici.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Vue Historique
 */
function HistoryView({ 
  userId, 
  onBack 
}: { 
  userId: string;
  onBack: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      
      <Tabs defaultValue="consultations" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="consultations">Consultations</TabsTrigger>
          <TabsTrigger value="prescriptions">Ordonnances</TabsTrigger>
        </TabsList>
        
        <TabsContent value="consultations">
          <Card>
            <CardHeader>
              <CardTitle>Historique des consultations</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Le composant ConsultationHistory sera intégré ici.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="prescriptions">
          <Card>
            <CardHeader>
              <CardTitle>Mes ordonnances</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Le composant PrescriptionsList sera intégré ici.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * Vue Communauté
 */
function CommunityView({ 
  userId, 
  onBack 
}: { 
  userId: string;
  onBack: () => void;
}) {
  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <Button variant="ghost" onClick={onBack} className="mb-4">
        ← Retour au tableau de bord
      </Button>
      <Card>
        <CardHeader>
          <CardTitle>Forum Santé Communautaire</CardTitle>
          <CardDescription>
            Partagez votre expérience et soutenez d'autres personnes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Le composant CommunityForum sera intégré ici.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
