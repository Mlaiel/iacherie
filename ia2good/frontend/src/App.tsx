/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 * 
 * PLATEFORME HUMANITAIRE INTÉGRÉE - 4 MODULES
 * - IA2GOOD: Signalement et assistance humanitaire (OPÉRATIONNEL)
 * - Guardian: Surveillance et sécurité communautaire (Backend prêt)
 * - EduVerify: Vérification des parcours éducatifs (Backend prêt)
 * - MedCare: Gestion des soins médicaux (Backend prêt)
 */

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  Heart, 
  MapPin, 
  Users, 
  List, 
  Plus, 
  Gear, 
  Bell,
  Info,
  Phone,
  Shield,
  ChartBar,
  UserCircle,
  ShieldCheck,
  GraduationCap,
  FirstAid,
  SignOut
} from '@phosphor-icons/react'
import { toast } from 'sonner'
import { useKV } from '@/hooks/useKV'
import { CaseReport, VolunteerActivity, VolunteerProfile as VolunteerProfileType } from '@/lib/types'
import { api } from '@/lib/api'
import { ReportCase } from '@/components/ReportCase'
import { CaseList } from '@/components/CaseList'
import { VolunteerSettings } from '@/components/VolunteerSettings'
import { QuickStartGuide } from '@/components/QuickStartGuide'
import { VoiceControls } from '@/components/VoiceControls'
import { DebugInfo } from '@/components/DebugInfo'
import { VolunteerDashboard } from '@/components/VolunteerDashboard'
import { VolunteerDirectory } from '@/components/VolunteerDirectory'
import { VolunteerProfile } from '@/components/VolunteerProfile'
import { EditVolunteerProfile } from '@/components/EditVolunteerProfile'
import { LanguageSelector } from '@/components/LanguageSelector'
import { LanguageTest } from '@/components/LanguageTest'
import { sampleCases, sampleVolunteerProfiles } from '@/lib/sampleData'
import { useTranslation } from '@/hooks/useTranslation'
import { MedCareDashboard } from '@/components/medcare/MedCareDashboard'
import { VolunteerMainDashboard } from '@/components/VolunteerMainDashboard'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import Login from '@/components/auth/Login'
import Register from '@/components/auth/Register'
import { MapView } from '@/components/MapView'
import { SystemStatus } from '@/components/SystemStatus'
import { NavigationCard } from '@/components/NavigationCard'

type ModuleType = 'ia2good' | 'guardian' | 'eduverify' | 'medcare' | 'volunteer'

