/**
 * Ainflue Desktop - Collaboration Desktop Client
 * 
 * Real-time collaboration system for desktop application
 * 
 * Author: Fahed Mlaiel (mlaiel@live.de)
 * Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
 * 
 * ⚠️ LEGAL NOTICE: This software is the exclusive intellectual property of Fahed Mlaiel.
 * Any unauthorized use, copying, or distribution is strictly prohibited.
 */

const { EventEmitter } = require('events');
const WebSocket = require('ws');
const log = require('electron-log');
const crypto = require('crypto');

class CollaborationDesktopClient extends EventEmitter {
  constructor() {
    super();
    this.ws = null;
    this.connectionState = 'disconnected';
    this.sessionId = null;
    this.userId = null;
    this.currentRoom = null;
    this.collaborators = new Map();
    this.pendingMessages = [];
    this.messageQueue = [];
    this.heartbeatInterval = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectTimeout = null;
    
    // Collaboration features
    this.cursors = new Map();
    this.selections = new Map();
    this.presence = new Map();
    this.sharedState = {};
    this.operationalTransform = new OperationalTransform();
    
    // Configuration
    this.config = {
      serverUrl: process.env.COLLABORATION_SERVER_URL || 'wss://localhost:3001/collaboration',
      heartbeatInterval: 30000,
      reconnectDelay: 5000,
      messageTimeout: 10000,
      maxMessageQueueSize: 1000
    };
  }

  async initialize(userId, credentials) {
    try {
      log.info('Initializing Collaboration Desktop Client...');
      
      this.userId = userId;
      this.sessionId = crypto.randomUUID();
      
      // Setup event handlers
      this.setupEventHandlers();
      
      // Connect to collaboration server
      await this.connect(credentials);
      
      log.info('Collaboration Desktop Client initialized successfully');
      this.emit('client:ready');
      
    } catch (error) {
      log.error('Failed to initialize Collaboration Desktop Client:', error);
      throw error;
    }
  }

