"""
LLM Manager - Centralized AI service management
All LLM/AI calls go through this manager for consistency and monitoring
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from services.azure_openai_service import AzureOpenAIService


class LLMManager:
    """Centralized manager for all LLM operations"""
    
    def __init__(self):
        self.ai_service = AzureOpenAIService()
        self.call_count = 0
        self.success_count = 0
    
    def analyze_thesis(self, thesis_text: str, max_tokens: int = 2000) -> Dict[str, Any]:
        """Core thesis analysis using AI"""
        prompt = f"""
        Analyze this investment thesis comprehensively:

        THESIS: {thesis_text}

        Provide structured analysis in JSON format:
        {{
            "core_claim": "Main investment claim",
            "core_analysis": "Detailed analysis of the claim",
            "causal_chain": ["Step 1", "Step 2", "Step 3"],
            "assumptions": ["Assumption 1", "Assumption 2"],
            "mental_model": "Investment framework/model",
            "counter_thesis": {{
                "scenario_1": "Alternative outcome 1",
                "scenario_2": "Alternative outcome 2"
            }}
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens, temperature=0.2)
    
    def extract_signals(self, analysis_data: Dict[str, Any], documents: List[Dict] = None) -> Dict[str, Any]:
        """Extract monitoring signals from analysis"""
        prompt = f"""
        Extract actionable monitoring signals from this investment analysis:

        ANALYSIS: {json.dumps(analysis_data, indent=2)}

        Generate monitoring signals in JSON format:
        {{
            "signals": [
                {{
                    "name": "Signal name",
                    "type": "Level_0_Raw_Economic_Activity|Level_1_Primary_Signals|Level_2_Derived_Metrics|Level_3_Technical_Indicators|Level_4_Market_Sentiment|Level_5_Meta_Analysis",
                    "description": "What this signal measures",
                    "data_source": "Where to find this data",
                    "frequency": "daily|weekly|monthly|quarterly",
                    "threshold_type": "above|below|change_percent",
                    "predictive_power": "high|medium|low"
                }}
            ]
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens=1500, temperature=0.3)
    
    def generate_significance_mapping(self, research_elements: List[Dict], signal_patterns: List[Dict]) -> Dict[str, Any]:
        """Generate connections between research elements and signals"""
        prompt = f"""
        Analyze the logical connections between research elements and signal patterns:

        RESEARCH ELEMENTS: {json.dumps(research_elements, indent=2)}
        SIGNAL PATTERNS: {json.dumps(signal_patterns, indent=2)}

        Generate connection mapping in JSON format:
        {{
            "connections": [
                {{
                    "research_id": "research element ID",
                    "signal_id": "signal pattern ID", 
                    "relationship_type": "validates|indicates|contradicts|supports",
                    "strength": 0.0-1.0,
                    "explanation": "Why this connection exists"
                }}
            ],
            "insights": {{
                "connection_quality": "excellent|good|moderate|weak",
                "research_signal_alignment": 0.0-1.0,
                "key_findings": ["Finding 1", "Finding 2"]
            }}
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens=1200, temperature=0.2)
    
    def prioritize_elements(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart prioritization for research and signals"""
        prompt = f"""
        Analyze and prioritize research quality and signal strength:

        THESIS ANALYSIS: {json.dumps(thesis_analysis, indent=2)}

        Generate dual prioritization in JSON format:
        {{
            "research_prioritization": {{
                "element_scores": {{
                    "core_claim": {{"overall_score": 0-10}},
                    "core_analysis": {{"overall_score": 0-10}},
                    "assumptions": {{"overall_score": 0-10}},
                    "mental_model": {{"overall_score": 0-10}},
                    "causal_chain": {{"overall_score": 0-10}}
                }},
                "priority_ranking": ["element1", "element2", "element3"],
                "research_quality_summary": "Assessment of overall research quality"
            }},
            "signal_prioritization": {{
                "signal_categories": {{
                    "financial_metrics": {{"overall_strength": 0-10}},
                    "market_indicators": {{"overall_strength": 0-10}},
                    "operational_metrics": {{"overall_strength": 0-10}}
                }},
                "signal_priority_ranking": ["category1", "category2"],
                "predictive_strength_summary": "Assessment of signal reliability"
            }}
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens=1500, temperature=0.2)
    
    def generate_scenario_analysis(self, thesis_data: Dict, scenario: str, time_horizon: int) -> Dict[str, Any]:
        """Generate scenario-based analysis"""
        prompt = f"""
        Generate scenario analysis for investment thesis:

        THESIS: {json.dumps(thesis_data, indent=2)}
        SCENARIO: {scenario}
        TIME HORIZON: {time_horizon} years

        Provide analysis in JSON format:
        {{
            "scenario_summary": "Brief scenario description",
            "performance_assessment": "Expected performance under this scenario",
            "key_risks": ["Risk 1", "Risk 2"],
            "key_opportunities": ["Opportunity 1", "Opportunity 2"],
            "strategic_recommendations": ["Recommendation 1", "Recommendation 2"],
            "conviction_level": "High|Medium|Low",
            "probability_assessment": "Likelihood assessment"
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens=1200, temperature=0.4)
    
    def analyze_market_sentiment(self, thesis_data: Dict) -> Dict[str, Any]:
        """Generate market sentiment analysis"""
        prompt = f"""
        Analyze current market sentiment for this investment thesis:

        THESIS: {json.dumps(thesis_data, indent=2)}

        Generate sentiment analysis in JSON format:
        {{
            "overall_sentiment": "bullish|neutral|bearish",
            "sentiment_score": 0.0-1.0,
            "market_factors": ["Factor 1", "Factor 2"],
            "sentiment_drivers": ["Driver 1", "Driver 2"],
            "risk_assessment": "Current risk level",
            "outlook": "Short to medium term outlook"
        }}
        """
        
        return self._make_ai_call(prompt, max_tokens=800, temperature=0.3)
    
    def _make_ai_call(self, prompt: str, max_tokens: int, temperature: float = 0.2) -> Dict[str, Any]:
        """Centralized AI call handling with monitoring and fallbacks"""
        self.call_count += 1
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.ai_service.generate_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if not response:
                raise Exception("Empty response from AI service")
            
            # Clean and parse JSON response
            cleaned_response = self._clean_json_response(response)
            result = json.loads(cleaned_response)
            
            self.success_count += 1
            logging.info(f"LLM call successful. Success rate: {self.success_count}/{self.call_count}")
            
            return result
            
        except (TimeoutError, ConnectionError, Exception) as e:
            error_msg = str(e).lower()
            # Check for network-related errors that should trigger fallbacks
            if any(keyword in error_msg for keyword in ['timeout', 'connection', 'network', 'ssl', 'recv', 'unavailable']):
                logging.warning(f"Network error detected, using structured fallback: {str(e)}")
            else:
                logging.warning(f"LLM call failed, using structured fallback: {str(e)}")
            return self._generate_structured_fallback(prompt)
    
    def _clean_json_response(self, response: str) -> str:
        """Clean AI response to extract valid JSON"""
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Find JSON boundaries
        if cleaned.startswith('{'):
            end = cleaned.rfind('}')
            if end != -1:
                cleaned = cleaned[:end+1]
        elif cleaned.startswith('['):
            end = cleaned.rfind(']')
            if end != -1:
                cleaned = cleaned[:end+1]
        
        return cleaned
    
    def _generate_structured_fallback(self, prompt: str) -> Dict[str, Any]:
        """Generate structured fallback responses when AI service fails"""
        
        # Analyze prompt to determine expected response structure
        if "thesis" in prompt.lower() and "analyze" in prompt.lower():
            return self._thesis_analysis_fallback()
        elif "signals" in prompt.lower() and "extract" in prompt.lower():
            return self._signal_extraction_fallback()
        elif "significance" in prompt.lower() and "mapping" in prompt.lower():
            return self._significance_mapping_fallback()
        elif "prioritize" in prompt.lower() or "prioritization" in prompt.lower():
            return self._prioritization_fallback()
        elif "scenario" in prompt.lower() and "analysis" in prompt.lower():
            return self._scenario_analysis_fallback()
        elif "sentiment" in prompt.lower() and "market" in prompt.lower():
            return self._market_sentiment_fallback()
        else:
            return self._generic_fallback()
    
    def _thesis_analysis_fallback(self) -> Dict[str, Any]:
        """Fallback structure for thesis analysis"""
        return {
            "core_claim": "Investment thesis requires detailed analysis",
            "core_analysis": "Analysis temporarily unavailable - please review thesis fundamentals",
            "causal_chain": ["Market conditions", "Company performance", "Investment outcome"],
            "assumptions": ["Market stability", "Company execution", "Sector growth"],
            "mental_model": "Fundamental analysis framework",
            "counter_thesis": {
                "scenario_1": "Market conditions deteriorate",
                "scenario_2": "Company execution falls short"
            }
        }
    
    def _signal_extraction_fallback(self) -> Dict[str, Any]:
        """Fallback structure for signal extraction"""
        return {
            "signals": [
                {
                    "name": "Revenue Growth Rate",
                    "type": "Level_1_Primary_Signals",
                    "description": "Quarterly revenue growth tracking",
                    "data_source": "Financial reports",
                    "frequency": "quarterly",
                    "threshold_type": "above",
                    "predictive_power": "high"
                },
                {
                    "name": "Market Share Indicator",
                    "type": "Level_2_Derived_Metrics", 
                    "description": "Company market position tracking",
                    "data_source": "Industry analysis",
                    "frequency": "monthly",
                    "threshold_type": "change_percent",
                    "predictive_power": "medium"
                }
            ]
        }
    
    def _significance_mapping_fallback(self) -> Dict[str, Any]:
        """Fallback structure for significance mapping"""
        return {
            "connections": [
                {
                    "research_id": "core_claim",
                    "signal_id": "revenue_growth",
                    "relationship_type": "validates",
                    "strength": 0.7,
                    "explanation": "Revenue growth directly supports investment thesis"
                }
            ],
            "insights": {
                "connection_quality": "moderate",
                "research_signal_alignment": 0.6,
                "key_findings": ["Analysis system temporarily unavailable", "Review connections manually"]
            }
        }
    
    def _prioritization_fallback(self) -> Dict[str, Any]:
        """Fallback structure for prioritization analysis"""
        return {
            "research_prioritization": {
                "element_scores": {
                    "core_claim": {"overall_score": 7},
                    "core_analysis": {"overall_score": 6},
                    "assumptions": {"overall_score": 5},
                    "mental_model": {"overall_score": 6},
                    "causal_chain": {"overall_score": 5}
                },
                "priority_ranking": ["core_claim", "core_analysis", "mental_model", "assumptions", "causal_chain"],
                "research_quality_summary": "Analysis temporarily unavailable"
            },
            "signal_prioritization": {
                "signal_categories": {
                    "financial_metrics": {"overall_strength": 7},
                    "market_indicators": {"overall_strength": 6},
                    "operational_metrics": {"overall_strength": 5}
                },
                "signal_priority_ranking": ["financial_metrics", "market_indicators", "operational_metrics"],
                "predictive_strength_summary": "Signal analysis temporarily unavailable"
            }
        }
    
    def _scenario_analysis_fallback(self) -> Dict[str, Any]:
        """Fallback structure for scenario analysis"""
        return {
            "scenario_summary": "Scenario analysis temporarily unavailable",
            "performance_assessment": "Review market conditions manually",
            "key_risks": ["Market volatility", "Execution risk", "External factors"],
            "key_opportunities": ["Market growth", "Competitive advantage", "Operational efficiency"],
            "strategic_recommendations": ["Monitor key metrics", "Review regularly", "Adjust as needed"],
            "conviction_level": "Medium",
            "probability_assessment": "Analysis requires review"
        }
    
    def _market_sentiment_fallback(self) -> Dict[str, Any]:
        """Fallback structure for market sentiment"""
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.5,
            "market_factors": ["Economic conditions", "Industry trends"],
            "sentiment_drivers": ["Market uncertainty", "Mixed signals"],
            "risk_assessment": "Moderate risk environment",
            "outlook": "Review current market conditions"
        }
    
    def _generic_fallback(self) -> Dict[str, Any]:
        """Generic fallback for unrecognized prompts"""
        return {
            "status": "analysis_unavailable",
            "message": "AI analysis service temporarily unavailable",
            "recommendation": "Review data manually or retry later"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LLM usage statistics"""
        return {
            'total_calls': self.call_count,
            'successful_calls': self.success_count,
            'success_rate': self.success_count / self.call_count if self.call_count > 0 else 0,
            'ai_service_status': 'active' if self.ai_service else 'inactive'
        }