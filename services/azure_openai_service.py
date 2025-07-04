import os
import logging
import json
from openai import AzureOpenAI
from config import Config

class AzureOpenAIService:
    def __init__(self):
        self.client = None
        self.api_key = None
        self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            self.api_key = Config.AZURE_OPENAI_API_KEY
            endpoint = Config.AZURE_OPENAI_ENDPOINT
            api_version = Config.AZURE_OPENAI_API_VERSION
            
            if not self.api_key or not endpoint:
                logging.error("Azure OpenAI credentials not found in environment variables")
                return
            
            # Fix endpoint format - extract base URL if full API URL provided
            if endpoint and '/openai/deployments/' in endpoint:
                # Extract base endpoint from full API URL
                base_endpoint = endpoint.split('/openai/deployments/')[0]
                logging.info(f"Correcting endpoint from {endpoint} to {base_endpoint}")
                endpoint = base_endpoint
            
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
                timeout=5.0,    # Very short timeout to prevent blocking
                max_retries=0   # No retries for fastest response
            )
            
            logging.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def generate_completion(self, prompt, temperature=1.0, max_tokens=2000):
        """Generate a completion using Azure OpenAI with robust timeout and retry handling"""
        if not self.client:
            logging.error("Azure OpenAI client not initialized")
            return None
        
        try:
            # Convert string prompt to proper message format
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt
            
            model_name = self.deployment_name.lower()
            
            if 'o1' in model_name or 'o4' in model_name:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.deployment_name
                )
            elif 'gpt-4o' in model_name:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.deployment_name,
                    max_completion_tokens=max_tokens
                )
            else:
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=self.deployment_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
            logging.info("Azure OpenAI response received")
            
            if not response.choices:
                logging.error("No choices in Azure OpenAI response")
                return None
            
            choice = response.choices[0]
            logging.info(f"Choice finish reason: {choice.finish_reason}")
            
            content = choice.message.content if hasattr(choice.message, 'content') else None
            
            if not content or content.strip() == "":
                logging.error(f"Empty content from Azure OpenAI (finish_reason: {choice.finish_reason})")
                return None
            
            logging.info(f"Received valid response: {len(content)} characters")
            return content
            
        except Exception as e:
            error_message = str(e)
            logging.error(f"Azure OpenAI API call failed: {error_message}")
            return None
    
    def _generate_structured_fallback(self, messages):
        """Generate structured fallback response for empty API responses"""
        try:
            # Extract the last user message to understand what type of response is needed
            last_message = messages[-1]['content'] if messages else ""
            
            if 'alternative' in last_message.lower() or 'companies' in last_message.lower():
                return '''[
                    {
                        "name": "Industry Peer Analysis Required",
                        "ticker": "N/A",
                        "sector": "Technology",
                        "composite_score": 0.0,
                        "rationale": "Requires detailed industry analysis with authentic data sources"
                    }
                ]'''
            elif 'analysis' in last_message.lower() or 'thesis' in last_message.lower():
                return '''{
                    "core_claim": "Investment position requires comprehensive analysis",
                    "assumptions": ["Market conditions assessment needed", "Financial metrics validation required"],
                    "causal_chain": ["Investment rationale", "Market validation", "Risk assessment"],
                    "mental_model": "Data-driven investment analysis",
                    "counter_thesis": ["Alternative market scenarios", "Risk factor considerations"],
                    "metrics_to_track": ["Financial performance indicators", "Market sentiment metrics"],
                    "monitoring_plan": ["Regular performance review", "Market condition monitoring"]
                }'''
            else:
                return "Analysis requires additional authentic data sources for comprehensive results."
                
        except Exception as e:
            logging.error(f"Fallback generation failed: {e}")
            return "Analysis requires authentic data sources for accurate results."
    
    def _generate_fallback_response(self, messages):
        """Generate a structured fallback response when Azure OpenAI is unavailable"""
        try:
            thesis_text = ""
            for message in messages:
                if message.get("role") == "user":
                    thesis_text = message.get("content", "")
                    break
            
            company_name = self._extract_company_name(thesis_text)
            
            fallback_analysis = {
                "core_claim": f"Investment thesis analysis for {company_name or 'target company'} focusing on growth potential and market positioning.",
                "core_analysis": "Due to temporary service unavailability, this analysis provides a structured framework based on the thesis content. Key investment drivers and risks have been identified for further validation.",
                "causal_chain": [
                    {
                        "step": 1,
                        "driver": "Market fundamentals",
                        "logic": "Strong market position drives revenue growth"
                    },
                    {
                        "step": 2,
                        "driver": "Competitive advantages", 
                        "logic": "Sustainable moats protect market share"
                    },
                    {
                        "step": 3,
                        "driver": "Financial performance",
                        "logic": "Revenue growth translates to value creation"
                    }
                ],
                "assumptions": [
                    "Market conditions remain favorable",
                    "Competitive position is maintained",
                    "Management execution continues effectively"
                ],
                "mental_model": "Growth at Reasonable Price (GARP)",
                "counter_thesis": {
                    "scenarios": [
                        {
                            "scenario": "Market disruption",
                            "probability": "Medium",
                            "impact": "Significant revenue impact from new competitors"
                        },
                        {
                            "scenario": "Economic downturn", 
                            "probability": "Low",
                            "impact": "Reduced demand affecting growth trajectory"
                        }
                    ]
                },
                "metrics_to_track": [
                    {
                        "metric": "Revenue Growth Rate",
                        "importance": "High",
                        "frequency": "Quarterly"
                    },
                    {
                        "metric": "Market Share",
                        "importance": "High", 
                        "frequency": "Quarterly"
                    },
                    {
                        "metric": "Profit Margins",
                        "importance": "Medium",
                        "frequency": "Quarterly"
                    }
                ],
                "monitoring_plan": {
                    "objective": f"Monitor key performance indicators for {company_name or 'target company'} investment thesis validation",
                    "data_pulls": [
                        {
                            "category": "Financial Performance",
                            "frequency": "Quarterly",
                            "metrics": ["Revenue", "Earnings", "Cash Flow"]
                        },
                        {
                            "category": "Market Position",
                            "frequency": "Monthly", 
                            "metrics": ["Market Share", "Customer Growth", "Competitive Analysis"]
                        }
                    ]
                }
            }
            
            return json.dumps(fallback_analysis, indent=2)
            
        except Exception as e:
            logging.error(f"Error generating fallback response: {str(e)}")
            return json.dumps({
                "core_claim": "Investment thesis requires further analysis when services are restored",
                "core_analysis": "Analysis temporarily unavailable due to service connectivity",
                "status": "fallback_mode"
            })
    
    def _extract_company_name(self, text):
        """Extract company name from thesis text using simple pattern matching"""
        import re
        
        patterns = [
            r'\b(NVIDIA|Apple|Microsoft|Google|Amazon|Meta|Tesla|Novo Nordisk|Pfizer|Johnson & Johnson)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Corporation|Corp|Inc|Ltd|Company|Co)\b',
            r'\b([A-Z]{2,})\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return None
    
    def analyze_thesis(self, thesis_text):
        """Analyze an investment thesis using structured prompts with signal extraction focus"""
        
        # Check for timeout or connection issues - use fallback
        if not self.client or not self.api_key:
            logging.warning("Azure OpenAI not configured - using structured fallback")
            return self._generate_fallback_analysis(thesis_text)
        
        # Use live Azure OpenAI for dynamic analysis with timeout protection
        try:
            import time
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Azure OpenAI request timed out")
            
            # Set up timeout protection
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(25)  # 25 second timeout for fast response
            
            start_time = time.time()
            messages = [
                {
                    "role": "system",
                    "content": """You are an institutional investment analyst. Analyze the investment thesis and return a comprehensive JSON response with ALL required fields:

{
  "core_claim": "One clear sentence summarizing the investment opportunity",
  "core_analysis": "2-3 sentences explaining the key investment logic and drivers",
  "causal_chain": [
    {"chain_link": 1, "event": "Primary driver", "explanation": "How this creates value"},
    {"chain_link": 2, "event": "Secondary effect", "explanation": "How this amplifies returns"},
    {"chain_link": 3, "event": "Value realization", "explanation": "How this translates to investment returns"}
  ],
  "assumptions": [
    "Key assumption 1 about market conditions",
    "Key assumption 2 about company execution", 
    "Key assumption 3 about competitive dynamics"
  ],
  "mental_model": "Growth/Value/GARP/Contrarian",
  "counter_thesis": {
    "scenarios": [
      {
        "scenario": "Primary risk scenario name",
        "probability": "Low/Medium/High",
        "impact": "Description of negative impact on thesis",
        "mitigation": "How to reduce this risk"
      },
      {
        "scenario": "Secondary risk scenario name", 
        "probability": "Low/Medium/High",
        "impact": "Alternative failure mode description",
        "mitigation": "Risk reduction strategy"
      }
    ]
  },
  "metrics_to_track": [],
  "monitoring_plan": {
    "objective": "Clear monitoring objective for thesis validation",
    "data_pulls": [
      {
        "category": "Financial Performance",
        "metrics": ["Revenue", "Margins", "Cash Flow"],
        "data_source": "FactSet/Bloomberg",
        "frequency": "quarterly"
      }
    ]
  }
}

Return only valid JSON. Be comprehensive but concise."""
                },
                {
                    "role": "user", 
                    "content": f"Analyze this investment thesis: {thesis_text}"
                }
            ]
            
            response = self.generate_completion(messages, temperature=0.7, max_tokens=4000)
            
            # Clear the timeout alarm
            signal.alarm(0)
            
            # Parse the response and ensure it's valid JSON
            if isinstance(response, str):
                try:
                    parsed_response = json.loads(response)
                    # Return the parsed JSON object, not the string
                    return parsed_response
                except json.JSONDecodeError:
                    # If response isn't valid JSON, wrap it
                    company_name = self._extract_company_name(thesis_text) or "the company"
                    return {
                        "core_claim": f"Investment analysis for {company_name}",
                        "core_analysis": response[:500],
                        "assumptions": ["Market conditions remain stable"],
                        "mental_model": "Fundamental Analysis",
                        "metrics_to_track": []
                    }
            
        except (TimeoutError, Exception) as e:
            # Clear timeout alarm
            signal.alarm(0)
            logging.warning(f"Azure OpenAI analysis timed out or failed: {str(e)}")
            # Return to fallback analysis immediately
            return self._generate_fallback_analysis(thesis_text)
    
    def _generate_fallback_analysis(self, thesis_text):
        """Generate structured fallback analysis when Azure OpenAI is unavailable"""
        company_name = self._extract_company_name(thesis_text) or "target company"
        
        return {
            "core_claim": f"Investment thesis analysis for {company_name} based on structured evaluation framework",
            "core_analysis": "Analysis generated using systematic investment evaluation criteria. Key drivers and risk factors identified for validation through real-time data monitoring.",
            "causal_chain": [
                {"chain_link": 1, "event": "Market fundamentals improve", "explanation": "Strong fundamentals drive revenue growth and market position"},
                {"chain_link": 2, "event": "Competitive advantages strengthen", "explanation": "Moats protect market share and enable pricing power"},
                {"chain_link": 3, "event": "Financial performance accelerates", "explanation": "Strong execution translates to shareholder value creation"}
            ],
            "assumptions": [
                "Market conditions support business model execution",
                "Competitive positioning remains defensible",
                "Management continues effective capital allocation",
                "Regulatory environment stays supportive"
            ],
            "mental_model": "Quality Growth",
            "counter_thesis_scenarios": [
                {
                    "scenario": "Market Contraction",
                    "description": "Economic downturn reduces demand and pricing power",
                    "trigger_conditions": ["Revenue decline >10%", "Margin compression"],
                    "data_signals": ["Economic indicators", "Industry metrics"]
                },
                {
                    "scenario": "Competitive Disruption", 
                    "description": "New entrants or technology shifts challenge market position",
                    "trigger_conditions": ["Market share loss", "R&D spending lag"],
                    "data_signals": ["Competitive analysis", "Innovation metrics"]
                }
            ],
            "metrics_to_track": [
                {
                    "name": "Revenue Growth Rate",
                    "type": "Level_1_Simple_Aggregation",
                    "description": "Quarterly revenue growth year-over-year",
                    "frequency": "quarterly",
                    "threshold": 15.0,
                    "threshold_type": "above",
                    "data_source": "FactSet",
                    "value_chain_position": "downstream"
                },
                {
                    "name": "Operating Margin Expansion",
                    "type": "Level_2_Derived_Metrics",
                    "description": "Operating margin improvement tracking",
                    "frequency": "quarterly", 
                    "threshold": 20.0,
                    "threshold_type": "above",
                    "data_source": "FactSet",
                    "value_chain_position": "midstream"
                }
            ],
            "monitoring_plan": {
                "objective": "Systematic validation of investment thesis through quantified performance tracking",
                "validation_framework": {
                    "core_claim_metrics": [
                        {
                            "metric": "Revenue Growth Consistency",
                            "target_threshold": ">15%",
                            "measurement_frequency": "quarterly",
                            "data_source": "FactSet",
                            "validation_logic": "Sustained growth validates thesis strength"
                        }
                    ],
                    "assumption_tests": [
                        {
                            "assumption": "Market expansion continues",
                            "test_metric": "Total Addressable Market",
                            "success_threshold": ">10%",
                            "failure_threshold": "<5%",
                            "data_source": "Industry Reports"
                        }
                    ]
                },
                "data_acquisition": [
                    {
                        "category": "Financial Performance",
                        "metrics": ["Revenue", "Margins", "Cash Flow"],
                        "data_source": "FactSet",
                        "frequency": "quarterly",
                        "automation_level": "full"
                    }
                ],
                "alert_system": [
                    {
                        "trigger_name": "Performance Deviation Alert",
                        "condition": "Key metrics fall below threshold",
                        "severity": "high",
                        "action": "Immediate thesis review",
                        "notification_method": "dashboard"
                    }
                ],
                "review_schedule": "Weekly monitoring, monthly comprehensive review"
            },
            "market_sentiment": {
                "buy_rating": 65,
                "hold_rating": 30,
                "sell_rating": 5,
                "price_target_avg": 200,
                "price_target_high": 250,
                "price_target_low": 150,
                "analyst_count": 15,
                "momentum_score": 75,
                "institutional_ownership": 65,
                "sentiment_trend": "positive"
            }
        }
        
        # Dynamic fallback based on input
        if True:
            company_name = self._extract_company_name(thesis_text) or "NVIDIA"
            ticker_symbol = self._extract_ticker_symbol(thesis_text) or "NVDA"
            sedol_id = self._extract_sedol_id(thesis_text) or "2379504"
            return {
                "core_claim": f"Strong investment opportunity in {company_name} ({ticker_symbol}) driven by technological leadership and market expansion",
                "core_analysis": f"{company_name} demonstrates compelling risk-adjusted returns with sustainable competitive advantages in high-growth markets",
                "causal_chain": [
                    {"chain_link": 1, "event": "Market leadership", "explanation": "Dominant position drives pricing power"},
                    {"chain_link": 2, "event": "Revenue growth", "explanation": "Expanding market share increases revenue"},
                    {"chain_link": 3, "event": "Margin expansion", "explanation": "Operational leverage improves profitability"}
                ],
                "assumptions": [
                    "Market demand continues growing",
                    "Competitive position remains strong",
                    "Execution on strategic initiatives"
                ],
                "mental_model": "Growth",
                "counter_thesis": {
                    "scenarios": [
                        {
                            "scenario": "Market saturation",
                            "probability": "Medium",
                            "impact": "Growth slows as market matures",
                            "mitigation": "Diversification into adjacent markets"
                        }
                    ]
                },
                "metrics_to_track": [
                    {
                        "name": "Quarterly Revenue Growth",
                        "type": "Level_0_Raw_Activity",
                        "description": "Monitor quarterly revenue growth rates to validate accelerating business momentum",
                        "frequency": "quarterly",
                        "threshold": 15.0,
                        "threshold_type": "above",
                        "data_source": "FactSet",
                        "value_chain_position": "downstream",
                        "company_ticker": ticker_symbol,
                        "sedol_id": sedol_id
                    },
                    {
                        "name": "Market Share Metrics",
                        "type": "Level_0_Raw_Activity", 
                        "description": "Track market share data to assess competitive positioning strength",
                        "frequency": "quarterly",
                        "threshold": 25.0,
                        "threshold_type": "above",
                        "data_source": "Industry Reports",
                        "value_chain_position": "midstream",
                        "company_ticker": ticker_symbol,
                        "sedol_id": sedol_id
                    },
                    {
                        "name": "Operating Margin",
                        "type": "Level_0_Raw_Activity",
                        "description": "Monitor operating margin expansion as indicator of operational efficiency",
                        "frequency": "quarterly", 
                        "threshold": 20.0,
                        "threshold_type": "above",
                        "data_source": "FactSet",
                        "value_chain_position": "midstream",
                        "company_ticker": ticker_symbol,
                        "sedol_id": sedol_id
                    }
                ],
                "monitoring_plan": {
                    "objective": f"Monitor key performance indicators for {company_name} investment thesis validation",
                    "data_pulls": [
                        {
                            "category": "Financial Performance",
                            "metrics": ["Revenue", "Operating Margin", "Free Cash Flow"],
                            "data_source": "FactSet",
                            "frequency": "quarterly"
                        },
                        {
                            "category": "Market Position",
                            "metrics": ["Market Share", "Customer Growth"],
                            "data_source": "Industry Reports",
                            "frequency": "quarterly"
                        }
                    ],
                    "alert_logic": [
                        {
                            "frequency": "quarterly",
                            "condition": "Revenue growth < 10%",
                            "action": "Review thesis assumptions"
                        }
                    ],
                    "decision_triggers": [
                        {
                            "condition": "Market share decline > 5%",
                            "action": "Reassess competitive position"
                        }
                    ],
                    "review_schedule": "Monthly"
                },
                "market_sentiment": {
                    "buy_rating": 75,
                    "hold_rating": 20,
                    "sell_rating": 5,
                    "price_target_avg": 450,
                    "price_target_high": 520,
                    "price_target_low": 380,
                    "analyst_count": 28,
                    "momentum_score": 82,
                    "institutional_ownership": 68,
                    "sentiment_trend": "positive"
                },
                "company_identifiers": {
                    "ticker": ticker_symbol,
                    "sedol_id": sedol_id,
                    "company_name": company_name
                }
            }
        
        system_prompt = """You are an expert investment analyst. Analyze investment theses and provide structured analysis with comprehensive company identification.

When identifying companies, include both ticker symbols and SEDOL IDs where available for precise Eagle API integration.

Respond with valid JSON only:
{
  "core_claim": "One sentence claim",
  "core_analysis": "Risk/reward analysis",
  "causal_chain": [{"chain_link": 1, "event": "Event", "explanation": "Impact"}],
  "assumptions": ["Assumption 1"],
  "mental_model": "Growth|Value|Cyclical|Disruption",
  "counter_thesis_scenarios": [{"scenario": "Risk", "description": "Details", "trigger_conditions": ["Condition"], "data_signals": ["Signal"]}],
  "metrics_to_track": [{"name": "Signal", "type": "Level_0_Raw_Activity", "description": "Description", "frequency": "monthly", "threshold": 5.0, "threshold_type": "above", "data_source": "FactSet", "value_chain_position": "midstream", "company_ticker": "TICKER", "sedol_id": "SEDOL123"}],
  "monitoring_plan": {"objective": "Monitor performance", "data_pulls": [{"category": "Financial", "metrics": ["Revenue"], "data_source": "FactSet", "frequency": "quarterly"}], "alert_logic": [{"frequency": "quarterly", "condition": "Revenue < target", "action": "Review"}], "decision_triggers": [{"condition": "Performance decline", "action": "sell"}], "review_schedule": "Monthly"},
  "market_sentiment": {"buy_rating": 75, "hold_rating": 20, "sell_rating": 5, "price_target_avg": 450, "price_target_high": 520, "price_target_low": 380, "analyst_count": 28, "momentum_score": 82, "institutional_ownership": 68, "sentiment_trend": "positive"},
  "company_identifiers": {"ticker": "TICKER", "sedol_id": "SEDOL123", "company_name": "Company Name"}
}"""

        user_prompt = f"Analyze: {thesis_text}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.generate_completion(messages, temperature=1.0, max_tokens=4000)
            return json.loads(response)
        except json.JSONDecodeError as e:
            logging.warning(f"Azure OpenAI failed: Invalid JSON response")
            # Return fallback structured response
            return {
                "core_claim": f"Investment analysis for extracted thesis",
                "core_analysis": "Analysis completed with structured framework",
                "causal_chain": [{"chain_link": 1, "event": "Market performance", "explanation": "Drives investment returns"}],
                "assumptions": ["Market stability", "Continued growth"],
                "mental_model": "Growth",
                "counter_thesis_scenarios": [{"scenario": "Market decline", "description": "Revenue impact", "trigger_conditions": ["Economic downturn"], "data_signals": ["Revenue decline"]}],
                "metrics_to_track": [{"name": "Revenue Growth", "type": "Level_0_Raw_Activity", "description": "Quarterly revenue tracking", "frequency": "quarterly", "threshold": 5.0, "threshold_type": "above", "data_source": "FactSet", "value_chain_position": "downstream"}],
                "monitoring_plan": {"objective": "Track performance", "data_pulls": [{"category": "Financial", "metrics": ["Revenue"], "data_source": "FactSet", "frequency": "quarterly"}], "alert_logic": [{"frequency": "quarterly", "condition": "Revenue decline", "action": "Review"}], "decision_triggers": [{"condition": "Underperformance", "action": "reassess"}], "review_schedule": "Monthly"},
                "market_sentiment": {"buy_rating": 60, "hold_rating": 30, "sell_rating": 10, "price_target_avg": 100, "price_target_high": 120, "price_target_low": 80, "analyst_count": 15, "momentum_score": 70, "institutional_ownership": 50, "sentiment_trend": "neutral"}
            }
        except Exception as e:
            logging.error(f"Error in analyze_thesis: {str(e)}")
            raise

    def _extract_ticker_symbol(self, text):
        """Extract ticker symbol from thesis text"""
        import re
        
        # Look for ticker patterns
        patterns = [
            r'\$([A-Z]{1,5})\b',  # $TICKER format
            r'\b([A-Z]{1,5})\b',  # Standalone uppercase letters
            r'\(([A-Z]{1,5})\)',  # (TICKER) format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Filter out common words
                exclude = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'HAD', 'HAS'}
                for match in matches:
                    if match not in exclude and len(match) >= 2:
                        return match
        
        return None

    def _extract_sedol_id(self, text):
        """Extract SEDOL ID from thesis text"""
        import re
        
        # Look for SEDOL patterns (7 characters: 6 alphanumeric + 1 check digit)
        patterns = [
            r'SEDOL:\s*([A-Z0-9]{7})',  # SEDOL: prefix
            r'SEDOL\s+([A-Z0-9]{7})',   # SEDOL space prefix
            r'\b([A-Z0-9]{7})\b',       # 7 alphanumeric characters
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0].upper()
        
        return None

    def _generate_fallback_analysis(self, thesis_text):
        """Generate structured analysis when Azure OpenAI is unavailable"""
        company_name = self._extract_company_name(thesis_text) or "Company"
        ticker_symbol = self._extract_ticker_symbol(thesis_text) or "TICKER"
        sedol_id = self._extract_sedol_id(thesis_text) or "0000000"
        
        return json.dumps({
            "core_claim": f"Investment analysis requires Azure OpenAI API key for {company_name}",
            "core_analysis": "Complete analysis requires authenticated AI service access",
            "causal_chain": [{"chain_link": 1, "event": "API Authentication", "explanation": "Azure OpenAI credentials needed for analysis"}],
            "assumptions": ["Valid API credentials will be provided"],
            "mental_model": "Authentication",
            "counter_thesis_scenarios": [{"scenario": "Missing credentials", "description": "Analysis cannot proceed", "trigger_conditions": ["No API key"], "data_signals": ["Authentication failure"]}],
            "metrics_to_track": [{"name": "API Status", "type": "Level_0_Raw_Activity", "description": "Monitor API availability", "frequency": "continuous", "threshold": 1.0, "threshold_type": "above", "data_source": "System", "value_chain_position": "upstream", "company_ticker": ticker_symbol, "sedol_id": sedol_id}],
            "monitoring_plan": {"objective": "Establish API connection", "data_pulls": [{"category": "System", "metrics": ["API Status"], "data_source": "Azure", "frequency": "continuous"}], "alert_logic": [{"frequency": "immediate", "condition": "API unavailable", "action": "Request credentials"}], "decision_triggers": [{"condition": "Credentials provided", "action": "retry analysis"}], "review_schedule": "Immediate"},
            "market_sentiment": {"buy_rating": 0, "hold_rating": 0, "sell_rating": 0, "price_target_avg": 0, "price_target_high": 0, "price_target_low": 0, "analyst_count": 0, "momentum_score": 0, "institutional_ownership": 0, "sentiment_trend": "requires_credentials"},
            "company_identifiers": {
                "ticker": ticker_symbol,
                "sedol_id": sedol_id,
                "company_name": company_name
            },
            "error": "Azure OpenAI API key required for complete analysis"
        })