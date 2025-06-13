"""
Data Validation Service for Level 0 Internal Research Signals
Integrates with external API to validate structured queries against real data
"""

import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import requests
from dataclasses import dataclass

@dataclass
class ValidationRequest:
    """Represents a data validation request"""
    request_id: str
    chat_id: str
    callback_url: str
    signal_name: str
    query_structure: Dict[str, Any]
    status: str = 'pending'  # pending, processing, completed, failed
    created_at: datetime = None
    completed_at: datetime = None
    result: Dict[str, Any] = None

class DataValidationService:
    """
    Service for validating Level 0 signals against external data sources
    """
    
    def __init__(self):
        self.api_base_url = "https://iggpt.core-ml-sqa.mle.aws-qa.capgroup.com"
        self.jwt_token = None  # Will be set from environment or user input
        self.active_requests = {}  # Track ongoing validation requests
        
    def set_auth_token(self, token: str):
        """Set the JWT token for API authentication"""
        self.jwt_token = token
        
    def generate_natural_query(self, query_structure: Dict[str, Any], signal_name: str) -> str:
        """
        Convert structured query to natural language for the external API
        """
        entities = query_structure.get('entities', [])
        relationships = query_structure.get('relationships', [])
        filters = query_structure.get('filters', [])
        metrics = query_structure.get('metrics', [])
        limit = query_structure.get('limit', 5)
        
        # Build natural language query based on structure
        if 'holder' in str(relationships).lower() or 'holding' in str(relationships).lower():
            entity_name = entities[0] if entities else "the company"
            if 'fund' in str(relationships).lower():
                return f"Which AMF-eligible funds hold {entity_name}?"
            else:
                return f"List the top {limit} manager holders of {entity_name}"
        
        elif 'revenue' in str(metrics).lower():
            entity_name = entities[0] if entities else "companies"
            return f"Show revenue analysis for {entity_name} with growth metrics"
            
        elif 'market_cap' in str(metrics).lower():
            entity_name = entities[0] if entities else "companies"
            return f"Compare market cap and valuation metrics for {entity_name}"
            
        else:
            entity_name = entities[0] if entities else "target entities"
            metrics_str = ", ".join(metrics[:3]) if metrics else "key metrics"
            return f"Analyze {metrics_str} for {entity_name}"
    
    def initiate_validation(self, query_structure: Dict[str, Any], signal_name: str) -> ValidationRequest:
        """
        Initiate validation request with external API
        """
        try:
            # Generate unique identifiers
            chat_id = f"thesis_validation_{uuid.uuid4().hex[:8]}"
            
            # Convert structured query to natural language
            natural_query = self.generate_natural_query(query_structure, signal_name)
            
            # Prepare API request
            headers = {
                'Content-Type': 'application/json',
                'Cookie': 'AWSALB=w+YW12qqt1LI/Qg368u7YAWZN5HwyHQ7gwk2kcfPs4T8Ym28bA6JwOg0SVsmvZAoTqdXiddDuEEXULq0zP8mccguPG2orfvLHEVmWDrEkwuR3RN/+b25w3CrAepE; AWSALBCORS=w+YW12qqt1LI/Qg368u7YAWZN5HwyHQ7gwk2kcfPs4T8Ym28bA6JwOg0SVsmvZAoTqdXiddDuEEXULq0zP8mccguPG2orfvLHEVmWDrEkwuR3RN/+b25w3CrAepE'
            }
            
            if self.jwt_token:
                headers['Authorization'] = f'Bearer {self.jwt_token}'
            
            payload = {
                'query': natural_query,
                'chat_id': chat_id
            }
            
            # Make initial request to start validation
            response = requests.post(
                f"{self.api_base_url}/api/query/structured/start",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Create validation request object
                validation_request = ValidationRequest(
                    request_id=result.get('request_id'),
                    chat_id=result.get('chat_id'),
                    callback_url=result.get('callback_url'),
                    signal_name=signal_name,
                    query_structure=query_structure,
                    status='processing',
                    created_at=datetime.now(timezone.utc)
                )
                
                # Store request for tracking
                self.active_requests[validation_request.request_id] = validation_request
                
                logging.info(f"Initiated validation for signal: {signal_name}")
                logging.info(f"Request ID: {validation_request.request_id}")
                logging.info(f"Callback URL: {validation_request.callback_url}")
                
                return validation_request
                
            else:
                # Handle API error
                logging.error(f"API request failed: {response.status_code} - {response.text}")
                return ValidationRequest(
                    request_id=f"error_{uuid.uuid4().hex[:8]}",
                    chat_id=chat_id,
                    callback_url="",
                    signal_name=signal_name,
                    query_structure=query_structure,
                    status='failed',
                    created_at=datetime.now(timezone.utc),
                    result={'error': f"API request failed: {response.status_code}"}
                )
                
        except Exception as e:
            logging.error(f"Error initiating validation: {str(e)}")
            return ValidationRequest(
                request_id=f"error_{uuid.uuid4().hex[:8]}",
                chat_id=f"error_{uuid.uuid4().hex[:8]}",
                callback_url="",
                signal_name=signal_name,
                query_structure=query_structure,
                status='failed',
                created_at=datetime.now(timezone.utc),
                result={'error': str(e)}
            )
    
    def check_validation_status(self, validation_request: ValidationRequest) -> ValidationRequest:
        """
        Check the status of a validation request using the callback URL
        """
        try:
            if not validation_request.callback_url:
                validation_request.status = 'failed'
                validation_request.result = {'error': 'No callback URL available'}
                return validation_request
            
            headers = {}
            if self.jwt_token:
                headers['Authorization'] = f'Bearer {self.jwt_token}'
            
            # Poll the callback URL for results
            response = requests.get(
                validation_request.callback_url,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we have widgets (indicating completion)
                if result.get('widgets'):
                    validation_request.status = 'completed'
                    validation_request.completed_at = datetime.now(timezone.utc)
                    validation_request.result = result
                    logging.info(f"Validation completed for: {validation_request.signal_name}")
                else:
                    # Still processing
                    validation_request.status = 'processing'
                    
            elif response.status_code == 202:
                # Still processing
                validation_request.status = 'processing'
                
            else:
                # Error occurred
                validation_request.status = 'failed'
                validation_request.result = {
                    'error': f"Status check failed: {response.status_code}",
                    'response': response.text[:200]
                }
                
        except Exception as e:
            logging.error(f"Error checking validation status: {str(e)}")
            validation_request.status = 'failed'
            validation_request.result = {'error': str(e)}
            
        return validation_request
    
    def get_validation_result(self, request_id: str) -> Optional[ValidationRequest]:
        """
        Get the current status and result of a validation request
        """
        validation_request = self.active_requests.get(request_id)
        if not validation_request:
            return None
            
        # Update status if still processing
        if validation_request.status == 'processing':
            validation_request = self.check_validation_status(validation_request)
            self.active_requests[request_id] = validation_request
            
        return validation_request
    
    def simulate_validation_result(self, query_structure: Dict[str, Any], signal_name: str) -> Dict[str, Any]:
        """
        Simulate a validation result for testing when API is not available
        This returns the expected format from the external API
        """
        entities = query_structure.get('entities', ['Target Company'])
        entity_name = entities[0] if entities else 'Target Company'
        
        return {
            "chat_id": f"chat_{uuid.uuid4().hex[:8]}",
            "disclaimer_messages": None,
            "request_id": f"coreml:iggpt:request:{uuid.uuid4()}",
            "widgets": [
                {
                    "assessed_quality_score": 0.92,
                    "chat_id": f"chat_{uuid.uuid4().hex[:8]}",
                    "generated_markdown_text": f"Here are the validation results for {signal_name}:\n\n1. **{entity_name}**: Market Value - $7,873,091,706.24\n2. **Fund A**: Market Value - $6,366,638,141.28\n3. **Fund B**: Market Value - $5,549,679,094.32\n4. **Fund C**: Market Value - $5,355,178,440.48\n5. **Fund D**: Market Value - $4,110,695,004.24\n\nValidation confirms the structured query executed successfully against live data.",
                    "generation_time_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                    "metadata": {
                        "signal_name": signal_name,
                        "validation_source": "Internal Research Database",
                        "query_structure": query_structure
                    },
                    "referenced_query": signal_name,
                    "request_id": f"coreml:iggpt:request:{uuid.uuid4()}",
                    "source_references": [
                        {
                            "id": f"data_provider_validation_{uuid.uuid4()}",
                            "relevant_content": None,
                            "source_metadata": {
                                "audience": None,
                                "authors": None,
                                "content_length": None,
                                "publication_date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                "reference_url": f"https://ig-portal-qa.capgroup.com/validation/{entity_name}",
                                "source": "Portal Data",
                                "tags": {
                                    "entity": entity_name,
                                    "validation_type": "structured_query",
                                    "last_update": datetime.now(timezone.utc).strftime("%Y-%m-%d")
                                }
                            },
                            "source_type": "url"
                        }
                    ],
                    "source_remote_reference": [],
                    "validation_scores": {
                        "data_quality": 0.92,
                        "completeness": 0.89,
                        "timeliness": 0.95
                    },
                    "widget_id": f"coreml:iggpt:widget:{uuid.uuid4()}"
                }
            ]
        }
    
    def process_validation_async(self, request_id: str, max_wait_time: int = 60):
        """
        Process validation asynchronously with polling
        """
        validation_request = self.active_requests.get(request_id)
        if not validation_request:
            return None
            
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            validation_request = self.check_validation_status(validation_request)
            self.active_requests[request_id] = validation_request
            
            if validation_request.status in ['completed', 'failed']:
                break
                
            time.sleep(5)  # Wait 5 seconds before next check
            
        return validation_request