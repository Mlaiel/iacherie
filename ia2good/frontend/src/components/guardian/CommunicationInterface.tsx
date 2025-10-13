import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Mic, MicOff, Volume2, Send, Save, Trash2 } from 'lucide-react';

interface Message {
  id: string;
  type: 'speech' | 'text';
  content: string;
  timestamp: Date;
  speaker?: 'user' | 'other';
}

interface CommunicationInterfaceProps {
  onSpeechToText?: (text: string) => void;
  onTextToSpeech?: (text: string) => void;
  mode?: 'continuous' | 'push-to-talk' | 'text-only';
}

export const CommunicationInterface: React.FC<CommunicationInterfaceProps> = ({
  onSpeechToText,
  onTextToSpeech,
  mode = 'push-to-talk',
}) => {
  const [isListening, setIsListening] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = mode === 'continuous';
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'fr-FR';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');

        setCurrentTranscript(transcript);

        // If final result
        if (event.results[event.results.length - 1].isFinal) {
          const newMessage: Message = {
            id: Date.now().toString(),
            type: 'speech',
            content: transcript,
            timestamp: new Date(),
            speaker: 'other',
          };
          setMessages((prev) => [...prev, newMessage]);
          setCurrentTranscript('');
          if (onSpeechToText) onSpeechToText(transcript);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        if (mode === 'continuous' && isListening) {
          recognitionRef.current?.start();
        } else {
          setIsListening(false);
        }
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [mode, isListening, onSpeechToText]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
      setIsListening(true);
      if ('vibrate' in navigator) navigator.vibrate(50);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      if ('vibrate' in navigator) navigator.vibrate(50);
    }
  };

  const handleTextToSpeech = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'fr-FR';
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);

      const newMessage: Message = {
        id: Date.now().toString(),
        type: 'text',
        content: text,
        timestamp: new Date(),
        speaker: 'user',
      };
      setMessages((prev) => [...prev, newMessage]);
      if (onTextToSpeech) onTextToSpeech(text);
    }
  };

  const handleSendText = () => {
    if (textInput.trim()) {
      handleTextToSpeech(textInput);
      setTextInput('');
    }
  };

  const handleSaveConversation = () => {
    const conversationText = messages
      .map(
        (msg) =>
          `[${msg.timestamp.toLocaleTimeString()}] ${msg.speaker === 'user' ? 'Vous' : 'Interlocuteur'}: ${msg.content}`
      )
      .join('\n');

    const blob = new Blob([conversationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation_${new Date().toISOString()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClearConversation = () => {
    setMessages([]);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full">
      {/* Transcription Area */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>🎤 Écoute (Speech-to-Text)</span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSaveConversation}
                disabled={messages.length === 0}
              >
                <Save className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearConversation}
                disabled={messages.length === 0}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto border rounded-lg p-4 mb-4 bg-gray-50 min-h-[300px]">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`mb-3 p-3 rounded-lg ${
                  msg.speaker === 'user'
                    ? 'bg-blue-100 ml-auto max-w-[80%]'
                    : 'bg-white mr-auto max-w-[80%]'
                }`}
              >
                <p className="text-sm text-gray-600 mb-1">
                  {msg.speaker === 'user' ? 'Vous' : 'Interlocuteur'} -{' '}
                  {msg.timestamp.toLocaleTimeString()}
                </p>
                <p className="text-lg">{msg.content}</p>
              </div>
            ))}
            {currentTranscript && (
              <div className="p-3 bg-yellow-50 rounded-lg border-2 border-yellow-300 animate-pulse">
                <p className="text-sm text-gray-600 mb-1">En cours...</p>
                <p className="text-lg opacity-70">{currentTranscript}</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Mode Controls */}
          <div className="flex justify-center gap-4">
            {mode === 'push-to-talk' && (
              <Button
                size="lg"
                variant={isListening ? 'destructive' : 'default'}
                onMouseDown={startListening}
                onMouseUp={stopListening}
                onTouchStart={startListening}
                onTouchEnd={stopListening}
                className="w-full"
              >
                {isListening ? (
                  <>
                    <MicOff className="w-6 h-6 mr-2" />
                    Relâcher pour arrêter
                  </>
                ) : (
                  <>
                    <Mic className="w-6 h-6 mr-2" />
                    Appuyer pour parler
                  </>
                )}
              </Button>
            )}
            {mode === 'continuous' && (
              <Button
                size="lg"
                variant={isListening ? 'destructive' : 'default'}
                onClick={isListening ? stopListening : startListening}
                className="w-full"
              >
                {isListening ? (
                  <>
                    <MicOff className="w-6 h-6 mr-2" />
                    Arrêter l'écoute
                  </>
                ) : (
                  <>
                    <Mic className="w-6 h-6 mr-2" />
                    Démarrer l'écoute
                  </>
                )}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Text-to-Speech Area */}
      <Card className="flex flex-col">
        <CardHeader>
          <CardTitle>🔊 Parler (Text-to-Speech)</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          <Textarea
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Tapez votre message ici..."
            className="flex-1 mb-4 text-lg min-h-[300px]"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                handleSendText();
              }
            }}
          />
          <Button size="lg" onClick={handleSendText} disabled={!textInput.trim()} className="w-full">
            <Volume2 className="w-6 h-6 mr-2" />
            Lire à voix haute
          </Button>

          {/* Quick Phrases */}
          <div className="mt-4">
            <p className="text-sm text-gray-600 mb-2">Phrases rapides :</p>
            <div className="grid grid-cols-2 gap-2">
              {[
                'Bonjour',
                'Merci',
                'Oui',
                'Non',
                "S'il vous plaît",
                'Au revoir',
              ].map((phrase) => (
                <Button
                  key={phrase}
                  variant="outline"
                  size="sm"
                  onClick={() => handleTextToSpeech(phrase)}
                >
                  {phrase}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
