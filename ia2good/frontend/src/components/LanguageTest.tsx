/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import React from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { LanguageSelector } from './LanguageSelector';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function LanguageTest() {
  const { t, currentLanguage, isLoading } = useTranslation();

  return (
    <div className="container mx-auto p-4">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Language Test Component</CardTitle>
          <p className="text-sm text-muted-foreground">
            Current Language: <strong>{currentLanguage}</strong> | Loading: {isLoading ? 'Yes' : 'No'}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">Language Selector:</h3>
            <LanguageSelector />
          </div>
          
          <div className="space-y-2">
            <h3 className="font-semibold">Translation Tests:</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>nav.dashboard:</div>
              <div className="font-mono">{t('nav.dashboard')}</div>
              
              <div>nav.volunteers:</div>
              <div className="font-mono">{t('nav.volunteers')}</div>
              
              <div>nav.settings:</div>
              <div className="font-mono">{t('nav.settings')}</div>
              
              <div>common.save:</div>
              <div className="font-mono">{t('common.save')}</div>
              
              <div>common.cancel:</div>
              <div className="font-mono">{t('common.cancel')}</div>
              
              <div>header.title:</div>
              <div className="font-mono">{t('header.title')}</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
