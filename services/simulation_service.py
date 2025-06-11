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
        
        # Check if performance generation returned an error
        if isinstance(performance_data, dict) and performance_data.get('error'):
            return {
                'error': True,
                'message': performance_data.get('message', 'Azure OpenAI service unavailable'),
                'description': performance_data.get('description', 'Valid API credentials required'),
                'action_needed': performance_data.get('action_needed', 'Configure Azure OpenAI credentials'),
                'chart_data': None,
                'events': [],
                'scenario_summary': 'Simulation requires Azure OpenAI credentials'
            }
        
        # Generate timeline labels
        timeline = self._generate_timeline(time_horizon)
        
        # Generate events if requested
        events = []
        if include_events:
            try:
                # Use combined performance data for event positioning
                event_data = performance_data if isinstance(performance_data, list) else performance_data.get('combined_performance', [])
                events = self._generate_event_scenarios(
                    thesis, time_horizon, scenario, event_data
                )
            except Exception as e:
                print(f"Event generation failed: {e}")
                events = []
        
        # Create chart configuration
        chart_config = self._create_chart_config(thesis, scenario, simulation_type)
        
        return {
            'chart_data': {
                'performance_data': performance_data,
                'timeline': timeline
            },
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
                                       scenario: str, volatility: str):
        """
        Generate realistic performance data using Azure OpenAI simulation
        """
        # Attempt LLM generation with optimized approach
        if self.ai_service and self.ai_service.is_available():
            try:
                # For o4-mini model, use very concise prompts to avoid length limits
                months = time_horizon * 12
                
                # Generate in smaller chunks to avoid length limits
                if months <= 12:
                    # Enhanced prompt for realistic market volatility
                    prompt = f"""Generate {months} realistic monthly investment values with volatility for {scenario} scenario:
- Market: broad market with ups/downs, starting 100
- Conviction: thesis strength with fluctuations, starting 100  
- Performance: combined result with realistic swings, starting 100

Include market volatility, corrections, rallies. No linear growth.
JSON: {{"market": [100,98.5,102.3,...], "conviction": [100,103.2,97.1,...], "performance": [100,101.8,99.4,...]}}"""
                    messages = [{"role": "user", "content": prompt}]
                    
                    response = self.ai_service.generate_completion(messages, temperature=1.0, max_tokens=300)
                    
                    print(f"Azure OpenAI response received: {len(response)} characters")
                    print(f"Response preview: {response[:200]}...")
                    
                    # Extract numbers from response with improved parsing
                    import re
                    import json
                    
                    # Try to find JSON object with three series first
                    try:
                        # Look for JSON object with market, conviction, performance arrays
                        json_match = re.search(r'\{[^}]*"market"[^}]*"conviction"[^}]*"performance"[^}]*\}', response, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            data_obj = json.loads(json_str)
                            
                            market_data = data_obj.get('market', [])
                            conviction_data = data_obj.get('conviction', [])
                            performance_data = data_obj.get('performance', [])
                            
                            if (len(market_data) >= months and len(conviction_data) >= months and len(performance_data) >= months):
                                result = {
                                    'market_performance': [float(x) for x in market_data[:months]],
                                    'thesis_conviction': [float(x) for x in conviction_data[:months]],
                                    'combined_performance': [float(x) for x in performance_data[:months]]
                                }
                                print(f"Generated 3-series LLM simulation data: {months} points each")
                                return result
                    except Exception as e:
                        print(f"Failed to parse 3-series JSON: {e}")
                    
                    # Fallback: try single array format
                    try:
                        json_match = re.search(r'\[[\d\s,.\-]+\]', response)
                        if json_match:
                            json_str = json_match.group()
                            performance_data = json.loads(json_str)
                            if len(performance_data) >= months:
                                single_series = [float(x) for x in performance_data[:months]]
                                # Generate market and conviction from single series
                                market_series = [100 + (x - 100) * 0.7 for x in single_series]  # Less volatile
                                conviction_series = [100 + (x - 100) * 1.3 for x in single_series]  # More volatile
                                
                                result = {
                                    'market_performance': market_series,
                                    'thesis_conviction': conviction_series,
                                    'combined_performance': single_series
                                }
                                print(f"Generated derived 3-series simulation data: {months} points each")
                                return result
                    except Exception as e:
                        print(f"Failed to parse single array: {e}")
                
            except Exception as e:
                print(f"LLM generation failed: {e}")
                
                # If Azure OpenAI fails but credentials exist, generate realistic volatile fallback
                if self.ai_service and hasattr(self.ai_service, 'client') and self.ai_service.client:
                    print("Generating realistic volatile fallback due to Azure OpenAI timeout")
                    import random
                    import math
                    
                    # Create realistic market volatility patterns
                    market_data = [100]
                    conviction_data = [100]
                    performance_data = [100]
                    
                    for i in range(1, months):
                        # Market volatility with corrections and rallies
                        market_change = random.gauss(0.008, 0.035)  # Monthly return with volatility
                        if random.random() < 0.15:  # 15% chance of larger move
                            market_change *= random.choice([2.5, -1.8])
                        market_val = market_data[-1] * (1 + market_change)
                        market_data.append(max(70, min(150, market_val)))
                        
                        # Thesis conviction with different pattern
                        conviction_change = random.gauss(0.015, 0.045)  # Higher volatility
                        if scenario == 'bull':
                            conviction_change += 0.008
                        elif scenario == 'bear':
                            conviction_change -= 0.012
                        conviction_val = conviction_data[-1] * (1 + conviction_change)
                        conviction_data.append(max(75, min(160, conviction_val)))
                        
                        # Combined performance (weighted average with noise)
                        combined_change = 0.6 * market_change + 0.4 * conviction_change + random.gauss(0, 0.02)
                        combined_val = performance_data[-1] * (1 + combined_change)
                        performance_data.append(max(72, min(155, combined_val)))
                    
                    return {
                        'market_performance': [round(x, 1) for x in market_data],
                        'thesis_conviction': [round(x, 1) for x in conviction_data], 
                        'combined_performance': [round(x, 1) for x in performance_data],
                        '_fallback_reason': 'Azure OpenAI timeout - realistic volatile simulation'
                    }
        
        # Return error state when Azure OpenAI is not available
        return {
            'error': True,
            'message': 'Azure OpenAI service unavailable',
            'description': 'Valid API credentials required for LLM-generated simulation data',
            'action_needed': 'Configure Azure OpenAI credentials'
        }
    
    def _generate_algorithmic_performance(self, time_horizon: int, scenario: str, volatility: str) -> List[float]:
        """
        Enhanced algorithmic performance generation designed to mimic LLM output patterns
        """
        months = time_horizon * 12
        data = [100.0]  # Start at baseline
        
        # Enhanced scenario parameters with realistic market behavior
        scenario_params = {
            'bull': {'annual_return': 0.14, 'volatility_mult': 0.9, 'momentum': 1.3, 'corrections': 0.7},
            'base': {'annual_return': 0.07, 'volatility_mult': 1.0, 'momentum': 1.0, 'corrections': 1.0},
            'bear': {'annual_return': -0.01, 'volatility_mult': 1.4, 'momentum': 0.7, 'corrections': 1.4},
            'stress': {'annual_return': -0.18, 'volatility_mult': 2.1, 'momentum': 0.5, 'corrections': 2.0}
        }
        
        volatility_params = {
            'low': 0.6, 'moderate': 1.0, 'high': 1.5, 'extreme': 2.3
        }
        
        params = scenario_params.get(scenario, scenario_params['base'])
        vol_mult = volatility_params.get(volatility, 1.0)
        
        monthly_return = params['annual_return'] / 12
        base_vol = 0.16 / math.sqrt(12)  # Base monthly volatility
        monthly_vol = base_vol * params['volatility_mult'] * vol_mult
        
        # State variables for realistic market dynamics
        momentum = 0
        market_regime = 'normal'  # normal, correction, rally
        regime_duration = 0
        
        for i in range(1, months):
            # Market regime transitions (realistic market phases)
            if regime_duration > random.randint(3, 12):
                if market_regime == 'normal':
                    market_regime = random.choice(['correction', 'rally'] if scenario in ['bull', 'base'] else ['correction'])
                else:
                    market_regime = 'normal'
                regime_duration = 0
            
            regime_duration += 1
            
            # Regime-specific adjustments
            regime_adjustments = {
                'normal': {'return_mult': 1.0, 'vol_mult': 1.0},
                'correction': {'return_mult': -2.5, 'vol_mult': 1.8},
                'rally': {'return_mult': 2.2, 'vol_mult': 0.7}
            }
            
            regime_adj = regime_adjustments[market_regime]
            
            # Momentum with persistence and mean reversion
            momentum = momentum * 0.75 + random.gauss(0, 0.015) * params['momentum']
            
            # Market cycles (business cycle effects)
            cycle_effect = 0.025 * math.sin(2 * math.pi * i / 22) * (1 + 0.3 * random.random())
            
            # Seasonal patterns (Q4 rally, January effect, summer doldrums)
            month_in_year = i % 12
            seasonal_effects = {0: 0.01, 1: 0.005, 5: -0.003, 6: -0.002, 10: 0.008, 11: 0.012}
            seasonal = seasonal_effects.get(month_in_year, 0)
            
            # Volatility clustering (GARCH-like behavior)
            vol_persistence = 0.85
            current_vol = monthly_vol * (vol_persistence + (1 - vol_persistence) * random.uniform(0.5, 1.8))
            
            # Fat tails and skewness in returns
            if random.random() < 0.08:  # 8% chance of extreme moves
                shock_magnitude = random.uniform(2.0, 4.0)
                shock_direction = 1 if scenario == 'bull' else -1 if scenario in ['bear', 'stress'] else random.choice([-1, 1])
                extreme_shock = shock_direction * shock_magnitude * current_vol
            else:
                extreme_shock = 0
            
            # Combine all factors
            base_return = monthly_return * regime_adj['return_mult']
            noise = random.gauss(0, current_vol * regime_adj['vol_mult'])
            
            total_return = (base_return + cycle_effect + seasonal + momentum + 
                          noise + extreme_shock * params['corrections'])
            
            # Apply bounds to prevent unrealistic values
            total_return = max(-0.25, min(0.25, total_return))  # Cap monthly moves
            
            new_value = data[i-1] * (1 + total_return)
            new_value = max(15, min(800, new_value))  # Reasonable value bounds
            
            data.append(round(new_value, 2))
        
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
            
            # Simplified prompt for faster generation
            prompt = f"""Generate 4 market events for {thesis.title} over {time_horizon} years.
            
Scenario: {scenario}
Signals: {', '.join(signals_list[:3])}

JSON format: [{{"month": 6, "title": "Event Title", "description": "Brief description", "impact_type": "positive", "notification_triggered": true, "signals_affected": ["Signal Name"]}}]"""
            
            messages = [{"role": "user", "content": prompt}]
            
            # Try with shorter timeout
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Event generation timeout")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(15)  # 15 second timeout
            
            try:
                response = self.ai_service.generate_completion(messages, temperature=1.0, max_tokens=800)
                signal.alarm(0)
                
                # Parse response
                response_cleaned = response.strip()
                if '```' in response_cleaned:
                    start = response_cleaned.find('[')
                    end = response_cleaned.rfind(']') + 1
                    if start != -1 and end > start:
                        response_cleaned = response_cleaned[start:end]
                
                events_data = json.loads(response_cleaned.strip())
                
                if isinstance(events_data, list):
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
                    
                    return formatted_events[:6]
                    
            except (TimeoutError, json.JSONDecodeError, Exception) as e:
                signal.alarm(0)
                print(f"AI event generation failed, using intelligent fallback: {e}")
                
        except Exception as e:
            print(f"Event generation setup failed: {e}")
        
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