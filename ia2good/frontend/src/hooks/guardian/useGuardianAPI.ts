import { useState } from 'react';

const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface SOSTriggerData {
  location: {
    latitude: number;
    longitude: number;
  };
  trigger_type: 'manual' | 'fall_detection' | 'panic_button' | 'auto';
}

export interface SOSAlert {
  id: string;
  user_id: string;
  location: {
    latitude: number;
    longitude: number;
  };
  address?: string;
  trigger_type: string;
  status: string;
  countdown_seconds?: number;
  contacts_notified: string[];
  created_at: string;
}

export interface HazardDetection {
  id: string;
  hazard_type: string;
  confidence: number;
  urgency: 'HIGH' | 'MEDIUM' | 'LOW';
  alert_message: string;
  timestamp: string;
}

// SOS Hooks
export const useSOSTrigger = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const triggerSOS = async (data: SOSTriggerData): Promise<SOSAlert | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/guardian/sos/trigger`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('Failed to trigger SOS');
      }

      const alert = await response.json();
      return alert;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { triggerSOS, isLoading, error };
};

export const useSOSCancel = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cancelSOS = async (alertId: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/guardian/sos/${alertId}/cancel`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to cancel SOS');
      }

      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return { cancelSOS, isLoading, error };
};

// Hazard Detection Hooks
export const useHazardDetection = () => {
  const [isListening, setIsListening] = useState(false);
  const [currentHazard, setCurrentHazard] = useState<HazardDetection | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startDetection = () => {
    setIsListening(true);
    // TODO: Implement WebSocket connection for real-time hazard detection
    console.log('Hazard detection started');
  };

  const stopDetection = () => {
    setIsListening(false);
    // TODO: Close WebSocket connection
    console.log('Hazard detection stopped');
  };

  const submitFeedback = async (
    detectionId: string,
    feedback: 'correct' | 'false_positive' | 'missed' | 'too_sensitive',
    comment?: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/guardian/hazards/${detectionId}/feedback`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({ user_feedback: feedback, feedback_comment: comment }),
        }
      );

      return response.ok;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    }
  };

  return {
    isListening,
    currentHazard,
    error,
    startDetection,
    stopDetection,
    submitFeedback,
  };
};

// Communication Hooks
export const useSpeechToText = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const transcribeAudio = async (audioBlob: Blob, language: string = 'fr-FR') => {
    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('language', language);

      const response = await fetch(`${API_BASE_URL}/guardian/speech-to-text`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const result = await response.json();
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  return { transcribeAudio, isProcessing, error };
};

export const useTextToSpeech = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const synthesizeSpeech = async (
    text: string,
    language: string = 'fr-FR',
    voice: string = 'default'
  ) => {
    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/guardian/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ text, language, voice }),
      });

      if (!response.ok) {
        throw new Error('Speech synthesis failed');
      }

      const audioBlob = await response.blob();
      return audioBlob;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  return { synthesizeSpeech, isProcessing, error };
};

// Accessibility Settings Hooks
export const useAccessibilitySettings = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const saveSettings = async (settings: any): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/guardian/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify(settings),
      });

      return response.ok;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/guardian/profile`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load settings');
      }

      const settings = await response.json();
      return settings;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  return { saveSettings, loadSettings, isLoading, error };
};
