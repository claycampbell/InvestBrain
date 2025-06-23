"""
Smart Prioritization Engine
AI-powered ranking system for research elements and signal patterns
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from services.azure_openai_service import AzureOpenAIService

class SmartPrioritizationService:
    def __init__(self):
        self.ai_service = AzureOpenAIService()
    
    def generate_dual_prioritization(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate separate prioritization for research elements and signal patterns
        """
        try:
            # Analyze research importance
            research_priority = self._analyze_research_importance(thesis_analysis)
            
            # Analyze signal predictive value
            signal_priority = self._analyze_signal_strength(thesis_analysis)
            
            # Generate alignment analysis
            alignment_analysis = self._analyze_priority_alignment(research_priority, signal_priority)
            
            prioritization_result = {
                'research_prioritization': research_priority,
                'signal_prioritization': signal_priority,
                'alignment_analysis': alignment_analysis,
                'actionable_insights': self._generate_actionable_insights(research_priority, signal_priority, alignment_analysis),
                'priority_matrix': self._create_priority_matrix(research_priority, signal_priority)
            }
            
            return prioritization_result
            
        except Exception as e:
            return self._fallback_prioritization()
    
    def _analyze_research_importance(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and rank research elements by analytical importance"""
        try:
            research_elements = {
                'core_claim': thesis_analysis.get('core_claim', ''),
                'core_analysis': thesis_analysis.get('core_analysis', ''),
                'assumptions': thesis_analysis.get('assumptions', []),
                'mental_model': thesis_analysis.get('mental_model', ''),
                'causal_chain': thesis_analysis.get('causal_chain', [])
            }
            
            prompt = f"""
            Analyze the research quality and importance of these investment thesis elements.
            Rate each element's analytical value on these criteria:

            1. Depth of Analysis (1-10): How thorough and well-reasoned
            2. Data Foundation (1-10): Quality of supporting evidence  
            3. Logical Consistency (1-10): Internal coherence and reasoning
            4. Market Relevance (1-10): Connection to actual market dynamics
            5. Actionability (1-10): How useful for investment decisions

            Research Elements:
            {json.dumps(research_elements, indent=2)}

            Respond with JSON:
            {{
                "element_scores": {{
                    "core_claim": {{"depth": 0-10, "data_foundation": 0-10, "logical_consistency": 0-10, "market_relevance": 0-10, "actionability": 0-10, "overall_score": 0-10}},
                    "core_analysis": {{"depth": 0-10, "data_foundation": 0-10, "logical_consistency": 0-10, "market_relevance": 0-10, "actionability": 0-10, "overall_score": 0-10}},
                    "assumptions": {{"depth": 0-10, "data_foundation": 0-10, "logical_consistency": 0-10, "market_relevance": 0-10, "actionability": 0-10, "overall_score": 0-10}},
                    "mental_model": {{"depth": 0-10, "data_foundation": 0-10, "logical_consistency": 0-10, "market_relevance": 0-10, "actionability": 0-10, "overall_score": 0-10}},
                    "causal_chain": {{"depth": 0-10, "data_foundation": 0-10, "logical_consistency": 0-10, "market_relevance": 0-10, "actionability": 0-10, "overall_score": 0-10}}
                }},
                "priority_ranking": ["element1", "element2", "element3", "element4", "element5"],
                "research_quality_summary": "brief assessment of overall research quality"
            }}
            """
            
            response = self.ai_service.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2
            )
            
            return json.loads(response)
            
        except Exception:
            return self._fallback_research_priority()
    
    def _analyze_signal_strength(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and rank signal patterns by predictive value"""
        try:
            signals_data = {
                'metrics_to_track': thesis_analysis.get('metrics_to_track', []),
                'monitoring_plan': thesis_analysis.get('monitoring_plan', [])
            }
            
            prompt = f"""
            Analyze the predictive strength and market value of these investment signals.
            Rate each signal type on these criteria:

            1. Historical Accuracy (1-10): Track record of predictive success
            2. Market Correlation (1-10): Strength of connection to market movements
            3. Data Availability (1-10): Ease of obtaining reliable data
            4. Timeliness (1-10): How quickly signal provides actionable information
            5. Risk Warning Value (1-10): Ability to predict downside scenarios

            Signal Data:
            {json.dumps(signals_data, indent=2)}

            Respond with JSON:
            {{
                "signal_categories": {{
                    "financial_metrics": {{"historical_accuracy": 0-10, "market_correlation": 0-10, "data_availability": 0-10, "timeliness": 0-10, "risk_warning": 0-10, "overall_strength": 0-10}},
                    "market_indicators": {{"historical_accuracy": 0-10, "market_correlation": 0-10, "data_availability": 0-10, "timeliness": 0-10, "risk_warning": 0-10, "overall_strength": 0-10}},
                    "operational_metrics": {{"historical_accuracy": 0-10, "market_correlation": 0-10, "data_availability": 0-10, "timeliness": 0-10, "risk_warning": 0-10, "overall_strength": 0-10}},
                    "external_factors": {{"historical_accuracy": 0-10, "market_correlation": 0-10, "data_availability": 0-10, "timeliness": 0-10, "risk_warning": 0-10, "overall_strength": 0-10}}
                }},
                "signal_priority_ranking": ["category1", "category2", "category3", "category4"],
                "predictive_strength_summary": "brief assessment of overall signal reliability"
            }}
            """
            
            response = self.ai_service.generate_completion(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.2
            )
            
            return json.loads(response)
            
        except Exception:
            return self._fallback_signal_priority()
    
    def _analyze_priority_alignment(self, research_priority: Dict, signal_priority: Dict) -> Dict[str, Any]:
        """Analyze how research importance aligns with signal strength"""
        try:
            research_scores = research_priority.get('element_scores', {})
            signal_scores = signal_priority.get('signal_categories', {})
            
            # Calculate alignment metrics
            research_avg = self._calculate_average_scores(research_scores)
            signal_avg = self._calculate_average_scores(signal_scores)
            
            alignment_score = min(research_avg, signal_avg) / max(research_avg, signal_avg) if max(research_avg, signal_avg) > 0 else 0
            
            alignment_analysis = {
                'alignment_score': alignment_score,
                'research_strength': research_avg,
                'signal_strength': signal_avg,
                'balance_assessment': self._assess_balance(research_avg, signal_avg),
                'gap_analysis': self._identify_gaps(research_priority, signal_priority),
                'recommendations': self._generate_alignment_recommendations(research_avg, signal_avg, alignment_score)
            }
            
            return alignment_analysis
            
        except Exception:
            return {'alignment_score': 0.5, 'balance_assessment': 'unknown', 'gap_analysis': [], 'recommendations': []}
    
    def _calculate_average_scores(self, scores_dict: Dict) -> float:
        """Calculate average overall scores from nested scoring structure"""
        total_score = 0
        count = 0
        
        for element, scores in scores_dict.items():
            if isinstance(scores, dict) and 'overall_score' in scores:
                total_score += scores['overall_score']
                count += 1
            elif isinstance(scores, dict) and 'overall_strength' in scores:
                total_score += scores['overall_strength']
                count += 1
        
        return total_score / count if count > 0 else 0
    
    def _assess_balance(self, research_avg: float, signal_avg: float) -> str:
        """Assess the balance between research and signal strength"""
        diff = abs(research_avg - signal_avg)
        
        if diff < 1.0:
            return 'well_balanced'
        elif research_avg > signal_avg:
            return 'research_heavy'
        else:
            return 'signal_heavy'
    
    def _identify_gaps(self, research_priority: Dict, signal_priority: Dict) -> List[Dict]:
        """Identify gaps between research depth and signal coverage"""
        gaps = []
        
        research_scores = research_priority.get('element_scores', {})
        signal_scores = signal_priority.get('signal_categories', {})
        
        # Identify weak research areas
        for element, scores in research_scores.items():
            if isinstance(scores, dict) and scores.get('overall_score', 0) < 6:
                gaps.append({
                    'type': 'research_weakness',
                    'element': element,
                    'score': scores.get('overall_score', 0),
                    'priority': 'high' if scores.get('overall_score', 0) < 4 else 'medium'
                })
        
        # Identify weak signal areas
        for category, scores in signal_scores.items():
            if isinstance(scores, dict) and scores.get('overall_strength', 0) < 6:
                gaps.append({
                    'type': 'signal_weakness',
                    'category': category,
                    'strength': scores.get('overall_strength', 0),
                    'priority': 'high' if scores.get('overall_strength', 0) < 4 else 'medium'
                })
        
        return gaps
    
    def _generate_alignment_recommendations(self, research_avg: float, signal_avg: float, alignment_score: float) -> List[str]:
        """Generate recommendations for improving research-signal alignment"""
        recommendations = []
        
        if alignment_score < 0.7:
            recommendations.append("Consider strengthening the weaker dimension to improve overall analysis quality")
        
        if research_avg < 6:
            recommendations.append("Research foundation needs strengthening with more data and deeper analysis")
        
        if signal_avg < 6:
            recommendations.append("Signal monitoring system needs more reliable and predictive indicators")
        
        if abs(research_avg - signal_avg) > 2:
            recommendations.append("Large gap between research depth and signal strength - focus on balancing both areas")
        
        return recommendations
    
    def _generate_actionable_insights(self, research_priority: Dict, signal_priority: Dict, alignment_analysis: Dict) -> List[Dict]:
        """Generate specific actionable insights for users"""
        insights = []
        
        # Research-focused insights
        research_ranking = research_priority.get('priority_ranking', [])
        if research_ranking:
            insights.append({
                'type': 'research_focus',
                'priority': 'high',
                'title': f'Strengthen {research_ranking[0].replace("_", " ").title()}',
                'description': f'This is your strongest research element - consider expanding it further',
                'action': 'enhance_research'
            })
        
        # Signal-focused insights
        signal_ranking = signal_priority.get('signal_priority_ranking', [])
        if signal_ranking:
            insights.append({
                'type': 'signal_focus',
                'priority': 'high',
                'title': f'Monitor {signal_ranking[0].replace("_", " ").title()}',
                'description': f'This signal category has the highest predictive value',
                'action': 'enhance_monitoring'
            })
        
        # Alignment insights
        balance = alignment_analysis.get('balance_assessment', '')
        if balance == 'research_heavy':
            insights.append({
                'type': 'balance_adjustment',
                'priority': 'medium',
                'title': 'Strengthen Signal Monitoring',
                'description': 'Your research is strong but signals need improvement',
                'action': 'add_signals'
            })
        elif balance == 'signal_heavy':
            insights.append({
                'type': 'balance_adjustment',
                'priority': 'medium',
                'title': 'Deepen Research Analysis',
                'description': 'Your signals are good but research needs more depth',
                'action': 'expand_research'
            })
        
        return insights
    
    def _create_priority_matrix(self, research_priority: Dict, signal_priority: Dict) -> Dict[str, Any]:
        """Create a 2x2 priority matrix showing research vs signal strength"""
        research_avg = self._calculate_average_scores(research_priority.get('element_scores', {}))
        signal_avg = self._calculate_average_scores(signal_priority.get('signal_categories', {}))
        
        # Determine quadrant
        quadrant = ''
        if research_avg >= 7 and signal_avg >= 7:
            quadrant = 'high_research_high_signal'
        elif research_avg >= 7 and signal_avg < 7:
            quadrant = 'high_research_low_signal'
        elif research_avg < 7 and signal_avg >= 7:
            quadrant = 'low_research_high_signal'
        else:
            quadrant = 'low_research_low_signal'
        
        return {
            'quadrant': quadrant,
            'research_score': research_avg,
            'signal_score': signal_avg,
            'matrix_position': {
                'x': signal_avg / 10,  # Signal strength on X-axis
                'y': research_avg / 10  # Research quality on Y-axis
            },
            'quadrant_description': self._get_quadrant_description(quadrant)
        }
    
    def _get_quadrant_description(self, quadrant: str) -> str:
        """Get description for priority matrix quadrant"""
        descriptions = {
            'high_research_high_signal': 'Strong Foundation - Both research depth and signal reliability are excellent',
            'high_research_low_signal': 'Research Heavy - Strong analysis but weak monitoring system',
            'low_research_high_signal': 'Signal Heavy - Good monitoring but research needs strengthening',
            'low_research_low_signal': 'Development Needed - Both research and signals require improvement'
        }
        return descriptions.get(quadrant, 'Position unclear')
    
    def _fallback_research_priority(self) -> Dict[str, Any]:
        """Fallback research prioritization when AI analysis fails"""
        return {
            'element_scores': {
                'core_claim': {'overall_score': 7},
                'core_analysis': {'overall_score': 6},
                'assumptions': {'overall_score': 5},
                'mental_model': {'overall_score': 6},
                'causal_chain': {'overall_score': 5}
            },
            'priority_ranking': ['core_claim', 'core_analysis', 'mental_model', 'assumptions', 'causal_chain'],
            'research_quality_summary': 'Analysis unavailable - using baseline assessment'
        }
    
    def _fallback_signal_priority(self) -> Dict[str, Any]:
        """Fallback signal prioritization when AI analysis fails"""
        return {
            'signal_categories': {
                'financial_metrics': {'overall_strength': 7},
                'market_indicators': {'overall_strength': 6},
                'operational_metrics': {'overall_strength': 5},
                'external_factors': {'overall_strength': 4}
            },
            'signal_priority_ranking': ['financial_metrics', 'market_indicators', 'operational_metrics', 'external_factors'],
            'predictive_strength_summary': 'Analysis unavailable - using baseline assessment'
        }
    
    def _fallback_prioritization(self) -> Dict[str, Any]:
        """Complete fallback prioritization structure"""
        return {
            'research_prioritization': self._fallback_research_priority(),
            'signal_prioritization': self._fallback_signal_priority(),
            'alignment_analysis': {
                'alignment_score': 0.6,
                'balance_assessment': 'unknown',
                'gap_analysis': [],
                'recommendations': ['Enable AI analysis for detailed prioritization']
            },
            'actionable_insights': [],
            'priority_matrix': {
                'quadrant': 'low_research_low_signal',
                'research_score': 5.8,
                'signal_score': 5.5,
                'matrix_position': {'x': 0.55, 'y': 0.58},
                'quadrant_description': 'Analysis unavailable - baseline positioning'
            }
        }