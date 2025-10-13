'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Globe, Search, Check, Sparkles, Mic } from 'lucide-react';

interface Language {
  code: string;
  name: string;
  nativeName: string;
  provider: 'deepl' | 'google' | 'libretranslate';
  voiceSupport?: boolean;
  region?: string;
}

interface LanguageSelectorProps {
  currentLanguage?: string;
  onLanguageChange?: (langCode: string) => void;
  showVoiceOnly?: boolean;
  className?: string;
}

export default function LanguageSelector({
  currentLanguage = 'EN',
  onLanguageChange,
  showVoiceOnly = false,
  className = ''
}: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [languages, setLanguages] = useState<Language[]>([]);
  const [filteredLanguages, setFilteredLanguages] = useState<Language[]>([]);
  const [selectedLang, setSelectedLang] = useState(currentLanguage);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Charger les langues depuis le backend
  useEffect(() => {
    async function loadLanguages() {
      try {
        // Fallback si API pas disponible - langues populaires
        const popularLanguages: Language[] = [
          { code: 'EN', name: 'English', nativeName: 'English', provider: 'deepl', voiceSupport: true },
          { code: 'FR', name: 'French', nativeName: 'Français', provider: 'deepl', voiceSupport: true },
          { code: 'ES', name: 'Spanish', nativeName: 'Español', provider: 'deepl', voiceSupport: true },
          { code: 'DE', name: 'German', nativeName: 'Deutsch', provider: 'deepl', voiceSupport: true },
          { code: 'IT', name: 'Italian', nativeName: 'Italiano', provider: 'deepl', voiceSupport: true },
          { code: 'PT', name: 'Portuguese', nativeName: 'Português', provider: 'deepl', voiceSupport: true },
          { code: 'RU', name: 'Russian', nativeName: 'Русский', provider: 'deepl', voiceSupport: true },
          { code: 'ZH', name: 'Chinese', nativeName: '中文', provider: 'deepl', voiceSupport: true },
          { code: 'JA', name: 'Japanese', nativeName: '日本語', provider: 'deepl', voiceSupport: true },
          { code: 'KO', name: 'Korean', nativeName: '한국어', provider: 'deepl', voiceSupport: true },
          { code: 'AR', name: 'Arabic', nativeName: 'العربية', provider: 'deepl', voiceSupport: true },
          { code: 'HI', name: 'Hindi', nativeName: 'हिन्दी', provider: 'google', voiceSupport: true },
          { code: 'NL', name: 'Dutch', nativeName: 'Nederlands', provider: 'deepl', voiceSupport: true },
          { code: 'PL', name: 'Polish', nativeName: 'Polski', provider: 'deepl', voiceSupport: true },
          { code: 'TR', name: 'Turkish', nativeName: 'Türkçe', provider: 'deepl', voiceSupport: true },
          { code: 'SV', name: 'Swedish', nativeName: 'Svenska', provider: 'deepl', voiceSupport: true },
          { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', provider: 'google' },
          { code: 'sq', name: 'Albanian', nativeName: 'Shqip', provider: 'google' },
          { code: 'am', name: 'Amharic', nativeName: 'አማርኛ', provider: 'google' },
          { code: 'hy', name: 'Armenian', nativeName: 'Հայերեն', provider: 'google' },
          { code: 'az', name: 'Azerbaijani', nativeName: 'Azərbaycan', provider: 'google' },
          { code: 'eu', name: 'Basque', nativeName: 'Euskara', provider: 'google' },
          { code: 'be', name: 'Belarusian', nativeName: 'Беларуская', provider: 'google' },
          { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', provider: 'google' },
          { code: 'bs', name: 'Bosnian', nativeName: 'Bosanski', provider: 'google' },
          { code: 'ca', name: 'Catalan', nativeName: 'Català', provider: 'google' },
          { code: 'hr', name: 'Croatian', nativeName: 'Hrvatski', provider: 'google' },
          { code: 'eo', name: 'Esperanto', nativeName: 'Esperanto', provider: 'google' },
          { code: 'tl', name: 'Filipino', nativeName: 'Filipino', provider: 'google' },
          { code: 'ka', name: 'Georgian', nativeName: 'ქართული', provider: 'google' },
          { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', provider: 'google', voiceSupport: true },
          { code: 'ha', name: 'Hausa', nativeName: 'Hausa', provider: 'google' },
          { code: 'iw', name: 'Hebrew', nativeName: 'עברית', provider: 'google' },
          { code: 'is', name: 'Icelandic', nativeName: 'Íslenska', provider: 'google' },
          { code: 'ga', name: 'Irish', nativeName: 'Gaeilge', provider: 'google' },
          { code: 'jw', name: 'Javanese', nativeName: 'Basa Jawa', provider: 'google' },
          { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', provider: 'google', voiceSupport: true },
          { code: 'km', name: 'Khmer', nativeName: 'ខ្មែរ', provider: 'google' },
          { code: 'ku', name: 'Kurdish', nativeName: 'Kurdî', provider: 'google' },
          { code: 'lo', name: 'Lao', nativeName: 'ລາວ', provider: 'google' },
          { code: 'la', name: 'Latin', nativeName: 'Latina', provider: 'google' },
          { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', provider: 'google', voiceSupport: true },
          { code: 'mr', name: 'Marathi', nativeName: 'मराठी', provider: 'google', voiceSupport: true },
          { code: 'mn', name: 'Mongolian', nativeName: 'Монгол', provider: 'google' },
          { code: 'my', name: 'Myanmar', nativeName: 'မြန်မာ', provider: 'google' },
          { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', provider: 'google' },
          { code: 'ps', name: 'Pashto', nativeName: 'پښتو', provider: 'google' },
          { code: 'fa', name: 'Persian', nativeName: 'فارسی', provider: 'google' },
          { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', provider: 'google', voiceSupport: true },
          { code: 'sr', name: 'Serbian', nativeName: 'Српски', provider: 'google' },
          { code: 'si', name: 'Sinhala', nativeName: 'සිංහල', provider: 'google' },
          { code: 'so', name: 'Somali', nativeName: 'Soomaali', provider: 'google' },
          { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', provider: 'google', voiceSupport: true },
          { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', provider: 'google', voiceSupport: true },
          { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', provider: 'google', voiceSupport: true },
          { code: 'th', name: 'Thai', nativeName: 'ไทย', provider: 'google', voiceSupport: true },
          { code: 'uk', name: 'Ukrainian', nativeName: 'Українська', provider: 'deepl' },
          { code: 'uz', name: 'Uzbek', nativeName: 'Oʻzbek', provider: 'google' },
          { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', provider: 'google', voiceSupport: true },
          { code: 'cy', name: 'Welsh', nativeName: 'Cymraeg', provider: 'google', voiceSupport: true },
          { code: 'xh', name: 'Xhosa', nativeName: 'isiXhosa', provider: 'google' },
          { code: 'yi', name: 'Yiddish', nativeName: 'ייִדיש', provider: 'google' },
          { code: 'yo', name: 'Yoruba', nativeName: 'Yorùbá', provider: 'google' },
          { code: 'zu', name: 'Zulu', nativeName: 'isiZulu', provider: 'google' },
        ];

        setLanguages(popularLanguages);
        setFilteredLanguages(showVoiceOnly 
          ? popularLanguages.filter(l => l.voiceSupport) 
          : popularLanguages
        );
      } catch (error) {
        console.error('Failed to load languages:', error);
      }
    }

    loadLanguages();
  }, [showVoiceOnly]);

  // Filtrer les langues selon la recherche
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredLanguages(showVoiceOnly 
        ? languages.filter(l => l.voiceSupport)
        : languages
      );
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = languages.filter(lang => 
      (lang.name.toLowerCase().includes(query) ||
       lang.nativeName.toLowerCase().includes(query) ||
       lang.code.toLowerCase().includes(query)) &&
      (!showVoiceOnly || lang.voiceSupport)
    );
    setFilteredLanguages(filtered);
  }, [searchQuery, languages, showVoiceOnly]);

  // Fermer le dropdown quand on clique dehors
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleSelectLanguage = (langCode: string) => {
    setSelectedLang(langCode);
    onLanguageChange?.(langCode);
    setIsOpen(false);
    setSearchQuery('');
  };

  const getCurrentLanguage = () => {
    return languages.find(l => l.code === selectedLang) || languages[0];
  };

  const getProviderBadge = (provider: string) => {
    const badges = {
      deepl: { text: 'Premium', color: 'bg-purple-100 text-purple-700' },
      google: { text: 'Standard', color: 'bg-blue-100 text-blue-700' },
      libretranslate: { text: 'Open', color: 'bg-green-100 text-green-700' }
    };
    return badges[provider as keyof typeof badges] || badges.google;
  };

  const currentLang = getCurrentLanguage();

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      {/* Bouton principal */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
      >
        <Globe className="w-5 h-5 text-blue-600" />
        <span className="font-medium text-gray-900">
          {currentLang?.nativeName || 'Select Language'}
        </span>
        <span className="text-xs text-gray-500 uppercase">{selectedLang}</span>
        {currentLang?.voiceSupport && (
          <Mic className="w-4 h-4 text-green-500" />
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white border border-gray-200 rounded-xl shadow-2xl z-50 max-h-[600px] overflow-hidden">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Globe className="w-6 h-6" />
                <h3 className="font-bold text-lg">Select Language</h3>
              </div>
              <div className="flex items-center gap-1 px-2 py-1 bg-white/20 rounded-full text-xs font-semibold">
                <Sparkles className="w-3 h-3" />
                644+ Languages
              </div>
            </div>
            
            {/* Barre de recherche */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or native name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/30"
              />
            </div>

            {showVoiceOnly && (
              <div className="mt-2 flex items-center gap-1 text-xs">
                <Mic className="w-3 h-3" />
                <span>Showing only languages with voice support</span>
              </div>
            )}
          </div>

          {/* Liste des langues */}
          <div className="overflow-y-auto max-h-[400px] p-2">
            {filteredLanguages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No languages found</p>
                <p className="text-sm">Try a different search term</p>
              </div>
            ) : (
              <div className="space-y-1">
                {filteredLanguages.map((lang) => {
                  const badge = getProviderBadge(lang.provider);
                  const isSelected = lang.code === selectedLang;

                  return (
                    <button
                      key={lang.code}
                      onClick={() => handleSelectLanguage(lang.code)}
                      className={`w-full flex items-center justify-between p-3 rounded-lg transition-all ${
                        isSelected
                          ? 'bg-blue-50 border-2 border-blue-500'
                          : 'hover:bg-gray-50 border-2 border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}>
                          {lang.code.substring(0, 2).toUpperCase()}
                        </div>
                        
                        <div className="text-left flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="font-semibold text-gray-900 truncate">
                              {lang.name}
                            </p>
                            {lang.voiceSupport && (
                              <Mic className="w-3 h-3 text-green-500 flex-shrink-0" />
                            )}
                          </div>
                          <p className="text-sm text-gray-500 truncate">
                            {lang.nativeName}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${badge.color}`}>
                          {badge.text}
                        </span>
                        {isSelected && (
                          <Check className="w-5 h-5 text-blue-600" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-3 bg-gray-50 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-600">
              <span>{filteredLanguages.length} languages available</span>
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                  DeepL
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  Google
                </span>
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  LibreTranslate
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
