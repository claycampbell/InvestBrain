"""
Data Manager - Centralized data access and external service management
All data connections and external APIs are managed through this module
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from app import db
from models import ThesisAnalysis, SignalMonitoring, DocumentUpload


class DataManager:
    """Centralized manager for all data operations and external services"""
    
    def __init__(self):
        self.eagle_api_available = bool(os.environ.get('EAGLE_API_TOKEN'))
        self.factset_api_available = bool(os.environ.get('FACTSET_API_KEY'))
        self.xpressfeed_api_available = bool(os.environ.get('XPRESSFEED_API_KEY'))
        
        # Initialize data adapters
        self._init_data_adapters()
    
    def _init_data_adapters(self):
        """Initialize external data service adapters"""
        try:
            from services.data_adapter_service import DataAdapter
            self.data_adapter = DataAdapter()
        except Exception as e:
            logging.warning(f"Data adapter initialization failed: {str(e)}")
            self.data_adapter = None
    
    # Database Operations
    def save_thesis_analysis(self, thesis_data: Dict[str, Any]) -> int:
        """Save thesis analysis to database"""
        try:
            thesis = ThesisAnalysis(
                title=thesis_data.get('title', 'Investment Thesis Analysis'),
                original_thesis=thesis_data.get('original_thesis', ''),
                core_claim=thesis_data.get('core_claim', ''),
                core_analysis=thesis_data.get('core_analysis', ''),
                causal_chain=thesis_data.get('causal_chain', []),
                assumptions=thesis_data.get('assumptions', []),
                mental_model=thesis_data.get('mental_model', ''),
                counter_thesis=thesis_data.get('counter_thesis', {}),
                metrics_to_track=thesis_data.get('metrics_to_track', []),
                monitoring_plan=thesis_data.get('monitoring_plan', {})
            )
            
            db.session.add(thesis)
            db.session.commit()
            
            logging.info(f"Saved thesis analysis with ID: {thesis.id}")
            return thesis.id
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to save thesis analysis: {str(e)}")
            raise Exception(f"Database save failed: {str(e)}")
    
    def get_thesis_analysis(self, thesis_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve thesis analysis from database"""
        try:
            thesis = ThesisAnalysis.query.get(thesis_id)
            if thesis:
                return thesis.to_dict()
            return None
            
        except Exception as e:
            logging.error(f"Failed to retrieve thesis {thesis_id}: {str(e)}")
            return None
    
    def get_all_thesis_analyses(self) -> List[Dict[str, Any]]:
        """Get all thesis analyses from database"""
        try:
            theses = ThesisAnalysis.query.order_by(ThesisAnalysis.created_at.desc()).all()
            return [thesis.to_dict() for thesis in theses]
            
        except Exception as e:
            logging.error(f"Failed to retrieve thesis analyses: {str(e)}")
            return []
    
    def save_signal_monitoring(self, thesis_id: int, signal_data: Dict[str, Any]) -> int:
        """Save signal monitoring configuration"""
        try:
            signal = SignalMonitoring(
                thesis_analysis_id=thesis_id,
                signal_name=signal_data.get('name', ''),
                signal_type=signal_data.get('type', ''),
                current_value=signal_data.get('current_value'),
                threshold_value=signal_data.get('threshold_value'),
                threshold_type=signal_data.get('threshold_type', 'above'),
                status='active'
            )
            
            db.session.add(signal)
            db.session.commit()
            
            return signal.id
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to save signal monitoring: {str(e)}")
            raise Exception(f"Signal save failed: {str(e)}")
    
    def get_active_signals(self, thesis_id: int) -> List[Dict[str, Any]]:
        """Get active monitoring signals for a thesis"""
        try:
            signals = SignalMonitoring.query.filter_by(
                thesis_analysis_id=thesis_id,
                status='active'
            ).all()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logging.error(f"Failed to retrieve signals for thesis {thesis_id}: {str(e)}")
            return []
    
    # External Data Operations
    def get_company_metrics(self, ticker: str, metric_categories: List[str] = None) -> Dict[str, Any]:
        """Get comprehensive company metrics from external sources"""
        if not self.data_adapter:
            return self._get_fallback_company_metrics(ticker)
        
        try:
            # Try Eagle API first (highest priority)
            if self.eagle_api_available:
                eagle_data = self.data_adapter.fetch_eagle_metrics(ticker, metric_categories)
                if eagle_data and eagle_data.get('success'):
                    return eagle_data
            
            # Try FactSet API (second priority)
            if self.factset_api_available:
                factset_data = self.data_adapter.fetch_factset_data(ticker)
                if factset_data and factset_data.get('success'):
                    return factset_data
            
            # Try Xpressfeed API (third priority)
            if self.xpressfeed_api_available:
                xpressfeed_data = self.data_adapter.fetch_xpressfeed_data(ticker)
                if xpressfeed_data and xpressfeed_data.get('success'):
                    return xpressfeed_data
            
            # Return fallback data if all APIs fail
            logging.warning(f"All external APIs failed for ticker {ticker}, using fallback data")
            return self._get_fallback_company_metrics(ticker)
            
        except Exception as e:
            logging.error(f"Failed to fetch company metrics for {ticker}: {str(e)}")
            return self._get_fallback_company_metrics(ticker)
    
    def check_signal_data_availability(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Check data availability and quality for a signal"""
        signal_name = signal.get('name', '')
        signal_type = signal.get('type', '')
        
        # Check if we have data sources for this signal
        availability_score = 0
        data_sources = []
        
        if self.eagle_api_available:
            availability_score += 0.4
            data_sources.append('Eagle API')
        
        if self.factset_api_available:
            availability_score += 0.3
            data_sources.append('FactSet API')
        
        if self.xpressfeed_api_available:
            availability_score += 0.3
            data_sources.append('Xpressfeed API')
        
        # Determine availability level
        if availability_score >= 0.8:
            availability = 'high'
        elif availability_score >= 0.5:
            availability = 'medium'
        else:
            availability = 'low'
        
        # Determine update frequency based on signal type
        frequency_map = {
            'Level_0_Raw_Economic_Activity': 'daily',
            'Level_1_Primary_Signals': 'daily',
            'Level_2_Derived_Metrics': 'weekly',
            'Level_3_Technical_Indicators': 'daily',
            'Level_4_Market_Sentiment': 'daily',
            'Level_5_Meta_Analysis': 'weekly'
        }
        
        return {
            'availability': availability,
            'quality': 'good' if availability_score > 0.5 else 'fair',
            'frequency': frequency_map.get(signal_type, 'weekly'),
            'sources': data_sources,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_market_context(self, thesis_claim: str, time_horizon: int) -> Dict[str, Any]:
        """Get relevant market context for analysis"""
        try:
            # Extract key terms from thesis for market context
            market_sectors = self._extract_market_sectors(thesis_claim)
            
            context = {
                'relevant_sectors': market_sectors,
                'market_conditions': self._get_current_market_conditions(),
                'economic_indicators': self._get_economic_indicators(),
                'time_horizon': time_horizon,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            return context
            
        except Exception as e:
            logging.error(f"Failed to get market context: {str(e)}")
            return {
                'relevant_sectors': ['Technology'],
                'market_conditions': 'neutral',
                'economic_indicators': {},
                'time_horizon': time_horizon
            }
    
    def get_historical_performance(self, ticker: str, period_days: int = 365) -> Dict[str, Any]:
        """Get historical performance data"""
        try:
            if self.data_adapter:
                return self.data_adapter.fetch_historical_data(ticker, period_days)
            else:
                return self._get_fallback_historical_data(ticker, period_days)
                
        except Exception as e:
            logging.error(f"Failed to get historical data for {ticker}: {str(e)}")
            return self._get_fallback_historical_data(ticker, period_days)
    
    # Document Management
    def save_document(self, filename: str, file_path: str, file_type: str, 
                     processed_data: Dict = None, thesis_id: int = None) -> int:
        """Save document upload record"""
        try:
            document = DocumentUpload(
                filename=filename,
                file_type=file_type,
                upload_path=file_path,
                processed_data=processed_data or {},
                thesis_analysis_id=thesis_id
            )
            
            db.session.add(document)
            db.session.commit()
            
            return document.id
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to save document: {str(e)}")
            raise Exception(f"Document save failed: {str(e)}")
    
    def get_documents_for_thesis(self, thesis_id: int) -> List[Dict[str, Any]]:
        """Get all documents associated with a thesis"""
        try:
            documents = DocumentUpload.query.filter_by(thesis_analysis_id=thesis_id).all()
            return [doc.to_dict() for doc in documents]
            
        except Exception as e:
            logging.error(f"Failed to retrieve documents for thesis {thesis_id}: {str(e)}")
            return []
    
    # Data Quality and Validation
    def validate_data_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data integrity and quality"""
        validation_result = {
            'is_valid': True,
            'quality_score': 1.0,
            'issues': [],
            'recommendations': []
        }
        
        # Check for required fields
        required_fields = ['timestamp', 'source']
        for field in required_fields:
            if field not in data:
                validation_result['issues'].append(f"Missing required field: {field}")
                validation_result['is_valid'] = False
        
        # Check data freshness
        if 'timestamp' in data:
            try:
                data_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                age_hours = (datetime.utcnow() - data_time.replace(tzinfo=None)).total_seconds() / 3600
                
                if age_hours > 24:
                    validation_result['quality_score'] *= 0.8
                    validation_result['recommendations'].append("Data is older than 24 hours")
                    
            except Exception:
                validation_result['issues'].append("Invalid timestamp format")
        
        return validation_result
    
    # Private Helper Methods
    def _get_fallback_company_metrics(self, ticker: str) -> Dict[str, Any]:
        """Provide fallback company metrics when external APIs are unavailable"""
        return {
            'success': True,
            'source': 'fallback_data',
            'ticker': ticker,
            'metrics': {
                'revenue_growth': 0.08,
                'profit_margin': 0.15,
                'market_cap': 1000000000,
                'pe_ratio': 20.0,
                'debt_to_equity': 0.3
            },
            'timestamp': datetime.utcnow().isoformat(),
            'data_quality': 'synthetic'
        }
    
    def _get_fallback_historical_data(self, ticker: str, period_days: int) -> Dict[str, Any]:
        """Provide fallback historical data"""
        return {
            'success': True,
            'source': 'fallback_data',
            'ticker': ticker,
            'period_days': period_days,
            'data_points': [],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _extract_market_sectors(self, thesis_claim: str) -> List[str]:
        """Extract relevant market sectors from thesis claim"""
        sector_keywords = {
            'technology': ['tech', 'software', 'ai', 'cloud', 'digital'],
            'healthcare': ['health', 'medical', 'pharma', 'biotech'],
            'finance': ['bank', 'financial', 'fintech', 'insurance'],
            'energy': ['energy', 'oil', 'renewable', 'solar', 'wind'],
            'consumer': ['retail', 'consumer', 'ecommerce', 'brand']
        }
        
        claim_lower = thesis_claim.lower()
        relevant_sectors = []
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in claim_lower for keyword in keywords):
                relevant_sectors.append(sector.title())
        
        return relevant_sectors if relevant_sectors else ['General Market']
    
    def _get_current_market_conditions(self) -> str:
        """Get current market conditions assessment"""
        # In production, this would query real market data
        return 'neutral'
    
    def _get_economic_indicators(self) -> Dict[str, Any]:
        """Get current economic indicators"""
        # In production, this would fetch real economic data
        return {
            'gdp_growth': 0.025,
            'inflation_rate': 0.03,
            'unemployment_rate': 0.04,
            'interest_rate': 0.05
        }
    
    # Service Status and Health Checks
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all external data services"""
        return {
            'eagle_api': {
                'available': self.eagle_api_available,
                'status': 'active' if self.eagle_api_available else 'unavailable'
            },
            'factset_api': {
                'available': self.factset_api_available,
                'status': 'active' if self.factset_api_available else 'unavailable'
            },
            'xpressfeed_api': {
                'available': self.xpressfeed_api_available,
                'status': 'active' if self.xpressfeed_api_available else 'unavailable'
            },
            'database': {
                'status': 'active',
                'last_check': datetime.utcnow().isoformat()
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of data services"""
        status = self.get_service_status()
        
        total_services = len([s for s in status.values() if isinstance(s, dict)])
        active_services = len([s for s in status.values() 
                             if isinstance(s, dict) and s.get('status') == 'active'])
        
        health_score = active_services / total_services if total_services > 0 else 0
        
        return {
            'overall_health': 'healthy' if health_score > 0.5 else 'degraded',
            'health_score': health_score,
            'active_services': active_services,
            'total_services': total_services,
            'service_details': status,
            'timestamp': datetime.utcnow().isoformat()
        }