  async connect(credentials) {
    return new Promise((resolve, reject) => {
      try {
        log.info(`Connecting to collaboration server: ${this.config.serverUrl}`);
        
        this.ws = new WebSocket(this.config.serverUrl, {
          headers: {
            'Authorization': `Bearer ${credentials.token}`,
            'User-Id': this.userId,
            'Session-Id': this.sessionId
          }
        });

        this.ws.on('open', () => {
          log.info('Connected to collaboration server');
          this.connectionState = 'connected';
          this.reconnectAttempts = 0;
          
          // Start heartbeat
          this.startHeartbeat();
          
          // Send pending messages
          this.processPendingMessages();
          
          this.emit('connection:established');
          resolve();
        });

        this.ws.on('message', (data) => {
          this.handleMessage(data);
        });

        this.ws.on('close', (code, reason) => {
          log.warn(`Collaboration connection closed: ${code} - ${reason}`);
          this.connectionState = 'disconnected';
          this.stopHeartbeat();
          this.emit('connection:closed', { code, reason });
          
          // Attempt reconnection
          this.attemptReconnection();
        });

        this.ws.on('error', (error) => {
          log.error('Collaboration connection error:', error);
          this.connectionState = 'error';
          this.emit('connection:error', error);
          reject(error);
        });

        // Connection timeout
        setTimeout(() => {
          if (this.connectionState !== 'connected') {
            reject(new Error('Connection timeout'));
          }
        }, 10000);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  async joinRoom(roomId, roomType = 'project') {
    try {
      if (this.connectionState !== 'connected') {
        throw new Error('Not connected to collaboration server');
      }

      const message = {
        type: 'join_room',
        data: {
          roomId,
          roomType,
          userId: this.userId,
          sessionId: this.sessionId,
          capabilities: [
            'real_time_editing',
            'cursor_tracking',
            'voice_chat',
            'screen_sharing',
            'file_sharing'
          ]
        }
      };

      await this.sendMessage(message);
      this.currentRoom = { id: roomId, type: roomType };
      
      log.info(`Joined collaboration room: ${roomId} (${roomType})`);
      this.emit('room:joined', { roomId, roomType });
      
    } catch (error) {
      log.error(`Failed to join room ${roomId}:`, error);
      throw error;
    }
  }

  async leaveRoom() {
    try {
      if (!this.currentRoom) {
        return;
      }

      const message = {
        type: 'leave_room',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          sessionId: this.sessionId
        }
      };

      await this.sendMessage(message);
      
      // Clear collaboration state
      this.collaborators.clear();
      this.cursors.clear();
      this.selections.clear();
      this.presence.clear();
      this.sharedState = {};
      
      const roomId = this.currentRoom.id;
      this.currentRoom = null;
      
      log.info(`Left collaboration room: ${roomId}`);
      this.emit('room:left', { roomId });
      
    } catch (error) {
      log.error('Failed to leave room:', error);
      throw error;
    }
  }

  async sendTextOperation(operation) {
    try {
      if (!this.currentRoom) {
        throw new Error('Not in a collaboration room');
      }

      // Apply operational transformation
      const transformedOp = this.operationalTransform.transform(operation);
      
      const message = {
        type: 'text_operation',
        data: {
          roomId: this.currentRoom.id,
          operation: transformedOp,
          userId: this.userId,
          timestamp: Date.now()
        }
      };

      await this.sendMessage(message);
      this.emit('operation:sent', { operation: transformedOp });
      
    } catch (error) {
      log.error('Failed to send text operation:', error);
      throw error;
    }
  }

  async updateCursor(position, selection = null) {
    try {
      if (!this.currentRoom) {
        return;
      }

      const message = {
        type: 'cursor_update',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          position,
          selection,
          timestamp: Date.now()
        }
      };

      await this.sendMessage(message);
      
    } catch (error) {
      log.warn('Failed to update cursor:', error);
    }
  }

  async shareScreen(screenId) {
    try {
      if (!this.currentRoom) {
        throw new Error('Not in a collaboration room');
      }

      const message = {
        type: 'screen_share_start',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          screenId,
          quality: 'high'
        }
      };

      await this.sendMessage(message);
      
      log.info(`Started screen sharing: ${screenId}`);
      this.emit('screen_share:started', { screenId });
      
    } catch (error) {
      log.error('Failed to start screen sharing:', error);
      throw error;
    }
  }

  async stopScreenShare() {
    try {
      if (!this.currentRoom) {
        return;
      }

      const message = {
        type: 'screen_share_stop',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId
        }
      };

      await this.sendMessage(message);
      
      log.info('Stopped screen sharing');
      this.emit('screen_share:stopped');
      
    } catch (error) {
      log.error('Failed to stop screen sharing:', error);
      throw error;
    }
  }

