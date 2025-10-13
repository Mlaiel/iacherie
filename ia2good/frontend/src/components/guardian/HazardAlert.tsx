import React, { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

export type HazardUrgency = 'HIGH' | 'MEDIUM' | 'LOW';

export interface Hazard {
  id: string;
  hazard_type: string;
  confidence: number;
  urgency: HazardUrgency;
  alert_message: string;
  timestamp: string;
}

interface HazardAlertProps {
  hazard: Hazard;
  onDismiss?: () => void;
}

const urgencyConfig = {
  HIGH: {
    icon: AlertTriangle,
    bgColor: 'bg-red-600',
    textColor: 'text-white',
    borderColor: 'border-red-800',
    vibrationPattern: [200, 100, 200, 100, 200],
    flashDuration: 5000,
    iconSize: 'w-16 h-16',
  },
  MEDIUM: {
    icon: AlertCircle,
    bgColor: 'bg-orange-500',
    textColor: 'text-white',
    borderColor: 'border-orange-700',
    vibrationPattern: [100],
    flashDuration: 3000,
    iconSize: 'w-12 h-12',
  },
  LOW: {
    icon: Info,
    bgColor: 'bg-blue-500',
    textColor: 'text-white',
    borderColor: 'border-blue-700',
    vibrationPattern: [50],
    flashDuration: 2000,
    iconSize: 'w-8 h-8',
  },
};

export const HazardAlert: React.FC<HazardAlertProps> = ({ hazard, onDismiss }) => {
  const [isVisible, setIsVisible] = useState(true);
  const config = urgencyConfig[hazard.urgency];
  const Icon = config.icon;

  useEffect(() => {
    // Trigger haptic feedback
    if ('vibrate' in navigator) {
      navigator.vibrate(config.vibrationPattern);
    }

    // Auto-dismiss after duration (except for HIGH urgency)
    if (hazard.urgency !== 'HIGH') {
      const timer = setTimeout(() => {
        setIsVisible(false);
        if (onDismiss) onDismiss();
      }, config.flashDuration);

      return () => clearTimeout(timer);
    }
  }, [hazard, config, onDismiss]);

  if (!isVisible) return null;

  // HIGH urgency: Fullscreen flash
  if (hazard.urgency === 'HIGH') {
    return (
      <div
        className={`fixed inset-0 ${config.bgColor} ${config.textColor} flex items-center justify-center z-50 animate-pulse`}
        role="alert"
        aria-live="assertive"
      >
        <div className="text-center p-8">
          <Icon className={`${config.iconSize} mx-auto mb-6 animate-bounce`} />
          <h1 className="text-6xl font-bold mb-4">{hazard.alert_message}</h1>
          <p className="text-2xl mb-2">Type: {hazard.hazard_type}</p>
          <p className="text-xl opacity-90">Confiance: {(hazard.confidence * 100).toFixed(0)}%</p>
          <button
            onClick={() => {
              setIsVisible(false);
              if (onDismiss) onDismiss();
            }}
            className="mt-8 px-8 py-4 bg-white text-red-600 rounded-lg text-xl font-bold hover:bg-gray-100"
          >
            Fermer (Appuyez ici)
          </button>
        </div>
      </div>
    );
  }

  // MEDIUM urgency: Top banner
  if (hazard.urgency === 'MEDIUM') {
    return (
      <div
        className={`fixed top-0 left-0 right-0 ${config.bgColor} ${config.textColor} border-b-4 ${config.borderColor} shadow-lg z-40 animate-slide-down`}
        role="alert"
        aria-live="assertive"
      >
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Icon className={config.iconSize} />
            <div>
              <h3 className="text-xl font-bold">{hazard.alert_message}</h3>
              <p className="text-sm opacity-90">
                {hazard.hazard_type} - {(hazard.confidence * 100).toFixed(0)}% sûr
              </p>
            </div>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              if (onDismiss) onDismiss();
            }}
            className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded"
          >
            ✕
          </button>
        </div>
      </div>
    );
  }

  // LOW urgency: Small notification
  return (
    <Alert
      className={`fixed bottom-4 right-4 ${config.bgColor} ${config.textColor} border-2 ${config.borderColor} shadow-lg max-w-sm z-30 animate-slide-up`}
    >
      <Icon className={config.iconSize} />
      <AlertTitle className="text-lg font-bold">{hazard.alert_message}</AlertTitle>
      <AlertDescription className="text-sm">
        {hazard.hazard_type} - Confiance: {(hazard.confidence * 100).toFixed(0)}%
      </AlertDescription>
      <button
        onClick={() => {
          setIsVisible(false);
          if (onDismiss) onDismiss();
        }}
        className="absolute top-2 right-2 text-white hover:text-gray-200"
      >
        ✕
      </button>
    </Alert>
  );
};

// Alert History Component
interface AlertHistoryProps {
  alerts: Hazard[];
  onFilter?: (type: string) => void;
}

export const AlertHistory: React.FC<AlertHistoryProps> = ({ alerts, onFilter }) => {
  const [selectedType, setSelectedType] = useState<string | null>(null);

  const filteredAlerts = selectedType
    ? alerts.filter((a) => a.hazard_type === selectedType)
    : alerts;

  const hazardTypes = Array.from(new Set(alerts.map((a) => a.hazard_type)));

  return (
    <div className="space-y-4">
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => {
            setSelectedType(null);
            if (onFilter) onFilter('all');
          }}
          className={`px-4 py-2 rounded ${
            selectedType === null ? 'bg-blue-600 text-white' : 'bg-gray-200'
          }`}
        >
          Tous ({alerts.length})
        </button>
        {hazardTypes.map((type) => (
          <button
            key={type}
            onClick={() => {
              setSelectedType(type);
              if (onFilter) onFilter(type);
            }}
            className={`px-4 py-2 rounded ${
              selectedType === type ? 'bg-blue-600 text-white' : 'bg-gray-200'
            }`}
          >
            {type} ({alerts.filter((a) => a.hazard_type === type).length})
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filteredAlerts.map((alert) => {
          const config = urgencyConfig[alert.urgency];
          const Icon = config.icon;
          return (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-2 ${config.borderColor} bg-white shadow`}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-8 h-8" />
                <div className="flex-1">
                  <p className="font-bold">{alert.alert_message}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(alert.timestamp).toLocaleString('fr-FR')}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded text-white text-sm ${config.bgColor}`}
                >
                  {alert.urgency}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
