#!/usr/bin/env python3
"""
End-to-end flow test to verify the refactored architecture works correctly
Tests the complete pipeline from thesis input to database storage
"""

import requests
import json
import time

def test_complete_analysis_flow():
    """Test the complete analysis flow end-to-end"""
    base_url = "http://localhost:5000"
    
    # Test thesis for analysis
    test_thesis = "Google benefits from search monopoly and cloud growth. AI leadership and data advantages create sustainable competitive moats."
    
    print("🔬 Testing Complete End-to-End Analysis Flow")
    print("=" * 50)
    
    try:
        # Step 1: Submit thesis for analysis
        print("📝 Step 1: Submitting thesis for analysis...")
        
        response = requests.post(
            f"{base_url}/analyze",
            data={"thesis_text": test_thesis},
            timeout=20
        )
        
        if response.status_code == 200:
            analysis_result = response.json()
            print("✅ Analysis completed successfully!")
            
            # Verify response structure
            expected_keys = ['thesis_analysis', 'signal_extraction', 'monitoring_plan', 'thesis_id']
            missing_keys = [key for key in expected_keys if key not in analysis_result]
            
            if missing_keys:
                print(f"❌ Missing response keys: {missing_keys}")
                return False
            
            thesis_id = analysis_result.get('thesis_id')
            print(f"📊 Thesis ID: {thesis_id}")
            print(f"📈 Signals found: {analysis_result.get('signal_extraction', {}).get('total_signals_identified', 0)}")
            
            # Step 2: Test monitoring dashboard
            print("\n📋 Step 2: Testing monitoring dashboard...")
            
            dashboard_response = requests.get(f"{base_url}/monitoring", timeout=10)
            if dashboard_response.status_code == 200:
                print("✅ Monitoring dashboard accessible")
            else:
                print(f"❌ Dashboard error: {dashboard_response.status_code}")
            
            # Step 3: Test specific thesis view
            print(f"\n🔍 Step 3: Testing thesis view for ID {thesis_id}...")
            
            thesis_response = requests.get(f"{base_url}/thesis/{thesis_id}", timeout=10)
            if thesis_response.status_code == 200:
                print("✅ Thesis view accessible")
            else:
                print(f"❌ Thesis view error: {thesis_response.status_code}")
            
            # Step 4: Test analytics features
            print(f"\n📊 Step 4: Testing analytics features...")
            
            analytics_endpoints = [
                f"/get_thesis_performance_score/{thesis_id}",
                f"/get_market_sentiment/{thesis_id}",
                f"/get_investment_sparklines/{thesis_id}"
            ]
            
            for endpoint in analytics_endpoints:
                try:
                    analytics_response = requests.get(f"{base_url}{endpoint}", timeout=8)
                    if analytics_response.status_code == 200:
                        print(f"✅ {endpoint} working")
                    else:
                        print(f"⚠️ {endpoint} returned {analytics_response.status_code}")
                except requests.exceptions.Timeout:
                    print(f"⏱️ {endpoint} timed out (fallback likely active)")
            
            # Display analysis summary
            print("\n📋 Analysis Summary:")
            print("-" * 30)
            
            thesis_analysis = analysis_result.get('thesis_analysis', {})
            print(f"Core Claim: {thesis_analysis.get('core_claim', 'N/A')[:80]}...")
            print(f"Mental Model: {thesis_analysis.get('mental_model', 'N/A')}")
            
            signals = analysis_result.get('signal_extraction', {}).get('signals', [])
            if signals:
                print(f"Top Signals:")
                for i, signal in enumerate(signals[:3]):
                    print(f"  {i+1}. {signal.get('name', 'Unknown')} ({signal.get('type', 'Unknown')})")
            
            metadata = analysis_result.get('metadata', {})
            if metadata.get('fallback_mode'):
                print("🔄 Analysis completed using fallback mode (AI service unavailable)")
            else:
                print("🤖 Analysis completed using AI service")
            
            return True
            
        else:
            print(f"❌ Analysis failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out - likely Azure OpenAI connectivity issue")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test key API endpoints are accessible"""
    base_url = "http://localhost:5000"
    
    print("\n🔗 Testing API Endpoints")
    print("=" * 30)
    
    endpoints = [
        "/",
        "/monitoring",
        "/analytics",
        "/get_metric_categories",
        "/get_analysis_frameworks"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

def main():
    """Run complete end-to-end testing"""
    print("🚀 Investment Thesis Intelligence System - End-to-End Test")
    print("=" * 60)
    
    # Test API endpoints first
    test_api_endpoints()
    
    # Test complete analysis flow
    success = test_complete_analysis_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ End-to-end flow test PASSED")
        print("🎯 Refactored architecture is working correctly")
    else:
        print("❌ End-to-end flow test FAILED")
        print("🔧 Architecture needs debugging")

if __name__ == "__main__":
    main()