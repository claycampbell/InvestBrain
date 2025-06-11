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
    
    def generate_completion(self, messages, temperature=1.0, max_tokens=2000):
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
        system_prompt = """You are an expert investment analyst specializing in comprehensive thesis analysis and signal extraction. 
        Your job is to analyze investment theses and provide detailed counter-thesis scenarios, sophisticated monitoring plans, and actionable Level 0-1 signals.
        
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
            "counter_thesis_scenarios": [
                {
                    "scenario": "Counter-thesis Scenario 1 - [Brief title]",
                    "description": "Detailed scenario explanation with specific conditions and triggers",
                    "trigger_conditions": ["Observable condition 1", "Observable condition 2"],
                    "data_signals": ["Specific metric changes that would confirm this scenario"]
                }
            ],
            "metrics_to_track": [
                {
                    "name": "Primary signal name",
                    "type": "Level_0_Raw_Activity|Level_1_Simple_Aggregation|Level_2_Derived_Metrics",
                    "description": "What this signal measures and predictive value",
                    "frequency": "daily|weekly|monthly|quarterly",
                    "threshold": 5.0,
                    "threshold_type": "above|below|change_percent",
                    "data_source": "Specific source (FactSet, Xpressfeed, government data, etc.)",
                    "value_chain_position": "upstream|midstream|downstream",
                    "what_it_tells_us": "Detailed explanation of the signal's predictive value"
                }
            ],
            "monitoring_plan": {
                "review_frequency": "weekly|monthly|quarterly",
                "key_indicators": ["Level 0 signal 1", "Level 0 signal 2"],
                "alert_conditions": ["Specific measurable condition with thresholds"],
                "leading_indicators": ["Early warning signals"],
                "lagging_indicators": ["Confirmatory signals"],
                "revision_triggers": ["Conditions that would require thesis revision"],
                "data_refresh_schedule": "How often to update each data source"
            }
        }
        
        Note: For value chain positioning:
        - upstream: raw materials, commodities, mining, agriculture, extraction
        - midstream: processing, manufacturing, transportation, logistics
        - downstream: retail, consumer, end-user, final demand"""
        
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
