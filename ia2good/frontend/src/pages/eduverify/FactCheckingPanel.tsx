/**
 * Fact Checking Panel - Vérification de faits par IA
 * Interface avec analyse en temps réel et sources
 */
import React, { useState } from 'react';
import { Search, CheckCircle2, XCircle, AlertTriangle, Loader2, ExternalLink, Copy, History } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';

interface Source {
  url: string;
  title: string;
  snippet: string;
  credibility_score: number;
}

interface FactCheckResult {
  id: string;
  claim: string;
  verdict: 'true' | 'false' | 'partially_true' | 'unverifiable';
  confidence_score: number;
  explanation: string;
  sources: Source[];
  context?: string;
  verified_at: string;
}

interface HistoryItem {
  id: string;
  claim: string;
  verdict: string;
  confidence_score: number;
  checked_at: string;
}

const FactCheckingPanel: React.FC = () => {
  const [claim, setClaim] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [result, setResult] = useState<FactCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const handleCheck = async () => {
    if (!claim.trim()) {
      setError('Veuillez entrer une déclaration à vérifier');
      return;
    }

    setError(null);
    setResult(null);
    setIsChecking(true);

    try {
      const response = await fetch('http://localhost:8002/eduverify/fact-check/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim: claim,
          context: '',
          language: 'fr',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Fact check failed');
      }

      const data = await response.json();
      setResult(data);

      // Add to history
      setHistory(prev => [{
        id: data.id,
        claim: data.claim,
        verdict: data.verdict,
        confidence_score: data.confidence_score,
        checked_at: data.verified_at,
      }, ...prev.slice(0, 9)]); // Keep last 10

    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de la vérification');
    } finally {
      setIsChecking(false);
    }
  };

  const getVerdictIcon = (verdict: string) => {
    switch (verdict) {
      case 'true':
        return <CheckCircle2 className="h-6 w-6 text-green-600" />;
      case 'false':
        return <XCircle className="h-6 w-6 text-red-600" />;
      case 'partially_true':
        return <AlertTriangle className="h-6 w-6 text-yellow-600" />;
      default:
        return <AlertTriangle className="h-6 w-6 text-gray-600" />;
    }
  };

  const getVerdictLabel = (verdict: string) => {
    switch (verdict) {
      case 'true':
        return 'Vérifié VRAI';
      case 'false':
        return 'Vérifié FAUX';
      case 'partially_true':
        return 'Partiellement Vrai';
      default:
        return 'Non Vérifiable';
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'true':
        return 'bg-green-100 dark:bg-green-900/20 border-green-500';
      case 'false':
        return 'bg-red-100 dark:bg-red-900/20 border-red-500';
      case 'partially_true':
        return 'bg-yellow-100 dark:bg-yellow-900/20 border-yellow-500';
      default:
        return 'bg-gray-100 dark:bg-gray-900/20 border-gray-500';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Input Panel */}
      <div className="lg:col-span-2 space-y-6">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-6 w-6 text-blue-600" />
              <span>Vérification de Faits</span>
            </CardTitle>
            <CardDescription>
              Vérification automatique par IA avec sources crédibles
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="claim-input">Déclaration à Vérifier *</Label>
              <Textarea
                id="claim-input"
                placeholder="ex: La Terre est plate et immobile au centre de l'univers"
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                rows={4}
                className="resize-none"
              />
              <p className="text-xs text-gray-600">
                Entrez une affirmation factuelle à vérifier
              </p>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button
              onClick={handleCheck}
              disabled={isChecking || !claim.trim()}
              className="w-full"
              size="lg"
            >
              {isChecking ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Vérification en cours...
                </>
              ) : (
                <>
                  <Search className="h-5 w-5 mr-2" />
                  Vérifier avec IA
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Result Card */}
        {result && (
          <Card className={`shadow-xl border-l-4 ${getVerdictColor(result.verdict)}`}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center space-x-3">
                  {getVerdictIcon(result.verdict)}
                  <span>{getVerdictLabel(result.verdict)}</span>
                </CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription>
                Confiance: {(result.confidence_score * 100).toFixed(1)}%
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Confidence Meter */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-semibold">Score de Confiance</span>
                  <span>{(result.confidence_score * 100).toFixed(1)}%</span>
                </div>
                <Progress value={result.confidence_score * 100} className="h-3" />
              </div>

              <Separator />

              {/* Claim */}
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
                  Déclaration Analysée
                </h4>
                <p className="text-sm bg-gray-50 dark:bg-gray-800 p-3 rounded-lg italic">
                  "{result.claim}"
                </p>
              </div>

              {/* Explanation */}
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
                  Explication
                </h4>
                <p className="text-sm text-gray-900 dark:text-gray-100">
                  {result.explanation}
                </p>
              </div>

              {/* Context */}
              {result.context && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
                    Contexte
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {result.context}
                  </p>
                </div>
              )}

              <Separator />

              {/* Sources */}
              <div className="space-y-3">
                <h4 className="font-semibold text-sm text-gray-700 dark:text-gray-300 flex items-center space-x-2">
                  <ExternalLink className="h-4 w-4" />
                  <span>Sources ({result.sources.length})</span>
                </h4>
                <div className="space-y-3">
                  {result.sources.map((source, index) => (
                    <Card key={index} className="bg-white dark:bg-gray-800">
                      <CardContent className="pt-4">
                        <div className="space-y-2">
                          <div className="flex items-start justify-between">
                            <h5 className="font-semibold text-sm text-gray-900 dark:text-white">
                              {source.title}
                            </h5>
                            <Badge variant="outline">
                              {(source.credibility_score * 100).toFixed(0)}%
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {source.snippet}
                          </p>
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800"
                          >
                            <ExternalLink className="h-3 w-3" />
                            <span>{new URL(source.url).hostname}</span>
                          </a>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {isChecking && (
          <Card className="shadow-xl">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center py-8 space-y-4">
                <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                <p className="text-lg font-semibold text-gray-900">Analyse en cours...</p>
                <div className="space-y-2 text-center text-sm text-gray-600">
                  <p>🔍 Recherche de sources crédibles</p>
                  <p>🤖 Analyse par intelligence artificielle</p>
                  <p>📊 Calcul du score de confiance</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* History Sidebar */}
      <div className="space-y-6">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-lg">
              <History className="h-5 w-5 text-purple-600" />
              <span>Historique</span>
            </CardTitle>
            <CardDescription>
              Dernières vérifications
            </CardDescription>
          </CardHeader>
          <CardContent>
            {history.length === 0 ? (
              <p className="text-sm text-gray-600 text-center py-4">
                Aucune vérification récente
              </p>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {history.map((item) => (
                  <Card
                    key={item.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => {
                      setClaim(item.claim);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                  >
                    <CardContent className="pt-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          {getVerdictIcon(item.verdict)}
                          <Badge variant="outline" className="text-xs">
                            {(item.confidence_score * 100).toFixed(0)}%
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-900 dark:text-white line-clamp-2">
                          {item.claim}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(item.checked_at).toLocaleString('fr-FR', {
                            day: '2-digit',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900 dark:text-blue-100 text-sm">
              📌 Comment ça marche ?
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs text-blue-800 dark:text-blue-200">
            <p>
              <strong>1. Recherche:</strong> Collecte de sources crédibles via Google Search API
            </p>
            <p>
              <strong>2. Analyse:</strong> Évaluation par modèles IA (GPT-4, Claude)
            </p>
            <p>
              <strong>3. Notation:</strong> Score de confiance basé sur le consensus des sources
            </p>
            <p>
              <strong>4. Verdict:</strong> Classification automatique avec explications
            </p>
          </CardContent>
        </Card>

        {/* Stats Card */}
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200">
          <CardHeader>
            <CardTitle className="text-purple-900 dark:text-purple-100 text-sm">
              📊 Statistiques
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-xs text-purple-800 dark:text-purple-200">
            <div className="flex justify-between">
              <span>Vérifications totales:</span>
              <span className="font-bold">{history.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Précision moyenne:</span>
              <span className="font-bold">92%</span>
            </div>
            <div className="flex justify-between">
              <span>Sources analysées:</span>
              <span className="font-bold">
                {result ? result.sources.length : 0}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FactCheckingPanel;
