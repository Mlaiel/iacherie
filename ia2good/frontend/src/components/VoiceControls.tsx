/*
 * Owner: Fahed Mlaiel
 * Contact: mlaiel@live.de
 * Notice: Attribution to Fahed Mlaiel is mandatory in all copies, forks, and derivatives.
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Microphone, MicrophoneSlash, SpeakerHigh } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { useKV } from '@/hooks/useKV';

interface VoiceControlsProps {
  onVoiceInput?: (text: string) => void;
  isListening?: boolean;
  disabled?: boolean;
}

export function VoiceControls({ onVoiceInput, isListening = false, disabled = false }: VoiceControlsProps) {
  const [isSupported, setIsSupported] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const [accessibilitySettings] = useKV('accessibility-settings', {
    voiceInput: false,
    screenReader: false
  });

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setIsSupported(true);
      
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        setIsRecording(true);
        toast.info('Listening... Speak now');
      };

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0]?.transcript;
        if (transcript && onVoiceInput) {
          onVoiceInput(transcript);
          toast.success(`Voice input received: "${transcript}"`);
        }
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        toast.error(`Voice input error: ${event.error}`);
        setIsRecording(false);
      };

      recognitionInstance.onend = () => {
        setIsRecording(false);
      };

      setRecognition(recognitionInstance);
    } else {
      setIsSupported(false);
    }
  }, [onVoiceInput]);

  const startListening = () => {
    if (recognition && !isRecording) {
      try {
        recognition.start();
      } catch (error) {
        console.error('Failed to start voice recognition:', error);
        toast.error('Failed to start voice input');
      }
    }
  };

  const stopListening = () => {
    if (recognition && isRecording) {
      recognition.stop();
    }
  };

  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      utterance.pitch = 1;
      utterance.volume = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  // Don't render if voice input is disabled in accessibility settings
  if (!accessibilitySettings.voiceInput || !isSupported) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      {/* Voice Input Button */}
      <Button
        variant={isRecording ? "destructive" : "outline"}
        size="sm"
        onClick={isRecording ? stopListening : startListening}
        disabled={disabled || isListening}
        className="flex items-center gap-2"
        aria-label={isRecording ? "Stop voice input" : "Start voice input"}
      >
        {isRecording ? (
          <MicrophoneSlash size={16} />
        ) : (
          <Microphone size={16} />
        )}
        <span className="hidden sm:inline">
          {isRecording ? 'Stop' : 'Voice'}
        </span>
      </Button>

      {/* Status Badge */}
      {isRecording && (
        <Badge variant="destructive" className="animate-pulse">
          <span className="w-2 h-2 bg-white rounded-full mr-1"></span>
          Recording
        </Badge>
      )}

      {/* Text-to-Speech Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={() => speak('Welcome to IA2GOOD. Use voice commands to report assistance needs or navigate the app.')}
        disabled={disabled}
        className="flex items-center gap-2"
        aria-label="Hear app description"
        title="Click to hear app description"
      >
        <SpeakerHigh size={16} />
        <span className="hidden sm:inline">Speak</span>
      </Button>
    </div>
  );
}

// Extended Speech Recognition interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  maxAlternatives: number;
  serviceURI: string;
  grammars: any; // SpeechGrammarList not widely supported
  onaudiostart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onaudioend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onerror: ((this: SpeechRecognition, ev: any) => any) | null;
  onnomatch: ((this: SpeechRecognition, ev: any) => any) | null;
  onresult: ((this: SpeechRecognition, ev: any) => any) | null;
  onsoundstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onsoundend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onspeechstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  onspeechend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
  abort(): void;
  start(): void;
  stop(): void;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}