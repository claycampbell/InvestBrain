import os
import logging
import json
from openai import AzureOpenAI
from config import Config

class AzureOpenAIService:
    def __init__(self):
        self.client = None
        self.deployment_name = Config.AZURE_OPENAI_DEPLOYMENT_NAME
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            api_key = Config.AZURE_OPENAI_API_KEY
            endpoint = Config.AZURE_OPENAI_ENDPOINT
            api_version = Config.AZURE_OPENAI_API_VERSION
            
            if not api_key or not endpoint:
                logging.error("Azure OpenAI credentials not found in environment variables")
                return
            
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint,
                timeout=60,  # 1 minute timeout
                max_retries=0  # Handle retries manually
            )
            
            logging.info("Azure OpenAI client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            self.client = None
    
    def generate_completion(self, messages, temperature=1.0, max_tokens=4000):
        """Generate a completion using Azure OpenAI with robust timeout and retry handling"""
        if not self.client:
            raise Exception("Azure OpenAI client not initialized")
        
        # Enhanced retry configuration for network issues
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Handle different model types with appropriate parameters
                model_name = self.deployment_name.lower()
                
                if 'o1' in model_name or 'o4' in model_name:
                    # o1/o4 models have specific parameter constraints
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name
                    )
                elif 'gpt-4o' in model_name:
                    # GPT-4o models support limited parameters
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name,
                        max_completion_tokens=max_tokens
                    )
                else:
                    # Standard GPT models
                    response = self.client.chat.completions.create(
                        messages=messages,
                        temperature=temperature,
                        max_completion_tokens=max_tokens,
                        model=self.deployment_name
                    )
                
                # Debug the full response structure
                logging.info(f"Azure OpenAI response received")
                logging.info(f"Response choices count: {len(response.choices) if response.choices else 0}")
                
                if not response.choices:
                    logging.error("No choices in Azure OpenAI response")
                    raise Exception("No choices in Azure OpenAI response")
                
                choice = response.choices[0]
                logging.info(f"Choice finish reason: {choice.finish_reason}")
                
                content = choice.message.content if hasattr(choice.message, 'content') else None
                
                if not content or content.strip() == "":
                    logging.error(f"Empty or null content from Azure OpenAI")
                    logging.error(f"Choice finish reason: {choice.finish_reason}")
                    logging.error(f"Choice message: {choice.message}")
                    
                    # Handle specific finish reasons
                    if choice.finish_reason == 'length':
                        logging.error("Response truncated due to length limit")
                    elif choice.finish_reason == 'content_filter':
                        logging.error("Response filtered by content policy")
                    
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
                    logging.warning(f"Attempt {attempt + 1} failed with network error: {error_message[:100]}...")
                    logging.warning(f"Retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    
                    # Reinitialize client on connection errors
                    try:
                        self._initialize_client()
                        logging.info("Client reinitialized for retry")
                    except:
                        pass
                    
                    continue
                else:
                    logging.error(f"Error generating completion after {attempt + 1} attempts: {error_message}")
                    raise
        
        # If all retries failed, return a graceful fallback
        logging.error(f"Azure OpenAI request failed after {max_retries} attempts, using fallback response")
        return self._generate_fallback_response(messages)
    
    def _generate_fallback_response(self, messages):
        """Generate a structured fallback response when Azure OpenAI is unavailable"""
        try:
            # Extract the user's thesis text from messages
            thesis_text = ""
            for message in messages:
                if message.get("role") == "user":
                    thesis_text = message.get("content", "")
                    break
            
            # Generate a structured analysis based on the thesis content
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
            # Minimal fallback if JSON generation fails
            return json.dumps({
                "core_claim": "Investment thesis requires further analysis when services are restored",
                "core_analysis": "Analysis temporarily unavailable due to service connectivity",
                "status": "fallback_mode"
            })
    
    def _extract_company_name(self, text):
        """Extract company name from thesis text using simple pattern matching"""
        import re
        
        # Common company patterns
        patterns = [
            r'\b(NVIDIA|Apple|Microsoft|Google|Amazon|Meta|Tesla|Novo Nordisk|Pfizer|Johnson & Johnson)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Corporation|Corp|Inc|Ltd|Company|Co)\b',
            r'\b([A-Z]{2,})\b'  # All caps abbreviations
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return None
    
    def analyze_thesis(self, thesis_text):
        """Analyze an investment thesis using structured prompts with signal extraction focus"""
        system_prompt = """You are an expert investment analyst. Analyze investment theses and provide structured analysis.

Respond with valid JSON only:
{
  "core_claim": "One sentence investment claim",
  "core_analysis": "Analysis of risk/reward dynamics and key uncertainties", 
  "causal_chain": [
    {"chain_link": 1, "event": "Market condition", "explanation": "How this affects thesis"},
    {"chain_link": 2, "event": "Next consequence", "explanation": "Connection to previous link"}
  ],
  "assumptions": ["Key assumption 1", "Key assumption 2"],
  "mental_model": "Growth|Value|Cyclical|Disruption",
  "counter_thesis_scenarios": [
    {"scenario": "Risk scenario", "description": "Brief explanation", "trigger_conditions": ["Condition 1"], "data_signals": ["Signal 1"]}
  ],
  "metrics_to_track": [
    {"name": "Signal name", "type": "Level_0_Raw_Activity|Level_1_Simple_Aggregation", "description": "Signal description", "frequency": "monthly", "threshold": 5.0, "threshold_type": "above", "data_source": "FactSet", "value_chain_position": "upstream|midstream|downstream"}
  ],
  "monitoring_plan": {
    "objective": "Monitor thesis performance",
    "data_pulls": [{"category": "Financial", "metrics": ["Revenue"], "data_source": "FactSet", "frequency": "quarterly"}],
    "alert_logic": [{"frequency": "quarterly", "condition": "Revenue growth <10%", "action": "Review assumptions"}],
    "decision_triggers": [{"condition": "Market share decline >5%", "action": "sell"}],
    "review_schedule": "Monthly review"
  }
}"""
        
        user_prompt = f"""Analyze this investment thesis: {thesis_text}

Create a comprehensive analysis with monitoring strategy. Focus on actionable insights.

Provide complete JSON response with all required fields."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.generate_completion(messages)
            
            # Ensure we have a valid response
            if not response:
                raise Exception("Empty response from Azure OpenAI")
            
            # Try to parse as JSON
            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                # If JSON parsing fails, extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise Exception("Could not parse extracted JSON from response")
                else:
                    raise Exception("Could not extract valid JSON from response")
                    
        except Exception as e:
            logging.error(f"Error analyzing thesis: {str(e)}")
            # Return a basic structure if analysis fails
            return {
                "core_claim": "Analysis failed - please try again",
                "causal_chain": [],
                "assumptions": [],
                "mental_model": "unknown",
                "counter_thesis": [],
                "metrics_to_track": [],
                "monitoring_plan": {
                    "review_frequency": "monthly",
                    "key_indicators": [],
                    "alert_conditions": []
                }
            }
    
    def generate_thesis_from_data(self, data_summary):
        """Generate a thesis statement from research data"""
        system_prompt = """You are an expert investment analyst. Based on the provided research data, 
        generate a clear, actionable investment thesis statement. The thesis should be specific, 
        measurable, and based on the evidence provided."""
        
        user_prompt = f"""Based on the following research data, generate an investment thesis:

        {data_summary}

        Please provide:
        1. A clear thesis statement (1-2 sentences)
        2. Key supporting evidence
        3. Primary risks to consider"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.generate_completion(messages, temperature=0.5)
    
    def is_available(self):
        """Check if the Azure OpenAI service is available"""
        return self.client is not None
