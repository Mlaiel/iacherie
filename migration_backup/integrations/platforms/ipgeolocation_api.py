#!/usr/bin/env python3
"""
🌍 IPGEOLOCATION API INTEGRATION
Intégration complète pour géolocalisation et analyse géographique
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GeolocationData:
    """Classe pour représenter les données de géolocalisation"""
    ip: str
    country_code2: str
    country_code3: str
    country_name: str
    state_prov: str
    city: str
    zipcode: str
    latitude: float
    longitude: float
    is_eu: bool
    calling_code: str
    country_tld: str
    languages: str
    country_flag: str
    geoname_id: str
    isp: str
    connection_type: str
    organization: str
    currency: Dict[str, str]
    time_zone: Dict[str, str]
    accuracy_radius: Optional[int] = None
    asn: Optional[str] = None
    threat_level: Optional[str] = None

@dataclass
class TimezoneData:
    """Classe pour représenter les données de fuseau horaire"""
    timezone: str
    timezone_offset: float
    timezone_offset_with_dst: float
    date: str
    date_time: str
    date_time_txt: str
    date_time_wti: str
    date_time_ymd: str
    date_time_unix: float
    time_24: str
    time_12: str
    week: int
    month: int
    year: int
    year_abbr: str
    is_dst: bool
    dst_savings: float

@dataclass
class SecurityData:
    """Classe pour représenter les données de sécurité"""
    threat_level: str
    is_tor: bool
    is_proxy: bool
    is_anonymous: bool
    is_known_attacker: bool
    is_known_abuser: bool
    is_threat: bool
    is_bogon: bool
    security_score: int

class IPGeolocationAPI:
    """Client API pour IPGeolocation"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.ipgeolocation.io"
        self.session = None
        self.rate_limit_remaining = 1000  # Plan gratuit: 1000 requêtes/mois
        self.rate_limit_reset = None
        
        # Headers par défaut
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Ainfluencer-Platform/1.0'
        }
        
        logger.info(f"🌍 IPGeolocationAPI initialisé avec clé: {api_key[:20]}...")

    async def __aenter__(self):
        """Initialiser la session async"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Faire une requête à l'API IPGeolocation"""
        url = f"{self.base_url}/{endpoint}"
        
        # Ajouter la clé API aux paramètres
        if not params:
            params = {}
        params['apiKey'] = self.api_key
        
        try:
            async with self.session.get(url, params=params) as response:
                # Mettre à jour les limites de taux si disponibles
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', self.rate_limit_remaining))
                self.rate_limit_reset = response.headers.get('X-RateLimit-Reset')
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Requête réussie: {endpoint}")
                    return data
                elif response.status == 429:
                    logger.warning(f"⚠️ Limite de taux atteinte. Reset: {self.rate_limit_reset}")
                    raise Exception("Rate limit exceeded")
                elif response.status == 401:
                    logger.error("❌ Clé API invalide ou expirée")
                    raise Exception("Invalid API key")
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    error_data = await response.text()
                    raise Exception(f"API Error {response.status}: {error_data}")
                    
        except Exception as e:
            logger.error(f"❌ Erreur de requête: {e}")
            raise

    async def get_geolocation(self, ip: str = None, include_hostname: bool = False) -> Optional[GeolocationData]:
        """Obtenir la géolocalisation d'une IP"""
        
        params = {}
        if ip:
            params['ip'] = ip
        if include_hostname:
            params['include'] = 'hostname'
            
        logger.info(f"🌍 Géolocalisation pour IP: {ip or 'IP actuelle'}")
        
        try:
            data = await self._make_request('ipgeo', params)
            
            return GeolocationData(
                ip=data.get('ip', ''),
                country_code2=data.get('country_code2', ''),
                country_code3=data.get('country_code3', ''),
                country_name=data.get('country_name', ''),
                state_prov=data.get('state_prov', ''),
                city=data.get('city', ''),
                zipcode=data.get('zipcode', ''),
                latitude=float(data.get('latitude', 0)),
                longitude=float(data.get('longitude', 0)),
                is_eu=data.get('is_eu', False),
                calling_code=data.get('calling_code', ''),
                country_tld=data.get('country_tld', ''),
                languages=data.get('languages', ''),
                country_flag=data.get('country_flag', ''),
                geoname_id=data.get('geoname_id', ''),
                isp=data.get('isp', ''),
                connection_type=data.get('connection_type', ''),
                organization=data.get('organization', ''),
                currency=data.get('currency', {}),
                time_zone=data.get('time_zone', {}),
                accuracy_radius=data.get('accuracy_radius'),
                asn=data.get('asn'),
                threat_level=data.get('threat_level')
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur de géolocalisation: {e}")
            return None

    async def get_timezone(self, ip: str = None, lat: float = None, lng: float = None) -> Optional[TimezoneData]:
        """Obtenir les informations de fuseau horaire"""
        
        params = {}
        if ip:
            params['ip'] = ip
        elif lat is not None and lng is not None:
            params['lat'] = lat
            params['long'] = lng
        else:
            # Utiliser l'IP actuelle
            pass
            
        logger.info(f"🕐 Fuseau horaire pour: {ip or f'Lat/Lng: {lat},{lng}' if lat else 'IP actuelle'}")
        
        try:
            data = await self._make_request('timezone', params)
            
            return TimezoneData(
                timezone=data.get('timezone', ''),
                timezone_offset=float(data.get('timezone_offset', 0)),
                timezone_offset_with_dst=float(data.get('timezone_offset_with_dst', 0)),
                date=data.get('date', ''),
                date_time=data.get('date_time', ''),
                date_time_txt=data.get('date_time_txt', ''),
                date_time_wti=data.get('date_time_wti', ''),
                date_time_ymd=data.get('date_time_ymd', ''),
                date_time_unix=float(data.get('date_time_unix', 0)),
                time_24=data.get('time_24', ''),
                time_12=data.get('time_12', ''),
                week=int(data.get('week', 0)),
                month=int(data.get('month', 0)),
                year=int(data.get('year', 0)),
                year_abbr=data.get('year_abbr', ''),
                is_dst=data.get('is_dst', False),
                dst_savings=float(data.get('dst_savings', 0))
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur de fuseau horaire: {e}")
            return None

    async def get_security_info(self, ip: str = None) -> Optional[SecurityData]:
        """Obtenir les informations de sécurité d'une IP"""
        
        params = {}
        if ip:
            params['ip'] = ip
            
        logger.info(f"🛡️ Sécurité pour IP: {ip or 'IP actuelle'}")
        
        try:
            data = await self._make_request('ipgeo-security', params)
            
            return SecurityData(
                threat_level=data.get('threat_level', 'unknown'),
                is_tor=data.get('is_tor', False),
                is_proxy=data.get('is_proxy', False),
                is_anonymous=data.get('is_anonymous', False),
                is_known_attacker=data.get('is_known_attacker', False),
                is_known_abuser=data.get('is_known_abuser', False),
                is_threat=data.get('is_threat', False),
                is_bogon=data.get('is_bogon', False),
                security_score=int(data.get('security_score', 0))
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur de sécurité: {e}")
            return None

    async def bulk_geolocation(self, ips: List[str]) -> Dict[str, GeolocationData]:
        """Géolocalisation en masse (max 50 IPs)"""
        
        if len(ips) > 50:
            logger.warning("⚠️ Limite de 50 IPs par requête bulk")
            ips = ips[:50]
            
        params = {
            'ips': ','.join(ips)
        }
        
        logger.info(f"🌍 Géolocalisation en masse: {len(ips)} IPs")
        
        try:
            data = await self._make_request('ipgeo-bulk', params)
            
            results = {}
            for item in data:
                geo_data = GeolocationData(
                    ip=item.get('ip', ''),
                    country_code2=item.get('country_code2', ''),
                    country_code3=item.get('country_code3', ''),
                    country_name=item.get('country_name', ''),
                    state_prov=item.get('state_prov', ''),
                    city=item.get('city', ''),
                    zipcode=item.get('zipcode', ''),
                    latitude=float(item.get('latitude', 0)),
                    longitude=float(item.get('longitude', 0)),
                    is_eu=item.get('is_eu', False),
                    calling_code=item.get('calling_code', ''),
                    country_tld=item.get('country_tld', ''),
                    languages=item.get('languages', ''),
                    country_flag=item.get('country_flag', ''),
                    geoname_id=item.get('geoname_id', ''),
                    isp=item.get('isp', ''),
                    connection_type=item.get('connection_type', ''),
                    organization=item.get('organization', ''),
                    currency=item.get('currency', {}),
                    time_zone=item.get('time_zone', {})
                )
                results[geo_data.ip] = geo_data
                
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur de géolocalisation en masse: {e}")
            return {}

    async def get_user_analytics(self, user_ips: List[str]) -> Dict:
        """Analyser les données géographiques des utilisateurs"""
        try:
            # Géolocalisation en masse
            geo_results = await self.bulk_geolocation(user_ips)
            
            # Analyser les données
            countries = {}
            cities = {}
            timezones = {}
            isps = {}
            
            for ip, geo_data in geo_results.items():
                # Compter par pays
                country = geo_data.country_name
                countries[country] = countries.get(country, 0) + 1
                
                # Compter par ville
                city = f"{geo_data.city}, {geo_data.country_name}"
                cities[city] = cities.get(city, 0) + 1
                
                # Compter par fuseau horaire
                tz = geo_data.time_zone.get('name', 'Unknown')
                timezones[tz] = timezones.get(tz, 0) + 1
                
                # Compter par ISP
                isp = geo_data.isp
                isps[isp] = isps.get(isp, 0) + 1
            
            # Trier les résultats
            top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:10]
            top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]
            top_timezones = sorted(timezones.items(), key=lambda x: x[1], reverse=True)[:5]
            top_isps = sorted(isps.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_ips': len(user_ips),
                'successful_geolocations': len(geo_results),
                'top_countries': top_countries,
                'top_cities': top_cities,
                'top_timezones': top_timezones,
                'top_isps': top_isps,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur d'analyse utilisateur: {e}")
            return {}

    def get_rate_limit_status(self) -> Dict:
        """Obtenir le statut des limites de taux"""
        return {
            'remaining': self.rate_limit_remaining,
            'reset': self.rate_limit_reset,
            'plan': 'free' if self.rate_limit_remaining <= 1000 else 'paid'
        }

# Fonctions utilitaires
def load_credentials() -> str:
    """Charger les credentials depuis les variables d'environnement"""
    api_key = os.getenv('IPGEOLOCATION_API_KEY')
    
    if not api_key:
        raise ValueError("La clé API IPGeolocation n'est pas configurée")
        
    return api_key

async def test_integration():
    """Tester l'intégration IPGeolocation"""
    try:
        api_key = load_credentials()
        
        async with IPGeolocationAPI(api_key) as api:
            # Test géolocalisation IP actuelle
            print("🌍 Test géolocalisation IP actuelle...")
            geo_data = await api.get_geolocation()
            
            if geo_data:
                print(f"✅ Géolocalisation réussie: {geo_data.city}, {geo_data.country_name}")
                print(f"📍 Coordonnées: {geo_data.latitude}, {geo_data.longitude}")
                print(f"🏢 ISP: {geo_data.isp}")
                
                # Test fuseau horaire
                print("\n🕐 Test fuseau horaire...")
                tz_data = await api.get_timezone()
                if tz_data:
                    print(f"✅ Fuseau horaire: {tz_data.timezone}")
                    print(f"⏰ Heure locale: {tz_data.time_24}")
                
                # Test sécurité
                print("\n🛡️ Test sécurité...")
                security_data = await api.get_security_info()
                if security_data:
                    print(f"✅ Niveau de menace: {security_data.threat_level}")
                    print(f"🔒 Score sécurité: {security_data.security_score}/100")
                    
                # Test géolocalisation d'IPs spécifiques
                print("\n🌐 Test géolocalisation d'IPs spécifiques...")
                test_ips = ['8.8.8.8', '1.1.1.1']
                bulk_results = await api.bulk_geolocation(test_ips)
                
                for ip, data in bulk_results.items():
                    print(f"✅ {ip}: {data.city}, {data.country_name} ({data.isp})")
                
                # Statut des limites
                rate_status = api.get_rate_limit_status()
                print(f"\n📊 Requêtes restantes: {rate_status['remaining']}")
                
                return True
            else:
                print("❌ Échec de géolocalisation")
                return False
                
    except Exception as e:
        print(f"❌ Erreur de test: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)