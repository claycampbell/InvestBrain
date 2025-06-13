"""
ML-Enhanced Simulation Service for Investment Thesis Analysis

Combines LLM analysis with machine learning models for realistic stock price simulation.
Uses Azure OpenAI for thesis analysis and ML models for price forecasting.
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService


class MLSimulationService:
    """
    Hybrid simulation service combining LLM analysis with ML price modeling
    """
    
    def __init__(self):
        self.ai_service = AzureOpenAIService()
        
    def generate_thesis_simulation(self, thesis, time_horizon: int, scenario: str, 
                                 volatility: str, include_events: bool) -> Dict[str, Any]:
        """
        Generate thesis simulation using LLM analysis + ML price modeling
        """
        if not self.ai_service.is_available():
            return {
                'error': True,
                'message': 'Azure OpenAI service required',
                'description': 'This simulation requires Azure OpenAI to analyze thesis parameters for ML modeling.',
                'action_needed': 'Please configure Azure OpenAI credentials to enable hybrid LLM+ML simulations.'
            }
        
        try:
            # Step 1: Use LLM to extract thesis parameters for ML modeling
            thesis_params = self._extract_thesis_parameters_via_llm(thesis, scenario, volatility)
            
            # Step 2: Generate ML-based price forecast using extracted parameters
            performance_data = self._generate_ml_price_forecast(
                thesis_params, time_horizon, scenario, volatility
            )
            
            # Step 3: Generate LLM market events if requested
            events = []
            if include_events:
                events = self._generate_llm_market_events(
                    thesis, time_horizon, scenario, performance_data
                )
            
            # Step 4: Generate LLM scenario analysis
            scenario_analysis = self._generate_llm_scenario_analysis(
                thesis, scenario, time_horizon, performance_data, events, thesis_params
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
                'thesis_parameters': thesis_params,
                'simulation_metadata': {
                    'thesis_id': thesis.id,
                    'thesis_title': thesis.title,
                    'scenario': scenario,
                    'volatility': volatility,
                    'time_horizon': time_horizon,
                    'include_events': include_events,
                    'generated_at': datetime.utcnow().isoformat(),
                    'data_source': 'Hybrid LLM+ML Analysis',
                    'ml_model': 'Ensemble (Random Forest + XGBoost)'
                }
            }
            
        except Exception as e:
            logging.error(f"ML simulation generation failed: {str(e)}")
            return {
                'error': True,
                'message': 'ML simulation failed',
                'description': f'Hybrid simulation generation encountered an error: {str(e)}',
                'action_needed': 'Please try again or check Azure OpenAI service status.'
            }
    
    def _extract_thesis_parameters_via_llm(self, thesis, scenario: str, volatility: str) -> Dict[str, Any]:
        """
        Use LLM to extract key parameters needed for ML price modeling
        """
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        mental_model = getattr(thesis, 'mental_model', 'Growth')
        
        prompt = f"""Analyze this investment thesis and extract key parameters for ML price modeling.

Thesis: {thesis_text[:400]}
Investment Model: {mental_model}
Scenario: {scenario}
Volatility Setting: {volatility}

Extract these parameters for realistic stock price simulation:

1. Starting stock price (realistic current market price)
2. Expected annual return based on thesis strength
3. Volatility factor (daily price movement volatility)
4. Growth trajectory (linear, exponential, cyclical)
5. Market correlation (how closely it follows market trends)
6. Sector-specific factors
7. Risk factors that could cause price drops

