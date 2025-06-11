import json
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from services.azure_openai_service import AzureOpenAIService

class SimulationService:
    """
    AI-powered simulation service for thesis testing with time horizon forecasts and event scenarios
    """
    
    def __init__(self):
        self.azure_openai = AzureOpenAIService()
        
    def run_time_horizon_forecast(self, thesis, time_horizon: str, scenario_type: str) -> Dict[str, Any]:
        """
        Generate time horizon forecast using AI analysis of thesis and market conditions
        """
        try:
            # Prepare thesis context
            thesis_context = self._prepare_thesis_context(thesis)
            
            # Generate forecast using Azure OpenAI
            forecast_prompt = self._build_forecast_prompt(thesis_context, time_horizon, scenario_type)
            
            messages = [
                {"role": "system", "content": self._get_forecast_system_prompt()},
                {"role": "user", "content": forecast_prompt}
            ]
            
            response = self.azure_openai.generate_completion(messages, temperature=0.7)
            
            # Parse AI response
            forecast_data = json.loads(response)
            
            # Generate signal forecasts
            signal_forecasts = self._generate_signal_forecasts(thesis, time_horizon, scenario_type)
            
            # Check for alert triggers
            alert_triggers = self._check_alert_triggers(thesis, forecast_data, signal_forecasts)
            
            return {
                'forecast': forecast_data,
                'performance_metrics': forecast_data.get('performance_metrics', {}),
                'signal_forecasts': signal_forecasts,
                'alert_triggers': alert_triggers,
                'simulation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in time horizon forecast: {str(e)}")
            raise
    
    def run_event_simulation(self, thesis, event_type: str, event_severity: str) -> Dict[str, Any]:
        """
        Simulate real-world events and their impact on thesis performance
        """
        try:
            # Prepare thesis context
            thesis_context = self._prepare_thesis_context(thesis)
            
            # Generate event simulation using Azure OpenAI
            event_prompt = self._build_event_prompt(thesis_context, event_type, event_severity)
            
            messages = [
                {"role": "system", "content": self._get_event_system_prompt()},
                {"role": "user", "content": event_prompt}
            ]
            
            response = self.azure_openai.generate_completion(messages, temperature=0.8)
            
            # Parse AI response
            event_data = json.loads(response)
            
            # Generate signal responses
            signal_responses = self._generate_signal_responses(thesis, event_data)
            
            # Check for alert triggers
            alert_triggers = self._check_event_alert_triggers(thesis, event_data, signal_responses)
            
            return {
                'event_simulation': event_data,
                'impact_analysis': event_data.get('impact_analysis', {}),
                'signal_responses': signal_responses,
                'alert_triggers': alert_triggers,
                'simulation_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error in event simulation: {str(e)}")
            raise
    
    def _prepare_thesis_context(self, thesis) -> Dict[str, Any]:
        """Prepare thesis data for simulation prompts"""
        return {
            'title': thesis.title,
            'core_claim': thesis.core_claim,
            'core_analysis': thesis.core_analysis,
            'mental_model': thesis.mental_model,
            'causal_chain': thesis.causal_chain if isinstance(thesis.causal_chain, list) else [],
            'assumptions': thesis.assumptions if isinstance(thesis.assumptions, list) else [],
            'counter_thesis': thesis.counter_thesis if isinstance(thesis.counter_thesis, list) else [],
            'metrics_to_track': thesis.metrics_to_track if isinstance(thesis.metrics_to_track, list) else [],
            'monitoring_plan': thesis.monitoring_plan if isinstance(thesis.monitoring_plan, dict) else {}
        }
    
    def _get_forecast_system_prompt(self) -> str:
        """System prompt for time horizon forecasting"""
        return """You are an expert investment analyst specializing in scenario analysis and forecasting. 

Generate realistic time horizon forecasts based on investment thesis analysis, considering market dynamics, competitive positioning, and macroeconomic factors.

Respond with valid JSON only:
{
  "time_horizon": "forecast period",
  "scenario_type": "bull|base|bear|black_swan",
  "confidence": 85,
  "key_outcomes": [
    "Specific outcome 1",
    "Specific outcome 2"
  ],
  "performance_metrics": {
    "expected_return": 25.5,
    "risk_level": "medium",
    "key_risks": [
      "Risk factor 1",
      "Risk factor 2"
    ]
  },
  "market_assumptions": [
    "Market assumption 1",
    "Market assumption 2"
  ],
  "catalyst_timeline": [
    {
      "timeframe": "Q1 2025",
      "event": "Expected catalyst",
      "impact": "Positive|Negative|Neutral"
    }
  ]
}"""
    
    def _get_event_system_prompt(self) -> str:
        """System prompt for event simulation"""
        return """You are an expert risk analyst specializing in event simulation and impact assessment.

Simulate realistic market events and analyze their impact on investment thesis performance, considering both direct and indirect effects.

Respond with valid JSON only:
{
  "event_type": "market|competitive|regulatory|macroeconomic|company_specific",
  "severity": "minor|moderate|major|critical",
  "description": "Detailed event description",
  "probability": 25,
  "impact_analysis": {
    "thesis_impact": -15.5,
    "recovery_time": "6-12 months",
    "permanent_impact": false,
    "mitigation_actions": [
      "Action 1",
      "Action 2"
    ]
  },
  "affected_assumptions": [
    "Assumption that would be challenged"
  ],
  "cascade_effects": [
    {
      "effect": "Secondary impact",
      "probability": 60,
      "timeline": "3-6 months"
    }
  ]
}"""
    
    def _build_forecast_prompt(self, thesis_context: Dict, time_horizon: str, scenario_type: str) -> str:
        """Build prompt for time horizon forecasting"""
        return f"""Analyze this investment thesis and generate a {time_horizon} forecast under {scenario_type} market conditions:

THESIS DETAILS:
Core Claim: {thesis_context.get('core_claim', 'N/A')}
Mental Model: {thesis_context.get('mental_model', 'N/A')}
Key Assumptions: {json.dumps(thesis_context.get('assumptions', []))}

CAUSAL CHAIN:
{json.dumps(thesis_context.get('causal_chain', []))}

MONITORING SIGNALS:
{json.dumps(thesis_context.get('metrics_to_track', []))}

Generate a comprehensive {time_horizon} forecast considering:
1. Market scenario: {scenario_type} conditions
2. Thesis-specific catalysts and risks
3. Competitive dynamics and market evolution
4. Macroeconomic factors
5. Signal performance expectations

Provide specific, quantitative outcomes with confidence levels and actionable insights."""
    
    def _build_event_prompt(self, thesis_context: Dict, event_type: str, event_severity: str) -> str:
        """Build prompt for event simulation"""
        return f"""Simulate a {event_severity} {event_type} event affecting this investment thesis:

THESIS DETAILS:
Core Claim: {thesis_context.get('core_claim', 'N/A')}
Mental Model: {thesis_context.get('mental_model', 'N/A')}
Key Assumptions: {json.dumps(thesis_context.get('assumptions', []))}

COUNTER-THESIS SCENARIOS:
{json.dumps(thesis_context.get('counter_thesis', []))}

MONITORING SIGNALS:
{json.dumps(thesis_context.get('metrics_to_track', []))}

Create a realistic {event_severity} {event_type} event scenario and analyze:
1. Specific event description and probability
2. Direct impact on thesis validity
3. Signal response patterns
4. Recovery timeline and permanent effects
5. Mitigation strategies and actions
6. Cascade effects and secondary impacts

Focus on events that could realistically challenge the thesis assumptions or trigger monitoring alerts."""
    
    def _generate_signal_forecasts(self, thesis, time_horizon: str, scenario_type: str) -> List[Dict[str, Any]]:
        """Generate individual signal performance forecasts"""
        signals = []
        
        if isinstance(thesis.metrics_to_track, list):
            for metric in thesis.metrics_to_track[:6]:  # Limit to top 6 signals
                if isinstance(metric, dict):
                    # Simulate signal direction based on scenario
                    direction = self._predict_signal_direction(metric, scenario_type)
                    confidence = self._calculate_signal_confidence(metric, time_horizon)
                    
                    signals.append({
                        'name': metric.get('name', 'Unknown Signal'),
                        'current_status': 'Active',
                        'direction': direction,
                        'confidence': confidence
                    })
        
        return signals
    
    def _generate_signal_responses(self, thesis, event_data: Dict) -> List[Dict[str, Any]]:
        """Generate signal responses to simulated events"""
        responses = []
        
        if isinstance(thesis.metrics_to_track, list):
            for metric in thesis.metrics_to_track[:6]:  # Limit to top 6 signals
                if isinstance(metric, dict):
                    # Simulate event impact on signal
                    impact = self._calculate_event_impact(metric, event_data)
                    alert_triggered = abs(impact) > 10  # Trigger if >10% impact
                    
                    responses.append({
                        'name': metric.get('name', 'Unknown Signal'),
                        'pre_event': '100',
                        'post_event': f'{100 + impact:.1f}',
                        'impact_pct': impact,
                        'alert_triggered': alert_triggered
                    })
        
        return responses
    
    def _predict_signal_direction(self, metric: Dict, scenario_type: str) -> str:
        """Predict signal direction based on scenario type"""
        if scenario_type == 'bull':
            return 'up'
        elif scenario_type == 'bear':
            return 'down'
        elif scenario_type == 'black_swan':
            return 'down'
        else:  # base case
            return 'stable'
    
    def _calculate_signal_confidence(self, metric: Dict, time_horizon: str) -> int:
        """Calculate confidence in signal forecast"""
        base_confidence = 75
        
        # Adjust based on time horizon
        if time_horizon in ['3m', '6m']:
            return min(90, base_confidence + 10)
        elif time_horizon in ['2y', '3y']:
            return max(50, base_confidence - 15)
        else:  # 1y
            return base_confidence
    
    def _calculate_event_impact(self, metric: Dict, event_data: Dict) -> float:
        """Calculate event impact on individual signals"""
        severity = event_data.get('severity', 'moderate')
        
        # Base impact by severity
        impact_map = {
            'minor': (-5, 5),
            'moderate': (-15, 10),
            'major': (-30, 15),
            'critical': (-50, 20)
        }
        
        # Get impact range and add some randomness
        import random
        min_impact, max_impact = impact_map.get(severity, (-10, 10))
        return random.uniform(min_impact, max_impact)
    
    def _check_alert_triggers(self, thesis, forecast_data: Dict, signal_forecasts: List) -> List[Dict[str, Any]]:
        """Check if forecast triggers any monitoring alerts"""
        alerts = []
        
        # Check confidence threshold
        confidence = forecast_data.get('confidence', 100)
        if confidence < 60:
            alerts.append({
                'signal_name': 'Thesis Confidence',
                'condition': f'Forecast confidence below 60% ({confidence}%)',
                'action': 'Review thesis assumptions and market analysis',
                'severity': 'high'
            })
        
        # Check expected return
        expected_return = forecast_data.get('performance_metrics', {}).get('expected_return', 0)
        if expected_return < -10:
            alerts.append({
                'signal_name': 'Expected Return',
                'condition': f'Negative expected return ({expected_return}%)',
                'action': 'Consider position size reduction or exit strategy',
                'severity': 'critical'
            })
        
        # Check signal directions
        down_signals = [s for s in signal_forecasts if s.get('direction') == 'down']
        if len(down_signals) >= 3:
            alerts.append({
                'signal_name': 'Signal Deterioration',
                'condition': f'{len(down_signals)} signals forecasting negative direction',
                'action': 'Investigate fundamental changes in thesis drivers',
                'severity': 'high'
            })
        
        return alerts
    
    def _check_event_alert_triggers(self, thesis, event_data: Dict, signal_responses: List) -> List[Dict[str, Any]]:
        """Check if event simulation triggers monitoring alerts"""
        alerts = []
        
        # Check thesis impact
        impact = event_data.get('impact_analysis', {}).get('thesis_impact', 0)
        if impact < -20:
            alerts.append({
                'signal_name': 'Thesis Impact',
                'condition': f'Event impact exceeds -20% threshold ({impact}%)',
                'action': 'Emergency thesis review and risk assessment required',
                'severity': 'critical'
            })
        
        # Check signal alerts
        triggered_signals = [s for s in signal_responses if s.get('alert_triggered')]
        if len(triggered_signals) >= 2:
            alerts.append({
                'signal_name': 'Multiple Signal Alerts',
                'condition': f'{len(triggered_signals)} signals triggered alerts',
                'action': 'Implement monitoring plan alert procedures immediately',
                'severity': 'high'
            })
        
        return alerts