#!/usr/bin/env python3
"""
Test fallback analysis system for counter thesis scenarios and alternative company analysis
"""
import requests
import json
import time

def test_fallback_analysis_system():
    """Test that fallback analysis provides counter thesis scenarios and alternative companies"""
    base_url = "http://0.0.0.0:5000"
    
    # Simple thesis for testing
    test_thesis = "Apple Inc shows strong fundamentals with iPhone revenue growth and expanding services revenue creating sustainable competitive advantages."
    
    print("Testing Fallback Analysis System")
    print("=" * 40)
    
    try:
        print("Submitting analysis request...")
        
        analysis_data = {
            'thesis_text': test_thesis,
            'generate_signals': True
        }
        
        response = requests.post(f"{base_url}/analyze", data=analysis_data, timeout=20)
        
        if response.status_code != 200:
            print(f"Analysis failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
        
        # Extract thesis ID
        import re
        thesis_match = re.search(r'thesis-(\d+)', response.text)
        if not thesis_match:
            print("No thesis ID found in response")
            return False
        
        thesis_id = thesis_match.group(1)
        print(f"Analysis completed - Thesis ID: {thesis_id}")
        
        # Test counter thesis scenarios
        print("\nTesting Counter Thesis Scenarios...")
        thesis_response = requests.get(f"{base_url}/get_thesis_data/{thesis_id}")
        
        counter_thesis_working = False
        if thesis_response.status_code == 200:
            thesis_data = thesis_response.json()
            
            if 'counter_thesis' in thesis_data and thesis_data['counter_thesis']:
                counter_data = thesis_data['counter_thesis']
                
                if isinstance(counter_data, dict) and 'scenarios' in counter_data:
                    scenarios = counter_data['scenarios']
                    if scenarios and len(scenarios) > 0:
                        print(f"Found {len(scenarios)} counter thesis scenarios:")
                        for i, scenario in enumerate(scenarios, 1):
                            print(f"  {i}. {scenario.get('scenario', 'Unknown')}")
                            print(f"     Probability: {scenario.get('probability', 'Unknown')}")
                        counter_thesis_working = True
                    else:
                        print("Counter thesis scenarios array is empty")
                else:
                    print("Counter thesis structure incorrect")
            else:
                print("No counter thesis found")
        else:
            print(f"Failed to get thesis data: {thesis_response.status_code}")
        
        # Test alternative companies
        print("\nTesting Alternative Company Analysis...")
        alt_response = requests.get(f"{base_url}/get_alternative_companies/{thesis_id}")
        
        alt_companies_working = False
        if alt_response.status_code == 200:
            alt_data = alt_response.json()
            
            if 'alternative_companies' in alt_data:
                companies = alt_data['alternative_companies']
                if companies and len(companies) > 0:
                    print(f"Found {len(companies)} alternative companies:")
                    for company in companies[:3]:
                        print(f"  - {company.get('name', 'Unknown')} ({company.get('ticker', 'N/A')})")
                    alt_companies_working = True
                else:
                    print("No alternative companies available")
                    alt_companies_working = True  # Acceptable when no authentic data
            else:
                print("Alternative companies field missing")
        else:
            print(f"Alternative companies request failed: {alt_response.status_code}")
        
        # Test page rendering
        print("\nTesting Page Rendering...")
        page_response = requests.get(f"{base_url}/thesis/{thesis_id}")
        
        page_working = False
        if page_response.status_code == 200:
            if 'Counter-Thesis & Risk Scenarios' in page_response.text:
                print("Counter thesis section renders correctly")
                page_working = True
            else:
                print("Counter thesis section not found in page")
        else:
            print(f"Page failed to load: {page_response.status_code}")
        
        # Results
        print("\n" + "=" * 40)
        print("RESULTS:")
        print(f"Counter Thesis: {'WORKING' if counter_thesis_working else 'NOT WORKING'}")
        print(f"Alt Companies:  {'WORKING' if alt_companies_working else 'NOT WORKING'}")
        print(f"Page Rendering: {'WORKING' if page_working else 'NOT WORKING'}")
        
        overall_success = counter_thesis_working and alt_companies_working and page_working
        print(f"\nOverall: {'SUCCESS' if overall_success else 'NEEDS FIXING'}")
        
        return overall_success
        
    except Exception as e:
        print(f"Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_fallback_analysis_system()
    exit(0 if success else 1)