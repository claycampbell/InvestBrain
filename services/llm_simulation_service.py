"""
LLM-Driven Simulation Service for Investment Thesis Analysis

Uses Azure OpenAI exclusively for authentic simulation data generation,
removing all algorithmic fallbacks to ensure data integrity.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService


class LLMSimulationService:
    """
    Pure LLM-driven simulation service using Azure OpenAI
    """
    
    def __init__(self):
        self.ai_service = AzureOpenAIService()
        
    def generate_thesis_simulation(self, thesis, time_horizon: int, scenario: str, 
                                 volatility: str, include_events: bool) -> Dict[str, Any]:
        """
        Generate comprehensive thesis simulation using Azure OpenAI exclusively
        """
        if not self.ai_service.is_available():
            return {
                'error': True,
                'message': 'Azure OpenAI service required',
                'description': 'This simulation requires Azure OpenAI to generate authentic market scenarios and performance forecasts.',
                'action_needed': 'Please configure Azure OpenAI credentials to enable LLM-generated simulations.'
            }
        
        try:
            # Generate performance forecast using LLM
            performance_data = self._generate_llm_performance_forecast(
                thesis, time_horizon, scenario, volatility
            )
            
            # Generate market events if requested
            events = []
            if include_events:
                events = self._generate_llm_market_events(
                    thesis, time_horizon, scenario, performance_data
                )
            
            # Generate scenario analysis
            scenario_analysis = self._generate_llm_scenario_analysis(
                thesis, scenario, time_horizon, performance_data, events
            )
            
            # Create timeline
            timeline = self._generate_timeline_labels(time_horizon)
            
            return {
                'chart_data': {
                    'performance_data': performance_data,
                    'timeline': timeline
                },
                'events': events,
                'scenario_analysis': scenario_analysis,
                'simulation_metadata': {
                    'thesis_id': thesis.id,
                    'thesis_title': thesis.title,
                    'scenario': scenario,
                    'volatility': volatility,
                    'time_horizon': time_horizon,
                    'include_events': include_events,
                    'generated_at': datetime.utcnow().isoformat(),
                    'data_source': 'Azure OpenAI LLM'
                }
            }
            
        except Exception as e:
            logging.error(f"LLM simulation generation failed: {str(e)}")
            return {
                'error': True,
                'message': 'LLM simulation failed',
                'description': f'Azure OpenAI simulation generation encountered an error: {str(e)}',
                'action_needed': 'Please try again or check Azure OpenAI service status.'
            }
    
    def _generate_llm_performance_forecast(self, thesis, time_horizon: int, 
                                         scenario: str, volatility: str) -> Dict[str, List[float]]:
        """
        Generate performance forecast using Azure OpenAI
        """
        months = time_horizon * 12
        
        # Extract thesis details for context
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        mental_model = getattr(thesis, 'mental_model', 'Growth')
        
        prompt = f"""Generate a realistic {months}-month investment performance simulation.

Thesis: {thesis_text[:300]}
Investment Model: {mental_model}
Scenario: {scenario} market conditions
Volatility: {volatility}

Generate two performance series:
1. Market baseline: Broad market performance with realistic volatility, corrections, and rallies
2. Thesis performance: Based on specific thesis expectations and analyst forecasts

Requirements:
- Start both at 100.0
- Market should show realistic volatility patterns, corrections (-10% to -20%), and rallies
- Thesis performance should reflect the specific investment expectations from the thesis
- {scenario} scenario should influence overall direction and volatility
- Include realistic market cycles and seasonal patterns

