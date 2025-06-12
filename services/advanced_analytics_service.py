import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from services.azure_openai_service import AzureOpenAIService
from models import ThesisAnalysis, SignalMonitoring, NotificationLog
from app import db

class AdvancedAnalyticsService:
    """
    Advanced analytics and intelligence for investment thesis analysis
    """
    
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.logger = logging.getLogger(__name__)
    
    def calculate_thesis_performance_score(self, thesis_id: int) -> Dict[str, Any]:
        """
        Calculate real-time conviction scoring based on signal confirmation and market validation
        """
        try:
            thesis = ThesisAnalysis.query.get(thesis_id)
            if not thesis:
                return {'error': 'Thesis not found'}
            
            # Get all signals for this thesis
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis_id).all()
            
            # Calculate signal confirmation rate
            signal_confirmation_rate = self._calculate_signal_confirmation_rate(signals)
            
            # Calculate market validation score
            market_validation_score = self._calculate_market_validation_score(thesis, signals)
            
            # Calculate time-weighted performance
            time_weighted_score = self._calculate_time_weighted_performance(thesis, signals)
            
            # Calculate momentum indicators
            momentum_score = self._calculate_momentum_indicators(signals)
            
            # Aggregate overall performance score
            overall_score = self._aggregate_performance_scores({
                'signal_confirmation': signal_confirmation_rate,
                'market_validation': market_validation_score,
                'time_weighted': time_weighted_score,
                'momentum': momentum_score
            })
            
            return {
                'thesis_id': thesis_id,
                'overall_score': overall_score,
                'components': {
                    'signal_confirmation_rate': signal_confirmation_rate,
                    'market_validation_score': market_validation_score,
                    'time_weighted_score': time_weighted_score,
                    'momentum_score': momentum_score
                },
                'performance_tier': self._determine_performance_tier(overall_score),
                'confidence_level': self._calculate_confidence_level(overall_score, len(signals)),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Performance scoring failed for thesis {thesis_id}: {str(e)}")
            return {'error': str(e)}
    
    def detect_cross_thesis_patterns(self, user_theses_ids: List[int] = None) -> Dict[str, Any]:
        """
        AI detection of recurring patterns across successful/failed investment theses
        """
        try:
            # Get all theses for pattern analysis
            if user_theses_ids:
                theses = ThesisAnalysis.query.filter(ThesisAnalysis.id.in_(user_theses_ids)).all()
            else:
                theses = ThesisAnalysis.query.limit(50).all()  # Analyze recent theses
            
            if len(theses) < 3:
                return {'error': 'Insufficient thesis data for pattern detection'}
            
            # Categorize theses by performance
            thesis_performance_data = []
            for thesis in theses:
                performance_score = self.calculate_thesis_performance_score(thesis.id)
                if 'error' not in performance_score:
                    thesis_performance_data.append({
                        'thesis': thesis,
                        'performance': performance_score
                    })
            
            # Detect patterns using AI analysis
            patterns = self._analyze_success_failure_patterns(thesis_performance_data)
            
            # Identify recurring themes
            recurring_themes = self._identify_recurring_themes(thesis_performance_data)
            
            # Generate pattern insights
            pattern_insights = self._generate_pattern_insights(patterns, recurring_themes)
            
            return {
                'total_theses_analyzed': len(thesis_performance_data),
                'success_patterns': patterns.get('success_patterns', []),
                'failure_patterns': patterns.get('failure_patterns', []),
                'recurring_themes': recurring_themes,
                'pattern_insights': pattern_insights,
                'confidence_score': self._calculate_pattern_confidence(patterns),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Cross-thesis pattern detection failed: {str(e)}")
            return {'error': str(e)}
    
    def predict_signal_strength(self, thesis_id: int) -> Dict[str, Any]:
        """
        Machine learning models to predict which signals are most likely to trigger first
        """
        try:
            thesis = ThesisAnalysis.query.get(thesis_id)
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis_id).all()
            
            if not signals:
                return {'error': 'No signals found for prediction'}
            
            # Calculate signal velocity and momentum
            signal_predictions = []
            for signal in signals:
                prediction = self._predict_individual_signal_strength(signal, thesis)
                signal_predictions.append(prediction)
            
            # Rank signals by trigger probability
            ranked_signals = sorted(signal_predictions, key=lambda x: x['trigger_probability'], reverse=True)
            
            # Generate predictive insights
            predictive_insights = self._generate_predictive_insights(ranked_signals, thesis)
            
            return {
                'thesis_id': thesis_id,
                'signal_predictions': ranked_signals[:10],  # Top 10 most likely
                'next_trigger_estimate': self._estimate_next_trigger_timing(ranked_signals),
                'predictive_insights': predictive_insights,
                'model_confidence': self._calculate_prediction_confidence(ranked_signals),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Signal strength prediction failed for thesis {thesis_id}: {str(e)}")
            return {'error': str(e)}
    
    def analyze_sector_rotation_intelligence(self, thesis_id: int) -> Dict[str, Any]:
        """
        Automated detection of sector momentum shifts affecting thesis validity
        """
        try:
            thesis = ThesisAnalysis.query.get(thesis_id)
            if not thesis:
                return {'error': 'Thesis not found'}
            
            # Extract sector from thesis
            sector_info = self._extract_sector_information(thesis)
            
            # Analyze sector momentum using AI
            sector_analysis = self._analyze_sector_momentum(sector_info, thesis)
            
            # Detect rotation patterns
            rotation_patterns = self._detect_rotation_patterns(sector_info)
            
            # Calculate thesis vulnerability to sector shifts
            vulnerability_assessment = self._assess_sector_vulnerability(thesis, sector_analysis)
            
            return {
                'thesis_id': thesis_id,
                'sector_info': sector_info,
                'sector_momentum': sector_analysis,
                'rotation_patterns': rotation_patterns,
                'vulnerability_assessment': vulnerability_assessment,
                'recommended_actions': self._generate_sector_recommendations(vulnerability_assessment),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sector rotation analysis failed for thesis {thesis_id}: {str(e)}")
            return {'error': str(e)}
    
    def generate_comprehensive_analytics_dashboard(self, thesis_ids: List[int]) -> Dict[str, Any]:
        """
        Generate comprehensive analytics dashboard combining all intelligence features
        """
        try:
            dashboard_data = {
                'overview': {
                    'total_theses': len(thesis_ids),
                    'analysis_timestamp': datetime.utcnow().isoformat()
                },
                'performance_scores': {},
                'cross_thesis_patterns': {},
                'signal_predictions': {},
                'sector_intelligence': {}
            }
            
            # Calculate performance scores for all theses
            for thesis_id in thesis_ids:
                dashboard_data['performance_scores'][thesis_id] = self.calculate_thesis_performance_score(thesis_id)
            
            # Analyze cross-thesis patterns
            dashboard_data['cross_thesis_patterns'] = self.detect_cross_thesis_patterns(thesis_ids)
            
            # Generate signal predictions for top performing theses
            top_theses = sorted(thesis_ids, key=lambda tid: 
                dashboard_data['performance_scores'][tid].get('overall_score', 0), reverse=True)[:5]
            
            for thesis_id in top_theses:
                dashboard_data['signal_predictions'][thesis_id] = self.predict_signal_strength(thesis_id)
                dashboard_data['sector_intelligence'][thesis_id] = self.analyze_sector_rotation_intelligence(thesis_id)
            
            # Generate summary insights
            dashboard_data['summary_insights'] = self._generate_dashboard_insights(dashboard_data)
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Comprehensive analytics dashboard generation failed: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _calculate_signal_confirmation_rate(self, signals: List) -> float:
        """Calculate rate of signal confirmations vs triggers"""
        if not signals:
            return 0.0
        
        triggered_signals = len([s for s in signals if s.status == 'triggered'])
        return min(triggered_signals / len(signals), 1.0) * 100
    
    def _calculate_market_validation_score(self, thesis: ThesisAnalysis, signals: List) -> float:
        """Calculate market validation based on thesis age and signal activity"""
        thesis_age_days = (datetime.utcnow() - thesis.created_at).days
        if thesis_age_days == 0:
            return 50.0  # Neutral for new theses
        
        signal_activity = len([s for s in signals if s.last_checked and 
                              (datetime.utcnow() - s.last_checked).days <= 7])
        
        # Higher score for more recent signal activity relative to thesis age
        validation_score = min((signal_activity / max(thesis_age_days / 30, 1)) * 100, 100)
        return validation_score
    
    def _calculate_time_weighted_performance(self, thesis: ThesisAnalysis, signals: List) -> float:
        """Calculate performance weighted by time since thesis creation"""
        thesis_age_days = (datetime.utcnow() - thesis.created_at).days
        if thesis_age_days <= 0:
            return 50.0
        
        # Recent signals weighted more heavily
        recent_activity = len([s for s in signals if s.last_checked and 
                              (datetime.utcnow() - s.last_checked).days <= 30])
        
        time_weight = max(1.0 - (thesis_age_days / 365), 0.1)  # Decay over a year
        return min(recent_activity * time_weight * 20, 100)
    
    def _calculate_momentum_indicators(self, signals: List) -> float:
        """Calculate momentum based on recent signal triggers"""
        recent_triggers = len([s for s in signals if s.status == 'triggered' and s.last_checked and
                              (datetime.utcnow() - s.last_checked).days <= 14])
        
        return min(recent_triggers * 25, 100)  # Max score for 4+ recent triggers
    
    def _aggregate_performance_scores(self, scores: Dict[str, float]) -> float:
        """Aggregate component scores into overall performance score"""
        weights = {
            'signal_confirmation': 0.3,
            'market_validation': 0.25,
            'time_weighted': 0.25,
            'momentum': 0.2
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in scores.keys() if key in weights)
        return round(weighted_score, 2)
    
    def _determine_performance_tier(self, score: float) -> str:
        """Determine performance tier based on overall score"""
        if score >= 80:
            return "High Conviction"
        elif score >= 60:
            return "Medium Conviction"
        elif score >= 40:
            return "Low Conviction"
        else:
            return "Under Review"
    
    def _calculate_confidence_level(self, score: float, signal_count: int) -> float:
        """Calculate confidence level based on score and signal diversity"""
        base_confidence = score / 100
        signal_diversity_factor = min(signal_count / 5, 1.0)  # Max confidence with 5+ signals
        return round(base_confidence * signal_diversity_factor, 3)
    
    def _analyze_success_failure_patterns(self, thesis_data: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in successful vs failed theses using AI"""
        try:
            # Categorize theses by performance
            high_performers = [t for t in thesis_data if t['performance']['overall_score'] >= 70]
            low_performers = [t for t in thesis_data if t['performance']['overall_score'] <= 40]
            
            if len(high_performers) < 2 or len(low_performers) < 2:
                return {'success_patterns': [], 'failure_patterns': []}
            
            # Generate AI analysis of patterns
            success_prompt = f"""
            Analyze these high-performing investment theses and identify common success patterns:
            
            High Performers: {json.dumps([self._thesis_to_analysis_summary(t['thesis']) for t in high_performers[:5]], indent=2)}
            
            Identify 3-5 specific patterns that contribute to success. Focus on:
            - Common thesis structures
            - Signal types that perform well
            - Timing and sector patterns
            - Risk management approaches
            
            Return JSON: {{"success_patterns": [{"pattern": "description", "frequency": "how often seen", "impact": "why it matters"}]}}
            """
            
            success_response = self.openai_service.generate_completion([{"role": "user", "content": success_prompt}], temperature=0.3)
            success_patterns = self._parse_json_response(success_response, "success_patterns")
            
            failure_prompt = f"""
            Analyze these low-performing investment theses and identify common failure patterns:
            
            Low Performers: {json.dumps([self._thesis_to_analysis_summary(t['thesis']) for t in low_performers[:5]], indent=2)}
            
            Identify 3-5 specific patterns that lead to underperformance. Focus on:
            - Common weaknesses in thesis structure
            - Signal types that consistently fail
            - Timing and market condition patterns
            - Risk factors that were overlooked
            
            Return JSON: {{"failure_patterns": [{"pattern": "description", "frequency": "how often seen", "risk": "why it's problematic"}]}}
            """
            
            failure_response = self.openai_service.generate_completion([{"role": "user", "content": failure_prompt}], temperature=0.3)
            failure_patterns = self._parse_json_response(failure_response, "failure_patterns")
            
            return {
                'success_patterns': success_patterns.get('success_patterns', []),
                'failure_patterns': failure_patterns.get('failure_patterns', [])
            }
            
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {str(e)}")
            return {'success_patterns': [], 'failure_patterns': []}
    
    def _identify_recurring_themes(self, thesis_data: List[Dict]) -> List[Dict[str, Any]]:
        """Identify recurring themes across theses"""
        try:
            themes_prompt = f"""
            Analyze these investment theses and identify recurring themes and sectors:
            
            Theses Summary: {json.dumps([self._thesis_to_analysis_summary(t['thesis']) for t in thesis_data[:10]], indent=2)}
            
            Identify recurring themes including:
            - Sector concentrations
            - Common investment rationales
            - Shared risk factors
            - Similar signal types
            
            Return JSON: {{"themes": [{"theme": "name", "frequency": "count", "avg_performance": "score", "description": "details"}]}}
            """
            
            response = self.openai_service.generate_completion([{"role": "user", "content": themes_prompt}], temperature=0.4)
            themes_data = self._parse_json_response(response, "themes")
            
            return themes_data.get('themes', [])
            
        except Exception as e:
            self.logger.error(f"Theme identification failed: {str(e)}")
            return []
    
    def _thesis_to_analysis_summary(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Convert thesis to summary for AI analysis"""
        return {
            'id': thesis.id,
            'title': thesis.title,
            'core_claim': thesis.core_claim[:200] if thesis.core_claim else '',
            'mental_model': thesis.mental_model,
            'assumptions_count': len(thesis.assumptions) if thesis.assumptions else 0,
            'created_at': thesis.created_at.isoformat() if thesis.created_at else '',
            'signals_count': len(thesis.signals) if hasattr(thesis, 'signals') else 0
        }
    
    def _parse_json_response(self, response: str, context: str) -> Dict[str, Any]:
        """Parse JSON response with error handling"""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            self.logger.error(f"JSON parsing failed for {context}: {str(e)}")
            return {}
    
    def _predict_individual_signal_strength(self, signal: SignalMonitoring, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Predict individual signal trigger probability"""
        # Calculate base probability based on signal characteristics
        base_probability = 0.3  # Default 30% chance
        
        # Adjust based on signal age
        if signal.last_checked:
            days_since_check = (datetime.utcnow() - signal.last_checked).days
            freshness_factor = max(1.0 - (days_since_check / 30), 0.1)
            base_probability *= freshness_factor
        
        # Adjust based on threshold proximity (if available)
        if signal.current_value and signal.threshold_value:
            threshold_proximity = abs(signal.current_value - signal.threshold_value) / signal.threshold_value
            proximity_factor = max(2.0 - threshold_proximity, 0.1)
            base_probability *= proximity_factor
        
        # Adjust based on signal type priority
        signal_type_multipliers = {
            'price': 1.2,
            'volume': 1.0,
            'fundamental': 1.1,
            'technical': 0.9,
            'sentiment': 0.8
        }
        
        signal_type = signal.signal_type.lower() if signal.signal_type else 'unknown'
        for type_key, multiplier in signal_type_multipliers.items():
            if type_key in signal_type:
                base_probability *= multiplier
                break
        
        trigger_probability = min(base_probability, 1.0)
        
        return {
            'signal_id': signal.id,
            'signal_name': signal.signal_name,
            'signal_type': signal.signal_type,
            'trigger_probability': round(trigger_probability, 3),
            'estimated_days_to_trigger': int(30 * (1 - trigger_probability)),
            'confidence': round(trigger_probability * 0.8, 3)  # Slightly lower confidence
        }
    
    def _generate_predictive_insights(self, ranked_signals: List[Dict], thesis: ThesisAnalysis) -> List[str]:
        """Generate insights from signal predictions"""
        insights = []
        
        if ranked_signals:
            top_signal = ranked_signals[0]
            if top_signal['trigger_probability'] > 0.7:
                insights.append(f"High probability ({top_signal['trigger_probability']:.1%}) that '{top_signal['signal_name']}' will trigger within {top_signal['estimated_days_to_trigger']} days")
            
            high_prob_signals = [s for s in ranked_signals if s['trigger_probability'] > 0.5]
            if len(high_prob_signals) >= 3:
                insights.append(f"Multiple signals ({len(high_prob_signals)}) showing high trigger probability - thesis momentum building")
            
            signal_types = set(s['signal_type'] for s in ranked_signals[:5])
            if len(signal_types) >= 3:
                insights.append("Diverse signal types in top predictions indicate broad-based thesis validation")
        
        return insights
    
    def _estimate_next_trigger_timing(self, ranked_signals: List[Dict]) -> Dict[str, Any]:
        """Estimate timing of next signal trigger"""
        if not ranked_signals:
            return {'estimated_days': None, 'confidence': 0}
        
        top_signal = ranked_signals[0]
        return {
            'estimated_days': top_signal['estimated_days_to_trigger'],
            'signal_name': top_signal['signal_name'],
            'confidence': top_signal['confidence']
        }
    
    def _calculate_prediction_confidence(self, ranked_signals: List[Dict]) -> float:
        """Calculate overall confidence in predictions"""
        if not ranked_signals:
            return 0.0
        
        avg_confidence = sum(s['confidence'] for s in ranked_signals) / len(ranked_signals)
        signal_diversity_factor = min(len(set(s['signal_type'] for s in ranked_signals)) / 5, 1.0)
        
        return round(avg_confidence * signal_diversity_factor, 3)
    
    def _extract_sector_information(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Extract sector information from thesis"""
        # Simple keyword-based sector detection
        thesis_text = (thesis.original_thesis or '') + ' ' + (thesis.core_claim or '')
        thesis_text = thesis_text.lower()
        
        sector_keywords = {
            'technology': ['tech', 'software', 'ai', 'artificial intelligence', 'cloud', 'saas', 'semiconductor'],
            'healthcare': ['healthcare', 'pharma', 'biotech', 'medical', 'drug', 'pharmaceutical'],
            'financial': ['bank', 'financial', 'fintech', 'insurance', 'credit', 'payment'],
            'energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind', 'battery'],
            'consumer': ['consumer', 'retail', 'brand', 'e-commerce', 'shopping'],
            'industrial': ['industrial', 'manufacturing', 'aerospace', 'defense', 'construction']
        }
        
        detected_sectors = []
        for sector, keywords in sector_keywords.items():
            if any(keyword in thesis_text for keyword in keywords):
                detected_sectors.append(sector)
        
        primary_sector = detected_sectors[0] if detected_sectors else 'mixed'
        
        return {
            'primary_sector': primary_sector,
            'detected_sectors': detected_sectors,
            'sector_confidence': 0.8 if detected_sectors else 0.3
        }
    
    def _analyze_sector_momentum(self, sector_info: Dict, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Analyze sector momentum using AI"""
        try:
            momentum_prompt = f"""
            Analyze current market momentum for the {sector_info['primary_sector']} sector:
            
            Sector: {sector_info['primary_sector']}
            Related Sectors: {sector_info['detected_sectors']}
            
            Thesis Context: {thesis.core_claim[:300] if thesis.core_claim else 'N/A'}
            
            Provide analysis on:
            - Current sector momentum (positive/negative/neutral)
            - Key drivers affecting the sector
            - Rotation patterns into/out of this sector
            - Timeline of momentum shifts
            
            Return JSON: {{
                "momentum_direction": "positive/negative/neutral",
                "momentum_strength": 0.0-1.0,
                "key_drivers": ["driver1", "driver2"],
                "rotation_probability": 0.0-1.0,
                "time_horizon": "short/medium/long"
            }}
            """
            
            response = self.openai_service.generate_completion([{"role": "user", "content": momentum_prompt}], temperature=0.4)
            return self._parse_json_response(response, "sector_momentum")
            
        except Exception as e:
            self.logger.error(f"Sector momentum analysis failed: {str(e)}")
            return {
                'momentum_direction': 'neutral',
                'momentum_strength': 0.5,
                'key_drivers': [],
                'rotation_probability': 0.5,
                'time_horizon': 'medium'
            }
    
    def _detect_rotation_patterns(self, sector_info: Dict) -> Dict[str, Any]:
        """Detect sector rotation patterns"""
        # Simplified rotation pattern detection
        sector = sector_info['primary_sector']
        
        rotation_cycles = {
            'technology': {'follows': ['healthcare', 'consumer'], 'leads_to': ['financial', 'industrial']},
            'healthcare': {'follows': ['financial'], 'leads_to': ['technology', 'consumer']},
            'financial': {'follows': ['energy', 'industrial'], 'leads_to': ['healthcare', 'technology']},
            'energy': {'follows': ['consumer', 'technology'], 'leads_to': ['financial', 'industrial']},
            'consumer': {'follows': ['industrial', 'energy'], 'leads_to': ['healthcare', 'technology']},
            'industrial': {'follows': ['technology', 'healthcare'], 'leads_to': ['energy', 'consumer']}
        }
        
        cycle_info = rotation_cycles.get(sector, {'follows': [], 'leads_to': []})
        
        return {
            'current_sector': sector,
            'typically_follows': cycle_info['follows'],
            'typically_leads_to': cycle_info['leads_to'],
            'cycle_position': 'mid-cycle',  # Simplified
            'rotation_risk': 0.4  # Moderate default risk
        }
    
    def _assess_sector_vulnerability(self, thesis: ThesisAnalysis, sector_analysis: Dict) -> Dict[str, Any]:
        """Assess thesis vulnerability to sector rotation"""
        momentum_strength = sector_analysis.get('momentum_strength', 0.5)
        momentum_direction = sector_analysis.get('momentum_direction', 'neutral')
        rotation_probability = sector_analysis.get('rotation_probability', 0.5)
        
        if momentum_direction == 'positive' and momentum_strength > 0.7:
            vulnerability = 'Low'
            risk_score = 0.2
        elif momentum_direction == 'negative' or rotation_probability > 0.7:
            vulnerability = 'High'
            risk_score = 0.8
        else:
            vulnerability = 'Medium'
            risk_score = 0.5
        
        return {
            'vulnerability_level': vulnerability,
            'risk_score': risk_score,
            'momentum_alignment': momentum_direction == 'positive',
            'rotation_risk': rotation_probability,
            'recommended_monitoring': rotation_probability > 0.6
        }
    
    def _generate_sector_recommendations(self, vulnerability_assessment: Dict) -> List[str]:
        """Generate recommendations based on sector vulnerability"""
        recommendations = []
        
        risk_score = vulnerability_assessment.get('risk_score', 0.5)
        vulnerability = vulnerability_assessment.get('vulnerability_level', 'Medium')
        
        if risk_score > 0.7:
            recommendations.extend([
                "Consider reducing position size due to high sector rotation risk",
                "Implement tighter stop-loss levels",
                "Monitor sector rotation indicators daily"
            ])
        elif risk_score > 0.4:
            recommendations.extend([
                "Maintain current position with enhanced monitoring",
                "Set up sector momentum alerts",
                "Review thesis assumptions monthly"
            ])
        else:
            recommendations.extend([
                "Favorable sector momentum supports thesis",
                "Consider increasing conviction or position size",
                "Monitor for momentum continuation signals"
            ])
        
        return recommendations
    
    def _generate_pattern_insights(self, patterns: Dict, themes: List) -> List[str]:
        """Generate insights from detected patterns"""
        insights = []
        
        success_patterns = patterns.get('success_patterns', [])
        failure_patterns = patterns.get('failure_patterns', [])
        
        if success_patterns:
            insights.append(f"Identified {len(success_patterns)} common success patterns across high-performing theses")
            
        if failure_patterns:
            insights.append(f"Detected {len(failure_patterns)} recurring failure patterns to avoid")
            
        if themes:
            top_theme = max(themes, key=lambda x: float(x.get('frequency', '0')))
            insights.append(f"Most common theme: {top_theme.get('theme', 'Unknown')} appearing in {top_theme.get('frequency', '0')} theses")
        
        return insights
    
    def _calculate_pattern_confidence(self, patterns: Dict) -> float:
        """Calculate confidence in pattern detection"""
        success_count = len(patterns.get('success_patterns', []))
        failure_count = len(patterns.get('failure_patterns', []))
        
        total_patterns = success_count + failure_count
        if total_patterns == 0:
            return 0.0
        
        # Higher confidence with more patterns detected
        base_confidence = min(total_patterns / 10, 1.0)
        return round(base_confidence * 0.8, 3)  # Conservative confidence
    
    def _generate_dashboard_insights(self, dashboard_data: Dict) -> List[str]:
        """Generate summary insights for the dashboard"""
        insights = []
        
        performance_scores = dashboard_data.get('performance_scores', {})
        if performance_scores:
            avg_score = sum(score.get('overall_score', 0) for score in performance_scores.values()) / len(performance_scores)
            insights.append(f"Portfolio average performance score: {avg_score:.1f}/100")
            
            high_conviction = len([s for s in performance_scores.values() if s.get('performance_tier') == 'High Conviction'])
            insights.append(f"{high_conviction} theses currently in 'High Conviction' tier")
        
        cross_patterns = dashboard_data.get('cross_thesis_patterns', {})
        if cross_patterns.get('success_patterns'):
            insights.append(f"Detected {len(cross_patterns['success_patterns'])} success patterns for portfolio optimization")
        
        return insights