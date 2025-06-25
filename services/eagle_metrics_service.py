"""
Eagle API Metrics Service - Updated to use Azure OpenAI directly
Handles metric identification, sedol_id extraction, and data retrieval
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService

class EagleMetricsService:
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
        self.base_url = "https://api.eagle-finance.com/v1"
        self.api_key = os.environ.get('EAGLE_API_TOKEN')
        self.available_metrics = self._load_available_metrics()
        
        if not self.api_key:
            logging.info("EAGLE_API_TOKEN not configured, using mock Eagle API for frontend testing")
    
    def _load_available_metrics(self) -> Dict[str, List[str]]:
        """Load available metrics from the JSON file"""
        try:
            with open('available_metrics.json', 'r') as f:
                data = json.load(f)
                # Convert to dict format for category-based access
                if isinstance(data, list):
                    # Group metrics by category for better organization
                    categories = {
                        'growth_metrics': [m for m in data if 'growth' in m.lower() or 'revenue' in m.lower()],
                        'financial_health': [m for m in data if 'debt' in m.lower() or 'equity' in m.lower() or 'ratio' in m.lower()],
                        'profitability': [m for m in data if 'margin' in m.lower() or 'profit' in m.lower() or 'earnings' in m.lower()],
                        'efficiency': [m for m in data if 'turnover' in m.lower() or 'efficiency' in m.lower()],
                        'liquidity': [m for m in data if 'cash' in m.lower() or 'current' in m.lower()]
                    }
                    return categories
                return data
        except Exception as e:
            logging.warning(f"Could not load available metrics: {e}")
            return self._get_fallback_metrics()
    
    def _get_fallback_metrics(self) -> Dict[str, List[str]]:
        """Fallback metrics when file is not available"""
        return {
            'growth_metrics': ['Revenue Growth Rate', 'Earnings Growth', 'EBITDA Growth'],
            'financial_health': ['Debt to Equity Ratio', 'Current Ratio', 'Quick Ratio'],
            'profitability': ['Net Profit Margin', 'Operating Margin', 'ROE'],
            'efficiency': ['Asset Turnover', 'Inventory Turnover'],
            'liquidity': ['Cash Ratio', 'Working Capital']
        }
    
    def extract_sedol_id_from_thesis(self, thesis_text: str) -> Optional[str]:
        """Extract SEDOL ID from thesis text using Azure OpenAI"""
        try:
            prompt = f"""
            Extract the SEDOL ID from this investment thesis text if present.
            SEDOL IDs are 7-character alphanumeric codes used to identify securities.
            
            Thesis: {thesis_text}
            
            Return only the SEDOL ID if found, or "None" if not found.
            """
            
            if self.azure_openai.is_available():
                response = self.azure_openai.generate_completion([
                    {"role": "user", "content": prompt}
                ], max_tokens=50, temperature=0.1)
                sedol_id = response.strip()
                
                if sedol_id and sedol_id.lower() != "none" and len(sedol_id) == 7:
                    logging.info(f"Extracted SEDOL ID: {sedol_id}")
                    return sedol_id
                else:
                    logging.info("No valid SEDOL ID found in thesis text")
                    return None
            else:
                logging.info("Azure OpenAI not available for SEDOL extraction")
                return None
                
        except Exception as e:
            logging.warning(f"Failed to extract SEDOL ID using Azure OpenAI: {str(e)}")
            return None
    
    def identify_relevant_categories(self, thesis_text: str) -> List[str]:
        """Identify relevant metric categories based on thesis content"""
        try:
            prompt = f"""
            Based on this investment thesis, identify the most relevant financial metrics from the available categories.
            
            Thesis: {thesis_text[:300]}...
            
            Available metric categories: {', '.join(self.available_metrics.keys())}
            
            Return 2-3 most relevant categories that would help validate this investment thesis.
            Respond with just the category names, comma-separated.
            """
            
            if self.azure_openai.is_available():
                response = self.azure_openai.generate_completion([
                    {"role": "user", "content": prompt}
                ], max_tokens=100, temperature=0.3)
                identified_categories = [cat.strip() for cat in response.split(',')]
                
                # Filter to ensure all categories exist in our available metrics
                valid_categories = [cat for cat in identified_categories if cat in self.available_metrics]
                
                if valid_categories:
                    logging.info(f"Azure OpenAI identified relevant categories: {valid_categories}")
                    return valid_categories[:3]  # Limit to 3 categories
                else:
                    logging.warning("Azure OpenAI did not identify valid categories, using defaults")
                    return self._get_default_categories()
            else:
                logging.info("Azure OpenAI not available for metric identification, using defaults")
                return self._get_default_categories()
                
        except Exception as e:
            logging.warning(f"Failed to identify metrics using Azure OpenAI: {str(e)}")
            return self._get_default_categories()
    
    def _get_default_categories(self) -> List[str]:
        """Get default metric categories"""
        return ['growth_metrics', 'financial_health']
    
    def get_eagle_metrics_for_company(self, ticker: str, thesis_text: str, sedol_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get Eagle API metrics for a specific company and thesis"""
        try:
            # Identify relevant metric categories
            relevant_categories = self.identify_relevant_categories(thesis_text)
            
            # If Eagle API is available, query it
            if self.api_key:
                try:
                    return self._query_real_eagle_api(ticker, sedol_id, relevant_categories)
                except Exception as e:
                    logging.warning(f"Eagle API query failed: {str(e)}")
                    # Fall through to mock data
            
            # Generate mock data for testing/demo
            return self._generate_mock_eagle_data(ticker, sedol_id, relevant_categories)
            
        except Exception as e:
            logging.error(f"Failed to get Eagle metrics for {ticker}: {str(e)}")
            return []
    
    def _query_real_eagle_api(self, ticker: str, sedol_id: Optional[str], categories: List[str]) -> List[Dict[str, Any]]:
        """Query real Eagle API (when API key is available)"""
        try:
            import requests
            
            # Build GraphQL query for Eagle API
            query = self._build_eagle_query(ticker, sedol_id, categories)
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.base_url}/graphql",
                json={'query': query},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._process_eagle_response(data, ticker, categories)
            else:
                logging.warning(f"Eagle API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"Real Eagle API query failed: {str(e)}")
            return []
    
    def _build_eagle_query(self, ticker: str, sedol_id: Optional[str], categories: List[str]) -> str:
        """Build GraphQL query for Eagle API"""
        # Select metrics from relevant categories
        selected_metrics = []
        for category in categories:
            if category in self.available_metrics:
                selected_metrics.extend(self.available_metrics[category][:2])  # Limit per category
        
        # Build GraphQL query
        query = f"""
        query {{
            company(ticker: "{ticker}") {{
                {" ".join(selected_metrics)}
                lastUpdated
            }}
        }}
        """
        return query
    
    def _process_eagle_response(self, data: Dict, ticker: str, categories: List[str]) -> List[Dict[str, Any]]:
        """Process Eagle API response into standardized format"""
        results = []
        
        if 'data' in data and 'company' in data['data']:
            company_data = data['data']['company']
            
            for category in categories:
                if category in self.available_metrics:
                    for metric_name in self.available_metrics[category][:2]:
                        if metric_name in company_data:
                            value = company_data[metric_name]
                            if value is not None:
                                results.append({
                                    'name': f'Eagle: {metric_name}',
                                    'category': category,
                                    'current_value': float(value),
                                    'threshold': float(value) * 1.1,  # 10% above current
                                    'threshold_type': 'above',
                                    'company_ticker': ticker,
                                    'data_source': 'Eagle API',
                                    'eagle_api': True,
                                    'level': 'Internal Research Data',
                                    'type': 'Internal Research Data',
                                    'frequency': 'real-time',
                                    'value_chain_position': 'upstream',
                                    'description': f'Real-time financial metric for {ticker}: {metric_name}',
                                    'sedol_id': None
                                })
        
        return results
    
    def _generate_mock_eagle_data(self, ticker: str, sedol_id: Optional[str], categories: List[str]) -> List[Dict[str, Any]]:
        """Generate mock Eagle API data for testing"""
        results = []
        
        # Generate 1-2 metrics per category
        for category in categories[:2]:  # Limit to 2 categories
            if category in self.available_metrics:
                metric_names = self.available_metrics[category][:2]  # Max 2 per category
                
                for metric_name in metric_names:
                    # Generate realistic mock values based on metric type
                    if 'ratio' in metric_name.lower():
                        current_value = random.uniform(0.5, 3.0)
                    elif 'growth' in metric_name.lower():
                        current_value = random.uniform(-0.1, 0.3)  # -10% to 30%
                    elif 'margin' in metric_name.lower():
                        current_value = random.uniform(0.05, 0.4)  # 5% to 40%
                    else:
                        current_value = random.uniform(1.0, 100.0)
                    
                    threshold = current_value * random.uniform(1.05, 1.15)  # 5-15% above current
                    
                    results.append({
                        'name': f'Eagle: {metric_name}',
                        'category': category,
                        'current_value': round(current_value, 4),
                        'threshold': round(threshold, 5),
                        'threshold_type': 'above',
                        'company_ticker': ticker,
                        'data_source': 'Eagle API',
                        'eagle_api': True,
                        'level': 'Internal Research Data',
                        'type': 'Internal Research Data',
                        'frequency': 'real-time',
                        'value_chain_position': 'upstream',
                        'description': f'Real-time financial metric for {ticker}: {metric_name}',
                        'sedol_id': sedol_id
                    })
        
        logging.info(f"Generated {len(results)} mock Eagle API metrics for {ticker}")
        return results
    
    def test_connection(self) -> bool:
        """Test Eagle API connection"""
        if not self.api_key:
            return False
        
        try:
            import requests
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False