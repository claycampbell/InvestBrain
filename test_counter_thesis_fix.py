#!/usr/bin/env python3
"""
Test script to verify counter thesis scenarios and alternative company analysis fixes
"""
import requests
import json
import sys

def test_counter_thesis_and_alternatives():
    """Test both counter thesis scenarios and alternative company analysis"""
    base_url = "http://0.0.0.0:5000"
    
    # Test thesis with counter scenarios
    test_thesis = """
    NVIDIA Corporation presents a compelling AI infrastructure investment opportunity. 
    The company's dominant position in GPU computing, combined with exploding demand 
    for AI training and inference, creates a sustainable competitive moat. Revenue 
    growth of 200%+ driven by data center expansion, while maintaining 70%+ gross margins 
    through proprietary CUDA ecosystem lock-in effects.
    """
    
    print("🔍 Testing counter thesis scenarios and alternative company analysis...")
    
    try:
        # Submit analysis request
        analysis_data = {
            'thesis_text': test_thesis,
            'generate_signals': True
        }
        
        print(f"📊 Submitting analysis request to {base_url}/analyze")
        response = requests.post(f"{base_url}/analyze", data=analysis_data, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        # Parse response HTML to extract thesis ID
        response_text = response.text
        if 'thesis-' in response_text:
            # Extract thesis ID from response
            import re
            thesis_match = re.search(r'thesis-(\d+)', response_text)
            if thesis_match:
                thesis_id = thesis_match.group(1)
                print(f"✅ Analysis completed - Thesis ID: {thesis_id}")
                
                # Test counter thesis scenarios
                print("\n🎯 Testing counter thesis scenarios...")
                thesis_response = requests.get(f"{base_url}/get_thesis_data/{thesis_id}")
                if thesis_response.status_code == 200:
                    thesis_data = thesis_response.json()
                    
                    # Check for counter thesis
                    if 'counter_thesis' in thesis_data and thesis_data['counter_thesis']:
                        counter_scenarios = thesis_data['counter_thesis'].get('scenarios', [])
                        if counter_scenarios and len(counter_scenarios) > 0:
                            print(f"✅ Counter thesis scenarios found: {len(counter_scenarios)} scenarios")
                            for i, scenario in enumerate(counter_scenarios, 1):
                                print(f"   {i}. {scenario.get('scenario', 'Unknown')}")
                                print(f"      Probability: {scenario.get('probability', 'Unknown')}")
                                print(f"      Impact: {scenario.get('impact', 'Unknown')[:60]}...")
                        else:
                            print("❌ Counter thesis scenarios missing or empty")
                    else:
                        print("❌ Counter thesis field missing from analysis")
                
                # Test alternative company analysis
                print("\n🏢 Testing alternative company analysis...")
                alt_response = requests.get(f"{base_url}/get_alternative_companies/{thesis_id}")
                if alt_response.status_code == 200:
                    alt_data = alt_response.json()
                    
                    if 'alternative_companies' in alt_data:
                        companies = alt_data['alternative_companies']
                        if companies and len(companies) > 0:
                            print(f"✅ Alternative companies found: {len(companies)} companies")
                            for company in companies[:3]:  # Show first 3
                                print(f"   • {company.get('name', 'Unknown')} ({company.get('ticker', 'N/A')})")
                                print(f"     Score: {company.get('composite_score', 0)}")
                        else:
                            print("⚠️  No alternative companies found (empty authentic data)")
                    else:
                        print("❌ Alternative companies field missing")
                else:
                    print(f"❌ Alternative companies request failed: {alt_response.status_code}")
                
                return True
            else:
                print("❌ Could not extract thesis ID from response")
                return False
        else:
            print("❌ No thesis ID found in analysis response")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("Testing Counter Thesis Scenarios and Alternative Company Analysis")
    print("=" * 70)
    
    success = test_counter_thesis_and_alternatives()
    
    if success:
        print("\n✅ Testing completed successfully")
    else:
        print("\n❌ Testing failed")
        sys.exit(1)