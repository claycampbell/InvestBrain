import json
import logging
from typing import Dict, Any, List
from services.azure_openai_service import AzureOpenAIService

class ChainedAnalysisService:
    """
    Investment thesis analysis using chained prompts for better reliability and depth
    """
    
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
    
    def analyze_thesis(self, thesis_text: str) -> Dict[str, Any]:
        """Analyze investment thesis using sequential chained prompts"""
        try:
            logging.info(f"Starting chained analysis for thesis: {thesis_text[:50]}...")
            
            # Step 1: Core thesis analysis
            try:
                core_analysis = self._analyze_core_thesis(thesis_text)
                logging.info("Step 1 completed: Core thesis analysis")
            except Exception as e:
                logging.warning(f"Step 1 failed, using fallback: {str(e)}")
                core_analysis = self._get_fallback_structure("core_analysis")
                core_analysis["core_claim"] = f"Investment thesis: {thesis_text[:100]}..."
            
            # Step 2: Signal extraction
            try:
                signals = self._extract_signals(thesis_text, core_analysis)
                logging.info(f"Step 2 completed: Extracted {len(signals)} signals")
            except Exception as e:
                logging.warning(f"Step 2 failed, using fallback: {str(e)}")
                signals = self._get_fallback_signals(thesis_text)
            
            # Step 3: Monitoring plan
            try:
                monitoring_plan = self._create_monitoring_plan(thesis_text, core_analysis, signals)
                logging.info("Step 3 completed: Monitoring plan created")
            except Exception as e:
                logging.warning(f"Step 3 failed, using fallback: {str(e)}")
                monitoring_plan = self._get_fallback_structure("monitoring_plan")
            
            # Combine all results
            complete_analysis = {
                **core_analysis,
                "metrics_to_track": signals,
                "monitoring_plan": monitoring_plan
            }
            
            logging.info("Chained analysis completed successfully")
            return complete_analysis
            
        except Exception as e:
            logging.error(f"Error in chained thesis analysis: {str(e)}")
            raise

    def _analyze_core_thesis(self, thesis_text: str) -> Dict[str, Any]:
        """Step 1: Analyze core thesis components"""
        system_prompt = """You are an expert investment analyst. Analyze the core components of investment theses.

Respond with valid JSON only:
{
  "core_claim": "One sentence investment claim",
  "core_analysis": "Detailed analysis of risk/reward dynamics and key uncertainties",
  "causal_chain": [
    {"chain_link": 1, "event": "Specific market condition or business development", "explanation": "Detailed explanation of how this affects the thesis"},
    {"chain_link": 2, "event": "Next logical consequence or market reaction", "explanation": "How this connects to the previous link and impacts outcomes"}
  ],
  "assumptions": ["Key assumption 1", "Key assumption 2"],
  "mental_model": "Growth|Value|Cyclical|Disruption",
  "counter_thesis_scenarios": [
    {"scenario": "Risk scenario title", "description": "Brief explanation", "trigger_conditions": ["Condition 1"], "data_signals": ["Signal 1"]}
  ]
}"""
        
        user_prompt = f"""Analyze this investment thesis: {thesis_text}

Extract the core investment logic, key assumptions, and risk scenarios. Focus on detailed causal relationships and chainlinked events that show how each step connects to the next."""
        
        response = self.azure_openai.generate_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=2500)
        
        return self._parse_json_response(response, "core_analysis")

    def _extract_signals(self, thesis_text: str, core_analysis: Dict) -> List[Dict[str, Any]]:
        """Step 2: Extract trackable signals with value chain positioning"""
        system_prompt = """You are an expert at identifying trackable investment signals. Focus on Level 0-1 signals closest to raw economic activity.

Respond with valid JSON array:
[
  {
    "name": "Specific signal name",
    "type": "Level_0_Raw_Activity|Level_1_Simple_Aggregation", 
    "description": "Detailed signal description",
    "frequency": "daily|weekly|monthly|quarterly",
    "threshold": 5.0,
    "threshold_type": "above|below|change_percent",
    "data_source": "FactSet|Xpressfeed",
    "value_chain_position": "upstream|midstream|downstream"
  }
]"""
        
        core_claim = core_analysis.get('core_claim', '')
        assumptions = core_analysis.get('assumptions', [])
        
        user_prompt = f"""Based on this thesis: {thesis_text}

Core claim: {core_claim}
Key assumptions: {', '.join(assumptions[:3])}

Identify 5-6 specific trackable signals that are closest to raw economic activity. Categorize each signal by value chain position:
- Upstream: Production, manufacturing, supply chain signals
- Midstream: Distribution, pricing, market dynamics
- Downstream: Consumer adoption, end-user metrics"""
        
        response = self.azure_openai.generate_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=2000)
        
        signals = self._parse_json_response(response, "signals")
        return signals if isinstance(signals, list) else []

    def _create_monitoring_plan(self, thesis_text: str, core_analysis: Dict, signals: List) -> Dict[str, Any]:
        """Step 3: Create comprehensive prescriptive monitoring plan"""
        system_prompt = """You are an expert at creating prescriptive monitoring strategies with specific thresholds and actions.

Respond with valid JSON:
{
  "objective": "Specific monitoring objective with clear success/failure criteria",
  "data_pulls": [
    {
      "category": "Category name",
      "metrics": ["Specific metric 1", "Specific metric 2"],
      "data_source": "FactSet|Xpressfeed", 
      "query_template": "SELECT specific_data FROM table WHERE conditions",
      "frequency": "daily|weekly|monthly|quarterly"
    }
  ],
  "alert_logic": [
    {
      "frequency": "daily|weekly|monthly|quarterly",
      "condition": "Specific threshold condition with numbers",
      "action": "Specific action to take when triggered"
    }
  ],
  "decision_triggers": [
    {
      "condition": "Specific exit/entry condition with thresholds",
      "action": "buy|sell|hold with specific reasoning"
    }
  ],
  "review_schedule": "Detailed review timing and escalation procedures"
}"""
        
        signal_names = [s.get('name', '') for s in signals[:4]]
        core_claim = core_analysis.get('core_claim', '')
        
        user_prompt = f"""Create a prescriptive monitoring plan for: {thesis_text}

Core claim: {core_claim}
Key signals to monitor: {', '.join(signal_names)}

Create:
- 4-5 data pull categories with specific metrics and SQL query templates
- 5-6 alert conditions with exact thresholds and corresponding actions
- 3-4 decision triggers with specific buy/sell/hold conditions
- Include specific data sources (FactSet/Xpressfeed) and frequencies"""
        
        response = self.azure_openai.generate_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=2500)
        
        return self._parse_json_response(response, "monitoring_plan")

    def _parse_json_response(self, response: str, step_name: str) -> Dict[str, Any]:
        """Parse JSON response with fallback handling"""
        try:
            parsed = json.loads(response)
            logging.info(f"Successfully parsed JSON for {step_name}")
            return parsed
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    logging.info(f"Extracted JSON for {step_name}")
                    return parsed
                except json.JSONDecodeError:
                    pass
            
            logging.warning(f"Failed to parse JSON for {step_name}")
            return self._get_fallback_structure(step_name)
    
    def _get_fallback_structure(self, step_name: str) -> Dict[str, Any]:
        """Provide fallback structure when JSON parsing fails"""
        if step_name == "signals":
            return []
        elif step_name == "monitoring_plan":
            return {
                "objective": "Monitor thesis performance and key assumptions",
                "data_pulls": [],
                "alert_logic": [],
                "decision_triggers": [],
                "review_schedule": "Monthly review"
            }
        else:  # core_analysis
            return {
                "core_claim": "Investment thesis analysis in progress",
                "core_analysis": "Analysis pending - processing error occurred",
                "causal_chain": [],
                "assumptions": ["Analysis in progress"],
                "mental_model": "Growth",
                "counter_thesis_scenarios": []
            }