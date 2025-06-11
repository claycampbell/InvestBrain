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
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logging.info(f"Azure OpenAI attempt {attempt + 1}/{max_retries}")
                
                # Use shorter timeout for individual attempts to fail fast and retry
                attempt_timeout = 45 if attempt < 2 else 90  # Shorter for first attempts
                # Handle different model types with appropriate parameters
                model_name = self.deployment_name.lower()
                
                if 'o1' in model_name or 'o4' in model_name:
                    # o1/o4 models have specific parameter constraints
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name,
                        timeout=attempt_timeout
                    )
                elif 'gpt-4o' in model_name:
                    # GPT-4o models support limited parameters
                    response = self.client.chat.completions.create(
                        messages=messages,
                        model=self.deployment_name,
                        max_completion_tokens=max_tokens,
                        timeout=attempt_timeout
                    )
                else:
                    # Standard GPT models
                    response = self.client.chat.completions.create(
                        messages=messages,
                        temperature=temperature,
                        max_completion_tokens=max_tokens,
                        model=self.deployment_name,
                        timeout=attempt_timeout
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
                is_timeout = any(keyword in error_message.lower() for keyword in ['timeout', 'read timeout', 'connection timeout', 'ssl', 'recv'])
                
                if is_timeout and attempt < max_retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed with timeout, retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logging.error(f"Error generating completion: {error_message}")
                    # Return a structured error response instead of raising
                    return self._get_connection_error_response()
        
        # If all retries failed, return error response
        logging.error(f"Azure OpenAI request failed after {max_retries} attempts")
        return self._get_connection_error_response()
    
    def _get_connection_error_response(self):
        """Return a structured error response when Azure OpenAI is unavailable"""
        return """{
            "error": "connection_failed",
            "message": "Unable to connect to Azure OpenAI service. Please check your network connection and try again.",
            "core_claim": "Analysis temporarily unavailable due to connection issues",
            "core_analysis": "The system encountered network connectivity issues while processing your thesis. Please verify your Azure OpenAI credentials and network connection, then try again.",
            "assumptions": ["Network connectivity will be restored", "Azure OpenAI service is operational"],
            "mental_model": "Technical Recovery",
            "causal_chain": [{"chain_link": 1, "event": "Network timeout", "explanation": "Connection to Azure OpenAI was interrupted"}],
            "counter_thesis_scenarios": [{"scenario": "Service unavailable", "description": "Analysis service temporarily offline", "trigger_conditions": ["Network issues"], "data_signals": ["Connection status"]}]
        }"""
    
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
