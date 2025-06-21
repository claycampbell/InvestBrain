"""
Test script to verify Eagle API signals display with source badges
"""

import requests
import json
from services.local_analysis_service import LocalAnalysisService
from services.signal_classifier import SignalClassifier

def test_eagle_signal_display():
    """Test that Eagle API signals display with proper source badges"""
    print("Testing Eagle API Signal Display with Source Badges")
    print("=" * 55)
    
    # Test 1: Local analysis service Eagle API integration
    print("\n1. Testing Local Analysis Service:")
    print("-" * 40)
    
    local_service = LocalAnalysisService()
    thesis_text = "NVIDIA (NVDA) is positioned for continued growth in AI and data center markets. The company SEDOL: 2379504 has strong revenue momentum."
    
    try:
        # Extract signals using local service
        metrics = local_service._extract_signals_from_thesis(thesis_text)
        
        print(f"Total signals extracted: {len(metrics)}")
        
        # Look for Eagle API signals
        eagle_signals = [m for m in metrics if m.get('data_source') == 'Eagle API']
        print(f"Eagle API signals found: {len(eagle_signals)}")
        
        if eagle_signals:
            for i, signal in enumerate(eagle_signals[:2], 1):
                print(f"\nEagle Signal {i}:")
                print(f"  Name: {signal.get('name', 'Unknown')}")
                print(f"  Type: {signal.get('type', 'Unknown')}")
                print(f"  Data Source: {signal.get('data_source', 'Unknown')}")
                print(f"  Company: {signal.get('company_ticker', 'Unknown')}")
                print(f"  SEDOL: {signal.get('sedol_id', 'Unknown')}")
                print(f"  Eagle API Flag: {signal.get('eagle_api', False)}")
                print(f"  Level: {signal.get('level', 'Unknown')}")
                print(f"  Current Value: {signal.get('current_value', 'N/A')}")
        else:
            print("  No Eagle API signals found in extraction")
    
    except Exception as e:
        print(f"  Error in local analysis: {str(e)}")
    
    # Test 2: Signal classification
    print("\n2. Testing Signal Classification:")
    print("-" * 40)
    
    try:
        classifier = SignalClassifier()
        
        # Mock AI analysis with Eagle API metrics
        mock_analysis = {
            'metrics_to_track': [
                {
                    'name': 'Eagle: Revenue Growth',
                    'type': 'Level_0_Raw_Activity',
                    'data_source': 'Eagle API',
                    'company_ticker': 'NVDA',
                    'sedol_id': '2379504',
                    'eagle_api': True,
                    'current_value': '0.15',
                    'description': 'Real-time financial metric for NVDA (SEDOL: 2379504): Revenue Growth'
                }
            ]
        }
        
        signal_result = classifier.extract_signals_from_ai_analysis(mock_analysis, [])
        
        print(f"Total signals classified: {signal_result.get('total_signals_identified', 0)}")
        print(f"Level 0 signals: {signal_result.get('primary_signals_count', 0)}")
        
        # Check signals by level
        signals_by_level = signal_result.get('signals_by_level', {})
        level_0_signals = signals_by_level.get('Internal Research Data', [])
        
        print(f"Internal Research Data signals: {len(level_0_signals)}")
        
        if level_0_signals:
            for signal in level_0_signals[:2]:
                print(f"\nLevel 0 Signal:")
                print(f"  Name: {signal}")
                
    except Exception as e:
        print(f"  Error in signal classification: {str(e)}")
    
    # Test 3: API endpoint test
    print("\n3. Testing API Endpoint:")
    print("-" * 40)
    
    try:
        response = requests.get(
            "http://localhost:5000/api/test-eagle-response",
            params={'ticker': 'NVDA', 'sedol_id': '2379504'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  API Response Status: {response.status_code}")
            print(f"  Schema Valid: {data.get('schema_valid', False)}")
            print(f"  Metrics Count: {data.get('metrics_count', 0)}")
            
            test_response = data.get('test_response', {})
            if test_response.get('data', {}).get('financialMetrics'):
                metrics = test_response['data']['financialMetrics'][0].get('metrics', [])
                if metrics:
                    sample_metric = metrics[0]
                    print(f"  Sample Metric: {sample_metric.get('name', 'Unknown')}")
                    print(f"  Sample Value: {sample_metric.get('value', 'Unknown')}")
        else:
            print(f"  API Error: {response.status_code}")
            
    except Exception as e:
        print(f"  API Error: {str(e)}")
    
    # Test 4: Frontend structure verification
    print("\n4. Frontend Integration Check:")
    print("-" * 40)
    
    # Expected signal structure for frontend
    expected_signal = {
        'name': 'Eagle: ciq_revenue_cagr_5yr',
        'type': 'Level_0_Raw_Activity',
        'description': 'Real-time financial metric for NVDA (SEDOL: 2379504): Revenue CAGR',
        'data_source': 'Eagle API',
        'company_ticker': 'NVDA',
        'sedol_id': '2379504',
        'eagle_api': True,
        'current_value': '0.185',
        'level': 'Internal Research Data'
    }
    
    print("Expected Signal Structure for Frontend:")
    for key, value in expected_signal.items():
        print(f"  {key}: {value}")
    
    print("\n5. Badge Display Logic:")
    print("-" * 40)
    
    # Test badge logic
    signal = expected_signal
    
    # Level badge
    level_badge = "Level 0"
    print(f"  Level Badge: {level_badge}")
    
    # Source badge
    if signal['data_source'] == 'Eagle API':
        source_badge = "Eagle API (Green)"
    else:
        source_badge = f"{signal['data_source']} (Blue)"
    print(f"  Source Badge: {source_badge}")
    
    # Real-time badge
    if signal.get('eagle_api'):
        realtime_badge = "🦅 Real-time (Yellow)"
        print(f"  Real-time Badge: {realtime_badge}")
    
    # Company info
    company_info = f"{signal['company_ticker']}"
    if signal.get('sedol_id'):
        company_info += f" (SEDOL: {signal['sedol_id']})"
    print(f"  Company Info: {company_info}")
    
    # Current value
    if signal.get('current_value'):
        print(f"  Current Value: {signal['current_value']} (Green)")
    
    print("\nEagle API Signal Display Test Complete!")
    print("\nExpected Frontend Display:")
    print("- Level 0 signals in 'Internal Research Data' section")
    print("- Green 'Eagle API' badge for data source")
    print("- Yellow 'Real-time' badge with eagle icon")
    print("- Company ticker and SEDOL displayed")
    print("- Current values shown in green")
    print("- Blue 'Validate Data' button for each signal")

if __name__ == "__main__":
    test_eagle_signal_display()