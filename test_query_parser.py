"""
Test script for Level 0 Query Parser Service
Demonstrates the parsing logic for structured financial queries
"""

import json
from services.query_parser_service import QueryParserService

def test_query_parser():
    """Test the query parser service with various structured queries"""
    print("Testing Level 0 Query Parser Service")
    print("=" * 50)
    
    parser = QueryParserService()
    
    # Test Case 1: Manager Holdings Query (from the example)
    print("\n1. Testing Manager Holdings Query")
    print("-" * 30)
    
    manager_holdings_query = {
        "entities": ["Microsoft"],
        "relationships": ["manager_holding"],
        "filters": [
            {"field": "market_cap", "operator": ">", "value": 100000000000}
        ],
        "metrics": ["market_cap", "share_count"],
        "sort_by": {"field": "market_cap", "order": "desc"},
        "limit": 5,
        "unsupported_filters": [
            {"field": "dps_cagr_5_yr", "reason": "Not joinable with manager_holding in current data pipeline"}
        ]
    }
    
    result = parser.parse_and_execute_query(
        manager_holdings_query, 
        "Top 5 Manager Holdings Analysis"
    )
    
    print(f"Chat ID: {result.chat_id}")
    print(f"Request ID: {result.request_id}")
    print(f"Number of widgets: {len(result.widgets)}")
    
    if result.widgets:
        widget = result.widgets[0]
        print(f"Quality Score: {widget.get('assessed_quality_score')}")
        print("Generated Response:")
        print(widget.get('generated_markdown_text', '')[:200] + "...")
        print(f"Source References: {len(widget.get('source_references', []))}")
    
    # Test Case 2: Revenue Analysis Query
    print("\n\n2. Testing Revenue Analysis Query")
    print("-" * 30)
    
    revenue_query = {
        "entities": ["NVIDIA"],
        "relationships": [],
        "filters": [
            {"field": "revenue_cagr_5_yr", "operator": ">", "value": 0.15}
        ],
        "metrics": ["revenue", "revenue_cagr_5_yr", "market_cap"],
        "sort_by": {"field": "revenue", "order": "desc"},
        "limit": 10
    }
    
    result = parser.parse_and_execute_query(
        revenue_query, 
        "Revenue Growth Validation"
    )
    
    if result.widgets:
        widget = result.widgets[0]
        print("Generated Response:")
        print(widget.get('generated_markdown_text', '')[:200] + "...")
        print(f"Execution Time: {widget.get('metadata', {}).get('execution_time', 'N/A')}")
    
    # Test Case 3: Market Cap Comparison Query
    print("\n\n3. Testing Market Cap Comparison Query")
    print("-" * 30)
    
    market_cap_query = {
        "entities": ["Apple", "Microsoft", "Google"],
        "relationships": [],
        "filters": [
            {"field": "market_cap", "operator": ">", "value": 1000000000000}
        ],
        "metrics": ["market_cap", "pe", "roic"],
        "sort_by": {"field": "market_cap", "order": "desc"},
        "limit": 5
    }
    
    result = parser.parse_and_execute_query(
        market_cap_query, 
        "Large Cap Technology Comparison"
    )
    
    if result.widgets:
        widget = result.widgets[0]
        print("Generated Response:")
        print(widget.get('generated_markdown_text', '')[:200] + "...")
    
    # Test Case 4: Invalid Query (to test error handling)
    print("\n\n4. Testing Invalid Query (Error Handling)")
    print("-" * 30)
    
    invalid_query = {
        "entities": [],
        "relationships": ["invalid_relationship"],
        "filters": [
            {"field": "invalid_field", "operator": "invalid_op", "value": "test"}
        ],
        "metrics": []
    }
    
    result = parser.parse_and_execute_query(
        invalid_query, 
        "Invalid Query Test"
    )
    
    if result.widgets:
        widget = result.widgets[0]
        print("Error Response:")
        print(widget.get('generated_markdown_text', ''))
        print(f"Quality Score: {widget.get('assessed_quality_score')}")
    
    # Test Case 5: Fund Holdings Query (realistic example)
    print("\n\n5. Testing Fund Holdings Query")
    print("-" * 30)
    
    fund_holdings_query = {
        "entities": ["Meta Platforms"],
        "relationships": ["fund_holding"],
        "filters": [
            {"field": "market_cap", "operator": ">", "value": 5000000000}
        ],
        "metrics": ["market_cap", "share_count"],
        "sort_by": {"field": "market_cap", "order": "desc"},
        "limit": 5
    }
    
    result = parser.parse_and_execute_query(
        fund_holdings_query, 
        "Top 5 Funds Holding Meta Platforms"
    )
    
    if result.widgets:
        widget = result.widgets[0]
        print("Generated Response:")
        print(widget.get('generated_markdown_text', ''))
        
        print("\nSource References:")
        for ref in widget.get('source_references', []):
            metadata = ref.get('source_metadata', {})
            print(f"  • Source: {metadata.get('source', 'Unknown')}")
            print(f"    URL: {metadata.get('reference_url', 'N/A')}")
            print(f"    Date: {metadata.get('publication_date_utc', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("✅ Query Parser Service Test Completed")
    print("✅ All test cases executed successfully")
    print("✅ Demonstrates structured query parsing and execution")
    print("✅ Shows realistic data generation and error handling")

if __name__ == "__main__":
    test_query_parser()