/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

export interface Translations {
  // Navigation
  nav: {
    cases: string;
    dashboard: string;
    volunteers: string;
    report: string;
    settings: string;
    people: string;
    stats: string;
  };
  
  // Common actions
  common: {
    save: string;
    cancel: string;
    submit: string;
    loading: string;
    error: string;
    success: string;
    back: string;
    next: string;
    close: string;
    edit: string;
    delete: string;
    search: string;
    filter: string;
  };
  
  // Header and stats
  header: {
    title: string;
    subtitle: string;
    totalCases: string;
    helped: string;
    needHelp: string;
    open: string;
    total: string;
  };

  // Main application
  app: {
    communityAssistanceRequests: string;
    liveUpdates: string;
    loadSampleData: string;
    reportSomeoneNeedsHelp: string;
    helpConnectCommunity: string;
    completed: string;
    started: string;
    assistanceFor: string;
    case: string;
    reportingGuidelines: string;
    respectDignity: string;
    respectDignityDesc: string;
    beAccurate: string;
    beAccurateDesc: string;
    emergencyFirst: string;
    emergencyFirstDesc: string;
    aboutIA2GOOD: string;
    aboutIA2GOODDesc: string;
    emergencyNotice: string;
    emergencyNoticeDesc: string;
    openSource: string;
    attributionRequired: string;
    copyright: string;
  };
  
  // Cases
  cases: {
    title: string;
    personNeedsHelp: string;
    animalNeedsHelp: string;
    allCases: string;
    people: string;
    animals: string;
    allStatus: string;
    inProgress: string;
    helped: string;
    noResults: string;
    noResultsDesc: string;
    distance: string;
    reported: string;
    statusLabel: string;
    noCasesFound: string;
    whatHappening: string;
    unknown: string;
    anonymousVolunteer: string;
    markedAsHelped: string;
    markedAsInProgress: string;
    showing: string;
    case: string;
    cases: string;
    only: string;
    urgency: {
      low: string;
      medium: string;
      high: string;
    };
    status: {
      open: string;
      inProgress: string;
      helped: string;
    };
    actions: {
      imGoingToHelp: string;
      markAsHelped: string;
      markAsAlreadyHelped: string;
    };
    details: {
      situation: string;
      distance: string;
      reported: string;
      whatHappening: string;
      helpProvided: string;
      assistanceCompleted: string;
    };
    timeAgo: {
      justNow: string;
      minutesAgo: string;
      hoursAgo: string;
      daysAgo: string;
      weeksAgo: string;
      monthsAgo: string;
    };
  };
  
  // Report form
  report: {
    title: string;
    subtitle: string;
    buttonText: string;
    buttonTextShort: string;
    whoNeedsHelp: string;
    personHomeless: string;
    strayAnimal: string;
    whatKindOfHelp: string;
    urgencyLevel: string;
    location: {
      getting: string;
      ready: string;
      needed: string;
      getLocation: string;
      unknown: string;
    };
    placeholders: {
      person: string;
      animal: string;
    };
    urgencyDesc: {
      low: string;
      medium: string;
      high: string;
    };
    guidelines: {
      title: string;
      respect: string;
      respectDesc: string;
      accurate: string;
      accurateDesc: string;
      emergency: string;
      emergencyDesc: string;
    };
    success: {
      person: string;
      animal: string;
    };
    disclaimer: string;
  };
  
  // Volunteers
  volunteers: {
    title: string;
    directory: string;
    profile: string;
    myProfile: string;
    editProfile: string;
    viewProfile: string;
    manageProfile: string;
    updateInfo: string;
    backToVolunteers: string;
  };
  
  // Dashboard
  dashboard: {
    title: string;
    overview: string;
    description: string;
    impact: string;
    activity: string;
    recentActivity: string;
    dayStreak: string;
    weeklyGoalProgress: string;
    helpedThisWeek: string;
    toGo: string;
    community: string;
    impactTracking: string;
    impactTrackingDesc: string;
    weeklyGoals: string;
    weeklyGoalsDesc: string;
    activityTimeline: string;
    activityTimelineDesc: string;
    achievementStreaks: string;
    achievementStreaksDesc: string;
    communityStats: string;
    communityStatsDesc: string;
    volunteerLeaderboard: string;
    volunteerLeaderboardDesc: string;
    gettingStarted: string;
    step1Title: string;
    step1Desc: string;
    step2Title: string;
    step2Desc: string;
    step3Title: string;
    step3Desc: string;
    everyActionCounts: string;
    rippleEffect: string;
    rememberTitle: string;
    totalHelped: string;
    peopleHelped: string;
    animalsHelped: string;
    avgResponse: string;
    weeklyImpactTrend: string;
    impactByCategory: string;
    homelessAssistance: string;
    animalCare: string;
    mostActiveIn: string;
    assistance: string;
    activeVolunteers: string;
    activeCases: string;
    resolvedToday: string;
    thisWeekCommunityImpact: string;
    casesResolved: string;
    averageResolutionTime: string;
    topCommunityHelpers: string;
    you: string;
    monthlyCommunityOverview: string;
    casesResolvedThisMonth: string;
    weeklyAverage: string;
    successRate: string;
    rememberDesc: string;
  };
  
