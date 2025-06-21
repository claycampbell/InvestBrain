"""
Test Eagle API Response Generator
Creates realistic test responses matching the Eagle API schema for frontend validation
"""

import json
from typing import Dict, Any, List

class TestEagleAPIResponses:
    """Generate test responses matching Eagle API schema for frontend validation"""
    
    def __init__(self):
        # Common financial metrics from Eagle API
        self.metric_templates = {
            # Cash Flow Metrics
            "ciq_fcf_usd_cagr_floating_ltm_to_ntm_plus_8": {"range": (0.05, 0.25), "format": "decimal"},
            "ciq_fcf_per_share_usd_cagr_floating_ltm_to_ntm_plus_4": {"range": (0.08, 0.20), "format": "decimal"},
            "ciq_fcf_yield_floating_ltm": {"range": (0.03, 0.12), "format": "decimal"},
            
            # Revenue Metrics
            "ciq_rps_usd_cagr_floating_ltm_to_ntm_plus_4": {"range": (0.10, 0.35), "format": "decimal"},
            "ciq_revenue_usd_cagr_floating_ltm_to_ntm_plus_8": {"range": (0.12, 0.28), "format": "decimal"},
            "ciq_revenue_ttm_usd": {"range": (50000000000, 200000000000), "format": "integer"},
            
            # Profitability Metrics
            "ciq_ebitda_margin_floating_ltm": {"range": (0.15, 0.45), "format": "decimal"},
            "ciq_operating_margin_floating_ltm": {"range": (0.10, 0.35), "format": "decimal"},
            "ciq_net_margin_floating_ltm": {"range": (0.08, 0.25), "format": "decimal"},
            
            # Valuation Metrics
            "ciq_pe_ratio_floating_ltm": {"range": (15, 45), "format": "decimal"},
            "ciq_ev_ebitda_floating_ltm": {"range": (8, 25), "format": "decimal"},
            "ciq_price_to_book_floating_ltm": {"range": (2, 12), "format": "decimal"},
            
            # Growth Metrics
            "ciq_eps_usd_cagr_floating_ltm_to_ntm_plus_4": {"range": (0.15, 0.40), "format": "decimal"},
            "ciq_book_value_per_share_cagr_floating_ltm_to_ntm_plus_4": {"range": (0.08, 0.22), "format": "decimal"},
            
            # Efficiency Metrics
            "ciq_roa_floating_ltm": {"range": (0.05, 0.20), "format": "decimal"},
            "ciq_roe_floating_ltm": {"range": (0.12, 0.35), "format": "decimal"},
            "ciq_roic_floating_ltm": {"range": (0.10, 0.30), "format": "decimal"}
        }
    
    def generate_nvidia_response(self) -> Dict[str, Any]:
        """Generate test response for NVIDIA (NVDA, SEDOL: 2379504)"""
        import random
        
        # Select 8-12 metrics for realistic response
        selected_metrics = random.sample(list(self.metric_templates.keys()), 10)
        
        metrics = []
        for metric_name in selected_metrics:
            template = self.metric_templates[metric_name]
            if template["format"] == "decimal":
                value = round(random.uniform(*template["range"]), 6)
            else:
                value = random.randint(*template["range"])
            
            metrics.append({
                "name": metric_name,
                "value": str(value)
            })
        
        return {
            "data": {
                "financialMetrics": [
                    {
                        "metrics": metrics
                    }
                ]
            }
        }
    
    def generate_apple_response(self) -> Dict[str, Any]:
        """Generate test response for Apple (AAPL, SEDOL: 2046251)"""
        import random
        
        # Apple-specific metric selection (focus on revenue and profitability)
        apple_metrics = [
            "ciq_rps_usd_cagr_floating_ltm_to_ntm_plus_4",
            "ciq_revenue_ttm_usd",
            "ciq_ebitda_margin_floating_ltm",
            "ciq_operating_margin_floating_ltm",
            "ciq_net_margin_floating_ltm",
            "ciq_pe_ratio_floating_ltm",
            "ciq_fcf_yield_floating_ltm",
            "ciq_roe_floating_ltm",
            "ciq_roic_floating_ltm"
        ]
        
        metrics = []
        for metric_name in apple_metrics:
            template = self.metric_templates[metric_name]
            if template["format"] == "decimal":
                # Apple typically has higher margins
                min_val, max_val = template["range"]
                adjusted_min = min_val * 1.2
                adjusted_max = max_val * 1.1
                value = round(random.uniform(adjusted_min, adjusted_max), 6)
            else:
                value = random.randint(*template["range"]) * 2  # Higher revenue
            
            metrics.append({
                "name": metric_name,
                "value": str(value)
            })
        
        return {
            "data": {
                "financialMetrics": [
                    {
                        "metrics": metrics
                    }
                ]
            }
        }
    
    def generate_microsoft_response(self) -> Dict[str, Any]:
        """Generate test response for Microsoft (MSFT, SEDOL: 2588173)"""
        import random
        
        # Microsoft-specific metrics (cloud growth focus)
        msft_metrics = [
            "ciq_revenue_usd_cagr_floating_ltm_to_ntm_plus_8",
            "ciq_fcf_usd_cagr_floating_ltm_to_ntm_plus_8",
            "ciq_eps_usd_cagr_floating_ltm_to_ntm_plus_4",
            "ciq_operating_margin_floating_ltm",
            "ciq_fcf_yield_floating_ltm",
            "ciq_pe_ratio_floating_ltm",
            "ciq_ev_ebitda_floating_ltm",
            "ciq_roa_floating_ltm",
            "ciq_roe_floating_ltm"
        ]
        
        metrics = []
        for metric_name in msft_metrics:
            template = self.metric_templates[metric_name]
            if template["format"] == "decimal":
                value = round(random.uniform(*template["range"]), 6)
            else:
                value = random.randint(*template["range"])
            
            metrics.append({
                "name": metric_name,
                "value": str(value)
            })
        
        return {
            "data": {
                "financialMetrics": [
                    {
                        "metrics": metrics
                    }
                ]
            }
        }
    
    def generate_empty_response(self) -> Dict[str, Any]:
        """Generate empty response for testing error states"""
        return {
            "data": {
                "financialMetrics": [
                    {
                        "metrics": []
                    }
                ]
            }
        }
    
    def generate_error_response(self) -> Dict[str, Any]:
        """Generate error response for testing error handling"""
        return {
            "errors": [
                {
                    "message": "Company not found",
                    "extensions": {
                        "code": "COMPANY_NOT_FOUND"
                    }
                }
            ]
        }
    
    def get_test_response_for_company(self, ticker: str = None, sedol_id: str = None) -> Dict[str, Any]:
        """Get appropriate test response based on company identifier"""
        if ticker:
            ticker = ticker.upper()
            if ticker == "NVDA" or sedol_id == "2379504":
                return self.generate_nvidia_response()
            elif ticker == "AAPL" or sedol_id == "2046251":
                return self.generate_apple_response()
            elif ticker == "MSFT" or sedol_id == "2588173":
                return self.generate_microsoft_response()
        
        # Default to NVIDIA response for unknown companies
        return self.generate_nvidia_response()
    
    def validate_response_schema(self, response: Dict[str, Any]) -> bool:
        """Validate that response matches Eagle API schema"""
        try:
            # Check top-level structure
            if "data" not in response:
                return False
            
            data = response["data"]
            if "financialMetrics" not in data:
                return False
            
            financial_metrics = data["financialMetrics"]
            if not isinstance(financial_metrics, list):
                return False
            
            # Check each financial metric object
            for metric_obj in financial_metrics:
                if "metrics" not in metric_obj:
                    return False
                
                metrics = metric_obj["metrics"]
                if not isinstance(metrics, list):
                    return False
                
                # Check each metric
                for metric in metrics:
                    if "name" not in metric or "value" not in metric:
                        return False
                    
                    if not isinstance(metric["name"], str) or not isinstance(metric["value"], str):
                        return False
            
            return True
        except Exception:
            return False

# Example usage for testing
def main():
    """Test the Eagle API response generator"""
    test_api = TestEagleAPIResponses()
    
    # Generate test responses
    nvidia_response = test_api.generate_nvidia_response()
    apple_response = test_api.generate_apple_response()
    microsoft_response = test_api.generate_microsoft_response()
    
    # Validate schemas
    print("NVIDIA Response Valid:", test_api.validate_response_schema(nvidia_response))
    print("Apple Response Valid:", test_api.validate_response_schema(apple_response))
    print("Microsoft Response Valid:", test_api.validate_response_schema(microsoft_response))
    
    # Print sample response
    print("\nSample NVIDIA Response:")
    print(json.dumps(nvidia_response, indent=2))

if __name__ == "__main__":
    main()