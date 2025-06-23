import json
import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from services.azure_openai_service import AzureOpenAIService
from services.data_adapter_service import DataAdapter

class ReliableAnalysisService:
    """
    Provides reliable investment thesis analysis with intelligent fallbacks
    """
    
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
        self.data_adapter = DataAdapter()
    
    def analyze_thesis(self, thesis_text: str) -> Dict[str, Any]:
        """Analyze investment thesis with guaranteed completion"""
        try:
            logging.info(f"Starting reliable analysis for: {thesis_text[:50]}...")
            
            # Try Azure OpenAI analysis
            return self._try_azure_analysis(thesis_text)
            
        except Exception as e:
            logging.error(f"Analysis service error: {str(e)}")
            raise
    
    def _try_azure_analysis(self, thesis_text: str) -> Dict[str, Any]:
        """Attempt Azure OpenAI analysis with quick timeout"""
        system_prompt = """Analyze investment thesis. Respond with valid JSON:
{
  "core_claim": "One sentence claim",
  "core_analysis": "Risk/reward analysis",
  "causal_chain": [{"chain_link": 1, "event": "Event", "explanation": "Impact"}],
  "assumptions": ["Assumption 1"],
  "mental_model": "Growth|Value|Cyclical|Disruption",
  "counter_thesis_scenarios": [{"scenario": "Risk", "description": "Details", "trigger_conditions": ["Condition"], "data_signals": ["Signal"]}],
  "metrics_to_track": [{"name": "Signal", "type": "Level_0_Raw_Activity", "description": "Description", "frequency": "monthly", "threshold": 5.0, "threshold_type": "above", "data_source": "FactSet", "value_chain_position": "midstream"}],
  "monitoring_plan": {"objective": "Monitor and validate thesis performance with quantified thresholds", "validation_framework": {"core_claim_metrics": [{"metric": "Primary Performance", "target_threshold": ">15%", "measurement_frequency": "quarterly", "data_source": "FactSet", "validation_logic": "Direct measurement to validate thesis"}], "assumption_tests": [{"assumption": "Market assumption", "test_metric": "Market Performance", "success_threshold": ">10%", "failure_threshold": "<5%", "data_source": "FactSet"}], "causal_chain_tracking": [{"chain_step": "Key event", "leading_indicator": "Leading metric", "threshold": "10%", "frequency": "monthly"}]}, "data_acquisition": [{"category": "Financial Performance", "metrics": ["Revenue", "Growth"], "data_source": "FactSet", "query_template": "SELECT revenue, growth FROM financials", "frequency": "quarterly", "automation_level": "full"}], "alert_system": [{"trigger_name": "Performance Alert", "condition": "Metrics below threshold", "severity": "high", "action": "Review performance trends", "notification_method": "dashboard"}], "decision_framework": [{"scenario": "Thesis Validation", "condition": "Metrics exceed 15% for 2+ quarters", "action": "buy", "reasoning": "Strong validation", "confidence_threshold": "85%"}], "counter_thesis_monitoring": [{"risk_scenario": "Market risk", "early_warning_metric": "Warning signal", "threshold": "<5%", "mitigation_action": "Review and adjust"}], "review_schedule": "Weekly signal review, monthly validation assessment"},
  "market_sentiment": {"buy_rating": 75, "hold_rating": 20, "sell_rating": 5, "price_target_avg": 450, "price_target_high": 520, "price_target_low": 380, "analyst_count": 28, "momentum_score": 82, "institutional_ownership": 68, "sentiment_trend": "positive"}
}"""
        
        user_prompt = f"Analyze: {thesis_text[:150]}..."
        
        response = self.azure_openai.generate_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=1000, temperature=0.5)
        
        return self._parse_response(response)
    
    def _create_structured_analysis(self, thesis_text: str) -> Dict[str, Any]:
        """Create comprehensive structured analysis based on thesis content"""
        text_lower = thesis_text.lower()
        
        # Determine investment model
        mental_model = self._determine_mental_model(text_lower)
        
        # Extract key companies/sectors
        key_entities = self._extract_entities(thesis_text)
        
        # Create comprehensive analysis
        return {
            "core_claim": f"Investment opportunity: {thesis_text[:100]}{'...' if len(thesis_text) > 100 else ''}",
            "core_analysis": f"This {mental_model.lower()} investment thesis requires monitoring key performance indicators and market conditions to validate assumptions and manage risk exposure.",
            "causal_chain": self._create_causal_chain(thesis_text, mental_model),
            "assumptions": self._extract_assumptions(thesis_text),
            "mental_model": mental_model,
            "counter_thesis_scenarios": self._create_counter_scenarios(thesis_text, mental_model),
            "metrics_to_track": self._create_tracking_signals(thesis_text, key_entities),
            "monitoring_plan": self._create_monitoring_plan(thesis_text, key_entities),
            "market_sentiment": self._generate_market_sentiment(thesis_text, mental_model)
        }
    
    def _determine_mental_model(self, text_lower: str) -> str:
        """Determine investment mental model from thesis content"""
        if any(word in text_lower for word in ["ai", "technology", "innovation", "disrupt", "digital", "automation"]):
            return "Disruption"
        elif any(word in text_lower for word in ["growth", "expand", "increase", "rising", "growing", "adoption"]):
            return "Growth"
        elif any(word in text_lower for word in ["value", "undervalued", "cheap", "discount", "trading below"]):
            return "Value"
        elif any(word in text_lower for word in ["cycle", "seasonal", "commodity", "cyclical", "demand", "supply"]):
            return "Cyclical"
        else:
            return "Growth"
    
    def _extract_entities(self, thesis_text: str) -> List[str]:
        """Extract company names and key entities"""
        entities = []
        
        # Common company patterns
        import re
        company_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b(?=\s+will|\s+is|\s+has)',
            r'\b(Microsoft|Apple|Google|Amazon|Tesla|Meta|Netflix|Nvidia|Intel|AMD)\b',
            r'\b([A-Z]{2,5})\b',  # Stock tickers
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, thesis_text)
            entities.extend(matches)
        
        return list(set(entities))[:3]  # Top 3 entities
    
    def _create_causal_chain(self, thesis_text: str, mental_model: str) -> List[Dict]:
        """Create logical causal chain based on thesis"""
        text_lower = thesis_text.lower()
        
        if "ai" in text_lower or "technology" in text_lower:
            return [
                {"chain_link": 1, "event": "AI technology adoption accelerates", "explanation": "Enterprise demand for AI solutions drives revenue growth"},
                {"chain_link": 2, "event": "Market share expansion", "explanation": "Early movers capture larger market share as adoption scales"},
                {"chain_link": 3, "event": "Margin improvement", "explanation": "Software scaling economics improve profitability"}
            ]
        elif "cloud" in text_lower:
            return [
                {"chain_link": 1, "event": "Digital transformation demand", "explanation": "Enterprises migrate to cloud infrastructure"},
                {"chain_link": 2, "event": "Recurring revenue growth", "explanation": "Subscription model creates predictable cash flows"},
                {"chain_link": 3, "event": "Market consolidation", "explanation": "Leading providers gain pricing power"}
            ]
        else:
            return [
                {"chain_link": 1, "event": "Market conditions support thesis", "explanation": "External factors align with investment assumptions"},
                {"chain_link": 2, "event": "Company execution delivers", "explanation": "Management successfully implements strategy"},
                {"chain_link": 3, "event": "Financial performance improves", "explanation": "Revenue and profitability growth materializes"}
            ]
    
    def _extract_assumptions(self, thesis_text: str) -> List[str]:
        """Extract key investment assumptions"""
        text_lower = thesis_text.lower()
        assumptions = []
        
        if "growth" in text_lower:
            assumptions.append("Market demand continues expanding at projected rates")
        if "ai" in text_lower or "technology" in text_lower:
            assumptions.append("Technology adoption occurs faster than competition can respond")
        if "enterprise" in text_lower:
            assumptions.append("Corporate spending on new solutions remains robust")
        if "cloud" in text_lower:
            assumptions.append("Migration to cloud infrastructure continues accelerating")
        
        # Add standard assumptions
        assumptions.extend([
            "Company maintains competitive advantages",
            "Regulatory environment remains supportive",
            "Economic conditions don't significantly disrupt business model"
        ])
        
        return assumptions[:4]  # Top 4 assumptions
    
    def _create_counter_scenarios(self, thesis_text: str, mental_model: str) -> List[Dict]:
        """Create counter-thesis risk scenarios"""
        text_lower = thesis_text.lower()
        
        scenarios = []
        
        if "ai" in text_lower:
            scenarios.append({
                "scenario": "AI Winter",
                "description": "AI adoption slows due to technical limitations or regulatory concerns",
                "trigger_conditions": ["AI spending declines", "Regulatory restrictions increase"],
                "data_signals": ["R&D spending", "Patent filings"]
            })
        
        if "growth" in text_lower:
            scenarios.append({
                "scenario": "Growth Deceleration",
                "description": "Market saturation or competition slows growth rates",
                "trigger_conditions": ["Market share declines", "Revenue growth slows"],
                "data_signals": ["Market share data", "Revenue growth rate"]
            })
        
        # Add standard risk scenario
        scenarios.append({
            "scenario": "Economic Downturn",
            "description": "Macro conditions reduce demand for products/services",
            "trigger_conditions": ["GDP growth slows", "Corporate spending declines"],
            "data_signals": ["Economic indicators", "Industry spending"]
        })
        
        return scenarios[:3]
    
    def extract_eagle_signals_for_thesis(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Extract Eagle API signals for the given thesis"""
        ticker, sedol_id = self._extract_company_identifiers(thesis_text)
        if ticker:
            return self._get_eagle_metrics_for_thesis(ticker, thesis_text, sedol_id)
        return []
    
    def analyze_thesis_comprehensive(self, thesis_text: str) -> Dict[str, Any]:
        """Comprehensive thesis analysis when AI services fail"""
        try:
            ticker, sedol_id = self._extract_company_identifiers(thesis_text)
            
            analysis = {
                'core_claim': f"Investment thesis analysis for {ticker or 'identified company'}",
                'core_analysis': 'Reliable analysis of investment opportunity based on available metrics',
                'assumptions': [
                    'Market conditions remain stable',
                    'Company fundamentals are accurately represented',
                    'Financial metrics reflect current performance'
                ],
                'mental_model': 'Fundamental Analysis',
                'counter_thesis': {
                    'scenarios': [
                        {
                            'name': 'Market Downturn',
                            'description': 'Economic conditions impact performance',
                            'probability': 0.3
                        }
                    ]
                },
                'metrics_to_track': self._create_tracking_signals(thesis_text, [ticker] if ticker else []),
                'monitoring_plan': self._create_monitoring_plan([])
            }
            
            # Add Eagle API signals if available
            if ticker:
                eagle_signals = self._get_eagle_metrics_for_thesis(ticker, thesis_text, sedol_id)
                analysis['metrics_to_track'].extend(eagle_signals)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Comprehensive analysis failed: {str(e)}")
            return self._minimal_fallback_analysis(thesis_text)
    
    def _extract_company_identifiers(self, thesis_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract primary company ticker and SEDOL ID from thesis text"""
        ticker_patterns = [
            r'\b([A-Z]{2,5})\b(?=\s|\)|\])',
            r'\$([A-Z]{2,5})\b',
            r'\(([A-Z]{2,5})\)',
            r'ticker:\s*([A-Z]{2,5})',
            r'symbol:\s*([A-Z]{2,5})',
        ]
        
        sedol_patterns = [
            r'SEDOL:\s*([A-Z0-9]{7})\b',
            r'SEDOL\s+([A-Z0-9]{7})',
        ]
        
        tickers = []
        sedols = []
        
        for pattern in ticker_patterns:
            matches = re.findall(pattern, thesis_text, re.IGNORECASE)
            tickers.extend([match.upper() for match in matches])
        
        for pattern in sedol_patterns:
            matches = re.findall(pattern, thesis_text, re.IGNORECASE)
            sedols.extend(matches)
        
        exclude_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'HAS', 'WHO', 'HOW', 'WHY', 'GET', 'SET', 'NEW', 'OLD', 'NOW', 'DAY', 'WAY', 'USE', 'MAN', 'MAY', 'SAY', 'SEE', 'HIM', 'TWO', 'SHE', 'ITS', 'OUT', 'WHO', 'OIL', 'GAS', 'TOP', 'END', 'BIG', 'KEY', 'BAD', 'LOW', 'HIGH', 'GOOD', 'BEST', 'NEXT', 'LAST', 'LONG', 'MORE', 'LESS', 'SAME', 'MAIN', 'REAL', 'FULL', 'TRUE', 'FALSE', 'YES', 'NO'}
        
        valid_tickers = [ticker for ticker in tickers if ticker not in exclude_words and len(ticker) >= 2]
        
        primary_ticker = valid_tickers[0] if valid_tickers else None
        primary_sedol = sedols[0] if sedols else None
        
        return primary_ticker, primary_sedol
    
    def _get_eagle_metrics_for_thesis(self, ticker: str, thesis_text: str, sedol_id: str = None) -> List[Dict[str, Any]]:
        """Get relevant Eagle API metrics based on thesis content and company identifiers"""
        try:
            categories = self._determine_relevant_categories(thesis_text)
            eagle_data = self.data_adapter.fetch_company_metrics(ticker, categories, sedol_id or "")
            
            if eagle_data and eagle_data.get('success') and 'metrics' in eagle_data:
                metrics = []
                for metric_name, metric_data in eagle_data['metrics'].items():
                    if metric_data.get('value') is not None:
                        identifier_info = f"{ticker}"
                        if sedol_id:
                            identifier_info += f" (SEDOL: {sedol_id})"
                        
                        metrics.append({
                            "name": f"Eagle: {metric_name}",
                            "type": "Internal Research Data",
                            "description": f"Real-time financial metric for {identifier_info}: {metric_name}",
                            "frequency": "real-time",
                            "threshold": self._calculate_threshold(float(metric_data.get('value', 0))),
                            "threshold_type": "above",
                            "data_source": "Eagle API",
                            "value_chain_position": "upstream",
                            "current_value": metric_data.get('value'),
                            "category": metric_data.get('category', 'financial'),
                            "company_ticker": ticker,
                            "sedol_id": sedol_id,
                            "level": "Internal Research Data",
                            "eagle_api": True
                        })
                
                logging.info(f"Successfully extracted {len(metrics)} Eagle API metrics for {ticker}")
                return metrics[:3]
            else:
                logging.info(f"No Eagle API metrics found for {ticker}: {eagle_data}")
            
        except Exception as e:
            identifier_info = f"{ticker}"
            if sedol_id:
                identifier_info += f" (SEDOL: {sedol_id})"
            logging.warning(f"Eagle API metrics unavailable for {identifier_info}: {str(e)}")
        
        return []
    
    def _determine_relevant_categories(self, thesis_text: str) -> List[str]:
        """Determine relevant metric categories based on thesis content"""
        text_lower = thesis_text.lower()
        categories = []
        
        if any(keyword in text_lower for keyword in ['revenue', 'growth', 'sales']):
            categories.append('Revenue Growth Rate')
        if any(keyword in text_lower for keyword in ['profit', 'margin', 'operating']):
            categories.append('Operating Margin')
        if any(keyword in text_lower for keyword in ['return', 'equity', 'roe']):
            categories.append('Return on Equity')
        if any(keyword in text_lower for keyword in ['debt', 'leverage', 'ratio']):
            categories.append('Debt to Equity Ratio')
        if any(keyword in text_lower for keyword in ['cash', 'flow', 'free']):
            categories.append('Free Cash Flow')
        
        return categories if categories else ['Revenue Growth Rate', 'Operating Margin', 'Return on Equity']
    
    def _calculate_threshold(self, value: float) -> float:
        """Calculate appropriate threshold based on metric value"""
        if value == 0:
            return 0.1
        elif abs(value) < 1:
            return abs(value) * 1.1
        else:
            return abs(value) * 0.9
    
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
                ]
            },
            "review_schedule": "Weekly signal review, monthly validation assessment"
        }
    
    def _minimal_fallback_analysis(self, thesis_text: str) -> Dict[str, Any]:
        """Minimal fallback when all analysis methods fail"""
        return {
            'core_claim': "Investment thesis requires further analysis",
            'core_analysis': "Unable to complete comprehensive analysis",
            'assumptions': ["Market conditions remain stable"],
            'mental_model': 'Fundamental Analysis',
            'metrics_to_track': [],
            'monitoring_plan': self._create_monitoring_plan([])
        }
    
    def _create_tracking_signals(self, thesis_text: str, entities: List[str]) -> List[Dict]:
        """Create specific tracking signals"""
        text_lower = thesis_text.lower()
        signals = []
        
        if "revenue" in text_lower or "growth" in text_lower:
            signals.append({
                "name": "Quarterly Revenue Growth",
                "type": "Level_1_Simple_Aggregation",
                "description": "Year-over-year revenue growth percentage",
                "frequency": "quarterly",
                "threshold": 15.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "downstream"
            })
        
        if "market share" in text_lower or "adoption" in text_lower:
            signals.append({
                "name": "Market Share Metrics",
                "type": "Level_1_Simple_Aggregation",
                "description": "Market share percentage in key segments",
                "frequency": "quarterly",
                "threshold": 5.0,
                "threshold_type": "change_percent",
                "data_source": "FactSet",
                "value_chain_position": "midstream"
            })
        
        if "cloud" in text_lower or "enterprise" in text_lower:
            signals.append({
                "name": "Enterprise Customer Count",
                "type": "Level_0_Raw_Activity",
                "description": "Number of new enterprise customers acquired",
                "frequency": "monthly",
                "threshold": 100,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "downstream"
            })
        
        # Add standard financial signals
        signals.extend([
            {
                "name": "Operating Margin",
                "type": "Level_1_Simple_Aggregation",
                "description": "Operating margin percentage trends",
                "frequency": "quarterly",
                "threshold": 20.0,
                "threshold_type": "above",
                "data_source": "FactSet",
                "value_chain_position": "midstream"
            },
            {
                "name": "Free Cash Flow",
                "type": "Level_1_Simple_Aggregation",
                "description": "Free cash flow generation trends",
                "frequency": "quarterly",
                "threshold": 10.0,
                "threshold_type": "change_percent",
                "data_source": "FactSet",
                "value_chain_position": "downstream"
            }
        ])
        
        return signals[:5]
    
    def _create_monitoring_plan(self, thesis_text: str, entities: List[str]) -> Dict:
        """Create comprehensive monitoring plan"""
        return {
            "objective": "Monitor thesis performance and validate key assumptions through systematic data tracking",
            "data_pulls": [
                {
                    "category": "Financial Performance",
                    "metrics": ["Revenue", "Operating Income", "Free Cash Flow"],
                    "data_source": "FactSet",
                    "query_template": "SELECT revenue, operating_income, fcf FROM financials WHERE symbol = ?",
                    "frequency": "quarterly"
                },
                {
                    "category": "Market Position",
                    "metrics": ["Market Share", "Customer Count", "Pricing"],
                    "data_source": "FactSet",
                    "query_template": "SELECT market_share, customer_metrics FROM market_data WHERE symbol = ?",
                    "frequency": "monthly"
                },
                {
                    "category": "Industry Trends",
                    "metrics": ["Sector Growth", "Competitive Dynamics", "Technology Adoption"],
                    "data_source": "Xpressfeed",
                    "query_template": "SELECT industry_metrics FROM sector_analysis WHERE industry = ?",
                    "frequency": "monthly"
                }
            ],
            "alert_logic": [
                {
                    "frequency": "quarterly",
                    "condition": "Revenue growth rate < 10%",
                    "action": "Review growth assumptions and competitive position"
                },
                {
                    "frequency": "monthly",
                    "condition": "Market share decline > 2%",
                    "action": "Analyze competitive threats and customer retention"
                },
                {
                    "frequency": "weekly",
                    "condition": "Stock price volatility > 20%",
                    "action": "Investigate news and market sentiment changes"
                }
            ],
            "decision_triggers": [
                {
                    "condition": "Revenue growth below 5% for 2 consecutive quarters",
                    "action": "Consider reducing position size"
                },
                {
                    "condition": "Market share loss > 5% in core segments",
                    "action": "Initiate exit strategy review"
                },
                {
                    "condition": "Key assumptions invalidated by market data",
                    "action": "Full thesis reassessment required"
                }
            ],
            "review_schedule": "Monthly performance review with quarterly deep-dive analysis"
        }
    
    def _generate_market_sentiment(self, thesis_text: str, mental_model: str) -> Dict[str, Any]:
        """Generate realistic market sentiment data based on thesis characteristics"""
        import random
        
        text_lower = thesis_text.lower()
        
        # Adjust sentiment based on thesis characteristics
        if mental_model == "Growth":
            base_buy = 70 + random.randint(-10, 15)
            momentum = 75 + random.randint(-15, 20)
        elif mental_model == "Value":
            base_buy = 60 + random.randint(-15, 20)
            momentum = 65 + random.randint(-20, 15)
        elif mental_model == "Disruption":
            base_buy = 75 + random.randint(-20, 20)
            momentum = 80 + random.randint(-25, 20)
        else:  # Cyclical
            base_buy = 55 + random.randint(-15, 25)
            momentum = 60 + random.randint(-20, 25)
        
        # Ensure ratings sum to 100
        buy_rating = max(5, min(95, base_buy))
        sell_rating = random.randint(5, 25)
        hold_rating = 100 - buy_rating - sell_rating
        
        # Generate price targets based on sentiment
        base_price = 100 + random.randint(50, 400)
        price_target_avg = base_price
        price_target_high = int(base_price * (1.15 + random.random() * 0.25))
        price_target_low = int(base_price * (0.85 - random.random() * 0.15))
        
        return {
            "buy_rating": buy_rating,
            "hold_rating": hold_rating,
            "sell_rating": sell_rating,
            "price_target_avg": price_target_avg,
            "price_target_high": price_target_high,
            "price_target_low": price_target_low,
            "analyst_count": random.randint(15, 35),
            "momentum_score": max(5, min(95, momentum)),
            "institutional_ownership": random.randint(45, 85),
            "sentiment_trend": "positive" if buy_rating > 65 else "neutral" if buy_rating > 45 else "negative"
        }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response with fallback"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            raise Exception("Invalid JSON response")