  // Settings
  settings: {
    title: string;
    subtitle: string;
    preferences: string;
    notifications: string;
    yourProfile: string;
    language: string;
    enableNotifications: string;
    enableNotificationsDesc: string;
    notificationSettings: string;
    notificationSettingsDesc: string;
    enableNotificationsAriaLabel: string;
    readyToHelp: string;
    notificationsDisabled: string;
    volunteerPreferencesTitle: string;
    volunteerPreferencesDesc: string;
  },
  
  // Directory
  directory: {
    title: string;
    subtitle: string;
    volunteers: string;
    searchPlaceholder: string;
    sortBy: string;
    sortByRating: string;
    sortByCases: string;
    sortByHours: string;
    sortByRecent: string;
    category: string;
    allCategories: string;
    homeless: string;
    animals: string;
    verifiedOnly: string;
    cases: string;
    hours: string;
    streak: string;
    skills: string;
    more: string;
    specializesIn: string;
    viewProfile: string;
    noVolunteersFound: string;
    adjustFilters: string;
    communityImpact: string;
    totalCasesHelped: string;
    totalHours: string;
    verifiedVolunteers: string;
    avgRating: string;
  },
  
  // Profile
  profile: {
    editProfile: string;
    editVolunteerProfile: string;
    basicInformation: string;
    displayName: string;
    displayNamePlaceholder: string;
    bio: string;
    bioPlaceholder: string;
    changePhoto: string;
    photoFormat: string;
    skillsExpertise: string;
    skills: string;
    addSkillPlaceholder: string;
    volunteerPreferences: string;
    maxTravelDistance: string;
    preferredCategories: string;
    homelessAssistance: string;
    animalCare: string;
    availability: string;
    availableDays: string;
    startTime: string;
    endTime: string;
    notificationSettings: string;
    enableNotifications: string;
    enableNotificationsDesc: string;
    quietHours: string;
    quietHoursDesc: string;
    profileUpdatedSuccess: string;
    saveChanges: string;
    cancel: string;
    peopleHelped: string;
    animalsHelped: string;
    weekdays: {
      monday: string;
      tuesday: string;
      wednesday: string;
      thursday: string;
      friday: string;
      saturday: string;
      sunday: string;
    };
  };
  
  // Footer
  footer: {
    about: string;
    aboutDesc: string;
    emergency: string;
    emergencyDesc: string;
    openSource: string;
    owner: string;
    contact: string;
    attribution: string;
    copyright: string;
  };
  
  // Quick start
  quickStart: {
    title: string;
    guide: string;
    forPeople: string;
    forAnimals: string;
    quickStartGuide: string;
    howItWorks: string;
    steps: {
      seeNeedsHelp: string;
      seeNeedsHelpDesc: string;
      reportLocation: string;
      wantToHelp: string;
      wantToHelpDesc: string;
      configureSettings: string;
      respondToRequests: string;
      respondToRequestsDesc: string;
      browseCases: string;
      makeDifference: string;
      makeDifferenceDesc: string;
      trackImpact: string;
    };
    emergency: {
      title: string;
      description: string;
      medical: string;
      medicalAction: string;
      medicalNote: string;
      weather: string;
      weatherAction: string;
      weatherNote: string;
      mental: string;
      mentalAction: string;
      mentalNote: string;
      animal: string;
      animalAction: string;
      animalNote: string;
    };
    guidelines: {
      title: string;
      respectDignity: string;
      respectDignityDesc: string;
      prioritizeSafety: string;
      prioritizeSafetyDesc: string;
      beAccurate: string;
      beAccurateDesc: string;
      followThrough: string;
      followThroughDesc: string;
      knowLimits: string;
      knowLimitsDesc: string;
    };
    help: {
      title: string;
      peopleFood: string;
      peopleClothing: string;
      peopleHygiene: string;
      peopleInfo: string;
      peopleTransport: string;
      animalFood: string;
      animalShelter: string;
      animalVet: string;
      animalTransport: string;
      animalControl: string;
    };
  };
  
