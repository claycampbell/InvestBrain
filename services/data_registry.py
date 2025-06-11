import os
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from config import Config

class DataRegistry:
    """
    Central registry for managing data sources and preferences
    Prioritizes FactSet/Xpressfeed as specified in requirements
    """
    
    def __init__(self):
        self.data_sources = {
            'factset': {
                'name': 'FactSet',
                'priority': 1,
                'api_key': Config.FACTSET_API_KEY,
                'base_url': 'https://api.factset.com/v1/',
                'enabled': bool(Config.FACTSET_API_KEY)
            },
            'xpressfeed': {
                'name': 'Xpressfeed',
                'priority': 2,
                'api_key': Config.XPRESSFEED_API_KEY,
                'base_url': 'https://api.xpressfeed.com/v1/',
                'enabled': bool(Config.XPRESSFEED_API_KEY)
            },
            'fallback': {
                'name': 'Fallback Data',
                'priority': 99,
                'enabled': True
            }
        }
        
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)
    
    def get_asset_data(self, symbol: str, data_type: str = 'price') -> Dict[str, Any]:
        """
        Retrieve asset data from the highest priority available source
        """
        cache_key = f"{symbol}_{data_type}"
        
        # Check cache first
        if self._is_cached(cache_key):
            logging.debug(f"Returning cached data for {cache_key}")
            return self.cache[cache_key]['data']
        
        # Try data sources in priority order
        for source_id, source_config in sorted(self.data_sources.items(), 
                                             key=lambda x: x[1]['priority']):
            if not source_config['enabled']:
                continue
            
            try:
                data = self._fetch_from_source(source_id, symbol, data_type)
                if data:
                    # Cache the result
                    self._cache_data(cache_key, data)
                    logging.info(f"Retrieved {data_type} data for {symbol} from {source_config['name']}")
                    return data
            except Exception as e:
                logging.warning(f"Failed to fetch from {source_config['name']}: {str(e)}")
                continue
        
        # If all sources fail, return empty state
        logging.error(f"Failed to retrieve data for {symbol} from all sources")
        return self._get_empty_state(symbol, data_type)
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve market data for multiple symbols
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_asset_data(symbol, 'market_data')
        return results
    
    def get_price_history(self, symbol: str, period: str = '1y') -> Dict[str, Any]:
        """
        Get historical price data for a symbol
        """
        cache_key = f"{symbol}_history_{period}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        # Try sources in priority order
        for source_id, source_config in sorted(self.data_sources.items(), 
                                             key=lambda x: x[1]['priority']):
            if not source_config['enabled']:
                continue
            
            try:
                data = self._fetch_price_history(source_id, symbol, period)
                if data:
                    self._cache_data(cache_key, data)
                    return data
            except Exception as e:
                logging.warning(f"Failed to fetch price history from {source_config['name']}: {str(e)}")
                continue
        
        return self._get_empty_price_history(symbol, period)
    
    def _fetch_from_source(self, source_id: str, symbol: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from a specific source
        """
        if source_id == 'factset':
            return self._fetch_from_factset(symbol, data_type)
        elif source_id == 'xpressfeed':
            return self._fetch_from_xpressfeed(symbol, data_type)
        elif source_id == 'fallback':
            return self._get_fallback_data(symbol, data_type)
        else:
            return None
    
    def _fetch_from_factset(self, symbol: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from FactSet API
        """
        if not self.data_sources['factset']['enabled']:
            return None
        
        try:
            headers = {
                'Authorization': f"Bearer {self.data_sources['factset']['api_key']}",
                'Content-Type': 'application/json'
            }
            
            if data_type == 'price':
                endpoint = f"{self.data_sources['factset']['base_url']}prices"
                params = {'ids': symbol}
            elif data_type == 'market_data':
                endpoint = f"{self.data_sources['factset']['base_url']}market-data"
                params = {'ids': symbol}
            else:
                return None
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_factset_data(data, symbol, data_type)
            else:
                logging.error(f"FactSet API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching from FactSet: {str(e)}")
            return None
    
    def _fetch_from_xpressfeed(self, symbol: str, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from Xpressfeed API
        """
        if not self.data_sources['xpressfeed']['enabled']:
            return None
        
        try:
            headers = {
                'X-API-Key': self.data_sources['xpressfeed']['api_key'],
                'Content-Type': 'application/json'
            }
            
            if data_type == 'price':
                endpoint = f"{self.data_sources['xpressfeed']['base_url']}quote"
                params = {'symbol': symbol}
            elif data_type == 'market_data':
                endpoint = f"{self.data_sources['xpressfeed']['base_url']}market"
                params = {'symbol': symbol}
            else:
                return None
            
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._normalize_xpressfeed_data(data, symbol, data_type)
            else:
                logging.error(f"Xpressfeed API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error fetching from Xpressfeed: {str(e)}")
            return None
    
    def _fetch_price_history(self, source_id: str, symbol: str, period: str) -> Optional[Dict[str, Any]]:
        """
        Fetch historical price data from a specific source
        """
        if source_id == 'factset':
            return self._fetch_factset_history(symbol, period)
        elif source_id == 'xpressfeed':
            return self._fetch_xpressfeed_history(symbol, period)
        elif source_id == 'fallback':
            return self._get_fallback_history(symbol, period)
        else:
            return None
    
    def _normalize_factset_data(self, data: Dict, symbol: str, data_type: str) -> Dict[str, Any]:
        """
        Normalize FactSet API response to standard format
        """
        try:
            # This is a placeholder - actual implementation would depend on FactSet API structure
            if data_type == 'price':
                return {
                    'symbol': symbol,
                    'price': data.get('price', 0.0),
                    'change': data.get('change', 0.0),
                    'change_percent': data.get('changePercent', 0.0),
                    'volume': data.get('volume', 0),
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'FactSet'
                }
            elif data_type == 'market_data':
                return {
                    'symbol': symbol,
                    'price': data.get('price', 0.0),
                    'open': data.get('open', 0.0),
                    'high': data.get('high', 0.0),
                    'low': data.get('low', 0.0),
                    'volume': data.get('volume', 0),
                    'market_cap': data.get('marketCap', 0),
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'FactSet'
                }
        except Exception as e:
            logging.error(f"Error normalizing FactSet data: {str(e)}")
            return None
    
    def _normalize_xpressfeed_data(self, data: Dict, symbol: str, data_type: str) -> Dict[str, Any]:
        """
        Normalize Xpressfeed API response to standard format
        """
        try:
            # This is a placeholder - actual implementation would depend on Xpressfeed API structure
            if data_type == 'price':
                return {
                    'symbol': symbol,
                    'price': data.get('last', 0.0),
                    'change': data.get('change', 0.0),
                    'change_percent': data.get('changePercent', 0.0),
                    'volume': data.get('volume', 0),
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'Xpressfeed'
                }
            elif data_type == 'market_data':
                return {
                    'symbol': symbol,
                    'price': data.get('last', 0.0),
                    'open': data.get('open', 0.0),
                    'high': data.get('high', 0.0),
                    'low': data.get('low', 0.0),
                    'volume': data.get('volume', 0),
                    'timestamp': datetime.utcnow().isoformat(),
                    'source': 'Xpressfeed'
                }
        except Exception as e:
            logging.error(f"Error normalizing Xpressfeed data: {str(e)}")
            return None
    
    def _get_fallback_data(self, symbol: str, data_type: str) -> Dict[str, Any]:
        """
        Provide fallback data structure when external APIs are unavailable
        """
        return {
            'symbol': symbol,
            'price': None,
            'change': None,
            'change_percent': None,
            'volume': None,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'Unavailable',
            'error': 'External data sources unavailable'
        }
    
    def _get_empty_state(self, symbol: str, data_type: str) -> Dict[str, Any]:
        """
        Return explicit empty state when data cannot be retrieved
        """
        return {
            'symbol': symbol,
            'data_type': data_type,
            'status': 'unavailable',
            'error': 'No data available from configured sources',
            'timestamp': datetime.utcnow().isoformat(),
            'available_sources': [name for name, config in self.data_sources.items() if config['enabled']]
        }
    
    def _get_empty_price_history(self, symbol: str, period: str) -> Dict[str, Any]:
        """
        Return explicit empty state for price history
        """
        return {
            'symbol': symbol,
            'period': period,
            'status': 'unavailable',
            'error': 'Historical data not available from configured sources',
            'timestamp': datetime.utcnow().isoformat(),
            'data': []
        }
    
    def _is_cached(self, cache_key: str) -> bool:
        """
        Check if data is cached and still valid
        """
        if cache_key not in self.cache:
            return False
        
        cache_entry = self.cache[cache_key]
        return datetime.utcnow() - cache_entry['timestamp'] < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Cache data with timestamp
        """
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
    
    def get_data_source_status(self) -> Dict[str, Any]:
        """
        Get status of all configured data sources
        """
        status = {}
        for source_id, config in self.data_sources.items():
            status[source_id] = {
                'name': config['name'],
                'enabled': config['enabled'],
                'priority': config['priority'],
                'has_api_key': bool(config.get('api_key'))
            }
        return status
    
    def clear_cache(self) -> None:
        """
        Clear all cached data
        """
        self.cache.clear()
        logging.info("Data registry cache cleared")
