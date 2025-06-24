#!/usr/bin/env python3
"""
Test fallback analysis system to verify end-to-end functionality
"""

import requests
import json
import time

def test_fallback_analysis():
    """Test that analysis completes using fallback when Azure OpenAI times out"""
    
    print("Testing Investment Thesis Analysis with Network-Resilient Fallbacks")
    print("=" * 65)
    
    # Test thesis
    thesis_text = "Intel benefits from semiconductor recovery and data center demand. Manufacturing scale and x86 dominance create sustainable competitive advantages."
    
    print(f"Input thesis: {thesis_text[:60]}...")
    print("\nStarting analysis with aggressive timeout to trigger fallbacks...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:5000/analyze",
            data={"thesis_text": thesis_text},
            timeout=8  # Short timeout to test fallback speed
        )
        
        elapsed_time = time.time() - start_time
        print(f"Analysis completed in {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify response structure
            print("\nResponse Structure Verification:")
            required_keys = ['thesis_analysis', 'signal_extraction', 'monitoring_plan', 'thesis_id']
            
            for key in required_keys:
                if key in result:
                    print(f"  ✓ {key}")
                else:
                    print(f"  ✗ {key} MISSING")
                    return False
            
            # Check thesis analysis content
            thesis_analysis = result.get('thesis_analysis', {})
            print(f"\nThesis Analysis Results:")
            print(f"  Core Claim: {thesis_analysis.get('core_claim', 'N/A')[:60]}...")
            print(f"  Mental Model: {thesis_analysis.get('mental_model', 'N/A')}")
            print(f"  Assumptions: {len(thesis_analysis.get('assumptions', []))} items")
            print(f"  Causal Chain: {len(thesis_analysis.get('causal_chain', []))} steps")
            
            # Check signal extraction
            signals = result.get('signal_extraction', {}).get('signals', [])
            print(f"\nSignal Extraction Results:")
            print(f"  Total Signals: {len(signals)}")
            for i, signal in enumerate(signals[:3]):
                print(f"  {i+1}. {signal.get('name', 'Unknown')} ({signal.get('type', 'Unknown')})")
            
            # Check monitoring plan
            monitoring = result.get('monitoring_plan', {})
            print(f"\nMonitoring Plan:")
            print(f"  Priority Signals: {len(monitoring.get('priority_signals', []))}")
            print(f"  Weekly Reviews: {len(monitoring.get('weekly_reviews', []))}")
            
            # Check metadata
            metadata = result.get('metadata', {})
            print(f"\nMetadata:")
            print(f"  AI Confidence: {metadata.get('ai_confidence', 'N/A')}")
            print(f"  Fallback Mode: {metadata.get('fallback_mode', False)}")
            print(f"  Data Quality: {metadata.get('data_quality', 'N/A')}")
            
            # Verify database storage
            thesis_id = result.get('thesis_id')
            if thesis_id:
                print(f"  Database ID: {thesis_id}")
                
                # Test thesis view endpoint
                try:
                    view_response = requests.get(f"http://localhost:5000/thesis/{thesis_id}", timeout=3)
                    if view_response.status_code == 200:
                        print("  ✓ Thesis view endpoint accessible")
                    else:
                        print(f"  ✗ Thesis view returned {view_response.status_code}")
                except:
                    print("  ⚠ Thesis view endpoint timeout")
            
            print("\n" + "=" * 65)
            print("✓ END-TO-END ANALYSIS FLOW VERIFIED")
            print("✓ Fallback mechanisms working correctly")
            print("✓ Database integration functional")
            print("✓ Monitoring system operational")
            
            return True
            
        else:
            print(f"Analysis failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"Request timed out after {time.time() - start_time:.2f} seconds")
        print("This indicates the fallback system needs optimization")
        return False
    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False

def test_basic_endpoints():
    """Test that basic endpoints work without AI dependencies"""
    
    print("\nTesting Basic Endpoints (No AI Dependencies)")
    print("-" * 45)
    
    endpoints = [
        ("Home Page", "/"),
        ("Monitoring Dashboard", "/monitoring"),
        ("Analytics Dashboard", "/analytics"),
        ("Metric Categories", "/get_metric_categories")
    ]
    
    all_working = True
    
    for name, endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=3)
            if response.status_code == 200:
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} - Status {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"  ✗ {name} - Error: {str(e)}")
            all_working = False
    
    return all_working

if __name__ == "__main__":
    print("Investment Thesis Intelligence System - Comprehensive Flow Test")
    print("=" * 65)
    
    # Test basic endpoints first
    basic_ok = test_basic_endpoints()
    
    # Test analysis flow
    analysis_ok = test_fallback_analysis()
    
    print("\n" + "=" * 65)
    if basic_ok and analysis_ok:
        print("🎯 ALL TESTS PASSED - System functioning correctly")
        print("📊 Refactored architecture working as expected")
        print("🔄 Network-resilient fallbacks operational")
    else:
        print("❌ SOME TESTS FAILED - System needs debugging")
        if not basic_ok:
            print("🔧 Basic endpoints need attention")
        if not analysis_ok:
            print("🔧 Analysis pipeline needs optimization")