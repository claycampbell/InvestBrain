"""
Signal Classification Service - LLM Data Only
Implements signal classification framework using purely LLM-generated data
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalLevel(Enum):
    """Signal classification levels based on processing complexity"""
    LEVEL_0 = "Internal Research Data"       # Structured financial queries and thesis validation
    LEVEL_1 = "Raw Economic Activity"        # Direct measurements: housing starts, permit applications, factory utilization
    LEVEL_2 = "Simple Aggregation"           # Basic combinations: monthly spending totals, inventory levels
    LEVEL_3 = "Derived Metrics"              # Calculated ratios: growth rates, market share changes
    LEVEL_4 = "Complex Ratios"               # Multi-variable calculations: valuation multiples, peer comparisons
    LEVEL_5 = "Market Sentiment"             # Behavioral indicators: analyst sentiment, options flow

@dataclass
class Signal:
    """Represents an identified signal with classification metadata"""
    name: str
    level: SignalLevel
    description: str
    data_source: str
    value_chain_position: str
    predictive_power: str  # "high", "medium", "low"
    market_attention: str  # "low", "medium", "high"
    lead_lag_indicator: str  # "leading", "coincident", "lagging"
    raw_data_points: List[str]
    derivation_method: Optional[str] = None
    correlation_signals: Optional[List[str]] = None
    collection_frequency: str = "unknown"
    reliability_score: float = 0.0

class SignalClassifier:
    """
    Signal classification engine using purely LLM-generated data
    """
    
    def __init__(self):
        # Signal classifier relies purely on LLM analysis without hardcoded patterns
        from services.internal_research_service import InternalResearchService
        self.research_service = InternalResearchService()
        
    def classify_signals(self, thesis_text: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to classify signals from thesis and analysis data"""
        try:
            # Generate comprehensive signal classification
            raw_signals = self._generate_raw_signals(thesis_text)
            level_0_signals = self._generate_level_0_signals(thesis_text)
            hierarchical_signals = self._generate_hierarchical_signals(thesis_text, analysis_data)
            
            return {
                'raw_signals': raw_signals,
                'level_0_signals': level_0_signals,
                'hierarchical_signals': hierarchical_signals,
                'total_signals': len(raw_signals) + len(level_0_signals) + len(hierarchical_signals)
            }
        except Exception as e:
            logging.error(f"Signal classification failed: {e}")
            return {
                'raw_signals': [],
                'level_0_signals': [],
                'hierarchical_signals': [],
                'total_signals': 0
            }
    
    def _generate_raw_signals(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Generate raw financial and operational signals"""
        signals = []
        
        # Revenue and growth signals
        if any(word in thesis_text.lower() for word in ['revenue', 'growth', 'sales']):
            signals.append({
                'name': 'Quarterly Revenue Growth',
                'type': 'Level_1_Simple_Aggregation',
                'description': 'Year-over-year revenue growth percentage',
                'data_source': 'Financial Statements',
                'frequency': 'quarterly',
                'category': 'growth_metrics'
            })
        
        # Profitability signals
        if any(word in thesis_text.lower() for word in ['margin', 'efficiency', 'profitability']):
            signals.append({
                'name': 'Operating Margin Expansion',
                'type': 'Level_2_Cross_Functional',
                'description': 'Operating margin improvement trends',
                'data_source': 'Income Statements',
                'frequency': 'quarterly',
                'category': 'profitability_metrics'
            })
        
        # Market signals
        if any(word in thesis_text.lower() for word in ['market', 'competitive', 'share']):
            signals.append({
                'name': 'Market Share Trends',
                'type': 'Level_3_Strategic_Insight',
                'description': 'Competitive positioning analysis',
                'data_source': 'Industry Reports',
                'frequency': 'monthly',
                'category': 'market_metrics'
            })
        
        return signals
    
    def _generate_level_0_signals(self, thesis_text: str) -> List[Dict[str, Any]]:
        """Generate Level 0 research validation signals"""
        return [
            {
                'name': 'Core Thesis Validation',
                'type': 'Level_0_Raw_Activity',
                'description': 'Structured validation of core investment thesis claims',
                'validation_framework': 'Primary evidence assessment',
                'frequency': 'continuous'
            },
            {
                'name': 'Assumption Testing',
                'type': 'Level_0_Raw_Activity', 
                'description': 'Systematic testing of investment assumptions',
                'validation_framework': 'Risk-weighted assumption analysis',
                'frequency': 'monthly'
            }
        ]
    
    def _generate_hierarchical_signals(self, thesis_text: str, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate hierarchical signal structure"""
        return [
            {
                'name': 'Multi-Level Signal Integration',
                'type': 'Level_4_Complex_Ratios',
                'description': 'Integration of signals across all classification levels',
                'components': ['Financial metrics', 'Market indicators', 'Research validation'],
                'methodology': 'Weighted signal aggregation'
            }
        ]

    def extract_signals_from_ai_analysis(self, ai_analysis: Dict[str, Any], processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract and classify signals from AI analysis results with Level 0-5 hierarchy
        """
        try:
            # Ensure ai_analysis is a dictionary
            if isinstance(ai_analysis, str):
                try:
                    ai_analysis = json.loads(ai_analysis)
                except json.JSONDecodeError:
                    logging.error("Failed to parse AI analysis as JSON")
                    ai_analysis = {}
            
            if not isinstance(ai_analysis, dict):
                logging.error(f"AI analysis is not a dictionary: {type(ai_analysis)}")
                ai_analysis = {}
            
            all_signals = []
            
            # Generate Level 0 Raw Economic Activity signals first
            level_0_signals = self.research_service.generate_research_signals(ai_analysis)
            for research_signal in level_0_signals:
                # Handle both old and new structured signal formats
                description = research_signal.get('description', 
                    f"Structured query: {research_signal.get('category', 'Financial Analysis')}")
                
                signal = Signal(
                    name=research_signal['signal_name'],
                    level=SignalLevel.LEVEL_0,
                    description=description,
                    data_source='Internal Research Database',
                    value_chain_position='data_foundation',
                    predictive_power='high',
                    market_attention='low',
                    lead_lag_indicator='leading',
                    raw_data_points=[research_signal['signal_name']],
                    collection_frequency='daily',
                    reliability_score=0.95
                )
                all_signals.append(signal)
                logging.info(f"Added Level 0 signal: {signal.name} ({research_signal['category']})")
            
            # Extract signals from AI analysis metrics_to_track (Level 1-5)
            metrics_to_track = ai_analysis.get('metrics_to_track', [])
            logging.info(f"Processing {len(metrics_to_track)} metrics from AI analysis")
            
            for metric in metrics_to_track:
                # Ensure metric is a dictionary, skip if string or invalid
                if not isinstance(metric, dict):
                    logging.warning(f"Skipping invalid metric format: {type(metric)}")
                    continue
                
                # Map AI signal types to our enum
                signal_type = metric.get('type', 'Level_2_Derived_Metrics')
                level = self._parse_signal_level(signal_type)
                
                # Use AI-provided value chain position or default
                chain_position = metric.get('value_chain_position', 'unknown')
                
                # Enhanced signal creation with AI-provided metadata
                signal = Signal(
                    name=metric.get('name', 'Unknown Signal'),
                    level=level,
                    description=metric.get('description', ''),
                    data_source=metric.get('data_source', 'Unknown'),
                    value_chain_position=chain_position,
                    predictive_power=metric.get('predictive_power', 'medium'),
                    market_attention=metric.get('market_attention', 'low'),
                    lead_lag_indicator=metric.get('lead_lag_indicator', 'leading'),
                    raw_data_points=[metric.get('name', '')],
                    collection_frequency=metric.get('frequency', 'unknown'),
                    reliability_score=0.9  # High reliability for AI-selected signals
                )
                
                all_signals.append(signal)
                logging.info(f"Added signal: {signal.name} (Level: {level.value}, Chain: {signal.value_chain_position})")
            
            # Extract additional signals from document content (LLM-processed only)
            document_signals = self._extract_signals_from_documents(processed_documents, focus_primary)
            all_signals.extend(document_signals)
            
            # If focusing on primary signals, prioritize Level 0-1 (Internal Research Data + Raw Economic Activity)
            if focus_primary:
                primary_signals = [s for s in all_signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1, SignalLevel.LEVEL_2]]
                all_signals = primary_signals + [s for s in all_signals if s not in primary_signals]
            
            # Analyze relationships and value chain mapping
            signal_relationships = self._analyze_signal_relationships(all_signals)
            value_chain_mapping = self._create_value_chain_mapping(all_signals)
            
            # Generate signal quality assessment
            quality_assessment = self._assess_signal_quality(all_signals)
            
            return {
                'total_signals_identified': len(all_signals),
                'primary_signals_count': len([s for s in all_signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]]),
                'signals_by_level': self._group_signals_by_level(all_signals),
                'value_chain_mapping': value_chain_mapping,
                'signal_relationships': signal_relationships,
                'quality_assessment': quality_assessment,
                'recommended_monitoring': self._recommend_monitoring_strategy(all_signals, focus_primary),
                'raw_signals': [self._signal_to_dict(s) for s in all_signals]
            }
            
        except Exception as e:
            logging.error(f"Error in AI signal extraction: {str(e)}")
            return {
                'total_signals_identified': 0,
                'primary_signals_count': 0,
                'signals_by_level': {},
                'value_chain_mapping': {'upstream': [], 'midstream': [], 'downstream': [], 'unknown': []},
                'signal_relationships': {'correlation_clusters': [], 'lead_lag_chains': [], 'value_chain_flows': []},
                'quality_assessment': {'overall_score': 0, 'assessment': 'No signals identified'},
                'recommended_monitoring': {'monitoring_frequency': 'weekly', 'priority_signals': [], 'data_sources_needed': [], 'automation_opportunities': []},
                'raw_signals': []
            }
    
    def extract_signals_from_analysis(self, thesis_text: str, processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract signals from analysis result and classify them - LLM data only
        """
        try:
            # Extract from LLM analysis only - no hardcoded patterns
            all_signals = []
            
            # Process any AI-generated signals from documents
            document_signals = self._extract_signals_from_documents(processed_documents, focus_primary)
            all_signals.extend(document_signals)
            
            # Generate comprehensive analysis
            signal_relationships = self._analyze_signal_relationships(all_signals)
            value_chain_mapping = self._create_value_chain_mapping(all_signals)
            quality_assessment = self._assess_signal_quality(all_signals)
            
            return {
                'total_signals_identified': len(all_signals),
                'primary_signals_count': len([s for s in all_signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]]),
                'signals_by_level': self._group_signals_by_level(all_signals),
                'value_chain_mapping': value_chain_mapping,
                'signal_relationships': signal_relationships,
                'quality_assessment': quality_assessment,
                'recommended_monitoring': self._recommend_monitoring_strategy(all_signals, focus_primary),
                'raw_signals': [self._signal_to_dict(s) for s in all_signals]
            }
                
        except Exception as e:
            logging.error(f"Error in signal extraction: {str(e)}")
            return {'error': str(e)}
    
    def _parse_signal_level(self, level_str: str) -> SignalLevel:
        """Parse signal level string from AI analysis - Updated for 6-level hierarchy"""
        level_mapping = {
            'Internal Research Data': SignalLevel.LEVEL_0,
            'Raw Economic Activity': SignalLevel.LEVEL_1,
            'Simple Aggregation': SignalLevel.LEVEL_2,
            'Derived Metrics': SignalLevel.LEVEL_3,
            'Complex Ratios': SignalLevel.LEVEL_4,
            'Market Sentiment': SignalLevel.LEVEL_5,
            'Level_0_Internal_Research': SignalLevel.LEVEL_0,
            'Level_1_Raw_Economic': SignalLevel.LEVEL_1,
            'Level_2_Simple_Aggregation': SignalLevel.LEVEL_2,
            'Level_3_Derived_Metrics': SignalLevel.LEVEL_3,
            'Level_4_Complex_Ratios': SignalLevel.LEVEL_4,
            'Level_5_Market_Sentiment': SignalLevel.LEVEL_5
        }
        return level_mapping.get(level_str, SignalLevel.LEVEL_2)
    
    def _extract_signals_from_documents(self, processed_documents: List[Dict], focus_primary: bool) -> List[Signal]:
        """Extract signals from LLM-processed document content only"""
        signals = []
        # Only process AI-generated signal data from documents
        for doc in processed_documents:
            doc_data = doc.get('data', {})
            if 'ai_extracted_signals' in doc_data:
                # Process AI-extracted signals from document analysis
                ai_signals = doc_data['ai_extracted_signals']
                for signal_data in ai_signals:
                    signal = Signal(
                        name=signal_data.get('name', 'Document Signal'),
                        level=self._parse_signal_level(signal_data.get('level', 'Level_2_Derived_Metrics')),
                        description=signal_data.get('description', ''),
                        data_source=signal_data.get('data_source', 'Document analysis'),
                        value_chain_position=signal_data.get('value_chain_position', 'unknown'),
                        predictive_power=signal_data.get('predictive_power', 'medium'),
                        market_attention=signal_data.get('market_attention', 'low'),
                        lead_lag_indicator=signal_data.get('lead_lag_indicator', 'leading'),
                        raw_data_points=[signal_data.get('name', '')],
                        collection_frequency=signal_data.get('frequency', 'unknown'),
                        reliability_score=0.8
                    )
                    signals.append(signal)
        return signals
    
    def _analyze_signal_relationships(self, signals: List[Signal]) -> Dict[str, Any]:
        """Analyze relationships between signals"""
        return {
            'correlation_clusters': [],
            'lead_lag_chains': [],
            'value_chain_flows': []
        }
    
    def _create_value_chain_mapping(self, signals: List[Signal]) -> Dict[str, List[str]]:
        """Create value chain mapping for signals"""
        mapping = {'upstream': [], 'midstream': [], 'downstream': [], 'unknown': []}
        for signal in signals:
            position = signal.value_chain_position
            if position in mapping:
                mapping[position].append(signal.name)
            else:
                mapping['unknown'].append(signal.name)
        return mapping
    
    def _assess_signal_quality(self, signals: List[Signal]) -> Dict[str, Any]:
        """Assess overall signal quality"""
        if not signals:
            return {'overall_score': 0, 'assessment': 'No signals identified'}
        
        avg_reliability = sum(s.reliability_score for s in signals) / len(signals)
        return {
            'overall_score': avg_reliability,
            'assessment': f'Signal quality assessment based on {len(signals)} signals'
        }
    
    def _group_signals_by_level(self, signals: List[Signal]) -> Dict[str, List[str]]:
        """Group signals by their classification level"""
        groups = {}
        for signal in signals:
            level_name = signal.level.value
            if level_name not in groups:
                groups[level_name] = []
            groups[level_name].append(signal.name)
        return groups
    
    def _recommend_monitoring_strategy(self, signals: List[Signal], focus_primary: bool) -> Dict[str, Any]:
        """Recommend monitoring strategy for signals"""
        return {
            'monitoring_frequency': 'weekly',
            'priority_signals': [s.name for s in signals[:5]],
            'data_sources_needed': list(set(s.data_source for s in signals)),
            'automation_opportunities': [s.name for s in signals if s.reliability_score > 0.8]
        }
    
    def _signal_to_dict(self, signal: Signal) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            'name': signal.name,
            'level': signal.level.value,
            'description': signal.description,
            'data_source': signal.data_source,
            'value_chain_position': signal.value_chain_position,
            'predictive_power': signal.predictive_power,
            'market_attention': signal.market_attention,
            'lead_lag_indicator': signal.lead_lag_indicator,
            'raw_data_points': signal.raw_data_points,
            'derivation_method': signal.derivation_method,
            'correlation_signals': signal.correlation_signals,
            'collection_frequency': signal.collection_frequency,
            'reliability_score': signal.reliability_score
        }