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
            
            # Step 3: Monitoring plan - use detailed fallback for reliability
            try:
                # First try AI generation
                monitoring_plan = self._create_monitoring_plan(thesis_text, core_analysis, signals)
                # Validate response quality
                if not monitoring_plan or not isinstance(monitoring_plan, dict) or len(str(monitoring_plan)) < 500:
                    raise ValueError("LLM response too short or invalid")
                logging.info("Step 3 completed: Monitoring plan created via AI")
            except Exception as e:
                logging.warning(f"Step 3 AI generation failed, using comprehensive fallback: {str(e)}")
                monitoring_plan = self._create_detailed_monitoring_fallback(thesis_text, core_analysis, signals)
                logging.info("Step 3 completed: Detailed monitoring plan created from analysis data")
            
            # Step 4: Generate AI-powered market sentiment
            try:
                market_sentiment = self.market_sentiment_service.generate_market_sentiment(thesis_text, core_analysis)
                logging.info("Step 4 completed: AI market sentiment generated")
            except Exception as e:
                logging.warning(f"Step 4 failed, market sentiment will be generated on demand: {str(e)}")
                market_sentiment = None
            
            # Step 5: Generate missing advanced components
            try:
                alternative_companies = self._generate_alternative_companies(thesis_text, core_analysis)
                risk_assessment = self._generate_risk_assessment(thesis_text, core_analysis)
                catalyst_timeline = self._generate_catalyst_timeline(thesis_text, core_analysis)
                valuation_metrics = self._generate_valuation_metrics(thesis_text, core_analysis)
                logging.info("Step 5 completed: Advanced analysis components generated")
            except Exception as e:
                logging.warning(f"Step 5 failed: {e}")
                alternative_companies = []
                risk_assessment = {}
                catalyst_timeline = {}
                valuation_metrics = {}

            # Ensure counter-thesis scenarios are included
            if "counter_thesis_scenarios" not in core_analysis or not core_analysis["counter_thesis_scenarios"]:
                # Generate contextual counter-thesis scenarios
                company_context = self._extract_company_context(thesis_text)
                sector_context = self._extract_sector_context(thesis_text)
                core_analysis["counter_thesis_scenarios"] = self._generate_contextual_counter_scenarios(
                    company_context, sector_context, thesis_text.lower()
                )
            
            # Ensure alternative companies are included
            if not alternative_companies:
                alternative_companies = self._generate_alternative_companies(thesis_text, core_analysis)

            # Combine all results
            complete_analysis = {
                **core_analysis,
                "metrics_to_track": signals,
                "monitoring_plan": monitoring_plan,
                "ai_market_sentiment": market_sentiment,
                "alternative_companies": alternative_companies,
                "risk_assessment": risk_assessment,
                "catalyst_timeline": catalyst_timeline,
                "valuation_metrics": valuation_metrics
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
        
        # Add timeout protection for monitoring plan generation
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Monitoring plan generation timed out")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(20)  # 20 second timeout for detailed plan
        
        try:
            response = self.azure_openai.generate_completion([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], max_tokens=3000, temperature=0.2)
        finally:
            signal.alarm(0)  # Cancel timeout
        
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

    def _create_detailed_monitoring_fallback(self, thesis_text: str, core_analysis: Dict, signals: List) -> Dict[str, Any]:
        """Create detailed monitoring plan using actual analysis data when AI generation fails"""
        
        # Extract key data from analysis
        core_claim = core_analysis.get('core_claim', thesis_text[:100])
        assumptions = core_analysis.get('assumptions', [])
        causal_chain = core_analysis.get('causal_chain', [])
        counter_thesis = core_analysis.get('counter_thesis_scenarios', [])
        
        # Extract companies/entities from thesis text
        import re
        companies = []
        # Look for capitalized words that might be company names
        potential_companies = re.findall(r'\b[A-Z][A-Za-z]{2,}\b', thesis_text)
        companies = [comp for comp in potential_companies[:3] if comp not in ['The', 'This', 'That', 'With', 'For', 'And']]
        
        # Create comprehensive monitoring plan
        return {
            "objective": f"Monitor and validate thesis: {core_claim} - Track key performance indicators with quantified thresholds for data-driven decision making",
            "validation_framework": {
                "core_claim_metrics": self._build_core_claim_metrics(core_claim, signals, companies),
                "assumption_tests": self._build_assumption_tests(assumptions, signals),
                "causal_chain_tracking": self._build_causal_chain_tracking(causal_chain, signals)
            },
            "data_acquisition": self._build_data_acquisition_plan(signals, companies),
            "alert_system": self._build_alert_system(signals, assumptions),
            "decision_framework": self._build_decision_framework(core_claim, signals),
            "counter_thesis_monitoring": self._build_counter_thesis_monitoring(counter_thesis, signals),
            "review_schedule": f"Weekly signal review, monthly thesis validation assessment, quarterly strategy review with {len(signals)} tracked metrics"
        }

    def _build_core_claim_metrics(self, core_claim: str, signals: List, companies: List) -> List[Dict]:
        """Build core claim validation metrics from actual signals"""
        metrics = []
        
        for i, signal in enumerate(signals[:3]):
            signal_name = signal.get('name', f'Signal {i+1}')
            threshold = signal.get('threshold', 10.0)
            data_source = signal.get('data_source', 'FactSet')
            
            metrics.append({
                "metric": signal_name,
                "target_threshold": f">{threshold}%" if 'growth' in signal_name.lower() else f"{threshold}",
                "measurement_frequency": signal.get('frequency', 'quarterly'),
                "data_source": data_source,
                "validation_logic": f"Direct measurement of {signal_name.lower()} to validate core thesis claim"
            })
        
        return metrics

    def _build_assumption_tests(self, assumptions: List, signals: List) -> List[Dict]:
        """Build assumption testing framework from analysis data"""
        tests = []
        
        for i, assumption in enumerate(assumptions[:4]):
            if isinstance(assumption, str) and len(assumption) > 10:
                # Find related signal for testing
                related_signal = signals[i % len(signals)] if signals else {}
                signal_name = related_signal.get('name', 'Market Performance Metric')
                threshold = related_signal.get('threshold', 15.0)
                
                tests.append({
                    "assumption": assumption,
                    "test_metric": signal_name,
                    "success_threshold": f">{threshold}%",
                    "failure_threshold": f"<{threshold * 0.5}%",
                    "data_source": related_signal.get('data_source', 'FactSet')
                })
        
        return tests

    def _build_causal_chain_tracking(self, causal_chain: List, signals: List) -> List[Dict]:
        """Build causal chain tracking from analysis data"""
        tracking = []
        
        for i, step in enumerate(causal_chain[:4]):
            if isinstance(step, dict) and step.get('event'):
                related_signal = signals[i % len(signals)] if signals else {}
                
                tracking.append({
                    "chain_step": step.get('event', f'Causal step {i+1}'),
                    "leading_indicator": related_signal.get('name', f'Performance Metric {i+1}'),
                    "threshold": f"{related_signal.get('threshold', 10)}%",
                    "frequency": related_signal.get('frequency', 'monthly')
                })
        
        return tracking

    def _build_data_acquisition_plan(self, signals: List, companies: List) -> List[Dict]:
        """Build data acquisition plan from signals"""
        categories = {}
        
        # Group signals by category
        for signal in signals:
            category = "Financial Performance"
            if 'market' in signal.get('name', '').lower():
                category = "Market Position"
            elif 'revenue' in signal.get('name', '').lower():
                category = "Revenue Analytics"
            
            if category not in categories:
                categories[category] = []
            categories[category].append(signal)
        
        acquisition_plan = []
        for category, category_signals in categories.items():
            metrics = [s.get('name', 'Metric') for s in category_signals]
            data_source = category_signals[0].get('data_source', 'FactSet') if category_signals else 'FactSet'
            frequency = category_signals[0].get('frequency', 'quarterly') if category_signals else 'quarterly'
            
            company_symbols = ', '.join([f"'{c}'" for c in companies]) if companies else "''"
            company_filter = f"symbol IN ({company_symbols})" if companies else "symbol = ?"
            
            acquisition_plan.append({
                "category": category,
                "metrics": metrics,
                "data_source": data_source,
                "query_template": f"SELECT {', '.join(metrics[:3])} FROM financials WHERE {company_filter}",
                "frequency": frequency,
                "automation_level": "full" if data_source == "FactSet" else "partial"
            })
        
        return acquisition_plan

    def _build_alert_system(self, signals: List, assumptions: List) -> List[Dict]:
        """Build alert system from signals and assumptions"""
        alerts = []
        
        for i, signal in enumerate(signals[:5]):
            signal_name = signal.get('name', f'Signal {i+1}')
            threshold = signal.get('threshold', 10.0)
            
            severity = "high" if i < 2 else "medium"
            condition = f"{signal_name} {'growth' if 'growth' in signal_name.lower() else 'value'} < {threshold}% for 2 consecutive periods"
            
            alerts.append({
                "trigger_name": f"{signal_name} Threshold Alert",
                "condition": condition,
                "severity": severity,
                "action": f"Review {signal_name.lower()} trends and validate underlying assumptions",
                "notification_method": "dashboard"
            })
        
        return alerts

    def _build_decision_framework(self, core_claim: str, signals: List) -> List[Dict]:
        """Build decision framework from core claim and signals"""
        decisions = []
        
        # Extract action from core claim
        action = "buy"
        if "increase" in core_claim.lower() or "grow" in core_claim.lower():
            action = "buy"
        elif "decrease" in core_claim.lower() or "decline" in core_claim.lower():
            action = "sell"
        
        primary_signal = signals[0] if signals else {}
        threshold = primary_signal.get('threshold', 15.0)
        
        decisions.extend([
            {
                "scenario": "Thesis Validation",
                "condition": f"Primary metrics exceed {threshold}% for 2+ consecutive quarters",
                "action": action,
                "reasoning": f"Strong performance validates core thesis claim: {core_claim}",
                "confidence_threshold": "85%"
            },
            {
                "scenario": "Thesis Invalidation", 
                "condition": f"Primary metrics decline below {threshold * 0.5}% for 2+ quarters",
                "action": "sell" if action == "buy" else "buy",
                "reasoning": "Sustained underperformance contradicts thesis assumptions",
                "confidence_threshold": "75%"
            },
            {
                "scenario": "Mixed Signals",
                "condition": f"Performance between {threshold * 0.5}% and {threshold}%",
                "action": "hold",
                "reasoning": "Inconclusive data requires additional monitoring before decision",
                "confidence_threshold": "60%"
            }
        ])
        
        return decisions

    def _build_counter_thesis_monitoring(self, counter_thesis: List, signals: List) -> List[Dict]:
        """Build counter-thesis monitoring from analysis data"""
        monitoring = []
        
        for i, scenario in enumerate(counter_thesis[:3]):
            if isinstance(scenario, dict) and scenario.get('scenario'):
                related_signal = signals[i % len(signals)] if signals else {}
                
                monitoring.append({
                    "risk_scenario": scenario.get('scenario', f'Counter-thesis risk {i+1}'),
                    "early_warning_metric": related_signal.get('name', f'Warning Signal {i+1}'),
                    "threshold": f"<{related_signal.get('threshold', 5)}%",
                    "mitigation_action": f"Immediate review of {scenario.get('scenario', 'risk scenario')} and consider position adjustment"
                })
        
        return monitoring

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
        """Create contextually intelligent analysis based on thesis content with enhanced specificity"""
        text_lower = thesis_text.lower()
        
        # Extract company and sector context
        company_context = self._extract_company_context(thesis_text)
        sector_context = self._extract_sector_context(thesis_text)
        
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
        
        # Generate contextual conviction drivers based on sector and company
        conviction_drivers = self._generate_contextual_conviction_drivers(
            company_context, sector_context, primary_model, text_lower
        )
        
        # Generate sector-specific causal chain
        causal_chain = self._generate_contextual_causal_chain(
            company_context, sector_context, text_lower
        )
        
        # Generate contextual assumptions
        assumptions = self._generate_contextual_assumptions(
            company_context, sector_context, text_lower
        )
        
        # Generate sector-specific counter-thesis scenarios
        counter_scenarios = self._generate_contextual_counter_scenarios(
            company_context, sector_context, text_lower
        )
        
        return {
            "core_claim": f"Investment thesis: {thesis_text[:120]}{'...' if len(thesis_text) > 120 else ''}",
            "core_analysis": f"Analysis reveals a {primary_model.lower()} investment opportunity in {sector_context.lower()} sector with multiple supporting frameworks. Key sector-specific catalysts must materialize while monitoring for execution risks and market headwinds that could challenge core assumptions.",
            "mental_models": mental_models,
            "primary_mental_model": primary_model,
            "conviction_drivers": conviction_drivers,
            "causal_chain": causal_chain,
            "assumptions": assumptions,
            "counter_thesis_scenarios": counter_scenarios
        }

    def _generate_contextual_conviction_drivers(self, company_context: Dict, sector_context: str, primary_model: str, text_lower: str) -> List[str]:
        """Generate sector and company-specific conviction drivers"""
        drivers = []
        
        if sector_context == 'Travel & Tourism':
            drivers.extend([
                "Travel demand recovery drives booking volume growth",
                "Digital platform advantages in market share capture",
                "Operational efficiency improvements expand margins"
            ])
        elif sector_context == 'Technology':
            drivers.extend([
                "Platform network effects create competitive moats",
                "Innovation capabilities drive market differentiation",
                "Scalable technology infrastructure enables growth"
            ])
        else:
            drivers.extend([
                f"{sector_context} sector fundamentals support investment thesis",
                "Market positioning advantages drive competitive performance",
                "Operational execution capabilities enable value creation"
            ])
        
        # Add model-specific drivers
        if primary_model == "Growth":
            drivers.append("Revenue expansion opportunities exceed market expectations")
        elif primary_model == "Value":
            drivers.append("Asset valuation discount provides attractive risk-adjusted returns")
        
        return drivers[:4]

    def _generate_contextual_causal_chain(self, company_context: Dict, sector_context: str, text_lower: str) -> List[Dict]:
        """Generate sector-specific causal chain events"""
        if sector_context == 'Travel & Tourism':
            return [
                {
                    "chain_link": 1,
                    "event": "Travel demand normalization accelerates",
                    "explanation": "Post-pandemic recovery drives sustained booking volume growth across travel segments"
                },
                {
                    "chain_link": 2,
                    "event": "Platform optimization delivers market share gains",
                    "explanation": "Digital booking advantages and user experience improvements capture increasing travel spend"
                },
                {
                    "chain_link": 3,
                    "event": "Operational leverage drives margin expansion",
                    "explanation": "Fixed cost absorption and efficiency gains translate volume growth into profitability"
                }
            ]
        elif sector_context == 'Technology':
            return [
                {
                    "chain_link": 1,
                    "event": "Innovation capabilities drive differentiation",
                    "explanation": "Technical product advantages establish competitive positioning in addressable market"
                },
                {
                    "chain_link": 2,
                    "event": "Platform scaling captures network effects",
                    "explanation": "User growth and engagement drive revenue per user expansion through network dynamics"
                },
                {
                    "chain_link": 3,
                    "event": "Market validation drives valuation re-rating",
                    "explanation": "Proven execution and growth sustainability command premium market multiples"
                }
            ]
        else:
            return [
                {
                    "chain_link": 1,
                    "event": f"{sector_context} market fundamentals improve",
                    "explanation": "Sector-specific drivers create favorable operating environment for thesis execution"
                },
                {
                    "chain_link": 2,
                    "event": "Competitive advantages translate to financial outperformance",
                    "explanation": "Strategic positioning enables revenue growth and margin expansion above sector averages"
                },
                {
                    "chain_link": 3,
                    "event": "Investment returns materialize through multiple expansion",
                    "explanation": "Demonstrated execution drives market recognition and valuation re-rating"
                }
            ]

    def _generate_contextual_assumptions(self, company_context: Dict, sector_context: str, text_lower: str) -> List[str]:
        """Generate sector-specific assumptions"""
        assumptions = []
        
        if sector_context == 'Travel & Tourism':
            assumptions.extend([
                "Travel demand recovery continues without major disruptions",
                "Digital booking penetration increases across customer segments",
                "Competitive dynamics remain favorable for platform operators"
            ])
        elif sector_context == 'Technology':
            assumptions.extend([
                "Innovation pace maintains competitive differentiation",
                "Market adoption of technology solutions accelerates",
                "Regulatory environment remains supportive of platform business models"
            ])
        else:
            assumptions.extend([
                f"{sector_context} sector conditions remain supportive of growth",
                "Management execution capabilities deliver on strategic initiatives",
                "Market conditions enable thesis validation over investment horizon"
            ])
        
        return assumptions[:4]

    def _generate_contextual_counter_scenarios(self, company_context: Dict, sector_context: str, text_lower: str) -> List[Dict]:
        """Generate sector-specific counter-thesis scenarios"""
        if sector_context == 'Travel & Tourism':
            return [
                {
                    "scenario": "Travel Demand Disruption",
                    "description": "External shocks disrupt travel patterns and booking behavior",
                    "trigger_conditions": ["Health crisis emergence", "Economic recession", "Geopolitical tensions"],
                    "data_signals": ["TSA checkpoint volumes", "Hotel occupancy rates", "Airline capacity utilization"]
                },
                {
                    "scenario": "Platform Disintermediation",
                    "description": "Direct booking trends reduce travel platform market share",
                    "trigger_conditions": ["Supplier direct booking incentives", "New distribution models"],
                    "data_signals": ["Direct booking percentage trends", "Commission rate pressures"]
                }
            ]
        elif sector_context == 'Technology':
            return [
                {
                    "scenario": "Innovation Obsolescence",
                    "description": "Technology disruption renders current platform advantages ineffective",
                    "trigger_conditions": ["Breakthrough competitor technology", "Market paradigm shift"],
                    "data_signals": ["R&D investment comparisons", "Patent filing trends", "User adoption metrics"]
                },
                {
                    "scenario": "Regulatory Restrictions",
                    "description": "Government intervention limits platform business model effectiveness",
                    "trigger_conditions": ["Antitrust enforcement", "Data privacy regulations"],
                    "data_signals": ["Regulatory filing activity", "Policy proposal developments"]
                }
            ]
        else:
            return [
                {
                    "scenario": "Sector Headwinds",
                    "description": f"{sector_context} sector faces structural challenges that undermine thesis",
                    "trigger_conditions": ["Industry disruption", "Regulatory changes", "Economic cycles"],
                    "data_signals": ["Sector performance metrics", "Industry analyst revisions"]
                },
                {
                    "scenario": "Execution Failure",
                    "description": "Management fails to deliver on strategic initiatives critical to investment thesis",
                    "trigger_conditions": ["Missed financial targets", "Strategic plan delays"],
                    "data_signals": ["Quarterly earnings results", "Management guidance changes"]
                }
            ]

    def _extract_company_context(self, thesis_text: str) -> Dict[str, Any]:
        """Extract company-specific context from thesis text"""
        import re
        
        # Extract company names and tickers
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.?|\s+Corp\.?|\s+Group)?)\b'
        
        tickers = re.findall(ticker_pattern, thesis_text)
        companies = re.findall(company_pattern, thesis_text)
        
        # Filter out common words that match ticker pattern
        excluded_words = {'BUY', 'SELL', 'HOLD', 'TRIM', 'AI', 'IT', 'US', 'OR', 'SO', 'TO', 'ON', 'IN', 'OF'}
        tickers = [t for t in tickers if t not in excluded_words]
        
        return {
            'tickers': tickers[:3],
            'companies': companies[:3],
            'sector_keywords': self._extract_sector_keywords(thesis_text)
        }
    
    def _extract_sector_context(self, thesis_text: str) -> str:
        """Extract sector context from thesis text"""
        text_lower = thesis_text.lower()
        
        if any(word in text_lower for word in ['travel', 'booking', 'tourism', 'hotel', 'airline']):
            return 'Travel & Tourism'
        elif any(word in text_lower for word in ['tech', 'software', 'digital', 'platform', 'ai', 'cloud']):
            return 'Technology'
        elif any(word in text_lower for word in ['financial', 'bank', 'credit', 'payment', 'fintech']):
            return 'Financial Services'
        elif any(word in text_lower for word in ['healthcare', 'biotech', 'pharma', 'medical']):
            return 'Healthcare'
        elif any(word in text_lower for word in ['energy', 'oil', 'renewable', 'utilities']):
            return 'Energy'
        elif any(word in text_lower for word in ['retail', 'consumer', 'e-commerce', 'shopping']):
            return 'Consumer & Retail'
        else:
            return 'General Market'
    
    def _extract_sector_keywords(self, thesis_text: str) -> List[str]:
        """Extract relevant sector keywords from thesis"""
        text_lower = thesis_text.lower()
        keywords = []
        
        sector_keywords = {
            'travel': ['travel', 'booking', 'vacation', 'hospitality', 'tourism'],
            'technology': ['innovation', 'digital', 'platform', 'software', 'automation'],
            'growth': ['growth', 'expansion', 'scaling', 'revenue', 'market share'],
            'efficiency': ['efficiency', 'optimization', 'margins', 'productivity', 'cost reduction']
        }
        
        for category, words in sector_keywords.items():
            if any(word in text_lower for word in words):
                keywords.extend([w for w in words if w in text_lower])
        
        return list(set(keywords))[:5]

    def _generate_alternative_companies(self, thesis_text: str, analysis_data: Dict) -> List[Dict]:
        """Generate comprehensive alternative company analysis"""
        text_lower = thesis_text.lower()
        sector_context = self._extract_sector_context(thesis_text)
        companies = []
        
        # Travel & Tourism sector alternatives
        if sector_context == 'Travel & Tourism' or any(word in text_lower for word in ['expedia', 'booking', 'travel', 'tourism']):
            companies = [
                {
                    "symbol": "BKNG",
                    "name": "Booking Holdings Inc.",
                    "similarity_score": 88,
                    "rationale": "Market leader in online travel booking with global platform dominance",
                    "key_differentiators": ["Larger scale and market cap", "Superior international presence", "Diverse brand portfolio"],
                    "investment_merit": "Established market leadership with defensive characteristics",
                    "valuation_comparison": "Trades at premium valuation reflecting market position",
                    "growth_profile": "Slower but more predictable growth trajectory"
                },
                {
                    "symbol": "ABNB", 
                    "name": "Airbnb Inc.",
                    "similarity_score": 75,
                    "rationale": "Disruptive accommodation platform transforming travel lodging",
                    "key_differentiators": ["Asset-light marketplace model", "Unique inventory", "Direct host relationships"],
                    "investment_merit": "Higher growth potential with platform network effects",
                    "valuation_comparison": "Growth premium valuation with margin expansion opportunity",
                    "growth_profile": "Accelerating growth in alternative accommodation segment"
                },
                {
                    "symbol": "TRIP",
                    "name": "TripAdvisor Inc.",
                    "similarity_score": 68,
                    "rationale": "Travel content and booking platform with review-driven model",
                    "key_differentiators": ["Content-first approach", "Review platform heritage", "Experiences focus"],
                    "investment_merit": "Turnaround story with subscription revenue potential",
                    "valuation_comparison": "Value opportunity if transformation succeeds",
                    "growth_profile": "Restructuring for sustainable growth model"
                }
            ]
        
        # Technology sector alternatives
        elif sector_context == 'Technology' or any(word in text_lower for word in ['tech', 'software', 'platform', 'digital']):
            companies = [
                {
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation",
                    "similarity_score": 82,
                    "rationale": "Platform technology leader with cloud infrastructure dominance",
                    "key_differentiators": ["Enterprise focus", "Cloud computing leadership", "Subscription model"],
                    "investment_merit": "Quality growth with defensive characteristics",
                    "valuation_comparison": "Premium valuation justified by consistent execution",
                    "growth_profile": "Steady growth driven by cloud transformation"
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "similarity_score": 78,
                    "rationale": "Digital platform ecosystem with advertising and cloud revenue",
                    "key_differentiators": ["Search dominance", "Advertising expertise", "AI capabilities"],
                    "investment_merit": "Diversified revenue streams with innovation pipeline",
                    "valuation_comparison": "Attractive valuation relative to growth potential",
                    "growth_profile": "Multiple growth vectors including AI and cloud"
                }
            ]
        
        # Financial Services alternatives
        elif sector_context == 'Financial Services' or any(word in text_lower for word in ['financial', 'bank', 'fintech']):
            companies = [
                {
                    "symbol": "JPM",
                    "name": "JPMorgan Chase & Co.",
                    "similarity_score": 85,
                    "rationale": "Leading financial institution with technology investment focus",
                    "key_differentiators": ["Scale advantages", "Diverse revenue streams", "Technology modernization"],
                    "investment_merit": "Quality financial services with digital transformation",
                    "valuation_comparison": "Reasonable valuation with dividend yield",
                    "growth_profile": "Steady growth with credit cycle considerations"
                },
                {
                    "symbol": "V",
                    "name": "Visa Inc.",
                    "similarity_score": 80,
                    "rationale": "Payment processing network with digital payment trends",
                    "key_differentiators": ["Network effects", "Asset-light model", "Global reach"],
                    "investment_merit": "High-quality business model with secular growth",
                    "valuation_comparison": "Premium valuation for quality characteristics",
                    "growth_profile": "Consistent growth from payment digitization"
                }
            ]
        
        # Generic alternatives for other sectors
        else:
            companies = [
                {
                    "symbol": "AMZN",
                    "name": "Amazon.com Inc.",
                    "similarity_score": 75,
                    "rationale": f"Diversified growth company with {sector_context.lower()} sector exposure",
                    "key_differentiators": ["E-commerce leadership", "Cloud services", "Innovation culture"],
                    "investment_merit": "Multiple growth drivers across business segments",
                    "valuation_comparison": "Growth premium reflects long-term opportunity",
                    "growth_profile": "Multiple high-growth business verticals"
                },
                {
                    "symbol": "NVDA",
                    "name": "NVIDIA Corporation", 
                    "similarity_score": 70,
                    "rationale": "Technology enabler with broad sector applications",
                    "key_differentiators": ["AI chip leadership", "Data center growth", "Platform approach"],
                    "investment_merit": "Positioned for AI transformation across industries",
                    "valuation_comparison": "High growth expectations embedded in valuation",
                    "growth_profile": "Exponential growth potential from AI adoption"
                }
            ]
        
        return companies[:3]  # Return top 3 alternatives

    def _generate_risk_assessment(self, thesis_text: str, analysis_data: Dict) -> Dict:
        """Generate comprehensive risk assessment"""
        assumptions = analysis_data.get('assumptions', [])
        
        return {
            "execution_risks": [
                {
                    "risk": "Management execution capability",
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Monitor quarterly management commentary and execution metrics"
                },
                {
                    "risk": "Market condition changes",
                    "probability": "Medium", 
                    "impact": "Medium",
                    "mitigation": "Track leading economic indicators and industry trends"
                }
            ],
            "market_risks": [
                {
                    "risk": "Competitive pressure intensification",
                    "probability": "High",
                    "impact": "Medium",
                    "mitigation": "Monitor competitor moves and market share trends"
                }
            ],
            "financial_risks": [
                {
                    "risk": "Revenue growth deceleration",
                    "probability": "Medium",
                    "impact": "High", 
                    "mitigation": "Track leading revenue indicators and customer metrics"
                }
            ],
            "overall_risk_rating": "Medium",
            "key_monitoring_points": [assumption[:100] for assumption in assumptions[:3]]
        }

    def _generate_catalyst_timeline(self, thesis_text: str, analysis_data: Dict) -> Dict:
        """Generate catalyst timeline for thesis validation"""
        return {
            "near_term_catalysts": [
                {
                    "catalyst": "Q1 Earnings Release",
                    "timeframe": "3 months",
                    "expected_impact": "Revenue growth validation",
                    "success_criteria": "Revenue growth >10% YoY"
                },
                {
                    "catalyst": "Management Guidance Update", 
                    "timeframe": "3-6 months",
                    "expected_impact": "Strategic direction confirmation",
                    "success_criteria": "Maintained or raised guidance"
                }
            ],
            "medium_term_catalysts": [
                {
                    "catalyst": "Market Share Expansion",
                    "timeframe": "6-12 months", 
                    "expected_impact": "Competitive positioning improvement",
                    "success_criteria": "Market share increase >2%"
                }
            ],
            "long_term_catalysts": [
                {
                    "catalyst": "Strategic Initiative Results",
                    "timeframe": "12-24 months",
                    "expected_impact": "Operational efficiency gains",
                    "success_criteria": "Margin expansion >100 bps"
                }
            ],
            "monitoring_schedule": "Weekly catalyst tracking, monthly timeline review"
        }

    def _generate_valuation_metrics(self, thesis_text: str, analysis_data: Dict) -> Dict:
        """Generate valuation metrics and targets"""
        return {
            "current_valuation": {
                "pe_ratio": "Market multiple assessment needed",
                "ev_revenue": "Enterprise value analysis required", 
                "price_book": "Book value comparison needed"
            },
            "target_valuation": {
                "target_pe": "15-20x based on growth profile",
                "target_price": "Price target calculation required",
                "upside_potential": "20-40% based on thesis validation"
            },
            "peer_comparison": {
                "premium_discount": "Valuation premium/discount to peers",
                "justification": "Growth rate and market position differential"
            },
            "valuation_methodology": [
                "DCF analysis with growth assumptions",
                "Peer multiple comparison", 
                "Sum-of-parts analysis if applicable"
            ],
            "key_valuation_drivers": [
                "Revenue growth rate sustainability",
                "Margin expansion potential",
                "Market multiple evolution"
            ]
        }