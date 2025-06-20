"""
Analysis Workflow Service - Orchestrates comprehensive analysis combining metrics and documents
"""

import json
from typing import Dict, Any, List
import logging
from datetime import datetime

from services.metric_selector import MetricSelector
from services.data_adapter_service import DataAdapter
from services.document_processor import DocumentProcessor
from services.azure_openai_service import AzureOpenAIService

class AnalysisWorkflowService:
    """Orchestrates comprehensive analysis workflows"""
    
    def __init__(self):
        self.metric_selector = MetricSelector()
        self.data_adapter = DataAdapter()
        self.document_processor = DocumentProcessor()
        self.openai_service = AzureOpenAIService()
    
    def process_analysis_request(self, request_type: str, documents: List[str] = None, 
                               context: Dict[str, Any] = None, entity_id: str = None) -> Dict[str, Any]:
        """Process a comprehensive analysis request"""
        
        if context is None:
            context = {}
        
        # Get relevant metrics for analysis type
        metrics_config = self.metric_selector.get_metrics_for_analysis(request_type)
        all_metrics = metrics_config.get('primary_metrics', []) + metrics_config.get('supporting_metrics', [])
        
        # Fetch metric data
        metric_data = {}
        if entity_id and all_metrics:
            metric_result = self.data_adapter.fetch_metric_values(all_metrics, entity_id)
            if metric_result.get('success'):
                metric_data = metric_result.get('metrics', {})
        
        # Process documents if provided
        document_insights = {}
        if documents:
            for doc in documents:
                try:
                    # In a real implementation, this would process actual uploaded documents
                    doc_result = self.document_processor.process_document(doc)
                    if doc_result:
                        document_insights[doc] = doc_result
                except Exception as e:
                    logging.error(f"Failed to process document {doc}: {e}")
        
        # Compile analysis data
        analysis_data = {
            'request_type': request_type,
            'timestamp': datetime.utcnow().isoformat(),
            'context': context,
            'metrics': {
                'config': metrics_config,
                'data': metric_data,
                'coverage': len(metric_data) / len(all_metrics) if all_metrics else 0
            },
            'documents': {
                'processed': list(document_insights.keys()),
                'insights': document_insights
            },
            'entity_id': entity_id
        }
        
        return analysis_data
    
    def generate_llm_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a comprehensive LLM prompt from analysis data"""
        
        request_type = analysis_data.get('request_type', 'comprehensive')
        metrics = analysis_data.get('metrics', {})
        documents = analysis_data.get('documents', {})
        context = analysis_data.get('context', {})
        
        prompt = f"""
Conduct a {request_type} investment analysis based on the following data:

CONTEXT:
{json.dumps(context, indent=2)}

QUANTITATIVE METRICS:
Available Metrics: {len(metrics.get('data', {}))} out of {len(metrics.get('config', {}).get('primary_metrics', []) + metrics.get('config', {}).get('supporting_metrics', []))}
Data Coverage: {metrics.get('coverage', 0):.1%}

Primary Metrics:
{json.dumps(metrics.get('config', {}).get('primary_metrics', []), indent=2)}

Supporting Metrics:
{json.dumps(metrics.get('config', {}).get('supporting_metrics', []), indent=2)}

Metric Values:
{json.dumps(metrics.get('data', {}), indent=2)}

QUALITATIVE INSIGHTS:
Documents Processed: {len(documents.get('processed', []))}
{json.dumps(documents.get('insights', {}), indent=2)}

ANALYSIS REQUIREMENTS:
1. Integrate quantitative metrics with qualitative document insights
2. Identify key trends, strengths, and risks
3. Provide specific, actionable investment recommendations
4. Consider both current performance and forward-looking indicators
5. Highlight any data gaps or limitations

