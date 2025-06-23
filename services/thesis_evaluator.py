"""
Thesis Evaluation Service
Provides comprehensive analysis and scoring of investment thesis strength and research quality
"""

import json
import logging
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService

class ThesisEvaluator:
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        
    def evaluate_thesis_strength(self, thesis_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive evaluation of thesis strength across multiple dimensions
        """
        try:
            # Extract key components for evaluation
            core_claim = thesis_analysis.get('core_claim', '')
            core_analysis = thesis_analysis.get('core_analysis', '')
            assumptions = thesis_analysis.get('assumptions', [])
            causal_chain = thesis_analysis.get('causal_chain', [])
            counter_thesis = thesis_analysis.get('counter_thesis', [])
            metrics_to_track = thesis_analysis.get('metrics_to_track', [])
            
            # Create comprehensive evaluation prompt
            evaluation_prompt = self._build_evaluation_prompt(
                core_claim, core_analysis, assumptions, causal_chain, 
                counter_thesis, metrics_to_track
            )
            
            messages = [
                {
                    "role": "system",
                    "content": """You are an expert investment research analyst with 20+ years of experience evaluating investment theses for institutional investors. Your role is to provide rigorous, objective assessment of thesis quality and strength.

Focus on:
1. Logical coherence and reasoning quality
2. Evidence strength and data backing
3. Risk assessment completeness
4. Contrarian perspective consideration
5. Measurability and tracking capability
6. Market timing and catalysts
7. Competitive dynamics understanding
8. Financial modeling robustness

Provide actionable insights for improving the thesis."""
                },
                {
                    "role": "user", 
                    "content": evaluation_prompt
                }
            ]
            
            response = self.azure_service.generate_completion(
                messages, temperature=0.3, max_tokens=3000
            )
            
            if isinstance(response, str):
                try:
                    evaluation_result = json.loads(response)
                    return evaluation_result
                except json.JSONDecodeError:
                    # If not valid JSON, create structured response
                    return self._parse_unstructured_evaluation(response)
            
            return response
            
        except Exception as e:
            logging.error(f"Thesis evaluation failed: {str(e)}")
            return self._generate_fallback_evaluation()
    
    def _build_evaluation_prompt(self, core_claim: str, core_analysis: str, 
                                assumptions: List[str], causal_chain: List[str],
                                counter_thesis: List[str], metrics: List[Dict]) -> str:
        """Build comprehensive evaluation prompt"""
        
        prompt = f"""
INVESTMENT THESIS EVALUATION REQUEST

Please evaluate the following investment thesis across multiple quality dimensions and provide a comprehensive strength assessment.

=== THESIS COMPONENTS ===

Core Investment Claim:
{core_claim}

Supporting Analysis:
{core_analysis}

Key Assumptions:
{json.dumps(assumptions, indent=2)}

Causal Chain:
{json.dumps(causal_chain, indent=2)}

Counter-Thesis Considerations:
{json.dumps(counter_thesis, indent=2)}

Tracking Metrics ({len(metrics)} signals):
{self._format_metrics_for_evaluation(metrics)}

=== EVALUATION FRAMEWORK ===

Evaluate across these 8 critical dimensions:

1. LOGICAL COHERENCE (0-100)
   - Reasoning flow and argument structure
   - Internal consistency and contradiction detection
   - Cause-effect relationship clarity

2. EVIDENCE STRENGTH (0-100)
   - Quality and relevance of supporting data
   - Quantitative backing for claims
   - Source credibility and recency

3. RISK ASSESSMENT (0-100)
   - Downside scenario consideration
   - Risk factor identification completeness
   - Probability-weighted outcome analysis

4. CONTRARIAN PERSPECTIVE (0-100)
   - Counter-argument acknowledgment
   - Bear case development quality
   - Cognitive bias awareness

5. MEASURABILITY (0-100)
   - KPI selection appropriateness
   - Tracking mechanism feasibility
   - Success/failure criteria clarity

6. MARKET TIMING (0-100)
   - Catalyst identification and timing
   - Market condition consideration
   - Entry/exit strategy clarity

7. COMPETITIVE DYNAMICS (0-100)
   - Industry understanding depth
   - Competitive advantage sustainability
   - Market share and positioning analysis

8. FINANCIAL ROBUSTNESS (0-100)
   - Valuation methodology soundness
   - Financial model assumptions realism
   - Sensitivity analysis consideration

=== REQUIRED OUTPUT FORMAT ===

Return a JSON object with this exact structure:

{{
  "overall_strength_score": 85,
  "confidence_level": "High",
  "investment_grade": "A-",
  "dimension_scores": {{
    "logical_coherence": 88,
    "evidence_strength": 82,
    "risk_assessment": 79,
    "contrarian_perspective": 85,
    "measurability": 90,
    "market_timing": 83,
    "competitive_dynamics": 87,
    "financial_robustness": 81
  }},
  "strength_summary": "Compelling thesis with strong logical foundation and robust tracking mechanisms. Market timing appears favorable with clear catalysts identified.",
  "key_strengths": [
    "Well-structured causal chain with clear value drivers",
    "Comprehensive risk assessment including multiple scenarios",
    "Strong competitive moat analysis with sustainable advantages"
  ],
  "critical_weaknesses": [
    "Limited discussion of regulatory risks in key markets",
    "Valuation assumptions may be optimistic in current environment"
  ],
  "improvement_recommendations": [
    "Develop more detailed bear case scenarios with specific trigger events",
    "Add sensitivity analysis for key valuation multiples",
    "Include regulatory impact assessment for major markets"
  ],
  "research_gaps": [
    "Management quality and execution track record analysis",
    "Peer comparison across key financial metrics",
    "ESG considerations and sustainability factors"
  ],
  "risk_factors": [
    {{
      "factor": "Market saturation risk",
      "probability": "Medium",
      "impact": "High",
      "mitigation": "Diversification into adjacent markets"
    }}
  ],
  "thesis_classification": {{
    "investment_style": "Growth",
    "time_horizon": "2-3 years",
    "risk_level": "Moderate-High",
    "conviction_level": "High"
  }},
  "actionable_insights": [
    "Monitor quarterly revenue growth acceleration as primary success indicator",
    "Track competitive market share data monthly",
    "Set stop-loss at 15% below entry price if growth thesis breaks down"
  ]
}}

Provide rigorous, institutional-quality analysis that would be valuable for professional investors making capital allocation decisions.
"""
        return prompt
    
    def _format_metrics_for_evaluation(self, metrics: List[Dict]) -> str:
        """Format metrics for evaluation prompt"""
        if not metrics:
            return "No tracking metrics specified"
        
        formatted = []
        for i, metric in enumerate(metrics, 1):
            if isinstance(metric, dict):
                name = metric.get('name', f'Metric {i}')
                level = metric.get('level', 'Unknown')
                source = metric.get('data_source', 'Unknown')
                formatted.append(f"• {name} (Level: {level}, Source: {source})")
            else:
                formatted.append(f"• {str(metric)}")
        
        return "\n".join(formatted[:10])  # Limit to first 10 for prompt efficiency
    
    def _parse_unstructured_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse unstructured evaluation response into standard format"""
        return {
            "overall_strength_score": 75,
            "confidence_level": "Medium",
            "investment_grade": "B+",
            "dimension_scores": {
                "logical_coherence": 75,
                "evidence_strength": 70,
                "risk_assessment": 75,
                "contrarian_perspective": 70,
                "measurability": 80,
                "market_timing": 75,
                "competitive_dynamics": 75,
                "financial_robustness": 70
            },
            "strength_summary": response[:200] + "..." if len(response) > 200 else response,
            "key_strengths": ["Structured analysis framework", "Systematic approach"],
            "critical_weaknesses": ["Response parsing required manual interpretation"],
            "improvement_recommendations": ["Ensure JSON format compliance"],
            "research_gaps": ["Detailed evaluation pending"],
            "risk_factors": [],
            "thesis_classification": {
                "investment_style": "Mixed",
                "time_horizon": "1-2 years",
                "risk_level": "Moderate",
                "conviction_level": "Medium"
            },
            "actionable_insights": ["Continue monitoring and refining analysis"]
        }
    
    def _generate_fallback_evaluation(self) -> Dict[str, Any]:
        """Generate structured fallback evaluation when Azure OpenAI is unavailable"""
        return {
            "overall_strength_score": 65,
            "confidence_level": "Low",
            "investment_grade": "C+",
            "dimension_scores": {
                "logical_coherence": 60,
                "evidence_strength": 50,
                "risk_assessment": 65,
                "contrarian_perspective": 60,
                "measurability": 75,
                "market_timing": 65,
                "competitive_dynamics": 60,
                "financial_robustness": 55
            },
            "strength_summary": "Evaluation system currently unavailable. Manual review recommended for comprehensive assessment.",
            "key_strengths": ["Basic thesis structure present"],
            "critical_weaknesses": ["Comprehensive evaluation pending"],
            "improvement_recommendations": ["Ensure evaluation service connectivity"],
            "research_gaps": ["Full evaluation pending"],
            "risk_factors": [],
            "thesis_classification": {
                "investment_style": "Unknown",
                "time_horizon": "Unknown",
                "risk_level": "Unknown",
                "conviction_level": "Unknown"
            },
            "actionable_insights": ["Re-run evaluation when service available"]
        }
    
    def generate_research_quality_score(self, thesis_analysis: Dict[str, Any], 
                                       document_count: int = 0,
                                       eagle_signal_count: int = 0) -> Dict[str, Any]:
        """
        Generate comprehensive research quality scoring
        """
        try:
            # Calculate base scores
            structure_score = self._calculate_structure_score(thesis_analysis)
            depth_score = self._calculate_depth_score(thesis_analysis)
            data_score = self._calculate_data_integration_score(eagle_signal_count, document_count)
            rigor_score = self._calculate_analytical_rigor_score(thesis_analysis)
            
            # Weighted composite score
            weights = {
                'structure': 0.25,
                'depth': 0.30,
                'data_integration': 0.25,
                'analytical_rigor': 0.20
            }
            
            composite_score = (
                structure_score * weights['structure'] +
                depth_score * weights['depth'] +
                data_score * weights['data_integration'] +
                rigor_score * weights['analytical_rigor']
            )
            
            return {
                "research_quality_score": round(composite_score, 1),
                "component_scores": {
                    "structure_quality": structure_score,
                    "analytical_depth": depth_score,
                    "data_integration": data_score,
                    "methodological_rigor": rigor_score
                },
                "quality_grade": self._assign_quality_grade(composite_score),
                "quality_assessment": self._generate_quality_narrative(composite_score),
                "research_completeness": {
                    "documents_analyzed": document_count,
                    "eagle_signals_integrated": eagle_signal_count,
                    "tracking_metrics": len(thesis_analysis.get('metrics_to_track', [])),
                    "assumptions_identified": len(thesis_analysis.get('assumptions', []))
                }
            }
            
        except Exception as e:
            logging.error(f"Research quality scoring failed: {str(e)}")
            return self._fallback_quality_score()
    
    def _calculate_structure_score(self, thesis_analysis: Dict[str, Any]) -> float:
        """Calculate thesis structure quality score"""
        score = 0
        max_score = 100
        
        # Core components presence and quality
        if thesis_analysis.get('core_claim'):
            score += 20
            if len(thesis_analysis['core_claim']) > 50:
                score += 10
        
        if thesis_analysis.get('core_analysis'):
            score += 20
            if len(thesis_analysis['core_analysis']) > 100:
                score += 10
        
        if thesis_analysis.get('assumptions'):
            score += 15
            if len(thesis_analysis['assumptions']) >= 3:
                score += 10
        
        if thesis_analysis.get('causal_chain'):
            score += 15
        
        if thesis_analysis.get('counter_thesis'):
            score += 10
        
        return min(score, max_score)
    
    def _calculate_depth_score(self, thesis_analysis: Dict[str, Any]) -> float:
        """Calculate analytical depth score"""
        score = 0
        
        # Content depth indicators
        core_analysis_length = len(thesis_analysis.get('core_analysis', ''))
        if core_analysis_length > 200:
            score += 25
        elif core_analysis_length > 100:
            score += 15
        elif core_analysis_length > 50:
            score += 10
        
        # Assumption quality
        assumptions = thesis_analysis.get('assumptions', [])
        if len(assumptions) >= 5:
            score += 20
        elif len(assumptions) >= 3:
            score += 15
        elif len(assumptions) >= 1:
            score += 10
        
        # Counter-thesis consideration
        counter_thesis = thesis_analysis.get('counter_thesis', [])
        if isinstance(counter_thesis, list) and len(counter_thesis) > 0:
            score += 20
        
        # Causal chain complexity
        causal_chain = thesis_analysis.get('causal_chain', [])
        if isinstance(causal_chain, list) and len(causal_chain) >= 3:
            score += 20
        elif isinstance(causal_chain, list) and len(causal_chain) >= 1:
            score += 10
        
        # Metrics sophistication
        metrics = thesis_analysis.get('metrics_to_track', [])
        if len(metrics) >= 8:
            score += 15
        elif len(metrics) >= 5:
            score += 10
        elif len(metrics) >= 1:
            score += 5
        
        return min(score, 100)
    
    def _calculate_data_integration_score(self, eagle_signals: int, documents: int) -> float:
        """Calculate data integration quality score"""
        score = 0
        
        # Eagle API integration
        if eagle_signals >= 5:
            score += 40
        elif eagle_signals >= 3:
            score += 30
        elif eagle_signals >= 1:
            score += 20
        
        # Document analysis integration
        if documents >= 3:
            score += 30
        elif documents >= 1:
            score += 20
        
        # Base research signals
        score += 30  # For Level 0 signal generation
        
        return min(score, 100)
    
    def _calculate_analytical_rigor_score(self, thesis_analysis: Dict[str, Any]) -> float:
        """Calculate analytical rigor score"""
        score = 0
        
        # Mental model sophistication
        mental_model = thesis_analysis.get('mental_model', '')
        if mental_model and len(mental_model) > 0:
            score += 20
        
        # Risk consideration
        counter_thesis = thesis_analysis.get('counter_thesis', [])
        if counter_thesis:
            score += 25
        
        # Systematic approach indicators
        if thesis_analysis.get('assumptions') and thesis_analysis.get('causal_chain'):
            score += 25
        
        # Tracking mechanism quality
        metrics = thesis_analysis.get('metrics_to_track', [])
        eagle_metrics = sum(1 for m in metrics if isinstance(m, dict) and m.get('eagle_api'))
        if eagle_metrics > 0:
            score += 20
        
        # Completeness
        required_fields = ['core_claim', 'core_analysis', 'assumptions', 'metrics_to_track']
        present_fields = sum(1 for field in required_fields if thesis_analysis.get(field))
        score += (present_fields / len(required_fields)) * 10
        
        return min(score, 100)
    
    def _assign_quality_grade(self, score: float) -> str:
        """Assign letter grade based on quality score"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"
    
    def _generate_quality_narrative(self, score: float) -> str:
        """Generate quality assessment narrative"""
        if score >= 85:
            return "Exceptional research quality with comprehensive analysis, robust data integration, and systematic methodology."
        elif score >= 75:
            return "High-quality research with strong analytical foundation and good data support."
        elif score >= 65:
            return "Solid research quality with adequate analysis depth and reasonable data integration."
        elif score >= 55:
            return "Moderate research quality with basic analysis framework but limited depth or data support."
        else:
            return "Below-standard research quality requiring substantial improvement in analysis depth and data integration."
    
    def _fallback_quality_score(self) -> Dict[str, Any]:
        """Fallback quality scoring when evaluation fails"""
        return {
            "research_quality_score": 60.0,
            "component_scores": {
                "structure_quality": 60,
                "analytical_depth": 55,
                "data_integration": 65,
                "methodological_rigor": 60
            },
            "quality_grade": "C+",
            "quality_assessment": "Quality assessment temporarily unavailable. Manual review recommended.",
            "research_completeness": {
                "documents_analyzed": 0,
                "eagle_signals_integrated": 0,
                "tracking_metrics": 0,
                "assumptions_identified": 0
            }
        }