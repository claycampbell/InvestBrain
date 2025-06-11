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
        Generate realistic performance data using Azure OpenAI simulation
        """
        try:
            # Create intelligent simulation prompt
            prompt = f"""
            Generate a realistic {time_horizon}-year monthly performance simulation for this investment thesis:
            
            Thesis: {thesis.title}
            Core Claim: {thesis.core_claim or 'Investment opportunity analysis'}
            Scenario: {scenario}
            Volatility: {volatility}
            
            Create {time_horizon * 12} monthly data points showing cumulative performance starting at 100.
            Include realistic market behavior:
            - {scenario} scenario characteristics
            - {volatility} volatility patterns
            - Market cycles and corrections
            - Seasonal effects where applicable
            
            Scenario guidelines:
            - bull: 8-15% annual growth with moderate volatility
            - base: 3-8% annual growth with normal volatility  
            - bear: -5% to +2% annual with higher volatility
            - stress: -20% to -5% annual with extreme volatility
            
            Return ONLY a JSON array of {time_horizon * 12} numbers:
            [100, 102.1, 99.8, 104.5, ...]
            """
            
            messages = [
                {"role": "system", "content": "You are a quantitative financial analyst. Generate realistic market performance data as a JSON array."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.ai_service.generate_completion(messages, temperature=0.7, max_tokens=2000)
            
            # Clean and parse the response
            response_cleaned = response.strip()
            if response_cleaned.startswith('```json'):
                response_cleaned = response_cleaned[7:]
            if response_cleaned.endswith('```'):
                response_cleaned = response_cleaned[:-3]
            
            performance_data = json.loads(response_cleaned.strip())
            
            if isinstance(performance_data, list) and len(performance_data) == time_horizon * 12:
                # Validate data is reasonable
                if all(isinstance(x, (int, float)) and 50 <= x <= 300 for x in performance_data):
                    return performance_data
                    
        except Exception as e:
            print(f"Azure OpenAI simulation generation failed: {e}")
        
        # Fallback to algorithmic generation only if AI fails
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
        Generate realistic market events and their impacts using Azure OpenAI
        """
        try:
            # Get the signals that exist for this thesis
            signals_list = []
            if hasattr(thesis, 'signals') and thesis.signals:
                signals_list = [signal.signal_name for signal in thesis.signals]
            
            if not signals_list:
                signals_list = ["Quarterly Revenue Growth", "Operating Margin", "Free Cash Flow"]
            
            prompt = f"""
            Generate 3-5 realistic market events over {time_horizon} years for this investment thesis:
            
            Thesis: {thesis.title}
            Core Claim: {thesis.core_claim or 'Investment opportunity analysis'}
            Scenario: {scenario}
            Available Signals: {', '.join(signals_list)}
            
            Create events that would realistically impact this thesis, including:
            - Earnings announcements, regulatory changes, market corrections
            - Industry developments, competitive threats, macroeconomic events
            - Technology disruptions, geopolitical events
            
            For each event:
            - Timing: month 1-{time_horizon * 12}
            - Realistic title and description
            - Impact type: positive/negative/neutral
            - Whether it triggers notifications
            - Which signals are affected
            
            Return ONLY valid JSON:
            [{{
                "month": 8,
                "title": "Q2 Earnings Beat Expectations",
                "description": "Company reports stronger than expected quarterly results",
                "impact_type": "positive",
                "notification_triggered": true,
                "signals_affected": ["Quarterly Revenue Growth", "Operating Margin"]
            }}]
            """
            
            messages = [
                {"role": "system", "content": "You are a financial analyst. Generate realistic market events as JSON array."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.ai_service.generate_completion(messages, temperature=0.8, max_tokens=1500)
            
            # Clean and parse the response
            response_cleaned = response.strip()
            if response_cleaned.startswith('```json'):
                response_cleaned = response_cleaned[7:]
            if response_cleaned.endswith('```'):
                response_cleaned = response_cleaned[:-3]
            
            events_data = json.loads(response_cleaned.strip())
            
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
                
        except Exception as e:
            print(f"Azure OpenAI event generation failed: {e}")
        
        # Fallback to intelligent algorithmic events
        return self._generate_intelligent_events(thesis, time_horizon, scenario, performance_data)
    
    def _generate_intelligent_events(self, thesis, time_horizon: int, scenario: str, 
                                   performance_data: List[float]) -> List[Dict[str, Any]]:
        """
        Generate contextually relevant events based on thesis content and scenario
        """
        # Analyze thesis for relevant event types
        thesis_keywords = self._extract_thesis_keywords(thesis)
        
        # Define event templates based on common investment scenarios
        event_templates = self._get_event_templates_by_scenario(scenario, thesis_keywords)
        
        # Generate events with realistic timing and impacts
        events = []
        num_events = min(random.randint(3, 6), time_horizon + 2)
        
        used_months = set()
        for i in range(num_events):
            template = random.choice(event_templates)
            
            # Pick a month that hasn't been used and has realistic spacing
            month = self._select_event_month(used_months, time_horizon, len(performance_data))
            if month is None:
                continue
                
            used_months.add(month)
            
            event = {
                'date': self._month_to_date(month, time_horizon),
                'title': template['title'],
                'description': template['description'],
                'impact_type': template['impact_type'],
                'impact_value': performance_data[month - 1] if month <= len(performance_data) else 100,
                'notification_triggered': template['notification_triggered'],
                'signals_affected': template.get('signals_affected', [])
            }
            events.append(event)
        
        # Sort events by date
        events.sort(key=lambda x: x['date'])
        return events
    
    def _extract_thesis_keywords(self, thesis) -> List[str]:
        """
        Extract key themes from thesis for contextual event generation
        """
        text = f"{thesis.title} {thesis.core_claim or ''}"
        
        # Common investment themes
        themes = {
            'tech': ['technology', 'ai', 'artificial intelligence', 'software', 'digital', 'cloud'],
            'energy': ['energy', 'oil', 'renewable', 'solar', 'wind', 'battery'],
            'healthcare': ['healthcare', 'pharma', 'biotech', 'medical', 'drug'],
            'finance': ['bank', 'financial', 'fintech', 'payment', 'credit'],
            'consumer': ['consumer', 'retail', 'brand', 'ecommerce', 'restaurant'],
            'industrial': ['manufacturing', 'infrastructure', 'construction', 'automotive'],
            'growth': ['growth', 'expansion', 'scaling', 'revenue', 'margin'],
            'dividend': ['dividend', 'income', 'yield', 'cash flow', 'distribution']
        }
        
        detected_themes = []
        text_lower = text.lower()
        
        for theme, keywords in themes.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes if detected_themes else ['general']
    
    def _get_event_templates_by_scenario(self, scenario: str, themes: List[str]) -> List[Dict[str, Any]]:
        """
        Get contextually relevant event templates
        """
        base_events = [
            {
                'title': 'Quarterly Earnings Release',
                'description': 'Company reports quarterly financial results with market reaction',
                'impact_type': 'positive' if scenario in ['bull', 'base'] else 'negative',
                'notification_triggered': True,
                'signals_affected': ['Quarterly Revenue Growth', 'Operating Margin']
            },
            {
                'title': 'Market Volatility Event',
                'description': 'Broader market experiences increased volatility affecting sector performance',
                'impact_type': 'negative' if scenario in ['bear', 'stress'] else 'neutral',
                'notification_triggered': True,
                'signals_affected': ['Free Cash Flow']
            },
            {
                'title': 'Industry Conference Impact',
                'description': 'Key industry event generates investor attention and sector movement',
                'impact_type': 'positive' if scenario == 'bull' else 'neutral',
                'notification_triggered': False,
                'signals_affected': []
            }
        ]
        
        # Add theme-specific events
        theme_events = {
            'tech': [
                {
                    'title': 'Technology Innovation Announcement',
                    'description': 'Major technological breakthrough impacts competitive positioning',
                    'impact_type': 'positive' if scenario != 'bear' else 'negative',
                    'notification_triggered': True,
                    'signals_affected': ['Quarterly Revenue Growth']
                }
            ],
            'energy': [
                {
                    'title': 'Commodity Price Movement',
                    'description': 'Significant energy commodity price changes affect industry dynamics',
                    'impact_type': 'positive' if scenario == 'bull' else 'negative',
                    'notification_triggered': True,
                    'signals_affected': ['Operating Margin']
                }
            ],
            'healthcare': [
                {
                    'title': 'Regulatory Development',
                    'description': 'Healthcare regulatory changes impact sector outlook',
                    'impact_type': 'neutral',
                    'notification_triggered': True,
                    'signals_affected': ['Free Cash Flow']
                }
            ]
        }
        
        events = base_events.copy()
        for theme in themes:
            if theme in theme_events:
                events.extend(theme_events[theme])
        
        return events
    
    def _select_event_month(self, used_months: set, time_horizon: int, data_length: int) -> Optional[int]:
        """
        Select a realistic month for an event with proper spacing
        """
        max_month = min(time_horizon * 12, data_length)
        available_months = []
        
        for month in range(1, max_month + 1):
            # Ensure at least 2 months spacing between events
            if month not in used_months and all(abs(month - used) >= 2 for used in used_months):
                available_months.append(month)
        
        return random.choice(available_months) if available_months else None
    
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
            if month % 6 == 0:  # Show every 6 months for better readability
                timeline.append(date.strftime('%Y-%m'))
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