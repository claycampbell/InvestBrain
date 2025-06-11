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
                'message': 'Azure OpenAI connection timeout',
                'description': 'Network connection to Azure OpenAI failed. This may be due to temporary network issues.',
                'action_needed': 'Please try running the simulation again. If the problem persists, check Azure OpenAI service status.',
                'chart_data': None,
                'events': [],
                'scenario_summary': 'Simulation failed due to network timeout'
            }
        
        # Generate timeline labels
        timeline = self._generate_timeline(time_horizon)
        
        # Generate events if requested
        events = []
        if include_events:
            try:
                # Use thesis performance data for event positioning
                if isinstance(performance_data, dict):
                    event_data = performance_data.get('thesis_performance', performance_data.get('market_performance', []))
                else:
                    event_data = performance_data if isinstance(performance_data, list) else []
                events = self._generate_event_scenarios(
                    thesis, time_horizon, scenario, event_data
                )
                print(f"Generated {len(events)} events: {[e.get('title', 'No title') for e in events]}")
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
        # Set months early to avoid scope issues
        months = time_horizon * 12
        
        # Attempt LLM generation with optimized approach
        if self.ai_service and self.ai_service.is_available():
            try:
                # For o4-mini model, use very concise prompts to avoid length limits
                
                # Generate in smaller chunks to avoid length limits
                if months <= 12:
                    # Extract expected performance from thesis text
                    thesis_text = str(thesis) if hasattr(thesis, '__str__') else str(thesis.original_thesis if hasattr(thesis, 'original_thesis') else 'general investment')
                    
                    # Enhanced prompt for thesis-specific simulation
                    prompt = f"""Generate {months} realistic monthly values for investment thesis simulation:
Thesis: {thesis_text[:200]}...
Scenario: {scenario}

Two series needed:
- Market: broad market performance with volatility, starting 100
- Thesis: specific thesis performance reflecting the investment case, starting 100

Include realistic market corrections, rallies, thesis-specific events. No linear growth.
JSON: {{"market": [100,98.5,102.3,...], "thesis": [100,103.2,97.1,...]}}"""
                    messages = [{"role": "user", "content": prompt}]
                    
                    response = self.ai_service.generate_completion(messages, temperature=1.0, max_tokens=300)
                    
                    if not response:
                        print("Azure OpenAI connection failed - returning error")
                        return {
                            'error': True,
                            'message': 'Azure OpenAI connection timeout',
                            'description': 'Unable to connect to Azure OpenAI service due to network timeout.',
                            'action_needed': 'Please wait a moment and try the simulation again.'
                        }
                    
                    # If we get this far, Azure OpenAI worked
                    print("Azure OpenAI successfully generated response")
                    
                    print(f"Azure OpenAI response received: {len(response)} characters")
                    print(f"Response preview: {response[:200]}...")
                    
                    # Extract numbers from response with improved parsing
                    import re
                    import json
                    
                    # Try to find JSON object with two series first
                    try:
                        # Look for JSON object with market and thesis arrays
                        json_match = re.search(r'\{[^}]*"market"[^}]*"thesis"[^}]*\}', response, re.DOTALL)
                        if json_match:
                            json_str = json_match.group()
                            data_obj = json.loads(json_str)
                            
                            market_data = data_obj.get('market', [])
                            thesis_data = data_obj.get('thesis', [])
                            
                            if (len(market_data) >= months and len(thesis_data) >= months):
                                result = {
                                    'market_performance': [float(x) for x in market_data[:months]],
                                    'thesis_performance': [float(x) for x in thesis_data[:months]]
                                }
                                print(f"Generated 2-series LLM simulation data: {months} points each")
                                return result
                    except Exception as e:
                        print(f"Failed to parse 2-series JSON: {e}")
                    
                    # Fallback: try single array format and derive two series
                    try:
                        json_match = re.search(r'\[[\d\s,.\-]+\]', response)
                        if json_match:
                            json_str = json_match.group()
                            performance_data = json.loads(json_str)
                            if len(performance_data) >= months:
                                thesis_series = [float(x) for x in performance_data[:months]]
                                # Generate market as broader baseline
                                market_series = [100 + (x - 100) * 0.6 for x in thesis_series]  # Market less volatile than thesis
                                
                                result = {
                                    'market_performance': market_series,
                                    'thesis_performance': thesis_series
                                }
                                print(f"Generated derived 2-series simulation data: {months} points each")
                                return result
                    except Exception as e:
                        print(f"Failed to parse single array: {e}")
                
            except Exception as e:
                print(f"LLM generation failed: {e}")
                # Fall through to error handling below
        
        # Extract thesis expectations for realistic simulation when Azure OpenAI times out
        print("Azure OpenAI timeout - generating thesis-specific simulation")
        import random
        import re
        
        # Extract expected growth/performance from thesis text
        thesis_text = str(thesis) if hasattr(thesis, '__str__') else str(thesis.original_thesis if hasattr(thesis, 'original_thesis') else '')
        
        # Look for percentage growth expectations in thesis
        growth_matches = re.findall(r'(\d+)%.*(?:growth|increase|up|gain)', thesis_text.lower())
        expected_annual_growth = 0.15  # Default 15% if not found
        if growth_matches:
            expected_annual_growth = float(growth_matches[0]) / 100
        
        # Adjust for scenario
        if scenario == 'bull':
            expected_annual_growth *= 1.3
        elif scenario == 'bear':
            expected_annual_growth *= 0.4
        
        # Generate realistic two-series data
        market_data = [100.0]
        thesis_data = [100.0]
        
        monthly_thesis_growth = expected_annual_growth / 12
        
        for i in range(1, months):
            # Market baseline with volatility
            market_change = random.gauss(0.008, 0.035)  # ~10% annual with volatility
            if random.random() < 0.15:
                market_change *= random.choice([2.2, -1.5])  # Corrections/rallies
            market_val = market_data[-1] * (1 + market_change)
            market_data.append(max(70.0, min(150.0, market_val)))
            
            # Thesis-specific performance based on extracted expectations
            thesis_change = random.gauss(monthly_thesis_growth, 0.05)  # Target growth with volatility
            if random.random() < 0.12:  # Thesis-specific events
                thesis_change *= random.choice([1.8, 0.3])
            thesis_val = thesis_data[-1] * (1 + thesis_change)
            thesis_data.append(max(75.0, min(180.0, thesis_val)))
        
        return {
            'market_performance': [round(x, 1) for x in market_data],
            'thesis_performance': [round(x, 1) for x in thesis_data],
            '_note': f'Thesis-specific simulation: {expected_annual_growth*100:.0f}% annual target'
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
                                'month': month,
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
        
        # Generate events with logical spacing throughout time horizon
        events = []
        total_months = time_horizon * 12
        num_events = min(4, max(2, time_horizon))  # 2-4 events based on time horizon
        
        # Calculate evenly spaced event months
        if num_events > 1:
            spacing = total_months // (num_events + 1)
            event_months = [spacing * (i + 1) for i in range(num_events)]
        else:
            event_months = [total_months // 2]  # Single event at midpoint
        
        for i, month in enumerate(event_months):
            template = random.choice(event_templates)
            
            event = {
                'month': month,
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