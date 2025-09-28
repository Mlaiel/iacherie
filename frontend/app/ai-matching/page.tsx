'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, Heart, Users, Zap, Target, Brain, Sparkles,
  MessageSquare, Video, Music, Camera, Palette, Code,
  Star, Filter, Search, MapPin, Clock, CheckCircle,
  UserPlus, Shield, Crown, Gift, TrendingUp
} from 'lucide-react';

interface Creator {
  id: string;
  name: string;
  avatar: string;
  type: 'musician' | 'artist' | 'developer' | 'writer' | 'designer' | 'influencer';
  location: string;
  languages: string[];
  skills: string[];
  genres: string[];
  experience: 'beginner' | 'intermediate' | 'professional' | 'expert';
  rating: number;
  followers: number;
  completedProjects: number;
  responseTime: string;
  availability: 'available' | 'busy' | 'unavailable';
  isVerified: boolean;
  isPremium: boolean;
  matchScore: number;
  commonInterests: string[];
  portfolio: string[];
  bio: string;
  hourlyRate?: number;
}

interface MatchFilter {
  type: string[];
  location: string;
  experience: string[];
  availability: string[];
  skills: string[];
  budget: { min: number; max: number };
  rating: number;
}

interface MatchRequest {
  id: string;
  fromUser: string;
  toUser: string;
  message: string;
  projectType: string;
  budget?: number;
  timeline: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  timestamp: string;
}