  // Voice controls
  voice: {
    listening: string;
    speak: string;
    stop: string;
  };
  
  // Languages
  languages: {
    en: string;
    fr: string;
    de: string;
    es: string;
    pt: string;
    it: string;
    ru: string;
    zh: string;
    ja: string;
    ko: string;
    ar: string;
    hi: string;
    tr: string;
    pl: string;
    nl: string;
    sv: string;
    da: string;
    no: string;
    fi: string;
    cs: string;
    hu: string;
    ro: string;
    bg: string;
    hr: string;
    sk: string;
    sl: string;
    et: string;
    lv: string;
    lt: string;
    mt: string;
    el: string;
    uk: string;
    be: string;
    th: string;
    vi: string;
    id: string;
    ms: string;
    tl: string;
    bn: string;
    ur: string;
    fa: string;
    he: string;
    sw: string;
    am: string;
    yo: string;
    ig: string;
    ha: string;
    zu: string;
    xh: string;
    af: string;
  };

  // Language selector specific texts
  languageSelector: {
    title: string;
    subtitle: string;
    note: string;
    noteSaved: string;
    missingLanguage: string;
    contactUs: string;
  };

  // Debug info
  debug: {
    title: string;
    clearData: string;
    exportData: string;
    systemInfo: string;
    capabilities: string;
    dataCleared: string;
    dataExported: string;
    gpsLocation: string;
    browserNotifications: string;
    speechRecognition: string;
    voiceInput: string;
    speechSynthesis: string;
    localStorage: string;
    dataPersistence: string;
    supported: string;
    notAvailable: string;
  };
}

export type SupportedLanguage = keyof Translations['languages'];

