/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Globe, Check } from '@phosphor-icons/react';
import { 
  supportedLanguages, 
  SupportedLanguage,
} from '@/lib/i18n';
import { useTranslation } from '@/hooks/useTranslation';

interface LanguageSelectorProps {
  onLanguageChange?: (language: SupportedLanguage) => void;
}

export function LanguageSelector({ onLanguageChange }: LanguageSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { currentLanguage, changeLanguage, t } = useTranslation();
  const currentLanguageInfo = supportedLanguages.find(l => l.code === currentLanguage);

  const handleLanguageChange = async (langCode: SupportedLanguage) => {
    await changeLanguage(langCode);
    onLanguageChange?.(langCode);
    setIsOpen(false);
  };

  // Group languages by region for better organization
  const languageGroups = {
    european: supportedLanguages.filter(l => 
      ['en', 'fr', 'de', 'es', 'pt', 'it', 'ru', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'cs', 'hu', 'ro', 'bg', 'hr', 'sk', 'sl', 'et', 'lv', 'lt', 'mt', 'el', 'uk', 'be'].includes(l.code)
    ),
    asian: supportedLanguages.filter(l => 
      ['zh', 'ja', 'ko', 'hi', 'th', 'vi', 'id', 'ms', 'tl', 'bn'].includes(l.code)
    ),
    middle_eastern: supportedLanguages.filter(l => 
      ['ar', 'tr', 'ur', 'fa', 'he'].includes(l.code)
    ),
    african: supportedLanguages.filter(l => 
      ['sw', 'am', 'yo', 'ig', 'ha', 'zu', 'xh', 'af'].includes(l.code)
    ),
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="flex items-center gap-2">
          <Globe size={16} />
          <span className="hidden sm:inline">{currentLanguageInfo?.flag}</span>
          <span className="hidden md:inline">{currentLanguageInfo?.nativeName}</span>
          <span className="sm:hidden">{currentLanguageInfo?.flag}</span>
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Globe className="text-primary" />
            {t('settings.language')} / Language Selection
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          {/* Current Language */}
          <div className="bg-muted/50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{currentLanguageInfo?.flag}</span>
                <div>
                  <div className="font-medium">{currentLanguageInfo?.nativeName}</div>
                  <div className="text-sm text-muted-foreground">{currentLanguageInfo?.name}</div>
                </div>
              </div>
              <Badge variant="default" className="flex items-center gap-1">
                <Check size={12} />
                Current
              </Badge>
            </div>
          </div>

          {/* European Languages */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">🇪🇺 European Languages</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {languageGroups.european.map((lang) => (
                <Button
                  key={lang.code}
                  variant={currentLanguage === lang.code ? "default" : "ghost"}
                  size="sm"
                  onClick={() => handleLanguageChange(lang.code)}
                  className="justify-start h-auto p-3"
                >
                  <div className="flex items-center gap-2 w-full">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="text-left flex-1 min-w-0">
                      <div className="font-medium text-sm">{lang.nativeName}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.name}</div>
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Asian Languages */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">🌏 Asian Languages</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {languageGroups.asian.map((lang) => (
                <Button
                  key={lang.code}
                  variant={currentLanguage === lang.code ? "default" : "ghost"}
                  size="sm"
                  onClick={() => handleLanguageChange(lang.code)}
                  className="justify-start h-auto p-3"
                >
                  <div className="flex items-center gap-2 w-full">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="text-left flex-1 min-w-0">
                      <div className="font-medium text-sm">{lang.nativeName}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.name}</div>
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Middle Eastern Languages */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">🕌 Middle Eastern Languages</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {languageGroups.middle_eastern.map((lang) => (
                <Button
                  key={lang.code}
                  variant={currentLanguage === lang.code ? "default" : "ghost"}
                  size="sm"
                  onClick={() => handleLanguageChange(lang.code)}
                  className="justify-start h-auto p-3"
                >
                  <div className="flex items-center gap-2 w-full">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="text-left flex-1 min-w-0">
                      <div className="font-medium text-sm">{lang.nativeName}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.name}</div>
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* African Languages */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">🌍 African Languages</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
              {languageGroups.african.map((lang) => (
                <Button
                  key={lang.code}
                  variant={currentLanguage === lang.code ? "default" : "ghost"}
                  size="sm"
                  onClick={() => handleLanguageChange(lang.code)}
                  className="justify-start h-auto p-3"
                >
                  <div className="flex items-center gap-2 w-full">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="text-left flex-1 min-w-0">
                      <div className="font-medium text-sm">{lang.nativeName}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.name}</div>
                    </div>
                  </div>
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Help Section */}
          <div className="bg-muted/30 p-4 rounded-lg text-sm text-muted-foreground">
            <p>
              <strong>{t('languageSelector.note')}</strong> {t('languageSelector.noteSaved')}
            </p>
            <p className="mt-2">
              {t('languageSelector.missingLanguage')} {t('languageSelector.contactUs')}
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