export default function AIMatchingPage() {
  const [matchingCreators, setMatchingCreators] = useState<Creator[]>([]);
  const [allCreators, setAllCreators] = useState<Creator[]>([]);
  const [selectedFilters, setSelectedFilters] = useState<MatchFilter>({
    type: [],
    location: '',
    experience: [],
    availability: [],
    skills: [],
    budget: { min: 0, max: 10000 },
    rating: 0
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [matchRequests, setMatchRequests] = useState<MatchRequest[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<Creator | null>(null);
  const [showMatchModal, setShowMatchModal] = useState(false);

  // Créateurs simulés avec scores IA
  const mockCreators: Creator[] = [
    {
      id: '1',
      name: 'Alex Music Producer',
      avatar: '🎵',
      type: 'musician',
      location: 'Paris, France',
      languages: ['Français', 'English', 'Español'],
      skills: ['Production', 'Mixing', 'Mastering', 'Composition'],
      genres: ['Electronic', 'Pop', 'Hip-Hop'],
      experience: 'professional',
      rating: 4.9,
      followers: 15600,
      completedProjects: 89,
      responseTime: '< 1h',
      availability: 'available',
      isVerified: true,
      isPremium: true,
      matchScore: 96,
      commonInterests: ['Electronic Music', 'AI Tools', 'Collaboration'],
      portfolio: ['Summer Hits EP', 'Brand Jingles', 'Podcast Intro'],
      bio: 'Producteur électronique passionné avec 8 ans d\'expérience. Spécialisé dans la musique commerciale et l\'audio branding.',
      hourlyRate: 75
    },
    {
      id: '2',
      name: 'Maya Digital Artist',
      avatar: '🎨',
      type: 'artist',
      location: 'Berlin, Germany',
      languages: ['Deutsch', 'English'],
      skills: ['Digital Art', '3D Modeling', 'NFT Creation', 'Animation'],
      genres: ['Digital', 'Abstract', 'Conceptual'],
      experience: 'expert',
      rating: 4.8,
      followers: 23400,
      completedProjects: 156,
      responseTime: '< 2h',
      availability: 'available',
      isVerified: true,
      isPremium: true,
      matchScore: 94,
      commonInterests: ['NFT Art', 'Metaverse', 'Creative Tech'],
      portfolio: ['Crypto Gallery', 'VR Exhibitions', 'Brand Identity'],
      bio: 'Artiste digitale primée spécialisée dans l\'art conceptuel et les créations NFT pour marques premium.',
      hourlyRate: 95
    },
    {
      id: '3',
      name: 'Liam Code Wizard',
      avatar: '💻',
      type: 'developer',
      location: 'London, UK',
      languages: ['English', 'Français'],
      skills: ['React', 'Node.js', 'AI Integration', 'Blockchain'],
      genres: ['Web Dev', 'Mobile', 'AI Apps'],
      experience: 'expert',
      rating: 4.9,
      followers: 8900,
      completedProjects: 234,
      responseTime: '< 30min',
      availability: 'busy',
      isVerified: true,
      isPremium: false,
      matchScore: 91,
      commonInterests: ['AI Development', 'Web3', 'Open Source'],
      portfolio: ['Creator Platform', 'DeFi Dashboard', 'AI Chatbot'],
      bio: 'Développeur full-stack avec expertise en IA et blockchain. Créateur de solutions innovantes pour créateurs.',
      hourlyRate: 120
    },
    {
      id: '4',
      name: 'Zoe Content Queen',
      avatar: '👑',
      type: 'influencer',
      location: 'Los Angeles, USA',
      languages: ['English', 'Português'],
      skills: ['Content Strategy', 'Video Production', 'Brand Partnerships', 'Social Media'],
      genres: ['Lifestyle', 'Tech', 'Music'],
      experience: 'professional',
      rating: 4.7,
      followers: 1200000,
      completedProjects: 67,
      responseTime: '< 4h',
      availability: 'available',
      isVerified: true,
      isPremium: true,
      matchScore: 88,
      commonInterests: ['Creator Economy', 'Brand Building', 'Tech Reviews'],
      portfolio: ['Viral Campaigns', 'Product Launches', 'Event Coverage'],
      bio: 'Influenceuse lifestyle et tech avec 1.2M followers. Spécialisée dans les campagnes créatives et partnerships premium.',
      hourlyRate: 200
    },
    {
      id: '5',
      name: 'Emma Creative Writer',
      avatar: '✍️',
      type: 'writer',
      location: 'Toronto, Canada',
      languages: ['English', 'Français'],
      skills: ['Copywriting', 'Storytelling', 'Content Marketing', 'SEO'],
      genres: ['Marketing', 'Tech', 'Creative'],
      experience: 'professional',
      rating: 4.6,
      followers: 5400,
      completedProjects: 178,
      responseTime: '< 2h',
      availability: 'available',
      isVerified: true,
      isPremium: false,
      matchScore: 85,
      commonInterests: ['Content Marketing', 'AI Writing', 'Brand Storytelling'],
      portfolio: ['Tech Blog Articles', 'Brand Stories', 'Marketing Copy'],
      bio: 'Rédactrice créative spécialisée en marketing digital et storytelling de marque. Expertise en contenu tech et IA.',
      hourlyRate: 60
    }
  ];

  useEffect(() => {
    // Charger les créateurs
    setTimeout(() => {
      setAllCreators(mockCreators);
      runAIMatching();
    }, 1000);
  }, []);

  const runAIMatching = async () => {
    setIsAnalyzing(true);
    
    // Simulation de l'analyse IA
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Algorithme de matching IA simulé
    const matchedCreators = mockCreators
      .map(creator => ({
        ...creator,
        matchScore: Math.floor(Math.random() * 30) + 70 // Score entre 70-100
      }))
      .sort((a, b) => b.matchScore - a.matchScore);

    setMatchingCreators(matchedCreators);
    setIsAnalyzing(false);
  };

  const sendMatchRequest = (creator: Creator, message: string, projectType: string, budget?: number) => {
    const newRequest: MatchRequest = {
      id: Date.now().toString(),
      fromUser: 'current-user',
      toUser: creator.id,
      message,
      projectType,
      budget,
      timeline: '1-2 semaines',
      status: 'pending',
      timestamp: new Date().toISOString()
    };

    setMatchRequests([...matchRequests, newRequest]);
    setShowMatchModal(false);
    setSelectedCreator(null);
    
    // Simulation de réponse
    setTimeout(() => {
      const updatedRequest = {
        ...newRequest,
        status: Math.random() > 0.3 ? 'accepted' as const : 'declined' as const
      };
      setMatchRequests(prev => prev.map(req => req.id === newRequest.id ? updatedRequest : req));
    }, 5000);
  };

  const filteredCreators = matchingCreators.filter(creator => {
    if (searchQuery && !creator.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !creator.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()))) {
      return false;
    }
    
    if (selectedFilters.type.length > 0 && !selectedFilters.type.includes(creator.type)) {
      return false;
    }
    
    if (selectedFilters.availability.length > 0 && !selectedFilters.availability.includes(creator.availability)) {
      return false;
    }

    return true;
  });

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'musician': return <Music className="h-4 w-4" />;
      case 'artist': return <Palette className="h-4 w-4" />;
      case 'developer': return <Code className="h-4 w-4" />;
      case 'writer': return <MessageSquare className="h-4 w-4" />;
      case 'designer': return <Palette className="h-4 w-4" />;
      case 'influencer': return <Video className="h-4 w-4" />;
      default: return <Users className="h-4 w-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
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
                <Brain className="h-8 w-8 text-blue-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">AI Matching System</h1>
                  <p className="text-sm text-gray-600">Trouvez les collaborateurs parfaits grâce à l'IA</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={runAIMatching}
                disabled={isAnalyzing}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                <Sparkles className="h-4 w-4" />
                <span>{isAnalyzing ? 'Analyse IA...' : '🤖 Nouveau Matching'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filtres et Recherche */}
          <div className="space-y-6">
            {/* Recherche */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center">
                <Search className="h-5 w-5 text-blue-600 mr-2" />
                Recherche
              </h3>
              <input
                type="text"
                placeholder="Compétences, nom, expertise..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Filtres */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="font-semibold text-lg mb-4 flex items-center">
                <Filter className="h-5 w-5 text-blue-600 mr-2" />
                Filtres IA
              </h3>
              
              <div className="space-y-4">
                {/* Type de créateur */}
                <div>
                  <label className="block text-sm font-medium mb-2">Type de créateur</label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { type: 'musician', label: '🎵 Musicien', count: 23 },
                      { type: 'artist', label: '🎨 Artiste', count: 18 },
                      { type: 'developer', label: '💻 Dev', count: 15 },
                      { type: 'writer', label: '✍️ Writer', count: 12 },
                      { type: 'designer', label: '🎨 Designer', count: 20 },
                      { type: 'influencer', label: '📱 Influencer', count: 8 }
                    ].map((item) => (
                      <button
                        key={item.type}
                        onClick={() => {
                          const newTypes = selectedFilters.type.includes(item.type)
                            ? selectedFilters.type.filter(t => t !== item.type)
                            : [...selectedFilters.type, item.type];
                          setSelectedFilters({ ...selectedFilters, type: newTypes });
                        }}
                        className={`text-xs px-2 py-1 rounded-full border transition-colors ${
                          selectedFilters.type.includes(item.type)
                            ? 'bg-blue-100 border-blue-300 text-blue-800'
                            : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {item.label} ({item.count})
                      </button>
                    ))}
                  </div>
                </div>

                {/* Disponibilité */}
                <div>
                  <label className="block text-sm font-medium mb-2">Disponibilité</label>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { status: 'available', label: '🟢 Disponible', count: 45 },
                      { status: 'busy', label: '🟡 Occupé', count: 23 },
                      { status: 'unavailable', label: '🔴 Indisponible', count: 8 }
                    ].map((item) => (
                      <button
                        key={item.status}
                        onClick={() => {
                          const newAvailability = selectedFilters.availability.includes(item.status)
                            ? selectedFilters.availability.filter(a => a !== item.status)
                            : [...selectedFilters.availability, item.status];
                          setSelectedFilters({ ...selectedFilters, availability: newAvailability });
                        }}
                        className={`text-xs px-2 py-1 rounded-full border transition-colors ${
                          selectedFilters.availability.includes(item.status)
                            ? 'bg-blue-100 border-blue-300 text-blue-800'
                            : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {item.label} ({item.count})
                      </button>
                    ))}
                  </div>
                </div>

                {/* Budget */}
                <div>
                  <label className="block text-sm font-medium mb-2">Budget horaire (€)</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      className="flex-1 p-2 border border-gray-300 rounded text-sm"
                      value={selectedFilters.budget.min || ''}
                      onChange={(e) => setSelectedFilters({
                        ...selectedFilters,
                        budget: { ...selectedFilters.budget, min: parseInt(e.target.value) || 0 }
                      })}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="Max"
                      className="flex-1 p-2 border border-gray-300 rounded text-sm"
                      value={selectedFilters.budget.max || ''}
                      onChange={(e) => setSelectedFilters({
                        ...selectedFilters,
                        budget: { ...selectedFilters.budget, max: parseInt(e.target.value) || 10000 }
                      })}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Statistiques Matching */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-xl shadow-lg p-6">
              <h3 className="font-semibold text-lg mb-4">📊 Matching Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Matches trouvés</span>
                  <span className="font-bold">{filteredCreators.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>Score moyen</span>
                  <span className="font-bold">
                    {filteredCreators.length > 0 
                      ? Math.round(filteredCreators.reduce((acc, c) => acc + c.matchScore, 0) / filteredCreators.length)
                      : 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Disponibles</span>
                  <span className="font-bold">
                    {filteredCreators.filter(c => c.availability === 'available').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Premium</span>
                  <span className="font-bold">
                    {filteredCreators.filter(c => c.isPremium).length}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Liste des créateurs matchés */}
          <div className="lg:col-span-3 space-y-6">
            {/* Header des résultats */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                    <Target className="h-6 w-6 text-blue-600 mr-2" />
                    Matches IA Recommandés ({filteredCreators.length})
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {isAnalyzing ? 'Analyse IA en cours...' : 'Triés par compatibilité et qualité'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {isAnalyzing && (
                    <div className="flex items-center space-x-2 text-blue-600">
                      <Sparkles className="h-5 w-5 animate-spin" />
                      <span className="text-sm">IA Active</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Grille des créateurs */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredCreators.map((creator) => (
                <div key={creator.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all">
                  <div className="p-6">
                    {/* Header du profil */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="text-3xl">{creator.avatar}</div>
                        <div>
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-lg">{creator.name}</h3>
                            {creator.isVerified && <CheckCircle className="h-5 w-5 text-blue-500" />}
                            {creator.isPremium && <Crown className="h-5 w-5 text-yellow-500" />}
                          </div>
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            {getTypeIcon(creator.type)}
                            <span className="capitalize">{creator.type}</span>
                            <span>•</span>
                            <MapPin className="h-4 w-4" />
                            <span>{creator.location}</span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${
                          creator.matchScore >= 90 ? 'text-green-600' :
                          creator.matchScore >= 80 ? 'text-blue-600' :
                          creator.matchScore >= 70 ? 'text-yellow-600' : 'text-gray-600'
                        }`}>
                          {creator.matchScore}%
                        </div>
                        <div className="text-xs text-gray-500">Match IA</div>
                      </div>
                    </div>

                    {/* Bio */}
                    <p className="text-sm text-gray-700 mb-4 line-clamp-2">{creator.bio}</p>

                    {/* Compétences */}
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-1">
                        {creator.skills.slice(0, 4).map((skill, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            {skill}
                          </span>
                        ))}
                        {creator.skills.length > 4 && (
                          <span className="text-xs text-gray-500">+{creator.skills.length - 4} autres</span>
                        )}
                      </div>
                    </div>

                    {/* Intérêts communs */}
                    {creator.commonInterests.length > 0 && (
                      <div className="mb-4">
                        <div className="text-xs text-gray-600 mb-1">🤝 Intérêts communs:</div>
                        <div className="flex flex-wrap gap-1">
                          {creator.commonInterests.map((interest, index) => (
                            <span key={index} className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                              {interest}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Statistiques */}
                    <div className="grid grid-cols-3 gap-3 mb-4 text-xs text-gray-600">
                      <div className="text-center">
                        <div className="flex items-center justify-center space-x-1">
                          <Star className="h-3 w-3 text-yellow-500" />
                          <span className="font-medium">{creator.rating}</span>
                        </div>
                        <div>Rating</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium">{creator.completedProjects}</div>
                        <div>Projets</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium">{creator.responseTime}</div>
                        <div>Réponse</div>
                      </div>
                    </div>

                    {/* Prix et disponibilité */}
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        {creator.hourlyRate && (
                          <div className="font-semibold text-lg">{creator.hourlyRate}€/h</div>
                        )}
                        <div className={`text-xs ${
                          creator.availability === 'available' ? 'text-green-600' :
                          creator.availability === 'busy' ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {creator.availability === 'available' ? '🟢 Disponible' :
                           creator.availability === 'busy' ? '🟡 Occupé' : '🔴 Indisponible'}
                        </div>
                      </div>
                      <div className="text-right text-xs text-gray-500">
                        <div>{creator.followers.toLocaleString()} followers</div>
                        <div>{creator.languages.join(', ')}</div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-3">
                      <button
                        onClick={() => {
                          setSelectedCreator(creator);
                          setShowMatchModal(true);
                        }}
                        className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                      >
                        <Heart className="h-4 w-4" />
                        <span>Match!</span>
                      </button>
                      <button className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center">
                        <MessageSquare className="h-4 w-4" />
                      </button>
                      <button className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center">
                        <Video className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pas de résultats */}
            {filteredCreators.length === 0 && !isAnalyzing && (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Users className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun match trouvé</h3>
                <p className="text-gray-600 mb-6">Essayez d'ajuster vos filtres ou lancez un nouveau matching IA</p>
                <button
                  onClick={runAIMatching}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
                >
                  <Sparkles className="h-5 w-5" />
                  <span>Nouveau Matching IA</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Modal de match */}
        {showMatchModal && selectedCreator && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Envoyer une demande de collaboration</h3>
                <button
                  onClick={() => setShowMatchModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="flex items-center space-x-3 mb-4">
                <span className="text-2xl">{selectedCreator.avatar}</span>
                <div>
                  <div className="font-medium">{selectedCreator.name}</div>
                  <div className="text-sm text-gray-600 capitalize">{selectedCreator.type}</div>
                </div>
                <div className="ml-auto text-right">
                  <div className="text-lg font-bold text-blue-600">{selectedCreator.matchScore}%</div>
                  <div className="text-xs text-gray-500">Match</div>
                </div>
              </div>

              <form onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                sendMatchRequest(
                  selectedCreator,
                  formData.get('message') as string,
                  formData.get('projectType') as string,
                  parseInt(formData.get('budget') as string) || undefined
                );
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Type de projet</label>
                    <select name="projectType" className="w-full p-2 border border-gray-300 rounded-lg">
                      <option value="collaboration">Collaboration créative</option>
                      <option value="freelance">Mission freelance</option>
                      <option value="partnership">Partenariat</option>
                      <option value="mentoring">Mentorat</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Budget (optionnel)</label>
                    <input
                      type="number"
                      name="budget"
                      placeholder="Budget en €"
                      className="w-full p-2 border border-gray-300 rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Message personnalisé</label>
                    <textarea
                      name="message"
                      required
                      placeholder="Décrivez votre projet et pourquoi vous souhaitez collaborer..."
                      className="w-full p-3 border border-gray-300 rounded-lg h-24 resize-none"
                    ></textarea>
                  </div>
                </div>

                <div className="flex space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowMatchModal(false)}
                    className="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300 transition-colors"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Envoyer 💌
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}