"""
Data Adapter Service - Handles interactions with external data sources
"""

import requests
from typing import Dict, Any, List, TYPE_CHECKING
import os
import logging
import json
from datetime import datetime
from .test_eagle_api_responses import TestEagleAPIResponses
from .mock_eagle_api import MockEagleAPI

if TYPE_CHECKING:
    from services.metric_selector import MetricSelector

class DataAdapter:
    """Adapter for handling data source interactions"""
    
    def __init__(self):
        self.eagle_url = "https://eagle-gamma.capgroup.com/svc-backend/graphql"
        self.token = os.getenv('EAGLE_API_TOKEN')
        self.test_api = TestEagleAPIResponses()
        self.mock_api = MockEagleAPI()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        if not self.token:
            logging.info("EAGLE_API_TOKEN not configured, using mock Eagle API for frontend testing")
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a GraphQL query and return results"""
        if not self.token:
            logging.info("EAGLE_API_TOKEN not configured, using mock data for testing")
            # Return mock data when authentication not available
            return self.test_api.get_test_response_for_company()['test_response']
            
        try:
            response = requests.post(
                self.eagle_url,
                headers=self.headers,
                json={'query': query},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check for API errors
                if 'errors' in result:
                    logging.error(f"API errors: {result['errors']}")
                    return {'error': 'API returned errors', 'details': result['errors']}
                
                # Process results
                if 'data' in result and 'financialMetrics' in result['data']:
                    metrics_data = result['data']['financialMetrics']
                    metrics_values = {}
                    
                    # Extract metric values
                    if metrics_data and len(metrics_data) > 0 and metrics_data[0].get('metrics'):
                        for metric in metrics_data[0]['metrics']:
                            if metric.get('value') is not None:
                                metrics_values[metric['name']] = metric['value']
                    
                    return {
                        'success': True,
                        'metrics': metrics_values,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                else:
                    return {'error': 'No financial metrics data found in response'}
                
            else:
                logging.error(f"HTTP Error {response.status_code}: {response.text}")
                return {'error': f'HTTP {response.status_code}', 'details': response.text}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Request Error: {str(e)}")
            return {'error': 'Network request failed', 'details': str(e)}
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return {'error': 'Unexpected error', 'details': str(e)}
    
    def fetch_metric_values(self, metrics: List[str], company_ticker: str = "NVDA") -> Dict[str, Any]:
        """Fetch values for specific metrics using ticker symbol"""
        if not metrics:
            return {'error': 'No metrics specified'}
            
        # Format metric names for GraphQL query
        metrics_str = ','.join([f'{{name: "{m}"}}' for m in metrics])
        
        query = f"""
        query {{
            financialMetrics(
                entityIds: [
                    {{id: "{company_ticker}", type: TICKER}}
                ],
                metricIds: [{metrics_str}]
            ) {{
                metrics {{
                    name
                    value
                    category
                }}
            }}
        }}
        """
        
        return self.execute_query(query)
    
    def get_eagle_metrics(self, sedol_id: str, metrics: List[str]) -> Dict[str, Any]:
        """Fetch Eagle API metrics using SEDOL ID and metric list"""
        if not metrics or not sedol_id:
            return {'success': False, 'error': 'Missing sedol_id or metrics'}
            
        # Format metric names for GraphQL query
        metrics_str = ','.join([f'"{m}"' for m in metrics])
        
        query = f"""
        query {{
            financialMetrics(
                entityIds: [
                    {{id: "{sedol_id}", type: SEDOL}}
                ],
                metricIds: [{metrics_str}]
            ) {{
                companyInfo {{
                    name
                    sedolId
                    currency
                }}
                metrics {{
                    name
                    value
                    category
                    unit
                    period
                }}
            }}
        }}
        """
        
        result = self.execute_query(query)
        
        if result and 'data' in result:
            return {
                'success': True,
                'data': result['data'],
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {'success': False, 'error': 'No data returned from Eagle API'}

    def fetch_metric_values_with_sedol(self, metrics: List[str], company_ticker: str, sedol_id: str) -> Dict[str, Any]:
        """Fetch values for specific metrics using both ticker and SEDOL ID"""
        if not metrics:
            return {'error': 'No metrics specified'}
            
        # Format metric names for GraphQL query
        metrics_str = ','.join([f'{{name: "{m}"}}' for m in metrics])
        
        query = f"""
        query {{
            financialMetrics(
                entityIds: [
                    {{id: "{sedol_id}", type: SEDOL}},
                    {{id: "{company_ticker}", type: TICKER}}
                ],
                metricIds: [{metrics_str}]
            ) {{
                metrics {{
                    name
                    value
                    category
                }}
            }}
        }}
        """
        
        return self.execute_query(query)
    
    def get_test_eagle_response(self, company_ticker: str = None, sedol_id: str = None) -> Dict[str, Any]:
        """Get test response matching Eagle API schema for frontend validation"""
        return self.test_api.get_test_response_for_company(ticker=company_ticker, sedol_id=sedol_id)
    
    def fetch_company_metrics(self, company_ticker: str, metric_categories: List[str] = None, sedol_id: str = "") -> Dict[str, Any]:
        """Fetch comprehensive metrics for a company using ticker and optional SEDOL ID"""
        from services.metric_selector import MetricSelector
        
        selector = MetricSelector()
        
        if metric_categories:
            # Get metrics for specific categories
            all_metrics = []
            for category in metric_categories:
                category_metrics = selector.get_metrics_by_category(category)
                if category_metrics and 'metrics' in category_metrics:
                    category_metric_names = []
                    selector._extract_primary_metric_names(category_metrics['metrics'], category_metric_names)
                    all_metrics.extend(category_metric_names)
        else:
            # Get comprehensive metrics for thesis analysis
            comprehensive = selector.get_comprehensive_metrics_for_thesis()
            all_metrics = []
            for category_metrics in comprehensive.values():
                all_metrics.extend(category_metrics)
        
        # Remove duplicates
        unique_metrics = list(set(all_metrics))
        
        # Use mock Eagle API for realistic testing when token not available
        if not self.token:
            return self.mock_api.get_company_metrics(company_ticker, metric_categories or [], sedol_id)
        
        # Fetch the metrics using both ticker and SEDOL if available
        if sedol_id:
            result = self.fetch_metric_values_with_sedol(unique_metrics, company_ticker, sedol_id)
        else:
            result = self.fetch_metric_values(unique_metrics, company_ticker)
        
        # Process Eagle API response (either real or test data)
        if result and 'data' in result and 'financialMetrics' in result['data']:
            # Extract metrics from Eagle API response structure
            financial_metrics = result['data']['financialMetrics']
            if financial_metrics and len(financial_metrics) > 0:
                metrics_data = financial_metrics[0].get('metrics', [])
                
                # Convert to expected format
                processed_metrics = {}
                for metric in metrics_data[:5]:  # Limit to first 5 metrics
                    metric_name = metric.get('name', 'unknown_metric')
                    processed_metrics[metric_name] = {
                        'value': metric.get('value'),
                        'category': metric.get('category', 'financial')
                    }
                
                result = {
                    'success': True,
                    'metrics': processed_metrics,
                    'company_ticker': company_ticker,
                    'sedol_id': sedol_id
                }
            else:
                result = {'success': False, 'error': 'No metrics found in response'}
        elif result and result.get('success'):
            # Handle already processed format
            result['company_ticker'] = company_ticker
            result['sedol_id'] = sedol_id
        
        return result
    
    def _organize_metrics_by_category(self, metrics: Dict[str, Any], selector: 'MetricSelector') -> Dict[str, Dict[str, Any]]:
        """Organize metrics by their categories"""
        organized = {
            'growth_metrics': {},
            'valuation_metrics': {},
            'profitability_metrics': {},
            'risk_metrics': {},
            'market_metrics': {}
        }
        
        # Map each metric to its category
        for category in organized.keys():
            category_data = selector.get_metrics_by_category(category.replace('_metrics', '_metrics'))
            if category_data and 'metrics' in category_data:
                category_metric_names = []
                selector._extract_primary_metric_names(category_data['metrics'], category_metric_names)
                
                for metric_name in category_metric_names:
                    if metric_name in metrics:
                        organized[category][metric_name] = metrics[metric_name]
        
        return organized
    
    def fetch_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """Fetch metadata for a document"""
        # This would typically interact with a document management system
        # For now, return structured metadata format
        return {
            'id': document_id,
            'type': 'financial_report',
            'date': datetime.utcnow().isoformat(),
            'status': 'active',
            'source': 'internal_data_source'
        }
    
    def validate_connection(self) -> bool:
        """Validate connection to data source"""
        test_query = """
        query {
            __schema {
                types {
                    name
                }
            }
        }
        """
        
        try:
            result = self.execute_query(test_query)
            return result.get('success', False) and 'error' not in result
        except Exception as e:
            logging.warning(f"Eagle API connection validation failed: {str(e)}")
            return False