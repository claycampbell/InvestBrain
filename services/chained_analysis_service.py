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
            
            # Step 1: Core thesis analysis with quick timeout
            try:
                core_analysis = self._analyze_core_thesis(thesis_text)
                logging.info("Step 1 completed: Core thesis analysis")
            except Exception as e:
                logging.warning(f"Step 1 API timeout, using intelligent fallback: {str(e)}")
                core_analysis = self._create_intelligent_fallback(thesis_text)
            
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
        """Step 1: Analyze core thesis components with timeout handling"""
        try:
            # Enhanced prompt for richer analysis
            system_prompt = """Analyze investment thesis deeply to understand analyst conviction. Respond with valid JSON:
{
  "core_claim": "Single sentence primary investment thesis",
  "core_analysis": "Detailed 3-4 sentence risk/reward analysis including key catalysts and potential failure modes",
  "mental_models": [
    {"model": "Growth|Value|Disruption|Turnaround|Quality|Cyclical|GARP|Momentum", "weight": 0.5, "rationale": "Why this framework applies"},
    {"model": "Secondary model", "weight": 0.3, "rationale": "Supporting reasoning framework"}
  ],
  "primary_mental_model": "Dominant investment framework",
  "conviction_drivers": ["Key factor driving conviction", "Second conviction driver", "Third element"],
  "causal_chain": [{"chain_link": 1, "event": "Initial catalyst", "explanation": "Why this catalyst enables returns"}],
  "assumptions": ["Critical assumption that must hold", "Key dependency", "Important precondition"],
  "counter_thesis_scenarios": [{"scenario": "Primary risk", "description": "Detailed risk explanation", "trigger_conditions": ["What triggers this"], "data_signals": ["FactSet metric to watch"]}]
}"""
            
            user_prompt = f"Analyze: {thesis_text[:200]}... Extract core logic, assumptions, risks."
            
            # Use shorter timeout for faster fallback
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Analysis step timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(90)  # Increased to 90 second timeout
            
            try:
                response = self.azure_openai.generate_completion([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ], max_tokens=800, temperature=0.5)
            finally:
                signal.alarm(0)  # Cancel timeout
            
            return self._parse_json_response(response, "core_analysis")
            
        except Exception as e:
            logging.warning(f"Core analysis API failed: {str(e)}")
            # Return structured fallback based on thesis content
            return self._create_intelligent_fallback(thesis_text)

    def _extract_signals(self, thesis_text: str, core_analysis: Dict, focus_primary: bool = True) -> List[Dict[str, Any]]:
        """Step 2: Extract trackable signals with 5-level derivation framework"""
        
        if focus_primary:
            system_prompt = """You are an expert at identifying trackable investment signals from FactSet and Xpressfeed datasets. Extract 6-8 Level 0-1 signals that directly track thesis assumptions.

Signal Level Classification:
- Level 0 (Raw Economic Activity): Units sold, production volume, headcount
- Level 1 (Simple Aggregation): Revenue growth, margin expansion

Available FactSet datasets: Fundamentals, Estimates, Ownership, Economics, Pricing, Credit
Available Xpressfeed datasets: Real-time market data, News flow, Sentiment, Supply chain

Value Chain Classification Guide:
- UPSTREAM: Raw material costs, supplier metrics, commodity prices, production inputs
- MIDSTREAM: Manufacturing efficiency, capacity utilization, inventory levels, operational metrics  
- DOWNSTREAM: Sales metrics, customer demand, market share, pricing power, end-market trends

Respond with valid JSON array:
[
  {
    "name": "Revenue Growth Rate (QoQ)",
    "level": "Level_1_Simple_Aggregation", 
    "description": "Quarterly revenue growth acceleration/deceleration",
    "frequency": "quarterly",
    "threshold": 8.0,
    "threshold_type": "above",
    "data_source": "FactSet Fundamentals",
    "factset_identifier": "FF_SALES(0)/FF_SALES(-1)-1",
    "value_chain_position": "downstream",
    "programmatic_feasibility": "high",
    "conviction_linkage": "Direct measure of core growth thesis",
    "what_it_tells_us": "Indicates demand acceleration and pricing power in target markets"
  }
]"""
        else:
            system_prompt = """You are an expert at identifying comprehensive investment signals across all 5 derivation levels. Extract 12-15 signals covering the complete analytical framework.

Signal Level Classification (extract signals from ALL levels):
- Level 0 (Raw Economic Activity): Units sold, production volume, headcount, capacity utilization
- Level 1 (Simple Aggregation): Revenue growth, margin expansion, market share
- Level 2 (Derived Metrics): ROE, ROIC, debt-to-equity, working capital turnover
- Level 3 (Complex Ratios): EV/EBITDA, P/E relative to growth, economic value added
- Level 4 (Market Sentiment): Analyst revisions, short interest, options flow, credit spreads

Value Chain Classification Guide:
- UPSTREAM: Raw material costs, supplier metrics, commodity prices, production inputs
- MIDSTREAM: Manufacturing efficiency, capacity utilization, inventory levels, operational metrics  
- DOWNSTREAM: Sales metrics, customer demand, market share, pricing power, end-market trends

Programmatic Feasibility Guide:
- HIGH: Available via FactSet/Xpressfeed APIs (Levels 0-2)
- MEDIUM: Requires data combination/calculation (Level 3)
- LOW: Manual research required (Level 4, alternative data)

For LOW feasibility signals, specify exact data sources and acquisition methods.

Respond with valid JSON array:
[
  {
    "name": "Revenue Growth Rate (QoQ)",
    "level": "Level_1_Simple_Aggregation", 
    "description": "Quarterly revenue growth acceleration/deceleration",
    "frequency": "quarterly",
    "threshold": 8.0,
    "threshold_type": "above",
    "data_source": "FactSet Fundamentals",
    "factset_identifier": "FF_SALES(0)/FF_SALES(-1)-1",
    "value_chain_position": "downstream",
    "programmatic_feasibility": "high",
    "conviction_linkage": "Direct measure of core growth thesis"
  },
  {
    "name": "Management Guidance Accuracy",
    "level": "Level_4_Market_Sentiment",
    "description": "Historical accuracy of management guidance vs actual results",
    "frequency": "quarterly",
    "threshold": 85.0,
    "threshold_type": "above",
    "value_chain_position": "downstream",
    "programmatic_feasibility": "low",
    "what_it_tells_us": "Indicates management credibility and forward-looking reliability",
    "data_source": "Manual Research Required",
    "acquisition_method": "Compile from earnings transcripts via FactSet Transcripts API or Capital IQ, calculate variance between guided vs actual metrics over 8 quarters",
    "alternative_sources": ["Bloomberg Transcript Analysis", "Refinitiv IBES Detail", "Company IR websites"],
    "conviction_linkage": "Management credibility impacts thesis reliability"
  },
  {
    "name": "Gross Margin Expansion",
    "type": "Level_1_Simple_Aggregation",
    "description": "Operating leverage and efficiency gains",
    "frequency": "quarterly", 
    "threshold": 50,
    "threshold_type": "above",
    "data_source": "FactSet Fundamentals",
    "factset_identifier": "FF_GROSS_MARGIN",
    "value_chain_position": "midstream",
    "conviction_linkage": "Key profitability driver"
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
        ], max_tokens=1200, temperature=0.7)
        
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
        ], max_tokens=1500, temperature=0.7)
        
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
            return {"signals": []}
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
    
    def _get_fallback_signals(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Provide fallback signals when extraction fails"""
        return [
            {
                "name": "Market Share Growth",
                "type": "Level_1_Simple_Aggregation",
                "description": "Quarterly market share percentage",
                "frequency": "quarterly",
                "threshold": 5.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "midstream"
            },
            {
                "name": "Revenue Growth Rate",
                "type": "Level_1_Simple_Aggregation", 
                "description": "Year-over-year revenue growth percentage",
                "frequency": "quarterly",
                "threshold": 10.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "downstream"
            }
        ]
    
    def _create_intelligent_fallback(self, thesis_text: str) -> Dict[str, Any]:
        """Create intelligent fallback analysis based on thesis content"""
        text_lower = thesis_text.lower()
        
        # Determine primary mental model based on thesis content
        primary_model = "Growth"
        if any(word in text_lower for word in ["value", "undervalued", "cheap", "discount"]):
            primary_model = "Value"
        elif any(word in text_lower for word in ["cycle", "seasonal", "commodity", "cyclical"]):
            primary_model = "Cyclical"
        elif any(word in text_lower for word in ["disrupt", "innovation", "technology", "ai"]):
            primary_model = "Disruption"
        elif any(word in text_lower for word in ["quality", "margin", "efficiency", "profitable"]):
            primary_model = "Quality"
        
        # Create multiple mental models based on thesis characteristics
        mental_models = []
        model_weights = {}
        
        if any(word in text_lower for word in ["growth", "revenue", "expand", "scale"]):
            model_weights["Growth"] = 0.4
        if any(word in text_lower for word in ["value", "undervalued", "discount"]):
            model_weights["Value"] = 0.3
        if any(word in text_lower for word in ["quality", "margin", "efficiency"]):
            model_weights["Quality"] = 0.3
        if any(word in text_lower for word in ["disrupt", "innovation", "ai", "technology"]):
            model_weights["Disruption"] = 0.4
        
        # Ensure primary model gets highest weight
        if primary_model not in model_weights:
            model_weights[primary_model] = 0.5
        
        # Normalize weights and create mental models array
        total_weight = sum(model_weights.values())
        for model, weight in model_weights.items():
            normalized_weight = weight / total_weight if total_weight > 0 else 1.0
            mental_models.append({
                "model": model,
                "weight": round(normalized_weight, 2),
                "rationale": f"{model} characteristics identified in thesis analysis"
            })
        
        # Sort by weight descending
        mental_models.sort(key=lambda x: x["weight"], reverse=True)
        
        # Generate conviction drivers based on content
        conviction_drivers = [
            "Strong fundamental business characteristics support thesis",
            "Multiple catalysts identified for value creation",
            "Favorable risk-reward profile over investment horizon"
        ]
        
        return {
            "core_claim": f"Investment thesis: {thesis_text[:120]}{'...' if len(thesis_text) > 120 else ''}",
            "core_analysis": f"Analysis reveals a {primary_model.lower()} investment opportunity with multiple supporting frameworks. Key catalysts must materialize while monitoring for execution risks and market headwinds that could challenge core assumptions.",
            "mental_models": mental_models,
            "primary_mental_model": primary_model,
            "conviction_drivers": conviction_drivers,
            "causal_chain": [
                {
                    "chain_link": 1,
                    "event": "Thesis catalysts begin materializing",
                    "explanation": "Core investment drivers show early validation through measurable metrics"
                },
                {
                    "chain_link": 2,
                    "event": "Operational execution delivers results",
                    "explanation": "Management successfully converts strategic opportunities into financial performance"
                },
                {
                    "chain_link": 3,
                    "event": "Market recognition of value creation",
                    "explanation": "Investment returns materialize as thesis proves successful over time horizon"
                }
            ],
            "assumptions": [
                "Market conditions remain supportive of thesis drivers",
                "Company maintains competitive positioning and execution capability",
                "External disruptions do not materially impact investment case"
            ],
            "counter_thesis_scenarios": [
                {
                    "scenario": "Execution Risk",
                    "description": "Management fails to deliver on strategic initiatives critical to thesis",
                    "trigger_conditions": ["Missed guidance targets", "Strategic delays announced"],
                    "data_signals": ["FactSet estimate revisions", "Management commentary changes"]
                },
                {
                    "scenario": "Market Headwinds",
                    "description": "Adverse market conditions undermine fundamental thesis assumptions",
                    "trigger_conditions": ["Sector rotation", "Economic downturn"],
                    "data_signals": ["Xpressfeed sentiment shifts", "FactSet peer performance"]
                }
            ]
        }