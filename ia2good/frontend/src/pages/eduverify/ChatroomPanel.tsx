/**
 * Chatroom Panel - Salle de discussion accessible avec WebSocket
 * Interface avec TTS, captions, alertes visuelles
 */
import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Volume2, VolumeX, Eye, AlertCircle, Users, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface Message {
  id: string;
  user_id: string;
  username: string;
  content: string;
  timestamp: string;
  message_type: string;
}

interface Room {
  id: string;
  name: string;
  description: string;
  active_users: number;
}

const ChatroomPanel: React.FC = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [username, setUsername] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Accessibility settings
  const [ttsEnabled, setTtsEnabled] = useState(false);
  const [captionsEnabled, setCaptionsEnabled] = useState(true);
  const [visualAlertsEnabled, setVisualAlertsEnabled] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchRooms();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchRooms = async () => {
    try {
      const response = await fetch('http://localhost:8002/eduverify/chatrooms');
      if (response.ok) {
        const data = await response.json();
        setRooms(data.items || []);
      }
    } catch (err) {
      console.error('Failed to fetch rooms:', err);
    }
  };

  const connectToRoom = (roomId: string) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(`ws://localhost:8002/ws/chatroom/${roomId}?user_id=${username}`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setSelectedRoom(roomId);
      setError(null);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'history') {
        setMessages(data.messages || []);
      } else if (data.type === 'message') {
        const newMessage: Message = {
          id: data.id || `msg_${Date.now()}`,
          user_id: data.user_id,
          username: data.username || data.user_id,
          content: data.content,
          timestamp: data.timestamp || new Date().toISOString(),
          message_type: data.message_type || 'text',
        };
        
        setMessages(prev => [...prev, newMessage]);

        // TTS for new messages
        if (ttsEnabled && data.user_id !== username) {
          speak(data.content);
        }

        // Visual alert
        if (visualAlertsEnabled) {
          flashScreen();
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Erreur de connexion WebSocket');
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    wsRef.current = ws;
  };

  const sendMessage = () => {
    if (!inputMessage.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }

    wsRef.current.send(JSON.stringify({
      type: 'message',
      content: inputMessage,
      user_id: username,
      username: username,
    }));

    setInputMessage('');
  };

  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'fr-FR';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const flashScreen = () => {
    document.body.style.backgroundColor = '#ffeb3b';
    setTimeout(() => {
      document.body.style.backgroundColor = '';
    }, 200);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Room List Sidebar */}
      <div className="lg:col-span-1 space-y-6">
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-lg">
              <Users className="h-5 w-5 text-purple-600" />
              <span>Salles</span>
            </CardTitle>
            <CardDescription>
              Salles de discussion disponibles
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {rooms.map(room => (
                <Card
                  key={room.id}
                  className={`cursor-pointer hover:shadow-md transition-shadow ${
                    selectedRoom === room.id ? 'border-purple-500 border-2' : ''
                  }`}
                  onClick={() => connectToRoom(room.id)}
                >
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-sm">{room.name}</h4>
                        <Badge variant="outline">
                          {room.active_users} <Users className="h-3 w-3 ml-1" />
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-600">{room.description}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {rooms.length === 0 && (
                <p className="text-sm text-gray-600 text-center py-4">
                  Aucune salle disponible
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Accessibility Settings */}
        <Card className="bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-900 dark:text-green-100 text-sm flex items-center space-x-2">
              <Eye className="h-4 w-4" />
              <span>Accessibilité</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="tts" className="text-xs">
                Synthèse vocale (TTS)
              </Label>
              <Switch
                id="tts"
                checked={ttsEnabled}
                onCheckedChange={setTtsEnabled}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="captions" className="text-xs">
                Sous-titres
              </Label>
              <Switch
                id="captions"
                checked={captionsEnabled}
                onCheckedChange={setCaptionsEnabled}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="visual-alerts" className="text-xs">
                Alertes visuelles
              </Label>
              <Switch
                id="visual-alerts"
                checked={visualAlertsEnabled}
                onCheckedChange={setVisualAlertsEnabled}
              />
            </div>
          </CardContent>
        </Card>

        {/* Connection Status */}
        <Card className={isConnected ? 'border-green-500' : 'border-gray-300'}>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold">Statut</span>
              <Badge variant={isConnected ? 'default' : 'secondary'}>
                {isConnected ? 'Connecté' : 'Déconnecté'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chat Area */}
      <div className="lg:col-span-3">
        <Card className="shadow-xl h-[calc(100vh-200px)] flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageCircle className="h-6 w-6 text-blue-600" />
              <span>
                {selectedRoom
                  ? rooms.find(r => r.id === selectedRoom)?.name || 'Chat'
                  : 'Sélectionnez une salle'}
              </span>
            </CardTitle>
            <CardDescription>
              {isConnected ? (
                <span className="flex items-center space-x-2">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  <span>Connecté en tant que {username}</span>
                </span>
              ) : (
                'Sélectionnez une salle pour commencer'
              )}
            </CardDescription>
          </CardHeader>

          {error && (
            <div className="px-6">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            </div>
          )}

          {/* Messages Area */}
          <CardContent className="flex-1 overflow-y-auto space-y-3 px-6">
            {!selectedRoom ? (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                <MessageCircle className="h-16 w-16 text-gray-300" />
                <p className="text-gray-600">
                  Sélectionnez une salle de discussion pour commencer à discuter
                </p>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                <p className="text-gray-600">Chargement de l'historique...</p>
              </div>
            ) : (
              <>
                {messages.map((message) => {
                  const isOwnMessage = message.user_id === username;
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg p-3 ${
                          isOwnMessage
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-xs font-semibold">
                            {message.username}
                          </span>
                          <span className="text-xs opacity-75">
                            {new Date(message.timestamp).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>
                        <p className="text-sm">{message.content}</p>
                        {captionsEnabled && !isOwnMessage && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="mt-1 p-0 h-auto text-xs"
                            onClick={() => speak(message.content)}
                          >
                            {ttsEnabled ? (
                              <Volume2 className="h-3 w-3" />
                            ) : (
                              <VolumeX className="h-3 w-3" />
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </>
            )}
          </CardContent>

          {/* Input Area */}
          {selectedRoom && isConnected && (
            <div className="border-t p-4">
              <div className="flex items-center space-x-2">
                <Input
                  placeholder="Tapez votre message..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  className="flex-1"
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim()}
                  size="icon"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default ChatroomPanel;
