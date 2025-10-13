import React, { useState, useEffect, useRef, useMemo } from 'react';
import Map, { Marker, Popup, NavigationControl, GeolocateControl } from 'react-map-gl/mapbox';
import { MapPin, Heart, Clock, NavigationArrow, Funnel, MagnifyingGlassPlus, MagnifyingGlassMinus } from '@phosphor-icons/react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Input } from './ui/input';
import 'mapbox-gl/dist/mapbox-gl.css';

interface CaseMarker {
  id: string;
  latitude: number;
  longitude: number;
  title: string;
  description: string;
  urgency: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'resolved';
  createdAt: string;
  distance?: number;
}

interface MapViewProps {
  onCaseSelect?: (caseId: string) => void;
  showUserLocation?: boolean;
  initialZoom?: number;
}

// Clé API Mapbox (configurable via .env)
// Pour obtenir une clé gratuite : https://account.mapbox.com/access-tokens/
// 50,000 requêtes/mois gratuit
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoiaWEyZ29vZCIsImEiOiJjbHRlc3QxMjMifQ.demo_token_replace_with_real';

export const MapView: React.FC<MapViewProps> = ({
  onCaseSelect,
  showUserLocation = true,
  initialZoom = 12,
}) => {
  const [viewState, setViewState] = useState({
    longitude: 2.3522, // Paris par défaut
    latitude: 48.8566,
    zoom: initialZoom,
  });

  const [cases, setCases] = useState<CaseMarker[]>([]);
  const [selectedCase, setSelectedCase] = useState<CaseMarker | null>(null);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<{
    urgency?: string;
    status?: string;
    search?: string;
  }>({});

  const mapRef = useRef<any>(null);

  // Récupérer la position de l'utilisateur
  useEffect(() => {
    if (showUserLocation && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          };
          setUserLocation(loc);
          setViewState((prev) => ({
            ...prev,
            longitude: loc.lng,
            latitude: loc.lat,
          }));
        },
        (error) => {
          console.error('Erreur géolocalisation:', error);
        }
      );
    }
  }, [showUserLocation]);

  // Charger les cas depuis l'API
  useEffect(() => {
    fetchCases();
  }, [filter]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      
      // Construire l'URL avec filtres
      const params = new URLSearchParams();
      if (filter.urgency) params.append('urgency', filter.urgency);
      if (filter.status) params.append('status', filter.status);
      if (filter.search) params.append('search', filter.search);

      const response = await fetch(
        `http://localhost:8000/api/v1/ia2good/cases?${params.toString()}`
      );

      if (!response.ok) throw new Error('Erreur chargement des cas');

      const data = await response.json();

      // Transformer les cas en marqueurs avec coordonnées
      const markers: CaseMarker[] = data.map((caseItem: any) => ({
        id: caseItem.id,
        latitude: caseItem.latitude || 48.8566 + (Math.random() - 0.5) * 0.1,
        longitude: caseItem.longitude || 2.3522 + (Math.random() - 0.5) * 0.1,
        title: caseItem.title,
        description: caseItem.description,
        urgency: caseItem.urgency,
        status: caseItem.status,
        createdAt: caseItem.created_at,
      }));

      // Calculer la distance si position utilisateur disponible
      if (userLocation) {
        markers.forEach((marker) => {
          marker.distance = calculateDistance(
            userLocation.lat,
            userLocation.lng,
            marker.latitude,
            marker.longitude
          );
        });
      }

      setCases(markers);
    } catch (error) {
      console.error('Erreur fetch cases:', error);
      // Fallback avec données de démo
      setCases(generateDemoCases());
    } finally {
      setLoading(false);
    }
  };

  // Générer des cas de démo si API échoue
  const generateDemoCases = (): CaseMarker[] => {
    const demoLocations = [
      { lat: 48.8566, lng: 2.3522, title: 'Centre Paris' },
      { lat: 48.8606, lng: 2.3376, title: 'Tour Eiffel' },
      { lat: 48.8738, lng: 2.2950, title: 'Arc de Triomphe' },
      { lat: 48.8530, lng: 2.3499, title: 'Notre-Dame' },
      { lat: 48.8867, lng: 2.3431, title: 'Sacré-Cœur' },
    ];

    return demoLocations.map((loc, index) => ({
      id: `demo-${index}`,
      latitude: loc.lat,
      longitude: loc.lng,
      title: `Cas médical ${index + 1} - ${loc.title}`,
      description: 'Cas d\'urgence nécessitant une assistance médicale',
      urgency: ['critical', 'high', 'medium', 'low'][index % 4] as any,
      status: ['open', 'in_progress', 'resolved'][index % 3] as any,
      createdAt: new Date(Date.now() - index * 3600000).toISOString(),
    }));
  };

  // Calculer la distance entre deux points (formule Haversine)
  const calculateDistance = (lat1: number, lng1: number, lat2: number, lng2: number): number => {
    const R = 6371; // Rayon de la Terre en km
    const dLat = ((lat2 - lat1) * Math.PI) / 180;
    const dLng = ((lng2 - lng1) * Math.PI) / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) *
        Math.cos((lat2 * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Couleur du marqueur selon urgence
  const getMarkerColor = (urgency: string): string => {
    const colors = {
      critical: '#dc2626', // red-600
      high: '#ea580c', // orange-600
      medium: '#f59e0b', // amber-500
      low: '#10b981', // green-500
    };
    return colors[urgency as keyof typeof colors] || colors.low;
  };

  // Filtrer les cas
  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      if (filter.urgency && c.urgency !== filter.urgency) return false;
      if (filter.status && c.status !== filter.status) return false;
      if (
        filter.search &&
        !c.title.toLowerCase().includes(filter.search.toLowerCase()) &&
        !c.description.toLowerCase().includes(filter.search.toLowerCase())
      ) {
        return false;
      }
      return true;
    });
  }, [cases, filter]);

  // Centrer la carte sur un cas
  const flyToCase = (caseMarker: CaseMarker) => {
    setViewState({
      longitude: caseMarker.longitude,
      latitude: caseMarker.latitude,
      zoom: 15,
    });
    setSelectedCase(caseMarker);
  };

  // Zoom in/out
  const zoomIn = () => {
    setViewState((prev) => ({ ...prev, zoom: Math.min(prev.zoom + 1, 20) }));
  };

  const zoomOut = () => {
    setViewState((prev) => ({ ...prev, zoom: Math.max(prev.zoom - 1, 1) }));
  };

  return (
    <div className="relative w-full h-full">
      {/* Barre de filtres */}
      <Card className="absolute top-4 left-4 z-10 shadow-lg max-w-md">
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Funnel className="w-5 h-5 text-gray-600" />
            <h3 className="font-semibold">Filtrer les cas</h3>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Select
              value={filter.urgency || 'all'}
              onValueChange={(value) =>
                setFilter((prev) => ({ ...prev, urgency: value === 'all' ? undefined : value }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Urgence" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes</SelectItem>
                <SelectItem value="critical">Critique</SelectItem>
                <SelectItem value="high">Élevée</SelectItem>
                <SelectItem value="medium">Moyenne</SelectItem>
                <SelectItem value="low">Faible</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filter.status || 'all'}
              onValueChange={(value) =>
                setFilter((prev) => ({ ...prev, status: value === 'all' ? undefined : value }))
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Statut" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous</SelectItem>
                <SelectItem value="open">Ouverts</SelectItem>
                <SelectItem value="in_progress">En cours</SelectItem>
                <SelectItem value="resolved">Résolus</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Input
            placeholder="Rechercher un cas..."
            value={filter.search || ''}
            onChange={(e) => setFilter((prev) => ({ ...prev, search: e.target.value }))}
          />

          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              {filteredCases.length} cas trouvé{filteredCases.length > 1 ? 's' : ''}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilter({})}
              disabled={!filter.urgency && !filter.status && !filter.search}
            >
              Réinitialiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Contrôles zoom */}
      <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
        <Button size="icon" variant="secondary" onClick={zoomIn} className="shadow-lg">
          <MagnifyingGlassPlus className="w-5 h-5" />
        </Button>
        <Button size="icon" variant="secondary" onClick={zoomOut} className="shadow-lg">
          <MagnifyingGlassMinus className="w-5 h-5" />
        </Button>
      </div>

      {/* Liste des cas proches (si position utilisateur) */}
      {userLocation && filteredCases.length > 0 && (
        <Card className="absolute bottom-4 left-4 z-10 shadow-lg max-w-sm max-h-64 overflow-y-auto">
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center gap-2 mb-2">
              <NavigationArrow className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold">Cas à proximité</h3>
            </div>
            {filteredCases
              .filter((c) => c.distance !== undefined)
              .sort((a, b) => (a.distance || 0) - (b.distance || 0))
              .slice(0, 5)
              .map((c) => (
                <button
                  key={c.id}
                  onClick={() => flyToCase(c)}
                  className="w-full text-left p-2 rounded hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{c.title}</p>
                      <p className="text-xs text-gray-600">
                        {c.distance ? `${c.distance.toFixed(1)} km` : 'Distance inconnue'}
                      </p>
                    </div>
                    <Badge
                      variant={c.urgency === 'critical' ? 'destructive' : 'secondary'}
                      className="shrink-0"
                    >
                      {c.urgency}
                    </Badge>
                  </div>
                </button>
              ))}
          </CardContent>
        </Card>
      )}

      {/* Carte Mapbox */}
      <Map
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle="mapbox://styles/mapbox/streets-v12"
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        ref={mapRef}
      >
        {/* Contrôles de navigation */}
        <NavigationControl position="top-right" />

        {/* Géolocalisation */}
        {showUserLocation && <GeolocateControl position="top-right" />}

        {/* Position utilisateur */}
        {userLocation && (
          <Marker longitude={userLocation.lng} latitude={userLocation.lat}>
            <div className="relative">
              <div className="absolute -inset-2 bg-blue-500 rounded-full opacity-25 animate-ping"></div>
              <div className="relative bg-blue-600 rounded-full p-2">
                <NavigationArrow className="w-4 h-4 text-white" weight="fill" />
              </div>
            </div>
          </Marker>
        )}

        {/* Marqueurs des cas */}
        {filteredCases.map((caseMarker) => (
          <Marker
            key={caseMarker.id}
            longitude={caseMarker.longitude}
            latitude={caseMarker.latitude}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              setSelectedCase(caseMarker);
            }}
          >
            <div
              className="cursor-pointer transform transition-transform hover:scale-110"
              style={{ color: getMarkerColor(caseMarker.urgency) }}
            >
              <MapPin className="w-8 h-8" weight="fill" />
            </div>
          </Marker>
        ))}

        {/* Popup pour cas sélectionné */}
        {selectedCase && (
          <Popup
            longitude={selectedCase.longitude}
            latitude={selectedCase.latitude}
            anchor="top"
            onClose={() => setSelectedCase(null)}
            closeButton={true}
            closeOnClick={false}
          >
            <div className="p-3 max-w-xs">
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="font-semibold text-sm">{selectedCase.title}</h4>
                <Badge
                  variant={selectedCase.urgency === 'critical' ? 'destructive' : 'secondary'}
                  className="shrink-0"
                >
                  {selectedCase.urgency}
                </Badge>
              </div>

              <p className="text-xs text-gray-600 mb-2 line-clamp-2">{selectedCase.description}</p>

              <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {new Date(selectedCase.createdAt).toLocaleDateString('fr-FR')}
                </span>
                {selectedCase.distance && (
                  <span className="flex items-center gap-1">
                    <NavigationArrow className="w-3 h-3" />
                    {selectedCase.distance.toFixed(1)} km
                  </span>
                )}
              </div>

              <Button
                size="sm"
                className="w-full"
                onClick={() => {
                  if (onCaseSelect) onCaseSelect(selectedCase.id);
                }}
              >
                <Heart className="w-4 h-4 mr-2" />
                Proposer mon aide
              </Button>
            </div>
          </Popup>
        )}
      </Map>

      {/* Indicateur de chargement */}
      {loading && (
        <div className="absolute inset-0 bg-white/80 flex items-center justify-center z-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement de la carte...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;
