'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, Video, VideoOff, Mic, MicOff, Users, MessageCircle, 
  Settings, Share2, Phone, PhoneOff, Camera, Monitor, Volume2,
  Maximize2, Minimize2, UserPlus, Crown, Shield, Gift, Heart
} from 'lucide-react';

interface ChatRoom {
  id: string;
  name: string;
  description: string;
  category: 'music' | 'gaming' | 'art' | 'business' | 'social';
  participants: number;
  maxParticipants: number;
  isPrivate: boolean;
  isLive: boolean;
  createdBy: string;
  avatar: string;
  tags: string[];
  language: string;
  createdAt: string;
}

interface Participant {
  id: string;
  name: string;
  avatar: string;
  isMuted: boolean;
  isVideoOn: boolean;
  isSpeaking: boolean;
  role: 'host' | 'moderator' | 'participant';
  joinedAt: string;
  country: string;
}

interface ChatMessage {
  id: string;
  userId: string;
  userName: string;
  userAvatar: string;
  message: string;
  timestamp: string;
  type: 'text' | 'emoji' | 'gift' | 'system';
}

export default function VideoChatRoomsPage() {
  const [activeRoom, setActiveRoom] = useState<ChatRoom | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [rooms, setRooms] = useState<ChatRoom[]>([]);
  const [isVideoOn, setIsVideoOn] = useState(true);
  const [isMicOn, setIsMicOn] = useState(true);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isFullScreen, setIsFullScreen] = useState(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  // Salles de chat simulées
  const mockRooms: ChatRoom[] = [
    {
      id: '1',
      name: '🎵 Studio Collaboratif Live',
      description: 'Session de production musicale en direct avec des producteurs du monde entier',
      category: 'music',
      participants: 12,
      maxParticipants: 50,
      isPrivate: false,
      isLive: true,
      createdBy: 'DJ Producer Max',
      avatar: '🎵',
      tags: ['Electronic', 'Collaboration', 'Live Session'],
      language: 'FR',
      createdAt: '2025-09-25T14:00:00Z'
    },
    {
      id: '2',
      name: '🎮 Gaming & Stream Discussion',
      description: 'Discussions sur le gaming, streaming et création de contenu',
      category: 'gaming',
      participants: 8,
      maxParticipants: 25,
      isPrivate: false,
      isLive: true,
      createdBy: 'StreamerPro',
      avatar: '🎮',
      tags: ['Gaming', 'Twitch', 'YouTube'],
      language: 'EN',
      createdAt: '2025-09-25T13:30:00Z'
    },
    {
      id: '3',
      name: '🎨 Art & Design Workshop',
      description: 'Atelier créatif pour artistes et designers',
      category: 'art',
      participants: 15,
      maxParticipants: 30,
      isPrivate: false,
      isLive: true,
      createdBy: 'ArtistCreative',
      avatar: '🎨',
      tags: ['Digital Art', 'NFT', 'Design'],
      language: 'FR',
      createdAt: '2025-09-25T12:00:00Z'
    },
    {
      id: '4',
      name: '💼 Business & Networking',
      description: 'Réunion professionnelle et opportunités de networking',
      category: 'business',
      participants: 22,
      maxParticipants: 100,
      isPrivate: false,
      isLive: true,
      createdBy: 'BusinessLeader',
      avatar: '💼',
      tags: ['Networking', 'Startup', 'Investment'],
      language: 'EN',
      createdAt: '2025-09-25T11:00:00Z'
    }
  ];

  // Participants simulés
  const mockParticipants: Participant[] = [
    {
      id: '1',
      name: 'DJ Producer Max',
      avatar: '👨‍🎤',
      isMuted: false,
      isVideoOn: true,
      isSpeaking: true,
      role: 'host',
      joinedAt: '2025-09-25T14:00:00Z',
      country: 'FR'
    },
    {
      id: '2',
      name: 'BeatMaker Sarah',
      avatar: '👩‍🎵',
      isMuted: false,
      isVideoOn: true,
      isSpeaking: false,
      role: 'moderator',
      joinedAt: '2025-09-25T14:05:00Z',
      country: 'US'
    },
    {
      id: '3',
      name: 'Remix Artist Tom',
      avatar: '🎧',
      isMuted: true,
      isVideoOn: false,
      isSpeaking: false,
      role: 'participant',
      joinedAt: '2025-09-25T14:10:00Z',
      country: 'DE'
    }
  ];

  // Messages de chat simulés
  const mockMessages: ChatMessage[] = [
    {
      id: '1',
      userId: '1',
      userName: 'DJ Producer Max',
      userAvatar: '👨‍🎤',
      message: 'Salut tout le monde! Prêts pour une session de folie? 🎵',
      timestamp: '2025-09-25T14:05:00Z',
      type: 'text'
    },
    {
      id: '2',
      userId: '2',
      userName: 'BeatMaker Sarah',
      userAvatar: '👩‍🎵',
      message: 'J\'ai hâte d\'entendre vos dernières productions! 🔥',
      timestamp: '2025-09-25T14:06:00Z',
      type: 'text'
    },
    {
      id: '3',
      userId: '3',
      userName: 'Remix Artist Tom',
      userAvatar: '🎧',
      message: '🎉🎉🎉',
      timestamp: '2025-09-25T14:07:00Z',
      type: 'emoji'
    }
  ];

  useEffect(() => {
    // Charger les données
    setTimeout(() => {
      setRooms(mockRooms);
      if (mockRooms.length > 0) {
        setActiveRoom(mockRooms[0]);
        setParticipants(mockParticipants);
        setChatMessages(mockMessages);
      }
    }, 1000);

    // Simuler l'activité du chat
    const chatInterval = setInterval(() => {
      const randomMessages = [
        'Super session! 🎵',
        'J\'adore ce beat!',
        'Qui veut collaborer?',
        '🔥🔥🔥',
        'Incroyable talent!',
        'Partage ton Instagram!',
        'Next level! 💯'
      ];
      
      const randomMessage = randomMessages[Math.floor(Math.random() * randomMessages.length)];
      const newMsg: ChatMessage = {
        id: Date.now().toString(),
        userId: '4',
        userName: 'Random User',
        userAvatar: '😎',
        message: randomMessage,
        timestamp: new Date().toISOString(),
        type: 'text'
      };
      
      setChatMessages(prev => [...prev, newMsg]);
    }, 15000);

    return () => clearInterval(chatInterval);
  }, []);

  useEffect(() => {
    // Auto-scroll du chat
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const joinRoom = (room: ChatRoom) => {
    setActiveRoom(room);
    setParticipants(mockParticipants);
    setChatMessages(mockMessages);
  };

  const leaveRoom = () => {
    setActiveRoom(null);
    setParticipants([]);
    setChatMessages([]);
  };

  const toggleVideo = () => {
    setIsVideoOn(!isVideoOn);
  };

  const toggleMic = () => {
    setIsMicOn(!isMicOn);
  };

  const toggleScreenShare = () => {
    setIsScreenSharing(!isScreenSharing);
  };

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const message: ChatMessage = {
      id: Date.now().toString(),
      userId: 'current-user',
      userName: 'Vous',
      userAvatar: '😊',
      message: newMessage,
      timestamp: new Date().toISOString(),
      type: 'text'
    };

    setChatMessages([...chatMessages, message]);
    setNewMessage('');
  };

  const filteredRooms = selectedCategory === 'all' 
    ? rooms 
    : rooms.filter(room => room.category === selectedCategory);

  if (activeRoom) {
    return (
      <div className="h-screen bg-gray-900 flex">
        {/* Zone Vidéo Principale */}
        <div className="flex-1 flex flex-col">
          {/* Header de la salle */}
          <div className="bg-gray-800 px-6 py-4 flex items-center justify-between border-b border-gray-700">
            <div className="flex items-center space-x-4">
              <button
                onClick={leaveRoom}
                className="text-red-400 hover:text-red-300 flex items-center space-x-2"
              >
                <PhoneOff className="h-5 w-5" />
                <span>Quitter</span>
              </button>
              <div className="h-6 w-px bg-gray-600"></div>
              <div>
                <h2 className="text-white font-semibold">{activeRoom.name}</h2>
                <p className="text-gray-400 text-sm">{participants.length} participants</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button className="text-gray-400 hover:text-white p-2">
                <Settings className="h-5 w-5" />
              </button>
              <button className="text-gray-400 hover:text-white p-2">
                <Share2 className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Grille de Vidéos */}
          <div className="flex-1 p-4 bg-gray-900">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-full">
              {participants.map((participant) => (
                <div key={participant.id} className="relative bg-gray-800 rounded-lg overflow-hidden">
                  {participant.isVideoOn ? (
                    <video
                      className="w-full h-full object-cover"
                      autoPlay
                      muted={participant.id !== 'current-user'}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-700">
                      <div className="text-center">
                        <div className="text-4xl mb-2">{participant.avatar}</div>
                        <p className="text-white font-medium">{participant.name}</p>
                      </div>
                    </div>
                  )}

                  {/* Overlay informations */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="text-white font-medium text-sm">{participant.name}</span>
                        {participant.role === 'host' && <Crown className="h-4 w-4 text-yellow-400" />}
                        {participant.role === 'moderator' && <Shield className="h-4 w-4 text-blue-400" />}
                      </div>
                      <div className="flex items-center space-x-1">
                        {!participant.isMuted ? (
                          <Mic className={`h-4 w-4 ${participant.isSpeaking ? 'text-green-400' : 'text-white'}`} />
                        ) : (
                          <MicOff className="h-4 w-4 text-red-400" />
                        )}
                        {participant.isVideoOn ? (
                          <Video className="h-4 w-4 text-white" />
                        ) : (
                          <VideoOff className="h-4 w-4 text-red-400" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Indicateur de parole */}
                  {participant.isSpeaking && (
                    <div className="absolute inset-0 border-4 border-green-400 rounded-lg pointer-events-none"></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Contrôles de la vidéo */}
          <div className="bg-gray-800 px-6 py-4 border-t border-gray-700">
            <div className="flex items-center justify-center space-x-6">
              <button
                onClick={toggleMic}
                className={`p-4 rounded-full transition-colors ${
                  isMicOn 
                    ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                {isMicOn ? <Mic className="h-6 w-6" /> : <MicOff className="h-6 w-6" />}
              </button>

              <button
                onClick={toggleVideo}
                className={`p-4 rounded-full transition-colors ${
                  isVideoOn 
                    ? 'bg-gray-700 hover:bg-gray-600 text-white' 
                    : 'bg-red-600 hover:bg-red-700 text-white'
                }`}
              >
                {isVideoOn ? <Video className="h-6 w-6" /> : <VideoOff className="h-6 w-6" />}
              </button>

              <button
                onClick={toggleScreenShare}
                className={`p-4 rounded-full transition-colors ${
                  isScreenSharing 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                }`}
              >
                <Monitor className="h-6 w-6" />
              </button>

              <button className="p-4 rounded-full bg-gray-700 hover:bg-gray-600 text-white transition-colors">
                <Settings className="h-6 w-6" />
              </button>

              <button
                onClick={leaveRoom}
                className="p-4 rounded-full bg-red-600 hover:bg-red-700 text-white transition-colors"
              >
                <PhoneOff className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>

        {/* Panneau de Chat */}
        <div className="w-80 bg-gray-800 border-l border-gray-700 flex flex-col">
          <div className="p-4 border-b border-gray-700">
            <h3 className="text-white font-semibold flex items-center">
              <MessageCircle className="h-5 w-5 mr-2" />
              Chat ({chatMessages.length})
            </h3>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.map((message) => (
              <div key={message.id} className="flex space-x-3">
                <div className="text-2xl">{message.userAvatar}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-white font-medium text-sm">{message.userName}</span>
                    <span className="text-gray-500 text-xs">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-gray-300 text-sm">{message.message}</p>
                </div>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <form onSubmit={sendMessage} className="p-4 border-t border-gray-700">
            <div className="flex space-x-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Tapez votre message..."
                className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={!newMessage.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
              >
                ➤
              </button>
            </div>
            <div className="flex space-x-2 mt-2">
              <button type="button" className="text-gray-400 hover:text-white text-xl">❤️</button>
              <button type="button" className="text-gray-400 hover:text-white text-xl">👏</button>
              <button type="button" className="text-gray-400 hover:text-white text-xl">🔥</button>
              <button type="button" className="text-gray-400 hover:text-white text-xl">😍</button>
              <button type="button" className="text-gray-400 hover:text-white text-xl">🎉</button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center text-gray-600 hover:text-blue-600">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Retour
              </Link>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-3">
                <Video className="h-8 w-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Video Chat Rooms</h1>
                  <p className="text-sm text-gray-600">Rejoignez des conversations vidéo en direct</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Filtres */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            {[
              { id: 'all', label: '🌟 Toutes', count: rooms.length },
              { id: 'music', label: '🎵 Musique', count: rooms.filter(r => r.category === 'music').length },
              { id: 'gaming', label: '🎮 Gaming', count: rooms.filter(r => r.category === 'gaming').length },
              { id: 'art', label: '🎨 Art & Design', count: rooms.filter(r => r.category === 'art').length },
              { id: 'business', label: '💼 Business', count: rooms.filter(r => r.category === 'business').length },
              { id: 'social', label: '💬 Social', count: rooms.filter(r => r.category === 'social').length }
            ].map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
                  selectedCategory === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                }`}
              >
                <span>{category.label}</span>
                <span className="text-sm bg-black bg-opacity-20 px-2 py-1 rounded-full">
                  {category.count}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Grille des salles */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRooms.map((room) => (
            <div key={room.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              <div className="relative">
                <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                  <div className="text-6xl">{room.avatar}</div>
                </div>
                <div className="absolute top-4 left-4">
                  <span className="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
                    <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                    <span>LIVE</span>
                  </span>
                </div>
                <div className="absolute top-4 right-4">
                  <span className="bg-black bg-opacity-50 text-white px-2 py-1 rounded-full text-xs">
                    {room.participants}/{room.maxParticipants}
                  </span>
                </div>
              </div>

              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-lg text-gray-900 line-clamp-1">{room.name}</h3>
                  {room.isPrivate && (
                    <Shield className="h-5 w-5 text-gray-400" />
                  )}
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-2">{room.description}</p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {room.tags.map((tag, index) => (
                    <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Users className="h-4 w-4 text-gray-500" />
                    <span className="text-sm text-gray-600">{room.participants} participants</span>
                  </div>
                  <span className="text-xs text-gray-500">{room.language}</span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Par {room.createdBy}
                  </div>
                  <button
                    onClick={() => joinRoom(room)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                  >
                    <Video className="h-4 w-4" />
                    <span>Rejoindre</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bouton Créer une salle */}
        <div className="text-center mt-12">
          <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all flex items-center space-x-3 mx-auto">
            <UserPlus className="h-6 w-6" />
            <span>Créer ma propre salle</span>
          </button>
        </div>
      </div>
    </div>
  );
}