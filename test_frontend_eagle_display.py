"""
Test frontend Eagle API signal display with direct analysis flow
"""

import requests
import json
import time

def test_frontend_eagle_display():
    """Test complete flow from analysis to frontend display"""
    print("Testing Frontend Eagle API Signal Display")
    print("=" * 45)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Simple analysis with NVDA ticker
    print("\n1. Testing Analysis with NVDA:")
    print("-" * 35)
    
    thesis_text = "NVIDIA (NVDA) is positioned for continued growth in AI and data center markets. Strong revenue momentum expected."
    
    try:
        response = requests.post(
            f"{base_url}/analyze",
            data={'thesis_text': thesis_text},
            timeout=60
        )
        
        print(f"Analysis Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Analysis Success: {result.get('published', False)}")
            
            # Check signal extraction
            signal_extraction = result.get('signal_extraction', {})
            total_signals = signal_extraction.get('total_signals_identified', 0)
            print(f"Total Signals Identified: {total_signals}")
            
            # Check signals by level
            signals_by_level = signal_extraction.get('signals_by_level', {})
            print(f"Signal Categories: {list(signals_by_level.keys())}")
            
            # Look for Internal Research Data (Level 0)
            internal_signals = signals_by_level.get('Internal Research Data', [])
            print(f"Level 0 (Internal Research Data) Signals: {len(internal_signals)}")
            
            if internal_signals:
                print("\nLevel 0 Signals Found:")
                for i, signal in enumerate(internal_signals[:3], 1):
                    if isinstance(signal, dict):
                        print(f"  {i}. {signal.get('name', 'Unknown')}")
                        print(f"     Source: {signal.get('data_source', 'Unknown')}")
                        print(f"     Eagle API: {signal.get('eagle_api', False)}")
                        print(f"     Company: {signal.get('company_ticker', 'Unknown')}")
                    else:
                        print(f"  {i}. {signal}")
            else:
                print("  No Level 0 signals found")
            
            # Check metrics_to_track from analysis
            thesis_analysis = result.get('thesis_analysis', {})
            metrics_to_track = thesis_analysis.get('metrics_to_track', [])
            print(f"\nMetrics to Track: {len(metrics_to_track)}")
            
            eagle_metrics = [m for m in metrics_to_track if isinstance(m, dict) and m.get('eagle_api')]
            print(f"Eagle API Metrics: {len(eagle_metrics)}")
            
            if eagle_metrics:
                print("\nEagle API Metrics Found:")
                for metric in eagle_metrics[:2]:
                    print(f"  - {metric.get('name', 'Unknown')}")
                    print(f"    Type: {metric.get('type', 'Unknown')}")
                    print(f"    Value: {metric.get('current_value', 'N/A')}")
            
        else:
            print(f"Analysis failed with status: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Analysis request failed: {str(e)}")
    
    # Test 2: Check main page rendering
    print("\n2. Testing Main Page:")
    print("-" * 25)
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Main Page Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if 'Internal Research Data' in content:
                print("✓ Level 0 section found in HTML")
            else:
                print("✗ Level 0 section not found in HTML")
                
            if 'Eagle API' in content:
                print("✓ Eagle API references found")
            else:
                print("✗ Eagle API references not found")
                
    except Exception as e:
        print(f"Main page request failed: {str(e)}")
    
    # Test 3: Eagle API test endpoint
    print("\n3. Testing Eagle API Endpoint:")
    print("-" * 35)
    
    try:
        response = requests.get(
            f"{base_url}/api/test-eagle-response",
            params={'ticker': 'NVDA', 'sedol_id': '2379504'},
            timeout=10
        )
        
        print(f"Eagle API Test Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Schema Valid: {data.get('schema_valid', False)}")
            print(f"Metrics Count: {data.get('metrics_count', 0)}")
            
            # Check test response structure
            test_response = data.get('test_response', {})
            if test_response.get('data'):
                financial_metrics = test_response['data'].get('financialMetrics', [])
                if financial_metrics:
                    metrics = financial_metrics[0].get('metrics', [])
                    print(f"Sample Metrics Available: {len(metrics)}")
                    if metrics:
                        sample = metrics[0]
                        print(f"Sample Metric: {sample.get('name')} = {sample.get('value')}")
        else:
            print(f"Eagle API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"Eagle API test failed: {str(e)}")
    
    print("\n" + "=" * 45)
    print("Frontend Display Test Summary:")
    print("- Analysis should extract Eagle API signals")
    print("- Level 0 signals should appear with badges")
    print("- Green 'Eagle API' badge for data source")
    print("- Yellow 'Real-time' badge with eagle icon")
    print("- Company ticker and SEDOL information")
    print("- Blue 'Validate Data' buttons")

if __name__ == "__main__":
    test_frontend_eagle_display()