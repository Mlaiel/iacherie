/**
 * Menu de navigation clair avec icônes et descriptions
 */
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  List,
  ChartBar,
  Users,
  Plus,
  Gear,
  MapPin,
  ChatCircle,
  Heart,
  ShieldCheck,
  GraduationCap,
  FirstAid,
} from '@phosphor-icons/react';

interface NavigationCardProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  onModuleChange?: (module: string) => void;
}

export function NavigationCard({ activeTab, onTabChange, onModuleChange }: NavigationCardProps) {
  const modules = [
    {
      id: 'cases',
      icon: List,
      title: 'Liste des Cas',
      description: '12 cas actifs',
      color: 'text-blue-500',
      badge: '12',
    },
    {
      id: 'dashboard',
      icon: ChartBar,
      title: 'Dashboard',
      description: 'Statistiques et graphiques',
      color: 'text-green-500',
      badge: 'Stats',
    },
    {
      id: 'volunteers',
      icon: Users,
      title: 'Bénévoles',
      description: 'Annuaire et profils',
      color: 'text-purple-500',
      badge: 'Pro',
    },
    {
      id: 'report',
      icon: Plus,
      title: 'Signaler un Cas',
      description: 'Créer un nouveau cas',
      color: 'text-red-500',
      badge: 'Nouveau',
    },
    {
      id: 'map',
      icon: MapPin,
      title: 'Carte Interactive',
      description: '12 marqueurs géolocalisés',
      color: 'text-orange-500',
      badge: 'Carte',
    },
    {
      id: 'chat',
      icon: ChatCircle,
      title: 'Chat Temps Réel',
      description: 'WebSocket actif',
      color: 'text-cyan-500',
      badge: 'Live',
    },
  ];

  const extraModules = [
    {
      id: 'medcare',
      icon: FirstAid,
      title: 'MedCare AI',
      description: 'Téléconsultations + Vidéo',
      color: 'text-pink-500',
      badge: 'Vidéo',
    },
    {
      id: 'guardian',
      icon: ShieldCheck,
      title: 'Guardian',
      description: 'Sécurité et SOS',
      color: 'text-yellow-600',
      badge: 'SOS',
    },
    {
      id: 'eduverify',
      icon: GraduationCap,
      title: 'EduVerify',
      description: 'Vérification éducation',
      color: 'text-indigo-500',
      badge: 'Quiz',
    },
  ];

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Heart className="text-primary" weight="fill" />
              Navigation Principale
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {modules.map((module) => {
                const Icon = module.icon;
                const isActive = activeTab === module.id;
                return (
                  <button
                    key={module.id}
                    onClick={() => onTabChange(module.id)}
                    className={`
                      flex items-start gap-3 p-4 rounded-lg border-2 transition-all
                      ${
                        isActive
                          ? 'bg-primary/10 border-primary shadow-md'
                          : 'bg-card border-border hover:border-primary/50 hover:shadow'
                      }
                    `}
                  >
                    <Icon
                      size={32}
                      className={module.color}
                      weight={isActive ? 'fill' : 'regular'}
                    />
                    <div className="flex-1 text-left">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-sm">{module.title}</h4>
                        {module.badge && (
                          <Badge variant={isActive ? 'default' : 'secondary'} className="text-xs">
                            {module.badge}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">{module.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-lg font-semibold mb-2">Modules Additionnels (Cliquez en haut pour changer)</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {extraModules.map((module) => {
                const Icon = module.icon;
                return (
                  <button
                    key={module.id}
                    onClick={() => onModuleChange && onModuleChange(module.id)}
                    className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:border-primary/50 hover:shadow transition-all"
                  >
                    <Icon size={24} className={module.color} />
                    <div className="flex-1 text-left">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-semibold text-sm">{module.title}</h4>
                        {module.badge && (
                          <Badge variant="secondary" className="text-xs">
                            {module.badge}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground">{module.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="bg-blue-50 dark:bg-blue-950 p-3 rounded-lg">
            <p className="text-sm">
              <strong>💡 Astuce:</strong> Cliquez sur une carte ci-dessus pour accéder aux
              différentes sections. Vous pouvez aussi utiliser les onglets en haut de la page.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
