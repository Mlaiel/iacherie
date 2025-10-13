#!/usr/bin/env python3
"""
💰 COINGECKO API INTEGRATION
Service gratuit de données crypto-monnaies
"""

import os
import sys
import json
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib.parse

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CoinData:
    """Données d'une crypto-monnaie"""
    id: str
    symbol: str
    name: str
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    fully_diluted_valuation: Optional[float] = None
    total_volume: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    market_cap_change_24h: Optional[float] = None
    market_cap_change_percentage_24h: Optional[float] = None
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    ath: Optional[float] = None
    ath_change_percentage: Optional[float] = None
    ath_date: Optional[str] = None
    atl: Optional[float] = None
    atl_change_percentage: Optional[float] = None
    atl_date: Optional[str] = None
    last_updated: Optional[str] = None
    image: Optional[str] = None

@dataclass
class PriceHistory:
    """Historique des prix"""
    coin_id: str
    prices: List[List[float]]  # [timestamp, price]
    market_caps: List[List[float]]
    total_volumes: List[List[float]]
    period: str
    currency: str = "usd"

@dataclass
class ExchangeRate:
    """Taux de change entre devises"""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: str

class CoinGeckoAPI:
    """Client pour CoinGecko API - Service gratuit de données crypto"""
    
    def __init__(self, api_key: Optional[str] = None):
        # CoinGecko gratuit avec limites, Pro avec clé API
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
        # Limites de l'API gratuite
        self.rate_limits = {
            "demo": {
                "calls_per_minute": 30,
                "monthly_calls": 10000
            },
            "pro": {
                "calls_per_minute": 500,
                "monthly_calls": 1000000
            }
        }
        
        # Devises supportées populaires
        self.supported_currencies = [
            "usd", "eur", "jpy", "gbp", "aud", "cad", "chf", "cny", "sek", "nzd",
            "btc", "eth", "bnb", "xrp", "ada", "dot", "ltc", "bch", "link", "xlm"
        ]
        
        logger.info("💰 CoinGeckoAPI initialisé - Service gratuit crypto")

    async def __aenter__(self):
        """Initialiser la session async"""
        headers = {'Accept': 'application/json'}
        
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
            
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermer la session async"""
        if self.session:
            await self.session.close()

    async def get_coin_list(self, include_platform: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Obtenir la liste de toutes les crypto-monnaies"""
        
        logger.info("💰 Récupération de la liste des crypto-monnaies...")
        
        try:
            url = f"{self.base_url}/coins/list"
            params = {}
            
            if include_platform:
                params['include_platform'] = 'true'
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    coins = await response.json()
                    logger.info(f"✅ {len(coins)} crypto-monnaies disponibles")
                    return coins
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def get_coin_data(self, 
                          coin_id: str,
                          vs_currency: str = "usd",
                          include_market_cap: bool = True,
                          include_24hr_vol: bool = True,
                          include_24hr_change: bool = True) -> Optional[CoinData]:
        """Obtenir les données détaillées d'une crypto-monnaie"""
        
        logger.info(f"💰 Récupération données pour {coin_id}")
        
        try:
            url = f"{self.base_url}/coins/{coin_id}"
            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extraire les données du marché
                    market_data = data.get('market_data', {})
                    current_price = market_data.get('current_price', {}).get(vs_currency)
                    
                    coin_data = CoinData(
                        id=data.get('id', ''),
                        symbol=data.get('symbol', '').upper(),
                        name=data.get('name', ''),
                        current_price=current_price,
                        market_cap=market_data.get('market_cap', {}).get(vs_currency),
                        market_cap_rank=market_data.get('market_cap_rank'),
                        total_volume=market_data.get('total_volume', {}).get(vs_currency),
                        high_24h=market_data.get('high_24h', {}).get(vs_currency),
                        low_24h=market_data.get('low_24h', {}).get(vs_currency),
                        price_change_24h=market_data.get('price_change_24h'),
                        price_change_percentage_24h=market_data.get('price_change_percentage_24h'),
                        market_cap_change_24h=market_data.get('market_cap_change_24h'),
                        market_cap_change_percentage_24h=market_data.get('market_cap_change_percentage_24h'),
                        circulating_supply=market_data.get('circulating_supply'),
                        total_supply=market_data.get('total_supply'),
                        max_supply=market_data.get('max_supply'),
                        ath=market_data.get('ath', {}).get(vs_currency),
                        ath_change_percentage=market_data.get('ath_change_percentage', {}).get(vs_currency),
                        ath_date=market_data.get('ath_date', {}).get(vs_currency),
                        atl=market_data.get('atl', {}).get(vs_currency),
                        atl_change_percentage=market_data.get('atl_change_percentage', {}).get(vs_currency),
                        atl_date=market_data.get('atl_date', {}).get(vs_currency),
                        last_updated=market_data.get('last_updated'),
                        image=data.get('image', {}).get('large')
                    )
                    
                    logger.info(f"✅ Données récupérées pour {coin_data.name} ({coin_data.symbol})")
                    return coin_data
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def get_market_data(self, 
                            vs_currency: str = "usd",
                            per_page: int = 100,
                            page: int = 1,
                            order: str = "market_cap_desc") -> Optional[List[CoinData]]:
        """Obtenir les données de marché pour plusieurs crypto-monnaies"""
        
        logger.info(f"💰 Récupération données de marché (page {page}, {per_page} items)")
        
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': vs_currency,
                'order': order,
                'per_page': min(per_page, 250),  # Max 250 pour l'API gratuite
                'page': page,
                'sparkline': 'false',
                'price_change_percentage': '24h'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    coins_data = []
                    for coin_info in data:
                        coin_data = CoinData(
                            id=coin_info.get('id', ''),
                            symbol=coin_info.get('symbol', '').upper(),
                            name=coin_info.get('name', ''),
                            current_price=coin_info.get('current_price'),
                            market_cap=coin_info.get('market_cap'),
                            market_cap_rank=coin_info.get('market_cap_rank'),
                            fully_diluted_valuation=coin_info.get('fully_diluted_valuation'),
                            total_volume=coin_info.get('total_volume'),
                            high_24h=coin_info.get('high_24h'),
                            low_24h=coin_info.get('low_24h'),
                            price_change_24h=coin_info.get('price_change_24h'),
                            price_change_percentage_24h=coin_info.get('price_change_percentage_24h'),
                            market_cap_change_24h=coin_info.get('market_cap_change_24h'),
                            market_cap_change_percentage_24h=coin_info.get('market_cap_change_percentage_24h'),
                            circulating_supply=coin_info.get('circulating_supply'),
                            total_supply=coin_info.get('total_supply'),
                            max_supply=coin_info.get('max_supply'),
                            ath=coin_info.get('ath'),
                            ath_change_percentage=coin_info.get('ath_change_percentage'),
                            ath_date=coin_info.get('ath_date'),
                            atl=coin_info.get('atl'),
                            atl_change_percentage=coin_info.get('atl_change_percentage'),
                            atl_date=coin_info.get('atl_date'),
                            last_updated=coin_info.get('last_updated'),
                            image=coin_info.get('image')
                        )
                        coins_data.append(coin_data)
                    
                    logger.info(f"✅ {len(coins_data)} crypto-monnaies récupérées")
                    return coins_data
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def get_price_history(self, 
                              coin_id: str,
                              vs_currency: str = "usd",
                              days: int = 7) -> Optional[PriceHistory]:
        """Obtenir l'historique des prix"""
        
        logger.info(f"💰 Récupération historique {coin_id} sur {days} jours")
        
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': vs_currency,
                'days': days,
                'interval': 'daily' if days > 1 else 'hourly'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    history = PriceHistory(
                        coin_id=coin_id,
                        prices=data.get('prices', []),
                        market_caps=data.get('market_caps', []),
                        total_volumes=data.get('total_volumes', []),
                        period=f"{days}d",
                        currency=vs_currency
                    )
                    
                    logger.info(f"✅ Historique récupéré: {len(history.prices)} points")
                    return history
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def search_coins(self, query: str) -> Optional[Dict[str, Any]]:
        """Rechercher des crypto-monnaies"""
        
        logger.info(f"💰 Recherche crypto: '{query}'")
        
        try:
            url = f"{self.base_url}/search"
            params = {'query': query}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    coins = data.get('coins', [])
                    logger.info(f"✅ Recherche: {len(coins)} résultats")
                    return data
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de recherche: {e}")
            return None

    async def get_exchange_rates(self) -> Optional[Dict[str, ExchangeRate]]:
        """Obtenir les taux de change"""
        
        logger.info("💰 Récupération taux de change")
        
        try:
            url = f"{self.base_url}/exchange_rates"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    rates = {}
                    rates_data = data.get('rates', {})
                    
                    for currency, rate_info in rates_data.items():
                        rate = ExchangeRate(
                            from_currency="btc",
                            to_currency=currency,
                            rate=rate_info.get('value', 0),
                            timestamp=datetime.now().isoformat()
                        )
                        rates[currency] = rate
                    
                    logger.info(f"✅ {len(rates)} taux de change récupérés")
                    return rates
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    async def get_trending_coins(self) -> Optional[Dict[str, Any]]:
        """Obtenir les crypto-monnaies tendance"""
        
        logger.info("💰 Récupération crypto tendance")
        
        try:
            url = f"{self.base_url}/search/trending"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    trending = data.get('coins', [])
                    logger.info(f"✅ {len(trending)} crypto tendance")
                    return data
                    
                elif response.status == 429:
                    logger.warning("⚠️ Limite de taux atteinte")
                    return None
                else:
                    logger.error(f"❌ Erreur API: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur de récupération: {e}")
            return None

    def get_supported_currencies(self) -> List[str]:
        """Obtenir les devises supportées"""
        return self.supported_currencies

    def get_service_info(self) -> Dict[str, Any]:
        """Informations sur le service CoinGecko"""
        return {
            'service': 'CoinGecko API',
            'base_url': self.base_url,
            'features': [
                'Cryptocurrency market data',
                'Price history and charts',
                'Market cap rankings',
                'Exchange rates',
                'Trending coins',
                'Search functionality',
                'Free tier available'
            ],
            'supported_currencies': len(self.supported_currencies),
            'has_api_key': self.api_key is not None,
            'rate_limits': self.rate_limits,
            'free_tier_limits': {
                'calls_per_minute': 30,
                'monthly_calls': 10000,
                'max_coins_per_request': 250
            }
        }

