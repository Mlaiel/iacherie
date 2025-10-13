/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Gear, Bell, BellSlash } from '@phosphor-icons/react';
import { LanguageSelector } from './LanguageSelector';
import { useTranslation } from '@/hooks/useTranslation';
import { useState } from 'react';

export function VolunteerSettings() {
  const { t } = useTranslation();
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  
  return (
    <div className="space-y-6">
      {/* Language and General Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gear className="text-primary" />
            {t('settings.preferences')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label className="font-medium">{t('settings.language')}</Label>
            <LanguageSelector />
          </div>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="text-primary" />
            {t('settings.notifications')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="font-medium">{t('settings.enableNotifications')}</Label>
              <p className="text-sm text-muted-foreground">
                {t('settings.enableNotificationsDesc')}
              </p>
            </div>
            <Switch
              checked={notificationsEnabled}
              onCheckedChange={setNotificationsEnabled}
              aria-label={t('settings.enableNotificationsAriaLabel')}
            />
          </div>

          {notificationsEnabled && (
            <>
              <Separator />
              <div className="space-y-3">
                <Label className="font-medium">{t('settings.notificationSettings')}</Label>
                <p className="text-sm text-muted-foreground">
                  {t('settings.notificationSettingsDesc')}
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardContent className="pt-6">
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2">
              {notificationsEnabled ? (
                <Bell className="text-green-600" size={20} />
              ) : (
                <BellSlash className="text-muted-foreground" size={20} />
              )}
              <span className="font-medium">
                                {notificationsEnabled ? t('settings.readyToHelp') : t('settings.notificationsDisabled')}
              </span>
            </div>
            {notificationsEnabled && (
              <p className="text-sm text-muted-foreground">
                {t('settings.notificationSettingsDesc')}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
