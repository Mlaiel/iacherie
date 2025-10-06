import { NextRequest, NextResponse } from 'next/server';

// Configuration Spotify
const SPOTIFY_CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const SPOTIFY_CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;

console.log("🎵 SPOTIFY API CONFIGURATION:");
console.log("Client ID:", SPOTIFY_CLIENT_ID ? "✅" : "❌");
console.log("Client Secret:", SPOTIFY_CLIENT_SECRET ? "✅" : "❌");

// Cache pour le token d'accès
let cachedToken: { access_token: string; expires_at: number } | null = null;

// Obtenir un token d'accès Spotify
async function getSpotifyAccessToken() {
  // Vérifier si on a un token en cache valide
  if (cachedToken && cachedToken.expires_at > Date.now()) {
    console.log("✅ Utilisation du token Spotify en cache");
    return cachedToken.access_token;
  }

  if (!SPOTIFY_CLIENT_ID || !SPOTIFY_CLIENT_SECRET) {
    throw new Error('Spotify credentials not configured');
  }

  console.log("🔄 Obtention d'un nouveau token Spotify...");

  const response = await fetch('https://accounts.spotify.com/api/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64')}`
    },
    body: 'grant_type=client_credentials'
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Spotify token error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  
  // Mettre en cache le token (expire dans 1 heure)
  cachedToken = {
    access_token: data.access_token,
    expires_at: Date.now() + (data.expires_in - 300) * 1000 // 5 min de marge
  };

  console.log("✅ Nouveau token Spotify obtenu");
  return data.access_token;
}

// Rechercher des pistes
async function searchTracks(query: string, limit: number = 10) {
  const token = await getSpotifyAccessToken();

  const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=track&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify search error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.tracks.items.map((track: any) => ({
    id: track.id,
    name: track.name,
    artist: track.artists.map((a: any) => a.name).join(', '),
    album: track.album.name,
    duration_ms: track.duration_ms,
    preview_url: track.preview_url,
    external_url: track.external_urls.spotify,
    image: track.album.images[0]?.url,
    popularity: track.popularity
  }));
}

// Obtenir des recommandations
async function getRecommendations(seedTracks: string[], limit: number = 10) {
  const token = await getSpotifyAccessToken();

  const seeds = seedTracks.slice(0, 5).join(','); // Max 5 seeds

  const response = await fetch(`https://api.spotify.com/v1/recommendations?seed_tracks=${seeds}&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify recommendations error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.tracks.map((track: any) => ({
    id: track.id,
    name: track.name,
    artist: track.artists.map((a: any) => a.name).join(', '),
    album: track.album.name,
    preview_url: track.preview_url,
    external_url: track.external_urls.spotify,
    image: track.album.images[0]?.url
  }));
}

// Obtenir des playlists populaires
async function getFeaturedPlaylists(limit: number = 10) {
  const token = await getSpotifyAccessToken();

  const response = await fetch(`https://api.spotify.com/v1/browse/featured-playlists?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify playlists error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.playlists.items.map((playlist: any) => ({
    id: playlist.id,
    name: playlist.name,
    description: playlist.description,
    tracks_total: playlist.tracks.total,
    external_url: playlist.external_urls.spotify,
    image: playlist.images[0]?.url,
    owner: playlist.owner.display_name
  }));
}

// Obtenir les top tracks d'un artiste
async function getArtistTopTracks(artistId: string) {
  const token = await getSpotifyAccessToken();

  const response = await fetch(`https://api.spotify.com/v1/artists/${artistId}/top-tracks?market=US`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify artist tracks error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.tracks.map((track: any) => ({
    id: track.id,
    name: track.name,
    album: track.album.name,
    preview_url: track.preview_url,
    external_url: track.external_urls.spotify,
    image: track.album.images[0]?.url,
    popularity: track.popularity
  }));
}