Return JSON format only:
{{
  "market_performance": [100.0, 98.5, 102.3, ...],
  "thesis_performance": [100.0, 102.1, 104.8, ...],
  "performance_summary": "Brief analysis of the forecast trajectory"
}}"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.7, max_tokens=2000
            )
            
            if not response:
                raise Exception("Azure OpenAI returned empty response")
            
            # Parse the JSON response
            cleaned_response = self._clean_json_response(response)
            data = json.loads(cleaned_response)
            
            market_data = data.get('market_performance', [])
            thesis_data = data.get('thesis_performance', [])
            
            if len(market_data) >= months and len(thesis_data) >= months:
                return {
                    'market_performance': [float(x) for x in market_data[:months]],
                    'thesis_performance': [float(x) for x in thesis_data[:months]],
                    'performance_summary': data.get('performance_summary', 'LLM-generated forecast')
                }
            else:
                raise Exception(f"Insufficient data points: market={len(market_data)}, thesis={len(thesis_data)}, needed={months}")
                
        except Exception as e:
            logging.error(f"LLM performance forecast failed: {str(e)}")
            raise Exception(f"Failed to generate LLM performance forecast: {str(e)}")
    
    def _generate_llm_market_events(self, thesis, time_horizon: int, scenario: str, 
                                  performance_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate market events using Azure OpenAI
        """
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        
        # Get thesis signals for context
        signals = []
        if hasattr(thesis, 'signals') and thesis.signals:
            signals = [signal.signal_name for signal in thesis.signals[:5]]
        
        prompt = f"""Generate realistic market events for this investment thesis simulation.

Thesis: {thesis_text[:300]}
Time Horizon: {time_horizon} years
Scenario: {scenario}
Key Signals: {', '.join(signals) if signals else 'Standard financial metrics'}

Generate 3-5 realistic market events that could impact this thesis:
- Events should be relevant to the thesis and scenario
- Include timing (month within the time horizon)
- Specify impact type (positive/negative/neutral)
- Include which signals would be affected
- Events should feel authentic to current market conditions

Return JSON array only:
[
  {{
    "month": 6,
    "title": "Event Title",
    "description": "Detailed event description and market implications",
    "impact_type": "positive",
    "magnitude": "moderate",
    "signals_affected": ["Signal Name 1", "Signal Name 2"],
    "market_context": "Why this event matters for the thesis"
  }}
]"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.8, max_tokens=1500
            )
            
            if not response:
                raise Exception("Azure OpenAI returned empty response for events")
            
            # Parse the JSON response
            cleaned_response = self._clean_json_response(response)
            events_data = json.loads(cleaned_response)
            
            if not isinstance(events_data, list):
                raise Exception("Expected array of events")
            
            # Format events with additional metadata
            formatted_events = []
            total_months = time_horizon * 12
            
            for event in events_data:
                month = event.get('month', 1)
                if 1 <= month <= total_months:
                    formatted_event = {
                        'month': month,
                        'date': self._month_to_date_string(month),
                        'title': event.get('title', 'Market Event'),
                        'description': event.get('description', 'Market development'),
                        'impact_type': event.get('impact_type', 'neutral'),
                        'magnitude': event.get('magnitude', 'moderate'),
                        'signals_affected': event.get('signals_affected', []),
                        'market_context': event.get('market_context', ''),
                        'impact_value': performance_data.get('thesis_performance', [100])[min(month-1, len(performance_data.get('thesis_performance', [100]))-1)]
                    }
                    formatted_events.append(formatted_event)
            
            return formatted_events[:6]  # Limit to 6 events max
            
        except Exception as e:
            logging.error(f"LLM event generation failed: {str(e)}")
            raise Exception(f"Failed to generate LLM market events: {str(e)}")
    
    def _generate_llm_scenario_analysis(self, thesis, scenario: str, time_horizon: int,
                                      performance_data: Dict, events: List[Dict]) -> Dict[str, Any]:
        """
        Generate comprehensive scenario analysis using Azure OpenAI
        """
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        
        # Calculate some basic metrics from performance data
        thesis_performance = performance_data.get('thesis_performance', [100])
        final_return = ((thesis_performance[-1] / thesis_performance[0]) - 1) * 100 if len(thesis_performance) > 1 else 0
        
        prompt = f"""Analyze this investment thesis simulation and provide comprehensive insights.

Thesis: {thesis_text[:300]}
Scenario: {scenario}
Time Horizon: {time_horizon} years
Simulated Return: {final_return:.1f}%
Key Events: {len(events)} market events generated

Provide detailed analysis covering:
1. Scenario implications for the thesis
2. Key risk factors and opportunities
3. Performance expectations and rationale
4. Strategic recommendations
5. Monitoring priorities

Return JSON format:
{{
  "scenario_summary": "Executive summary of the scenario analysis",
  "performance_assessment": "Analysis of expected performance under this scenario",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "key_opportunities": ["Opportunity 1", "Opportunity 2"],
  "strategic_recommendations": ["Recommendation 1", "Recommendation 2"],
  "monitoring_priorities": ["Priority 1", "Priority 2"],
  "conviction_level": "High/Medium/Low",
  "probability_assessment": "Assessment of scenario likelihood and thesis success probability"
}}"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.6, max_tokens=1500
            )
            
            if not response:
                raise Exception("Azure OpenAI returned empty response for scenario analysis")
            
            # Parse the JSON response
            cleaned_response = self._clean_json_response(response)
            analysis = json.loads(cleaned_response)
            
            return analysis
            
        except Exception as e:
            logging.error(f"LLM scenario analysis failed: {str(e)}")
            raise Exception(f"Failed to generate LLM scenario analysis: {str(e)}")
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean Azure OpenAI response to extract valid JSON
        """
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Find JSON object or array boundaries
        if cleaned.startswith('{'):
            end = cleaned.rfind('}')
            if end != -1:
                cleaned = cleaned[:end+1]
        elif cleaned.startswith('['):
            end = cleaned.rfind(']')
            if end != -1:
                cleaned = cleaned[:end+1]
        
        return cleaned
    
    def _generate_timeline_labels(self, time_horizon: int) -> List[str]:
        """
        Generate timeline labels for the simulation
        """
        months = time_horizon * 12
        timeline = []
        
        current_date = datetime.now()
        
        for i in range(months):
            future_date = current_date + timedelta(days=30 * i)
            if i % 3 == 0:  # Label every 3 months
                timeline.append(future_date.strftime('%b %Y'))
            else:
                timeline.append('')
        
        return timeline
    
    def _month_to_date_string(self, month: int) -> str:
        """
        Convert month number to date string
        """
        current_date = datetime.now()
        future_date = current_date + timedelta(days=30 * (month - 1))
        return future_date.strftime('%B %Y')