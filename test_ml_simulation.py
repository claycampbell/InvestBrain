#!/usr/bin/env python3
"""
Test ML Simulation Service without network dependencies
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ml_simulation_service import MLSimulationService

def test_ml_simulation():
    """Test ML simulation with intelligent fallback"""
    print("Testing ML Simulation Service...")
    
    # Create a mock thesis object
    class MockThesis:
        def __init__(self):
            self.core_claim = "NVIDIA Corp is positioned for strong growth driven by AI demand and data center expansion. Expected 25% annual growth with market leadership in GPU technology."
            self.original_thesis = "Investment thesis on NVIDIA focusing on AI market opportunities"
            self.mental_model = "Growth"
    
    # Initialize the service
    service = MLSimulationService()
    
    # Test parameters
    thesis = MockThesis()
    time_horizon = 2  # 2 years
    scenario = "bull"
    volatility = "moderate"
    include_events = True
    
    try:
        print(f"Running simulation for {time_horizon} year horizon under {scenario} scenario...")
        
        # Run the simulation
        result = service.generate_thesis_simulation(
            thesis, time_horizon, scenario, volatility, include_events
        )
        
        if 'error' in result:
            print(f"ERROR: {result['message']}")
            return False
        
        # Validate results
        performance_data = result.get('performance_data', {})
        market_prices = performance_data.get('market_performance', [])
        thesis_prices = performance_data.get('thesis_performance', [])
        
        print(f"✓ Market prices generated: {len(market_prices)} data points")
        print(f"✓ Thesis prices generated: {len(thesis_prices)} data points")
        
        if market_prices and thesis_prices:
            final_market = market_prices[-1]
            final_thesis = thesis_prices[-1]
            initial_market = market_prices[0]
            initial_thesis = thesis_prices[0]
            
            market_return = ((final_market / initial_market) - 1) * 100
            thesis_return = ((final_thesis / initial_thesis) - 1) * 100
            
            print(f"✓ Market return: {market_return:.1f}%")
            print(f"✓ Thesis return: {thesis_return:.1f}%")
        
        # Check events
        events = result.get('events', [])
        print(f"✓ Events generated: {len(events)}")
        
        # Check scenario analysis
        scenario_analysis = result.get('scenario_analysis', {})
        print(f"✓ Scenario analysis: {scenario_analysis.get('conviction_level', 'N/A')}")
        
        print("\n✅ ML Simulation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_simulation()
    sys.exit(0 if success else 1)