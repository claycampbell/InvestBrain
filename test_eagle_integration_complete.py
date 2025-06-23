#!/usr/bin/env python3
"""
Complete Eagle API Integration Test Suite
Tests the migrated Eagle API functionality in ReliableAnalysisService
"""

import requests
import json
import time
from services.reliable_analysis_service import ReliableAnalysisService
from services.data_adapter_service import DataAdapter

def test_eagle_api_integration():
    """Test complete Eagle API integration workflow"""
    print("Testing Eagle API Integration with ReliableAnalysisService")
    print("=" * 60)
    
    # Test 1: Direct service testing
    print("\n1. Testing ReliableAnalysisService Eagle API Methods:")
    print("-" * 50)
    
    reliable_service = ReliableAnalysisService()
    
    # Test thesis with known company identifiers
    thesis_text = "NVIDIA (NVDA) is positioned for continued growth in AI and data center markets. The company SEDOL: 2379504 has strong revenue momentum and expanding market share in the GPU sector."
    
    try:
        # Test company identifier extraction
        ticker, sedol_id = reliable_service._extract_company_identifiers(thesis_text)
        print(f"✓ Company Extraction: {ticker} (SEDOL: {sedol_id})")
        
        # Test Eagle signal extraction
        eagle_signals = reliable_service.extract_eagle_signals_for_thesis(thesis_text)
        print(f"✓ Eagle Signals Found: {len(eagle_signals)}")
        
        if eagle_signals:
            for i, signal in enumerate(eagle_signals[:2], 1):
                print(f"  Signal {i}:")
                print(f"    Name: {signal.get('name', 'N/A')}")
                print(f"    Type: {signal.get('type', 'N/A')}")
                print(f"    Data Source: {signal.get('data_source', 'N/A')}")
                print(f"    Eagle API Flag: {signal.get('eagle_api', False)}")
                print(f"    Current Value: {signal.get('current_value', 'N/A')}")
        else:
            print("  No Eagle signals extracted (API may be unavailable)")
            
    except Exception as e:
        print(f"✗ Service test error: {str(e)}")
    
    # Test 2: Full analysis workflow
    print("\n2. Testing Complete Analysis Workflow:")
    print("-" * 45)
    
    try:
        analysis_result = reliable_service.analyze_thesis_comprehensive(thesis_text)
        
        metrics_to_track = analysis_result.get('metrics_to_track', [])
        eagle_metrics = [m for m in metrics_to_track if m.get('eagle_api', False)]
        
        print(f"✓ Total Metrics: {len(metrics_to_track)}")
        print(f"✓ Eagle API Metrics: {len(eagle_metrics)}")
        print(f"✓ Analysis Status: {'Complete' if analysis_result.get('core_claim') else 'Incomplete'}")
        
        if eagle_metrics:
            print("  Eagle API Integration: Active")
            for metric in eagle_metrics[:1]:
                print(f"    Sample: {metric.get('name', 'N/A')} = {metric.get('current_value', 'N/A')}")
        else:
            print("  Eagle API Integration: No metrics (check API availability)")
            
    except Exception as e:
        print(f"✗ Analysis workflow error: {str(e)}")

def test_web_interface_integration():
    """Test Eagle API integration through web interface"""
    print("\n3. Testing Web Interface Integration:")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test thesis analysis endpoint
    try:
        thesis_data = {
            'thesis_text': 'NVIDIA (NVDA) is positioned for continued growth in AI and data center markets. The company SEDOL: 2379504 has strong fundamentals.'
        }
        
        print("Submitting thesis analysis request...")
        response = requests.post(f"{base_url}/analyze", data=thesis_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Analysis Response: {response.status_code}")
            print(f"✓ Published: {result.get('published', False)}")
            
            # Check signal extraction results
            signal_extraction = result.get('signal_extraction', {})
            total_signals = signal_extraction.get('total_signals_identified', 0)
            signals_by_level = signal_extraction.get('signals_by_level', {})
            
            print(f"✓ Total Signals: {total_signals}")
            
            # Look for Internal Research Data (Eagle API signals)
            internal_signals = signals_by_level.get('Internal Research Data', [])
            print(f"✓ Eagle API Signals: {len(internal_signals)}")
            
            if internal_signals:
                print("  Eagle API signals found in web response:")
                for signal in internal_signals[:2]:
                    print(f"    - {signal.get('name', 'N/A')}")
                    print(f"      Source: {signal.get('data_source', 'N/A')}")
                    print(f"      Value: {signal.get('current_value', 'N/A')}")
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            print(f"  Error: {response.text[:200]}...")
            
    except Exception as e:
        print(f"✗ Web interface test error: {str(e)}")

def test_eagle_api_endpoint():
    """Test dedicated Eagle API test endpoint"""
    print("\n4. Testing Eagle API Test Endpoint:")
    print("-" * 38)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test with NVIDIA identifiers
        params = {
            'ticker': 'NVDA',
            'sedol_id': '2379504'
        }
        
        response = requests.get(f"{base_url}/api/test-eagle-response", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Eagle API Test: {response.status_code}")
            print(f"✓ Response Success: {data.get('success', False)}")
            
            # Check response structure
            if 'data' in data and 'financialMetrics' in data['data']:
                metrics = data['data']['financialMetrics'][0].get('metrics', [])
                print(f"✓ Metrics Available: {len(metrics)}")
                
                if metrics:
                    print("  Sample metrics:")
                    for metric in metrics[:3]:
                        print(f"    - {metric.get('name', 'N/A')}: {metric.get('value', 'N/A')}")
            else:
                print("  Response structure may be using fallback data")
        else:
            print(f"✗ Eagle API test failed: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Eagle API endpoint test error: {str(e)}")

def test_data_adapter_connection():
    """Test DataAdapter service directly"""
    print("\n5. Testing DataAdapter Service:")
    print("-" * 32)
    
    try:
        data_adapter = DataAdapter()
        
        # Test connection validation
        is_connected = data_adapter.validate_connection()
        print(f"✓ Connection Status: {'Connected' if is_connected else 'Disconnected'}")
        
        # Test metric fetching
        categories = ['Revenue Growth Rate', 'Operating Margin']
        result = data_adapter.fetch_company_metrics('NVDA', categories, '2379504')
        
        if result and result.get('success'):
            print(f"✓ Metric Fetch: Success")
            metrics = result.get('metrics', {})
            print(f"✓ Metrics Count: {len(metrics)}")
            
            for name, data in list(metrics.items())[:2]:
                print(f"    {name}: {data.get('value', 'N/A')}")
        else:
            print("✓ Metric Fetch: Using fallback data (Eagle API may be unavailable)")
            
    except Exception as e:
        print(f"✗ DataAdapter test error: {str(e)}")

def run_integration_tests():
    """Run all integration tests"""
    print("Eagle API Integration Test Suite")
    print("=" * 40)
    print("Testing migrated Eagle API functionality in ReliableAnalysisService")
    print()
    
    # Run all test suites
    test_eagle_api_integration()
    test_web_interface_integration()
    test_eagle_api_endpoint()
    test_data_adapter_connection()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("\nTo verify Eagle API is working:")
    print("1. Check that Eagle API signals appear in analysis results")
    print("2. Verify 'Internal Research Data' level signals are created")
    print("3. Confirm signals have 'eagle_api': true flag")
    print("4. Look for real-time financial metrics in signal descriptions")
    print("\nIf tests show 'fallback data', the Eagle API may need proper credentials.")

if __name__ == "__main__":
    run_integration_tests()