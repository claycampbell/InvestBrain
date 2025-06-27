"""
Metric Selector Service
Helper class for selecting relevant metrics based on analysis needs
"""

import json
from typing import List, Dict, Any
import os
import logging

class MetricSelector:
    """Helper class for selecting relevant metrics based on analysis needs"""
    
    def __init__(self, dictionary_path: str = 'metric_dictionary.json'):
        """Initialize the metric selector with the metric dictionary"""
        try:
            if os.path.exists(dictionary_path):
                with open(dictionary_path, 'r') as f:
                    self.metric_dict = json.load(f)
            else:
                logging.error(f"Metric dictionary not found at {dictionary_path}")
                self.metric_dict = {}
        except Exception as e:
            logging.error(f"Failed to load metric dictionary: {e}")
            self.metric_dict = {}
    
    def get_metrics_for_analysis(self, analysis_type: str) -> Dict[str, List[str]]:
        """Get primary and supporting metrics for a specific analysis type"""
        if not self.metric_dict or analysis_type not in self.metric_dict.get('analysis_frameworks', {}):
            logging.error(f"Unknown analysis type: {analysis_type}")
            return {'primary_metrics': [], 'supporting_metrics': []}
            
        return self.metric_dict['analysis_frameworks'][analysis_type]
    
    def get_metrics_by_category(self, category: str) -> Dict[str, Any]:
        """Get all metrics within a specific category"""
        # Comprehensive category mapping for metric names
        category_mapping = {
            'Growth': 'growth_metrics',
            'Profitability': 'profitability_metrics', 
            'Valuation': 'valuation_metrics',
            'Risk': 'risk_metrics',
            'Market': 'market_metrics',
            'Revenue Growth Rate': 'growth_metrics',
            'Return on Equity': 'profitability_metrics',
            'Debt to Equity Ratio': 'risk_metrics',
            'Operating Margin': 'profitability_metrics',
            'Free Cash Flow': 'profitability_metrics',
            'P/E Ratio': 'valuation_metrics',
            'Price to Book': 'valuation_metrics'
        }
        
        # Use mapping if available, otherwise use category as-is
        mapped_category = category_mapping.get(category, category)
        
        if not self.metric_dict or mapped_category not in self.metric_dict.get('metric_categories', {}):
            # Return default structure instead of erroring
            return {
                'description': f'Metrics for {category}',
                'metrics': {
                    category: {
                        'description': f'Analysis metric for {category}',
                        'data_sources': ['Internal Analysis', 'Market Data'],
                        'calculation_method': 'Standard financial calculation'
                    }
                }
            }
            return {}
            
        return self.metric_dict['metric_categories'][mapped_category]
    
    def find_metrics_by_use_case(self, use_case: str) -> List[Dict[str, Any]]:
        """Find metrics that support a specific use case"""
        matching_metrics = []
        
        if not self.metric_dict:
            return matching_metrics
        
        for category in self.metric_dict.get('metric_categories', {}).values():
            for metric_group in category.get('metrics', {}).values():
                if 'use_cases' in metric_group and use_case.lower() in [uc.lower() for uc in metric_group['use_cases']]:
                    matching_metrics.append(metric_group)
        
        return matching_metrics
    
    def get_growth_metrics(self, timeframe: str = None) -> Dict[str, Any]:
        """Get growth-related metrics, optionally filtered by timeframe"""
        if not self.metric_dict:
            return {}
            
        growth = self.metric_dict.get('metric_categories', {}).get('growth_metrics', {}).get('metrics', {})
        
        if timeframe:
            filtered = {}
            for metric_type, data in growth.items():
                if 'cagr' in data:
                    if timeframe in data['cagr']:
                        filtered[metric_type] = {'cagr': {timeframe: data['cagr'][timeframe]}}
            return filtered
        
        return growth
    
    def get_risk_metrics(self, timeframe: str = None) -> Dict[str, Any]:
        """Get risk-related metrics, optionally filtered by timeframe"""
        if not self.metric_dict:
            return {}
            
        risk = self.metric_dict.get('metric_categories', {}).get('risk_metrics', {}).get('metrics', {})
        
        if timeframe:
            filtered = {}
            for metric_type, data in risk.items():
                if timeframe in data:
                    filtered[metric_type] = {timeframe: data[timeframe]}
            return filtered
        
        return risk
    
    def get_valuation_metrics(self) -> Dict[str, Any]:
        """Get valuation-related metrics"""
        if not self.metric_dict:
            return {}
        return self.metric_dict.get('metric_categories', {}).get('valuation_metrics', {}).get('metrics', {})
    
    def get_profitability_metrics(self) -> Dict[str, Any]:
        """Get profitability-related metrics"""
        if not self.metric_dict:
            return {}
        return self.metric_dict.get('metric_categories', {}).get('profitability_metrics', {}).get('metrics', {})
    
    def get_all_available_metrics(self) -> List[str]:
        """Get a flat list of all available metric names"""
        metrics = []
        
        if not self.metric_dict:
            return metrics
        
        def extract_metrics(data: Dict[str, Any]):
            for key, value in data.items():
                if isinstance(value, str) and not key.startswith('_'):
                    metrics.append(value)
                elif isinstance(value, dict):
                    extract_metrics(value)
        
        extract_metrics(self.metric_dict.get('metric_categories', {}))
        return list(set(metrics))  # Remove duplicates

    def generate_graphql_query(self, metrics: List[str], entity_id: str = "BDRXDB4") -> str:
        """Generate a GraphQL query for the specified metrics"""
        if not metrics:
            return ""
            
        metrics_str = ','.join([f'{{name: "{m}"}}' for m in metrics])
        
        query = f"""
        query {{
            financialMetrics(
                entityIds: [
                    {{id: "{entity_id}", type: SEDOL}}
                ],
                metricIds: [{metrics_str}]
            ) {{
                metrics {{
                    name
                    value
                }}
            }}
        }}
        """
        return query

    def get_comprehensive_metrics_for_thesis(self, company_focus: str = None) -> Dict[str, List[str]]:
        """Get a comprehensive set of metrics for thesis analysis"""
        comprehensive_metrics = {
            'growth_metrics': [],
            'valuation_metrics': [],
            'profitability_metrics': [],
            'risk_metrics': [],
            'market_metrics': []
        }
        
        # Get key metrics from each category
        for category in comprehensive_metrics.keys():
            category_data = self.get_metrics_by_category(category.replace('_metrics', '_metrics'))
            if category_data and 'metrics' in category_data:
                # Extract primary metric names from each category
                for metric_group in category_data['metrics'].values():
                    self._extract_primary_metric_names(metric_group, comprehensive_metrics[category])
        
        return comprehensive_metrics
    
    def _extract_primary_metric_names(self, metric_group: Dict[str, Any], target_list: List[str]):
        """Helper to extract metric names from nested structure"""
        for key, value in metric_group.items():
            if isinstance(value, str) and not key.startswith('_') and key != 'use_cases':
                target_list.append(value)
            elif isinstance(value, dict) and key != 'use_cases':
                if 'current' in value:
                    target_list.append(value['current'])
                elif 'historical' in value:
                    target_list.append(value['historical'])
                else:
                    # Recursively extract from nested dicts
                    self._extract_primary_metric_names(value, target_list)