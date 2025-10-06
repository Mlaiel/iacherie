'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Radio, Users, DollarSign, Eye, Heart, MessageCircle, Share2, Settings, Play, Pause, Loader2, TrendingUp } from 'lucide-react';

interface Stream {
  id: string;
  title: string;
  creator_id: string;
  creator_name: string;
  status: 'live' | 'preparing' | 'ended';
  viewers_count: number;
  likes_count: number;
  started_at: string;
  thumbnail_url: string;
  stream_key?: string;
  rtmp_url?: string;
  hls_url?: string;
  quality: string;
}

interface Donation {
  id: string;
  amount: number;
  currency: string;
  donor_name: string;
  message: string;
  created_at: string;
}

interface StreamAnalytics {
  peak_viewers: number;
  avg_watch_time: number;
  total_donations: number;
  engagement_rate: number;
}

export default function StreamingLivePage() {
  const [myStreams, setMyStreams] = useState<Stream[]>([]);
  const [liveStreams, setLiveStreams] = useState<Stream[]>([]);
  const [selectedStream, setSelectedStream] = useState<Stream | null>(null);
  const [donations, setDonations] = useState<Donation[]>([]);
  const [analytics, setAnalytics] = useState<StreamAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingStream, setCreatingStream] = useState(false);
  
  // Create Stream Form
  const [streamTitle, setStreamTitle] = useState('');
  const [streamQuality, setStreamQuality] = useState<'720p' | '1080p' | '4k'>('1080p');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch my streams
      const myStreamsResponse = await fetch('http://localhost:8000/streaming/my-streams', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      if (myStreamsResponse.ok) {
        const data = await myStreamsResponse.json();
        setMyStreams(data.streams || []);
      }

      // Fetch live streams
      const liveResponse = await fetch('http://localhost:8000/streaming/live');
      if (liveResponse.ok) {
        const data = await liveResponse.json();
        setLiveStreams(data.streams || []);
      }

      // Fetch donations if stream selected
      if (selectedStream) {
        const donationsResponse = await fetch(`http://localhost:8000/streaming/${selectedStream.id}/donations`);
        if (donationsResponse.ok) {
          const data = await donationsResponse.json();
          setDonations(data.donations || []);
        }

        // Fetch analytics
        const analyticsResponse = await fetch(`http://localhost:8000/streaming/${selectedStream.id}/analytics`);
        if (analyticsResponse.ok) {
          const data = await analyticsResponse.json();
          setAnalytics(data.analytics);
        }
      }
    } catch (error) {
      console.error('Error fetching streaming data:', error);
    } finally {
      setLoading(false);
    }
  };

  const createStream = async () => {
    if (!streamTitle.trim()) return;

    try {
      setCreatingStream(true);

      const response = await fetch('http://localhost:8000/streaming/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          title: streamTitle,
          quality: streamQuality,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSelectedStream(data.stream);
        setStreamTitle('');
        fetchData();
      } else {
        alert('Failed to create stream');
      }
    } catch (error) {
      console.error('Error creating stream:', error);
    } finally {
      setCreatingStream(false);
    }
  };

  const startStream = async (streamId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/streaming/${streamId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Error starting stream:', error);
    }
  };

  const endStream = async (streamId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/streaming/${streamId}/end`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (response.ok) {
        setSelectedStream(null);
        fetchData();
      }
    } catch (error) {
      console.error('Error ending stream:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-red-600 transition">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <Radio className="h-8 w-8 text-red-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Live Streaming Studio</h1>
                <p className="text-sm text-gray-500">RTMP • WebRTC • HLS • Multi-Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-red-100 text-red-700 px-4 py-2 rounded-lg">
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
                <span className="font-semibold">{liveStreams.length} Live Now</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Create Stream */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center space-x-3 mb-6">
                <Play className="h-6 w-6 text-red-600" />
                <h2 className="text-xl font-bold text-gray-900">Create New Stream</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stream Title
                  </label>
                  <input
                    type="text"
                    value={streamTitle}
                    onChange={(e) => setStreamTitle(e.target.value)}
                    placeholder="Enter stream title..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Stream Quality
                  </label>
                  <select
                    value={streamQuality}
                    onChange={(e) => setStreamQuality(e.target.value as any)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  >
                    <option value="720p">720p HD</option>
                    <option value="1080p">1080p Full HD</option>
                    <option value="4k">4K Ultra HD</option>
                  </select>
                </div>

                <button
                  onClick={createStream}
                  disabled={!streamTitle.trim() || creatingStream}
                  className="w-full bg-gradient-to-r from-red-600 to-pink-600 text-white py-4 px-6 rounded-lg font-semibold hover:from-red-700 hover:to-pink-700 disabled:opacity-50 transition flex items-center justify-center space-x-2"
                >
                  {creatingStream ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <Radio className="h-5 w-5" />
                      <span>Create Stream</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Selected Stream Details */}
            {selectedStream && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900">{selectedStream.title}</h2>
                  <div className={`px-4 py-2 rounded-full font-semibold ${
                    selectedStream.status === 'live' ? 'bg-red-100 text-red-700' :
                    selectedStream.status === 'preparing' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {selectedStream.status === 'live' && <div className="w-2 h-2 bg-red-600 rounded-full inline-block mr-2 animate-pulse"></div>}
                    {selectedStream.status.toUpperCase()}
                  </div>
                </div>

                {/* Stream Stats */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 rounded-lg p-4 text-center">
                    <Eye className="h-6 w-6 text-blue-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-blue-600">{selectedStream.viewers_count}</div>
                    <div className="text-sm text-blue-700">Viewers</div>
                  </div>
                  <div className="bg-pink-50 rounded-lg p-4 text-center">
                    <Heart className="h-6 w-6 text-pink-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-pink-600">{selectedStream.likes_count}</div>
                    <div className="text-sm text-pink-700">Likes</div>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <DollarSign className="h-6 w-6 text-green-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-green-600">
                      ${donations.reduce((sum, d) => sum + d.amount, 0).toFixed(2)}
                    </div>
                    <div className="text-sm text-green-700">Donations</div>
                  </div>
                </div>

                {/* Stream Controls */}
                <div className="space-y-4">
                  {selectedStream.rtmp_url && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">RTMP URL</div>
                      <div className="flex items-center space-x-2">
                        <code className="flex-1 bg-white px-3 py-2 rounded border border-gray-300 text-sm">
                          {selectedStream.rtmp_url}
                        </code>
                        <button
                          onClick={() => navigator.clipboard.writeText(selectedStream.rtmp_url!)}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  )}

                  {selectedStream.stream_key && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Stream Key</div>
                      <div className="flex items-center space-x-2">
                        <code className="flex-1 bg-white px-3 py-2 rounded border border-gray-300 text-sm">
                          {selectedStream.stream_key}
                        </code>
                        <button
                          onClick={() => navigator.clipboard.writeText(selectedStream.stream_key!)}
                          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-4">
                    {selectedStream.status === 'preparing' && (
                      <button
                        onClick={() => startStream(selectedStream.id)}
                        className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition flex items-center justify-center space-x-2"
                      >
                        <Play className="h-5 w-5" />
                        <span>Go Live</span>
                      </button>
                    )}
                    {selectedStream.status === 'live' && (
                      <button
                        onClick={() => endStream(selectedStream.id)}
                        className="flex-1 bg-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-700 transition flex items-center justify-center space-x-2"
                      >
                        <Pause className="h-5 w-5" />
                        <span>End Stream</span>
                      </button>
                    )}
                    <button className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                      <Settings className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {/* Analytics */}
                {analytics && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-4">Stream Analytics</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Peak Viewers</div>
                        <div className="text-2xl font-bold text-gray-900">{analytics.peak_viewers}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Avg Watch Time</div>
                        <div className="text-2xl font-bold text-gray-900">{analytics.avg_watch_time}m</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Total Donations</div>
                        <div className="text-2xl font-bold text-gray-900">${analytics.total_donations}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Engagement Rate</div>
                        <div className="text-2xl font-bold text-gray-900">{analytics.engagement_rate}%</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* My Streams */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">My Streams</h2>
              {loading && myStreams.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-red-600" />
                </div>
              ) : myStreams.length > 0 ? (
                <div className="space-y-3">
                  {myStreams.map((stream) => (
                    <button
                      key={stream.id}
                      onClick={() => setSelectedStream(stream)}
                      className={`w-full text-left p-4 rounded-lg border-2 transition hover:border-red-300 ${
                        selectedStream?.id === stream.id ? 'border-red-500 bg-red-50' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold text-gray-900">{stream.title}</div>
                        <div className={`text-xs px-2 py-1 rounded ${
                          stream.status === 'live' ? 'bg-red-100 text-red-700' :
                          stream.status === 'preparing' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {stream.status}
                        </div>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Eye className="h-4 w-4" />
                          <span>{stream.viewers_count}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Heart className="h-4 w-4" />
                          <span>{stream.likes_count}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(stream.started_at).toLocaleString()}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No streams yet. Create your first stream!
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Live Streams */}
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">Live Now</h3>
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse"></div>
              </div>

              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {liveStreams.map((stream) => (
                  <div key={stream.id} className="border border-gray-200 rounded-lg p-3 hover:border-red-300 transition cursor-pointer">
                    <div className="font-semibold text-sm text-gray-900 mb-2">{stream.title}</div>
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Users className="h-3 w-3" />
                        <span>{stream.viewers_count}</span>
                      </div>
                      <span className="text-gray-500">{stream.creator_name}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Donations */}
            {donations.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Donations</h3>
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {donations.slice(0, 10).map((donation) => (
                    <div key={donation.id} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-green-900">{donation.donor_name}</span>
                        <span className="font-bold text-green-600">${donation.amount}</span>
                      </div>
                      {donation.message && (
                        <div className="text-sm text-green-700 italic">"{donation.message}"</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
