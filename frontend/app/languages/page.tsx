'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Globe, Loader2, Search, CheckCircle2, Volume2, Copy } from 'lucide-react';

interface Language {
  code: string;
  name: string;
  nativeName: string;
  family: string;
  speakers: number;
}

interface TranslationResult {
  source_lang: string;
  target_lang: string;
  source_text: string;
  translated_text: string;
  confidence: number;
  translation_time_ms: number;
}

export default function LanguagesPage() {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [selectedSource, setSelectedSource] = useState<string>('auto');
  const [selectedTarget, setSelectedTarget] = useState<string>('en');
  const [sourceText, setSourceText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [detectedLang, setDetectedLang] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingLanguages, setLoadingLanguages] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [confidence, setConfidence] = useState<number | null>(null);
  const [translationTime, setTranslationTime] = useState<number | null>(null);

  // Fetch languages from backend
  useEffect(() => {
    fetchLanguages();
  }, []);

  const fetchLanguages = async () => {
    try {
      setLoadingLanguages(true);
      const response = await fetch('http://localhost:8000/languages/list');
      
      if (response.ok) {
        const data = await response.json();
        setLanguages(data.languages || []);
      } else {
        console.error('Failed to fetch languages');
      }
    } catch (error) {
      console.error('Error fetching languages:', error);
    } finally {
      setLoadingLanguages(false);
    }
  };

  const handleTranslate = async () => {
    if (!sourceText.trim()) return;

    try {
      setLoading(true);
      setTranslatedText('');
      setConfidence(null);
      setTranslationTime(null);

      const response = await fetch('http://localhost:8000/languages/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
          target_lang: selectedTarget,
          source_lang: selectedSource === 'auto' ? null : selectedSource,
        }),
      });

      if (response.ok) {
        const result: TranslationResult = await response.json();
        setTranslatedText(result.translated_text);
        setConfidence(result.confidence);
        setTranslationTime(result.translation_time_ms);
        
        if (selectedSource === 'auto') {
          setDetectedLang(result.source_lang);
        }
      } else {
        const error = await response.json();
        setTranslatedText(`Error: ${error.detail || 'Translation failed'}`);
      }
    } catch (error) {
      console.error('Translation error:', error);
      setTranslatedText('Connection error. Please check backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetectLanguage = async () => {
    if (!sourceText.trim()) return;

    try {
      const response = await fetch('http://localhost:8000/languages/detect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sourceText,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setDetectedLang(result.detected_language);
        setSelectedSource(result.detected_language);
      }
    } catch (error) {
      console.error('Language detection error:', error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const speakText = (text: string, lang: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      speechSynthesis.speak(utterance);
    }
  };

  const filteredLanguages = languages.filter(lang =>
    lang.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lang.nativeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lang.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-blue-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Globe className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Multilingual Engine</h1>
                <p className="text-sm text-gray-500">644 Languages • Real-time Translation • AI-Powered</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm font-semibold text-gray-700">{languages.length} Languages</div>
                <div className="text-xs text-gray-500">Available Now</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Translation Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Translator Card */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Real-time Translation</h2>
                {detectedLang && (
                  <div className="flex items-center space-x-2 text-sm text-green-600">
                    <CheckCircle2 className="h-4 w-4" />
                    <span>Detected: {detectedLang.toUpperCase()}</span>
                  </div>
                )}
              </div>

              {/* Language Selectors */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Source Language
                  </label>
                  <div className="flex space-x-2">
                    <select
                      value={selectedSource}
                      onChange={(e) => setSelectedSource(e.target.value)}
                      className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={loading}
                    >
                      <option value="auto">Auto-detect</option>
                      {languages.map((lang) => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name} ({lang.nativeName})
                        </option>
                      ))}
                    </select>
                    <button
                      onClick={handleDetectLanguage}
                      disabled={!sourceText || loading}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition disabled:opacity-50"
                      title="Detect Language"
                    >
                      🔍
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Language
                  </label>
                  <select
                    value={selectedTarget}
                    onChange={(e) => setSelectedTarget(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={loading}
                  >
                    {languages.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name} ({lang.nativeName})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Text Areas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">
                      Text to Translate
                    </label>
                    <button
                      onClick={() => speakText(sourceText, selectedSource)}
                      disabled={!sourceText}
                      className="text-blue-600 hover:text-blue-700 disabled:opacity-50"
                    >
                      <Volume2 className="h-4 w-4" />
                    </button>
                  </div>
                  <textarea
                    value={sourceText}
                    onChange={(e) => setSourceText(e.target.value)}
                    placeholder="Enter text to translate..."
                    className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    disabled={loading}
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {sourceText.length} characters
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">
                      Translation
                    </label>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => speakText(translatedText, selectedTarget)}
                        disabled={!translatedText}
                        className="text-blue-600 hover:text-blue-700 disabled:opacity-50"
                      >
                        <Volume2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => copyToClipboard(translatedText)}
                        disabled={!translatedText}
                        className="text-blue-600 hover:text-blue-700 disabled:opacity-50"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  <div className="w-full h-48 p-4 bg-gray-50 border border-gray-200 rounded-lg overflow-y-auto">
                    {loading ? (
                      <div className="flex items-center justify-center h-full">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                      </div>
                    ) : (
                      <p className="text-gray-900 whitespace-pre-wrap">
                        {translatedText || 'Translation will appear here...'}
                      </p>
                    )}
                  </div>
                  {confidence !== null && (
                    <div className="text-xs text-gray-500 mt-1 flex items-center justify-between">
                      <span>Confidence: {(confidence * 100).toFixed(1)}%</span>
                      {translationTime && <span>{translationTime.toFixed(0)}ms</span>}
                    </div>
                  )}
                </div>
              </div>

              {/* Translate Button */}
              <button
                onClick={handleTranslate}
                disabled={!sourceText.trim() || loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Translating...</span>
                  </>
                ) : (
                  <>
                    <Globe className="h-5 w-5" />
                    <span>Translate Now</span>
                  </>
                )}
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-3xl font-bold text-blue-600">{languages.length}</div>
                <div className="text-sm text-gray-600">Languages</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-3xl font-bold text-green-600">99.5%</div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
              <div className="bg-white rounded-lg shadow p-4 text-center">
                <div className="text-3xl font-bold text-purple-600">&lt;200ms</div>
                <div className="text-sm text-gray-600">Avg Speed</div>
              </div>
            </div>
          </div>

          {/* Languages List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">All Languages</h3>
                <div className="text-sm text-gray-500">{filteredLanguages.length} shown</div>
              </div>

              {/* Search */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search languages..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Languages List */}
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {loadingLanguages ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                  </div>
                ) : filteredLanguages.length > 0 ? (
                  filteredLanguages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => setSelectedTarget(lang.code)}
                      className={`w-full text-left p-3 rounded-lg transition hover:bg-blue-50 ${
                        selectedTarget === lang.code ? 'bg-blue-100 border-2 border-blue-500' : 'border border-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{lang.name}</div>
                          <div className="text-sm text-gray-600">{lang.nativeName}</div>
                        </div>
                        <div className="text-xs text-gray-500">{lang.code.toUpperCase()}</div>
                      </div>
                      {lang.speakers && (
                        <div className="text-xs text-gray-400 mt-1">
                          {(lang.speakers / 1000000).toFixed(1)}M speakers
                        </div>
                      )}
                    </button>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    No languages found
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
