/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useTranslation } from '@/hooks/useTranslation';
import { 
  Heart, 
  MapPin, 
  Plus, 
  Bell, 
  CheckCircle, 
  Info,
  PhoneCall,
  Users
} from '@phosphor-icons/react';

export function QuickStartGuide() {
  const { t } = useTranslation();
  const steps = [
    {
      icon: MapPin,
      title: t('quickStart.steps.seeNeedsHelp'),
      description: t('quickStart.steps.seeNeedsHelpDesc'),
      action: t('quickStart.steps.reportLocation'),
      color: "primary"
    },
    {
      icon: Bell,
      title: t('quickStart.steps.wantToHelp'),
      description: t('quickStart.steps.wantToHelpDesc'),
      action: t('quickStart.steps.configureSettings'),
      color: "accent"
    },
    {
      icon: Users,
      title: t('quickStart.steps.respondToRequests'),
      description: t('quickStart.steps.respondToRequestsDesc'),
      action: t('quickStart.steps.browseCases'),
      color: "success"
    },
    {
      icon: CheckCircle,
      title: t('quickStart.steps.makeDifference'),
      description: t('quickStart.steps.makeDifferenceDesc'),
      action: t('quickStart.steps.trackImpact'),
      color: "success"
    }
  ];

  const emergencyInfo = [
    {
      situation: t('quickStart.emergency.medical'),
      action: t('quickStart.emergency.medicalAction'),
      note: t('quickStart.emergency.medicalNote')
    },
    {
      situation: t('quickStart.emergency.weather'),
      action: t('quickStart.emergency.weatherAction'),
      note: t('quickStart.emergency.weatherNote')
    },
    {
      situation: t('quickStart.emergency.mental'),
      action: t('quickStart.emergency.mentalAction'),
      note: t('quickStart.emergency.mentalNote')
    },
    {
      situation: t('quickStart.emergency.animal'),
      action: t('quickStart.emergency.animalAction'),
      note: t('quickStart.emergency.animalNote')
    }
  ];

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Info className="mr-2" size={16} />
          {t('quickStart.quickStartGuide')}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Heart className="text-primary" weight="fill" />
            {t('quickStart.howItWorks')}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Steps */}
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={index} className="flex gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    step.color === 'primary' ? 'bg-primary text-primary-foreground' :
                    step.color === 'accent' ? 'bg-accent text-accent-foreground' :
                    'bg-green-600 text-white'
                  }`}>
                    <step.icon size={20} />
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">{step.title}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{step.description}</p>
                  <Badge variant="outline" className="text-xs">
                    {step.action}
                  </Badge>
                </div>
              </div>
            ))}
          </div>

          {/* Emergency Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <PhoneCall className="text-destructive" />
                {t('quickStart.emergency.title')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground mb-3">
                {t('quickStart.emergency.description')}
              </p>
              
              <div className="space-y-3">
                {emergencyInfo.map((item, index) => (
                  <div key={index} className="border-l-4 border-destructive pl-3">
                    <div className="font-medium text-sm">{item.situation}</div>
                    <div className="text-sm text-muted-foreground">{item.action}</div>
                    <div className="text-xs text-muted-foreground italic">{item.note}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Community Guidelines */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('quickStart.guidelines.title')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={16} />
                <span><strong>{t('quickStart.guidelines.respectDignity')}</strong> {t('quickStart.guidelines.respectDignityDesc')}</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={16} />
                <span><strong>{t('quickStart.guidelines.prioritizeSafety')}</strong> {t('quickStart.guidelines.prioritizeSafetyDesc')}</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={16} />
                <span><strong>{t('quickStart.guidelines.beAccurate')}</strong> {t('quickStart.guidelines.beAccurateDesc')}</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={16} />
                <span><strong>{t('quickStart.guidelines.followThrough')}</strong> {t('quickStart.guidelines.followThroughDesc')}</span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={16} />
                <span><strong>{t('quickStart.guidelines.knowLimits')}</strong> {t('quickStart.guidelines.knowLimitsDesc')}</span>
              </div>
            </CardContent>
          </Card>

          {/* What You Can Do */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">{t('quickStart.help.title')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div className="space-y-1">
                  <div className="font-medium">{t('quickStart.forPeople')}</div>
                  <ul className="text-muted-foreground space-y-1">
                    <li>{t('quickStart.help.peopleFood')}</li>
                    <li>{t('quickStart.help.peopleClothing')}</li>
                    <li>{t('quickStart.help.peopleHygiene')}</li>
                    <li>{t('quickStart.help.peopleInfo')}</li>
                    <li>{t('quickStart.help.peopleTransport')}</li>
                  </ul>
                </div>
                <div className="space-y-1">
                  <div className="font-medium">{t('quickStart.forAnimals')}</div>
                  <ul className="text-muted-foreground space-y-1">
                    <li>{t('quickStart.help.animalFood')}</li>
                    <li>{t('quickStart.help.animalShelter')}</li>
                    <li>{t('quickStart.help.animalVet')}</li>
                    <li>{t('quickStart.help.animalTransport')}</li>
                    <li>{t('quickStart.help.animalControl')}</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}