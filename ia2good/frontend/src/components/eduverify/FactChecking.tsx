import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, HelpCircle, ExternalLink, Loader2 } from 'lucide-react';

export type FactVerdict =
  | 'true'
  | 'mostly_true'
  | 'half_true'
  | 'mostly_false'
  | 'false'
  | 'unverified';

export interface FactCheckSource {
  title: string;
  url: string;
  credibility_score: number;
  date?: string;
}

export interface FactCheck {
  id: string;
  claim: string;
  verdict: FactVerdict;
  confidence: number;
  sources: FactCheckSource[];
  explanation: string;
  context?: string;
  ai_reasoning: string;
  human_verified: boolean;
}

interface FactCheckingInterfaceProps {
  onCheck: (claim: string) => Promise<FactCheck>;
  initialClaim?: string;
}

const verdictConfig: Record<
  FactVerdict,
  { icon: React.FC<any>; color: string; label: string; bgColor: string }
> = {
  true: {
    icon: CheckCircle,
    color: 'text-green-700',
    label: 'VRAI',
    bgColor: 'bg-green-100',
  },
  mostly_true: {
    icon: CheckCircle,
    color: 'text-green-600',
    label: 'PLUTÔT VRAI',
    bgColor: 'bg-green-50',
  },
  half_true: {
    icon: AlertTriangle,
    color: 'text-yellow-700',
    label: 'PARTIELLEMENT VRAI',
    bgColor: 'bg-yellow-100',
  },
  mostly_false: {
    icon: XCircle,
    color: 'text-orange-600',
    label: 'PLUTÔT FAUX',
    bgColor: 'bg-orange-50',
  },
  false: {
    icon: XCircle,
    color: 'text-red-700',
    label: 'FAUX',
    bgColor: 'bg-red-100',
  },
  unverified: {
    icon: HelpCircle,
    color: 'text-gray-600',
    label: 'NON VÉRIFIÉ',
    bgColor: 'bg-gray-100',
  },
};

export const FactCheckingInterface: React.FC<FactCheckingInterfaceProps> = ({
  onCheck,
  initialClaim = '',
}) => {
  const [claim, setClaim] = useState(initialClaim);
  const [isChecking, setIsChecking] = useState(false);
  const [result, setResult] = useState<FactCheck | null>(null);

  const handleCheck = async () => {
    if (!claim.trim()) return;

    setIsChecking(true);
    try {
      const factCheck = await onCheck(claim);
      setResult(factCheck);
    } catch (error) {
      console.error('Fact check error:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const handleNewCheck = () => {
    setResult(null);
    setClaim('');
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">🔍 Vérification de Faits</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Textarea
              placeholder="Entrez une affirmation à vérifier... 
Ex: Napoléon est né en 1769 en Corse"
              value={claim}
              onChange={(e) => setClaim(e.target.value)}
              className="min-h-[120px] text-lg"
              disabled={isChecking || result !== null}
            />
          </div>

          {!result && (
            <Button
              onClick={handleCheck}
              disabled={!claim.trim() || isChecking}
              size="lg"
              className="w-full"
            >
              {isChecking ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Vérification en cours...
                </>
              ) : (
                <>🔍 Vérifier cette affirmation</>
              )}
            </Button>
          )}

          {isChecking && (
            <div className="text-center py-6 space-y-2">
              <Loader2 className="w-12 h-12 animate-spin mx-auto text-blue-600" />
              <p className="text-gray-600">Analyse en cours...</p>
              <p className="text-sm text-gray-500">
                Recherche de sources • Analyse IA • Calcul de confiance
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {result && (
        <>
          {/* Verdict Card */}
          <Card className={verdictConfig[result.verdict].bgColor}>
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                {React.createElement(verdictConfig[result.verdict].icon, {
                  className: `w-16 h-16 ${verdictConfig[result.verdict].color}`,
                })}
                <div className="flex-1">
                  <h2
                    className={`text-3xl font-bold ${verdictConfig[result.verdict].color} mb-2`}
                  >
                    {verdictConfig[result.verdict].label}
                  </h2>
                  <p className="text-lg text-gray-700 italic">"{result.claim}"</p>
                  <div className="flex items-center gap-4 mt-2">
                    <Badge variant="outline" className="text-base">
                      Confiance: {(result.confidence * 100).toFixed(0)}%
                    </Badge>
                    {result.human_verified && (
                      <Badge variant="secondary" className="text-base">
                        ✓ Vérifié par un humain
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Explanation */}
          <Card>
            <CardHeader>
              <CardTitle>📖 Explication</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-lg leading-relaxed">{result.explanation}</p>

              {result.context && (
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="font-medium text-blue-900 mb-2">Contexte additionnel:</p>
                  <p className="text-gray-700">{result.context}</p>
                </div>
              )}

              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900 mb-2">Raisonnement de l'IA:</p>
                <p className="text-sm text-gray-600">{result.ai_reasoning}</p>
              </div>
            </CardContent>
          </Card>

          {/* Sources */}
          {result.sources.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>📚 Sources ({result.sources.length})</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.sources.map((source, index) => (
                  <a
                    key={index}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-medium text-lg mb-1 flex items-center gap-2">
                          {source.title}
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">{source.url}</p>
                        {source.date && (
                          <p className="text-xs text-gray-500">
                            Publié le: {new Date(source.date).toLocaleDateString('fr-FR')}
                          </p>
                        )}
                      </div>
                      <div className="flex flex-col items-end">
                        <p className="text-xs text-gray-600 mb-1">Crédibilité</p>
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-green-500 rounded-full"
                              style={{ width: `${source.credibility_score * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {(source.credibility_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </a>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Actions */}
          <div className="flex gap-4 justify-center">
            <Button variant="outline" size="lg" onClick={handleNewCheck}>
              Vérifier une autre affirmation
            </Button>
            <Button variant="outline" size="lg">
              Signaler une erreur
            </Button>
            <Button size="lg">Partager ce résultat</Button>
          </div>
        </>
      )}
    </div>
  );
};

// Quick Facts Component for batch checking
interface QuickFactsProps {
  facts: string[];
  onBatchCheck: (facts: string[]) => Promise<FactCheck[]>;
}

export const QuickFacts: React.FC<QuickFactsProps> = ({ facts, onBatchCheck }) => {
  const [results, setResults] = useState<FactCheck[]>([]);
  const [isChecking, setIsChecking] = useState(false);

  const handleBatchCheck = async () => {
    setIsChecking(true);
    try {
      const checks = await onBatchCheck(facts);
      setResults(checks);
    } catch (error) {
      console.error('Batch check error:', error);
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>⚡ Vérification Rapide</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {facts.map((fact, index) => {
            const result = results[index];
            return (
              <div
                key={index}
                className={`p-3 rounded-lg border-2 ${
                  result
                    ? verdictConfig[result.verdict].bgColor
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  {result &&
                    React.createElement(verdictConfig[result.verdict].icon, {
                      className: `w-5 h-5 ${verdictConfig[result.verdict].color}`,
                    })}
                  <p className="flex-1 text-sm">{fact}</p>
                  {result && (
                    <Badge variant="outline" className="text-xs">
                      {verdictConfig[result.verdict].label}
                    </Badge>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <Button onClick={handleBatchCheck} disabled={isChecking} className="w-full">
          {isChecking ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Vérification...
            </>
          ) : (
            <>Vérifier toutes les affirmations</>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