# Fonctions utilitaires
async def test_coingecko_integration():
    """Tester l'intégration CoinGecko"""
    try:
        async with CoinGeckoAPI() as crypto_api:
            # Test 1: Données de marché top 10
            print("💰 Test données de marché top 10...")
            market_data = await crypto_api.get_market_data(per_page=10)
            
            if market_data:
                print(f"✅ {len(market_data)} crypto-monnaies récupérées")
                for coin in market_data[:3]:
                    print(f"   {coin.name} ({coin.symbol}): ${coin.current_price}")
                    print(f"      Cap: ${coin.market_cap:,.0f} | Rang: {coin.market_cap_rank}")
            
            # Test 2: Données spécifiques Bitcoin
            print("\n💰 Test données Bitcoin...")
            btc_data = await crypto_api.get_coin_data("bitcoin")
            
            if btc_data:
                print(f"✅ {btc_data.name} récupéré")
                print(f"   Prix: ${btc_data.current_price}")
                print(f"   24h: {btc_data.price_change_percentage_24h:.2f}%")
                print(f"   ATH: ${btc_data.ath}")
            
            # Test 3: Recherche crypto
            print("\n🔍 Test recherche crypto...")
            search_results = await crypto_api.search_coins("ethereum")
            
            if search_results:
                coins = search_results.get('coins', [])
                print(f"✅ Recherche 'ethereum': {len(coins)} résultats")
                if coins:
                    print(f"   Premier: {coins[0].get('name')} ({coins[0].get('symbol')})")
            
            # Test 4: Crypto tendance
            print("\n🔥 Test crypto tendance...")
            trending = await crypto_api.get_trending_coins()
            
            if trending:
                trending_coins = trending.get('coins', [])
                print(f"✅ {len(trending_coins)} crypto tendance")
                for coin in trending_coins[:3]:
                    coin_info = coin.get('item', {})
                    print(f"   {coin_info.get('name')} ({coin_info.get('symbol')})")
            
            # Test 5: Historique prix
            print("\n📈 Test historique prix...")
            history = await crypto_api.get_price_history("bitcoin", days=7)
            
            if history:
                print(f"✅ Historique Bitcoin: {len(history.prices)} points")
                if history.prices:
                    latest_price = history.prices[-1][1]
                    print(f"   Dernier prix: ${latest_price}")
            
            # Test 6: Taux de change
            print("\n💱 Test taux de change...")
            rates = await crypto_api.get_exchange_rates()
            
            if rates:
                print(f"✅ {len(rates)} taux de change")
                if 'usd' in rates:
                    print(f"   BTC/USD: {rates['usd'].rate}")
                if 'eur' in rates:
                    print(f"   BTC/EUR: {rates['eur'].rate}")
            
            # Test 7: Devises supportées
            print("\n💰 Devises supportées...")
            currencies = crypto_api.get_supported_currencies()
            print(f"✅ {len(currencies)} devises supportées")
            print(f"   Principales: {currencies[:10]}")
            
            # Test 8: Informations service
            print("\n📊 Informations service...")
            service_info = crypto_api.get_service_info()
            print(f"✅ Service: {service_info['service']}")
            print(f"💰 Devises: {service_info['supported_currencies']}")
            print(f"⏱️ Limite gratuite: {service_info['free_tier_limits']['calls_per_minute']}/min")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de test CoinGecko: {e}")
        return False

if __name__ == "__main__":
    # Test de l'intégration CoinGecko
    result = asyncio.run(test_coingecko_integration())
    sys.exit(0 if result else 1)