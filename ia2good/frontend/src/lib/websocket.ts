/**
 * WebSocket Client pour Chat en Temps Réel
 * Gère la connexion WebSocket et les événements de chat
 */

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8765';

type MessageHandler = (data: any) => void;
type ConnectHandler = () => void;
type DisconnectHandler = () => void;

class ChatWebSocketClient {
  private ws: WebSocket | null = null;
  private baseUrl: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers = new Set<MessageHandler>();
  private connectHandlers = new Set<ConnectHandler>();
  private disconnectHandlers = new Set<DisconnectHandler>();
  private isManualClose = false;

  constructor(baseUrl: string = WS_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Connecte au serveur WebSocket
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      this.connectHandlers.forEach(handler => handler());
      return;
    }

    this.isManualClose = false;

    try {
      const wsUrl = this.baseUrl;
      console.log('Connecting to WebSocket:', wsUrl);
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        this.connectHandlers.forEach(handler => {
          try {
            handler();
          } catch (error) {
            console.error('Error in connect handler:', error);
          }
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', data);
          
          this.messageHandlers.forEach(handler => {
            try {
              handler(data);
            } catch (error) {
              console.error('Error in message handler:', error);
            }
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (event) => {
        console.error('❌ WebSocket error:', event);
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        
        this.disconnectHandlers.forEach(handler => {
          try {
            handler();
          } catch (error) {
            console.error('Error in disconnect handler:', error);
          }
        });
        
        if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.attemptReconnect();
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }

  /**
   * Déconnecte du serveur WebSocket
   */
  disconnect(): void {
    this.isManualClose = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Envoie un message via WebSocket
   */
  send(data: any): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket is not connected, cannot send:', data);
      return;
    }

    this.ws.send(JSON.stringify(data));
    console.log('📤 Message sent:', data);
  }

  /**
   * S'abonne aux messages
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  /**
   * S'abonne à la connexion
   */
  onConnect(handler: ConnectHandler): () => void {
    this.connectHandlers.add(handler);
    return () => this.connectHandlers.delete(handler);
  }

  /**
   * S'abonne à la déconnexion
   */
  onDisconnect(handler: DisconnectHandler): () => void {
    this.disconnectHandlers.add(handler);
    return () => this.disconnectHandlers.delete(handler);
  }

  /**
   * Tente une reconnexion avec backoff exponentiel
   */
  private attemptReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

    setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Vérifie si le WebSocket est connecté
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const chatWebSocket = new ChatWebSocketClient();
