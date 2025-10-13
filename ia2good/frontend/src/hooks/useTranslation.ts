/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState, useEffect } from 'react';
import { 
  getCurrentLanguage, 
  setCurrentLanguage, 
  initializeLanguage, 
  loadTranslations, 
  t as translate,
  SupportedLanguage,
  formatTimeAgo as formatTimeAgoI18n
} from '@/lib/i18n';

export function useTranslation() {
  const [currentLanguage, setCurrentLanguageState] = useState<SupportedLanguage>(getCurrentLanguage());
  const [isLoading, setIsLoading] = useState(true);
  const [triggerReload, setTriggerReload] = useState(0);
  const [forceRender, setForceRender] = useState(0); // Force component re-render

  useEffect(() => {
    const initialize = async () => {
      console.log('🔥 [DEBUG] Initializing translations...');
      setIsLoading(true);
      initializeLanguage();
      const currentLang = getCurrentLanguage();
      console.log('🔥 [DEBUG] Current language:', currentLang);
      setCurrentLanguageState(currentLang);
      await loadTranslations();
      console.log('🔥 [DEBUG] Translations loaded');
      setIsLoading(false);
      setForceRender(prev => prev + 1); // Force re-render after load
    };
    
    initialize();
  }, [triggerReload]);

  const changeLanguage = async (newLanguage: SupportedLanguage) => {
    console.log('🔥 [DEBUG] Changing language to:', newLanguage);
    setCurrentLanguage(newLanguage);
    setCurrentLanguageState(newLanguage);
    // Reload translations to ensure the i18n system is updated
    await loadTranslations();
    console.log('🔥 [DEBUG] Language changed and translations reloaded');
    // Force re-render of all components using this hook
    setForceRender(prev => prev + 1);
    // Trigger a reload of the hook state
    setTriggerReload(prev => prev + 1);
  };

  const t = (key: string): string => {
    // Access forceRender to make this function reactive to language changes
    void forceRender;
    if (isLoading) return key;
    return translate(key);
  };

  const formatTimeAgo = (timestamp: string): string => {
    if (isLoading) return timestamp;
    return formatTimeAgoI18n(timestamp, currentLanguage);
  };

  return {
    t,
    currentLanguage,
    changeLanguage,
    isLoading,
    formatTimeAgo,
  };
}

// Also export the translation function for use outside components
export { t as translate } from '@/lib/i18n';
