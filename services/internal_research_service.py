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
        """Generate structured queries to validate core thesis claims"""
        try:
            prompt = f"""Convert this investment thesis core claim into structured financial data queries.

Core Claim: {core_claim}
Mental Model: {mental_model}

Generate 2-3 specific financial data queries that would validate or challenge this thesis claim. 
Use only these supported fields: {', '.join(self.supported_fields['fundamental'] + self.supported_fields['performance'])}

For each query, provide:
1. A clear signal name
2. Entities (companies/funds) to analyze
3. Specific metrics to retrieve
4. Filters with operators (gt, gte, lt, lte, eq, between for numbers; in, contains for categories)
5. Relationships if needed (manager_holding, fund_holding)
6. Sort criteria
7. Result limit

Output valid JSON array of query objects."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_service.generate_completion(messages, temperature=0.3, max_tokens=800)
            
            if response:
                queries = self._parse_query_response(response)
                return [self._create_research_signal(q, "Core Validation") for q in queries]
            
        except Exception as e:
            logging.warning(f"Core validation query generation failed: {str(e)}")
        
        return []
    
    def _generate_assumption_queries(self, assumptions: List[str]) -> List[Dict[str, Any]]:
        """Generate queries to test thesis assumptions"""
        if not assumptions:
            return []
            
        try:
            assumptions_text = '; '.join(assumptions[:3])  # Limit to top 3 assumptions
            
            prompt = f"""Convert these thesis assumptions into testable financial data queries.

Assumptions: {assumptions_text}

Generate specific queries that would test each assumption using financial data.
Use only supported fields: {', '.join(self.supported_fields['fundamental'] + self.supported_fields['categorical'])}

Output JSON array of structured query objects with signal names, entities, metrics, filters, and sort criteria."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_service.generate_completion(messages, temperature=0.3, max_tokens=600)
            
            if response:
                queries = self._parse_query_response(response)
                return [self._create_research_signal(q, "Assumption Testing") for q in queries]
                
        except Exception as e:
            logging.warning(f"Assumption query generation failed: {str(e)}")
        
        return []
    
    def _generate_metric_tracking_queries(self, metrics: List[str]) -> List[Dict[str, Any]]:
        """Generate queries for metrics tracking"""
        if not metrics:
            return []
            
        try:
            metrics_text = '; '.join(metrics[:4])  # Limit to top 4 metrics
            
            prompt = f"""Convert these investment metrics into structured data retrieval queries.

Metrics to Track: {metrics_text}

Create queries that would monitor these metrics using supported financial fields:
{', '.join(self.supported_fields['fundamental'] + self.supported_fields['performance'])}

Output JSON array of query objects for tracking these metrics."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_service.generate_completion(messages, temperature=0.3, max_tokens=500)
            
            if response:
                queries = self._parse_query_response(response)
                return [self._create_research_signal(q, "Metrics Tracking") for q in queries]
                
        except Exception as e:
            logging.warning(f"Metrics query generation failed: {str(e)}")
        
        return []
    
    def _generate_peer_comparison_queries(self, core_claim: str) -> List[Dict[str, Any]]:
        """Generate peer comparison queries"""
        try:
            prompt = f"""Based on this investment thesis, create peer comparison queries.

Thesis: {core_claim}

Generate 1-2 queries that would compare the thesis target with industry peers or competitors.
Use sector, industry filters and comparative metrics like pe, roic, revenue_growth.

Output JSON array of comparative query objects."""

            messages = [{"role": "user", "content": prompt}]
            response = self.ai_service.generate_completion(messages, temperature=0.3, max_tokens=400)
            
            if response:
                queries = self._parse_query_response(response)
                return [self._create_research_signal(q, "Peer Comparison") for q in queries]
                
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