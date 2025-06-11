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
        """Generate a completion using Azure OpenAI"""
        if not self.client:
            raise Exception("Azure OpenAI client not initialized")
        
        response = None
        try:
            # o4-mini model only supports default temperature (1.0)
            response = self.client.chat.completions.create(
                messages=messages,
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
                raise Exception("Empty response from Azure OpenAI")
            
            logging.info(f"Received valid response: {len(content)} characters")
            return content
            
        except Exception as e:
            logging.error(f"Error generating completion: {str(e)}")
            if response:
                logging.error(f"Response object exists, choices: {len(response.choices) if response.choices else 0}")
            else:
                logging.error("No response object received")
            raise
    
    def analyze_thesis(self, thesis_text):
        """Analyze an investment thesis using structured prompts with signal extraction focus"""
        system_prompt = """You are an expert investment analyst. Analyze investment theses and provide structured analysis with detailed causal chains, counter-scenarios and Level 0-1 signals.

Create detailed chainlinked events showing how each step connects to the next. Focus on signals closest to raw economic activity with minimal processing.

Respond with valid JSON only:
{
  "core_claim": "One sentence investment claim",
  "core_analysis": "Detailed analysis of the stock's risk/reward dynamics and key uncertainties",
  "causal_chain": [
    {
      "chain_link": 1,
      "event": "Specific market condition or business development",
      "explanation": "Detailed explanation of how this affects the thesis"
    },
    {
      "chain_link": 2, 
      "event": "Next logical consequence or market reaction",
      "explanation": "How this connects to the previous link and impacts outcomes"
    }
  ],
  "assumptions": ["Assumption 1", "Assumption 2"],
  "mental_model": "Growth|Value|Cyclical|Disruption",
  "counter_thesis_scenarios": [
    {
      "scenario": "Risk scenario title",
      "description": "Brief explanation",
      "trigger_conditions": ["Condition 1", "Condition 2"],
      "data_signals": ["Signal 1", "Signal 2"]
    }
  ],
  "metrics_to_track": [
    {
      "name": "Signal name",
      "type": "Level_0_Raw_Activity|Level_1_Simple_Aggregation",
      "description": "Signal description",
      "frequency": "daily|weekly|monthly",
      "threshold": 5.0,
      "threshold_type": "above|below|change_percent",
      "data_source": "Source name",
      "value_chain_position": "upstream|midstream|downstream"
    }
  ],
  "monitoring_plan": {
    "objective": "Clear monitoring objective statement",
    "data_pulls": [
      {
        "category": "Category name",
        "metrics": ["Metric 1", "Metric 2"],
        "data_source": "Xpressfeed|FactSet",
        "query_template": "SELECT statement with WHERE clause",
        "frequency": "daily|weekly|quarterly"
      }
    ],
    "alert_logic": [
      {
        "frequency": "daily|weekly|quarterly",
        "condition": "Specific threshold condition",
        "action": "Flag/review action to take"
      }
    ],
    "decision_triggers": [
      {
        "condition": "Specific exit/entry condition",
        "action": "buy|sell|hold decision"
      }
    ],
    "review_schedule": "Formal review timing"
  }
}"""
        
        user_prompt = f"""Analyze this thesis: {thesis_text}

Create a comprehensive monitoring plan with specific data sources (Xpressfeed/FactSet), SQL query templates, alert conditions, and decision triggers like the Nutrien example.

Provide complete JSON response with all monitoring_plan fields populated."""
        
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
