"""
Simulation Service for Investment Thesis Performance and Event Modeling

Generates realistic time-series performance data and event scenarios
using Azure OpenAI for intelligent simulation generation.
"""

import json
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService


class SimulationService:
    """
    Comprehensive simulation service for investment thesis modeling
    """
    
    def __init__(self):
        self.ai_service = AzureOpenAIService()
        
    def generate_simulation(self, thesis, time_horizon: int, scenario: str, 
                          volatility: str, include_events: bool, simulation_type: str) -> Dict[str, Any]:
        """
        Generate comprehensive thesis simulation with performance data and events
        """
        # Generate base performance simulation
        performance_data = self._generate_performance_simulation(
            thesis, time_horizon, scenario, volatility
        )
        
        # Generate timeline labels
        timeline = self._generate_timeline(time_horizon)
        
        # Generate events if requested
        events = []
        if include_events:
            events = self._generate_event_scenarios(
                thesis, time_horizon, scenario, performance_data
            )
        
        # Create chart configuration
        chart_config = self._create_chart_config(thesis, scenario, simulation_type)
        
        return {
            'performance_data': performance_data,
            'timeline': timeline,
            'events': events,
            'chart_config': chart_config,
            'scenario_summary': self._create_scenario_summary(thesis, scenario, time_horizon),
            'simulation_metadata': {
                'thesis_id': thesis.id,
                'thesis_title': thesis.title,
                'scenario': scenario,
                'volatility': volatility,
                'time_horizon': time_horizon,
                'include_events': include_events,
                'simulation_type': simulation_type,
                'generated_at': datetime.utcnow().isoformat()
            }
        }
    
    def _generate_performance_simulation(self, thesis, time_horizon: int, 
                                       scenario: str, volatility: str) -> List[float]:
        """
        Generate realistic performance data using AI-powered simulation
        """
        try:
            # Create intelligent simulation prompt
            prompt = f"""
            Generate a realistic {time_horizon}-year performance simulation for the following investment thesis:
            
            Thesis: {thesis.title}
            Core Claim: {thesis.core_claim or 'Investment opportunity analysis'}
            Scenario: {scenario}
            Volatility: {volatility}
            
            Create a monthly performance simulation with realistic market behavior including:
            - Trend direction based on scenario (bull/bear/base/stress)
            - Appropriate volatility levels
            - Realistic market cycles and corrections
            - Seasonal patterns where applicable
            
            Return ONLY a JSON array of {time_horizon * 12} monthly percentage values representing cumulative performance.
            Start at 100 (baseline) and show realistic progression.
            
            Example format: [100, 102.5, 101.8, 105.2, ...]
            
            Scenario guidelines:
            - bull: 8-15% annual growth with moderate volatility
            - base: 3-8% annual growth with normal volatility  
            - bear: -5% to +2% annual with higher volatility
            - stress: -20% to -5% annual with extreme volatility
            """
            
            response = self.ai_service.generate_completion([
                {"role": "system", "content": "You are a financial modeling expert. Generate realistic market performance data."},
                {"role": "user", "content": prompt}
            ], temperature=0.7)
            
            # Parse the response
            try:
                performance_data = json.loads(response)
                if isinstance(performance_data, list) and len(performance_data) == time_horizon * 12:
                    return performance_data
                else:
                    raise ValueError("Invalid data format")
            except (json.JSONDecodeError, ValueError):
                # Fallback to algorithmic generation
                return self._generate_algorithmic_performance(time_horizon, scenario, volatility)
                
        except Exception as e:
            print(f"AI simulation failed, using algorithmic fallback: {e}")
            return self._generate_algorithmic_performance(time_horizon, scenario, volatility)
    
    def _generate_algorithmic_performance(self, time_horizon: int, scenario: str, volatility: str) -> List[float]:
        """
        Fallback algorithmic performance generation
        """
        months = time_horizon * 12
        data = [100.0]  # Start at baseline
        
        # Scenario parameters
        scenario_params = {
            'bull': {'annual_return': 0.12, 'volatility_mult': 1.0},
            'base': {'annual_return': 0.06, 'volatility_mult': 1.2},
            'bear': {'annual_return': -0.02, 'volatility_mult': 1.5},
            'stress': {'annual_return': -0.15, 'volatility_mult': 2.0}
        }
        
        volatility_params = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.8
        }
        
        params = scenario_params.get(scenario, scenario_params['base'])
        vol_mult = volatility_params.get(volatility, 1.0)
        
        monthly_return = params['annual_return'] / 12
        monthly_vol = (params['volatility_mult'] * vol_mult * 0.15) / math.sqrt(12)
        
        for i in range(1, months):
            # Add trend + noise + some autocorrelation
            trend = monthly_return
            noise = random.gauss(0, monthly_vol)
            
            # Add market cycle effects
            cycle_effect = 0.02 * math.sin(2 * math.pi * i / 24)  # 2-year cycle
            
            # Add some mean reversion
            deviation = (data[i-1] - 100) / 100
            reversion = -0.1 * deviation
            
            monthly_change = trend + noise + cycle_effect + reversion
            data.append(data[i-1] * (1 + monthly_change))
        
        return data
    
    def _generate_event_scenarios(self, thesis, time_horizon: int, scenario: str, 
                                performance_data: List[float]) -> List[Dict[str, Any]]:
        """
        Generate realistic market events and their impacts
        """
        try:
            # Use AI to generate contextual events
            prompt = f"""
            Generate 3-6 realistic market events over {time_horizon} years for this investment thesis:
            
            Thesis: {thesis.title}
            Core Claim: {thesis.core_claim or 'Investment analysis'}
            Scenario: {scenario}
            
            Create events that would realistically impact this thesis, including:
            - Market corrections, earnings announcements, regulatory changes
            - Industry developments, competitive threats, macroeconomic events
            - Technology disruptions, geopolitical events
            
            For each event, specify:
            - Realistic timing (month 1-{time_horizon * 12})
            - Event title and description
            - Impact type (positive/negative/neutral)
            - Which signals would be affected
            - Whether it would trigger notifications
            
            Return ONLY valid JSON format:
            [{{
                "month": 8,
                "title": "Q2 Earnings Beat",
                "description": "Company reports stronger than expected quarterly results",
                "impact_type": "positive",
                "impact_value": 105.2,
                "notification_triggered": true,
                "signals_affected": ["Quarterly Revenue Growth", "Operating Margin"]
            }}]
            """
            
            response = self.ai_service.generate_completion([
                {"role": "system", "content": "You are a financial analyst. Generate realistic market events as JSON."},
                {"role": "user", "content": prompt}
            ], temperature=0.8)
            
            try:
                events_data = json.loads(response)
                if isinstance(events_data, list):
                    # Process and format events
                    formatted_events = []
                    for event in events_data:
                        month = event.get('month', 1)
                        if 1 <= month <= len(performance_data):
                            formatted_event = {
                                'date': self._month_to_date(month, time_horizon),
                                'title': event.get('title', 'Market Event'),
                                'description': event.get('description', 'Market development'),
                                'impact_type': event.get('impact_type', 'neutral'),
                                'impact_value': performance_data[month - 1] if month <= len(performance_data) else 100,
                                'notification_triggered': event.get('notification_triggered', False),
                                'signals_affected': event.get('signals_affected', [])
                            }
                            formatted_events.append(formatted_event)
                    
                    return formatted_events[:6]  # Limit to 6 events
                
            except (json.JSONDecodeError, ValueError):
                pass
                
        except Exception as e:
            print(f"AI event generation failed: {e}")
        
        # Fallback event generation
        return self._generate_fallback_events(time_horizon, scenario, performance_data)
    
    def _generate_fallback_events(self, time_horizon: int, scenario: str, 
                                performance_data: List[float]) -> List[Dict[str, Any]]:
        """
        Generate fallback events when AI generation fails
        """
        event_templates = [
            {
                'title': 'Quarterly Earnings Release',
                'description': 'Company reports quarterly financial results',
                'impact_type': 'positive' if scenario in ['bull', 'base'] else 'negative',
                'notification_triggered': True,
                'signals_affected': ['Quarterly Revenue Growth', 'Operating Margin']
            },
            {
                'title': 'Market Correction',
                'description': 'Broader market experiences volatility',
                'impact_type': 'negative',
                'notification_triggered': True,
                'signals_affected': ['Free Cash Flow']
            },
            {
                'title': 'Industry Development',
                'description': 'Significant development in the industry sector',
                'impact_type': 'positive' if scenario == 'bull' else 'neutral',
                'notification_triggered': False,
                'signals_affected': []
            }
        ]
        
        events = []
        num_events = min(4, time_horizon + 1)
        
        for i in range(num_events):
            template = random.choice(event_templates)
            month = random.randint(1, min(len(performance_data), time_horizon * 12))
            
            event = {
                'date': self._month_to_date(month, time_horizon),
                'title': template['title'],
                'description': template['description'],
                'impact_type': template['impact_type'],
                'impact_value': performance_data[month - 1] if month <= len(performance_data) else 100,
                'notification_triggered': template['notification_triggered'],
                'signals_affected': template['signals_affected']
            }
            events.append(event)
        
        return events
    
    def _generate_timeline(self, time_horizon: int) -> List[str]:
        """
        Generate timeline labels for the chart
        """
        timeline = []
        start_date = datetime.now()
        
        for month in range(time_horizon * 12):
            date = start_date + timedelta(days=30 * month)
            if month % 3 == 0:  # Show every quarter
                timeline.append(date.strftime('%Y Q%q').replace('Q1', 'Q1').replace('Q2', 'Q2').replace('Q3', 'Q3').replace('Q4', 'Q4'))
            else:
                timeline.append('')
        
        return timeline
    
    def _month_to_date(self, month: int, time_horizon: int) -> str:
        """
        Convert month number to readable date
        """
        start_date = datetime.now()
        target_date = start_date + timedelta(days=30 * (month - 1))
        return target_date.strftime('%Y-%m')
    
    def _create_chart_config(self, thesis, scenario: str, simulation_type: str) -> Dict[str, Any]:
        """
        Create chart configuration based on thesis and scenario
        """
        scenario_colors = {
            'bull': 'rgb(34, 197, 94)',      # Green
            'base': 'rgb(59, 130, 246)',     # Blue  
            'bear': 'rgb(239, 68, 68)',      # Red
            'stress': 'rgb(147, 51, 234)'    # Purple
        }
        
        scenario_names = {
            'bull': 'Bull Case',
            'base': 'Base Case', 
            'bear': 'Bear Case',
            'stress': 'Stress Test'
        }
        
        return {
            'title': f'{thesis.title} - {scenario_names.get(scenario, scenario.title())} Simulation',
            'primary_metric': 'Performance Index',
            'y_axis_label': 'Cumulative Performance (%)',
            'color': scenario_colors.get(scenario, 'rgb(75, 192, 192)'),
            'scenario': scenario,
            'simulation_type': simulation_type
        }
    
    def _create_scenario_summary(self, thesis, scenario: str, time_horizon: int) -> str:
        """
        Create a summary description of the simulation scenario
        """
        scenario_descriptions = {
            'bull': f'Optimistic {time_horizon}-year projection assuming favorable market conditions and strong execution',
            'base': f'Expected {time_horizon}-year trajectory under normal market conditions',
            'bear': f'Conservative {time_horizon}-year outlook considering potential headwinds and challenges', 
            'stress': f'Stress test scenario modeling extreme market conditions over {time_horizon} years'
        }
        
        return scenario_descriptions.get(scenario, f'{time_horizon}-year simulation scenario')