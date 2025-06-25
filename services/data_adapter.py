from datetime import datetime
"""
Data Adapter Service - Handles interactions with external data sources

Required Environment Variables:
    EAGLE_API_TOKEN: Authentication token for Eagle API
    EAGLE_ENTITY_ID: Entity ID for querying data (defaults to BDRXDB4)
    EAGLE_ENTITY_TYPE: Entity type for the ID (defaults to SEDOL)
"""

import requests
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import json
import re


class DataAdapter:
    """Adapter for handling data source interactions"""

    def __init__(self):
        """Initialize the adapter with configuration from environment variables"""
        load_dotenv()
        self.eagle_url = "https://eagle-gamma.capgroup.com/svc-backend/graphql"
        self.token = os.getenv('AZURE_OPENAI_TOKEN')
        self.entity_id = os.getenv('EAGLE_ENTITY_ID', 'BDRXDB4')
        self.entity_type = os.getenv('EAGLE_ENTITY_TYPE', 'SEDOL')

        # Check required configuration
        if not self.token:
            raise EnvironmentError(
                "EAGLE_API_TOKEN environment variable is required")

        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }

    def validate_period(self, period: Optional[str] = None) -> str:
        """
        Validate and normalize the period parameter.

        Supported formats:
        - CY_YYYY: Calendar year (e.g., CY_2024)
        - FY_YYYY: Fiscal year (e.g., FY_2024)
        - LTM: Last twelve months
        - LTM-N: Last twelve months offset by N quarters (e.g., LTM-4)
        - NTM: Next twelve months
        - FLOATING-NTM: Floating next twelve months
        - FLOATING-LTM: Floating last twelve months
        - QN_CY_YYYY: Calendar year quarter (e.g., Q1_CY_2024)

        Returns:
            str: Validated period string or 'LTM' if None provided

        Raises:
            ValueError: If period format is invalid
        """
        if not period:
            return 'LTM'  # Default to LTM for backward compatibility

        # Define regex patterns for validation
        patterns = {
            r'^CY_\d{4}$': 'Calendar Year',
            r'^FY_\d{4}$': 'Fiscal Year',
            r'^LTM$': 'Last Twelve Months',
            r'^LTM-(?:4|8|12)$': 'Last Twelve Months with Offset',
            r'^NTM$': 'Next Twelve Months',
            r'^FLOATING-(?:NTM|LTM)$': 'Floating Twelve Months',
            r'^Q[1-4]_CY_\d{4}$': 'Calendar Year Quarter'
        }

        for pattern, description in patterns.items():
            if re.match(pattern, period):
                return period

        valid_formats = [
            "CY_YYYY (e.g., CY_2024)", "FY_YYYY (e.g., FY_2024)", "LTM",
            "LTM-4, LTM-8, LTM-12", "NTM", "FLOATING-NTM, FLOATING-LTM",
            "Q1_CY_YYYY through Q4_CY_YYYY"
        ]
        raise ValueError(f"Invalid period format. Supported formats:\n" +
                         "\n".join(valid_formats))

    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a GraphQL query and return results"""
        try:
            # Debug log the query
            print(f"Executing Eagle API Query:\n{query}")

            # Debug: print headers (redact token for security)
            redacted_headers = dict(self.headers)
            if 'Authorization' in redacted_headers:
                redacted_headers['Authorization'] = 'Bearer [REDACTED]'
            print(
                f"Eagle API Request Headers: {json.dumps(redacted_headers, indent=2)}"
            )
            response = requests.post(
                self.eagle_url,
                headers=self.headers,
                json={'query': query},
                verify=False  # Ignore SSL certificate verification
            )

            # Debug log the response
            print(f"Eagle API Response Status: {response.status_code}")
            print(f"Eagle API Response: {response.text[:1000]}")

            if response.status_code == 200:
                result = response.json()

                # Check for API errors
                if 'errors' in result:
                    error_msgs = [
                        f"- {error.get('message', 'Unknown error')}"
                        for error in result['errors']
                    ]
                    error_str = "\n".join(error_msgs)
                    return {
                        'success': False,
                        'error': f"Eagle API Errors: {error_str}"
                    }

                # Process results
                if 'data' in result and 'financialMetrics' in result['data']:
                    metrics_data = result['data']['financialMetrics']
                    metrics_values = {}

                    # Extract metric values
                    if metrics_data and metrics_data[0].get('metrics'):
                        for metric in metrics_data[0]['metrics']:
                            if metric['value'] is not None:
                                metrics_values[
                                    metric['name']] = metric['value']

                    return {
                        'success': True,
                        'metrics': metrics_values,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No financial metrics found in response'
                    }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'details': response.text
                }

        except Exception as e:
            raise Exception(f"Eagle API Request Error: {str(e)}")

    def fetch_metric_values(self,
                            metrics: List[str],
                            period: Optional[str] = None,
                            sedol_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch values for specific metrics for a given period and SEDOL.

        Args:
            metrics: List of metric names to fetch
            period: Optional period specification. If not provided, defaults to LTM.
                    See validate_period() docstring for supported formats.
            sedol_id: SEDOL identifier for the company. Required for Eagle API queries.

        Returns:
            Dict mapping metric names to their values, or error if SEDOL is missing
        """
        # Validate period format
        period = self.validate_period(period)

        # Use SEDOL as the only valid entity type for Eagle API
        if sedol_id:
            entity_id = sedol_id
            entity_type = "SEDOL"
        else:
            return {
                "success": False,
                "error": "SEDOL identifier is required for Eagle API queries."
            }

        # Format metrics as a GraphQL-compatible string
        metrics_str = ",".join(
            ['{name: "' + metric + '"}' for metric in metrics])

        # Build query using SEDOL
        query = """
        query FinancialMetrics {
          financialMetrics(
            entityIds: [
              {id: "%s", type: %s}
            ],
            metricIds: [
              %s
            ]
          ) {
            entityId {
              id
            }
            metrics {
              name
              value
              period
            }
          }
        }
        """ % (entity_id, entity_type, metrics_str)

        return self.execute_query(query)

    def fetch_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """Fetch metadata for a document"""
        return {
            'id': document_id,
            'type': 'financial_report',
            'date': '2025-06-20',
            'status': 'active'
        }


if __name__ == "__main__":
    adapter = DataAdapter()

    # Test fetching some metrics
    test_metrics = [
        "revenue_growth_this_yr", "operating_margin_this_yr",
        "net_margin_this_yr"
    ]

    # Test with different periods
    periods = ['LTM', 'CY_2024', 'Q1_CY_2024', 'FY_2024']

    for period in periods:
        print(f"\nTesting metrics for period: {period}")
        try:
            results = adapter.fetch_metric_values(test_metrics, period)
            print(json.dumps(results, indent=2))
        except ValueError as e:
            print(f"Error: {str(e)}")
