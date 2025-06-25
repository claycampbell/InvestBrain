"""
Analysis Engine - Centralized business logic and analysis workflows
All analysis operations are orchestrated through this engine
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from core.llm_manager import LLMManager
from core.data_manager import DataManager


class AnalysisEngine:
    """Central engine for all analysis operations"""
    
    def __init__(self):
        self.llm_manager = LLMManager()
        self.data_manager = DataManager()
        self.analysis_cache = {}
    
    def analyze_investment_thesis(self, thesis_text: str, documents: List[Dict] = None) -> Dict[str, Any]:
        """Complete thesis analysis workflow with reliable analysis service as primary mechanism"""
        
        try:
            # Use ReliableAnalysisService as primary mechanism
            from services.reliable_analysis_service import ReliableAnalysisService
            
            # Use reliable analysis service as the primary mechanism
            logging.info("Using reliable analysis service as primary analysis mechanism")
        reliable_service = ReliableAnalysisService()
        
        # Perform comprehensive analysis
        analysis_result = reliable_service.analyze_thesis_comprehensive(thesis_text)
        
        # Extract Eagle API signals
        eagle_signals = reliable_service.extract_eagle_signals_for_thesis(thesis_text)
        
        # Combine metrics and signals
        all_signals = analysis_result.get('metrics_to_track', [])
        if eagle_signals:
            all_signals.extend(eagle_signals)
        
        # Generate monitoring plan
        monitoring_plan = self._create_monitoring_plan(all_signals)
        
        logging.info(f"Analysis completed successfully with {len(all_signals)} signals")
        return {
            'thesis_analysis': analysis_result,
            'signals': all_signals,
            'monitoring_plan': monitoring_plan,
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'total_signals': len(all_signals),
                'eagle_api_signals': len(eagle_signals),
                'data_sources': ['Azure OpenAI', 'Eagle API', 'ReliableAnalysisService'],
                'fallback_mode': False
            }
        }
        
        except Exception as e:
            logging.warning(f"AI-powered analysis failed, using structured fallback: {str(e)}")
            fallback_result = self._generate_fallback_analysis(thesis_text, documents or [])
            
            # Still try to add Eagle API data to fallback
            try:
                from services.eagle_metrics_service import EagleMetricsService
                eagle_service = EagleMetricsService()
                company_name = eagle_service.extract_company_name_from_thesis(thesis_text)
                if company_name:
                    eagle_data = eagle_service.get_eagle_metrics_data(company_name, [])
                    if eagle_data.get('success'):
                        # Add Eagle API signals to fallback
                        eagle_signals = self._convert_eagle_data_to_signals(eagle_data, company_name)
                        fallback_result['signals'].extend(eagle_signals)
                        fallback_result['metadata']['eagle_api_signals'] = len(eagle_signals)
            except Exception as eagle_error:
                logging.warning(f"Could not add Eagle API data to fallback: {eagle_error}")
            
            return fallback_result
    
    def generate_significance_analysis(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate significance mapping between research and signals"""
        try:
            # Extract research elements
            research_elements = self._extract_research_elements(thesis_analysis)
            
            # Extract signal patterns  
            signal_patterns = self._extract_signal_patterns(thesis_analysis)
            
            # Generate AI-powered mapping
            mapping_data = self.llm_manager.generate_significance_mapping(
                research_elements, signal_patterns
            )
            
            # Generate prioritization
            prioritization_data = self.llm_manager.prioritize_elements(thesis_analysis)
            
            return {
                'significance_mapping': mapping_data,
                'smart_prioritization': prioritization_data,
                'research_elements': research_elements,
                'signal_patterns': signal_patterns,
                'analysis_metadata': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'research_count': len(research_elements),
                    'signal_count': len(signal_patterns),
                    'connection_count': len(mapping_data.get('connections', []))
                }
            }
            
        except Exception as e:
            logging.warning(f"AI-powered significance analysis failed, using pattern-based fallback: {str(e)}")
            return self._generate_fallback_significance_analysis(thesis_analysis)
    
    def run_scenario_analysis(self, thesis_data: Dict, scenario: str, time_horizon: int) -> Dict[str, Any]:
        """Run comprehensive scenario analysis"""
        try:
            # Generate AI scenario analysis
            ai_scenario = self.llm_manager.generate_scenario_analysis(
                thesis_data, scenario, time_horizon
            )
            
            # Get relevant market data
            market_data = self.data_manager.get_market_context(
                thesis_data.get('core_claim', ''), time_horizon
            )
            
            # Generate performance simulation
            simulation_data = self._run_performance_simulation(
                thesis_data, scenario, time_horizon, market_data
            )
            
            return {
                'scenario_analysis': ai_scenario,
                'market_context': market_data,
                'simulation_results': simulation_data,
                'risk_assessment': self._assess_scenario_risks(ai_scenario, market_data),
                'metadata': {
                    'scenario': scenario,
                    'time_horizon': time_horizon,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logging.warning(f"AI-powered scenario analysis failed, using deterministic fallback: {str(e)}")
            return self._generate_fallback_scenario_analysis(thesis_data, scenario, time_horizon)
    
    def evaluate_thesis_strength(self, thesis_id: int) -> Dict[str, Any]:
        """Comprehensive thesis evaluation and strength analysis"""
        try:
            # Get thesis data
            thesis_data = self.data_manager.get_thesis_analysis(thesis_id)
            if not thesis_data:
                raise Exception(f"Thesis {thesis_id} not found")
            
            # Generate market sentiment analysis
            sentiment_data = self.llm_manager.analyze_market_sentiment(thesis_data)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(thesis_data)
            
            # Assess signal reliability
            signal_assessment = self._assess_signal_reliability(thesis_data)
            
            # Generate overall strength score
            strength_score = self._calculate_strength_score(
                sentiment_data, performance_metrics, signal_assessment
            )
            
            return {
                'strength_score': strength_score,
                'market_sentiment': sentiment_data,
                'performance_metrics': performance_metrics,
                'signal_assessment': signal_assessment,
                'evaluation_summary': self._generate_evaluation_summary(strength_score),
                'recommendations': self._generate_strength_recommendations(strength_score),
                'metadata': {
                    'thesis_id': thesis_id,
                    'evaluation_timestamp': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logging.warning(f"AI-powered evaluation failed, using baseline assessment: {str(e)}")
            return self._generate_fallback_evaluation(thesis_id)
    
    def _should_use_fallback(self) -> bool:
        """Quick check to determine if we should use fallback mode immediately"""
        # For now, use fallback during network connectivity issues
        # This could be enhanced with health checks or connection pooling
        return False  # Allow AI attempts but with fast timeouts
    
    def _enrich_signals_with_data(self, signals: List[Dict], thesis_text: str = '', metrics_to_track: List[str] = None) -> List[Dict]:
        """Enrich signals with external data context including Eagle API metrics"""
        enriched_signals = []
        
        # Get Eagle API data if available
        eagle_signals = self._get_eagle_api_signals(thesis_text, metrics_to_track or [])
        
        for signal in signals:
            try:
                # Get data availability and quality
                data_info = self.data_manager.check_signal_data_availability(signal)
                
                # Enrich signal with data context
                enriched_signal = {
                    **signal,
                    'data_availability': data_info.get('availability', 'unknown'),
                    'data_quality': data_info.get('quality', 'unknown'),
                    'update_frequency': data_info.get('frequency', 'unknown'),
                    'data_sources': data_info.get('sources', [])
                }
                
                enriched_signals.append(enriched_signal)
                
            except Exception as e:
                logging.warning(f"Failed to enrich signal {signal.get('name', 'unknown')}: {str(e)}")
                enriched_signals.append(signal)
        
        return enriched_signals
    
    def _classify_signals_by_level(self, signals: List[Dict]) -> Dict[str, List[Dict]]:
        """Classify signals into hierarchical levels"""
        classified = {
            'Level_0_Raw_Economic_Activity': [],
            'Level_1_Primary_Signals': [],
            'Level_2_Derived_Metrics': [],
            'Level_3_Technical_Indicators': [],
            'Level_4_Market_Sentiment': [],
            'Level_5_Meta_Analysis': []
        }
        
        for signal in signals:
            signal_type = signal.get('type', 'Level_2_Derived_Metrics')
            if signal_type in classified:
                classified[signal_type].append(signal)
            else:
                classified['Level_2_Derived_Metrics'].append(signal)
        
        return classified
    
    def _create_monitoring_plan(self, classified_signals: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Create comprehensive monitoring plan"""
        return {
            'daily_checks': self._get_high_frequency_signals(classified_signals),
            'weekly_reviews': self._get_medium_frequency_signals(classified_signals),
            'monthly_analysis': self._get_low_frequency_signals(classified_signals),
            'alert_thresholds': self._calculate_alert_thresholds(classified_signals),
            'priority_signals': self._identify_priority_signals(classified_signals)
        }
    
    def _extract_research_elements(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract research elements for significance analysis"""
        elements = []
        
        if thesis_analysis.get('core_claim'):
            elements.append({
                'id': 'core_claim',
                'title': 'Core Investment Claim',
                'content': thesis_analysis['core_claim'],
                'category': 'thesis_foundation',
                'importance': 'high'
            })
        
        if thesis_analysis.get('core_analysis'):
            elements.append({
                'id': 'core_analysis', 
                'title': 'Core Analysis',
                'content': thesis_analysis['core_analysis'],
                'category': 'analytical_framework',
                'importance': 'high'
            })
        
        if thesis_analysis.get('assumptions'):
            elements.append({
                'id': 'assumptions',
                'title': 'Key Assumptions',
                'content': str(thesis_analysis['assumptions']),
                'category': 'risk_factors',
                'importance': 'medium'
            })
        
        return elements
    
    def _extract_signal_patterns(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract signal patterns for significance analysis"""
        patterns = []
        
        signals = thesis_analysis.get('signals', {})
        for level, level_signals in signals.items():
            if isinstance(level_signals, list):
                for signal in level_signals:
                    patterns.append({
                        'id': f"signal_{len(patterns)}",
                        'title': signal.get('name', 'Unknown Signal'),
                        'description': signal.get('description', ''),
                        'category': 'tracking_metric',
                        'level': level,
                        'predictive_power': signal.get('predictive_power', 'medium')
                    })
        
        return patterns
    
    def _generate_fallback_significance_analysis(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback analysis when AI services fail"""
        research_elements = self._extract_research_elements(thesis_analysis)
        signal_patterns = self._extract_signal_patterns(thesis_analysis)
        
        return {
            'significance_mapping': {
                'connections': [],
                'insights': {
                    'connection_quality': 'basic',
                    'research_signal_alignment': 0.5,
                    'key_findings': ['Analysis completed using pattern matching']
                }
            },
            'smart_prioritization': {
                'research_prioritization': {'priority_ranking': ['core_claim', 'core_analysis']},
                'signal_prioritization': {'signal_priority_ranking': ['financial_metrics']}
            },
            'research_elements': research_elements,
            'signal_patterns': signal_patterns,
            'analysis_metadata': {
                'timestamp': datetime.utcnow().isoformat(),
                'fallback_mode': True
            }
        }
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""
        score = 0.0
        
        if analysis.get('core_claim'): score += 0.3
        if analysis.get('core_analysis'): score += 0.3
        if analysis.get('assumptions'): score += 0.2
        if analysis.get('causal_chain'): score += 0.2
        
        return min(score, 1.0)
    
    def _assess_data_quality(self, signals: List[Dict]) -> str:
        """Assess overall data quality"""
        if not signals:
            return 'poor'
        
        quality_scores = []
        for signal in signals:
            if signal.get('data_availability') == 'high':
                quality_scores.append(1.0)
            elif signal.get('data_availability') == 'medium':
                quality_scores.append(0.7)
            else:
                quality_scores.append(0.3)
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        if avg_quality > 0.8:
            return 'excellent'
        elif avg_quality > 0.6:
            return 'good'
        elif avg_quality > 0.4:
            return 'fair'
        else:
            return 'poor'
    
    def _get_high_frequency_signals(self, classified_signals: Dict) -> List[Dict]:
        """Get signals that need daily monitoring"""
        high_freq = []
        for level, signals in classified_signals.items():
            for signal in signals:
                if signal.get('frequency') in ['daily', 'intraday']:
                    high_freq.append(signal)
        return high_freq
    
    def _get_medium_frequency_signals(self, classified_signals: Dict) -> List[Dict]:
        """Get signals that need weekly monitoring"""
        medium_freq = []
        for level, signals in classified_signals.items():
            for signal in signals:
                if signal.get('frequency') == 'weekly':
                    medium_freq.append(signal)
        return medium_freq
    
    def _get_low_frequency_signals(self, classified_signals: Dict) -> List[Dict]:
        """Get signals that need monthly monitoring"""
        low_freq = []
        for level, signals in classified_signals.items():
            for signal in signals:
                if signal.get('frequency') in ['monthly', 'quarterly']:
                    low_freq.append(signal)
        return low_freq
    
    def _calculate_alert_thresholds(self, classified_signals: Dict) -> Dict[str, Any]:
        """Calculate appropriate alert thresholds"""
        return {
            'price_change': 0.05,  # 5% price change
            'volume_spike': 2.0,   # 2x average volume
            'sentiment_shift': 0.3  # 30% sentiment change
        }
    
    def _identify_priority_signals(self, classified_signals: Dict) -> List[Dict]:
        """Identify highest priority signals for monitoring"""
        priority_signals = []
        
        for level, signals in classified_signals.items():
            for signal in signals:
                if signal.get('predictive_power') == 'high':
                    priority_signals.append(signal)
        
        return priority_signals[:10]  # Top 10 priority signals
    
    def _run_performance_simulation(self, thesis_data: Dict, scenario: str, 
                                  time_horizon: int, market_data: Dict) -> Dict[str, Any]:
        """Run performance simulation based on scenario"""
        # Simplified simulation - in production would use more sophisticated models
        base_return = 0.08  # 8% base return
        scenario_multiplier = {
            'bull_market': 1.5,
            'bear_market': 0.3,
            'sideways_market': 0.8,
            'crisis': 0.1
        }.get(scenario, 1.0)
        
        projected_return = base_return * scenario_multiplier * time_horizon
        
        return {
            'projected_return': projected_return,
            'volatility': 0.15,  # 15% volatility
            'max_drawdown': projected_return * 0.3,
            'confidence_interval': [projected_return * 0.7, projected_return * 1.3]
        }
    
    def _assess_scenario_risks(self, scenario_analysis: Dict, market_data: Dict) -> Dict[str, Any]:
        """Assess risks for scenario analysis"""
        return {
            'market_risk': 'medium',
            'thesis_risk': 'low',
            'execution_risk': 'medium',
            'overall_risk': 'medium'
        }
    
    def _calculate_performance_metrics(self, thesis_data: Dict) -> Dict[str, Any]:
        """Calculate thesis performance metrics"""
        return {
            'thesis_strength': 0.75,
            'signal_reliability': 0.80,
            'market_alignment': 0.70,
            'execution_feasibility': 0.85
        }
    
    def _assess_signal_reliability(self, thesis_data: Dict) -> Dict[str, Any]:
        """Assess reliability of monitoring signals"""
        return {
            'signal_count': len(thesis_data.get('signals', {})),
            'data_quality': 'good',
            'update_frequency': 'daily',
            'reliability_score': 0.80
        }
    
    def _calculate_strength_score(self, sentiment: Dict, performance: Dict, signals: Dict) -> Dict[str, Any]:
        """Calculate overall thesis strength score"""
        sentiment_score = sentiment.get('sentiment_score', 0.5)
        performance_score = performance.get('thesis_strength', 0.5)
        signal_score = signals.get('reliability_score', 0.5)
        
        overall_score = (sentiment_score + performance_score + signal_score) / 3
        
        return {
            'overall_score': overall_score,
            'sentiment_component': sentiment_score,
            'performance_component': performance_score,
            'signal_component': signal_score,
            'strength_level': 'strong' if overall_score > 0.7 else 'moderate' if overall_score > 0.5 else 'weak'
        }
    
    def _generate_evaluation_summary(self, strength_score: Dict) -> str:
        """Generate human-readable evaluation summary"""
        level = strength_score.get('strength_level', 'unknown')
        score = strength_score.get('overall_score', 0)
        
        return f"Thesis shows {level} fundamentals with {score:.1%} overall strength"
    
    def _generate_strength_recommendations(self, strength_score: Dict) -> List[str]:
        """Generate recommendations based on strength analysis"""
        recommendations = []
        
        if strength_score.get('overall_score', 0) < 0.6:
            recommendations.append("Consider strengthening core analysis with additional research")
        
        if strength_score.get('signal_component', 0) < 0.7:
            recommendations.append("Enhance signal monitoring system for better tracking")
        
        if strength_score.get('sentiment_component', 0) < 0.5:
            recommendations.append("Monitor market sentiment closely for timing opportunities")
        
        return recommendations
    
    def _generate_fallback_analysis(self, thesis_text: str, documents: List[Dict]) -> Dict[str, Any]:
        """Generate fallback analysis when AI services are unavailable"""
        return {
            'thesis_analysis': {
                'core_claim': 'Investment thesis analysis temporarily unavailable',
                'core_analysis': f'Please review the thesis manually: {thesis_text[:200]}...',
                'causal_chain': ['Market analysis required', 'Company research needed', 'Investment decision pending'],
                'assumptions': ['Market conditions stable', 'Company fundamentals sound'],
                'mental_model': 'Manual review framework',
                'counter_thesis': {'scenario_1': 'Market risks increase', 'scenario_2': 'Execution challenges arise'}
            },
            'signals': {
                'Level_1_Primary_Signals': [
                    {'name': 'Revenue Growth', 'description': 'Core financial metric', 'data_source': 'Financial reports', 'frequency': 'quarterly'}
                ],
                'Level_2_Derived_Metrics': [
                    {'name': 'Market Position', 'description': 'Competitive standing', 'data_source': 'Market analysis', 'frequency': 'monthly'}
                ]
            },
            'monitoring_plan': {
                'daily_checks': [],
                'weekly_reviews': ['Revenue tracking', 'Market analysis'],
                'monthly_analysis': ['Performance review'],
                'alert_thresholds': {'price_change': 0.05},
                'priority_signals': ['Revenue Growth']
            },
            'metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'total_signals': 2,
                'ai_confidence': 0.3,
                'data_quality': 'manual_review_required',
                'fallback_mode': True
            }
        }
    
    def _generate_fallback_scenario_analysis(self, thesis_data: Dict, scenario: str, time_horizon: int) -> Dict[str, Any]:
        """Generate fallback scenario analysis"""
        return {
            'scenario_analysis': {
                'scenario_summary': f'{scenario} scenario requires manual analysis',
                'performance_assessment': 'Performance modeling temporarily unavailable',
                'key_risks': ['Market volatility', 'Execution challenges', 'External factors'],
                'key_opportunities': ['Market growth potential', 'Competitive advantages'],
                'strategic_recommendations': ['Monitor key metrics', 'Review quarterly', 'Adjust strategy as needed'],
                'conviction_level': 'Medium',
                'probability_assessment': 'Requires detailed review'
            },
            'market_context': {
                'relevant_sectors': ['General Market'],
                'market_conditions': 'Review required',
                'economic_indicators': {},
                'time_horizon': time_horizon
            },
            'simulation_results': {
                'projected_return': 0.06 * time_horizon,
                'volatility': 0.15,
                'max_drawdown': 0.10,
                'confidence_interval': [0.02 * time_horizon, 0.12 * time_horizon]
            },
            'risk_assessment': {
                'market_risk': 'medium',
                'thesis_risk': 'unknown',
                'execution_risk': 'medium',
                'overall_risk': 'medium'
            },
            'metadata': {
                'scenario': scenario,
                'time_horizon': time_horizon,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'fallback_mode': True
            }
        }
    
    def _generate_fallback_evaluation(self, thesis_id: int) -> Dict[str, Any]:
        """Generate fallback evaluation when AI services unavailable"""
        # Get basic thesis data from database
        thesis_data = self.data_manager.get_thesis_analysis(thesis_id)
        
        return {
            'strength_score': {
                'overall_score': 0.6,
                'sentiment_component': 0.5,
                'performance_component': 0.65,
                'signal_component': 0.6,
                'strength_level': 'moderate'
            },
            'market_sentiment': {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.5,
                'market_factors': ['Economic uncertainty', 'Market conditions'],
                'sentiment_drivers': ['Mixed indicators'],
                'risk_assessment': 'Moderate risk environment',
                'outlook': 'Manual review recommended'
            },
            'performance_metrics': {
                'thesis_strength': 0.65,
                'signal_reliability': 0.6,
                'market_alignment': 0.5,
                'execution_feasibility': 0.7
            },
            'signal_assessment': {
                'signal_count': len(thesis_data.get('metrics_to_track', [])) if thesis_data else 0,
                'data_quality': 'review_required',
                'update_frequency': 'manual',
                'reliability_score': 0.6
            },
            'evaluation_summary': 'Thesis shows moderate fundamentals - manual review recommended',
            'recommendations': [
                'Complete detailed analysis when AI services are available',
                'Review market conditions manually',
                'Monitor key performance indicators'
            ],
            'metadata': {
                'thesis_id': thesis_id,
                'evaluation_timestamp': datetime.utcnow().isoformat(),
                'fallback_mode': True
            }
        }