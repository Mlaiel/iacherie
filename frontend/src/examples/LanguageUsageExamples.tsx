/*
 * Language Pack Usage Examples
 * ============================
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: © 2025 Fahed Mlaiel. All rights reserved.
 * 
 * Professional examples for using the new modular translation system
 */

import React from 'react';
import { useLanguage } from '../hooks/useLanguage';

// Example 1: Basic usage (backward compatible)
export function WelcomeMessage() {
  const { t } = useLanguage();
  
  return (
    <div>
      <h1>{t('welcome')}</h1>
      <p>{t('ai_powered_protection')}</p>
    </div>
  );
}

// Example 2: Module-specific translations
export function GamificationPanel() {
  const { t } = useLanguage();
  
  return (
    <div className="gamification-panel">
      <h2>{t('achievements', 'gamification')}</h2>
      <div className="stats">
        <span>{t('points', 'gamification')}: 1250</span>
        <span>{t('level', 'gamification')}: 15</span>
        <span>{t('badges', 'gamification')}: 8</span>
      </div>
      <button>{t('view_analytics')}</button>
    </div>
  );
}

// Example 3: AI Remix Studio interface
export function RemixStudioControls() {
  const { t } = useLanguage();
  
  return (
    <div className="remix-controls">
      <h3>{t('ai_remix', 'remix')}</h3>
      <div className="actions">
        <button>{t('generate_content', 'remix')}</button>
        <button>{t('style_transfer', 'remix')}</button>
        <button>{t('smart_optimization', 'remix')}</button>
      </div>
      <div className="features">
        <span>{t('creative_ai', 'remix')}</span>
        <span>{t('intelligent_remix', 'remix')}</span>
      </div>
    </div>
  );
}

// Example 4: Language selector with new languages
export function ExtendedLanguageSelector() {
  const { language, setLanguage, availableLanguages } = useLanguage();
  
  return (
    <select 
      value={language} 
      onChange={(e) => setLanguage(e.target.value as any)}
      className="language-selector"
    >
      {availableLanguages.map(lang => (
        <option key={lang.code} value={lang.code}>
          {lang.nativeName} ({lang.name})
        </option>
      ))}
    </select>
  );
}

// Example 5: Multi-module content display
export function DashboardSummary() {
  const { t } = useLanguage();
  
  return (
    <div className="dashboard-summary">
      {/* Common UI elements */}
      <header>
        <h1>{t('dashboard')}</h1>
        <p>{t('total_content')}: 45</p>
      </header>
      
      {/* Gamification section */}
      <section className="gamification">
        <h2>{t('achievements', 'gamification')}</h2>
        <div className="achievement-list">
          <div>{t('content_champion', 'gamification')}</div>
          <div>{t('protection_master', 'gamification')}</div>
          <div>{t('monetization_expert', 'gamification')}</div>
        </div>
      </section>
      
      {/* Remix AI section */}
      <section className="ai-tools">
        <h2>{t('creative_ai', 'remix')}</h2>
        <div className="tools">
          <button>{t('content_enhancement', 'remix')}</button>
          <button>{t('automated_editing', 'remix')}</button>
          <button>{t('performance_prediction', 'remix')}</button>
        </div>
      </section>
    </div>
  );
}

/*
 * Available Languages (10 total):
 * - English (en) - 360 total keys
 * - French (fr) - 360 total keys  
 * - German (de) - 225 total keys
 * - Spanish (es) - 89 total keys
 * - Italian (it) - 89 total keys
 * - Portuguese (pt) - 89 total keys
 * - Russian (ru) - 89 total keys
 * - Chinese (zh) - 89 total keys
 * - Japanese (ja) - 89 total keys
 * - Arabic (ar) - 89 total keys (RTL support)
 * 
 * Available Modules:
 * - common: Core UI, platform features, legal notices
 * - gamification: Achievements, levels, rewards, competitions
 * - remix: AI content generation, creative tools, style transfer
 * 
 * Translation Function Signatures:
 * - t(key: string): string - Basic lookup (backward compatible)
 * - t(key: string, module: 'common' | 'gamification' | 'remix'): string - Module-specific lookup
 * 
 * The system automatically falls back to direct key lookup if module-specific key is not found.
 */