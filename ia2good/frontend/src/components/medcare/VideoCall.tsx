/**
 * Video Call Component
 * WebRTC-based video consultation interface
 */
import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Video, 
  VideoOff, 
  Mic, 
  MicOff, 
  Phone,
  MessageSquare,
  Maximize2,
  Settings
} from 'lucide-react';

interface VideoCallProps {
  consultationId: string;
  patientName?: string;
  doctorName?: string;
}

export function VideoCall({ consultationId, patientName, doctorName }: VideoCallProps) {
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isAudioOn, setIsAudioOn] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [duration, setDuration] = useState(0);
  
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerConnection = useRef<RTCPeerConnection | null>(null);

  useEffect(() => {
    // Initialize video call
    initializeCall();
    
    // Cleanup on unmount
    return () => {
      cleanupCall();
    };
  }, [consultationId]);

  useEffect(() => {
    // Duration timer
    if (isConnected) {
      const interval = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const initializeCall = async () => {
    try {
      // Get local media stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }

      // Initialize WebRTC connection
      await setupWebRTC(stream);
      
    } catch (error) {
      console.error('Error initializing call:', error);
      alert('Failed to access camera/microphone. Please check permissions.');
    }
  };

  const setupWebRTC = async (stream: MediaStream) => {
    try {
      // Get ICE server configuration from backend
      const roomResponse = await fetch(`/api/medcare/webrtc/rooms/${consultationId}`, {
        method: 'POST'
      });
      const roomData = await roomResponse.json();
      
      // Create RTCPeerConnection with ICE servers
      const configuration: RTCConfiguration = {
        iceServers: roomData.ice_servers
      };
      
      peerConnection.current = new RTCPeerConnection(configuration);
      
      // Add local stream tracks to peer connection
      stream.getTracks().forEach(track => {
        peerConnection.current?.addTrack(track, stream);
      });
      
      // Handle incoming remote stream
      peerConnection.current.ontrack = (event) => {
        if (remoteVideoRef.current && event.streams[0]) {
          remoteVideoRef.current.srcObject = event.streams[0];
          setIsConnected(true);
        }
      };
      
      // Handle ICE candidates
      peerConnection.current.onicecandidate = (event) => {
        if (event.candidate && wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'ice-candidate',
            candidate: event.candidate
          }));
        }
      };
      
      // Connect to signaling server
      await connectSignaling();
      
    } catch (error) {
      console.error('Error setting up WebRTC:', error);
      alert('Failed to setup video call connection.');
    }
  };

  const wsRef = useRef<WebSocket | null>(null);

  const connectSignaling = async () => {
    try {
      // Determine user role (patient or doctor)
      const role = patientName ? 'patient' : 'doctor';
      const userId = 'user_' + Math.random().toString(36).substr(2, 9);
      
      // Connect to WebSocket signaling server
      // Use relative URL for WebSocket to work through proxy
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host; // This will be localhost:5173
      const wsUrl = `${wsProtocol}//${wsHost}/medcare/webrtc/signal/${consultationId}?user_id=${userId}&role=${role}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      
      ws.onopen = async () => {
        console.log('Signaling connected');
        
        // Create and send offer if patient (initiator)
        if (role === 'patient' && peerConnection.current) {
          const offer = await peerConnection.current.createOffer();
          await peerConnection.current.setLocalDescription(offer);
          
          ws.send(JSON.stringify({
            type: 'offer',
            sdp: offer.sdp
          }));
        }
      };
      
      ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        await handleSignalingMessage(message);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('Signaling disconnected');
        setIsConnected(false);
      };
      
    } catch (error) {
      console.error('Error connecting to signaling server:', error);
    }
  };

  const handleSignalingMessage = async (message: any) => {
    if (!peerConnection.current) return;
    
    switch (message.type) {
      case 'joined':
        console.log('Joined room:', message.data);
        break;
        
      case 'offer':
        // Received offer from other peer
        await peerConnection.current.setRemoteDescription(
          new RTCSessionDescription({ type: 'offer', sdp: message.sdp })
        );
        
        // Create and send answer
        const answer = await peerConnection.current.createAnswer();
        await peerConnection.current.setLocalDescription(answer);
        
        if (wsRef.current) {
          wsRef.current.send(JSON.stringify({
            type: 'answer',
            sdp: answer.sdp
          }));
        }
        break;
        
      case 'answer':
        // Received answer from other peer
        await peerConnection.current.setRemoteDescription(
          new RTCSessionDescription({ type: 'answer', sdp: message.sdp })
        );
        break;
        
      case 'ice-candidate':
        // Received ICE candidate from other peer
        if (message.candidate) {
          await peerConnection.current.addIceCandidate(
            new RTCIceCandidate(message.candidate)
          );
        }
        break;
        
      case 'participant-left':
        // Other participant left
        alert('Other participant has left the call');
        cleanupCall();
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const cleanupCall = () => {
    // Stop all media tracks
    if (localVideoRef.current?.srcObject) {
      const stream = localVideoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }

    // Close peer connection
    if (peerConnection.current) {
      peerConnection.current.close();
      peerConnection.current = null;
    }
    
    // Close WebSocket
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const toggleVideo = () => {
    if (localVideoRef.current?.srcObject) {
      const stream = localVideoRef.current.srcObject as MediaStream;
      const videoTrack = stream.getVideoTracks()[0];
      videoTrack.enabled = !videoTrack.enabled;
      setIsVideoOn(videoTrack.enabled);
    }
  };

  const toggleAudio = () => {
    if (localVideoRef.current?.srcObject) {
      const stream = localVideoRef.current.srcObject as MediaStream;
      const audioTrack = stream.getAudioTracks()[0];
      audioTrack.enabled = !audioTrack.enabled;
      setIsAudioOn(audioTrack.enabled);
    }
  };

  const endCall = async () => {
    try {
      // TODO: Call API to end consultation
      await fetch(`/api/medcare/consultations/${consultationId}/end`, {
        method: 'POST'
      });
      
      cleanupCall();
      // Redirect or show end call screen
    } catch (error) {
      console.error('Error ending call:', error);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 text-white p-4 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">
            Consultation with {doctorName || 'Doctor'}
          </h2>
          <div className="flex items-center gap-4 mt-1">
            <Badge variant={isConnected ? "default" : "destructive"} className="text-xs">
              {isConnected ? 'Connected' : 'Connecting...'}
            </Badge>
            {isConnected && (
              <span className="text-sm text-gray-400">{formatDuration(duration)}</span>
            )}
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => {/* TODO: Implement settings */}}
        >
          <Settings className="h-5 w-5" />
        </Button>
      </div>

      {/* Video Area */}
      <div className="flex-1 relative">
        {/* Remote Video (Doctor) */}
        <video
          ref={remoteVideoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />

        {/* Local Video (Patient) - Picture in Picture */}
        <div className="absolute top-4 right-4 w-48 h-36 rounded-lg overflow-hidden border-2 border-white shadow-lg">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover mirror"
          />
          {!isVideoOn && (
            <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
              <VideoOff className="h-8 w-8 text-gray-400" />
            </div>
          )}
        </div>

        {/* Chat Panel (Overlay) */}
        {showChat && (
          <div className="absolute right-4 top-20 bottom-24 w-80 bg-white rounded-lg shadow-2xl flex flex-col">
            <div className="p-3 border-b">
              <h3 className="font-semibold">Chat</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {/* TODO: Implement chat messages */}
              <p className="text-sm text-gray-500 text-center">No messages yet</p>
            </div>
            <div className="p-3 border-t">
              <input
                type="text"
                placeholder="Type a message..."
                className="w-full px-3 py-2 border rounded-lg text-sm"
              />
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-900 text-white p-6">
        <div className="max-w-md mx-auto flex justify-center items-center gap-4">
          <Button
            variant={isVideoOn ? "secondary" : "destructive"}
            size="icon"
            className="h-14 w-14 rounded-full"
            onClick={toggleVideo}
          >
            {isVideoOn ? <Video className="h-6 w-6" /> : <VideoOff className="h-6 w-6" />}
          </Button>

          <Button
            variant={isAudioOn ? "secondary" : "destructive"}
            size="icon"
            className="h-14 w-14 rounded-full"
            onClick={toggleAudio}
          >
            {isAudioOn ? <Mic className="h-6 w-6" /> : <MicOff className="h-6 w-6" />}
          </Button>

          <Button
            variant="destructive"
            size="icon"
            className="h-16 w-16 rounded-full"
            onClick={endCall}
          >
            <Phone className="h-6 w-6 rotate-[135deg]" />
          </Button>

          <Button
            variant="secondary"
            size="icon"
            className="h-14 w-14 rounded-full"
            onClick={() => setShowChat(!showChat)}
          >
            <MessageSquare className="h-6 w-6" />
          </Button>

          <Button
            variant="secondary"
            size="icon"
            className="h-14 w-14 rounded-full"
            onClick={() => {/* TODO: Implement fullscreen */}}
          >
            <Maximize2 className="h-6 w-6" />
          </Button>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4">
          This call is recorded for quality assurance and medical records
        </p>
      </div>

      <style>{`
        .mirror {
          transform: scaleX(-1);
        }
      `}</style>
    </div>
  );
}
