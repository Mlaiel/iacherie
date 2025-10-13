'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, Video, VideoOff, Mic, MicOff, Users, MessageCircle, 
  Phone, PhoneOff, Monitor, Loader2, Crown, Plus
} from 'lucide-react';

interface ChatRoom {
  room_id: string;
  name: string;
  description: string;
  category: string;
  participants_count: number;
  max_participants: number;
  is_active: boolean;
  host_id: string;
  host_name: string;
  created_at: string;
  webrtc_url?: string;
}

interface Participant {
  user_id: string;
  username: string;
  is_muted: boolean;
  is_video_on: boolean;
  role: string;
  joined_at: string;
}

interface ChatMessage {
  message_id: string;
  sender_id: string;
  sender_name: string;
  message: string;
  timestamp: string;
}

export default function VideoChatRoomsPage() {
  const [activeRoom, setActiveRoom] = useState<ChatRoom | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isMicOn, setIsMicOn] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [roomName, setRoomName] = useState('');
  const [roomDescription, setRoomDescription] = useState('');
  const [roomCategory, setRoomCategory] = useState('social');

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeRoom) {
      fetchParticipants(activeRoom.room_id);
      fetchMessages(activeRoom.room_id);
      initializeWebRTC();
      
      const participantsInterval = setInterval(() => fetchParticipants(activeRoom.room_id), 5000);
      const messagesInterval = setInterval(() => fetchMessages(activeRoom.room_id), 3000);
      
      return () => {
        clearInterval(participantsInterval);
        clearInterval(messagesInterval);
        cleanupWebRTC();
      };
    }
  }, [activeRoom]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const fetchRooms = async () => {
    try {
      const response = await fetch('http://localhost:8000/video-chat/rooms', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setRooms(data.rooms || []);
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchParticipants = async (roomId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/video-chat/rooms/${roomId}/participants`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setParticipants(data.participants || []);
      }
    } catch (error) {
      console.error('Error fetching participants:', error);
    }
  };

  const fetchMessages = async (roomId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/video-chat/rooms/${roomId}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setChatMessages(data.messages || []);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const createRoom = async () => {
    try {
      const response = await fetch('http://localhost:8000/video-chat/rooms/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          name: roomName,
          description: roomDescription,
          category: roomCategory,
          max_participants: 50,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setShowCreateModal(false);
        setRoomName('');
        setRoomDescription('');
        await fetchRooms();
      }
    } catch (error) {
      console.error('Error creating room:', error);
    }
  };

  const joinRoom = async (room: ChatRoom) => {
    try {
      const response = await fetch(`http://localhost:8000/video-chat/rooms/${room.room_id}/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (response.ok) {
        setActiveRoom(room);
      }
    } catch (error) {
      console.error('Error joining room:', error);
    }
  };

  const leaveRoom = async () => {
    if (!activeRoom) return;
    
    try {
      await fetch(`http://localhost:8000/video-chat/rooms/${activeRoom.room_id}/leave`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      cleanupWebRTC();
      setActiveRoom(null);
      setParticipants([]);
      setChatMessages([]);
    } catch (error) {
      console.error('Error leaving room:', error);
    }
  };

  const initializeWebRTC = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: isVideoOn, 
        audio: isMicOn 
      });
      
      setLocalStream(stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Error accessing media devices:', error);
    }
  };

  const cleanupWebRTC = () => {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoOn(videoTrack.enabled);
      }
    }
  };

  const toggleMic = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMicOn(audioTrack.enabled);
      }
    }
  };

  const sendMessage = async () => {
    if (!activeRoom || !newMessage.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/video-chat/rooms/${activeRoom.room_id}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ message: newMessage }),
      });
      
      if (response.ok) {
        setNewMessage('');
        await fetchMessages(activeRoom.room_id);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const categories = ['all', 'social', 'music', 'gaming', 'business', 'education'];

  const filteredRooms = selectedCategory === 'all' 
    ? rooms 
    : rooms.filter(r => r.category === selectedCategory);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 flex items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-purple-600" />
      </div>
    );
  }

  if (activeRoom) {
    return (
      <div className="min-h-screen bg-gray-900 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button onClick={leaveRoom} className="text-red-400 hover:text-red-300">
                <PhoneOff className="h-6 w-6" />
              </button>
              <div>
                <h2 className="text-xl font-bold text-white">{activeRoom.name}</h2>
                <p className="text-sm text-gray-400">{participants.length} participants</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleMic}
                className={`p-3 rounded-full ${isMicOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-500'}`}
              >
                {isMicOn ? <Mic className="h-5 w-5 text-white" /> : <MicOff className="h-5 w-5 text-white" />}
              </button>
              <button
                onClick={toggleVideo}
                className={`p-3 rounded-full ${isVideoOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-500'}`}
              >
                {isVideoOn ? <Video className="h-5 w-5 text-white" /> : <VideoOff className="h-5 w-5 text-white" />}
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Video Grid */}
          <div className="flex-1 p-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 h-full">
              {/* Local Video */}
              <div className="relative bg-gray-800 rounded-lg overflow-hidden">
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 px-2 py-1 rounded">
                  <span className="text-white font-medium text-sm">You</span>
                </div>
              </div>

              {/* Participants Videos */}
              {participants.map((participant) => (
                <div key={participant.user_id} className="relative bg-gray-800 rounded-lg overflow-hidden">
                  {participant.is_video_on ? (
                    <div className="w-full h-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                      <Users className="h-12 w-12 text-white opacity-50" />
                    </div>
                  ) : (
                    <div className="w-full h-full bg-gray-700 flex items-center justify-center">
                      <Users className="h-12 w-12 text-gray-500" />
                    </div>
                  )}
                  <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 px-2 py-1 rounded flex items-center space-x-1">
                    <span className="text-white font-medium text-sm">{participant.username}</span>
                    {participant.role === 'host' && <Crown className="h-3 w-3 text-yellow-400" />}
                    {participant.is_muted && <MicOff className="h-3 w-3 text-red-400" />}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <h3 className="font-semibold text-white flex items-center">
                <MessageCircle className="h-5 w-5 mr-2" />
                Chat
              </h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.map((msg) => (
                <div key={msg.message_id} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-semibold text-sm text-white">{msg.sender_name}</span>
                    <span className="text-xs text-gray-400">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">{msg.message}</p>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-gray-700">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  onClick={sendMessage}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-purple-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Video className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Video Chat Rooms</h1>
                <p className="text-sm text-gray-500">Real-time video communication with WebRTC</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition"
            >
              <Plus className="h-5 w-5" />
              <span>Create Room</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Category Filter */}
        <div className="flex space-x-2 mb-6 overflow-x-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-purple-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {/* Rooms Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRooms.map((room) => (
            <div key={room.room_id} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{room.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{room.description}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="flex items-center">
                      <Users className="h-4 w-4 mr-1" />
                      {room.participants_count}/{room.max_participants}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                      {room.category}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="text-xs text-gray-500">
                  Host: {room.host_name}
                </div>
                <button
                  onClick={() => joinRoom(room)}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition"
                >
                  Join Room
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Room Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Create Video Room</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Room Name</label>
                <input
                  type="text"
                  value={roomName}
                  onChange={(e) => setRoomName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter room name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Description</label>
                <textarea
                  value={roomDescription}
                  onChange={(e) => setRoomDescription(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  placeholder="Describe your room"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Category</label>
                <select
                  value={roomCategory}
                  onChange={(e) => setRoomCategory(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  {categories.filter(c => c !== 'all').map((cat) => (
                    <option key={cat} value={cat}>
                      {cat.charAt(0).toUpperCase() + cat.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={createRoom}
                disabled={!roomName.trim()}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
