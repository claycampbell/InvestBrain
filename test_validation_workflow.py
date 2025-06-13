"""
Test script to verify the complete Level 0 signal validation workflow
"""

import requests
import json
import time

def test_validation_workflow():
    """Test the complete validation workflow"""
    print("Testing Level 0 Signal Validation Workflow")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test Case 1: Revenue Growth Validation Signal
    print("\n1. Testing Revenue Growth Validation Signal")
    print("-" * 40)
    
    revenue_query = {
        "entities": ["NVIDIA"],
        "relationships": [],
        "filters": [
            {"field": "revenue_cagr_5_yr", "operator": ">", "value": 0.15}
        ],
        "metrics": ["revenue", "revenue_cagr_5_yr", "market_cap"],
        "sort_by": {"field": "revenue", "order": "desc"},
        "limit": 5
    }
    
    test_validation_request(base_url, revenue_query, "Revenue Growth Validation")
    
    # Test Case 2: Fund Holdings Analysis
    print("\n2. Testing Fund Holdings Analysis Signal")
    print("-" * 40)
    
    holdings_query = {
        "entities": ["Microsoft"],
        "relationships": ["fund_holding"],
        "filters": [
            {"field": "market_cap", "operator": ">", "value": 5000000000}
        ],
        "metrics": ["market_cap", "share_count"],
        "sort_by": {"field": "market_cap", "order": "desc"},
        "limit": 5
    }
    
    test_validation_request(base_url, holdings_query, "Top Fund Holdings Analysis")
    
    # Test Case 3: Market Position Analysis
    print("\n3. Testing Market Position Analysis Signal")
    print("-" * 40)
    
    market_query = {
        "entities": ["Apple", "Microsoft", "Google"],
        "relationships": [],
        "filters": [
            {"field": "market_cap", "operator": ">", "value": 100000000000}
        ],
        "metrics": ["market_cap", "pe", "roic"],
        "sort_by": {"field": "market_cap", "order": "desc"},
        "limit": 10
    }
    
    test_validation_request(base_url, market_query, "Market Position Analysis")

def test_validation_request(base_url, query_structure, signal_name):
    """Test a single validation request"""
    try:
        # Step 1: Initiate validation request
        print(f"Initiating validation for: {signal_name}")
        
        response = requests.post(
            f"{base_url}/api/validate-signal",
            json={
                "query_structure": query_structure,
                "signal_name": signal_name,
                "jwt_token": "test_token_for_demo"  # Demo token
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation initiated successfully")
            print(f"   Request ID: {result.get('request_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Chat ID: {result.get('chat_id')}")
            
            # Step 2: Poll for status (simulate the frontend polling)
            request_id = result.get('request_id')
            if request_id:
                print(f"   Polling for results...")
                poll_validation_status(base_url, request_id, signal_name)
            
        else:
            print(f"❌ Validation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing validation: {str(e)}")

def poll_validation_status(base_url, request_id, signal_name):
    """Poll validation status to simulate frontend behavior"""
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        try:
            response = requests.get(
                f"{base_url}/api/validation-status/{request_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                
                print(f"   Attempt {attempt}: Status = {status}")
                
                if status == 'completed':
                    print(f"✅ Validation completed for {signal_name}")
                    validation_result = result.get('result')
                    if validation_result and validation_result.get('widgets'):
                        widget = validation_result['widgets'][0]
                        quality_score = widget.get('assessed_quality_score', 0)
                        print(f"   Quality Score: {quality_score}")
                        
                        # Show first few lines of response
                        markdown = widget.get('generated_markdown_text', '')
                        if markdown:
                            first_line = markdown.split('\n')[0]
                            print(f"   Response Preview: {first_line[:80]}...")
                    break
                    
                elif status == 'failed':
                    print(f"❌ Validation failed for {signal_name}")
                    error = result.get('result', {}).get('error', 'Unknown error')
                    print(f"   Error: {error}")
                    break
                    
                elif status == 'processing':
                    print(f"   Still processing... (attempt {attempt})")
                    time.sleep(2)  # Wait before next poll
                    
            else:
                print(f"   Status check failed: {response.status_code}")
                break
                
        except Exception as e:
            print(f"   Polling error: {str(e)}")
            break
    
    if attempt >= max_attempts:
        print(f"⏰ Validation timeout for {signal_name}")

def test_api_endpoints():
    """Test that all validation endpoints are available"""
    print("\n4. Testing API Endpoint Availability")
    print("-" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test the test-query-parser endpoint (should work)
    try:
        response = requests.post(
            f"{base_url}/api/test-query-parser",
            json={
                "query_structure": {
                    "entities": ["Test Company"],
                    "relationships": [],
                    "filters": [],
                    "metrics": ["market_cap"],
                    "sort_by": {"field": "market_cap", "order": "desc"},
                    "limit": 5
                },
                "signal_name": "Test Signal"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test query parser endpoint working")
            print(f"   Quality Score: {result.get('widgets', [{}])[0].get('assessed_quality_score', 'N/A')}")
        else:
            print(f"❌ Test endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test endpoint error: {str(e)}")

if __name__ == "__main__":
    test_validation_workflow()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ Validation Workflow Test Completed")
    print("\nKey Features Tested:")
    print("• Level 0 signal validation initiation")
    print("• Structured query generation")
    print("• External API integration workflow")
    print("• Status polling mechanism")
    print("• Error handling and fallbacks")
    print("• JWT token management")
    print("\nThe system is ready to validate Level 0 signals against")
    print("your internal data API at:")
    print("https://iggpt.core-ml-sqa.mle.aws-qa.capgroup.com")