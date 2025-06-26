"""
Significance Mapping Service
Creates visual connections between research elements and signal patterns
"""

import json
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService

class SignificanceMappingService:
    def __init__(self):
        self.ai_service = AzureOpenAIService()
    
    def generate_significance_map(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a visual mapping showing connections between research elements and signal patterns
        """
        try:
            # Extract research elements and signals
            research_elements = self._extract_research_elements(thesis_analysis)
            signal_patterns = self._extract_signal_patterns(thesis_analysis)
            
            # Generate AI-powered connections
            connections = self._generate_connections(research_elements, signal_patterns, thesis_analysis)
            
            # Calculate connection strength scores
            connection_scores = self._calculate_connection_scores(connections)
            
            # Create visualization data structure
            mapping_data = {
                'research_nodes': research_elements,
                'signal_nodes': signal_patterns,
                'connections': connections,
                'connection_scores': connection_scores,
                'metadata': {
                    'total_connections': len(connections),
                    'strong_connections': len([c for c in connections if c.get('strength', 0) > 0.7]),
                    'research_coverage': len(research_elements),
                    'signal_coverage': len(signal_patterns)
                }
            }
            
            return mapping_data
            
        except Exception as e:
            return self._fallback_mapping()
    
    def _extract_research_elements(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key research components from thesis analysis"""
        elements = []
        
        # Core claim
        if thesis_analysis.get('core_claim'):
            elements.append({
                'id': 'core_claim',
                'type': 'research',
                'category': 'thesis_foundation',
                'title': 'Core Investment Claim',
                'content': thesis_analysis['core_claim'][:200] + '...' if len(thesis_analysis['core_claim']) > 200 else thesis_analysis['core_claim'],
                'importance_score': 0.95
            })
        
        # Key assumptions
        assumptions = thesis_analysis.get('assumptions', [])
        if isinstance(assumptions, list):
            for i, assumption in enumerate(assumptions[:5]):
                elements.append({
                    'id': f'assumption_{i}',
                    'type': 'research',
                    'category': 'key_assumption',
                    'title': f'Key Assumption {i+1}',
                    'content': assumption[:150] + '...' if len(assumption) > 150 else assumption,
                    'importance_score': 0.8 - (i * 0.1)
                })
        
        # Mental model
        if thesis_analysis.get('mental_model'):
            elements.append({
                'id': 'mental_model',
                'type': 'research',
                'category': 'analytical_framework',
                'title': 'Analytical Framework',
                'content': thesis_analysis['mental_model'],
                'importance_score': 0.85
            })
        
        # Core analysis insights
        if thesis_analysis.get('core_analysis'):
            elements.append({
                'id': 'core_analysis',
                'type': 'research',
                'category': 'analytical_depth',
                'title': 'Core Analysis',
                'content': thesis_analysis['core_analysis'][:200] + '...' if len(thesis_analysis['core_analysis']) > 200 else thesis_analysis['core_analysis'],
                'importance_score': 0.9
            })
        
        return elements
    
    def _extract_signal_patterns(self, thesis_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract signal patterns from monitoring data"""
        signals = []
        
        # Extract from metrics_to_track
        metrics = thesis_analysis.get('metrics_to_track', [])
        if isinstance(metrics, list):
            for i, metric in enumerate(metrics[:8]):
                signals.append({
                    'id': f'signal_{i}',
                    'type': 'signal',
                    'category': 'tracking_metric',
                    'title': metric.get('name', f'Signal {i+1}') if isinstance(metric, dict) else str(metric),
                    'signal_type': metric.get('type', 'quantitative') if isinstance(metric, dict) else 'quantitative',
                    'confidence_score': 0.8 - (i * 0.05),
                    'predictive_value': 0.75 + (i % 3) * 0.05
                })
        
        # Extract from monitoring plan
        monitoring_plan = thesis_analysis.get('monitoring_plan', [])
        if isinstance(monitoring_plan, list):
            for i, plan_item in enumerate(monitoring_plan[:5]):
                signals.append({
                    'id': f'monitor_{i}',
                    'type': 'signal',
                    'category': 'monitoring_signal',
                    'title': plan_item.get('signal', f'Monitor {i+1}') if isinstance(plan_item, dict) else str(plan_item),
                    'signal_type': 'qualitative',
                    'confidence_score': 0.7 + (i % 2) * 0.1,
                    'predictive_value': 0.65 + (i % 4) * 0.05
                })
        
        return signals
    
    def _generate_connections(self, research_elements: List[Dict], signal_patterns: List[Dict], thesis_analysis: Dict) -> List[Dict[str, Any]]:
        """Use AI to identify logical connections between research and signals"""
        try:
            prompt = f"""
            Analyze the logical connections between research elements and signal patterns in this investment thesis.
            
            Research Elements:
            {json.dumps([{'id': r['id'], 'title': r['title'], 'content': r['content']} for r in research_elements], indent=2)}
            
            Signal Patterns:
            {json.dumps([{'id': s['id'], 'title': s['title'], 'type': s['signal_type']} for s in signal_patterns], indent=2)}
            
            For each meaningful connection, provide:
            1. Which research element connects to which signal
            2. The logical relationship type (validates, measures, indicates, contradicts)
            3. Connection strength (0.0-1.0)
            4. Brief explanation of the connection
            
            Respond with JSON array of connections:
            [{{
                "research_id": "string",
                "signal_id": "string", 
                "relationship_type": "validates|measures|indicates|contradicts",
                "strength": 0.0-1.0,
                "explanation": "brief explanation"
            }}]
            """
            
            response = self.ai_service.generate_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            connections_data = json.loads(response)
            return connections_data if isinstance(connections_data, list) else []
            
        except Exception:
            return self._generate_fallback_connections(research_elements, signal_patterns)
    
    def _generate_fallback_connections(self, research_elements: List[Dict], signal_patterns: List[Dict]) -> List[Dict]:
        """Generate logical connections using pattern matching"""
        connections = []
        
        for research in research_elements:
            for signal in signal_patterns:
                # Create connections based on category matching
                strength = 0.0
                relationship = "indicates"
                
                if research['category'] == 'thesis_foundation' and signal['category'] == 'tracking_metric':
                    strength = 0.8
                    relationship = "validates"
                elif research['category'] == 'key_assumption' and signal['category'] == 'monitoring_signal':
                    strength = 0.7
                    relationship = "measures"
                elif research['category'] == 'analytical_framework':
                    strength = 0.6
                    relationship = "indicates"
                
                if strength > 0.5:
                    connections.append({
                        'research_id': research['id'],
                        'signal_id': signal['id'],
                        'relationship_type': relationship,
                        'strength': strength,
                        'explanation': f"{research['title']} {relationship} {signal['title']}"
                    })
        
        return connections
    
    def _calculate_connection_scores(self, connections: List[Dict]) -> Dict[str, float]:
        """Calculate overall connection strength metrics"""
        if not connections:
            return {'average_strength': 0.0, 'max_strength': 0.0, 'connection_density': 0.0}
        
        strengths = [c.get('strength', 0.0) for c in connections]
        
        return {
            'average_strength': sum(strengths) / len(strengths),
            'max_strength': max(strengths),
            'connection_density': len([s for s in strengths if s > 0.7]) / len(strengths)
        }
    
    def _fallback_mapping(self) -> Dict[str, Any]:
        """Fallback mapping structure when AI analysis fails"""
        return {
            'research_nodes': [],
            'signal_nodes': [],
            'connections': [],
            'connection_scores': {'average_strength': 0.0, 'max_strength': 0.0, 'connection_density': 0.0},
            'metadata': {
                'total_connections': 0,
                'strong_connections': 0,
                'research_coverage': 0,
                'signal_coverage': 0,
                'status': 'fallback_mode'
            }
        }
    
    def get_connection_insights(self, mapping_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights about the research-signal connections"""
        connections = mapping_data.get('connections', [])
        scores = mapping_data.get('connection_scores', {})
        
        # Analyze connection patterns
        strong_connections = [c for c in connections if c.get('strength', 0) > 0.7]
        validation_connections = [c for c in connections if c.get('relationship_type') == 'validates']
        measurement_connections = [c for c in connections if c.get('relationship_type') == 'measures']
        
        insights = {
            'connection_quality': 'high' if scores.get('average_strength', 0) > 0.7 else 'moderate' if scores.get('average_strength', 0) > 0.5 else 'low',
            'research_signal_alignment': len(strong_connections) / max(len(connections), 1),
            'validation_coverage': len(validation_connections),
            'measurement_coverage': len(measurement_connections),
            'key_findings': []
        }
        
        # Generate key findings
        if scores.get('connection_density', 0) > 0.6:
            insights['key_findings'].append("Strong alignment between research depth and signal reliability")
        if len(validation_connections) > 3:
            insights['key_findings'].append("Multiple research elements have direct signal validation")
        if scores.get('average_strength', 0) < 0.5:
            insights['key_findings'].append("Research elements may need stronger signal support")
        
        return insights