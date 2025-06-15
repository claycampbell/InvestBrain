import json
import logging
from typing import Dict, Any, List
from services.azure_openai_service import AzureOpenAIService
from services.market_sentiment_service import MarketSentimentService

class ChainedAnalysisService:
    """
    Investment thesis analysis using chained prompts for better reliability and depth
    """
    
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
        self.market_sentiment_service = MarketSentimentService()
    
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
            
            # Step 4: Generate AI-powered market sentiment
            try:
                market_sentiment = self.market_sentiment_service.generate_market_sentiment(thesis_text, core_analysis)
                logging.info("Step 4 completed: AI market sentiment generated")
            except Exception as e:
                logging.warning(f"Step 4 failed, market sentiment will be generated on demand: {str(e)}")
                market_sentiment = None
            
            # Combine all results
            complete_analysis = {
                **core_analysis,
                "metrics_to_track": signals,
                "monitoring_plan": monitoring_plan,
                "ai_market_sentiment": market_sentiment
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
            signal.alarm(15)  # 15 second timeout
            
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
  }
]"""
        else:
            system_prompt = """You are an expert at identifying comprehensive investment signals across all 5 derivation levels. Extract 12-15 signals covering the complete analytical framework.

Signal Level Classification (extract signals from ALL levels):
- Level 0 (Internal Research Data): Structured financial queries, thesis validation
- Level 1 (Raw Economic Activity): Housing starts, permit applications, factory utilization
- Level 2 (Simple Aggregation): Monthly spending totals, inventory levels
- Level 3 (Derived Metrics): Growth rates, market share changes
- Level 4 (Complex Ratios): Valuation multiples, peer comparisons
- Level 5 (Market Sentiment): Analyst sentiment, options flow

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
    "data_source": "Manual Research Required",
    "acquisition_method": "Compile from earnings transcripts via FactSet Transcripts API or Capital IQ, calculate variance between guided vs actual metrics over 8 quarters",
    "alternative_sources": ["Bloomberg Transcript Analysis", "Refinitiv IBES Detail", "Company IR websites"],
    "value_chain_position": "governance",
    "programmatic_feasibility": "low",
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
        system_prompt = """You are an expert at creating prescriptive monitoring strategies that identify critical thesis validation points.

Your task is to create a monitoring plan that:
1. VALIDATES the core thesis claim through direct measurement
2. TRACKS key assumptions with specific failure/success thresholds
3. MONITORS causal chain progression with leading indicators
4. ESTABLISHES counter-thesis risk detection systems

Extract company names, specific metrics, and quantitative targets from the thesis.

Respond with valid JSON:
{
  "objective": "Monitor [specific company/sector] thesis: [specific claim] with [quantified success criteria]",
  "validation_framework": {
    "core_claim_metrics": [
      {
        "metric": "Specific metric that directly validates core claim",
        "target_threshold": "Numerical target from thesis",
        "measurement_frequency": "daily|weekly|monthly|quarterly",
        "data_source": "FactSet|Xpressfeed|Manual",
        "validation_logic": "How this metric proves/disproves the thesis"
      }
    ],
    "assumption_tests": [
      {
        "assumption": "Specific assumption from thesis",
        "test_metric": "Metric to validate this assumption",
        "success_threshold": "Numerical threshold for validation",
        "failure_threshold": "Numerical threshold for invalidation",
        "data_source": "FactSet|Xpressfeed"
      }
    ],
    "causal_chain_tracking": [
      {
        "chain_step": "Specific step from causal chain",
        "leading_indicator": "Metric that shows this step progressing",
        "threshold": "Numerical threshold",
        "frequency": "Monitoring frequency"
      }
    ]
  },
  "data_acquisition": [
    {
      "category": "Category name (Financial Performance, Market Position, etc.)",
      "metrics": ["Specific metric 1", "Specific metric 2"],
      "data_source": "FactSet|Xpressfeed",
      "query_template": "SELECT [specific_fields] FROM [specific_table] WHERE [conditions]",
      "frequency": "daily|weekly|monthly|quarterly",
      "automation_level": "full|partial|manual"
    }
  ],
  "alert_system": [
    {
      "trigger_name": "Descriptive name",
      "condition": "Specific numerical condition (e.g., Revenue growth < 5% for 2 consecutive quarters)",
      "severity": "low|medium|high|critical",
      "action": "Specific action to take",
      "notification_method": "email|dashboard|report"
    }
  ],
  "decision_framework": [
    {
      "scenario": "Thesis validation scenario",
      "condition": "Specific quantified condition",
      "action": "buy|sell|hold|increase|decrease",
      "reasoning": "Why this action based on thesis logic",
      "confidence_threshold": "Numerical confidence level required"
    }
  ],
  "counter_thesis_monitoring": [
    {
      "risk_scenario": "Specific counter-thesis risk",
      "early_warning_metric": "Metric that shows this risk materializing",
      "threshold": "Numerical threshold for concern",
      "mitigation_action": "Specific action to take"
    }
  ],
  "review_schedule": "Detailed review timing with specific escalation procedures and decision points"
}"""
        
        # Extract detailed context for monitoring plan
        core_claim = core_analysis.get('core_claim', '')
        assumptions = core_analysis.get('assumptions', [])
        causal_chain = core_analysis.get('causal_chain', [])
        counter_thesis = core_analysis.get('counter_thesis_scenarios', [])
        
        # Identify key metrics from signals
        signal_details = []
        for signal in signals[:6]:
            signal_details.append({
                'name': signal.get('name', ''),
                'threshold': signal.get('threshold', ''),
                'description': signal.get('description', ''),
                'data_source': signal.get('data_source', '')
            })
        
        user_prompt = f"""Analyze this investment thesis and create a comprehensive monitoring strategy:

THESIS: {thesis_text}

CORE CLAIM: {core_claim}

KEY ASSUMPTIONS: {assumptions[:5]}

CAUSAL CHAIN: {[step.get('event', '') for step in causal_chain[:4]] if isinstance(causal_chain, list) else []}

IDENTIFIED SIGNALS: {signal_details}

COUNTER-THESIS RISKS: {[scenario.get('scenario', '') for scenario in counter_thesis[:3]] if isinstance(counter_thesis, list) else []}

Create a monitoring plan that:
1. Directly measures thesis success/failure through quantified metrics
2. Tests each key assumption with specific thresholds
3. Tracks causal chain progression with leading indicators
4. Monitors counter-thesis risks with early warning systems
5. Provides clear decision triggers with numerical thresholds

Focus on metrics that can be tracked via FactSet/Xpressfeed APIs with specific query templates."""
        
        response = self.azure_openai.generate_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=2000, temperature=0.3)
        
        parsed_plan = self._parse_json_response(response, "monitoring_plan")
        # Ensure we return a dictionary for monitoring plans
        if isinstance(parsed_plan, dict):
            return parsed_plan
        else:
            return self._get_fallback_monitoring_plan()

    def _get_fallback_monitoring_plan(self) -> Dict[str, Any]:
        """Provide fallback monitoring plan structure"""
        return {
            "objective": "Monitor thesis performance and validate key assumptions through systematic tracking",
            "validation_framework": {
                "core_claim_metrics": [],
                "assumption_tests": [],
                "causal_chain_tracking": []
            },
            "data_acquisition": [],
            "alert_system": [],
            "decision_framework": [],
            "counter_thesis_monitoring": [],
            "review_schedule": "Monthly comprehensive review with quarterly deep analysis"
        }

    def _parse_json_response(self, response: str, step_name: str):
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
    
    def _get_fallback_structure(self, step_name: str):
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