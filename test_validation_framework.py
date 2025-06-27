"""
Test script to demonstrate the new validation framework structure
"""

from models import ThesisAnalysis
from services.one_pager_service import OnePagerService
from app import app, db

def test_validation_framework():
    """Test the new validation framework structure"""
    with app.app_context():
        # Get the latest thesis
        thesis = ThesisAnalysis.query.order_by(ThesisAnalysis.id.desc()).first()
        
        if not thesis:
            print("No thesis found for testing")
            return
        
        print(f"Testing validation framework for thesis: {thesis.title}")
        
        # Create one pager service
        service = OnePagerService()
        
        # Test individual validation framework components
        print("\n=== Testing Core Claim Validation ===")
        try:
            core_validation = service._build_core_claim_validation(thesis)
            print(f"Primary validators: {len(core_validation.get('primary_validators', []))}")
            print(f"Supporting validators: {len(core_validation.get('supporting_validators', []))}")
            print(f"Validation frequency: {core_validation.get('validation_frequency')}")
            print(f"Success criteria: {core_validation.get('success_criteria')}")
        except Exception as e:
            print(f"Error in core claim validation: {e}")
        
        print("\n=== Testing Assumption Testing Framework ===")
        try:
            assumption_testing = service._build_assumption_testing_framework(thesis)
            print(f"Total assumptions: {assumption_testing.get('total_assumptions')}")
            print(f"Testing methodology: {assumption_testing.get('testing_methodology')}")
        except Exception as e:
            print(f"Error in assumption testing: {e}")
        
        print("\n=== Testing Causal Chain Tracking ===")
        try:
            causal_tracking = service._build_causal_chain_tracking(thesis)
            print(f"Chain length: {causal_tracking.get('chain_length')}")
            print(f"Critical linkages: {len(causal_tracking.get('critical_linkages', []))}")
        except Exception as e:
            print(f"Error in causal chain tracking: {e}")
        
        print("\n=== Testing Data Acquisition Plan ===")
        try:
            data_plan = service._build_data_acquisition_plan(thesis)
            print(f"Primary data sources: {len(data_plan.get('primary_data_sources', []))}")
            print(f"Alternative sources: {len(data_plan.get('alternative_data_sources', []))}")
        except Exception as e:
            print(f"Error in data acquisition plan: {e}")

if __name__ == "__main__":
    test_validation_framework()