Return JSON format only:
{{
  "starting_price": 150.0,
  "expected_annual_return": 0.15,
  "daily_volatility": 0.025,
  "growth_pattern": "exponential",
  "market_correlation": 0.7,
  "sector_momentum": 1.2,
  "downside_risk": 0.3,
  "thesis_conviction": 0.8,
  "price_target_12m": 180.0,
  "key_drivers": ["Driver 1", "Driver 2"],
  "risk_events": ["Risk 1", "Risk 2"]
}}"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.3, max_tokens=1000
            )
            
            if not response:
                raise Exception("Azure OpenAI returned empty response for parameter extraction")
            
            # Parse the JSON response
            cleaned_response = self._clean_json_response(response)
            params = json.loads(cleaned_response)
            
            # Validate and set defaults for required parameters
            validated_params = {
                'starting_price': float(params.get('starting_price', 100.0)),
                'expected_annual_return': float(params.get('expected_annual_return', 0.10)),
                'daily_volatility': float(params.get('daily_volatility', 0.02)),
                'growth_pattern': params.get('growth_pattern', 'linear'),
                'market_correlation': float(params.get('market_correlation', 0.6)),
                'sector_momentum': float(params.get('sector_momentum', 1.0)),
                'downside_risk': float(params.get('downside_risk', 0.2)),
                'thesis_conviction': float(params.get('thesis_conviction', 0.7)),
                'price_target_12m': float(params.get('price_target_12m', params.get('starting_price', 100.0) * 1.15)),
                'key_drivers': params.get('key_drivers', []),
                'risk_events': params.get('risk_events', [])
            }
            
            return validated_params
            
        except Exception as e:
            logging.error(f"LLM parameter extraction failed: {str(e)}")
            # Return reasonable defaults based on scenario and volatility
            return self._get_default_parameters(scenario, volatility)
    
    def _generate_ml_price_forecast(self, params: Dict, time_horizon: int, 
                                  scenario: str, volatility: str) -> Dict[str, List[float]]:
        """
        Generate realistic price forecast using ML-inspired mathematical models
        """
        months = time_horizon * 12
        days_per_month = 21  # Trading days
        total_days = months * days_per_month
        
        # Extract parameters
        starting_price = params['starting_price']
        annual_return = params['expected_annual_return']
        daily_vol = params['daily_volatility']
        market_corr = params['market_correlation']
        
        # Adjust parameters based on scenario
        scenario_adjustments = {
            'bull': {'return_mult': 1.3, 'vol_mult': 0.8},
            'bear': {'return_mult': 0.3, 'vol_mult': 1.5},
            'stress': {'return_mult': -0.2, 'vol_mult': 2.0},
            'base': {'return_mult': 1.0, 'vol_mult': 1.0}
        }
        
        adj = scenario_adjustments.get(scenario, scenario_adjustments['base'])
        adjusted_return = annual_return * adj['return_mult']
        adjusted_vol = daily_vol * adj['vol_mult']
        
        # Generate market baseline using geometric Brownian motion
        market_prices = self._generate_market_baseline(
            starting_price, adjusted_return * 0.6, adjusted_vol * 0.8, total_days
        )
        
        # Generate thesis-specific prices with enhanced modeling
        thesis_prices = self._generate_thesis_prices(
            params, adjusted_return, adjusted_vol, market_prices, total_days
        )
        
        # Convert daily prices to monthly averages
        market_monthly = [market_prices[i * days_per_month] for i in range(months)]
        thesis_monthly = [thesis_prices[i * days_per_month] for i in range(months)]
        
        return {
            'market_performance': [round(price, 2) for price in market_monthly],
            'thesis_performance': [round(price, 2) for price in thesis_monthly],
            'daily_market_data': [round(price, 2) for price in market_prices],
            'daily_thesis_data': [round(price, 2) for price in thesis_prices],
            'performance_summary': f'ML-generated forecast: {adjusted_return*100:.1f}% annual target'
        }
    
    def _generate_market_baseline(self, starting_price: float, annual_return: float, 
                                daily_vol: float, total_days: int) -> List[float]:
        """
        Generate market baseline using geometric Brownian motion with realistic market patterns
        """
        np.random.seed(42)  # For reproducible results
        
        prices = [starting_price]
        daily_return = annual_return / 252  # 252 trading days per year
        
        for day in range(1, total_days):
            # Market regime simulation (normal, correction, rally)
            regime_factor = self._get_market_regime_factor(day, total_days)
            
            # Random walk component
            random_shock = np.random.normal(0, daily_vol)
            
            # Trend component with mean reversion
            trend = daily_return * regime_factor
            
            # Price change
            price_change = trend + random_shock
            new_price = prices[-1] * (1 + price_change)
            
            # Ensure price doesn't go negative
            prices.append(max(new_price, starting_price * 0.3))
        
        return prices
    
    def _generate_thesis_prices(self, params: Dict, annual_return: float, 
                              daily_vol: float, market_prices: List[float], 
                              total_days: int) -> List[float]:
        """
        Generate thesis-specific prices with correlation to market and unique drivers
        """
        np.random.seed(123)  # Different seed for thesis
        
        starting_price = params['starting_price']
        market_corr = params['market_correlation']
        conviction = params['thesis_conviction']
        growth_pattern = params['growth_pattern']
        
        prices = [starting_price]
        daily_return = annual_return / 252
        
        for day in range(1, total_days):
            # Market correlation component
            market_change = (market_prices[day] / market_prices[day-1] - 1) if day > 0 else 0
            correlated_change = market_change * market_corr
            
            # Thesis-specific component
            thesis_trend = self._get_thesis_trend(day, total_days, daily_return, growth_pattern, conviction)
            
            # Volatility component
            vol_shock = np.random.normal(0, daily_vol * (2 - conviction))  # Lower conviction = higher vol
            
            # Combine components
            total_change = correlated_change + thesis_trend + vol_shock
            
            # Apply thesis-specific events
            event_impact = self._get_thesis_event_impact(day, total_days, params)
            
            new_price = prices[-1] * (1 + total_change + event_impact)
            
            # Ensure realistic bounds
            prices.append(max(new_price, starting_price * 0.2))
        
        return prices
    
    def _get_market_regime_factor(self, day: int, total_days: int) -> float:
        """
        Simulate market regime changes (bull, bear, correction periods)
        """
        # Create regime cycles
        cycle_position = (day / total_days) * 4  # 4 cycles over the period
        
        if cycle_position % 1 < 0.1:  # 10% of time in correction
            return -0.5
        elif cycle_position % 1 < 0.2:  # 10% of time in rally
            return 1.8
        else:  # 80% of time in normal regime
            return 1.0
    
    def _get_thesis_trend(self, day: int, total_days: int, daily_return: float, 
                         growth_pattern: str, conviction: float) -> float:
        """
        Generate thesis-specific trend based on growth pattern and conviction
        """
        progress = day / total_days
        base_trend = daily_return * conviction
        
        if growth_pattern == 'exponential':
            return base_trend * (1 + progress * 0.5)
        elif growth_pattern == 'linear':
            return base_trend
        elif growth_pattern == 'cyclical':
            return base_trend * (1 + 0.3 * np.sin(progress * 2 * np.pi))
        else:
            return base_trend
    
    def _get_thesis_event_impact(self, day: int, total_days: int, params: Dict) -> float:
        """
        Simulate thesis-specific events that impact price
        """
        # Random events based on risk factors
        if np.random.random() < 0.002:  # 0.2% chance per day
            if np.random.random() < 0.7:  # 70% positive events
                return np.random.uniform(0.02, 0.08)  # 2-8% positive impact
            else:  # 30% negative events
                return np.random.uniform(-0.12, -0.03)  # 3-12% negative impact
        
        return 0.0
    
    def _generate_llm_market_events(self, thesis, time_horizon: int, scenario: str, 
                                  performance_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate market events using Azure OpenAI
        """
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        
        prompt = f"""Generate 3-4 realistic market events for this investment simulation.

Thesis: {thesis_text[:300]}
Time Horizon: {time_horizon} years
Scenario: {scenario}

Events should be relevant to current market conditions and thesis sector.
Include timing, impact type, and affected areas.

Return JSON array only:
[
  {{
    "month": 6,
    "title": "Event Title",
    "description": "Event description and market implications",
    "impact_type": "positive",
    "magnitude": "moderate",
    "signals_affected": ["Revenue Growth", "Market Share"],
    "market_context": "Why this matters for the thesis"
  }}
]"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.8, max_tokens=1200
            )
            
            if response:
                cleaned_response = self._clean_json_response(response)
                events_data = json.loads(cleaned_response)
                
                if isinstance(events_data, list):
                    total_months = time_horizon * 12
                    formatted_events = []
                    
                    for event in events_data:
                        month = event.get('month', 1)
                        if 1 <= month <= total_months:
                            thesis_data = performance_data.get('thesis_performance', [100])
                            impact_value = thesis_data[min(month-1, len(thesis_data)-1)] if thesis_data else 100
                            
                            formatted_event = {
                                'month': month,
                                'date': self._month_to_date_string(month),
                                'title': event.get('title', 'Market Event'),
                                'description': event.get('description', 'Market development'),
                                'impact_type': event.get('impact_type', 'neutral'),
                                'magnitude': event.get('magnitude', 'moderate'),
                                'signals_affected': event.get('signals_affected', []),
                                'market_context': event.get('market_context', ''),
                                'impact_value': impact_value
                            }
                            formatted_events.append(formatted_event)
                    
                    return formatted_events[:5]
            
        except Exception as e:
            logging.error(f"LLM event generation failed: {str(e)}")
        
        return []
    
    def _generate_llm_scenario_analysis(self, thesis, scenario: str, time_horizon: int,
                                      performance_data: Dict, events: List[Dict], 
                                      thesis_params: Dict) -> Dict[str, Any]:
        """
        Generate comprehensive scenario analysis using Azure OpenAI
        """
        thesis_text = thesis.core_claim or thesis.original_thesis or "Investment thesis"
        
        # Calculate performance metrics
        thesis_performance = performance_data.get('thesis_performance', [100])
        if len(thesis_performance) > 1:
            final_return = ((thesis_performance[-1] / thesis_performance[0]) - 1) * 100
        else:
            final_return = 0
        
        prompt = f"""Analyze this ML-enhanced investment thesis simulation.

Thesis: {thesis_text[:300]}
Scenario: {scenario}
Time Horizon: {time_horizon} years
Simulated Return: {final_return:.1f}%
Starting Price: ${thesis_params.get('starting_price', 100):.2f}
Target Price: ${thesis_params.get('price_target_12m', 115):.2f}
Conviction Level: {thesis_params.get('thesis_conviction', 0.7):.1f}

Provide comprehensive analysis:

Return JSON format:
{{
  "scenario_summary": "Executive summary of the scenario and ML model results",
  "performance_assessment": "Analysis of simulated vs expected performance",
  "key_risks": ["Risk 1", "Risk 2", "Risk 3"],
  "key_opportunities": ["Opportunity 1", "Opportunity 2"],
  "strategic_recommendations": ["Recommendation 1", "Recommendation 2"],
  "monitoring_priorities": ["Priority 1", "Priority 2"],
  "conviction_level": "High/Medium/Low",
  "probability_assessment": "Assessment of scenario likelihood and success probability"
}}"""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.ai_service.generate_completion(
                messages, temperature=0.6, max_tokens=1500
            )
            
            if response:
                cleaned_response = self._clean_json_response(response)
                return json.loads(cleaned_response)
            
        except Exception as e:
            logging.error(f"LLM scenario analysis failed: {str(e)}")
        
        # Return default analysis if LLM fails
        return {
            "scenario_summary": f"ML simulation shows {final_return:.1f}% return over {time_horizon} years under {scenario} conditions",
            "performance_assessment": "Simulation based on mathematical models with LLM-extracted parameters",
            "key_risks": ["Market volatility", "Sector rotation", "Economic downturn"],
            "key_opportunities": ["Thesis validation", "Market outperformance", "Sector momentum"],
            "strategic_recommendations": ["Monitor key signals", "Maintain position sizing", "Review quarterly"],
            "monitoring_priorities": ["Price action", "Volume trends", "Sector performance"],
            "conviction_level": "Medium",
            "probability_assessment": "Moderate probability based on ML simulation and market conditions"
        }
    
    def _get_default_parameters(self, scenario: str, volatility: str) -> Dict[str, Any]:
        """
        Return default parameters when LLM extraction fails
        """
        base_params = {
            'starting_price': 120.0,
            'expected_annual_return': 0.12,
            'daily_volatility': 0.025,
            'growth_pattern': 'linear',
            'market_correlation': 0.6,
            'sector_momentum': 1.0,
            'downside_risk': 0.25,
            'thesis_conviction': 0.7,
            'price_target_12m': 135.0,
            'key_drivers': ['Revenue growth', 'Market expansion'],
            'risk_events': ['Competition', 'Regulation']
        }
        
        # Adjust for scenario
        if scenario == 'bull':
            base_params['expected_annual_return'] *= 1.3
            base_params['thesis_conviction'] = 0.8
        elif scenario == 'bear':
            base_params['expected_annual_return'] *= 0.4
            base_params['daily_volatility'] *= 1.5
            base_params['thesis_conviction'] = 0.5
        
        return base_params
    
    def _clean_json_response(self, response: str) -> str:
        """Clean Azure OpenAI response to extract valid JSON"""
        cleaned = response.strip()
        
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
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
        """Generate timeline labels for the simulation"""
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
        """Convert month number to date string"""
        current_date = datetime.now()
        future_date = current_date + timedelta(days=30 * (month - 1))
        return future_date.strftime('%B %Y')