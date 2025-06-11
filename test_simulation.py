#!/usr/bin/env python3
"""
Test script for the simulation service to verify Azure OpenAI integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.simulation_service import SimulationService
import json

def test_simulation():
    # Create a mock thesis object
    class MockThesis:
        def __init__(self):
            self.title = "NVIDIA AI Growth Thesis"
            self.core_claim = "NVIDIA is positioned to benefit from AI chip demand growth over the next 3-5 years"
            self.signals = []
    
    # Initialize service
    simulation_service = SimulationService()
    
    # Test parameters
    thesis = MockThesis()
    time_horizon = 3
    scenario = "bull"
    volatility = "moderate"
    include_events = True
    simulation_type = "comprehensive"
    
    print("Testing Azure OpenAI simulation generation...")
    print(f"Thesis: {thesis.title}")
    print(f"Time horizon: {time_horizon} years")
    print(f"Scenario: {scenario}")
    print(f"Volatility: {volatility}")
    print("-" * 50)
    
    try:
        # Generate simulation
        result = simulation_service.generate_simulation(
            thesis, time_horizon, scenario, volatility, include_events, simulation_type
        )
        
        print("✅ Simulation generated successfully!")
        print(f"Performance data points: {len(result['chart_data']['performance_data'])}")
        print(f"Timeline labels: {len(result['chart_data']['timeline'])}")
        print(f"Events generated: {len(result['events'])}")
        
        # Show sample data
        performance = result['chart_data']['performance_data']
        print(f"Initial value: {performance[0]}")
        print(f"Final value: {performance[-1]}")
        print(f"Total return: {((performance[-1] / performance[0]) - 1) * 100:.1f}%")
        
        # Show events
        print("\nGenerated Events:")
        for event in result['events'][:3]:  # Show first 3 events
            print(f"- {event['date']}: {event['title']} ({event['impact_type']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simulation()