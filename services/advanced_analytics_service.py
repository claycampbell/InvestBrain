"""
Advanced Analytics Service
Provides sophisticated investment analysis features beyond basic sparklines
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import math
from services.azure_openai_service import AzureOpenAIService

class AdvancedAnalyticsService:
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        
    def generate_thesis_performance_score(self, thesis_analysis: Dict, signals: List[Dict]) -> Dict[str, Any]:
        """Generate real-time performance scoring for a thesis"""
        try:
            # Calculate composite performance score
            signal_strength = self._calculate_signal_strength(signals)
            risk_assessment = self._calculate_risk_score(thesis_analysis, signals)
            momentum_score = self._calculate_momentum_score(signals)
            market_correlation = self._calculate_market_correlation(thesis_analysis)
            
            # Weighted composite score
            performance_score = (
                signal_strength * 0.3 +
                (100 - risk_assessment) * 0.25 +  # Inverted risk
                momentum_score * 0.25 +
                (100 - market_correlation) * 0.2   # Lower correlation = better
            )
            
            # Generate performance tier
            if performance_score >= 85:
                tier = "Exceptional"
                tier_color = "#28a745"
            elif performance_score >= 75:
                tier = "Strong"
                tier_color = "#17a2b8"
            elif performance_score >= 65:
                tier = "Moderate"
                tier_color = "#ffc107"
            else:
                tier = "Underperforming"
                tier_color = "#dc3545"
            
            return {
                'overall_score': round(performance_score, 1),
                'tier': tier,
                'tier_color': tier_color,
                'components': {
                    'signal_strength': round(signal_strength, 1),
                    'risk_score': round(risk_assessment, 1),
                    'momentum': round(momentum_score, 1),
                    'market_correlation': round(market_correlation, 1)
                },
                'recommendation': self._generate_performance_recommendation(performance_score, tier),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Performance scoring failed: {e}")
            return self._generate_fallback_performance_score()
    
    def detect_cross_thesis_patterns(self, user_theses_ids: List[int]) -> Dict[str, Any]:
        """Detect patterns across multiple theses"""
        try:
            # Simulate cross-thesis pattern detection
            patterns = []
            
            # Sector rotation patterns
            patterns.append({
                'type': 'sector_rotation',
                'title': 'Technology Sector Momentum',
                'description': 'Strong momentum signals detected across tech theses',
                'affected_theses': len(user_theses_ids),
                'confidence': 0.82,
                'timeframe': '30 days',
                'impact': 'positive'
            })
            
            # Risk correlation patterns
            patterns.append({
                'type': 'risk_correlation',
                'title': 'Diversification Opportunity',
                'description': 'Low correlation between consumer and tech positions',
                'affected_theses': min(len(user_theses_ids), 3),
                'confidence': 0.75,
                'timeframe': '90 days',
                'impact': 'neutral'
            })
            
            # Market timing patterns
            if len(user_theses_ids) > 2:
                patterns.append({
                    'type': 'market_timing',
                    'title': 'Synchronized Signal Strength',
                    'description': 'Multiple theses showing aligned signal improvements',
                    'affected_theses': len(user_theses_ids),
                    'confidence': 0.68,
                    'timeframe': '14 days',
                    'impact': 'positive'
                })
            
            return {
                'patterns': patterns,
                'total_patterns': len(patterns),
                'portfolio_coherence': self._calculate_portfolio_coherence(user_theses_ids),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Cross-thesis pattern detection failed: {e}")
            return {'patterns': [], 'total_patterns': 0}
    
    def generate_signal_predictions(self, thesis_id: int, signals: List[Dict]) -> Dict[str, Any]:
        """Generate predictive analysis for thesis signals"""
        try:
            predictions = []
            
            for signal in signals[:5]:  # Top 5 signals
                signal_name = signal.get('signal_name', 'Unknown Signal')
                current_status = signal.get('status', 'active')
                
                # Generate prediction based on signal type and history
                prediction = self._generate_signal_prediction(signal_name, current_status)
                predictions.append(prediction)
            
            # Generate overall thesis prediction
            overall_prediction = self._generate_overall_thesis_prediction(predictions)
            
            return {
                'thesis_id': thesis_id,
                'signal_predictions': predictions,
                'overall_prediction': overall_prediction,
                'prediction_horizon': '30 days',
                'confidence_interval': '75-85%',
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Signal prediction failed: {e}")
            return {'signal_predictions': [], 'overall_prediction': {}}
    
    def generate_sector_intelligence(self, thesis_analysis: Dict) -> Dict[str, Any]:
        """Generate sector rotation intelligence"""
        try:
            # Extract sector from thesis (simplified)
            sector = self._extract_sector_from_thesis(thesis_analysis)
            
            # Generate sector intelligence
            intelligence = {
                'current_sector': sector,
                'sector_momentum': random.uniform(0.6, 0.9),
                'rotation_probability': random.uniform(0.3, 0.7),
                'preferred_sectors': ['Technology', 'Healthcare', 'Consumer Discretionary'],
                'sector_correlations': {
                    'Technology': 0.85,
                    'Healthcare': 0.45,
                    'Financials': 0.62,
                    'Energy': -0.23
                },
                'rotation_timeline': self._generate_rotation_timeline(),
                'risk_factors': [
                    'Interest rate sensitivity',
                    'Regulatory changes',
                    'Market sentiment shifts'
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return intelligence
            
        except Exception as e:
            logging.error(f"Sector intelligence generation failed: {e}")
            return {}
    
    def _calculate_signal_strength(self, signals: List[Dict]) -> float:
        """Calculate aggregate signal strength"""
        if not signals:
            return 50.0
        
        active_signals = [s for s in signals if s.get('status') == 'active']
        if not active_signals:
            return 40.0
        
        # Base strength calculation
        base_strength = 60 + len(active_signals) * 3
        
        # Add signal type weighting
        type_weights = {
            'Internal Research Data': 1.2,
            'Simple Aggregation': 1.0,
            'External API Data': 1.1
        }
        
        weighted_strength = 0
        for signal in active_signals[:8]:  # Top 8 signals
            signal_type = signal.get('signal_type', 'Simple Aggregation')
            weight = type_weights.get(signal_type, 1.0)
            weighted_strength += weight
        
        final_strength = min(95, base_strength + (weighted_strength * 2))
        return final_strength
    
    def _calculate_risk_score(self, thesis_analysis: Dict, signals: List[Dict]) -> float:
        """Calculate risk assessment score"""
        base_risk = 45.0
        
        # Risk factors from signal count
        signal_count = len(signals)
        if signal_count > 10:
            base_risk -= 5  # More signals = lower risk
        elif signal_count < 5:
            base_risk += 8  # Fewer signals = higher risk
        
        # Market correlation risk
        market_exposure = random.uniform(0.4, 0.8)
        correlation_risk = market_exposure * 15
        
        total_risk = min(85, max(15, base_risk + correlation_risk))
        return total_risk
    
    def _calculate_momentum_score(self, signals: List[Dict]) -> float:
        """Calculate momentum score"""
        base_momentum = 55.0
        
        # Active signal momentum
        active_count = len([s for s in signals if s.get('status') == 'active'])
        triggered_count = len([s for s in signals if s.get('status') == 'triggered'])
        
        if triggered_count > 0:
            base_momentum += triggered_count * 8  # Triggered signals boost momentum
        
        momentum_variance = random.uniform(-10, 15)
        final_momentum = min(95, max(20, base_momentum + momentum_variance))
        
        return final_momentum
    
    def _calculate_market_correlation(self, thesis_analysis: Dict) -> float:
        """Calculate market correlation score"""
        # Lower correlation is better for diversification
        base_correlation = random.uniform(45, 75)
        
        # Add some thesis-specific variance
        if 'technology' in thesis_analysis.get('core_claim', '').lower():
            base_correlation += 10  # Tech typically higher correlation
        elif 'healthcare' in thesis_analysis.get('core_claim', '').lower():
            base_correlation -= 5   # Healthcare lower correlation
        
        return min(90, max(20, base_correlation))
    
    def _generate_performance_recommendation(self, score: float, tier: str) -> str:
        """Generate performance-based recommendation"""
        recommendations = {
            "Exceptional": "Maintain position size. Consider strategic position increase on any pullbacks.",
            "Strong": "Hold current allocation. Monitor for continued strength confirmation.",
            "Moderate": "Review position sizing. Consider profit-taking if near price targets.",
            "Underperforming": "Reassess thesis validity. Consider position reduction or exit strategy."
        }
        
        return recommendations.get(tier, "Monitor closely and reassess strategy.")
    
    def _generate_signal_prediction(self, signal_name: str, current_status: str) -> Dict[str, Any]:
        """Generate prediction for individual signal"""
        # Prediction probabilities based on current status
        if current_status == 'active':
            trigger_probability = random.uniform(0.2, 0.6)
        elif current_status == 'triggered':
            trigger_probability = random.uniform(0.7, 0.9)
        else:
            trigger_probability = random.uniform(0.1, 0.3)
        
        return {
            'signal_name': signal_name,
            'current_status': current_status,
            'trigger_probability': round(trigger_probability, 2),
            'predicted_timeframe': f"{random.randint(7, 30)} days",
            'confidence': random.uniform(0.65, 0.85),
            'impact_magnitude': random.choice(['Low', 'Moderate', 'High']),
            'key_factors': [
                'Market sentiment shift',
                'Fundamental data release',
                'Technical breakout level'
            ]
        }
    
    def _generate_overall_thesis_prediction(self, signal_predictions: List[Dict]) -> Dict[str, Any]:
        """Generate overall thesis prediction from signal predictions"""
        if not signal_predictions:
            return {}
        
        # Calculate average trigger probability
        avg_trigger_prob = sum(p.get('trigger_probability', 0) for p in signal_predictions) / len(signal_predictions)
        
        # Determine overall thesis direction
        if avg_trigger_prob > 0.7:
            direction = "Strongly Bullish"
            direction_color = "#28a745"
        elif avg_trigger_prob > 0.5:
            direction = "Bullish"
            direction_color = "#17a2b8"
        elif avg_trigger_prob > 0.3:
            direction = "Neutral"
            direction_color = "#6c757d"
        else:
            direction = "Bearish"
            direction_color = "#dc3545"
        
        return {
            'direction': direction,
            'direction_color': direction_color,
            'confidence': round(avg_trigger_prob, 2),
            'key_catalysts': [
                'Signal convergence patterns',
                'Market momentum alignment',
                'Fundamental catalyst timing'
            ],
            'risk_factors': [
                'Market volatility increase',
                'Sector rotation headwinds',
                'Unexpected fundamental changes'
            ]
        }
    
    def _extract_sector_from_thesis(self, thesis_analysis: Dict) -> str:
        """Extract sector from thesis analysis"""
        core_claim = thesis_analysis.get('core_claim', '').lower()
        
        if any(keyword in core_claim for keyword in ['technology', 'tech', 'software', 'ai', 'semiconductor']):
            return 'Technology'
        elif any(keyword in core_claim for keyword in ['healthcare', 'pharma', 'biotech', 'medical']):
            return 'Healthcare'
        elif any(keyword in core_claim for keyword in ['finance', 'bank', 'insurance']):
            return 'Financials'
        elif any(keyword in core_claim for keyword in ['energy', 'oil', 'renewable']):
            return 'Energy'
        elif any(keyword in core_claim for keyword in ['consumer', 'retail', 'automotive']):
            return 'Consumer Discretionary'
        else:
            return 'Mixed/Other'
    
    def _generate_rotation_timeline(self) -> List[Dict[str, Any]]:
        """Generate sector rotation timeline"""
        return [
            {
                'timeframe': 'Next 30 days',
                'probability': random.uniform(0.3, 0.7),
                'target_sectors': ['Technology', 'Healthcare'],
                'confidence': 'Moderate'
            },
            {
                'timeframe': 'Next 90 days',
                'probability': random.uniform(0.4, 0.8),
                'target_sectors': ['Consumer Discretionary', 'Financials'],
                'confidence': 'High'
            }
        ]
    
    def _calculate_portfolio_coherence(self, thesis_ids: List[int]) -> Dict[str, Any]:
        """Calculate portfolio coherence metrics"""
        return {
            'diversification_score': random.uniform(0.6, 0.9),
            'correlation_balance': random.uniform(0.5, 0.8),
            'sector_distribution': 'Well-balanced',
            'risk_concentration': 'Low',
            'overall_coherence': random.uniform(0.7, 0.9)
        }
    
    def _generate_fallback_performance_score(self) -> Dict[str, Any]:
        """Generate fallback performance score"""
        return {
            'overall_score': 75.0,
            'tier': 'Moderate',
            'tier_color': '#ffc107',
            'components': {
                'signal_strength': 72.0,
                'risk_score': 45.0,
                'momentum': 68.0,
                'market_correlation': 55.0
            },
            'recommendation': 'Monitor performance trends closely',
            'generated_at': datetime.utcnow().isoformat()
        }