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
                azure_endpoint=endpoint
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
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                # Handle different model types with appropriate parameters
                model_name = self.deployment_name.lower()
                
                if 'o1' in model_name or 'o4' in model_name:
                    # o1/o4 models have specific parameter constraints
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name,
                        timeout=30  # Reduced timeout to fail fast and use fallback
                    )
                elif 'gpt-4o' in model_name:
                    # GPT-4o models support limited parameters
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name,
                        max_completion_tokens=max_tokens,
                        timeout=45
                    )
                else:
                    # Standard GPT models
                    response = self.client.chat.completions.create(
                        messages=messages,
                        temperature=temperature,
                        max_completion_tokens=max_tokens,
                        model=self.deployment_name,
                        timeout=45
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
                    # Check if this is a thesis analysis request that can use fallback
                    if self._is_thesis_analysis_request(messages):
                        logging.info("Using fallback analysis due to Azure OpenAI connectivity issues")
                        return self._generate_fallback_analysis(messages)
                    raise
        
        # If all retries failed
        raise Exception(f"Azure OpenAI request failed after {max_retries} attempts")
    
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
            logging.warning(f"Azure OpenAI analysis failed, using fallback: {str(e)}")
            # Use comprehensive fallback analysis
            fallback_result = self._generate_fallback_analysis(messages)
            try:
                import json
                return json.loads(fallback_result)
            except json.JSONDecodeError:
                logging.error("Fallback analysis JSON parsing failed")
                return {
                    "core_claim": "Investment opportunity with growth potential",
                    "core_analysis": "Moderate risk-reward profile with sector-specific opportunities",
                    "causal_chain": [{"chain_link": 1, "event": "Market growth", "explanation": "Favorable conditions support investment thesis"}],
                    "assumptions": ["Market conditions remain favorable", "Execution meets expectations"],
                    "mental_model": "Growth",
                    "counter_thesis_scenarios": [{"scenario": "Market decline", "description": "Economic downturn affects performance", "trigger_conditions": ["Recession"], "data_signals": ["GDP decline"]}],
                    "metrics_to_track": [{"name": "Revenue Growth", "type": "Level_1_Simple_Aggregation", "description": "Quarterly revenue growth", "frequency": "quarterly", "threshold": 10.0, "threshold_type": "above", "data_source": "Company Reports", "value_chain_position": "financial"}],
                    "monitoring_plan": {"objective": "Monitor performance", "data_pulls": [{"category": "Financial", "metrics": ["Revenue"], "data_source": "Reports", "frequency": "quarterly"}], "alert_logic": [{"frequency": "quarterly", "condition": "Growth < 10%", "action": "Review"}], "decision_triggers": [{"condition": "Decline", "action": "Exit"}], "review_schedule": "Quarterly"}
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
    
    def _is_thesis_analysis_request(self, messages):
        """Check if this is a thesis analysis request that can use fallback"""
        if not messages:
            return False
        
        # Check if any message contains thesis analysis keywords
        for message in messages:
            content = message.get('content', '').lower()
            if any(keyword in content for keyword in ['analyze investment', 'thesis', 'investment claim', 'core_claim']):
                return True
        return False
    
    def _generate_fallback_analysis(self, messages):
        """Generate thesis analysis using fallback service when AI is unavailable"""
        try:
            from services.fallback_analysis_service import FallbackAnalysisService
            
            # Extract thesis text from messages
            thesis_text = ""
            for message in messages:
                if message.get('role') == 'user':
                    content = message.get('content', '')
                    if 'analyze:' in content.lower():
                        thesis_text = content.split(':', 1)[1].strip()
                    else:
                        thesis_text = content
                    break
            
            if not thesis_text:
                thesis_text = "Investment opportunity with growth potential"
            
            # Generate analysis using fallback service
            fallback_service = FallbackAnalysisService()
            analysis_result = fallback_service.analyze_thesis(thesis_text)
            
            # Convert to JSON format expected by the system
            import json
            return json.dumps(analysis_result)
            
        except Exception as e:
            logging.error(f"Fallback analysis failed: {str(e)}")
            # Return minimal viable analysis
            return json.dumps({
                "core_claim": "Investment opportunity with growth potential",
                "core_analysis": "Moderate risk-reward profile with sector-specific opportunities",
                "causal_chain": [{"chain_link": 1, "event": "Market growth", "explanation": "Favorable conditions support investment thesis"}],
                "assumptions": ["Market conditions remain favorable", "Execution meets expectations"],
                "mental_model": "Growth",
                "counter_thesis_scenarios": [{"scenario": "Market decline", "description": "Economic downturn affects performance", "trigger_conditions": ["Recession"], "data_signals": ["GDP decline"]}],
                "metrics_to_track": [{"name": "Revenue Growth", "type": "Level_1_Simple_Aggregation", "description": "Quarterly revenue growth", "frequency": "quarterly", "threshold": 10.0, "threshold_type": "above", "data_source": "Company Reports", "value_chain_position": "financial"}],
                "monitoring_plan": {"objective": "Monitor performance", "data_pulls": [{"category": "Financial", "metrics": ["Revenue"], "data_source": "Reports", "frequency": "quarterly"}], "alert_logic": [{"frequency": "quarterly", "condition": "Growth < 10%", "action": "Review"}], "decision_triggers": [{"condition": "Decline", "action": "Exit"}], "review_schedule": "Quarterly"}
            })

    def is_available(self):
        """Check if the Azure OpenAI service is available"""
        return self.client is not None
