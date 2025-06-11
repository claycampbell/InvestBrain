import logging
from services.azure_openai_service import AzureOpenAIService

class ThesisAnalyzer:
    def __init__(self):
        self.openai_service = AzureOpenAIService()
    
    def analyze_thesis(self, thesis_text):
        """
        Analyze an investment thesis and return structured components
        """
        if not self.openai_service.is_available():
            raise Exception("Azure OpenAI service is not available. Please check your configuration.")
        
        try:
            # Use Azure OpenAI to analyze the thesis
            analysis = self.openai_service.analyze_thesis(thesis_text)
            
            # Validate and enhance the analysis
            enhanced_analysis = self._enhance_analysis(analysis, thesis_text)
            
            logging.info(f"Successfully analyzed thesis: {thesis_text[:100]}...")
            return enhanced_analysis
            
        except Exception as e:
            logging.error(f"Error in thesis analysis: {str(e)}")
            raise
    
    def _enhance_analysis(self, analysis, original_thesis):
        """
        Enhance the AI analysis with additional validation and structure
        """
        # Ensure all required fields are present
        required_fields = [
            'core_claim', 'causal_chain', 'assumptions', 'mental_model',
            'counter_thesis', 'metrics_to_track', 'monitoring_plan'
        ]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = self._get_default_value(field)
        
        # Validate metrics structure
        if analysis.get('metrics_to_track'):
            validated_metrics = []
            for metric in analysis['metrics_to_track']:
                if isinstance(metric, dict) and 'name' in metric:
                    # Ensure all metric fields are present
                    validated_metric = {
                        'name': metric.get('name', 'Unknown Metric'),
                        'type': metric.get('type', 'price'),
                        'description': metric.get('description', ''),
                        'frequency': metric.get('frequency', 'daily'),
                        'threshold': metric.get('threshold', 5.0),
                        'threshold_type': metric.get('threshold_type', 'change_percent')
                    }
                    validated_metrics.append(validated_metric)
            analysis['metrics_to_track'] = validated_metrics
        
        # Validate monitoring plan structure
        if analysis.get('monitoring_plan'):
            monitoring_plan = analysis['monitoring_plan']
            if not isinstance(monitoring_plan, dict):
                monitoring_plan = {}
            
            analysis['monitoring_plan'] = {
                'review_frequency': monitoring_plan.get('review_frequency', 'monthly'),
                'key_indicators': monitoring_plan.get('key_indicators', []),
                'alert_conditions': monitoring_plan.get('alert_conditions', [])
            }
        
        # Add metadata
        analysis['analysis_metadata'] = {
            'original_thesis_length': len(original_thesis),
            'analysis_timestamp': None,  # Will be set when saved to database
            'ai_model_used': 'gpt-35-turbo',
            'confidence_score': self._calculate_confidence_score(analysis)
        }
        
        return analysis
    
    def _get_default_value(self, field):
        """Get default values for missing fields"""
        defaults = {
            'core_claim': 'Unable to extract core claim',
            'causal_chain': [],
            'assumptions': [],
            'mental_model': 'unknown',
            'counter_thesis': [],
            'metrics_to_track': [],
            'monitoring_plan': {
                'review_frequency': 'monthly',
                'key_indicators': [],
                'alert_conditions': []
            }
        }
        return defaults.get(field, None)
    
    def _calculate_confidence_score(self, analysis):
        """Calculate a confidence score based on the completeness of the analysis"""
        score = 0
        max_score = 100
        
        # Check core components (40 points)
        if analysis.get('core_claim') and analysis['core_claim'] != 'Unable to extract core claim':
            score += 10
        if analysis.get('causal_chain') and len(analysis['causal_chain']) > 0:
            score += 10
        if analysis.get('assumptions') and len(analysis['assumptions']) > 0:
            score += 10
        if analysis.get('mental_model') and analysis['mental_model'] != 'unknown':
            score += 10
        
        # Check analysis depth (30 points)
        if analysis.get('counter_thesis') and len(analysis['counter_thesis']) > 0:
            score += 15
        if analysis.get('metrics_to_track') and len(analysis['metrics_to_track']) > 0:
            score += 15
        
        # Check monitoring plan (30 points)
        monitoring_plan = analysis.get('monitoring_plan', {})
        if monitoring_plan.get('key_indicators') and len(monitoring_plan['key_indicators']) > 0:
            score += 15
        if monitoring_plan.get('alert_conditions') and len(monitoring_plan['alert_conditions']) > 0:
            score += 15
        
        return min(score, max_score)
    
    def generate_thesis_from_documents(self, processed_documents):
        """
        Generate a thesis statement from processed document data
        """
        if not self.openai_service.is_available():
            raise Exception("Azure OpenAI service is not available. Please check your configuration.")
        
        try:
            # Combine document data into a summary
            data_summary = self._create_data_summary(processed_documents)
            
            # Generate thesis using AI
            thesis_statement = self.openai_service.generate_thesis_from_data(data_summary)
            
            # Analyze the generated thesis
            analysis = self.analyze_thesis(thesis_statement)
            analysis['generated_from_documents'] = True
            analysis['source_documents'] = [doc.get('filename', 'unknown') for doc in processed_documents]
            
            return {
                'thesis_statement': thesis_statement,
                'analysis': analysis
            }
            
        except Exception as e:
            logging.error(f"Error generating thesis from documents: {str(e)}")
            raise
    
    def _create_data_summary(self, processed_documents):
        """Create a summary of processed document data for thesis generation"""
        summary_parts = []
        
        for doc in processed_documents:
            doc_summary = f"Document: {doc.get('filename', 'Unknown')}\n"
            
            if doc.get('processed_data'):
                data = doc['processed_data']
                
                # Add text content if available
                if data.get('text_content'):
                    doc_summary += f"Key content: {data['text_content'][:500]}...\n"
                
                # Add table data if available
                if data.get('tables'):
                    doc_summary += f"Tables found: {len(data['tables'])} tables with financial/numerical data\n"
                
                # Add metadata
                if data.get('metadata'):
                    metadata = data['metadata']
                    doc_summary += f"Document type: {metadata.get('document_type', 'unknown')}\n"
                    doc_summary += f"Page count: {metadata.get('page_count', 'unknown')}\n"
            
            summary_parts.append(doc_summary)
        
        return "\n\n".join(summary_parts)
