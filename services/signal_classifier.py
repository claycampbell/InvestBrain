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
    LEVEL_0 = "Internal Research Data"        # Structured financial queries
    LEVEL_1 = "Raw Economic Activity"         # Direct measurements
    LEVEL_2 = "Simple Aggregation"           # Basic combinations
    LEVEL_3 = "Derived Metrics"              # Calculated ratios
    LEVEL_4 = "Complex Derivatives"          # Multi-input calculations
    LEVEL_5 = "Synthetic Indicators"         # Highly processed composites

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
        
    def extract_signals_from_ai_analysis(self, ai_analysis: Dict[str, Any], processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract and classify signals from AI analysis results with Level 0-5 hierarchy
        """
        try:
            all_signals = []
            
            # Generate Level 0 Internal Research Data signals first
            level_0_signals = self.research_service.generate_research_signals(ai_analysis)
            for research_signal in level_0_signals:
                signal = Signal(
                    name=research_signal['signal_name'],
                    level=SignalLevel.LEVEL_0,
                    description=research_signal['description'],
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
            
            # If focusing on primary signals, prioritize Level 0-2 (Internal Research + Raw Activity + Simple Aggregation)
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
            'Level_0_Internal_Research': SignalLevel.LEVEL_0,
            'Level_1_Raw_Activity': SignalLevel.LEVEL_1,
            'Level_2_Simple_Aggregation': SignalLevel.LEVEL_2,
            'Level_3_Derived_Metrics': SignalLevel.LEVEL_3,
            'Level_4_Complex_Derivatives': SignalLevel.LEVEL_4,
            'Level_5_Synthetic_Indicators': SignalLevel.LEVEL_5,
            # Legacy mappings for backward compatibility
            'Level_0_Raw_Activity': SignalLevel.LEVEL_1,
            'Level_1_Simple_Aggregation': SignalLevel.LEVEL_2,
            'Level_2_Derived_Metrics': SignalLevel.LEVEL_3,
            'Level_3_Complex_Derivatives': SignalLevel.LEVEL_4,
            'Level_4_Synthetic_Indicators': SignalLevel.LEVEL_5
        }
        return level_mapping.get(level_str, SignalLevel.LEVEL_3)
    
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