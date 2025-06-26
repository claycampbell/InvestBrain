"""
Test script for Financial Position Extraction Service
Demonstrates the document-based thesis statement generation workflow
"""

import requests
import json
import os
from io import StringIO

def test_financial_position_extraction():
    """Test the complete document-based analysis workflow"""
    
    base_url = "http://localhost:5000"
    
    print("Testing Financial Position Extraction Service")
    print("=" * 50)
    
    # Test 1: Create a sample research document content
    sample_research_content = """
    Investment Thesis: BUY CARR (99% 3-yr base case return): a historically starved business with leading HVAC market 
    share, now regaining its focus on growth (with a Gitlin leading the turnaround).
    
    I view Carrier as a fundamentally undervalued business trading at trough valuations and trough volumes – primarily 
    due to high leverage and partially due to underinvestment in R&D and sales (as a subsidiary of UTC). As management 
    executes on its 3-year supply chain cost-out/reinvestment plan and deleverages, I project a 90% base case return – even 
    on a modest volume rebound (base case assumes 2024 revenues at 2019 levels).
    
    1. HVAC is one of the highest quality building products segments given its non-discretionary nature (people need 
    their A/C!). The industry has relatively less cyclical volumes (70-80% levered to replacement), is experiencing 
    secular tailwinds in its replacement cycle, and has strong pricing power. I project a 5-6% growth CAGR in HVAC 
    from 2020-2024.
    
    2. The business has been starved under UTC and only has room to improve. I am positive on management's plan to 
    drive a focus on growth and to reinvest $300M in R&D and sales (cash from $600M supply chain cost out). I 
    project 0-1% topline growth above market, 12% annualized EBIT growth (assisted by volume rebound).
    
    Price Target: $65 (current: $43)
    Expected Return: 90% over 3 years
    Risk: High leverage, cyclical exposure
    """
    
    # Test the extraction service directly
    try:
        from services.financial_position_extractor import FinancialPositionExtractor
        
        extractor = FinancialPositionExtractor()
        position_data = extractor.extract_financial_position(sample_research_content, "test_document.txt")
        
        print("✓ Financial Position Extraction Test Results:")
        print(f"  Investment Position: {position_data.get('investment_position')}")
        print(f"  Company: {position_data.get('company_name')}")
        print(f"  Confidence: {position_data.get('confidence_level')}")
        print(f"  Thesis Statement: {position_data.get('thesis_statement', '')[:100]}...")
        print(f"  Expected Return: {position_data.get('expected_return')}")
        print(f"  Price Target: {position_data.get('price_target')}")
        print(f"  Key Arguments: {len(position_data.get('key_arguments', []))} arguments")
        print(f"  Risk Factors: {len(position_data.get('risk_factors', []))} risks")
        
    except Exception as e:
        print(f"✗ Financial Position Extraction Test Failed: {e}")
        return
    
    # Test 2: Create a temporary file for document upload test
    test_filename = "test_research_document.txt"
    try:
        with open(test_filename, 'w') as f:
            f.write(sample_research_content)
        
        # Test the complete analysis workflow
        print("\n✓ Testing Complete Document-Based Analysis Workflow")
        
        # Prepare file for upload
        files = {'research_files': open(test_filename, 'rb')}
        data = {'focus_primary_signals': 'on'}
        
        # Test the analyze endpoint
        try:
            response = requests.post(f"{base_url}/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Document-based analysis completed successfully")
                print(f"  Analysis result type: {type(result)}")
                
                if isinstance(result, dict):
                    if 'core_claim' in result:
                        print(f"  Core Claim: {result['core_claim'][:100]}...")
                    if 'extracted_position' in result:
                        pos = result['extracted_position']
                        print(f"  Extracted Position: {pos.get('investment_position')}")
                        print(f"  Company: {pos.get('company_name')}")
                    if 'signals' in result:
                        print(f"  Signals Extracted: {len(result.get('signals', []))}")
                    if 'document_count' in result:
                        print(f"  Documents Processed: {result.get('document_count')}")
                        
            else:
                print(f"✗ Analysis request failed: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("✗ Could not connect to server - ensure the application is running")
        except Exception as e:
            print(f"✗ Analysis workflow test failed: {e}")
        
        finally:
            files['research_files'].close()
            
    except Exception as e:
        print(f"✗ File creation test failed: {e}")
    
    finally:
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
    
    # Test 3: Validate different document types and positions
    print("\n✓ Testing Different Financial Position Types")
    
    test_cases = [
        {
            "content": """
            SELL Recommendation: Target price $25 vs current $45
            Overvalued at current levels with declining fundamentals
            Risk: Significant competition, margin pressure
            """,
            "expected_position": "SELL"
        },
        {
            "content": """
            HOLD rating maintained. Fair value $50, current $48
            Stable business but limited upside near-term
            """,
            "expected_position": "HOLD"
        },
        {
            "content": """
            Bottom-line: I am going to trim my position and rotate some of the proceeds
            This is mainly a portfolio construction-driven trim as opposed to fundamental concerns
            """,
            "expected_position": "TRIM"
        }
    ]
    
    try:
        from services.financial_position_extractor import FinancialPositionExtractor
        extractor = FinancialPositionExtractor()
        
        for i, test_case in enumerate(test_cases, 1):
            position_data = extractor.extract_financial_position(test_case["content"])
            extracted_position = position_data.get('investment_position', 'UNKNOWN')
            expected_position = test_case["expected_position"]
            
            if extracted_position == expected_position:
                print(f"  Test {i}: ✓ Correctly identified {extracted_position}")
            else:
                print(f"  Test {i}: ✗ Expected {expected_position}, got {extracted_position}")
                
    except Exception as e:
        print(f"✗ Position type validation failed: {e}")
    
    print("\n" + "=" * 50)
    print("Financial Position Extraction Testing Complete")
    
    # Display key features
    print("\nKey Features Implemented:")
    print("• Document-based thesis statement extraction")
    print("• AI-powered financial position identification (BUY/SELL/HOLD/TRIM)")
    print("• Price target and return expectation extraction")
    print("• Key arguments and risk factor identification")
    print("• Company name and sector detection")
    print("• Confidence scoring for extraction quality")
    print("• Fallback rule-based extraction when AI fails")
    print("• Integration with existing signal classification system")


if __name__ == "__main__":
    test_financial_position_extraction()