Please provide a structured analysis with:
- Executive Summary
- Key Findings (quantitative and qualitative)
- Risk Assessment
- Investment Recommendation
- Supporting Rationale
"""
        
        return prompt
    
    def run_comprehensive_analysis(self, company_ticker: str, analysis_type: str = "comprehensive",
                                 documents: List[str] = None) -> Dict[str, Any]:
        """Run a complete analysis workflow"""
        
        context = {
            'company_ticker': company_ticker,
            'analysis_date': datetime.utcnow().isoformat(),
            'analyst': 'AI Investment Analysis System'
        }
        
        # Process the analysis request
        analysis_data = self.process_analysis_request(
            request_type=analysis_type,
            documents=documents or [],
            context=context,
            entity_id=self._get_entity_id_for_ticker(company_ticker)
        )
        
        # Generate LLM analysis if we have sufficient data
        llm_analysis = None
        if analysis_data.get('metrics', {}).get('data') or analysis_data.get('documents', {}).get('insights'):
            try:
                prompt = self.generate_llm_prompt(analysis_data)
                
                messages = [
                    {
                        "role": "system", 
                        "content": "You are an expert investment analyst with deep knowledge of financial metrics and qualitative analysis. Provide comprehensive, actionable investment insights."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
                
                llm_response = self.openai_service.generate_completion(messages, temperature=0.3)
                llm_analysis = self._parse_llm_analysis(llm_response)
                
            except Exception as e:
                logging.error(f"LLM analysis failed: {e}")
                llm_analysis = {'error': 'Analysis generation failed', 'details': str(e)}
        
        # Compile final result
        result = {
            'company_ticker': company_ticker,
            'analysis_type': analysis_type,
            'timestamp': datetime.utcnow().isoformat(),
            'raw_data': analysis_data,
            'llm_analysis': llm_analysis,
            'data_quality': self._assess_data_quality(analysis_data),
            'recommendations': self._extract_recommendations(llm_analysis) if llm_analysis else []
        }
        
        return result
    
    def _get_entity_id_for_ticker(self, ticker: str) -> str:
        """Map ticker to entity ID - in production this would use a proper mapping service"""
        # This is a placeholder - in production, you'd have a proper ticker-to-entity mapping
        ticker_mapping = {
            'NVDA': 'BDRXDB4',  # Example mapping
            'AAPL': 'EXAMPLE_ID',
            # Add more mappings as needed
        }
        return ticker_mapping.get(ticker.upper(), 'BDRXDB4')  # Default fallback
    
    def _parse_llm_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract structured data if the LLM returns JSON
            if '{' in response and '}' in response:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Otherwise, return as structured text
            return {
                'analysis_text': response,
                'parsed': False,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Failed to parse LLM response: {e}")
            return {
                'analysis_text': response,
                'parsing_error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _assess_data_quality(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality and completeness of analysis data"""
        metrics = analysis_data.get('metrics', {})
        documents = analysis_data.get('documents', {})
        
        return {
            'metric_coverage': metrics.get('coverage', 0),
            'metric_count': len(metrics.get('data', {})),
            'document_count': len(documents.get('processed', [])),
            'data_freshness': analysis_data.get('timestamp'),
            'completeness_score': (
                (metrics.get('coverage', 0) * 0.7) + 
                (min(len(documents.get('processed', [])) / 3, 1) * 0.3)  # Normalize doc count
            ),
            'quality_rating': 'high' if metrics.get('coverage', 0) > 0.8 else 'medium' if metrics.get('coverage', 0) > 0.5 else 'low'
        }
    
    def _extract_recommendations(self, llm_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable recommendations from LLM analysis"""
        if not llm_analysis or 'error' in llm_analysis:
            return []
        
        # Try to extract recommendations from structured analysis
        if 'recommendations' in llm_analysis:
            return llm_analysis['recommendations']
        
        # Otherwise, generate basic recommendations based on available data
        return [
            {
                'action': 'Review Analysis',
                'rationale': 'Comprehensive analysis completed with available data',
                'priority': 'medium',
                'timeframe': 'immediate'
            }
        ]