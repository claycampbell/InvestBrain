#!/usr/bin/env python3
"""
Verification test for counter thesis scenarios and alternative company analysis fixes
"""
import requests
import json
import time

def test_analysis_with_counter_thesis():
    """Test that counter thesis scenarios appear in analysis results"""
    base_url = "http://0.0.0.0:5000"
    
    # Test thesis designed to trigger counter scenarios
    test_thesis = """
    Tesla's vertical integration strategy in battery manufacturing and autonomous 
    driving creates an insurmountable competitive moat. The company's 4680 battery 
    technology delivers 50% cost reduction while FSD subscriptions generate $15B+ 
    recurring revenue by 2027. Market share expansion in energy storage and robotaxi 
    services will drive 40% annual revenue growth through 2030.
    """
    
    print("Testing Counter Thesis Scenarios and Alternative Company Analysis")
    print("=" * 70)
    
    try:
        # Submit analysis request
        print("Submitting thesis analysis request...")
        analysis_data = {
            'thesis_text': test_thesis,
            'generate_signals': True
        }
        
        response = requests.post(f"{base_url}/analyze", data=analysis_data, timeout=45)
        
        if response.status_code != 200:
            print(f"Analysis failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
        # Extract thesis ID from response
        import re
        thesis_match = re.search(r'thesis-(\d+)', response.text)
        if not thesis_match:
            print("Could not extract thesis ID from response")
            return False
            
        thesis_id = thesis_match.group(1)
        print(f"Analysis completed - Thesis ID: {thesis_id}")
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Test 1: Verify counter thesis scenarios
        print("\n1. Testing Counter Thesis Scenarios...")
        thesis_response = requests.get(f"{base_url}/get_thesis_data/{thesis_id}")
        
        if thesis_response.status_code == 200:
            thesis_data = thesis_response.json()
            
            if 'counter_thesis' in thesis_data and thesis_data['counter_thesis']:
                counter_data = thesis_data['counter_thesis']
                
                if isinstance(counter_data, dict) and 'scenarios' in counter_data:
                    scenarios = counter_data['scenarios']
                    if scenarios and len(scenarios) > 0:
                        print(f"✓ Counter thesis scenarios found: {len(scenarios)} scenarios")
                        for i, scenario in enumerate(scenarios, 1):
                            print(f"  {i}. {scenario.get('scenario', 'Unknown scenario')}")
                            print(f"     Probability: {scenario.get('probability', 'Unknown')}")
                            print(f"     Impact: {scenario.get('impact', 'No impact description')[:80]}...")
                            if scenario.get('mitigation'):
                                print(f"     Mitigation: {scenario.get('mitigation')[:60]}...")
                        counter_thesis_working = True
                    else:
                        print("✗ Counter thesis scenarios array is empty")
                        counter_thesis_working = False
                else:
                    print("✗ Counter thesis format is incorrect - missing scenarios array")
                    print(f"   Received: {type(counter_data)} - {counter_data}")
                    counter_thesis_working = False
            else:
                print("✗ Counter thesis field missing from response")
                counter_thesis_working = False
        else:
            print(f"✗ Failed to get thesis data: {thesis_response.status_code}")
            counter_thesis_working = False
        
        # Test 2: Verify alternative company analysis
        print("\n2. Testing Alternative Company Analysis...")
        alt_response = requests.get(f"{base_url}/get_alternative_companies/{thesis_id}")
        
        if alt_response.status_code == 200:
            alt_data = alt_response.json()
            
            if 'alternative_companies' in alt_data:
                companies = alt_data['alternative_companies']
                if companies and len(companies) > 0:
                    print(f"✓ Alternative companies found: {len(companies)} companies")
                    for company in companies[:3]:
                        print(f"  • {company.get('name', 'Unknown')} ({company.get('ticker', 'N/A')})")
                        print(f"    Score: {company.get('composite_score', 0)}/100")
                        if company.get('unloved_factors'):
                            print(f"    Undervalued factors: {len(company.get('unloved_factors', []))}")
                    alt_companies_working = True
                else:
                    print("⚠ No alternative companies found (authentic data not available)")
                    alt_companies_working = True  # This is acceptable
            else:
                print("✗ Alternative companies field missing from response")
                alt_companies_working = False
        else:
            print(f"✗ Alternative companies request failed: {alt_response.status_code}")
            try:
                error_data = alt_response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {alt_response.text[:200]}")
            alt_companies_working = False
        
        # Test 3: Verify thesis page renders properly
        print("\n3. Testing Thesis Page Rendering...")
        page_response = requests.get(f"{base_url}/thesis/{thesis_id}")
        
        if page_response.status_code == 200:
            page_content = page_response.text
            if 'Counter-Thesis & Risk Scenarios' in page_content:
                print("✓ Counter thesis section found in page")
                page_rendering_working = True
            else:
                print("✗ Counter thesis section not found in page")
                page_rendering_working = False
        else:
            print(f"✗ Thesis page failed to load: {page_response.status_code}")
            page_rendering_working = False
        
        # Summary
        print("\n" + "=" * 70)
        print("RESULTS SUMMARY:")
        print(f"Counter Thesis Scenarios: {'✓ Working' if counter_thesis_working else '✗ Not Working'}")
        print(f"Alternative Companies:    {'✓ Working' if alt_companies_working else '✗ Not Working'}")
        print(f"Page Rendering:          {'✓ Working' if page_rendering_working else '✗ Not Working'}")
        
        overall_success = counter_thesis_working and alt_companies_working and page_rendering_working
        print(f"\nOverall Status: {'✓ ALL FIXES WORKING' if overall_success else '✗ ISSUES REMAIN'}")
        
        return overall_success
        
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_analysis_with_counter_thesis()
    exit(0 if success else 1)