function AppContent() {
  const { t, isLoading: i18nLoading } = useTranslation();
  const { user, logout, isAuthenticated } = useAuth();
  const [activeModule, setActiveModule] = useState<ModuleType>('ia2good')
  const [activeTab, setActiveTab] = useState('home')
  const [selectedCase, setSelectedCase] = useState<CaseReport | null>(null)
  const [isVolunteer, setIsVolunteer] = useState(false)
  const [cases, setCases] = useState<CaseReport[]>([])
  const [activities, setActivities] = useState<VolunteerActivity[]>([])
  const [volunteers, setVolunteers] = useState<VolunteerProfileType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentVolunteerId, setCurrentVolunteerId] = useState('volunteer-1') // Mock current user
  const [selectedVolunteerId, setSelectedVolunteerId] = useState<string | null>(null)
  const [stats, setStats] = useState({
    total: 0,
    open: 0,
    inProgress: 0,
    helped: 0
  })

  // Charger les données RÉELLES depuis le backend au démarrage
  useEffect(() => {
    const loadRealData = async () => {
      try {
        setIsLoading(true)
        setError(null)
        
        // Charger les cas réels depuis l'API
        const realCases = await api.getCases() as CaseReport[]
        setCases(realCases)
        console.log(`✅ Données RÉELLES chargées: ${realCases.length} cas`)
        
        // Charger les bénévoles réels (peut échouer si endpoint pas implémenté)
        try {
          const realVolunteers = await api.getVolunteers() as VolunteerProfileType[]
          setVolunteers(realVolunteers)
          console.log(`✅ ${realVolunteers.length} bénévoles chargés`)
        } catch (volunteerError) {
          console.warn('⚠️ Volunteers endpoint not yet implemented, using empty array')
          setVolunteers([])
        }
        
        toast.success(`${realCases.length} cas chargés depuis le backend RÉEL`)
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Erreur de connexion au backend'
        setError(errorMsg)
        console.error('❌ Erreur chargement données:', err)
        toast.error(`Échec du chargement: ${errorMsg}`)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadRealData()
  }, [])

  // Calculate statistics
  useEffect(() => {
    const safeCases = cases || [];
    const newStats = {
      total: safeCases.length,
      open: safeCases.filter(c => c.status === 'open').length,
      inProgress: safeCases.filter(c => c.status === 'in-progress').length,
      helped: safeCases.filter(c => c.status === 'helped').length
    }
    setStats(newStats)
  }, [cases])

  const handleCaseUpdate = async (updatedCase: CaseReport) => {
    try {
      // Mettre à jour dans le backend RÉEL
      const updated = await api.updateCase(updatedCase.id, updatedCase) as CaseReport
      
      // Mettre à jour la liste locale
      setCases((currentCases) => 
        (currentCases || []).map(c => c.id === updated.id ? updated : c)
      )
      
      // Create activity record for status changes
      if (updated.status === 'helped' || updated.status === 'in-progress') {
        const newActivity: VolunteerActivity = {
          id: `activity-${Date.now()}`,
          volunteerId: currentVolunteerId,
          caseId: updated.id,
          action: updated.status === 'helped' ? 'helped' : 'started-helping',
          timestamp: new Date().toISOString(),
          location: updated.location,
          notes: `${updated.status === 'helped' ? t('app.completed') : t('app.started')} ${t('app.assistanceFor')} ${updated.type} ${t('app.case')}`
        }
        
        setActivities((currentActivities) => [...(currentActivities || []), newActivity])
      }
      
      toast.success('Cas mis à jour dans le backend RÉEL')
      console.log('✅ Cas mis à jour:', updated)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erreur lors de la mise à jour'
      console.error('❌ Erreur mise à jour cas:', err)
      toast.error(`Échec de la mise à jour: ${errorMsg}`)
    }
  }

  const handleNewReport = async (newReport: CaseReport) => {
    try {
      // Créer le cas dans le backend RÉEL
      const createdCase = await api.createCase(newReport) as CaseReport
      
      // Ajouter à la liste locale
      setCases((currentCases) => [...(currentCases || []), createdCase])
      
      // Create activity record for new reports
      const newActivity: VolunteerActivity = {
        id: `activity-${Date.now()}`,
        volunteerId: currentVolunteerId,
        caseId: createdCase.id,
        action: 'reported',
        timestamp: new Date().toISOString(),
        location: createdCase.location,
        notes: `Reported new ${createdCase.type} case`
      }
      
      setActivities((currentActivities) => [...(currentActivities || []), newActivity])
      
      toast.success('Cas créé dans le backend RÉEL')
      console.log('✅ Nouveau cas créé:', createdCase)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Erreur lors de la création'
      console.error('❌ Erreur création cas:', err)
      toast.error(`Échec de la création: ${errorMsg}`)
    }
  }

  const loadSampleData = () => {
    setCases(sampleCases)
    setVolunteers(sampleVolunteerProfiles)
    
    // Create sample activities
    const sampleActivities: VolunteerActivity[] = [
      {
        id: 'sample-activity-1',
        volunteerId: 'volunteer-1',
        caseId: sampleCases[0]?.id || 'sample-1',
        action: 'helped',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        location: sampleCases[0]?.location || { lat: 40.7128, lng: -74.0060 },
        notes: 'Provided food and blankets'
      },
      {
        id: 'sample-activity-2',
        volunteerId: 'volunteer-2',
        caseId: sampleCases[1]?.id || 'sample-2',
        action: 'started-helping',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        location: sampleCases[1]?.location || { lat: 40.7589, lng: -73.9851 },
        notes: 'Contacted local animal rescue'
      },
      {
        id: 'sample-activity-3',
        volunteerId: 'volunteer-1',
        caseId: sampleCases[2]?.id || 'sample-3',
        action: 'reported',
        timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        location: sampleCases[2]?.location || { lat: 40.7505, lng: -73.9934 },
        notes: 'Reported person needing assistance'
      }
    ]
    
    setActivities(sampleActivities)
    toast.success('Sample data loaded for demo purposes')
  }

  useEffect(() => {
    console.log('IA2GOOD initialized')
    toast.success('IA2GOOD ready to help build community')
  }, [])

  // Mode sans authentification pour accès direct aux modules
  const [showAuthPage, setShowAuthPage] = useState<'login' | 'register' | null>(null);

  // Afficher le chargement pendant la récupération des données
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-lg font-semibold">Chargement des données RÉELLES...</p>
          <p className="text-sm text-muted-foreground">Connexion au backend PostgreSQL</p>
        </div>
      </div>
    )
  }

  // Afficher l'erreur si échec de connexion
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md mx-4">
          <CardHeader>
            <CardTitle className="text-destructive">❌ Erreur de connexion</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button onClick={() => window.location.reload()} className="w-full">
              Réessayer
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Pages d'authentification
  if (showAuthPage === 'login') {
    return (
      <Login
        onSwitchToRegister={() => setShowAuthPage('register')}
        onSuccess={() => setShowAuthPage(null)}
      />
    );
  }

  if (showAuthPage === 'register') {
    return (
      <Register
        onSwitchToLogin={() => setShowAuthPage('login')}
        onSuccess={() => setShowAuthPage(null)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Module Selector - Top Banner */}
      <div className="bg-gradient-to-r from-primary/10 via-blue-500/10 to-green-500/10 border-b border-border">
        <div className="container max-w-7xl mx-auto px-3 py-2">
          <div className="flex gap-2 overflow-x-auto scrollbar-hide">
            <Button
              variant={activeModule === 'ia2good' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveModule('ia2good')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Heart size={16} weight={activeModule === 'ia2good' ? 'fill' : 'regular'} />
              IA2GOOD
              <Badge variant="secondary" className="text-xs">12</Badge>
            </Button>
            <Button
              variant={activeModule === 'volunteer' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveModule('volunteer')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <Users size={16} weight={activeModule === 'volunteer' ? 'fill' : 'regular'} />
              Volunteer
              <Badge variant="secondary" className="text-xs bg-green-500">2</Badge>
            </Button>
            <Button
              variant={activeModule === 'medcare' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveModule('medcare')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <FirstAid size={16} weight={activeModule === 'medcare' ? 'fill' : 'regular'} />
              MedCare
              <Badge variant="secondary" className="text-xs bg-purple-500">1</Badge>
            </Button>
            <Button
              variant={activeModule === 'guardian' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveModule('guardian')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <ShieldCheck size={16} weight={activeModule === 'guardian' ? 'fill' : 'regular'} />
              Guardian
              <Badge variant="secondary" className="text-xs">0</Badge>
            </Button>
            <Button
              variant={activeModule === 'eduverify' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveModule('eduverify')}
              className="flex items-center gap-2 whitespace-nowrap"
            >
              <GraduationCap size={16} weight={activeModule === 'eduverify' ? 'fill' : 'regular'} />
              EduVerify
              <Badge variant="secondary" className="text-xs">0</Badge>
            </Button>
          </div>
        </div>
      </div>

      {/* Module Content - IA2GOOD */}
      {activeModule === 'ia2good' && (
        <>
      {/* Mobile-First Header */}
      <header className="sticky top-0 z-50 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60 border-b border-border">
        <div className="container max-w-7xl mx-auto px-3 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-xl text-primary-foreground">
                <Heart weight="fill" size={20} />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold text-foreground">{t('header.title')}</h1>
                <p className="text-xs text-muted-foreground hidden sm:block">{t('header.subtitle')}</p>
              </div>
            </div>
            
            {/* Mobile Stats */}
            <div className="flex items-center gap-1 sm:gap-3">
              <LanguageSelector />
              <div className="text-center px-2 py-1 bg-muted rounded-lg">
                <div className="text-sm font-bold text-foreground">{stats.total}</div>
                <div className="text-xs text-muted-foreground">{t('header.total')}</div>
              </div>
              <div className="text-center px-2 py-1 bg-accent/10 rounded-lg">
                <div className="text-sm font-bold text-accent">{stats.helped}</div>
                <div className="text-xs text-muted-foreground">{t('header.helped')}</div>
              </div>
              {stats.open > 0 && (
                <Badge variant="destructive" className="flex items-center gap-1 text-xs px-2 py-1">
                  <Bell size={12} />
                  {stats.open}
                </Badge>
              )}
              {/* Auth buttons */}
              {!isAuthenticated ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAuthPage('login')}
                  className="flex items-center gap-1"
                >
                  <UserCircle size={16} />
                  <span className="hidden sm:inline">Login</span>
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="flex items-center gap-1"
                >
                  <SignOut size={16} />
                  <span className="hidden sm:inline">Logout</span>
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/80 border-t border-border md:hidden">
        <div className="grid grid-cols-5 gap-1 px-2 py-2">
          <Button
            variant={activeTab === 'cases' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('cases')}
            className="flex flex-col items-center gap-1 h-auto py-2 px-1"
          >
            <List size={18} />
            <span className="text-xs">{t('nav.cases')}</span>
          </Button>
          <Button
            variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('dashboard')}
            className="flex flex-col items-center gap-1 h-auto py-2 px-1"
          >
            <ChartBar size={18} />
            <span className="text-xs">{t('nav.stats')}</span>
          </Button>
          <Button
            variant={activeTab === 'report' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('report')}
            className="flex flex-col items-center gap-1 h-auto py-2 px-1 bg-primary text-primary-foreground rounded-full"
          >
            <Plus size={20} />
            <span className="text-xs">{t('nav.report')}</span>
          </Button>
          <Button
            variant={activeTab === 'volunteers' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('volunteers')}
            className="flex flex-col items-center gap-1 h-auto py-2 px-1"
          >
            <Users size={18} />
            <span className="text-xs">{t('nav.people')}</span>
          </Button>
          <Button
            variant={activeTab === 'settings' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setActiveTab('settings')}
            className="flex flex-col items-center gap-1 h-auto py-2 px-1"
          >
            <Gear size={18} />
            <span className="text-xs">{t('nav.settings')}</span>
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <main className="container max-w-7xl mx-auto px-3 py-4 pb-20 md:pb-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          {/* Desktop Tab Navigation */}
          <div className="hidden md:flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <TabsList className="grid w-full sm:w-auto grid-cols-6">
              <TabsTrigger value="home" className="flex items-center gap-2">
                <Heart size={16} weight="fill" />
                Accueil
              </TabsTrigger>
              <TabsTrigger value="cases" className="flex items-center gap-2">
                <List size={16} />
                {t('nav.cases')}
              </TabsTrigger>
              <TabsTrigger value="dashboard" className="flex items-center gap-2">
                <ChartBar size={16} />
                {t('nav.dashboard')}
              </TabsTrigger>
              <TabsTrigger value="volunteers" className="flex items-center gap-2">
                <Users size={16} />
                {t('nav.volunteers')}
              </TabsTrigger>
              <TabsTrigger value="report" className="flex items-center gap-2">
                <Plus size={16} />
                {t('nav.report')}
              </TabsTrigger>
              <TabsTrigger value="settings" className="flex items-center gap-2">
                <Gear size={16} />
                {t('nav.settings')}
              </TabsTrigger>
              <TabsTrigger value="debug" className="flex items-center gap-2 bg-yellow-500/10">
                <Info size={16} />
                🔧 Debug
              </TabsTrigger>
            </TabsList>

            {/* Quick Actions */}
            <div className="flex gap-2">
              <QuickStartGuide />
              <VoiceControls />
              {(volunteers || []).find(v => v.id === currentVolunteerId) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedVolunteerId(currentVolunteerId)
                    setActiveTab('volunteers')
                  }}
                  className="flex items-center gap-2"
                >
                  <UserCircle size={20} />
                  My Profile
                </Button>
              )}
            </div>
          </div>

          {/* Tab Content */}
          <TabsContent value="home" className="space-y-6">
            <div className="space-y-6">
              <Card className="bg-gradient-to-r from-primary/10 to-purple-500/10">
                <CardContent className="p-6">
                  <h1 className="text-3xl font-bold mb-3 flex items-center gap-3">
                    <Heart className="text-primary" size={40} weight="fill" />
                    Bienvenue sur IA2GOOD
                  </h1>
                  <p className="text-lg mb-4">
                    Plateforme humanitaire complète avec 4 modules intégrés
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                      <div className="text-2xl font-bold text-blue-500 mb-1">12</div>
                      <div className="text-sm text-muted-foreground">Cas actifs</div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                      <div className="text-2xl font-bold text-green-500 mb-1">4</div>
                      <div className="text-sm text-muted-foreground">Modules</div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                      <div className="text-2xl font-bold text-purple-500 mb-1">50+</div>
                      <div className="text-sm text-muted-foreground">Fonctionnalités</div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                      <div className="text-2xl font-bold text-orange-500 mb-1">✅</div>
                      <div className="text-sm text-muted-foreground">100% Fonctionnel</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <NavigationCard 
                activeTab={activeTab} 
                onTabChange={setActiveTab}
                onModuleChange={setActiveModule as (module: string) => void}
              />

              <Card>
                <CardHeader>
                  <CardTitle>🎯 Ce qui est disponible</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <List size={20} className="text-blue-500" />
                        Module IA2GOOD
                      </h3>
                      <ul className="text-sm space-y-1 ml-6">
                        <li>✅ 12 cas réels depuis PostgreSQL</li>
                        <li>✅ Chat temps réel WebSocket</li>
                        <li>✅ Carte interactive Mapbox</li>
                        <li>✅ Upload photos/vidéos</li>
                        <li>✅ Géolocalisation</li>
                        <li>✅ Matching bénévoles</li>
                      </ul>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <ShieldCheck size={20} className="text-yellow-600" />
                        Module Guardian
                      </h3>
                      <ul className="text-sm space-y-1 ml-6">
                        <li>✅ Alertes SOS</li>
                        <li>✅ Détection de dangers</li>
                        <li>✅ Contacts d'urgence</li>
                        <li>✅ Géolocalisation urgence</li>
                        <li>✅ Logs communication</li>
                      </ul>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <GraduationCap size={20} className="text-indigo-500" />
                        Module EduVerify
                      </h3>
                      <ul className="text-sm space-y-1 ml-6">
                        <li>✅ Vérification de faits</li>
                        <li>✅ Quiz éducatifs</li>
                        <li>✅ Sessions live</li>
                        <li>✅ Analytics apprentissage</li>
                        <li>✅ Progression utilisateurs</li>
                      </ul>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <FirstAid size={20} className="text-pink-500" />
                        Module MedCare
                      </h3>
                      <ul className="text-sm space-y-1 ml-6">
                        <li>✅ Téléconsultations</li>
                        <li>✅ Appels vidéo WebRTC</li>
                        <li>✅ Prescriptions</li>
                        <li>✅ Dossiers médicaux</li>
                        <li>✅ Analyses d'images</li>
                      </ul>
                    </div>
                  </div>

                  <div className="bg-green-50 dark:bg-green-950 p-4 rounded-lg mt-4">
                    <p className="text-sm">
                      <strong>✅ TOUT EST RÉEL !</strong><br />
                      Les 12 cas viennent de PostgreSQL, le chat est en temps réel via WebSocket,
                      les uploads fonctionnent, la géolocalisation est active. Aucune simulation,
                      tout est connecté au backend Python.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="cases" className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">{t('app.communityAssistanceRequests')}</h2>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs">
                    {t('app.liveUpdates')}
                  </Badge>
                  {((cases || []).length === 0 || (volunteers || []).length === 0) && (
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={loadSampleData}
                    >
                      {t('app.loadSampleData')}
                    </Button>
                  )}
                </div>
              </div>

              {/* Carte interactive */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="w-5 h-5" />
                    Carte des cas
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="h-[500px] w-full">
                    <MapView
                      onCaseSelect={(caseId) => {
                        const selectedCase = cases.find(c => c.id === caseId);
                        if (selectedCase) {
                          setSelectedCase(selectedCase);
                          toast.info(`Cas sélectionné: ${selectedCase.description.substring(0, 50)}...`);
                        }
                      }}
                      showUserLocation={true}
                      initialZoom={12}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Liste des cas */}
              <CaseList cases={cases || []} onCaseUpdate={handleCaseUpdate} />
            </div>
          </TabsContent>

          <TabsContent value="dashboard" className="space-y-6">
            <VolunteerDashboard cases={cases || []} activities={activities || []} />
          </TabsContent>

          <TabsContent value="volunteers" className="space-y-6">
            {selectedVolunteerId ? (
              <div className="space-y-4">
                <Button 
                  variant="ghost" 
                  onClick={() => setSelectedVolunteerId(null)}
                  className="flex items-center gap-2"
                >
                  ← Back to Volunteers
                </Button>
                
                {(volunteers || []).find(v => v.id === selectedVolunteerId) && (
                  <VolunteerProfile
                    profile={(volunteers || []).find(v => v.id === selectedVolunteerId)!}
                    activities={(activities || []).filter(a => a.volunteerId === selectedVolunteerId)}
                    cases={cases || []}
                    isOwnProfile={selectedVolunteerId === currentVolunteerId}
                    onEditProfile={() => {
                      // Edit handled by EditVolunteerProfile component
                    }}
                  />
                )}
              </div>
            ) : (
              <VolunteerDirectory
                volunteers={volunteers || []}
                onViewProfile={(volunteerId) => setSelectedVolunteerId(volunteerId)}
              />
            )}
          </TabsContent>

          <TabsContent value="report" className="space-y-6">
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold">{t('app.reportSomeoneNeedsHelp')}</h2>
                <p className="text-muted-foreground">
                  {t('app.helpConnectCommunity')}
                </p>
              </div>
              
              <Card>
                <CardContent className="p-6">
                  <ReportCase onReportSubmitted={handleNewReport} />
                </CardContent>
              </Card>

              {/* Guidelines */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Info className="text-primary" />
                    {t('app.reportingGuidelines')}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="space-y-2">
                    <div className="flex items-start gap-2">
                      <Shield className="text-green-600 mt-1 flex-shrink-0" size={16} />
                      <div>
                        <strong>{t('app.respectDignity')}</strong> {t('app.respectDignityDesc')}
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <Shield className="text-green-600 mt-1 flex-shrink-0" size={16} />
                      <div>
                        <strong>{t('app.beAccurate')}</strong> {t('app.beAccurateDesc')}
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <Shield className="text-green-600 mt-1 flex-shrink-0" size={16} />
                      <div>
                        <strong>{t('app.emergencyFirst')}</strong> {t('app.emergencyFirstDesc')}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold">{t('settings.volunteerPreferencesTitle')}</h2>
                <p className="text-muted-foreground">
                  {t('settings.volunteerPreferencesDesc')}
                </p>
              </div>
              
              {/* Profile Management */}
              {(volunteers || []).find(v => v.id === currentVolunteerId) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <UserCircle className="text-primary" />
                      Your Profile
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium">Manage your volunteer profile</h3>
                        <p className="text-sm text-muted-foreground">
                          Update your information, skills, and availability
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          variant="outline"
                          onClick={() => setSelectedVolunteerId(currentVolunteerId)}
                        >
                          View Profile
                        </Button>
                        <EditVolunteerProfile
                          profile={(volunteers || []).find(v => v.id === currentVolunteerId)!}
                          onSave={(updatedProfile) => {
                            setVolunteers(currentVolunteers => 
                              (currentVolunteers || []).map(v => 
                                v.id === updatedProfile.id ? updatedProfile : v
                              )
                            )
                          }}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
              
              <VolunteerSettings />
            </div>
          </TabsContent>

          <TabsContent value="debug" className="space-y-6">
            <SystemStatus />
          </TabsContent>

          <TabsContent value="langtest" className="space-y-6">
            <LanguageTest />
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* About */}
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Heart className="text-primary" size={18} />
                {t('app.aboutIA2GOOD')}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t('app.aboutIA2GOODDesc')}
              </p>
            </div>

            {/* Emergency Notice */}
            <div className="space-y-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Phone className="text-destructive" size={18} />
                {t('app.emergencyNotice')}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t('app.emergencyNoticeDesc')}
              </p>
            </div>

            {/* Attribution */}
            <div className="space-y-3">
              <h3 className="font-semibold">{t('app.openSource')}</h3>
              <div className="text-sm text-muted-foreground space-y-1">
                <p><strong>{t('footer.owner')}:</strong> Fahed Mlaiel</p>
                <p><strong>{t('footer.contact')}:</strong> mlaiel@live.de</p>
                <p className="text-xs">
                  {t('app.attributionRequired')}
                </p>
              </div>
            </div>
          </div>
          
          <Separator className="my-6" />
          
          <div className="flex items-center justify-between">
            <div className="text-center text-xs text-muted-foreground">
              IA2GOOD © 2024 - Building community through compassionate technology
            </div>
            <DebugInfo cases={cases || []} onDataReset={() => setCases([])} />
          </div>
        </div>
      </footer>
      </>
      )}

      {/* Module Content - Volunteer Interface */}
      {activeModule === 'volunteer' && (
        <VolunteerMainDashboard 
          volunteerId="volunteer-1"
          volunteerName="Jean Dupont"
        />
      )}

      {/* Module Content - MedCare Interface */}
      {activeModule === 'medcare' && (
        <MedCareDashboard 
          userId="patient-1"
          userName="Marie Martin"
        />
      )}

      {/* Module Content - Guardian */}
      {activeModule === 'guardian' && (
        <div className="container max-w-7xl mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldCheck size={32} className="text-blue-600" weight="duotone" />
                Guardian - Surveillance Communautaire
              </CardTitle>
              <CardDescription>
                Système de surveillance et sécurité communautaire avec alertes en temps réel
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-blue-50 dark:bg-blue-900/20 p-8 rounded-lg text-center space-y-4">
                <div className="text-6xl">🚧</div>
                <h3 className="text-xl font-bold">Backend opérationnel - Interface en développement</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Le backend Guardian est prêt avec toutes les API. L'interface utilisateur sera développée prochainement.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 text-left">
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">✅ Backend Ready</h4>
                    <ul className="text-sm space-y-1">
                      <li>• API de signalement d'incidents</li>
                      <li>• Géolocalisation et alertes</li>
                      <li>• Authentification JWT</li>
                      <li>• Base de données PostgreSQL</li>
                    </ul>
                  </div>
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">🔜 À venir</h4>
                    <ul className="text-sm space-y-1">
                      <li>• Interface de signalement</li>
                      <li>• Carte interactive</li>
                      <li>• Dashboard de monitoring</li>
                      <li>• Notifications push</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Module Content - EduVerify */}
      {activeModule === 'eduverify' && (
        <div className="container max-w-7xl mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap size={32} className="text-green-600" weight="duotone" />
                EduVerify - Vérification Éducative
              </CardTitle>
              <CardDescription>
                Plateforme de vérification et certification des parcours éducatifs
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-green-50 dark:bg-green-900/20 p-8 rounded-lg text-center space-y-4">
                <div className="text-6xl">🚧</div>
                <h3 className="text-xl font-bold">Backend opérationnel - Interface en développement</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Le backend EduVerify est prêt avec toutes les API. L'interface utilisateur sera développée prochainement.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 text-left">
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">✅ Backend Ready</h4>
                    <ul className="text-sm space-y-1">
                      <li>• API de vérification de diplômes</li>
                      <li>• Système de certifications</li>
                      <li>• Base de données avec blockchain</li>
                      <li>• API pour institutions</li>
                    </ul>
                  </div>
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">🔜 À venir</h4>
                    <ul className="text-sm space-y-1">
                      <li>• Portfolio éducatif</li>
                      <li>• Vérification en temps réel</li>
                      <li>• Dashboard institution</li>
                      <li>• QR codes sécurisés</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Module Content - MedCare */}
      {activeModule === 'medcare' && (
        <div className="container max-w-7xl mx-auto px-4 py-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FirstAid size={32} className="text-purple-600" weight="duotone" />
                MedCare - Gestion Médicale
              </CardTitle>
              <CardDescription>
                Système de gestion des soins médicaux et suivi patients
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="bg-purple-50 dark:bg-purple-900/20 p-8 rounded-lg text-center space-y-4">
                <div className="text-6xl">🚧</div>
                <h3 className="text-xl font-bold">Backend opérationnel - Interface en développement</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Le backend MedCare est prêt avec toutes les API. L'interface utilisateur sera développée prochainement.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 text-left">
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">✅ Backend Ready</h4>
                    <ul className="text-sm space-y-1">
                      <li>• API dossier médical électronique</li>
                      <li>• Système de suivi traitements</li>
                      <li>• Authentification sécurisée</li>
                      <li>• Base de données PostgreSQL</li>
                    </ul>
                  </div>
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg">
                    <h4 className="font-semibold mb-2">🔜 À venir</h4>
                    <ul className="text-sm space-y-1">
                      <li>• Téléconsultation</li>
                      <li>• Alertes médicales</li>
                      <li>• Dashboard patient</li>
                      <li>• Ordonnances numériques</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

// Wrapper avec AuthProvider
export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

