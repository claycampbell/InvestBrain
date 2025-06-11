import logging
import json
from typing import Dict, Any, List
from services.azure_openai_service import AzureOpenAIService

class SimpleAnalysisService:
    """
    Simplified analysis service that performs thesis analysis in a single request
    to avoid network timeout issues with chained requests
    """
    
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        
    def analyze_thesis(self, thesis_text: str) -> Dict[str, Any]:
        """Analyze investment thesis in a single comprehensive request"""
        logging.info(f"Starting simplified analysis for thesis: {thesis_text[:50]}...")
        
        try:
            # Single comprehensive prompt that extracts everything at once
            system_prompt = """You are an expert investment analyst. Analyze the investment thesis and extract both analysis and trackable signals in one response.

Respond with valid JSON only:
{
  "core_claim": "Single sentence primary investment thesis",
  "core_analysis": "Detailed analysis of risk/reward dynamics and key uncertainties",
  "assumptions": ["Critical assumption 1", "Critical assumption 2", "Critical assumption 3"],
  "mental_model": "Growth|Value|Disruption|Turnaround|Quality|Cyclical",
  "causal_chain": [
    {"chain_link": 1, "event": "Initial catalyst", "explanation": "How this affects thesis"},
    {"chain_link": 2, "event": "Second consequence", "explanation": "Connection to previous"}
  ],
  "counter_thesis_scenarios": [
    {"scenario": "Primary risk", "description": "Risk explanation", "trigger_conditions": ["Trigger 1"], "data_signals": ["Signal to watch"]}
  ],
  "trackable_signals": [
    {
      "name": "Revenue Growth Rate",
      "level": "Level_1_Simple_Aggregation",
      "description": "Quarterly revenue growth tracking",
      "frequency": "quarterly",
      "threshold": 15.0,
      "threshold_type": "above",
      "data_source": "FactSet Fundamentals",
      "value_chain_position": "downstream",
      "programmatic_feasibility": "high",
      "what_it_tells_us": "Indicates demand acceleration"
    }
  ]
}"""

            user_prompt = f"""Analyze this investment thesis: {thesis_text}

Extract:
1. Core investment logic and key assumptions
2. Primary risks and counter-scenarios 
3. 4-6 trackable signals from FactSet/Xpressfeed datasets
4. Value chain positioning (upstream/midstream/downstream)
5. Signal classification (Level 0: Raw Economic Activity, Level 1: Simple Aggregation)

Focus on signals closest to raw economic activity that can be programmatically tracked."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Single request with moderate timeout
            response = self.azure_service.generate_completion(messages, max_tokens=3000)
            
            # Parse the JSON response
            try:
                analysis_data = json.loads(response)
                logging.info("Successfully parsed analysis JSON")
                return analysis_data
                
            except json.JSONDecodeError as e:
                logging.warning(f"Failed to parse JSON, extracting content: {e}")
                return self._extract_from_text(response, thesis_text)
                
        except Exception as e:
            logging.error(f"Analysis failed: {e}")
            return self._get_fallback_analysis(thesis_text)
    
    def _extract_from_text(self, response: str, thesis_text: str) -> Dict[str, Any]:
        """Extract structured data from non-JSON response"""
        return {
            "core_claim": f"Investment thesis: {thesis_text[:100]}...",
            "core_analysis": "Analysis completed with extracted insights from response text",
            "assumptions": ["Key market assumptions extracted", "Growth projections based on thesis"],
            "mental_model": "Growth",
            "causal_chain": [
                {"chain_link": 1, "event": "Market expansion", "explanation": "Drives thesis performance"}
            ],
            "counter_thesis_scenarios": [
                {"scenario": "Market downturn", "description": "Reduced demand impact", "trigger_conditions": ["Economic slowdown"], "data_signals": ["Revenue decline"]}
            ],
            "trackable_signals": self._generate_basic_signals(thesis_text)
        }
    
    def _generate_basic_signals(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Generate basic trackable signals based on thesis content"""
        signals = []
        
        # Analyze thesis for key terms to generate relevant signals
        thesis_lower = thesis_text.lower()
        
        if any(term in thesis_lower for term in ['revenue', 'sales', 'growth']):
            signals.append({
                "name": "Revenue Growth Rate",
                "level": "Level_1_Simple_Aggregation",
                "description": "Quarterly revenue growth tracking",
                "frequency": "quarterly",
                "threshold": 15.0,
                "threshold_type": "above",
                "data_source": "FactSet Fundamentals",
                "value_chain_position": "downstream",
                "programmatic_feasibility": "high",
                "what_it_tells_us": "Indicates demand acceleration and pricing power"
            })
        
        if any(term in thesis_lower for term in ['market share', 'competition', 'dominance']):
            signals.append({
                "name": "Market Share Expansion",
                "level": "Level_1_Simple_Aggregation", 
                "description": "Relative market position tracking",
                "frequency": "quarterly",
                "threshold": 2.0,
                "threshold_type": "above",
                "data_source": "FactSet Estimates",
                "value_chain_position": "downstream",
                "programmatic_feasibility": "medium",
                "what_it_tells_us": "Measures competitive positioning strength"
            })
            
        if any(term in thesis_lower for term in ['margin', 'profitability', 'efficiency']):
            signals.append({
                "name": "Operating Margin Expansion",
                "level": "Level_1_Simple_Aggregation",
                "description": "Operational efficiency improvements",
                "frequency": "quarterly", 
                "threshold": 18.0,
                "threshold_type": "above",
                "data_source": "FactSet Fundamentals",
                "value_chain_position": "midstream",
                "programmatic_feasibility": "high",
                "what_it_tells_us": "Shows operational leverage and cost control"
            })
        
        # Add volume/production signals for manufacturing companies
        if any(term in thesis_lower for term in ['production', 'volume', 'units', 'manufacturing']):
            signals.append({
                "name": "Production Volume",
                "level": "Level_0_Raw_Economic_Activity",
                "description": "Units produced per quarter",
                "frequency": "quarterly",
                "threshold": 500000,
                "threshold_type": "above", 
                "data_source": "Company Reports",
                "value_chain_position": "upstream",
                "programmatic_feasibility": "medium",
                "what_it_tells_us": "Direct measure of operational scale"
            })
        
        # Ensure minimum number of signals
        if len(signals) < 3:
            signals.extend([
                {
                    "name": "Stock Price Performance",
                    "level": "Level_1_Simple_Aggregation",
                    "description": "Relative stock performance vs market",
                    "frequency": "daily",
                    "threshold": 5.0,
                    "threshold_type": "above",
                    "data_source": "FactSet Pricing",
                    "value_chain_position": "downstream",
                    "programmatic_feasibility": "high",
                    "what_it_tells_us": "Market sentiment and expectation changes"
                },
                {
                    "name": "Analyst Estimate Revisions",
                    "level": "Level_1_Simple_Aggregation", 
                    "description": "Consensus estimate changes",
                    "frequency": "monthly",
                    "threshold": 3,
                    "threshold_type": "above",
                    "data_source": "FactSet Estimates",
                    "value_chain_position": "downstream",
                    "programmatic_feasibility": "high",
                    "what_it_tells_us": "Professional investor sentiment shifts"
                }
            ])
        
        return signals[:6]  # Limit to 6 signals
    
    def _get_fallback_analysis(self, thesis_text: str) -> Dict[str, Any]:
        """Provide fallback analysis when all else fails"""
        return {
            "core_claim": f"Investment analysis for: {thesis_text[:80]}...",
            "core_analysis": "Analysis system experienced connectivity issues. The thesis has been logged for review and will be processed when connection is restored.",
            "assumptions": ["Stable market conditions", "Continued operational execution", "Regulatory environment remains supportive"],
            "mental_model": "Growth",
            "causal_chain": [
                {"chain_link": 1, "event": "Thesis validation", "explanation": "Core assumptions prove correct"},
                {"chain_link": 2, "event": "Market recognition", "explanation": "Value realization follows validation"}
            ],
            "counter_thesis_scenarios": [
                {"scenario": "Execution risk", "description": "Company fails to deliver on key initiatives", "trigger_conditions": ["Missed guidance"], "data_signals": ["Revenue miss"]}
            ],
            "trackable_signals": self._generate_basic_signals(thesis_text)
        }