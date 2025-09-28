'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Users, Search, Filter, Star, MapPin, Clock, Tag, MessageCircle, Video, Music, Palette } from 'lucide-react';

interface Creator {
  id: string;
  username: string;
  avatar: string;
  skills: string[];
  genres: string[];
  location: string;
  rating: number;
  completedProjects: number;
  isOnline: boolean;
  bio: string;
  collaborationTypes: string[];
  languages: string[];
  price_range: string;
}

interface MatchResult {
  creator: Creator;
  compatibility_score: number;
  matching_factors: string[];
  collaboration_potential: string;
}

export default function CollaborationPage() {
  const [creators, setCreators] = useState<Creator[]>([]);
  const [matches, setMatches] = useState<MatchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [activeCollaborations, setActiveCollaborations] = useState(0);

  // Données simulées réalistes
  const mockCreators: Creator[] = [
    {
      id: '1',
      username: 'BeatMasterPro',
      avatar: '🎵',
      skills: ['Production Audio', 'Mastering', 'Sound Design'],
      genres: ['Electronic', 'Techno', 'House'],
      location: 'Paris, France',
      rating: 4.9,
      completedProjects: 127,
      isOnline: true,
      bio: 'Producteur professionnel avec 8 ans d\'expérience en musique électronique',
      collaborationTypes: ['Remix', 'Production Originale', 'Mastering'],
      languages: ['Français', 'Anglais', 'Espagnol'],
      price_range: '500-2000€'
    },
    {
      id: '2',
      username: 'VocalHarmony',
      avatar: '🎤',
      skills: ['Chant', 'Écriture', 'Harmonisation'],
      genres: ['Pop', 'R&B', 'Soul'],
      location: 'Londres, UK',
      rating: 4.8,
      completedProjects: 89,
      isOnline: true,
      bio: 'Chanteuse professionnelle spécialisée en harmonies vocales et top-lines',
      collaborationTypes: ['Featuring', 'Harmonies', 'Écriture'],
      languages: ['Anglais', 'Français'],
      price_range: '300-1500€'
    },
    {
      id: '3',
      username: 'VideoCreativeStudio',
      avatar: '🎬',
      skills: ['Montage Vidéo', 'Motion Graphics', 'Color Grading'],
      genres: ['Music Video', 'Commercial', 'Documentary'],
      location: 'Los Angeles, USA',
      rating: 4.7,
      completedProjects: 156,
      isOnline: false,
      bio: 'Studio créatif spécialisé en vidéos musicales et contenus promotionnels',
      collaborationTypes: ['Clip Vidéo', 'Visualiseur', 'Promotion'],
      languages: ['Anglais', 'Espagnol'],
      price_range: '800-5000€'
    },
    {
      id: '4',
      username: 'RemixKing',
      avatar: '🎛️',
      skills: ['Remix', 'DJ', 'Production Live'],
      genres: ['EDM', 'Future Bass', 'Trap'],
      location: 'Berlin, Allemagne',
      rating: 4.9,
      completedProjects: 203,
      isOnline: true,
      bio: 'DJ/Producteur international spécialisé en remixes et sets live',
      collaborationTypes: ['Remix', 'Collaboration Live', 'Festival'],
      languages: ['Allemand', 'Anglais', 'Français'],
      price_range: '1000-3000€'
    }
  ];

  const availableSkills = ['Production Audio', 'Mastering', 'Chant', 'Écriture', 'Montage Vidéo', 'DJ', 'Remix', 'Sound Design', 'Motion Graphics'];
  const availableGenres = ['Electronic', 'Pop', 'Hip-Hop', 'Rock', 'Jazz', 'Classical', 'EDM', 'R&B'];

  useEffect(() => {
    // Simulation du chargement des créateurs
    setTimeout(() => {
      setCreators(mockCreators);
      setActiveCollaborations(47);
    }, 1000);
  }, []);

  const findMatches = async () => {
    setLoading(true);
    
    // Simulation d'algorithme de matching IA
    setTimeout(() => {
      const simulatedMatches: MatchResult[] = mockCreators.map(creator => ({
        creator,
        compatibility_score: Math.floor(Math.random() * 30) + 70, // 70-100%
        matching_factors: [
          'Compétences complémentaires',
          'Genres compatibles', 
          'Disponibilité similaire',
          'Historique de collaboration positif'
        ].slice(0, Math.floor(Math.random() * 4) + 1),
        collaboration_potential: ['Excellent', 'Très bon', 'Bon'][Math.floor(Math.random() * 3)]
      })).sort((a, b) => b.compatibility_score - a.compatibility_score);

      setMatches(simulatedMatches);
      setLoading(false);
    }, 2000);
  };

  const initiateCollaboration = async (creatorId: string) => {
    // Simulation d'envoi de demande de collaboration
    alert(`Demande de collaboration envoyée avec succès! 🤝`);
    setActiveCollaborations(prev => prev + 1);
  };

  const filteredCreators = creators.filter(creator => {
    const matchesSearch = creator.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         creator.skills.some(skill => skill.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesSkills = selectedSkills.length === 0 || selectedSkills.some(skill => creator.skills.includes(skill));
    const matchesGenres = selectedGenres.length === 0 || selectedGenres.some(genre => creator.genres.includes(genre));
    
    return matchesSearch && matchesSkills && matchesGenres;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-green-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/" className="flex items-center text-gray-600 hover:text-emerald-600">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Retour
              </Link>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-3">
                <Users className="h-8 w-8 text-emerald-600" />
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Collaboration Hub</h1>
                  <p className="text-sm text-gray-600">Matching intelligent et projets collaboratifs</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                🤝 {activeCollaborations} Collaborations Actives
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Créateurs Actifs</p>
                <p className="text-2xl font-bold text-emerald-600">{creators.length}</p>
              </div>
              <Users className="h-12 w-12 text-emerald-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">En Ligne</p>
                <p className="text-2xl font-bold text-green-600">
                  {creators.filter(c => c.isOnline).length}
                </p>
              </div>
              <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Collaborations</p>
                <p className="text-2xl font-bold text-blue-600">{activeCollaborations}</p>
              </div>
              <MessageCircle className="h-12 w-12 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Taux de Réussite</p>
                <p className="text-2xl font-bold text-purple-600">94.2%</p>
              </div>
              <Star className="h-12 w-12 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Matching IA Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">🤖 Matching IA Intelligent</h2>
          <div className="flex flex-col lg:flex-row gap-6">
            <div className="lg:w-1/3">
              <button
                onClick={findMatches}
                disabled={loading}
                className="w-full bg-gradient-to-r from-emerald-600 to-green-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-emerald-700 hover:to-green-700 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Analyse IA en cours...
                  </div>
                ) : (
                  '🎯 Lancer le Matching IA'
                )}
              </button>
              <p className="text-sm text-gray-600 mt-2">
                Notre IA analyse 50+ critères pour vous trouver les collaborateurs parfaits
              </p>
            </div>

            <div className="lg:w-2/3">
              {matches.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">✨ Matches Recommandés par l'IA</h3>
                  <div className="space-y-4">
                    {matches.slice(0, 3).map((match) => (
                      <div key={match.creator.id} className="border border-emerald-200 rounded-lg p-4 bg-emerald-50">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{match.creator.avatar}</span>
                            <div>
                              <h4 className="font-semibold">{match.creator.username}</h4>
                              <p className="text-sm text-gray-600">{match.creator.bio}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-bold text-emerald-600">
                              {match.compatibility_score}% Compatible
                            </div>
                            <div className="text-sm text-gray-600">{match.collaboration_potential}</div>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-2 mb-3">
                          {match.matching_factors.map((factor, index) => (
                            <span key={index} className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full">
                              {factor}
                            </span>
                          ))}
                        </div>
                        <button
                          onClick={() => initiateCollaboration(match.creator.id)}
                          className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-emerald-700 transition-colors"
                        >
                          💬 Démarrer Collaboration
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Filtres et Recherche */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">🔍 Recherche Avancée</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recherche</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Rechercher créateurs, compétences..."
                  className="pl-10 w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Compétences</label>
              <select
                multiple
                value={selectedSkills}
                onChange={(e) => setSelectedSkills(Array.from(e.target.selectedOptions, option => option.value))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
              >
                {availableSkills.map(skill => (
                  <option key={skill} value={skill}>{skill}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Genres</label>
              <select
                multiple
                value={selectedGenres}
                onChange={(e) => setSelectedGenres(Array.from(e.target.selectedOptions, option => option.value))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
              >
                {availableGenres.map(genre => (
                  <option key={genre} value={genre}>{genre}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Liste des Créateurs */}
        <div className="bg-white rounded-xl shadow-lg">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">👥 Créateurs Disponibles ({filteredCreators.length})</h2>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCreators.map((creator) => (
                <div key={creator.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <span className="text-3xl">{creator.avatar}</span>
                      <div>
                        <h3 className="font-semibold text-lg">{creator.username}</h3>
                        <div className="flex items-center space-x-2">
                          <div className={`h-2 w-2 rounded-full ${creator.isOnline ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                          <span className="text-sm text-gray-600">
                            {creator.isOnline ? 'En ligne' : 'Hors ligne'}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 text-yellow-500 fill-current" />
                      <span className="text-sm font-medium">{creator.rating}</span>
                    </div>
                  </div>

                  <p className="text-gray-600 text-sm mb-4">{creator.bio}</p>

                  <div className="space-y-3 mb-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Compétences:</h4>
                      <div className="flex flex-wrap gap-1">
                        {creator.skills.map((skill, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Genres:</h4>
                      <div className="flex flex-wrap gap-1">
                        {creator.genres.map((genre, index) => (
                          <span key={index} className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
                            {genre}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <MapPin className="h-4 w-4" />
                        <span>{creator.location}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Clock className="h-4 w-4" />
                        <span>{creator.completedProjects} projets</span>
                      </div>
                    </div>

                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Budget: </span>
                      <span className="text-emerald-600">{creator.price_range}</span>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => initiateCollaboration(creator.id)}
                      className="flex-1 bg-emerald-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
                    >
                      🤝 Collaborer
                    </button>
                    <button className="bg-gray-100 text-gray-700 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                      💬 Message
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}