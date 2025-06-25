"""
Document Validation Service - Extracts thesis statements from research documents and validates findings
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.azure_openai_service import AzureOpenAIService
from services.document_processor import DocumentProcessor
from services.reliable_analysis_service import ReliableAnalysisService


class DocumentValidationService:
    """Service for extracting and validating thesis statements from research documents"""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
        self.document_processor = DocumentProcessor()
        self.analysis_service = ReliableAnalysisService()
        
    def extract_thesis_from_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """Extract thesis statement and key findings from a research document"""
        try:
            # Process the document to extract content
            processed_doc = self.document_processor.process_document(file_path)
            
            # Extract thesis using AI analysis
            thesis_extraction = self._analyze_document_for_thesis(processed_doc, filename)
            
            return {
                'success': True,
                'extracted_thesis': thesis_extraction.get('thesis_statement', ''),
                'key_findings': thesis_extraction.get('key_findings', []),
                'investment_logic': thesis_extraction.get('investment_logic', ''),
                'risk_factors': thesis_extraction.get('risk_factors', []),
                'target_metrics': thesis_extraction.get('target_metrics', []),
                'document_summary': thesis_extraction.get('document_summary', ''),
                'confidence_score': thesis_extraction.get('confidence_score', 0.0),
                'processed_document': processed_doc
            }
            
        except Exception as e:
            logging.error(f"Error extracting thesis from document {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'extracted_thesis': '',
                'key_findings': [],
                'investment_logic': '',
                'risk_factors': [],
                'target_metrics': [],
                'document_summary': '',
                'confidence_score': 0.0
            }
    
    def _analyze_document_for_thesis(self, processed_doc: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Use AI to analyze document content and extract thesis components"""
        
        # Prepare document content for analysis
        content_text = ""
        if 'text_content' in processed_doc:
            content_text = processed_doc['text_content']
        elif 'data' in processed_doc:
            # For CSV/Excel files, create text summary
            content_text = self._create_data_summary(processed_doc)
        
        # Create AI prompt for thesis extraction
        extraction_prompt = f"""
Analyze this investment research document and extract the core investment thesis and supporting elements.

Document: {filename}
Content: {content_text[:8000]}  # Limit content to avoid token limits

Please extract and structure the following information:

1. THESIS STATEMENT: The main investment thesis or recommendation (1-2 sentences)
2. KEY FINDINGS: Top 3-5 supporting findings or evidence points
3. INVESTMENT LOGIC: The core reasoning behind the investment recommendation
4. RISK FACTORS: Key risks or concerns mentioned
5. TARGET METRICS: Specific financial metrics or KPIs mentioned
6. DOCUMENT SUMMARY: Brief summary of the document's purpose and scope
7. CONFIDENCE SCORE: Rate confidence in thesis extraction from 0.0 to 1.0

Format your response as JSON with the following structure:
{{
    "thesis_statement": "Clear, concise investment thesis",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
    "investment_logic": "Detailed explanation of investment reasoning",
    "risk_factors": ["Risk 1", "Risk 2"],
    "target_metrics": ["Metric 1", "Metric 2"],
    "document_summary": "Brief document overview",
    "confidence_score": 0.85
}}

Focus on extracting the core investment proposition and supporting evidence.
"""

        try:
            messages = [
                {"role": "system", "content": "You are an expert investment analyst who extracts thesis statements and key insights from research documents."},
                {"role": "user", "content": extraction_prompt}
            ]
            
            response = self.azure_openai.generate_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse JSON response
            if response and 'choices' in response and response['choices']:
                content = response['choices'][0]['message']['content']
                
                # Try to parse as JSON
                try:
                    extracted_data = json.loads(content)
                    return extracted_data
                except json.JSONDecodeError:
                    # If JSON parsing fails, create structured response from text
                    return self._parse_text_response(content)
            
        except Exception as e:
            logging.error(f"Error in AI thesis extraction: {str(e)}")
        
        # Fallback extraction using pattern matching
        return self._fallback_thesis_extraction(content_text, filename)
    
    def _create_data_summary(self, processed_doc: Dict[str, Any]) -> str:
        """Create text summary from structured data"""
        summary_parts = []
        
        if 'tables' in processed_doc:
            for i, table in enumerate(processed_doc['tables']):
                if 'data' in table and table['data']:
                    summary_parts.append(f"Table {i+1}: {len(table['data'])} rows")
                    # Add sample data
                    if len(table['data']) > 0:
                        sample_row = table['data'][0]
                        if isinstance(sample_row, dict):
                            summary_parts.append(f"Columns: {list(sample_row.keys())}")
        
        if 'key_metrics' in processed_doc:
            metrics_text = "Key metrics: " + ", ".join([f"{k}: {v}" for k, v in processed_doc['key_metrics'].items()][:10])
            summary_parts.append(metrics_text)
        
        return "\n".join(summary_parts)
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response text when JSON parsing fails"""
        result = {
            'thesis_statement': '',
            'key_findings': [],
            'investment_logic': '',
            'risk_factors': [],
            'target_metrics': [],
            'document_summary': '',
            'confidence_score': 0.5
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if 'thesis' in line.lower():
                current_section = 'thesis_statement'
            elif 'findings' in line.lower():
                current_section = 'key_findings'
            elif 'logic' in line.lower() or 'reasoning' in line.lower():
                current_section = 'investment_logic'
            elif 'risk' in line.lower():
                current_section = 'risk_factors'
            elif 'metric' in line.lower():
                current_section = 'target_metrics'
            elif 'summary' in line.lower():
                current_section = 'document_summary'
            elif current_section:
                # Add content to current section
                if current_section in ['key_findings', 'risk_factors', 'target_metrics']:
                    if line.startswith('-') or line.startswith('*'):
                        result[current_section].append(line[1:].strip())
                else:
                    if result[current_section]:
                        result[current_section] += " " + line
                    else:
                        result[current_section] = line
        
        return result
    
    def _fallback_thesis_extraction(self, content: str, filename: str) -> Dict[str, Any]:
        """Fallback method for thesis extraction using keyword analysis"""
        
        # Simple keyword-based extraction
        thesis_keywords = ['recommend', 'buy', 'sell', 'hold', 'target', 'price', 'valuation']
        risk_keywords = ['risk', 'concern', 'challenge', 'threat', 'downside']
        metric_keywords = ['revenue', 'profit', 'margin', 'growth', 'eps', 'pe', 'ratio']
        
        content_lower = content.lower()
        
        # Extract potential thesis statements (sentences with key words)
        sentences = content.split('.')
        thesis_candidates = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in thesis_keywords):
                thesis_candidates.append(sentence.strip())
        
        thesis_statement = thesis_candidates[0] if thesis_candidates else "Investment thesis not clearly identified"
        
        # Extract risks and metrics similarly
        risk_factors = []
        target_metrics = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in risk_keywords):
                risk_factors.append(sentence.strip())
            if any(keyword in sentence.lower() for keyword in metric_keywords):
                target_metrics.append(sentence.strip())
        
        return {
            'thesis_statement': thesis_statement,
            'key_findings': thesis_candidates[:3],
            'investment_logic': "Extracted from document analysis",
            'risk_factors': risk_factors[:3],
            'target_metrics': target_metrics[:3],
            'document_summary': f"Analysis of {filename}",
            'confidence_score': 0.3
        }
    
    def validate_extracted_thesis(self, extracted_thesis: str, document_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the extracted thesis using full analysis pipeline"""
        try:
            # Run the thesis through our standard analysis pipeline
            analysis_result = self.analysis_service.analyze_thesis_comprehensive(extracted_thesis)
            
            # Extract Eagle API signals for additional validation
            eagle_signals = self.analysis_service.extract_eagle_signals_for_thesis(extracted_thesis)
            
            # Create validation report
            validation_report = self._create_validation_report(
                extracted_thesis, 
                analysis_result, 
                eagle_signals, 
                document_context
            )
            
            return {
                'success': True,
                'analysis_result': analysis_result,
                'eagle_signals': eagle_signals,
                'validation_report': validation_report
            }
            
        except Exception as e:
            logging.error(f"Error validating extracted thesis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis_result': {},
                'eagle_signals': [],
                'validation_report': {}
            }
    
    def _create_validation_report(self, thesis: str, analysis: Dict[str, Any], 
                                eagle_signals: List[Dict], document_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive validation report"""
        
        return {
            'executive_summary': {
                'thesis_statement': thesis,
                'extraction_confidence': document_context.get('confidence_score', 0.0),
                'analysis_quality': self._assess_analysis_quality(analysis),
                'signal_count': len(analysis.get('metrics_to_track', [])) + len(eagle_signals),
                'validation_timestamp': datetime.utcnow().isoformat()
            },
            'thesis_analysis': {
                'core_claim': analysis.get('core_claim', ''),
                'mental_model': analysis.get('mental_model', ''),
                'causal_chain': analysis.get('causal_chain', []),
                'assumptions': analysis.get('assumptions', [])
            },
            'signal_analysis': {
                'internal_signals': analysis.get('metrics_to_track', []),
                'external_signals': eagle_signals,
                'signal_classification': self._classify_signals(analysis.get('metrics_to_track', []), eagle_signals)
            },
            'document_validation': {
                'source_document': document_context.get('filename', 'Unknown'),
                'key_findings': document_context.get('key_findings', []),
                'risk_factors': document_context.get('risk_factors', []),
                'target_metrics': document_context.get('target_metrics', [])
            },
            'recommendations': self._generate_validation_recommendations(analysis, document_context),
            'next_steps': self._suggest_next_steps(analysis, eagle_signals)
        }
    
    def _assess_analysis_quality(self, analysis: Dict[str, Any]) -> str:
        """Assess the quality of the analysis"""
        score = 0
        
        if analysis.get('core_claim'):
            score += 25
        if analysis.get('causal_chain'):
            score += 25
        if analysis.get('assumptions'):
            score += 25
        if analysis.get('metrics_to_track'):
            score += 25
        
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _classify_signals(self, internal_signals: List[Dict], external_signals: List[Dict]) -> Dict[str, Any]:
        """Classify signals by type and priority"""
        classification = {
            'level_0': [],
            'level_1': [],
            'level_2': [],
            'level_3': [],
            'level_4': [],
            'level_5': [],
            'total_count': len(internal_signals) + len(external_signals)
        }
        
        # Classify internal signals
        for signal in internal_signals:
            level = signal.get('level', 'unknown')
            if level in classification:
                classification[level].append(signal)
        
        # Classify external signals (Eagle API)
        for signal in external_signals:
            # External signals are typically Level 1-2
            classification['level_1'].append(signal)
        
        return classification
    
    def _generate_validation_recommendations(self, analysis: Dict[str, Any], 
                                           document_context: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving the analysis"""
        recommendations = []
        
        confidence = document_context.get('confidence_score', 0.0)
        if confidence < 0.7:
            recommendations.append("Consider reviewing the source document for clearer thesis articulation")
        
        if not analysis.get('core_claim'):
            recommendations.append("Strengthen the core investment claim with more specific details")
        
        signal_count = len(analysis.get('metrics_to_track', []))
        if signal_count < 3:
            recommendations.append("Identify additional monitoring signals for comprehensive tracking")
        
        if not analysis.get('assumptions'):
            recommendations.append("Explicitly state key assumptions underlying the investment thesis")
        
        return recommendations
    
    def _suggest_next_steps(self, analysis: Dict[str, Any], eagle_signals: List[Dict]) -> List[str]:
        """Suggest next steps for thesis validation"""
        next_steps = []
        
        next_steps.append("Set up real-time monitoring for identified signals")
        next_steps.append("Establish threshold values for key performance indicators")
        
        if eagle_signals:
            next_steps.append("Validate external data sources and signal reliability")
        
        next_steps.append("Schedule periodic review of thesis assumptions")
        next_steps.append("Prepare contingency scenarios for risk factors")
        
        return next_steps
    
    def generate_analyst_report(self, validation_data: Dict[str, Any]) -> str:
        """Generate a formatted report for analyst validation"""
        
        report_sections = []
        
        # Executive Summary
        report_sections.append("# INVESTMENT THESIS VALIDATION REPORT")
        report_sections.append("=" * 50)
        report_sections.append("")
        
        exec_summary = validation_data.get('validation_report', {}).get('executive_summary', {})
        report_sections.append("## EXECUTIVE SUMMARY")
        report_sections.append(f"**Thesis Statement:** {exec_summary.get('thesis_statement', 'Not available')}")
        report_sections.append(f"**Extraction Confidence:** {exec_summary.get('extraction_confidence', 0.0):.1%}")
        report_sections.append(f"**Analysis Quality:** {exec_summary.get('analysis_quality', 'Unknown')}")
        report_sections.append(f"**Total Signals Identified:** {exec_summary.get('signal_count', 0)}")
        report_sections.append("")
        
        # Thesis Analysis
        thesis_analysis = validation_data.get('validation_report', {}).get('thesis_analysis', {})
        report_sections.append("## THESIS ANALYSIS")
        report_sections.append(f"**Core Claim:** {thesis_analysis.get('core_claim', 'Not identified')}")
        report_sections.append(f"**Mental Model:** {thesis_analysis.get('mental_model', 'Not identified')}")
        
        if thesis_analysis.get('assumptions'):
            report_sections.append("**Key Assumptions:**")
            for i, assumption in enumerate(thesis_analysis['assumptions'][:5], 1):
                report_sections.append(f"  {i}. {assumption}")
        report_sections.append("")
        
        # Signal Analysis
        signal_analysis = validation_data.get('validation_report', {}).get('signal_analysis', {})
        report_sections.append("## MONITORING SIGNALS")
        
        internal_signals = signal_analysis.get('internal_signals', [])
        if internal_signals:
            report_sections.append("**Internal Analysis Signals:**")
            for signal in internal_signals[:5]:
                signal_name = signal.get('signal_name', 'Unknown Signal')
                signal_type = signal.get('signal_type', 'Unknown')
                report_sections.append(f"  • {signal_name} ({signal_type})")
        
        external_signals = signal_analysis.get('external_signals', [])
        if external_signals:
            report_sections.append("**External Data Signals:**")
            for signal in external_signals[:5]:
                signal_name = signal.get('metric_name', 'Unknown Metric')
                source = signal.get('source', 'External')
                report_sections.append(f"  • {signal_name} ({source})")
        report_sections.append("")
        
        # Recommendations
        recommendations = validation_data.get('validation_report', {}).get('recommendations', [])
        if recommendations:
            report_sections.append("## RECOMMENDATIONS")
            for i, rec in enumerate(recommendations, 1):
                report_sections.append(f"{i}. {rec}")
            report_sections.append("")
        
        # Next Steps
        next_steps = validation_data.get('validation_report', {}).get('next_steps', [])
        if next_steps:
            report_sections.append("## NEXT STEPS")
            for i, step in enumerate(next_steps, 1):
                report_sections.append(f"{i}. {step}")
            report_sections.append("")
        
        # Footer
        report_sections.append("---")
        report_sections.append(f"Report generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        report_sections.append("Investment Thesis Intelligence System")
        
        return "\n".join(report_sections)