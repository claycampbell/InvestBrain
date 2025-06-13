"""
Internal Research Data Service - Level 0 Signal Generation
Converts thesis analysis into structured financial data queries using LLM intelligence
"""

import json
import logging
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService

class InternalResearchService:
    """
    Level 0 signal generation - converts thesis analysis into structured financial queries
    """
    
    def __init__(self):
        self.ai_service = AzureOpenAIService()
        
        # Supported financial data fields and operators
        self.supported_fields = {
            'fundamental': [
                'market_cap', 'enterprise_value', 'revenue', 'dividend_yield', 
                'pe', 'roic', 'fcf', 'dps', 'revenue_growth', 'revenue_cagr_5_yr',
                'dps_cagr_1_yr', 'dps_cagr_5_yr', 'dps_cagr_10_yr'
            ],
            'performance': [
                'maximum_drawdown_1_yr', 'maximum_drawdown_3_yr', 'maximum_drawdown_5_yr',
                'total_returns_1_ytd', 'total_returns_3_ytd'
            ],
            'categorical': [
                'cc_rating', 'industry', 'sector', 'country', 'credit_rating',
                'covering_analyst', 'eligibility'
            ]
        }
        
        self.supported_operators = {
            'numerical': ['gt', 'gte', 'lt', 'lte', 'eq', 'between'],
            'categorical': ['in', 'not_in', 'eq', 'contains']
        }
        
        self.supported_relationships = ['manager_holding', 'fund_holding']
    
    def generate_research_signals(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate Level 0 Internal Research Data signals from thesis analysis
        """
        try:
            # Extract thesis components
            core_claim = thesis_analysis.get('core_claim', '')
            assumptions = thesis_analysis.get('assumptions', [])
            mental_model = thesis_analysis.get('mental_model', '')
            metrics_to_track = thesis_analysis.get('metrics_to_track', [])
            
            # Generate structured queries for each thesis component
            research_signals = []
            
            # Generate queries for core thesis validation
            core_queries = self._generate_core_validation_queries(core_claim, mental_model)
            research_signals.extend(core_queries)
            
            # Generate queries for assumption testing
            assumption_queries = self._generate_assumption_queries(assumptions)
            research_signals.extend(assumption_queries)
            
            # Generate queries for metrics tracking
            metric_queries = self._generate_metric_tracking_queries(metrics_to_track)
            research_signals.extend(metric_queries)
            
            # Generate peer comparison queries
            peer_queries = self._generate_peer_comparison_queries(core_claim)
            research_signals.extend(peer_queries)
            
            logging.info(f"Generated {len(research_signals)} Level 0 research signals")
            return research_signals
            
        except Exception as e:
            logging.error(f"Error generating research signals: {str(e)}")
            return []
    
    def _generate_core_validation_queries(self, core_claim: str, mental_model: str) -> List[Dict[str, Any]]:
        """Generate structured queries to validate core thesis claims using intelligent analysis"""
        try:
            # Use intelligent analysis to generate thesis-specific queries
            return self._generate_intelligent_core_queries(core_claim, mental_model)
            
        except Exception as e:
            logging.warning(f"Core validation query generation failed: {str(e)}")
            return []
    
    def _generate_assumption_queries(self, assumptions: List[str]) -> List[Dict[str, Any]]:
        """Generate queries to test thesis assumptions using intelligent analysis"""
        if not assumptions:
            return []
            
        try:
            return self._generate_intelligent_assumption_queries(assumptions[:3])
                
        except Exception as e:
            logging.warning(f"Assumption query generation failed: {str(e)}")
        
        return []
    
    def _generate_metric_tracking_queries(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Generate queries for metrics tracking using intelligent analysis"""
        if not metrics:
            return []
            
        try:
            return self._generate_intelligent_metric_queries(metrics[:4])
                
        except Exception as e:
            logging.warning(f"Metrics query generation failed: {str(e)}")
        
        return []
    
    def _generate_peer_comparison_queries(self, core_claim: str) -> List[Dict[str, Any]]:
        """Generate peer comparison queries using intelligent analysis"""
        try:
            return self._generate_intelligent_peer_queries(core_claim)
                
        except Exception as e:
            logging.warning(f"Peer comparison query generation failed: {str(e)}")
        
        return []
    
    def _parse_query_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response into structured query objects"""
        try:
            # Clean response to extract JSON
            response = response.strip()
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join([line for line in lines if not line.startswith('```')])
            
            # Try to find JSON array in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                queries = json.loads(json_str)
                
                # Validate and clean queries
                validated_queries = []
                for query in queries:
                    if isinstance(query, dict) and 'signal_name' in query:
                        validated_queries.append(query)
                
                return validated_queries
            
        except Exception as e:
            logging.warning(f"Query parsing failed: {str(e)}")
        
        return []
    
    def _create_research_signal(self, query: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Create a Level 0 research signal from a structured query"""
        return {
            'signal_name': query.get('signal_name', f"{category} Query"),
            'signal_level': 'Internal Research Data',
            'category': category,
            'description': f"Structured financial data query for {category.lower()}",
            'query_structure': {
                'entities': query.get('entities', []),
                'metrics': query.get('metrics', []),
                'filters': query.get('filters', {}),
                'relationships': query.get('relationships', []),
                'sort_by': query.get('sort_by', {}),
                'limit': query.get('limit', 10)
            },
            'data_type': 'financial_structured',
            'execution_frequency': 'daily',
            'priority': 'high',
            'validation_rules': {
                'supported_fields': self._validate_fields(query.get('metrics', [])),
                'supported_operators': self._validate_operators(query.get('filters', {}))
            }
        }
    
    def _validate_fields(self, fields: List[str]) -> bool:
        """Validate that fields are supported"""
        all_supported = (self.supported_fields['fundamental'] + 
                        self.supported_fields['performance'] + 
                        self.supported_fields['categorical'])
        return all(field in all_supported for field in fields)
    
    def _validate_operators(self, filters: Dict[str, Any]) -> bool:
        """Validate that operators are supported"""
        for field, condition in filters.items():
            if isinstance(condition, dict) and 'operator' in condition:
                operator = condition['operator']
                if operator not in (self.supported_operators['numerical'] + 
                                  self.supported_operators['categorical']):
                    return False
        return True
    
    def execute_research_query(self, query_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured research query (placeholder for actual implementation)
        In production, this would connect to financial data APIs
        """
        return {
            'query_executed': True,
            'query_structure': query_structure,
            'execution_timestamp': 'placeholder',
            'result_count': 'placeholder',
            'data_source': 'Internal Research Database',
            'note': 'Query structure validated and ready for execution'
        }
    
    def _generate_intelligent_core_queries(self, core_claim: str, mental_model: str) -> List[Dict[str, Any]]:
        """Generate intelligent core validation queries based on thesis analysis"""
        queries = []
        
        # Extract company/sector from core claim
        entities = self._extract_entities_from_text(core_claim)
        
        # Generate fundamental validation query
        if 'growth' in core_claim.lower() or mental_model.lower() == 'growth':
            queries.append({
                'signal_name': 'Revenue Growth Validation',
                'entities': entities,
                'metrics': ['revenue_growth', 'revenue_cagr_5_yr', 'market_cap'],
                'filters': {
                    'revenue_growth': {'operator': 'gte', 'value': 0.15}  # 15%+ growth
                },
                'sort_by': {'field': 'revenue_growth', 'order': 'desc'},
                'limit': 10
            })
        
        # Generate market position query
        if any(word in core_claim.lower() for word in ['market', 'leader', 'share', 'competitive']):
            queries.append({
                'signal_name': 'Market Position Analysis',
                'entities': entities,
                'metrics': ['market_cap', 'enterprise_value', 'pe', 'roic'],
                'filters': {
                    'market_cap': {'operator': 'gte', 'value': 1000000000}  # $1B+ market cap
                },
                'sort_by': {'field': 'market_cap', 'order': 'desc'},
                'limit': 5
            })
        
        # Generate profitability validation
        if any(word in core_claim.lower() for word in ['profit', 'margin', 'efficiency', 'return']):
            queries.append({
                'signal_name': 'Profitability Metrics',
                'entities': entities,
                'metrics': ['roic', 'pe', 'fcf', 'dividend_yield'],
                'filters': {
                    'roic': {'operator': 'gte', 'value': 0.10}  # 10%+ ROIC
                },
                'sort_by': {'field': 'roic', 'order': 'desc'},
                'limit': 8
            })
        
        return [self._create_research_signal(q, "Core Validation") for q in queries]
    
    def _generate_intelligent_assumption_queries(self, assumptions: List[str]) -> List[Dict[str, Any]]:
        """Generate intelligent assumption testing queries"""
        queries = []
        
        for i, assumption in enumerate(assumptions):
            assumption_lower = assumption.lower()
            
            # Technology/innovation assumptions
            if any(word in assumption_lower for word in ['ai', 'technology', 'innovation', 'digital']):
                queries.append({
                    'signal_name': f'Tech Innovation Validation {i+1}',
                    'entities': self._extract_entities_from_text(assumption),
                    'metrics': ['revenue_growth', 'revenue_cagr_5_yr', 'market_cap'],
                    'filters': {
                        'sector': {'operator': 'in', 'value': ['Technology', 'Communication Services']},
                        'revenue_growth': {'operator': 'gte', 'value': 0.20}
                    },
                    'sort_by': {'field': 'revenue_growth', 'order': 'desc'},
                    'limit': 10
                })
            
            # Market demand assumptions
            elif any(word in assumption_lower for word in ['demand', 'market', 'adoption', 'growth']):
                queries.append({
                    'signal_name': f'Market Demand Validation {i+1}',
                    'entities': self._extract_entities_from_text(assumption),
                    'metrics': ['revenue_growth', 'total_returns_1_ytd', 'pe'],
                    'filters': {
                        'revenue_growth': {'operator': 'gte', 'value': 0.15}
                    },
                    'sort_by': {'field': 'total_returns_1_ytd', 'order': 'desc'},
                    'limit': 12
                })
            
            # Competitive moat assumptions
            elif any(word in assumption_lower for word in ['competitive', 'moat', 'advantage', 'leadership']):
                queries.append({
                    'signal_name': f'Competitive Advantage Test {i+1}',
                    'entities': self._extract_entities_from_text(assumption),
                    'metrics': ['roic', 'market_cap', 'pe', 'revenue_growth'],
                    'filters': {
                        'roic': {'operator': 'gte', 'value': 0.15},
                        'market_cap': {'operator': 'gte', 'value': 10000000000}  # $10B+
                    },
                    'sort_by': {'field': 'roic', 'order': 'desc'},
                    'limit': 8
                })
        
        return [self._create_research_signal(q, "Assumption Testing") for q in queries]
    
    def _extract_entities_from_text(self, text: str) -> List[str]:
        """Extract likely company/entity names from text"""
        # Simple entity extraction based on common patterns
        entities = []
        
        # Look for common company indicators
        words = text.split()
        for i, word in enumerate(words):
            if word in ['Corporation', 'Corp', 'Inc', 'Company', 'Ltd']:
                if i > 0:
                    entities.append(f"{words[i-1]} {word}")
            elif word.isupper() and len(word) > 2:  # Likely ticker symbols
                entities.append(word)
            elif word[0].isupper() and word.lower() in ['nvidia', 'apple', 'microsoft', 'amazon', 'google', 'tesla']:
                entities.append(word.title())
        
        return entities[:3] if entities else ['Target Company']
    
    def _generate_intelligent_metric_queries(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Generate intelligent metric tracking queries"""
        queries = []
        
        for metric in metrics:
            metric_name = metric.get('name', '') if isinstance(metric, dict) else str(metric)
            metric_lower = metric_name.lower()
            
            # Revenue-focused metrics
            if any(word in metric_lower for word in ['revenue', 'sales', 'income']):
                queries.append({
                    'signal_name': f'Revenue Tracking - {metric_name}',
                    'entities': ['Target Company'],
                    'metrics': ['revenue', 'revenue_growth', 'revenue_cagr_5_yr'],
                    'filters': {},
                    'sort_by': {'field': 'revenue_growth', 'order': 'desc'},
                    'limit': 15
                })
            
            # Profitability metrics
            elif any(word in metric_lower for word in ['margin', 'profit', 'roic', 'efficiency']):
                queries.append({
                    'signal_name': f'Profitability Tracking - {metric_name}',
                    'entities': ['Target Company'],
                    'metrics': ['roic', 'pe', 'fcf', 'dividend_yield'],
                    'filters': {},
                    'sort_by': {'field': 'roic', 'order': 'desc'},
                    'limit': 12
                })
            
            # Market performance metrics
            elif any(word in metric_lower for word in ['market', 'share', 'position', 'performance']):
                queries.append({
                    'signal_name': f'Market Performance - {metric_name}',
                    'entities': ['Target Company'],
                    'metrics': ['market_cap', 'total_returns_1_ytd', 'total_returns_3_ytd'],
                    'filters': {},
                    'sort_by': {'field': 'total_returns_1_ytd', 'order': 'desc'},
                    'limit': 10
                })
        
        return [self._create_research_signal(q, "Metrics Tracking") for q in queries]
    
    def _generate_intelligent_peer_queries(self, core_claim: str) -> List[Dict[str, Any]]:
        """Generate intelligent peer comparison queries"""
        queries = []
        entities = self._extract_entities_from_text(core_claim)
        
        # Technology sector comparison
        if any(word in core_claim.lower() for word in ['ai', 'technology', 'software', 'semiconductor']):
            queries.append({
                'signal_name': 'Technology Sector Peer Analysis',
                'entities': entities,
                'metrics': ['market_cap', 'revenue_growth', 'pe', 'roic'],
                'filters': {
                    'sector': {'operator': 'in', 'value': ['Technology']},
                    'market_cap': {'operator': 'gte', 'value': 1000000000}
                },
                'sort_by': {'field': 'market_cap', 'order': 'desc'},
                'limit': 20
            })
        
        # Growth company comparison
        if any(word in core_claim.lower() for word in ['growth', 'expanding', 'accelerating']):
            queries.append({
                'signal_name': 'High Growth Peer Comparison',
                'entities': entities,
                'metrics': ['revenue_growth', 'revenue_cagr_5_yr', 'total_returns_1_ytd'],
                'filters': {
                    'revenue_growth': {'operator': 'gte', 'value': 0.20}
                },
                'sort_by': {'field': 'revenue_growth', 'order': 'desc'},
                'limit': 15
            })
        
        return [self._create_research_signal(q, "Peer Comparison") for q in queries]