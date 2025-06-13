#!/usr/bin/env python3
"""
Test script for expanded 6-level signal classification system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.signal_classifier import SignalClassifier
from services.internal_research_service import InternalResearchService

def test_expanded_signal_system():
    """Test the expanded 6-level signal classification system"""
    print("Testing Expanded Signal Classification System (Levels 0-5)")
    print("=" * 60)
    
    # Mock thesis analysis data
    mock_thesis_analysis = {
        'core_claim': 'NVIDIA Corporation is positioned for sustained growth driven by AI demand, data center expansion, and automotive AI adoption. Expected 25% annual growth with expanding market leadership in GPU and AI accelerator technology.',
        'assumptions': [
            'AI market demand will continue accelerating through 2025-2027',
            'Data center modernization will drive GPU adoption',
            'Automotive AI and autonomous driving will reach commercial scale',
            'Competitive moat in GPU architecture will be maintained'
        ],
        'mental_model': 'Growth',
        'metrics_to_track': [
            {
                'name': 'Data center revenue growth',
                'type': 'Level_1_Raw_Activity',
                'description': 'Quarterly data center revenue growth rate',
                'data_source': 'NVIDIA financial reports',
                'predictive_power': 'high',
                'lead_lag_indicator': 'leading'
            },
            {
                'name': 'AI chip market share',
                'type': 'Level_2_Simple_Aggregation',
                'description': 'Market share in AI acceleration chips',
                'data_source': 'Industry reports',
                'predictive_power': 'high',
                'lead_lag_indicator': 'coincident'
            },
            {
                'name': 'GPU performance per dollar ratio',
                'type': 'Level_3_Derived_Metrics',
                'description': 'Performance efficiency compared to competition',
                'data_source': 'Technical benchmarks',
                'predictive_power': 'medium',
                'lead_lag_indicator': 'leading'
            }
        ]
    }
    
    # Test Level 0 Internal Research Service
    print("\n1. Testing Level 0 Internal Research Data Generation")
    print("-" * 50)
    
    research_service = InternalResearchService()
    level_0_signals = research_service.generate_research_signals(mock_thesis_analysis)
    
    print(f"Generated {len(level_0_signals)} Level 0 signals:")
    for signal in level_0_signals:
        print(f"  • {signal['signal_name']} ({signal['category']})")
        query_structure = signal['query_structure']
        print(f"    - Entities: {query_structure.get('entities', [])}")
        print(f"    - Metrics: {query_structure.get('metrics', [])}")
        print(f"    - Filters: {query_structure.get('filters', {})}")
    
    # Test Full Signal Classification
    print("\n2. Testing Complete Signal Classification (Levels 0-5)")
    print("-" * 50)
    
    classifier = SignalClassifier()
    classification_result = classifier.extract_signals_from_ai_analysis(
        mock_thesis_analysis, [], focus_primary=True
    )
    
    if 'error' in classification_result:
        print(f"Classification error: {classification_result['error']}")
        return False
    
    # Display signal hierarchy
    signals_by_level = classification_result.get('signals_by_level', {})
    total_signals = sum(len(signals) for signals in signals_by_level.values())
    
    print(f"Total signals classified: {total_signals}")
    print("\nSignal Distribution by Level:")
    
    level_descriptions = {
        'Internal Research Data': 'Level 0 - Structured financial queries and thesis validation',
        'Raw Economic Activity': 'Level 1 - Direct measurements: housing starts, permit applications, factory utilization',
        'Simple Aggregation': 'Level 2 - Basic combinations: monthly spending totals, inventory levels',
        'Derived Metrics': 'Level 3 - Calculated ratios: growth rates, market share changes',
        'Complex Ratios': 'Level 4 - Multi-variable calculations: valuation multiples, peer comparisons',
        'Market Sentiment': 'Level 5 - Behavioral indicators: analyst sentiment, options flow'
    }
    
    for level, description in level_descriptions.items():
        signal_count = len(signals_by_level.get(level, []))
        print(f"  {description}: {signal_count} signals")
        if signal_count > 0:
            for signal_name in signals_by_level[level][:3]:  # Show first 3
                print(f"    • {signal_name}")
            if signal_count > 3:
                print(f"    ... and {signal_count - 3} more")
    
    # Test Signal Quality Assessment
    print("\n3. Testing Signal Quality Assessment")
    print("-" * 50)
    
    quality_assessment = classification_result.get('quality_assessment', {})
    print(f"Overall Quality Score: {quality_assessment.get('overall_score', 0):.2f}")
    print(f"Assessment: {quality_assessment.get('assessment', 'N/A')}")
    
    # Test Value Chain Mapping
    print("\n4. Testing Value Chain Mapping")
    print("-" * 50)
    
    value_chain = classification_result.get('value_chain_mapping', {})
    for position, signals in value_chain.items():
        if signals:
            print(f"{position.title()}: {len(signals)} signals")
    
    # Test Monitoring Strategy
    print("\n5. Testing Monitoring Strategy")
    print("-" * 50)
    
    monitoring = classification_result.get('monitoring_strategy', {})
    print(f"Recommended Frequency: {monitoring.get('monitoring_frequency', 'N/A')}")
    priority_signals = monitoring.get('priority_signals', [])
    print(f"Priority Signals: {len(priority_signals)}")
    for signal in priority_signals[:3]:
        print(f"  • {signal}")
    
    print("\n" + "=" * 60)
    print("✅ Expanded Signal Classification System Test Completed")
    print(f"✅ Generated {len(level_0_signals)} Level 0 Internal Research signals")
    print(f"✅ Classified {total_signals} total signals across 6 levels")
    print(f"✅ Quality score: {quality_assessment.get('overall_score', 0):.2f}")
    
    return True

if __name__ == "__main__":
    success = test_expanded_signal_system()
    sys.exit(0 if success else 1)