"""
Test script to demonstrate the comprehensive thesis evaluation system
Shows how AI-powered analysis evaluates investment research strength across 8 dimensions
"""

import requests
import json
import time

def test_thesis_evaluation():
    """Test the comprehensive thesis evaluation framework"""
    base_url = "http://localhost:5000"
    
    print("=== THESIS EVALUATION SYSTEM TEST ===")
    print("Testing comprehensive investment research strength analysis\n")
    
    # Test thesis creation and evaluation
    test_thesis = "Apple (AAPL) services revenue will drive sustainable growth through ecosystem lock-in and subscription monetization"
    
    print("1. Creating new thesis analysis...")
    create_response = requests.post(f"{base_url}/analyze", data={"thesis_text": test_thesis}, timeout=45)
    
    if create_response.status_code == 200:
        analysis_data = create_response.json()
        thesis_id = analysis_data.get('thesis_id')
        print(f"   ✓ Analysis created (ID: {thesis_id})")
        
        # Test evaluation system
        print("\n2. Running comprehensive strength evaluation...")
        eval_response = requests.get(f"{base_url}/evaluate_thesis/{thesis_id}", timeout=60)
        
        if eval_response.status_code == 200:
            evaluation = eval_response.json()['thesis_evaluation']
            display_evaluation_results(evaluation)
        else:
            print(f"   ✗ Evaluation failed: {eval_response.status_code}")
            print(f"   Response: {eval_response.text[:200]}")
    else:
        print(f"   ✗ Analysis creation failed: {create_response.status_code}")

def display_evaluation_results(evaluation):
    """Display comprehensive evaluation results"""
    strength = evaluation['strength_analysis']
    quality = evaluation['quality_assessment']
    metadata = evaluation['metadata']
    
    print("   ✓ Evaluation completed\n")
    
    print("=== STRENGTH ANALYSIS ===")
    print(f"Overall Score: {strength['overall_strength_score']}/100")
    print(f"Investment Grade: {strength['investment_grade']}")
    print(f"Confidence Level: {strength['confidence_level']}")
    print(f"Summary: {strength['strength_summary'][:100]}...")
    
    print("\n=== 8-DIMENSION BREAKDOWN ===")
    dimensions = strength['dimension_scores']
    for dim, score in dimensions.items():
        bar = "█" * (score // 5) + "░" * (20 - score // 5)
        print(f"{dim.replace('_', ' ').title():20} [{bar}] {score}/100")
    
    print("\n=== RESEARCH QUALITY ===")
    print(f"Quality Score: {quality['research_quality_score']}/100")
    print(f"Quality Grade: {quality['quality_grade']}")
    print(f"Assessment: {quality['quality_assessment'][:80]}...")
    
    print(f"\nResearch Completeness:")
    completeness = quality['research_completeness']
    print(f"  • Documents analyzed: {completeness['documents_analyzed']}")
    print(f"  • Eagle signals: {completeness['eagle_signals_integrated']}")
    print(f"  • Tracking metrics: {completeness['tracking_metrics']}")
    print(f"  • Assumptions: {completeness['assumptions_identified']}")
    
    print("\n=== KEY INSIGHTS ===")
    print("Strengths:")
    for i, strength_item in enumerate(strength['key_strengths'][:3], 1):
        print(f"  {i}. {strength_item}")
    
    print("\nWeaknesses:")
    for i, weakness in enumerate(strength['critical_weaknesses'][:3], 1):
        print(f"  {i}. {weakness}")
    
    print("\nImprovement Recommendations:")
    for i, recommendation in enumerate(strength['improvement_recommendations'][:3], 1):
        print(f"  {i}. {recommendation}")
    
    print("\n=== INVESTMENT CLASSIFICATION ===")
    classification = strength['thesis_classification']
    print(f"Style: {classification['investment_style']}")
    print(f"Time Horizon: {classification['time_horizon']}")
    print(f"Risk Level: {classification['risk_level']}")
    print(f"Conviction: {classification['conviction_level']}")
    
    print("\n=== ACTIONABLE INSIGHTS ===")
    for i, insight in enumerate(strength['actionable_insights'][:3], 1):
        print(f"  {i}. {insight}")
    
    print("\n=== RISK FACTORS ===")
    for risk in strength['risk_factors'][:2]:
        print(f"  • {risk['factor']}")
        print(f"    Probability: {risk['probability']} | Impact: {risk['impact']}")
        print(f"    Mitigation: {risk['mitigation']}")

def test_evaluation_prompting_examples():
    """Show examples of the sophisticated prompting used for evaluation"""
    print("\n=== EVALUATION FRAMEWORK EXAMPLES ===")
    
    print("\nThe evaluation system uses sophisticated prompting to analyze:")
    print("1. LOGICAL COHERENCE - Reasoning flow and argument structure")
    print("2. EVIDENCE STRENGTH - Quality and relevance of supporting data")
    print("3. RISK ASSESSMENT - Downside scenario consideration")
    print("4. CONTRARIAN PERSPECTIVE - Counter-argument acknowledgment")
    print("5. MEASURABILITY - KPI selection appropriateness")
    print("6. MARKET TIMING - Catalyst identification and timing")
    print("7. COMPETITIVE DYNAMICS - Industry understanding depth")
    print("8. FINANCIAL ROBUSTNESS - Valuation methodology soundness")
    
    print("\nPrompting approach:")
    print("• Expert investment analyst persona with 20+ years experience")
    print("• Institutional-quality assessment framework")
    print("• Structured JSON response format for consistency")
    print("• Actionable insights for improving investment decisions")
    print("• Risk-weighted outcome analysis")
    print("• Competitive advantage sustainability assessment")

if __name__ == "__main__":
    try:
        test_thesis_evaluation()
        test_evaluation_prompting_examples()
        print("\n=== TEST COMPLETED ===")
        print("Thesis evaluation system demonstrates:")
        print("• Multi-dimensional strength analysis")
        print("• Professional-grade investment assessment")
        print("• Actionable improvement recommendations")
        print("• Risk factor identification and mitigation")
        print("• Research quality scoring and completeness metrics")
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        print("Note: Ensure the application is running on localhost:5000")