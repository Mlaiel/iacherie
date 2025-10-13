/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useTranslation } from '@/hooks/useTranslation'
import { 
  ChartBar, 
  TrendUp, 
  Target, 
  Clock, 
  Heart,
  Trophy,
  Users,
  Globe
} from '@phosphor-icons/react'

export function DashboardGuide() {
  const { t } = useTranslation();
  const features = [
    {
      icon: <TrendUp className="text-primary" size={20} />,
      title: t('dashboard.impactTracking'),
      description: t('dashboard.impactTrackingDesc')
    },
    {
      icon: <Target className="text-accent" size={20} />,
      title: t('dashboard.weeklyGoals'),
      description: t('dashboard.weeklyGoalsDesc')
    },
    {
      icon: <Clock className="text-green-600" size={20} />,
      title: t('dashboard.activityTimeline'),
      description: t('dashboard.activityTimelineDesc')
    },
    {
      icon: <Trophy className="text-yellow-600" size={20} />,
      title: t('dashboard.achievementStreaks'),
      description: t('dashboard.achievementStreaksDesc')
    },
    {
      icon: <Globe className="text-blue-600" size={20} />,
      title: t('dashboard.communityStats'),
      description: t('dashboard.communityStatsDesc')
    },
    {
      icon: <Users className="text-purple-600" size={20} />,
      title: t('dashboard.volunteerLeaderboard'),
      description: t('dashboard.volunteerLeaderboardDesc')
    }
  ]

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="flex items-center justify-center gap-2">
          <ChartBar className="text-primary" size={32} />
          <h2 className="text-2xl font-bold">{t('dashboard.title')}</h2>
        </div>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          {t('dashboard.description')}
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {features.map((feature, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-muted flex items-center justify-center">
                  {feature.icon}
                </div>
                <div className="space-y-1">
                  <h3 className="font-semibold text-foreground">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="text-accent" />
            {t('dashboard.gettingStarted')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Badge variant="secondary" className="flex-shrink-0">1</Badge>
              <div>
                <p className="font-medium">{t('dashboard.step1Title')}</p>
                <p className="text-sm text-muted-foreground">{t('dashboard.step1Desc')}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="secondary" className="flex-shrink-0">2</Badge>
              <div>
                <p className="font-medium">{t('dashboard.step2Title')}</p>
                <p className="text-sm text-muted-foreground">{t('dashboard.step2Desc')}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="secondary" className="flex-shrink-0">3</Badge>
              <div>
                <p className="font-medium">{t('dashboard.step3Title')}</p>
                <p className="text-sm text-muted-foreground">{t('dashboard.step3Desc')}</p>
              </div>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <div className="flex items-start gap-2">
              <Heart className="text-primary flex-shrink-0 mt-1" size={16} />
              <div className="text-sm">
                <p className="font-medium text-foreground">{t('dashboard.everyActionCounts')}</p>
                <p className="text-muted-foreground">
                  {t('dashboard.rippleEffect')}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}