// Rechercher des artistes
async function searchArtists(query: string, limit: number = 10) {
  const token = await getSpotifyAccessToken();

  const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=artist&limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify artist search error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.artists.items.map((artist: any) => ({
    id: artist.id,
    name: artist.name,
    genres: artist.genres,
    popularity: artist.popularity,
    followers: artist.followers.total,
    external_url: artist.external_urls.spotify,
    image: artist.images[0]?.url
  }));
}

// Obtenir les catégories
async function getCategories(limit: number = 20) {
  const token = await getSpotifyAccessToken();

  const response = await fetch(`https://api.spotify.com/v1/browse/categories?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Spotify categories error: ${response.status}`);
  }

  const data = await response.json();
  
  return data.categories.items.map((category: any) => ({
    id: category.id,
    name: category.name,
    icon: category.icons[0]?.url
  }));
}

export async function POST(request: NextRequest) {
  try {
    const { action, ...params } = await request.json();

    console.log("🎵 SPOTIFY API REQUEST:", action);

    let result;

    switch (action) {
      case 'search_tracks':
        result = await searchTracks(params.query, params.limit);
        break;

      case 'search_artists':
        result = await searchArtists(params.query, params.limit);
        break;

      case 'get_recommendations':
        result = await getRecommendations(params.seedTracks, params.limit);
        break;

      case 'get_featured_playlists':
        result = await getFeaturedPlaylists(params.limit);
        break;

      case 'get_artist_top_tracks':
        result = await getArtistTopTracks(params.artistId);
        break;

      case 'get_categories':
        result = await getCategories(params.limit);
        break;

      default:
        return NextResponse.json({
          success: false,
          error: `Action inconnue: ${action}`
        }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      data: result,
      action: action,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error("❌ Erreur Spotify:", error);
    
    return NextResponse.json({
      success: false,
      error: error.message || "Erreur lors de l'appel Spotify"
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    message: "Spotify API Integration - Music & Audio",
    status: "OPERATIONAL",
    
    endpoints: {
      POST: "/api/spotify"
    },

    actions: {
      search_tracks: {
        description: "Rechercher des pistes musicales",
        parameters: {
          action: "search_tracks",
          query: "string (required) - Terme de recherche",
          limit: "number (optional) - Nombre de résultats (default: 10)"
        }
      },
      search_artists: {
        description: "Rechercher des artistes",
        parameters: {
          action: "search_artists",
          query: "string (required) - Nom de l'artiste",
          limit: "number (optional) - Nombre de résultats (default: 10)"
        }
      },
      get_recommendations: {
        description: "Obtenir des recommandations musicales",
        parameters: {
          action: "get_recommendations",
          seedTracks: "string[] (required) - IDs de pistes pour les recommandations",
          limit: "number (optional) - Nombre de recommandations (default: 10)"
        }
      },
      get_featured_playlists: {
        description: "Obtenir les playlists populaires",
        parameters: {
          action: "get_featured_playlists",
          limit: "number (optional) - Nombre de playlists (default: 10)"
        }
      },
      get_artist_top_tracks: {
        description: "Obtenir les meilleures pistes d'un artiste",
        parameters: {
          action: "get_artist_top_tracks",
          artistId: "string (required) - ID Spotify de l'artiste"
        }
      },
      get_categories: {
        description: "Obtenir les catégories musicales",
        parameters: {
          action: "get_categories",
          limit: "number (optional) - Nombre de catégories (default: 20)"
        }
      }
    },

    features: [
      "Recherche de musique et artistes",
      "Recommandations personnalisées",
      "Playlists populaires",
      "Catégories musicales",
      "Aperçus audio (30 secondes)",
      "Métadonnées complètes"
    ],

    configuration: {
      client_id: !!SPOTIFY_CLIENT_ID,
      client_secret: !!SPOTIFY_CLIENT_SECRET,
      token_caching: true
    },

    exemples: [
      {
        action: "search_tracks",
        request: { action: "search_tracks", query: "jazz piano", limit: 5 }
      },
      {
        action: "search_artists",
        request: { action: "search_artists", query: "Daft Punk" }
      },
      {
        action: "get_featured_playlists",
        request: { action: "get_featured_playlists", limit: 10 }
      }
    ]
  });
}
