"""
Mock Eagle API Service
Provides realistic financial data in authentic Eagle API format for frontend testing
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

class MockEagleAPI:
    """Mock Eagle API that returns realistic financial data in proper format"""
    
    def __init__(self):
        self.company_data = {
            'NVDA': {
                'name': 'NVIDIA Corporation',
                'sedol': '2379504',
                'sector': 'Technology',
                'industry': 'Semiconductors',
                'base_metrics': {
                    'Revenue Growth Rate': 0.126,
                    'Operating Margin': 0.321,
                    'Free Cash Flow': 26.04,
                    'Return on Equity': 0.873,
                    'Debt to Equity Ratio': 0.247,
                    'Current Ratio': 3.51,
                    'Price to Earnings Ratio': 65.3,
                    'Enterprise Value to Revenue': 24.1,
                    'Gross Margin': 0.732,
                    'R&D Expense Ratio': 0.201
                }
            },
            'AAPL': {
                'name': 'Apple Inc.',
                'sedol': '2046251',
                'sector': 'Technology',
                'industry': 'Consumer Electronics',
                'base_metrics': {
                    'Revenue Growth Rate': 0.033,
                    'Operating Margin': 0.298,
                    'Free Cash Flow': 93.21,
                    'Return on Equity': 1.474,
                    'Debt to Equity Ratio': 1.822,
                    'Current Ratio': 1.07,
                    'Price to Earnings Ratio': 31.2,
                    'Enterprise Value to Revenue': 7.8,
                    'Gross Margin': 0.451,
                    'Net Profit Margin': 0.241
                }
            },
            'MSFT': {
                'name': 'Microsoft Corporation',
                'sedol': '2588173',
                'sector': 'Technology',
                'industry': 'Software',
                'base_metrics': {
                    'Revenue Growth Rate': 0.152,
                    'Operating Margin': 0.424,
                    'Free Cash Flow': 56.12,
                    'Return on Equity': 0.389,
                    'Debt to Equity Ratio': 0.312,
                    'Current Ratio': 1.98,
                    'Price to Earnings Ratio': 36.4,
                    'Enterprise Value to Revenue': 12.3,
                    'Gross Margin': 0.693,
                    'Cloud Revenue Growth': 0.298
                }
            },
            'TSLA': {
                'name': 'Tesla Inc.',
                'sedol': 'B616C79',
                'sector': 'Consumer Discretionary',
                'industry': 'Automobiles',
                'base_metrics': {
                    'Revenue Growth Rate': 0.374,
                    'Operating Margin': 0.084,
                    'Free Cash Flow': 7.53,
                    'Return on Equity': 0.284,
                    'Debt to Equity Ratio': 0.073,
                    'Current Ratio': 1.69,
                    'Price to Earnings Ratio': 62.1,
                    'Enterprise Value to Revenue': 8.2,
                    'Gross Margin': 0.208,
                    'Vehicle Delivery Growth': 0.351
                }
            },
            'JPM': {
                'name': 'JPMorgan Chase & Co.',
                'sedol': '2190165',
                'sector': 'Financials',
                'industry': 'Banks',
                'base_metrics': {
                    'Revenue Growth Rate': 0.089,
                    'Return on Equity': 0.154,
                    'Net Interest Margin': 0.024,
                    'Tier 1 Capital Ratio': 0.159,
                    'Loan Loss Provision Ratio': 0.021,
                    'Efficiency Ratio': 0.571,
                    'Price to Book Ratio': 1.82,
                    'Dividend Yield': 0.024,
                    'Trading Revenue Growth': 0.142,
                    'Investment Banking Revenue': 0.067
                }
            }
        }
    
    def get_company_metrics(self, ticker: str, categories: List[str] = None, sedol_id: str = None) -> Dict[str, Any]:
        """Get financial metrics for a company in Eagle API format"""
        
        # Get company data or use default
        company_info = self.company_data.get(ticker.upper(), {
            'name': f'{ticker.upper()} Corporation',
            'sedol': sedol_id or 'UNKNOWN',
            'sector': 'Unknown',
            'industry': 'Unknown',
            'base_metrics': {
                'Revenue Growth Rate': random.uniform(0.02, 0.25),
                'Operating Margin': random.uniform(0.05, 0.35),
                'Free Cash Flow': random.uniform(1.0, 50.0),
                'Return on Equity': random.uniform(0.08, 0.25),
                'Debt to Equity Ratio': random.uniform(0.1, 2.0)
            }
        })
        
        # Add realistic time-based variation
        variation_factor = 1 + random.uniform(-0.05, 0.05)  # ±5% variation
        
        metrics = {}
        base_metrics = company_info['base_metrics']
        
        # Filter metrics by categories if provided
        if categories:
            filtered_metrics = {}
            for category in categories:
                # Map category to actual metric names
                if category in base_metrics:
                    filtered_metrics[category] = base_metrics[category]
                elif 'Revenue' in category and 'Revenue Growth Rate' in base_metrics:
                    filtered_metrics['Revenue Growth Rate'] = base_metrics['Revenue Growth Rate']
                elif 'Margin' in category and 'Operating Margin' in base_metrics:
                    filtered_metrics['Operating Margin'] = base_metrics['Operating Margin']
                elif 'Cash Flow' in category and 'Free Cash Flow' in base_metrics:
                    filtered_metrics['Free Cash Flow'] = base_metrics['Free Cash Flow']
            
            if filtered_metrics:
                base_metrics = filtered_metrics
        
        # Convert to Eagle API format with realistic variations
        for metric_name, base_value in base_metrics.items():
            varied_value = base_value * variation_factor
            
            metrics[metric_name] = {
                'value': round(varied_value, 4),
                'currency': 'USD' if 'Cash Flow' in metric_name else None,
                'unit': '%' if any(x in metric_name for x in ['Rate', 'Margin', 'Ratio', 'Growth']) else 'billions' if 'Cash Flow' in metric_name else None,
                'period': 'TTM',
                'category': self._get_metric_category(metric_name),
                'last_updated': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                'data_quality': 'verified',
                'source': 'Eagle API'
            }
        
        return {
            'success': True,
            'company': {
                'ticker': ticker.upper(),
                'name': company_info['name'],
                'sedol': company_info['sedol'],
                'sector': company_info['sector'],
                'industry': company_info['industry']
            },
            'metrics': metrics,
            'metadata': {
                'request_time': datetime.now().isoformat(),
                'api_version': '2.1',
                'data_source': 'Eagle Financial Platform',
                'metrics_count': len(metrics)
            }
        }
    
    def get_test_response_for_company(self, ticker: str = 'NVDA', sedol_id: str = '2379504') -> Dict[str, Any]:
        """Get test response in full Eagle API format for frontend testing"""
        
        company_metrics = self.get_company_metrics(ticker, sedol_id=sedol_id)
        
        # Convert to full Eagle API response format
        financial_metrics = []
        for metric_name, metric_data in company_metrics['metrics'].items():
            financial_metrics.append({
                'name': metric_name,
                'value': metric_data['value'],
                'currency': metric_data.get('currency'),
                'unit': metric_data.get('unit'),
                'period': metric_data['period'],
                'category': metric_data['category'],
                'last_updated': metric_data['last_updated'],
                'data_quality': metric_data['data_quality']
            })
        
        return {
            'success': True,
            'request_id': f'mock-{ticker.lower()}-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'data': {
                'company': company_metrics['company'],
                'financialMetrics': [{
                    'metrics': financial_metrics,
                    'summary': {
                        'total_metrics': len(financial_metrics),
                        'data_coverage': 'comprehensive',
                        'last_refresh': datetime.now().isoformat()
                    }
                }]
            },
            'metadata': company_metrics['metadata']
        }
    
    def _get_metric_category(self, metric_name: str) -> str:
        """Categorize metrics for proper classification"""
        if any(x in metric_name for x in ['Revenue', 'Growth']):
            return 'growth_metrics'
        elif any(x in metric_name for x in ['Margin', 'Profit']):
            return 'profitability'
        elif any(x in metric_name for x in ['Cash Flow', 'Current', 'Debt']):
            return 'financial_health'
        elif any(x in metric_name for x in ['Return', 'ROE', 'ROA']):
            return 'efficiency'
        elif any(x in metric_name for x in ['Price', 'P/E', 'EV']):
            return 'valuation'
        else:
            return 'operational'
    
    def validate_connection(self) -> bool:
        """Mock connection validation that always succeeds"""
        return True
    
    def get_available_metrics(self, ticker: str) -> List[str]:
        """Get list of available metrics for a company"""
        company_info = self.company_data.get(ticker.upper(), {})
        return list(company_info.get('base_metrics', {}).keys())
    
    def get_historical_data(self, ticker: str, metric: str, periods: int = 12) -> Dict[str, Any]:
        """Get historical data for a metric (mock implementation)"""
        base_value = random.uniform(0.05, 0.50)
        historical_data = []
        
        for i in range(periods):
            date = datetime.now() - timedelta(days=30 * i)
            variation = 1 + random.uniform(-0.1, 0.1)
            value = base_value * variation
            
            historical_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': round(value, 4),
                'period': f'Q{((date.month - 1) // 3) + 1} {date.year}'
            })
        
        return {
            'success': True,
            'ticker': ticker.upper(),
            'metric': metric,
            'data': list(reversed(historical_data)),
            'metadata': {
                'periods': periods,
                'frequency': 'quarterly',
                'last_updated': datetime.now().isoformat()
            }
        }