import logging
import json
import re
from typing import Dict, List, Any

class LocalAnalysisService:
    """Local analysis service for thesis processing when Azure OpenAI is unavailable"""
    
    def __init__(self):
        self.mental_models = ['Growth', 'Value', 'Cyclical', 'Disruption', 'Quality', 'Momentum']
        self.signal_types = [
            'Revenue Growth Rate',
            'Market Share Analysis',
            'Competitive Position',
            'Financial Performance',
            'Operational Metrics',
            'Technology Innovation'
        ]
    
    def analyze_thesis(self, thesis_text: str) -> Dict[str, Any]:
        """Analyze investment thesis using rule-based approach"""
        try:
            # Extract core components from thesis text
            core_claim = self._extract_core_claim(thesis_text)
            mental_model = self._determine_mental_model(thesis_text)
            assumptions = self._extract_assumptions(thesis_text)
            metrics = self._identify_metrics(thesis_text)
            
            analysis_result = {
                'core_claim': core_claim,
                'core_analysis': f"Analysis of {mental_model.lower()} thesis with focus on {self._get_focus_area(thesis_text)}",
                'causal_chain': self._build_causal_chain(thesis_text),
                'assumptions': assumptions,
                'mental_model': mental_model,
                'counter_thesis_scenarios': self._generate_counter_scenarios(thesis_text),
                'metrics_to_track': metrics,
                'monitoring_plan': self._create_monitoring_plan(metrics),
                'market_sentiment': self._generate_market_sentiment()
            }
            
            logging.info("Local thesis analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logging.error(f"Local analysis failed: {str(e)}")
            raise Exception("Analysis service temporarily unavailable. Please try again.")
    
    def _extract_core_claim(self, thesis_text: str) -> str:
        """Extract the main investment claim from thesis text"""
        # Look for key phrases that indicate the main claim
        sentences = thesis_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in [
                'positioned', 'growth', 'opportunity', 'advantage', 'potential',
                'expects', 'will', 'should', 'strong', 'leadership'
            ]):
                return sentence
        
        # Fallback to first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                return sentence.strip()
        
        return "Investment opportunity identified through fundamental analysis"
    
    def _determine_mental_model(self, thesis_text: str) -> str:
        """Determine the investment mental model based on text content"""
        text_lower = thesis_text.lower()
        
        # Growth indicators
        if any(keyword in text_lower for keyword in [
            'growth', 'expansion', 'increasing', 'growing', 'revenue growth'
        ]):
            return 'Growth'
        
        # Disruption indicators
        if any(keyword in text_lower for keyword in [
            'disruption', 'innovation', 'technology', 'ai', 'artificial intelligence'
        ]):
            return 'Disruption'
        
        # Value indicators
        if any(keyword in text_lower for keyword in [
            'undervalued', 'cheap', 'discount', 'value'
        ]):
            return 'Value'
        
        # Cyclical indicators
        if any(keyword in text_lower for keyword in [
            'cycle', 'cyclical', 'recovery', 'turnaround'
        ]):
            return 'Cyclical'
        
        return 'Quality'
    
    def _get_focus_area(self, thesis_text: str) -> str:
        """Identify the primary focus area of the thesis"""
        text_lower = thesis_text.lower()
        
        if any(keyword in text_lower for keyword in ['cloud', 'azure', 'aws']):
            return 'cloud computing services'
        elif any(keyword in text_lower for keyword in ['ai', 'artificial intelligence']):
            return 'artificial intelligence capabilities'
        elif any(keyword in text_lower for keyword in ['market share', 'competition']):
            return 'competitive positioning'
        elif any(keyword in text_lower for keyword in ['revenue', 'financial']):
            return 'financial performance'
        else:
            return 'business fundamentals'
    
    def _extract_assumptions(self, thesis_text: str) -> List[str]:
        """Extract key assumptions from the thesis"""
        assumptions = []
        text_lower = thesis_text.lower()
        
        if 'growth' in text_lower:
            assumptions.append("Market demand will continue to grow")
        if 'market share' in text_lower or 'competition' in text_lower:
            assumptions.append("Company can maintain or gain competitive position")
        if 'technology' in text_lower or 'innovation' in text_lower:
            assumptions.append("Technology advantages will be sustained")
        if 'partnership' in text_lower:
            assumptions.append("Strategic partnerships will deliver expected value")
        
        return assumptions[:4]  # Limit to top 4 assumptions
    
    def _build_causal_chain(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Build a logical causal chain for the investment thesis"""
        chain = []
        
        # Determine chain based on thesis content
        if 'cloud' in thesis_text.lower():
            chain = [
                {
                    "chain_link": 1,
                    "event": "Cloud adoption increases",
                    "explanation": "Digital transformation drives demand for cloud services"
                },
                {
                    "chain_link": 2,
                    "event": "Revenue growth accelerates", 
                    "explanation": "Higher cloud adoption translates to increased revenue"
                },
                {
                    "chain_link": 3,
                    "event": "Market valuation increases",
                    "explanation": "Strong revenue growth improves company valuation"
                }
            ]
        else:
            chain = [
                {
                    "chain_link": 1,
                    "event": "Market opportunity expands",
                    "explanation": "Industry fundamentals support growth"
                },
                {
                    "chain_link": 2,
                    "event": "Company captures market share",
                    "explanation": "Competitive advantages enable market share gains"
                },
                {
                    "chain_link": 3,
                    "event": "Financial performance improves",
                    "explanation": "Market share gains drive financial outperformance"
                }
            ]
        
        return chain
    
    def _identify_metrics(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Identify key metrics to track based on thesis content"""
        metrics = []
        text_lower = thesis_text.lower()
        
        if 'revenue' in text_lower or 'growth' in text_lower:
            metrics.append({
                "name": "Revenue Growth Rate",
                "type": "Level_2_Derived_Metrics",
                "description": "Quarterly revenue growth year-over-year",
                "frequency": "quarterly",
                "threshold": 15.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "downstream"
            })
        
        if 'market share' in text_lower or 'competition' in text_lower:
            metrics.append({
                "name": "Market Position Analysis",
                "type": "Level_3_Comparative_Analysis",
                "description": "Competitive market share tracking",
                "frequency": "quarterly",
                "threshold": 10.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "midstream"
            })
        
        if 'cloud' in text_lower or 'technology' in text_lower:
            metrics.append({
                "name": "Technology Performance Metrics",
                "type": "Level_2_Derived_Metrics", 
                "description": "Technology adoption and performance indicators",
                "frequency": "monthly",
                "threshold": 20.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "upstream"
            })
        
        return metrics[:3]  # Limit to top 3 metrics
    
    def _generate_counter_scenarios(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Generate counter-thesis scenarios"""
        scenarios = []
        text_lower = thesis_text.lower()
        
        if 'growth' in text_lower:
            scenarios.append({
                "scenario": "Growth Slowdown Risk",
                "description": "Market saturation or competitive pressure reduces growth rates",
                "trigger_conditions": ["Revenue growth below 10%", "Market share decline"],
                "data_signals": ["Quarterly revenue", "Market share data"]
            })
        
        if 'technology' in text_lower or 'innovation' in text_lower:
            scenarios.append({
                "scenario": "Technology Disruption Risk",
                "description": "New technologies or competitors challenge current position",
                "trigger_conditions": ["Competitor innovation", "Technology shift"],
                "data_signals": ["R&D spending", "Patent filings", "Competitor analysis"]
            })
        
        return scenarios[:2]  # Limit to top 2 scenarios
    
    def _create_monitoring_plan(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a comprehensive monitoring plan"""
        return {
            "objective": "Monitor and validate thesis performance with quantified thresholds",
            "validation_framework": {
                "core_claim_metrics": [
                    {
                        "metric": "Primary Performance Indicator",
                        "target_threshold": ">15%",
                        "measurement_frequency": "quarterly",
                        "data_source": "FactSet",
                        "validation_logic": "Direct measurement to validate thesis"
                    }
                ],
                "assumption_tests": [
                    {
                        "assumption": "Market growth assumption",
                        "test_metric": "Market Growth Rate",
                        "success_threshold": ">10%",
                        "failure_threshold": "<5%",
                        "data_source": "FactSet"
                    }
                ]
            },
            "data_acquisition": [
                {
                    "category": "Financial Performance",
                    "metrics": ["Revenue", "Growth Rate"],
                    "data_source": "FactSet",
                    "frequency": "quarterly",
                    "automation_level": "full"
                }
            ],
            "alert_system": [
                {
                    "trigger_name": "Performance Alert",
                    "condition": "Metrics below threshold",
                    "severity": "high",
                    "action": "Review performance trends",
                    "notification_method": "dashboard"
                }
            ],
            "review_schedule": "Weekly signal review, monthly validation assessment"
        }
    
    def _generate_market_sentiment(self) -> Dict[str, Any]:
        """Generate market sentiment data structure"""
        return {
            "buy_rating": 70,
            "hold_rating": 25,
            "sell_rating": 5,
            "price_target_avg": 200,
            "price_target_high": 250,
            "price_target_low": 150,
            "analyst_count": 15,
            "momentum_score": 75,
            "institutional_ownership": 65,
            "sentiment_trend": "positive"
        }