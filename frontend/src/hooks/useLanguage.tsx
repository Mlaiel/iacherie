import { useState, useEffect, createContext, useContext, ReactNode } from 'react';

// Supported languages
export type Language = 'en' | 'fr' | 'de' | 'ar' | 'ber';

interface TranslationMap {
  [key: string]: string;
}

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  availableLanguages: { code: Language; name: string; nativeName: string }[];
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

// Language configurations
const LANGUAGES = [
  { code: 'en' as Language, name: 'English', nativeName: 'English' },
  { code: 'fr' as Language, name: 'French', nativeName: 'Français' },
  { code: 'de' as Language, name: 'German', nativeName: 'Deutsch' },
  { code: 'ar' as Language, name: 'Arabic', nativeName: 'العربية' },
  { code: 'ber' as Language, name: 'Berber', nativeName: 'Tamaziɣt' },
];

// RTL languages
const RTL_LANGUAGES: Language[] = ['ar', 'ber'];

// Load translation function
async function loadTranslations(language: Language): Promise<TranslationMap> {
  try {
    const translations = await import(`../locales/${language}.json`);
    return translations.default || translations;
  } catch (error) {
    console.warn(`Failed to load translations for ${language}, falling back to English`);
    const fallbackTranslations = await import('../locales/en.json');
    return fallbackTranslations.default || fallbackTranslations;
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

  const t = (key: string): string => {
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