/**
 * Interface de Chat Temps Réel
 */
import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Paperclip, Smile, Check, CheckCheck } from 'lucide-react';
import { chatWebSocket } from '@/lib/websocket';
import { format } from 'date-fns';

interface Message {
  id: string;
  senderId: string;
  senderName: string;
  content: string;
  timestamp: string;
  read: boolean;
  type: 'text' | 'image' | 'file';
}

interface ChatInterfaceProps {
  caseId: string;
  currentUserId: string;
  currentUserName: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  caseId,
  currentUserId,
  currentUserName,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    // Connexion WebSocket
    chatWebSocket.connect();

    const unsubscribeConnect = chatWebSocket.onConnect(() => {
      setIsConnected(true);
      // Rejoindre la room du cas
      chatWebSocket.send({
        type: 'join',
        caseId,
        userId: currentUserId,
        userName: currentUserName,
      });
    });

    const unsubscribeDisconnect = chatWebSocket.onDisconnect(() => {
      setIsConnected(false);
    });

    const unsubscribeMessage = chatWebSocket.onMessage((data) => {
      if (data.caseId !== caseId) return;

      switch (data.type) {
        case 'message':
          setMessages((prev) => [...prev, data.message]);
          scrollToBottom();
          break;
        case 'typing':
          if (data.userId !== currentUserId) {
            setIsTyping(true);
            clearTimeout(typingTimeoutRef.current);
            typingTimeoutRef.current = setTimeout(() => {
              setIsTyping(false);
            }, 2000);
          }
          break;
        case 'read':
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === data.messageId ? { ...msg, read: true } : msg
            )
          );
          break;
        case 'history':
          setMessages(data.messages);
          scrollToBottom();
          break;
      }
    });

    return () => {
      unsubscribeConnect();
      unsubscribeDisconnect();
      unsubscribeMessage();
      chatWebSocket.send({ type: 'leave', caseId, userId: currentUserId });
    };
  }, [caseId, currentUserId, currentUserName]);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleSend = () => {
    if (!inputValue.trim() || !isConnected) return;

    const message: Message = {
      id: `${Date.now()}-${currentUserId}`,
      senderId: currentUserId,
      senderName: currentUserName,
      content: inputValue,
      timestamp: new Date().toISOString(),
      read: false,
      type: 'text',
    };

    chatWebSocket.send({
      type: 'message',
      caseId,
      message,
    });

    setInputValue('');
  };

  const handleTyping = () => {
    if (isConnected) {
      chatWebSocket.send({
        type: 'typing',
        caseId,
        userId: currentUserId,
        userName: currentUserName,
      });
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Discussion</CardTitle>
          <Badge variant={isConnected ? 'default' : 'secondary'}>
            {isConnected ? '🟢 Connecté' : '🔴 Déconnecté'}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-hidden p-0 flex flex-col">
        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((message) => {
              const isOwn = message.senderId === currentUserId;
              return (
                <div
                  key={message.id}
                  className={`flex gap-3 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <Avatar className="h-8 w-8 flex-shrink-0">
                    <AvatarFallback>
                      {message.senderName.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>

                  <div className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'} max-w-[70%]`}>
                    {!isOwn && (
                      <span className="text-xs text-muted-foreground mb-1">
                        {message.senderName}
                      </span>
                    )}
                    <div
                      className={`rounded-lg px-4 py-2 ${
                        isOwn
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap break-words">
                        {message.content}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(message.timestamp), 'HH:mm')}
                      </span>
                      {isOwn && (
                        <span className="text-xs">
                          {message.read ? (
                            <CheckCheck className="h-3 w-3 text-blue-500" />
                          ) : (
                            <Check className="h-3 w-3 text-muted-foreground" />
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

            {isTyping && (
              <div className="flex gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>...</AvatarFallback>
                </Avatar>
                <div className="bg-muted rounded-lg px-4 py-2">
                  <div className="flex gap-1">
                    <span className="animate-bounce">●</span>
                    <span className="animate-bounce delay-100">●</span>
                    <span className="animate-bounce delay-200">●</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="flex-shrink-0">
              <Paperclip className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="flex-shrink-0">
              <Smile className="h-5 w-5" />
            </Button>
            <Input
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                handleTyping();
              }}
              onKeyPress={handleKeyPress}
              placeholder="Écrivez votre message..."
              disabled={!isConnected}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!inputValue.trim() || !isConnected}
              size="icon"
              className="flex-shrink-0"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
