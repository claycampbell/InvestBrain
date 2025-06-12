import logging
import json
from typing import Dict, Any, List
from services.azure_openai_service import AzureOpenAIService

class SignalClassifier:
    """
    Enhanced signal classification and extraction service
    """
    
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.signal_levels = {
            'economic': 'Macro-economic indicators and market conditions',
            'sector': 'Industry and sector-specific metrics',
            'company': 'Company-specific operational metrics',
            'technical': 'Price action and technical indicators',
            'sentiment': 'Market sentiment and positioning indicators'
        }
    
    def classify_and_extract_signals(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and classify signals from thesis analysis
        """
        try:
            if not self.openai_service.is_available():
                return self._extract_fallback_signals(thesis_analysis)
            
            # Extract signals using AI
            signals = self._extract_signals_from_ai_analysis(thesis_analysis)
            
            # Classify signals by level
            classified_signals = self._classify_signals_by_level(signals)
            
            # Assess programmatic feasibility
            feasibility_assessment = self._assess_programmatic_feasibility(classified_signals)
            
            return {
                'raw_signals': signals,
                'classified_signals': classified_signals,
                'feasibility_assessment': feasibility_assessment,
                'total_signals': len(signals),
                'feasible_signals': len([s for s in signals if s.get('programmatically_feasible', False)])
            }
            
        except Exception as e:
            logging.error(f"Error in signal classification: {str(e)}")
            return self._extract_fallback_signals(thesis_analysis)
    
    def _extract_signals_from_ai_analysis(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract signals using AI analysis
        """
        try:
            core_claim = thesis_analysis.get('core_claim', '')
            causal_chain = thesis_analysis.get('causal_chain', [])
            metrics_to_track = thesis_analysis.get('metrics_to_track', [])
            
            prompt = f"""Analyze this investment thesis and extract specific, measurable signals that can be monitored:

Core Claim: {core_claim}
Causal Chain: {json.dumps(causal_chain, indent=2)}
Metrics to Track: {json.dumps(metrics_to_track, indent=2)}

Extract 5-8 specific signals that meet these criteria:
1. Quantifiable and measurable
2. Available through public data sources
3. Directly related to thesis validation
4. Can be programmatically monitored

For each signal, provide:
- name: Descriptive name
- level: One of [economic, sector, company, technical, sentiment]
- description: What this signal measures
- threshold: Numeric threshold for triggering
- threshold_type: "above", "below", or "change_percent"
- data_source: Potential data source
- programmatically_feasible: true/false
- what_it_tells_us: How this validates/invalidates the thesis

Return as JSON array."""

            response = self.openai_service.generate_completion([
                {"role": "system", "content": "You are a quantitative analyst extracting measurable signals from investment theses."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            if response:
                try:
                    signals = json.loads(response)
                    return signals if isinstance(signals, list) else []
                except json.JSONDecodeError:
                    logging.error("Failed to parse AI response as JSON")
                    return self._generate_fallback_signals(thesis_analysis)
            
            return self._generate_fallback_signals(thesis_analysis)
            
        except Exception as e:
            logging.error(f"Error extracting signals from AI: {str(e)}")
            return self._generate_fallback_signals(thesis_analysis)
    
    def _classify_signals_by_level(self, signals: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Classify signals by their level (economic, sector, company, etc.)
        """
        classified = {level: [] for level in self.signal_levels.keys()}
        
        for signal in signals:
            level = signal.get('level', 'company').lower()
            if level in classified:
                classified[level].append(signal)
            else:
                classified['company'].append(signal)
        
        return classified
    
    def _assess_programmatic_feasibility(self, classified_signals: Dict[str, List]) -> Dict[str, Any]:
        """
        Assess the programmatic feasibility of monitoring signals
        """
        total_signals = sum(len(signals) for signals in classified_signals.values())
        feasible_signals = 0
        feasibility_by_level = {}
        
        for level, signals in classified_signals.items():
            level_feasible = len([s for s in signals if s.get('programmatically_feasible', False)])
            feasibility_by_level[level] = {
                'total': len(signals),
                'feasible': level_feasible,
                'feasibility_rate': level_feasible / len(signals) if signals else 0
            }
            feasible_signals += level_feasible
        
        return {
            'overall_feasibility_rate': feasible_signals / total_signals if total_signals > 0 else 0,
            'total_signals': total_signals,
            'feasible_signals': feasible_signals,
            'by_level': feasibility_by_level,
            'recommendations': self._generate_feasibility_recommendations(feasibility_by_level)
        }
    
    def _generate_feasibility_recommendations(self, feasibility_by_level: Dict) -> List[str]:
        """
        Generate recommendations for improving signal feasibility
        """
        recommendations = []
        
        for level, stats in feasibility_by_level.items():
            if stats['total'] > 0 and stats['feasibility_rate'] < 0.5:
                recommendations.append(f"Consider simplifying {level}-level signals for better monitoring")
        
        if not recommendations:
            recommendations.append("Signal set has good programmatic feasibility")
        
        return recommendations
    
    def _extract_fallback_signals(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback signals when AI is unavailable
        """
        signals = self._generate_fallback_signals(thesis_analysis)
        classified_signals = self._classify_signals_by_level(signals)
        feasibility_assessment = self._assess_programmatic_feasibility(classified_signals)
        
        return {
            'raw_signals': signals,
            'classified_signals': classified_signals,
            'feasibility_assessment': feasibility_assessment,
            'total_signals': len(signals),
            'feasible_signals': len([s for s in signals if s.get('programmatically_feasible', False)])
        }
    
    def _generate_fallback_signals(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate basic signals when AI analysis fails
        """
        core_claim = thesis_analysis.get('core_claim', 'Investment thesis')
        
        fallback_signals = [
            {
                'name': 'Quarterly Revenue Growth',
                'level': 'company',
                'description': 'Year-over-year quarterly revenue growth rate',
                'threshold': 10.0,
                'threshold_type': 'above',
                'data_source': 'Financial statements',
                'programmatically_feasible': True,
                'what_it_tells_us': 'Indicates business growth momentum'
            },
            {
                'name': 'Operating Margin',
                'level': 'company',
                'description': 'Operating income as percentage of revenue',
                'threshold': 15.0,
                'threshold_type': 'above',
                'data_source': 'Financial statements',
                'programmatically_feasible': True,
                'what_it_tells_us': 'Shows operational efficiency'
            },
            {
                'name': 'Free Cash Flow',
                'level': 'company',
                'description': 'Operating cash flow minus capital expenditures',
                'threshold': 0.05,
                'threshold_type': 'change_percent',
                'data_source': 'Cash flow statements',
                'programmatically_feasible': True,
                'what_it_tells_us': 'Measures cash generation ability'
            }
        ]
        
        return fallback_signals