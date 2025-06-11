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
    
    def generate_completion(self, messages, temperature=0.7, max_tokens=2000):
        """Generate a completion using Azure OpenAI"""
        if not self.client:
            raise Exception("Azure OpenAI client not initialized")
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                max_completion_tokens=max_tokens,
                model=self.deployment_name
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating completion: {str(e)}")
            raise
    
    def analyze_thesis(self, thesis_text):
        """Analyze an investment thesis using structured prompts with signal extraction focus"""
        system_prompt = """You are an expert investment analyst specializing in signal extraction and early indicator identification. 
        Your job is to analyze investment theses and identify actionable Level 0 (raw economic activity) and Level 1 (simple aggregation) signals.
        
        Focus on signals that:
        - Are closest to the source of economic activity
        - Have minimal processing or manipulation  
        - Provide early warning indicators
        - Have low market attention
        
        Always respond with valid JSON in the following format:
        {
            "core_claim": "The central investment claim in one clear sentence",
            "causal_chain": ["Step 1 of logical chain", "Step 2", "Step 3"],
            "assumptions": ["Critical assumption 1", "Critical assumption 2"],
            "mental_model": "Value|Growth|Cyclical|Disruption|Quality|Momentum",
            "counter_thesis": ["Counter-argument 1", "Counter-argument 2"],
            "metrics_to_track": [
                {
                    "name": "Primary signal name",
                    "type": "Level_0_Raw_Activity|Level_1_Simple_Aggregation|Level_2_Derived_Metrics",
                    "description": "What this signal measures and predictive value",
                    "frequency": "daily|weekly|monthly|quarterly",
                    "threshold": 5.0,
                    "threshold_type": "above|below|change_percent",
                    "data_source": "Specific source for obtaining this data",
                    "value_chain_position": "upstream|midstream|downstream"
                }
            ],
            "monitoring_plan": {
                "review_frequency": "weekly|monthly|quarterly",
                "key_indicators": ["Level 0 signal 1", "Level 0 signal 2"],
                "alert_conditions": ["Specific condition 1", "Specific condition 2"],
                "primary_signal_focus": true
            }
        }"""
        
        user_prompt = f"""Analyze the following investment thesis:

        {thesis_text}

        Please provide a structured analysis following the JSON format specified in the system prompt."""
        
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
