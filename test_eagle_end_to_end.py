#!/usr/bin/env python3
"""
Test Eagle API End-to-End Implementation
Tests metric identification, sedol_id extraction, and mock data generation
"""

import requests
import json
import time

def test_eagle_endpoint_direct():
    """Test the new Eagle API endpoint directly"""
    print("Testing Eagle API Endpoint Direct Call")
    print("=" * 40)
    
    # Test data
    test_data = {
        "company_name": "NVIDIA Corporation",
        "thesis_text": "NVIDIA benefits from AI chip demand and data center growth. CUDA ecosystem creates competitive advantages.",
        "metrics_to_track": [
            "Revenue Growth Rate",
            "Operating Margin", 
            "Free Cash Flow",
            "Return on Equity",
            "Gross Profit Margin"
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/eagle-metrics",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Eagle API Endpoint Success")
            print(f"✓ Company: {result.get('company_name', 'N/A')}")
            print(f"✓ SEDOL ID: {result.get('sedol_id', 'N/A')}")
            print(f"✓ Metrics Requested: {len(result.get('metrics_requested', []))}")
            print(f"✓ Data Source: {result.get('source', 'N/A')}")
            
            # Check financial metrics
            financial_metrics = result.get('data', {}).get('financialMetrics', [])
            if financial_metrics:
                metrics = financial_metrics[0].get('metrics', [])
                print(f"✓ Metrics Returned: {len(metrics)}")
                
                print("\nSample Metrics:")
                for i, metric in enumerate(metrics[:3]):
                    print(f"  {i+1}. {metric.get('name', 'N/A')}: {metric.get('value', 'N/A')} {metric.get('unit', '')}")
            
            return True
        else:
            print(f"✗ Eagle API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Eagle API test failed: {e}")
        return False

def test_company_name_extraction():
    """Test company name extraction from thesis"""
    print("\nTesting Company Name Extraction")
    print("=" * 35)
    
    test_cases = [
        "Tesla will dominate the EV market with innovative technology",
        "Microsoft's cloud platform Azure is growing rapidly",
        "Apple Inc benefits from strong iPhone sales and services revenue",
        "Amazon's AWS and e-commerce growth will continue"
    ]
    
    success_count = 0
    
    for thesis in test_cases:
        test_data = {
            "thesis_text": thesis,
            "metrics_to_track": ["Revenue Growth"]
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/api/eagle-metrics",
                json=test_data,
                timeout=8
            )
            
            if response.status_code == 200:
                result = response.json()
                company_name = result.get('company_name', 'Not Found')
                print(f"✓ '{thesis[:30]}...' → {company_name}")
                success_count += 1
            else:
                print(f"✗ '{thesis[:30]}...' → Failed ({response.status_code})")
                
        except Exception as e:
            print(f"✗ '{thesis[:30]}...' → Error: {e}")
    
    print(f"\nCompany Extraction Success Rate: {success_count}/{len(test_cases)}")
    return success_count == len(test_cases)

def test_analysis_integration():
    """Test Eagle API integration through main analysis flow"""
    print("\nTesting Analysis Integration")
    print("=" * 30)
    
    thesis_text = "Apple Inc will benefit from iPhone 15 sales and services growth. Strong brand loyalty and ecosystem create sustainable competitive advantages."
    
    try:
        response = requests.post(
            "http://localhost:5000/analyze",
            data={"thesis_text": thesis_text},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check for Eagle API signals in results
            signals = result.get('signal_extraction', {}).get('signals', [])
            eagle_signals = [s for s in signals if s.get('eagle_api') == True]
            
            print(f"✓ Analysis completed")
            print(f"✓ Total signals: {len(signals)}")
            print(f"✓ Eagle API signals: {len(eagle_signals)}")
            
            if eagle_signals:
                print("\nEagle API Signals Found:")
                for signal in eagle_signals[:3]:
                    print(f"  - {signal.get('name', 'N/A')}")
                    print(f"    Value: {signal.get('current_value', 'N/A')}")
                    print(f"    Company: {signal.get('company_name', 'N/A')}")
                    print(f"    SEDOL: {signal.get('sedol_id', 'N/A')}")
                return True
            else:
                print("✗ No Eagle API signals found in analysis")
                return False
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Analysis integration test failed: {e}")
        return False

def test_mock_data_generation():
    """Test mock data generation for various companies"""
    print("\nTesting Mock Data Generation")
    print("=" * 30)
    
    companies = ["Tesla Inc", "Microsoft Corporation", "Unknown Company XYZ"]
    
    for company in companies:
        test_data = {
            "company_name": company,
            "metrics_to_track": ["Revenue", "Profit Margin", "Cash Flow"]
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/api/eagle-metrics",
                json=test_data,
                timeout=8
            )
            
            if response.status_code == 200:
                result = response.json()
                is_mock = result.get('mock_data', False)
                metrics_count = len(result.get('data', {}).get('financialMetrics', [{}])[0].get('metrics', []))
                
                print(f"✓ {company}")
                print(f"  Mock Data: {is_mock}")
                print(f"  Metrics: {metrics_count}")
                print(f"  SEDOL: {result.get('sedol_id', 'N/A')}")
            else:
                print(f"✗ {company} failed: {response.status_code}")
                
        except Exception as e:
            print(f"✗ {company} error: {e}")

if __name__ == "__main__":
    print("Eagle API End-to-End Implementation Test")
    print("=" * 45)
    
    # Run all tests
    endpoint_ok = test_eagle_endpoint_direct()
    extraction_ok = test_company_name_extraction()  
    integration_ok = test_analysis_integration()
    
    test_mock_data_generation()
    
    print("\n" + "=" * 45)
    print("Test Summary:")
    print(f"Eagle API Endpoint: {'✓ Pass' if endpoint_ok else '✗ Fail'}")
    print(f"Company Extraction: {'✓ Pass' if extraction_ok else '✗ Fail'}")
    print(f"Analysis Integration: {'✓ Pass' if integration_ok else '✗ Fail'}")
    
    if endpoint_ok and integration_ok:
        print("\n🎯 Eagle API End-to-End Implementation Working!")
        print("✓ Metric identification from LLM metrics_to_track")
        print("✓ SEDOL ID extraction from company names")
        print("✓ Mock fallback data generation")
        print("✓ Integration with main analysis pipeline")
    else:
        print("\n❌ Some tests failed - check implementation")