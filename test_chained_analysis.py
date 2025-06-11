#!/usr/bin/env python3
"""
Test script to demonstrate the chained analysis approach working step by step
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.chained_analysis_service import ChainedAnalysisService
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_chained_analysis():
    """Test the chained analysis service"""
    service = ChainedAnalysisService()
    
    # Simple test thesis
    thesis = "Microsoft will benefit from enterprise AI adoption driving Azure cloud growth and productivity software demand."
    
    print(f"Testing chained analysis for: {thesis}")
    print("=" * 80)
    
    try:
        # Run the analysis
        result = service.analyze_thesis(thesis)
        
        print("\n✓ Analysis completed successfully!")
        print(f"Core claim: {result.get('core_claim', 'N/A')}")
        print(f"Mental model: {result.get('mental_model', 'N/A')}")
        print(f"Signals extracted: {len(result.get('metrics_to_track', []))}")
        print(f"Monitoring plan: {'✓' if result.get('monitoring_plan') else '✗'}")
        
        # Show structure
        print("\nAnalysis structure:")
        for key in result.keys():
            if isinstance(result[key], list):
                print(f"  {key}: {len(result[key])} items")
            elif isinstance(result[key], dict):
                print(f"  {key}: {len(result[key])} keys")
            else:
                print(f"  {key}: {type(result[key]).__name__}")
        
        return True
        
    except Exception as e:
        print(f"✗ Analysis failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_chained_analysis()
    sys.exit(0 if success else 1)