export const supportedLanguages: { code: SupportedLanguage; name: string; nativeName: string; flag: string }[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' },
  { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
  { code: 'tr', name: 'Turkish', nativeName: 'Türkçe', flag: '🇹🇷' },
  { code: 'pl', name: 'Polish', nativeName: 'Polski', flag: '🇵🇱' },
  { code: 'nl', name: 'Dutch', nativeName: 'Nederlands', flag: '🇳🇱' },
  { code: 'sv', name: 'Swedish', nativeName: 'Svenska', flag: '🇸🇪' },
  { code: 'da', name: 'Danish', nativeName: 'Dansk', flag: '🇩🇰' },
  { code: 'no', name: 'Norwegian', nativeName: 'Norsk', flag: '🇳🇴' },
  { code: 'fi', name: 'Finnish', nativeName: 'Suomi', flag: '🇫🇮' },
  { code: 'cs', name: 'Czech', nativeName: 'Čeština', flag: '🇨🇿' },
  { code: 'hu', name: 'Hungarian', nativeName: 'Magyar', flag: '🇭🇺' },
  { code: 'ro', name: 'Romanian', nativeName: 'Română', flag: '🇷🇴' },
  { code: 'bg', name: 'Bulgarian', nativeName: 'Български', flag: '🇧🇬' },
  { code: 'hr', name: 'Croatian', nativeName: 'Hrvatski', flag: '🇭🇷' },
  { code: 'sk', name: 'Slovak', nativeName: 'Slovenčina', flag: '🇸🇰' },
  { code: 'sl', name: 'Slovenian', nativeName: 'Slovenščina', flag: '🇸🇮' },
  { code: 'et', name: 'Estonian', nativeName: 'Eesti', flag: '🇪🇪' },
  { code: 'lv', name: 'Latvian', nativeName: 'Latviešu', flag: '🇱🇻' },
  { code: 'lt', name: 'Lithuanian', nativeName: 'Lietuvių', flag: '🇱🇹' },
  { code: 'mt', name: 'Maltese', nativeName: 'Malti', flag: '🇲🇹' },
  { code: 'el', name: 'Greek', nativeName: 'Ελληνικά', flag: '🇬🇷' },
  { code: 'uk', name: 'Ukrainian', nativeName: 'Українська', flag: '🇺🇦' },
  { code: 'be', name: 'Belarusian', nativeName: 'Беларуская', flag: '🇧🇾' },
  { code: 'th', name: 'Thai', nativeName: 'ไทย', flag: '🇹🇭' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', flag: '🇻🇳' },
  { code: 'id', name: 'Indonesian', nativeName: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'ms', name: 'Malay', nativeName: 'Bahasa Melayu', flag: '🇲🇾' },
  { code: 'tl', name: 'Filipino', nativeName: 'Filipino', flag: '🇵🇭' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', flag: '🇧🇩' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', flag: '🇵🇰' },
  { code: 'fa', name: 'Persian', nativeName: 'فارسی', flag: '🇮🇷' },
  { code: 'he', name: 'Hebrew', nativeName: 'עברית', flag: '🇮🇱' },
  { code: 'sw', name: 'Swahili', nativeName: 'Kiswahili', flag: '🇰🇪' },
  { code: 'am', name: 'Amharic', nativeName: 'አማርኛ', flag: '🇪🇹' },
  { code: 'yo', name: 'Yoruba', nativeName: 'Yorùbá', flag: '🇳🇬' },
  { code: 'ig', name: 'Igbo', nativeName: 'Igbo', flag: '🇳🇬' },
  { code: 'ha', name: 'Hausa', nativeName: 'Hausa', flag: '🇳🇬' },
  { code: 'zu', name: 'Zulu', nativeName: 'isiZulu', flag: '🇿🇦' },
  { code: 'xh', name: 'Xhosa', nativeName: 'isiXhosa', flag: '🇿🇦' },
  { code: 'af', name: 'Afrikaans', nativeName: 'Afrikaans', flag: '🇿🇦' },
];

let currentLanguage: SupportedLanguage = 'en';
let translations: Record<SupportedLanguage, Translations> = {} as any;

export const getCurrentLanguage = (): SupportedLanguage => currentLanguage;
export const setCurrentLanguage = (lang: SupportedLanguage): void => {
  currentLanguage = lang;
  localStorage.setItem('solidarity-language', lang);
};

export const initializeLanguage = (): void => {
  const saved = localStorage.getItem('solidarity-language') as SupportedLanguage;
  if (saved && supportedLanguages.find(l => l.code === saved)) {
    currentLanguage = saved;
  } else {
    // Auto-detect browser language
    const browserLang = navigator.language.split('-')[0] as SupportedLanguage;
    if (supportedLanguages.find(l => l.code === browserLang)) {
      currentLanguage = browserLang;
    }
  }
};

export const loadTranslations = async (): Promise<void> => {
  console.log('🔥 [DEBUG] Loading translations for all languages...');
  // Load all translations dynamically
  const translationModules = await Promise.all(
    supportedLanguages.map(async (lang) => {
      try {
        console.log('🔥 [DEBUG] Loading translations for:', lang.code);
        const module = await import(`../locales/${lang.code}.ts`);
        console.log('🔥 [DEBUG] Successfully loaded:', lang.code);
        return { code: lang.code, translations: module.default };
      } catch (error) {
        console.warn(`❌ Failed to load translations for ${lang.code}:`, error);
        return null;
      }
    })
  );

  translationModules.forEach((module) => {
    if (module) {
      translations[module.code] = module.translations;
      console.log('🔥 [DEBUG] Registered translations for:', module.code);
    }
  });
  
  console.log('🔥 [DEBUG] All translations loaded. Available languages:', Object.keys(translations));
};

export const t = (key: string): string => {
  console.log('🔥 [DEBUG] Translating key:', key, 'for language:', currentLanguage);
  const keys = key.split('.');
  let value: any = translations[currentLanguage];
  
  console.log('🔥 [DEBUG] Available translations for', currentLanguage, ':', !!translations[currentLanguage]);
  
  for (const k of keys) {
    value = value?.[k];
  }
  
  if (typeof value === 'string') {
    console.log('🔥 [DEBUG] Found translation:', value);
    return value;
  }
  
  // Fallback to English if translation not found
  if (currentLanguage !== 'en') {
    console.log('🔥 [DEBUG] Fallback to English for key:', key);
    value = translations['en'];
    for (const k of keys) {
      value = value?.[k];
    }
    if (typeof value === 'string') {
      console.log('🔥 [DEBUG] Found English fallback:', value);
      return value;
    }
  }
  
  console.log('🔥 [DEBUG] No translation found, returning key:', key);
  return key; // Return key if no translation found
};

export const formatTimeAgo = (timestamp: string, lang: SupportedLanguage = currentLanguage): string => {
  const now = new Date();
  const time = new Date(timestamp);
  const diffMs = now.getTime() - time.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);

  if (diffMinutes < 1) return t('cases.timeAgo.justNow');
  if (diffMinutes < 60) return `${diffMinutes} ${t('cases.timeAgo.minutesAgo')}`;
  if (diffHours < 24) return `${diffHours} ${t('cases.timeAgo.hoursAgo')}`;
  if (diffDays < 7) return `${diffDays} ${t('cases.timeAgo.daysAgo')}`;
  if (diffWeeks < 4) return `${diffWeeks} ${t('cases.timeAgo.weeksAgo')}`;
  return `${diffMonths} ${t('cases.timeAgo.monthsAgo')}`;
};
