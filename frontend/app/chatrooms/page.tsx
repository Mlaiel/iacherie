/**
 * CHATROOMS DASHBOARD
 * Real-time chat rooms with WebSocket integration (988 rooms)
 * 
 * @author Fahed Mlaiel (mlaiel@live.de)
 * @copyright © 2025 Fahed Mlaiel. All rights reserved.
 */

'use client';

import { useState, useEffect } from 'react';
import { useChatroomsStore } from '@/lib/store/generated';
import { useChatroomWebSocket, useWebSocketStatus } from '@/lib/websocket';
import { MessageSquare, Video, Mic, Users, Send, MoreVertical, Search } from 'lucide-react';

const ROOM_TYPES = [
  { id: 'all', name: 'All Rooms', icon: MessageSquare, count: 988, color: 'from-blue-500 to-cyan-500' },
  { id: 'video', name: 'Video Chat', icon: Video, count: 247, color: 'from-purple-500 to-pink-500' },
  { id: 'audio', name: 'Audio Chat', icon: Mic, count: 246, color: 'from-green-500 to-emerald-500' },
  { id: 'text', name: 'Text Chat', icon: MessageSquare, count: 247, color: 'from-orange-500 to-red-500' },
  { id: 'collaboration', name: 'Collaboration', icon: Users, count: 248, color: 'from-indigo-500 to-blue-500' },
];

export default function ChatroomsPage() {
  const { items, loading, fetchItems } = useChatroomsStore();
  const { connected } = useWebSocketStatus();
  const [selectedType, setSelectedType] = useState('all');
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // WebSocket for selected room
  const { messages, users, sendMessage } = useChatroomWebSocket(selectedRoom || '');
  const [messageInput, setMessageInput] = useState('');

  useEffect(() => {
    fetchItems();
  }, []);

  const filteredRooms = items.filter(room => {
    const matchesSearch = !searchQuery || 
      room.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = selectedType === 'all' || room.type === selectedType;
    return matchesSearch && matchesType;
  });

  const handleSendMessage = () => {
    if (messageInput.trim() && selectedRoom) {
      sendMessage(messageInput);
      setMessageInput('');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">Chatrooms</h1>
          </div>
          <p className="text-gray-600">
            Connect and collaborate in 988 real-time chat rooms
          </p>
          
          {/* Status */}
          <div className="mt-4 flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-gray-600">
                {connected ? 'Real-time messaging active' : 'Reconnecting...'}
              </span>
            </div>
            {selectedRoom && users.length > 0 && (
              <span className="text-gray-500">
                {users.length} users online
              </span>
            )}
          </div>
        </div>

        {/* Search Bar */}
        <div className="bg-white rounded-xl shadow-sm p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search chatrooms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Room Types */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {ROOM_TYPES.map((type) => (
            <button
              key={type.id}
              onClick={() => setSelectedType(type.id)}
              className={`relative bg-white rounded-xl shadow-sm hover:shadow-md transition-all p-4 ${
                selectedType === type.id ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${type.color} ${
                selectedType === type.id ? 'opacity-10' : 'opacity-0'
              } transition-opacity rounded-xl`}></div>
              
              <div className="relative text-center">
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${type.color} flex items-center justify-center mx-auto mb-2`}>
                  <type.icon className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900">{type.name}</h3>
                <p className="text-xs text-gray-500">{type.count}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Layout: Rooms List + Chat */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Rooms List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h2 className="font-semibold text-gray-900">
                  {selectedType === 'all' ? 'All Rooms' : ROOM_TYPES.find(t => t.id === selectedType)?.name}
                </h2>
                <p className="text-xs text-gray-500 mt-1">{filteredRooms.length} rooms</p>
              </div>
              
              <div className="max-h-[600px] overflow-y-auto">
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                  </div>
                ) : filteredRooms.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                    <p>No rooms found</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {filteredRooms.slice(0, 20).map((room) => (
                      <button
                        key={room.id}
                        onClick={() => setSelectedRoom(room.id)}
                        className={`w-full p-4 hover:bg-gray-50 transition text-left ${
                          selectedRoom === room.id ? 'bg-blue-50' : ''
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${
                            ROOM_TYPES.find(t => t.id === room.type)?.color || 'from-gray-500 to-gray-600'
                          } flex items-center justify-center flex-shrink-0`}>
                            {(() => {
                              const Icon = ROOM_TYPES.find(t => t.id === room.type)?.icon || MessageSquare;
                              return <Icon className="w-5 h-5 text-white" />;
                            })()}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-gray-900 truncate">
                              {room.name || 'Unnamed Room'}
                            </h3>
                            <p className="text-xs text-gray-500 capitalize">{room.type}</p>
                          </div>
                          {room.status === 'active' && (
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-2">
            {selectedRoom ? (
              <div className="bg-white rounded-xl shadow-sm overflow-hidden flex flex-col h-[600px]">
                {/* Chat Header */}
                <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                  <div>
                    <h2 className="font-semibold text-gray-900">
                      {items.find(r => r.id === selectedRoom)?.name || 'Chat Room'}
                    </h2>
                    <p className="text-xs text-gray-500">{users.length} participants online</p>
                  </div>
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <MoreVertical className="w-5 h-5 text-gray-600" />
                  </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-gray-500">
                      <div className="text-center">
                        <MessageSquare className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                        <p>No messages yet. Start the conversation!</p>
                      </div>
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div key={idx} className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                          <span className="text-white text-xs font-bold">
                            {msg.user?.charAt(0).toUpperCase() || 'U'}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-baseline gap-2 mb-1">
                            <span className="font-medium text-gray-900 text-sm">{msg.user || 'User'}</span>
                            <span className="text-xs text-gray-500">{msg.timestamp}</span>
                          </div>
                          <p className="text-gray-700 text-sm">{msg.content}</p>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Message Input */}
                <div className="p-4 border-t border-gray-200">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Type your message..."
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={!connected}
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!messageInput.trim() || !connected}
                      className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <Send className="w-4 h-4" />
                      Send
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm h-[600px] flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a chatroom</h3>
                  <p>Choose a room from the list to start chatting</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