  async startVoiceChat() {
    try {
      if (!this.currentRoom) {
        throw new Error('Not in a collaboration room');
      }

      const message = {
        type: 'voice_chat_start',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          audioSettings: {
            sampleRate: 48000,
            channels: 2,
            bitRate: 128
          }
        }
      };

      await this.sendMessage(message);
      
      log.info('Started voice chat');
      this.emit('voice_chat:started');
      
    } catch (error) {
      log.error('Failed to start voice chat:', error);
      throw error;
    }
  }

  async stopVoiceChat() {
    try {
      if (!this.currentRoom) {
        return;
      }

      const message = {
        type: 'voice_chat_stop',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId
        }
      };

      await this.sendMessage(message);
      
      log.info('Stopped voice chat');
      this.emit('voice_chat:stopped');
      
    } catch (error) {
      log.error('Failed to stop voice chat:', error);
      throw error;
    }
  }

  async shareFile(filePath, fileData) {
    try {
      if (!this.currentRoom) {
        throw new Error('Not in a collaboration room');
      }

      const fileId = crypto.randomUUID();
      const message = {
        type: 'file_share',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          fileId,
          fileName: filePath,
          fileSize: fileData.length,
          mimeType: this.getMimeType(filePath),
          checksum: crypto.createHash('sha256').update(fileData).digest('hex')
        }
      };

      await this.sendMessage(message);
      
      // Send file data in chunks
      await this.sendFileChunks(fileId, fileData);
      
      log.info(`Shared file: ${filePath} (${fileId})`);
      this.emit('file:shared', { fileId, fileName: filePath });
      
    } catch (error) {
      log.error('Failed to share file:', error);
      throw error;
    }
  }

  async requestFileDownload(fileId) {
    try {
      if (!this.currentRoom) {
        throw new Error('Not in a collaboration room');
      }

      const message = {
        type: 'file_download_request',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          fileId
        }
      };

      await this.sendMessage(message);
      
      log.info(`Requested file download: ${fileId}`);
      
    } catch (error) {
      log.error('Failed to request file download:', error);
      throw error;
    }
  }

  async updatePresence(status, activity = null) {
    try {
      if (!this.currentRoom) {
        return;
      }

      const message = {
        type: 'presence_update',
        data: {
          roomId: this.currentRoom.id,
          userId: this.userId,
          status, // 'online', 'away', 'busy', 'offline'
          activity,
          timestamp: Date.now()
        }
      };

      await this.sendMessage(message);
      
    } catch (error) {
      log.warn('Failed to update presence:', error);
    }
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data.toString());
      
      switch (message.type) {
        case 'user_joined':
          this.handleUserJoined(message.data);
          break;
          
        case 'user_left':
          this.handleUserLeft(message.data);
          break;
          
        case 'text_operation':
          this.handleTextOperation(message.data);
          break;
          
        case 'cursor_update':
          this.handleCursorUpdate(message.data);
          break;
          
        case 'presence_update':
          this.handlePresenceUpdate(message.data);
          break;
          
        case 'screen_share_start':
          this.handleScreenShareStart(message.data);
          break;
          
        case 'screen_share_stop':
          this.handleScreenShareStop(message.data);
          break;
          
        case 'voice_chat_start':
          this.handleVoiceChatStart(message.data);
          break;
          
        case 'voice_chat_stop':
          this.handleVoiceChatStop(message.data);
          break;
          
        case 'file_share':
          this.handleFileShare(message.data);
          break;
          
        case 'file_chunk':
          this.handleFileChunk(message.data);
          break;
          
        case 'error':
          this.handleError(message.data);
          break;
          
        case 'pong':
          // Heartbeat response
          break;
          
        default:
          log.warn(`Unknown message type: ${message.type}`);
      }
      
    } catch (error) {
      log.error('Failed to handle message:', error);
    }
  }

  handleUserJoined(data) {
    const { userId, userInfo } = data;
    this.collaborators.set(userId, userInfo);
    
    log.info(`User joined collaboration: ${userInfo.name} (${userId})`);
    this.emit('user:joined', { userId, userInfo });
  }

  handleUserLeft(data) {
    const { userId } = data;
    const userInfo = this.collaborators.get(userId);
    
    this.collaborators.delete(userId);
    this.cursors.delete(userId);
    this.selections.delete(userId);
    this.presence.delete(userId);
    
    log.info(`User left collaboration: ${userId}`);
    this.emit('user:left', { userId, userInfo });
  }

  handleTextOperation(data) {
    const { operation, userId } = data;
    
    // Apply operational transformation
    const transformedOp = this.operationalTransform.apply(operation);
    
    this.emit('operation:received', { operation: transformedOp, userId });
  }

  handleCursorUpdate(data) {
    const { userId, position, selection } = data;
    
    this.cursors.set(userId, { position, selection, timestamp: Date.now() });
    this.emit('cursor:updated', { userId, position, selection });
  }

  handlePresenceUpdate(data) {
    const { userId, status, activity } = data;
    
    this.presence.set(userId, { status, activity, timestamp: Date.now() });
    this.emit('presence:updated', { userId, status, activity });
  }

  handleScreenShareStart(data) {
    const { userId, screenId } = data;
    
    log.info(`User started screen sharing: ${userId} (${screenId})`);
    this.emit('screen_share:user_started', { userId, screenId });
  }

  handleScreenShareStop(data) {
    const { userId } = data;
    
    log.info(`User stopped screen sharing: ${userId}`);
    this.emit('screen_share:user_stopped', { userId });
  }

  handleVoiceChatStart(data) {
    const { userId } = data;
    
    log.info(`User started voice chat: ${userId}`);
    this.emit('voice_chat:user_started', { userId });
  }

  handleVoiceChatStop(data) {
    const { userId } = data;
    
    log.info(`User stopped voice chat: ${userId}`);
    this.emit('voice_chat:user_stopped', { userId });
  }

  handleFileShare(data) {
    const { userId, fileId, fileName, fileSize } = data;
    
    log.info(`User shared file: ${userId} - ${fileName} (${fileId})`);
    this.emit('file:received', { userId, fileId, fileName, fileSize });
  }

  handleFileChunk(data) {
    // Handle file chunk reception
    this.emit('file:chunk_received', data);
  }

  handleError(data) {
    log.error('Collaboration error:', data);
    this.emit('collaboration:error', data);
  }

  async sendMessage(message) {
    return new Promise((resolve, reject) => {
      if (this.connectionState !== 'connected') {
        this.pendingMessages.push({ message, resolve, reject });
        return;
      }

      try {
        const messageId = crypto.randomUUID();
        const envelope = {
          id: messageId,
          timestamp: Date.now(),
          ...message
        };

        this.ws.send(JSON.stringify(envelope));
        
        // Set timeout for response
        setTimeout(() => {
          reject(new Error('Message timeout'));
        }, this.config.messageTimeout);
        
        resolve(messageId);
        
      } catch (error) {
        reject(error);
      }
    });
  }

  async sendFileChunks(fileId, fileData) {
    const chunkSize = 64 * 1024; // 64KB chunks
    const totalChunks = Math.ceil(fileData.length / chunkSize);
    
    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, fileData.length);
      const chunk = fileData.slice(start, end);
      
      const message = {
        type: 'file_chunk',
        data: {
          fileId,
          chunkIndex: i,
          totalChunks,
          data: chunk.toString('base64')
        }
      };
      
      await this.sendMessage(message);
    }
  }

  processPendingMessages() {
    while (this.pendingMessages.length > 0) {
      const { message, resolve, reject } = this.pendingMessages.shift();
      this.sendMessage(message).then(resolve).catch(reject);
    }
  }

  startHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    
    this.heartbeatInterval = setInterval(() => {
      if (this.connectionState === 'connected') {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, this.config.heartbeatInterval);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  attemptReconnection() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      log.error('Max reconnection attempts reached');
      this.emit('connection:failed');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    log.info(`Attempting reconnection in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    this.reconnectTimeout = setTimeout(() => {
      this.connect().catch((error) => {
        log.warn('Reconnection failed:', error);
        this.attemptReconnection();
      });
    }, delay);
  }

  setupEventHandlers() {
    // Setup event handlers for different collaboration features
    this.on('operation:received', (data) => {
      // Handle received operations for real-time editing
    });
    
    this.on('cursor:updated', (data) => {
      // Handle cursor position updates
    });
    
    this.on('presence:updated', (data) => {
      // Handle presence status updates
    });
  }

  getMimeType(filePath) {
    // Simple MIME type detection based on file extension
    const ext = filePath.split('.').pop().toLowerCase();
    const mimeTypes = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'mp4': 'video/mp4',
      'mp3': 'audio/mpeg',
      'wav': 'audio/wav',
      'pdf': 'application/pdf',
      'txt': 'text/plain',
      'json': 'application/json'
    };
    
    return mimeTypes[ext] || 'application/octet-stream';
  }

  // Getters
  getCollaborators() {
    return Array.from(this.collaborators.entries());
  }

  getCursors() {
    return Array.from(this.cursors.entries());
  }

  getPresence() {
    return Array.from(this.presence.entries());
  }

  getCurrentRoom() {
    return this.currentRoom;
  }

  getConnectionState() {
    return this.connectionState;
  }

  // Cleanup
  async disconnect() {
    try {
      // Leave current room
      if (this.currentRoom) {
        await this.leaveRoom();
      }
      
      // Stop heartbeat
      this.stopHeartbeat();
      
      // Clear reconnection timeout
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      
      // Close WebSocket connection
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
      
      this.connectionState = 'disconnected';
      
      log.info('Collaboration client disconnected');
      this.emit('client:disconnected');
      
    } catch (error) {
      log.error('Error during collaboration client disconnect:', error);
    }
  }
}

// Operational Transform implementation for real-time collaboration
class OperationalTransform {
  constructor() {
    this.operations = [];
    this.revision = 0;
  }
  
  transform(operation) {
    // Simple operational transform implementation
    // In a real implementation, this would be much more sophisticated
    return {
      ...operation,
      revision: this.revision++,
      transformed: true
    };
  }
  
  apply(operation) {
    this.operations.push(operation);
    return operation;
  }
}

module.exports = CollaborationDesktopClient;