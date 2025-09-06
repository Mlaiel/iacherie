import { useState, useEffect, createContext, useContext, ReactNode } from 'react';

/*
 * Professional Multilingual Support System
 * ========================================
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: © 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ PROPRIETARY SOFTWARE - ALL RIGHTS RESERVED ⚠️
 * This modular translation system supports 10 languages with professional-grade
 * gamification and remix modules for the IA Influencer Agent platform.
 */

// Supported languages - Extended to 10 professional languages
export type Language = 'en' | 'fr' | 'de' | 'es' | 'it' | 'pt' | 'ru' | 'zh' | 'ja' | 'ar';

interface TranslationMap {
  [key: string]: string;
}

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, module?: 'common' | 'gamification' | 'remix') => string;
  availableLanguages: { code: Language; name: string; nativeName: string }[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Professional language configurations
const LANGUAGES = [
  { code: 'en' as Language, name: 'English', nativeName: 'English' },
  { code: 'fr' as Language, name: 'French', nativeName: 'Français' },
  { code: 'de' as Language, name: 'German', nativeName: 'Deutsch' },
  { code: 'es' as Language, name: 'Spanish', nativeName: 'Español' },
  { code: 'it' as Language, name: 'Italian', nativeName: 'Italiano' },
  { code: 'pt' as Language, name: 'Portuguese', nativeName: 'Português' },
  { code: 'ru' as Language, name: 'Russian', nativeName: 'Русский' },
  { code: 'zh' as Language, name: 'Chinese', nativeName: '中文' },
  { code: 'ja' as Language, name: 'Japanese', nativeName: '日本語' },
  { code: 'ar' as Language, name: 'Arabic', nativeName: 'العربية' },
];

// RTL languages
const RTL_LANGUAGES: Language[] = ['ar'];

// Modular translation loading function
async function loadTranslations(language: Language): Promise<TranslationMap> {
  try {
    // Load all three modules: common, gamification, remix
    const [commonModule, gamificationModule, remixModule] = await Promise.all([
      import(`../locales/${language}/common.json`).catch(() => 
        import(`../locales/${language}.json`).catch(() => null)
      ),
      import(`../locales/${language}/gamification.json`).catch(() => null),
      import(`../locales/${language}/remix.json`).catch(() => null)
    ]);

    // Combine all translations with module prefixes for organization
    const allTranslations: TranslationMap = {};
    
    // Add common translations (no prefix for backward compatibility)
    if (commonModule) {
      const commonData = commonModule.default || commonModule;
      Object.assign(allTranslations, commonData);
    }
    
    // Add gamification translations with prefix
    if (gamificationModule) {
      const gamificationData = gamificationModule.default || gamificationModule;
      Object.keys(gamificationData).forEach(key => {
        allTranslations[`gamification.${key}`] = gamificationData[key];
        allTranslations[key] = gamificationData[key]; // Also add without prefix for convenience
      });
    }
    
    // Add remix translations with prefix
    if (remixModule) {
      const remixData = remixModule.default || remixModule;
      Object.keys(remixData).forEach(key => {
        allTranslations[`remix.${key}`] = remixData[key];
        allTranslations[key] = remixData[key]; // Also add without prefix for convenience
      });
    }

    return allTranslations;
  } catch (_error) {
    console.warn(`Failed to load translations for ${language}, falling back to English`);
    try {
      // Fallback to English with modular structure
      const [commonModule, gamificationModule, remixModule] = await Promise.all([
        import('../locales/en/common.json').catch(() => import('../locales/en.json')),
        import('../locales/en/gamification.json').catch(() => null),
        import('../locales/en/remix.json').catch(() => null)
      ]);
      
      const fallbackTranslations: TranslationMap = {};
      
      if (commonModule) {
        Object.assign(fallbackTranslations, commonModule.default || commonModule);
      }
      
      if (gamificationModule) {
        const gamificationData = gamificationModule.default || gamificationModule;
        Object.keys(gamificationData).forEach(key => {
          fallbackTranslations[`gamification.${key}`] = (gamificationData as any)[key];
          fallbackTranslations[key] = (gamificationData as any)[key];
        });
      }
      
      if (remixModule) {
        const remixData = remixModule.default || remixModule;
        Object.keys(remixData).forEach(key => {
          fallbackTranslations[`remix.${key}`] = (remixData as any)[key];
          fallbackTranslations[key] = (remixData as any)[key];
        });
      }
      
      return fallbackTranslations;
    } catch (fallbackError) {
      console.error('Failed to load fallback translations:', fallbackError);
      return {};
    }
  }
}

// Language Provider Component
interface LanguageProviderProps {
  children: ReactNode;
  defaultLanguage?: Language;
}

export function LanguageProvider({ children, defaultLanguage = 'en' }: LanguageProviderProps) {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);
  const [translations, setTranslations] = useState<TranslationMap>({});
  const [isLoading, setIsLoading] = useState(true);

  // Initialize language from localStorage or browser
  useEffect(() => {
    const initializeLanguage = () => {
      // Check localStorage first
      const savedLanguage = localStorage.getItem('ainflue-language') as Language;
      if (savedLanguage && LANGUAGES.some(lang => lang.code === savedLanguage)) {
        setLanguageState(savedLanguage);
        return savedLanguage;
      }

      // Detect from browser
      const browserLanguage = navigator.language.split('-')[0] as Language;
      if (LANGUAGES.some(lang => lang.code === browserLanguage)) {
        setLanguageState(browserLanguage);
        return browserLanguage;
      }

      // Default to English
      return defaultLanguage;
    };

    const initialLanguage = initializeLanguage();
    loadTranslations(initialLanguage).then(trans => {
      setTranslations(trans);
      setIsLoading(false);
    });
  }, [defaultLanguage]);

  // Load translations when language changes
  useEffect(() => {
    if (language) {
      setIsLoading(true);
      loadTranslations(language).then(trans => {
        setTranslations(trans);
        setIsLoading(false);
        
        // Save to localStorage
        localStorage.setItem('ainflue-language', language);
        
        // Update document direction for RTL languages
        document.documentElement.dir = RTL_LANGUAGES.includes(language) ? 'rtl' : 'ltr';
        document.documentElement.lang = language;
      });
    }
  }, [language]);

  const setLanguage = (newLanguage: Language) => {
    setLanguageState(newLanguage);
  };

  const t = (key: string, module?: 'common' | 'gamification' | 'remix'): string => {
    // If module is specified, try module-prefixed key first
    if (module && module !== 'common') {
      const moduleKey = `${module}.${key}`;
      if (translations[moduleKey]) {
        return translations[moduleKey];
      }
    }
    
    // Fallback to direct key lookup
    return translations[key] || key;
  };

  const contextValue: LanguageContextType = {
    language,
    setLanguage,
    t,
    availableLanguages: LANGUAGES,
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

// Hook to use language context
export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// Utility functions
export function isRTL(language: Language): boolean {
  return RTL_LANGUAGES.includes(language);
}

export function getLanguageName(code: Language): string {
  const lang = LANGUAGES.find(l => l.code === code);
  return lang?.name || code;
}

export function getNativeLanguageName(code: Language): string {
  const lang = LANGUAGES.find(l => l.code === code);
  return lang?.nativeName || code;
}