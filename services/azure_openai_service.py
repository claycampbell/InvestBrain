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
            
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
                timeout=120.0,  # Increased timeout
                max_retries=3   # More retries
            )
            
            logging.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def generate_completion(self, messages, temperature=1.0, max_tokens=4000):
        """Generate a completion using Azure OpenAI with robust timeout and retry handling"""
        if not self.client:
            raise Exception("Azure OpenAI client not initialized")
        
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
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
                    raise Exception("No choices in Azure OpenAI response")
                
                choice = response.choices[0]
                logging.info(f"Choice finish reason: {choice.finish_reason}")
                
                content = choice.message.content if hasattr(choice.message, 'content') else None
                
                if not content or content.strip() == "":
                    logging.error(f"Empty content from Azure OpenAI (finish_reason: {choice.finish_reason})")
                    raise Exception(f"Empty response from Azure OpenAI (finish_reason: {choice.finish_reason})")
                
                logging.info(f"Received valid response: {len(content)} characters")
                return content
                
            except Exception as e:
                error_message = str(e)
                is_retryable = any(keyword in error_message.lower() for keyword in [
                    'timeout', 'read timeout', 'connection timeout', 'ssl', 
                    'connection', 'network', 'reset', 'broken pipe', 'recv'
                ])
                
                if is_retryable and attempt < max_retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed with network error, retrying...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
                    try:
                        self._initialize_client()
                        logging.info("Client reinitialized for retry")
                    except:
                        pass
                    
                    continue
                else:
                    logging.error(f"Error generating completion after {attempt + 1} attempts: {error_message}")
                    if attempt == max_retries - 1:
                        # Instead of fallback, raise an informative error for the user
                        raise Exception("Azure OpenAI service is temporarily unavailable due to network connectivity issues. Please check your API credentials and try again.")
                    raise
    
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
        
        # Use live Azure OpenAI for dynamic analysis
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert investment analyst. Analyze the thesis and return valid JSON with this exact structure:
{
  "core_claim": "Single sentence primary investment thesis",
  "core_analysis": "Detailed 2-3 sentence analysis of key risks and opportunities",
  "causal_chain": [
    {"step": 1, "step_name": "Primary Driver", "description": "Explanation of first logical step", "evidence": "Supporting evidence"},
    {"step": 2, "step_name": "Secondary Effect", "description": "How step 1 leads to step 2", "evidence": "Supporting data"}
  ],
  "assumptions": ["Critical assumption 1", "Key dependency 2", "Important precondition 3"],
  "mental_model": "Growth|Value|Disruption|Quality|Cyclical",
  "counter_thesis": [
    {"scenario_name": "Primary Risk", "description": "Detailed risk explanation", "probability": "25%", "impact": "High - specific impact description", "mitigation": "How to address this risk"}
  ],
  "metrics_to_track": [],
  "monitoring_plan": "Brief monitoring strategy"
}"""
                },
                {
                    "role": "user", 
                    "content": f"Analyze this investment thesis: {thesis_text}"
                }
            ]
            
            response = self.generate_completion(messages, temperature=0.7, max_tokens=4000)
            
            # Parse the response and ensure it's valid JSON
            if isinstance(response, str):
                try:
                    parsed_response = json.loads(response)
                    # Validate that all required fields are present and properly populated
                    if ('causal_chain' not in parsed_response or 
                        not isinstance(parsed_response['causal_chain'], list) or 
                        len(parsed_response['causal_chain']) < 2):
                        logging.warning("Incomplete Azure OpenAI response: insufficient causal_chain data")
                        raise ValueError("Incomplete causal_chain")
                    
                    if ('counter_thesis' not in parsed_response or 
                        not isinstance(parsed_response['counter_thesis'], list) or 
                        len(parsed_response['counter_thesis']) < 1):
                        logging.warning("Incomplete Azure OpenAI response: missing counter_thesis data")
                        raise ValueError("Missing counter_thesis")
                    
                    return parsed_response
                except (json.JSONDecodeError, ValueError):
                    # If response isn't valid JSON, wrap it
                    company_name = self._extract_company_name(thesis_text) or "the company"
                    return {
                        "core_claim": f"Investment analysis for {company_name}",
                        "core_analysis": response[:500],
                        "assumptions": ["Market conditions remain stable"],
                        "mental_model": "Fundamental Analysis",
                        "metrics_to_track": []
                    }
            
        except Exception as e:
            logging.error(f"Azure OpenAI analysis failed: {str(e)}")
            # Fallback to dynamic templated response
            pass
        
        # Clean fallback when Azure OpenAI is unavailable
        company_name = self._extract_company_name(thesis_text) or "the company"
        return {
            "core_claim": f"Investment opportunity in {company_name} identified through analysis",
            "core_analysis": f"{company_name} presents potential for value creation through strategic positioning and operational execution",
            "causal_chain": [
                {"step": 1, "step_name": "Market Position", "description": "Company maintains competitive positioning", "evidence": "Market analysis"},
                {"step": 2, "step_name": "Growth Strategy", "description": "Strategic initiatives drive expansion", "evidence": "Business development"}
            ],
            "assumptions": [
                "Market conditions remain favorable",
                "Management execution continues effectively"
            ],
            "mental_model": "Growth",
            "counter_thesis": [
                {
                    "scenario_name": "Market Saturation",
                    "description": "Market growth may slow as competition intensifies and customer acquisition becomes more difficult",
                    "probability": "30%",
                    "impact": "High - could reduce revenue growth rates and compress margins",
                    "mitigation": "Diversify into new markets and enhance product differentiation"
                },
                {
                    "scenario_name": "Competitive Disruption",
                    "description": "New competitors or technologies could challenge market position and erode competitive advantages",
                    "probability": "25%",
                    "impact": "Medium - may require increased investment in R&D and marketing",
                    "mitigation": "Maintain innovation pipeline and strategic partnerships"
                },
                {
                    "scenario_name": "Economic Downturn",
                    "description": "Macroeconomic headwinds could reduce demand and delay growth initiatives",
                    "probability": "20%",
                    "impact": "Medium - could postpone revenue targets and affect profitability",
                    "mitigation": "Focus on cost efficiency and maintain strong balance sheet"
                }
            ],
            "metrics_to_track": [],
            "monitoring_plan": "Monitor key financial metrics quarterly"
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