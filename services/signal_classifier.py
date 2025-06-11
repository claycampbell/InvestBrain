"""
Signal Classification Service
Implements the hierarchical signal classification framework for investment analysis
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalLevel(Enum):
    """Signal classification levels based on processing complexity"""
    LEVEL_0 = "Raw Economic Activity"          # Direct measurements
    LEVEL_1 = "Simple Aggregation"            # Basic combinations
    LEVEL_2 = "Derived Metrics"               # Calculated ratios
    LEVEL_3 = "Complex Derivatives"           # Multi-input calculations
    LEVEL_4 = "Synthetic Indicators"          # Highly processed composites

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
    Advanced signal classification engine implementing the hierarchical framework
    """
    
    def __init__(self):
        self.level_0_indicators = self._load_level_0_patterns()
        self.level_1_indicators = self._load_level_1_patterns()
        self.value_chain_keywords = self._load_value_chain_patterns()
        self.predictive_keywords = self._load_predictive_patterns()
        
    def _load_level_0_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying Level 0 (raw economic activity) signals"""
        return {
            'production_activity': [
                'factory utilization', 'manufacturing output', 'production capacity',
                'assembly line speed', 'shift patterns', 'overtime hours',
                'raw material consumption', 'energy consumption per unit',
                'machine uptime', 'production schedules', 'order backlogs'
            ],
            'construction_activity': [
                'housing starts', 'building permits', 'construction permits',
                'excavation permits', 'foundation pours', 'concrete deliveries',
                'lumber deliveries', 'electrical installations', 'plumbing permits',
                'occupancy certificates', 'site preparations'
            ],
            'employment_activity': [
                'job postings', 'hiring rates', 'termination rates',
                'overtime authorizations', 'temporary worker requests',
                'contractor agreements', 'training enrollments',
                'badge swipes', 'parking utilization', 'cafeteria usage'
            ],
            'supply_chain_activity': [
                'shipping container volume', 'truck movements', 'rail car loadings',
                'warehouse receipts', 'dock utilization', 'port traffic',
                'inventory receipts', 'supplier deliveries', 'return shipments',
                'cargo manifests', 'customs clearances'
            ],
            'retail_activity': [
                'foot traffic', 'transaction counts', 'basket sizes',
                'checkout times', 'inventory turns', 'stockouts',
                'return rates', 'store hours', 'staff scheduling',
                'promotional activity', 'price changes'
            ],
            'financial_activity': [
                'loan applications', 'credit inquiries', 'account openings',
                'transaction volumes', 'ATM usage', 'branch visits',
                'wire transfers', 'check clearings', 'deposit flows',
                'withdrawal patterns', 'payment processing volumes'
            ],
            'innovation_activity': [
                'patent applications', 'R&D spending', 'prototype builds',
                'clinical trials', 'regulatory filings', 'testing schedules',
                'researcher hiring', 'lab equipment purchases', 'facility expansions',
                'intellectual property registrations', 'licensing agreements'
            ],
            'resource_extraction': [
                'drilling permits', 'extraction rates', 'ore grades',
                'well completions', 'mining equipment hours', 'blast schedules',
                'transportation loads', 'processing volumes', 'stockpile levels',
                'equipment maintenance', 'worker safety incidents'
            ]
        }
    
    def _load_level_1_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying Level 1 (simple aggregation) signals"""
        return {
            'daily_totals': [
                'daily production', 'daily sales', 'daily shipments',
                'daily transactions', 'daily visits', 'daily registrations'
            ],
            'weekly_aggregates': [
                'weekly averages', 'weekly totals', 'weekly counts',
                'weekly volumes', 'weekly rates', 'weekly utilization'
            ],
            'monthly_summaries': [
                'monthly totals', 'monthly averages', 'monthly peaks',
                'monthly minimums', 'monthly ranges', 'monthly distributions'
            ],
            'regional_aggregates': [
                'regional totals', 'state-level data', 'county data',
                'city-level metrics', 'district summaries', 'zone aggregates'
            ],
            'simple_ratios': [
                'utilization rates', 'completion rates', 'success rates',
                'conversion rates', 'efficiency ratios', 'productivity metrics'
            ]
        }
    
    def _load_value_chain_patterns(self) -> Dict[str, List[str]]:
        """Load value chain position identifiers"""
        return {
            'upstream': [
                'raw materials', 'commodities', 'mining', 'extraction',
                'agriculture', 'forestry', 'fishing', 'primary production',
                'gpu', 'chip', 'semiconductor', 'wafer', 'foundry', 'silicon',
                'ai accelerator', 'processor', 'hardware', 'components',
                'nvidia', 'tsmc', 'capacity utilization', 'shipments'
            ],
            'midstream': [
                'processing', 'refining', 'manufacturing', 'assembly',
                'transportation', 'logistics', 'distribution', 'warehousing',
                'data center', 'capex', 'infrastructure', 'deployment',
                'hyperscaler', 'azure', 'cloud', 'server', 'facility',
                'installation', 'integration', 'system build'
            ],
            'downstream': [
                'retail', 'consumer', 'end-user', 'final demand',
                'services', 'consumption', 'customer-facing', 'point-of-sale',
                'registration', 'adoption', 'usage', 'subscription',
                'enterprise', 'deals', 'revenue', 'market share',
                'autonomous vehicle', 'api calls', 'copilot', 'application'
            ]
        }
    
    def _load_predictive_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for assessing predictive power"""
        return {
            'high_predictive': [
                'leading indicator', 'early warning', 'advance signal',
                'forward-looking', 'predictive', 'forecasting'
            ],
            'medium_predictive': [
                'coincident', 'concurrent', 'real-time', 'current'
            ],
            'low_predictive': [
                'lagging', 'trailing', 'historical', 'backward-looking',
                'confirmatory', 'retrospective'
            ]
        }
    
    def extract_signals_from_ai_analysis(self, ai_analysis: Dict[str, Any], processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract and classify signals from AI analysis results
        """
        try:
            all_signals = []
            
            # Extract signals from AI analysis metrics_to_track
            metrics_to_track = ai_analysis.get('metrics_to_track', [])
            logging.info(f"Processing {len(metrics_to_track)} metrics from AI analysis")
            
            for metric in metrics_to_track:
                # Map AI signal types to our enum
                signal_type = metric.get('type', 'Level_2_Derived_Metrics')
                level = self._parse_signal_level(signal_type)
                
                # Determine value chain position if not specified by AI
                chain_position = metric.get('value_chain_position', 'unknown')
                if chain_position == 'unknown':
                    chain_position = self._determine_value_chain_position(metric.get('name', ''))
                
                # Enhanced signal creation with additional metadata
                signal = Signal(
                    name=metric.get('name', 'Unknown Signal'),
                    level=level,
                    description=metric.get('description', ''),
                    data_source=metric.get('data_source', 'Unknown'),
                    value_chain_position=chain_position,
                    predictive_power='high',  # AI-selected signals are high value
                    market_attention='low',   # Primary signals have low market attention
                    lead_lag_indicator='leading',
                    raw_data_points=[metric.get('name', '')],
                    collection_frequency=metric.get('frequency', 'unknown'),
                    reliability_score=0.9  # High reliability for AI-selected signals
                )
                # Add enhanced metadata for detailed analysis
                signal.what_it_tells_us = metric.get('what_it_tells_us', metric.get('description', ''))
                signal.threshold = metric.get('threshold', 0)
                signal.threshold_type = metric.get('threshold_type', 'change_percent')
                
                all_signals.append(signal)
                logging.info(f"Added signal: {signal.name} (Level: {level.value}, Chain: {signal.value_chain_position})")
            
            # Extract additional signals from document content
            document_signals = self._extract_signals_from_documents(processed_documents, focus_primary)
            all_signals.extend(document_signals)
            
            # If focusing on primary signals, prioritize Level 0-1
            if focus_primary:
                primary_signals = [s for s in all_signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]]
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
    
    def _parse_signal_level(self, level_str: str) -> SignalLevel:
        """Parse signal level string from AI analysis"""
        level_mapping = {
            'Level_0_Raw_Activity': SignalLevel.LEVEL_0,
            'Level_1_Simple_Aggregation': SignalLevel.LEVEL_1,
            'Level_2_Derived_Metrics': SignalLevel.LEVEL_2,
            'Level_3_Complex_Derivatives': SignalLevel.LEVEL_3,
            'Level_4_Synthetic_Indicators': SignalLevel.LEVEL_4
        }
        return level_mapping.get(level_str, SignalLevel.LEVEL_2)
    
    def _extract_signals_from_documents(self, processed_documents: List[Dict], focus_primary: bool) -> List[Signal]:
        """Extract signals from processed document content"""
        signals = []
        for doc in processed_documents:
            doc_data = doc.get('data', {})
            if 'text_content' in doc_data:
                text_signals = self._extract_level_0_signals(doc_data['text_content'])
                signals.extend(text_signals)
                if not focus_primary:
                    text_signals.extend(self._extract_level_1_signals(doc_data['text_content']))
                    text_signals.extend(self._extract_level_2_signals(doc_data['text_content']))
        return signals

    def extract_signals_from_ai_analysis(self, analysis_result: Dict, processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract signals from AI analysis result and classify them across all 5 levels when focus_primary=False
        """
        try:
            # Get thesis text from analysis result
            thesis_text = analysis_result.get('original_thesis', '') or analysis_result.get('thesis_text', '')
            signals_data = analysis_result.get('signals', [])
            
            if not focus_primary:
                # Extract comprehensive signals across all 5 levels
                return self._extract_comprehensive_signals(thesis_text, processed_documents, signals_data)
            else:
                # Focus on primary signals (Level 0-1)
                return self._extract_primary_signals(thesis_text, processed_documents, signals_data)
                
        except Exception as e:
            logging.error(f"Error in AI signal extraction: {str(e)}")
            return {'error': str(e)}
    
    def _extract_comprehensive_signals(self, thesis_text: str, processed_documents: List[Dict], ai_signals: List[Dict]) -> Dict[str, Any]:
        """Extract signals across all 5 derivation levels with acquisition guidance"""
        all_signals = []
        
        # Level 0: Raw Economic Activity
        level_0_signals = self._extract_level_0_comprehensive(thesis_text, processed_documents)
        
        # Level 1: Simple Aggregation
        level_1_signals = self._extract_level_1_comprehensive(thesis_text, processed_documents)
        
        # Level 2: Derived Metrics
        level_2_signals = self._extract_level_2_comprehensive(thesis_text, processed_documents)
        
        # Level 3: Complex Ratios
        level_3_signals = self._extract_level_3_comprehensive(thesis_text, processed_documents)
        
        # Level 4: Market Sentiment
        level_4_signals = self._extract_level_4_comprehensive(thesis_text, processed_documents)
        
        # Combine all signals
        all_signals.extend(level_0_signals)
        all_signals.extend(level_1_signals)
        all_signals.extend(level_2_signals)
        all_signals.extend(level_3_signals)
        all_signals.extend(level_4_signals)
        
        # Add programmatic feasibility assessment
        for signal in all_signals:
            signal['acquisition_guidance'] = self._assess_acquisition_feasibility(signal)
        
        return {
            'comprehensive_analysis': True,
            'total_signals_identified': len(all_signals),
            'signals_by_level': {
                'Level_0_Raw_Economic': [s for s in all_signals if s.get('level') == 'Level_0_Raw_Economic'],
                'Level_1_Simple_Aggregation': [s for s in all_signals if s.get('level') == 'Level_1_Simple_Aggregation'],
                'Level_2_Derived_Metrics': [s for s in all_signals if s.get('level') == 'Level_2_Derived_Metrics'],
                'Level_3_Complex_Ratios': [s for s in all_signals if s.get('level') == 'Level_3_Complex_Ratios'],
                'Level_4_Market_Sentiment': [s for s in all_signals if s.get('level') == 'Level_4_Market_Sentiment']
            },
            'programmatic_vs_manual': self._categorize_by_feasibility(all_signals),
            'acquisition_strategy': self._create_acquisition_strategy(all_signals),
            'raw_signals': all_signals
        }
    
    def _extract_primary_signals(self, thesis_text: str, processed_documents: List[Dict], ai_signals: List[Dict]) -> Dict[str, Any]:
        """Extract only Level 0-1 signals for focused analysis"""
        primary_signals = []
        
        # Level 0: Raw Economic Activity
        level_0_signals = self._extract_level_0_comprehensive(thesis_text, processed_documents)
        
        # Level 1: Simple Aggregation  
        level_1_signals = self._extract_level_1_comprehensive(thesis_text, processed_documents)
        
        primary_signals.extend(level_0_signals)
        primary_signals.extend(level_1_signals)
        
        return {
            'focused_analysis': True,
            'total_signals_identified': len(primary_signals),
            'primary_signals_count': len(primary_signals),
            'signals_by_level': {
                'Level_0_Raw_Economic': [s for s in primary_signals if s.get('level') == 'Level_0_Raw_Economic'],
                'Level_1_Simple_Aggregation': [s for s in primary_signals if s.get('level') == 'Level_1_Simple_Aggregation']
            },
            'raw_signals': primary_signals
        }

    def extract_signals_from_analysis(self, thesis_text: str, processed_documents: List[Dict], focus_primary: bool = True) -> Dict[str, Any]:
        """
        Extract and classify signals from thesis and supporting documents
        """
        try:
            all_signals = []
            document_texts = []
            
            # Extract text from processed documents
            for doc in processed_documents:
                doc_data = doc.get('data', {})
                if 'text_content' in doc_data:
                    document_texts.append(doc_data['text_content'])
                if 'summary' in doc_data:
                    document_texts.append(doc_data['summary'])
            
            # Combine all text sources
            combined_text = thesis_text + ' ' + ' '.join(document_texts)
            
            # Extract signals by level
            level_0_signals = self._extract_level_0_signals(combined_text)
            level_1_signals = self._extract_level_1_signals(combined_text)
            level_2_signals = self._extract_level_2_signals(combined_text)
            
            # Combine all signals
            all_signals.extend(level_0_signals)
            all_signals.extend(level_1_signals)
            all_signals.extend(level_2_signals)
            
            # If focusing on primary signals, prioritize Level 0-1
            if focus_primary:
                primary_signals = [s for s in all_signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]]
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
            logging.error(f"Error in signal extraction: {str(e)}")
            return {'error': str(e)}
    
    def _extract_level_0_signals(self, text: str) -> List[Signal]:
        """Extract Level 0 (raw economic activity) signals"""
        signals = []
        text_lower = text.lower()
        
        for category, patterns in self.level_0_indicators.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    # Extract context around the signal
                    context = self._extract_signal_context(text, pattern)
                    
                    signal = Signal(
                        name=pattern.title(),
                        level=SignalLevel.LEVEL_0,
                        description=f"Raw economic activity: {pattern}",
                        data_source="Document analysis",
                        value_chain_position=self._determine_value_chain_position(pattern),
                        predictive_power=self._assess_predictive_power(pattern, context),
                        market_attention="low",  # Level 0 signals typically have low market attention
                        lead_lag_indicator="leading",  # Level 0 signals are typically leading
                        raw_data_points=[pattern],
                        collection_frequency=self._estimate_collection_frequency(pattern),
                        reliability_score=self._calculate_reliability_score(pattern, context)
                    )
                    signals.append(signal)
        
        return signals
    
    def _extract_level_1_signals(self, text: str) -> List[Signal]:
        """Extract Level 1 (simple aggregation) signals"""
        signals = []
        text_lower = text.lower()
        
        for category, patterns in self.level_1_indicators.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    context = self._extract_signal_context(text, pattern)
                    
                    signal = Signal(
                        name=pattern.title(),
                        level=SignalLevel.LEVEL_1,
                        description=f"Simple aggregation: {pattern}",
                        data_source="Document analysis",
                        value_chain_position=self._determine_value_chain_position(pattern),
                        predictive_power=self._assess_predictive_power(pattern, context),
                        market_attention="low",
                        lead_lag_indicator="leading",
                        raw_data_points=[pattern],
                        derivation_method="Simple aggregation or basic mathematical operation",
                        collection_frequency=self._estimate_collection_frequency(pattern),
                        reliability_score=self._calculate_reliability_score(pattern, context)
                    )
                    signals.append(signal)
        
        return signals
    
    def _extract_level_2_signals(self, text: str) -> List[Signal]:
        """Extract Level 2 (derived metrics) signals"""
        signals = []
        
        # Look for ratio indicators, growth rates, percentages
        ratio_patterns = [
            r'(\w+)\s+ratio', r'(\w+)\s+rate', r'(\w+)\s+percentage',
            r'(\w+)\s+growth', r'(\w+)\s+margin', r'(\w+)\s+yield',
            r'(\w+)\s+efficiency', r'(\w+)\s+productivity'
        ]
        
        for pattern in ratio_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                metric_name = match.group(1).title() + " " + match.group(0).split()[-1].title()
                context = self._extract_signal_context(text, match.group(0))
                
                signal = Signal(
                    name=metric_name,
                    level=SignalLevel.LEVEL_2,
                    description=f"Derived metric: {metric_name}",
                    data_source="Document analysis",
                    value_chain_position=self._determine_value_chain_position(metric_name),
                    predictive_power=self._assess_predictive_power(metric_name, context),
                    market_attention="medium",
                    lead_lag_indicator="coincident",
                    raw_data_points=[match.group(0)],
                    derivation_method="Mathematical calculation from Level 0/1 signals",
                    collection_frequency=self._estimate_collection_frequency(metric_name),
                    reliability_score=self._calculate_reliability_score(metric_name, context)
                )
                signals.append(signal)
        
        return signals
    
    def _extract_signal_context(self, text: str, signal: str) -> str:
        """Extract surrounding context for a signal"""
        signal_index = text.lower().find(signal.lower())
        if signal_index == -1:
            return ""
        
        start = max(0, signal_index - 100)
        end = min(len(text), signal_index + len(signal) + 100)
        return text[start:end]
    
    def _determine_value_chain_position(self, signal: str) -> str:
        """Determine the value chain position of a signal"""
        signal_lower = signal.lower()
        
        for position, keywords in self.value_chain_keywords.items():
            if any(keyword in signal_lower for keyword in keywords):
                return position
        
        return "unknown"
    
    def _assess_predictive_power(self, signal: str, context: str) -> str:
        """Assess the predictive power of a signal"""
        combined_text = (signal + " " + context).lower()
        
        for power_level, keywords in self.predictive_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return power_level.replace('_predictive', '')
        
        # Default assessment based on signal characteristics
        if any(word in signal.lower() for word in ['permit', 'application', 'order', 'booking']):
            return "high"
        elif any(word in signal.lower() for word in ['production', 'manufacturing', 'activity']):
            return "medium"
        else:
            return "low"
    
    def _estimate_collection_frequency(self, signal: str) -> str:
        """Estimate how frequently a signal can be collected"""
        signal_lower = signal.lower()
        
        if any(word in signal_lower for word in ['daily', 'real-time', 'hourly']):
            return "daily"
        elif any(word in signal_lower for word in ['weekly', 'week']):
            return "weekly"
        elif any(word in signal_lower for word in ['monthly', 'month']):
            return "monthly"
        elif any(word in signal_lower for word in ['quarterly', 'quarter']):
            return "quarterly"
        elif any(word in signal_lower for word in ['annual', 'yearly']):
            return "annual"
        else:
            return "unknown"
    
    def _calculate_reliability_score(self, signal: str, context: str) -> float:
        """Calculate a reliability score for the signal (0.0 to 1.0)"""
        score = 0.5  # Base score
        
        # Boost score for objective measurements
        if any(word in signal.lower() for word in ['count', 'volume', 'quantity', 'number']):
            score += 0.2
        
        # Boost for regulatory or official sources
        if any(word in context.lower() for word in ['government', 'regulatory', 'official', 'census']):
            score += 0.2
        
        # Reduce for subjective measures
        if any(word in signal.lower() for word in ['sentiment', 'opinion', 'perception', 'feeling']):
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _analyze_signal_relationships(self, signals: List[Signal]) -> Dict[str, Any]:
        """Analyze relationships between identified signals"""
        relationships = {
            'lead_lag_chains': [],
            'value_chain_flows': [],
            'correlation_clusters': []
        }
        
        # Group signals by value chain position
        by_position = {}
        for signal in signals:
            position = signal.value_chain_position
            if position not in by_position:
                by_position[position] = []
            by_position[position].append(signal)
        
        # Create value chain flows
        if 'upstream' in by_position and 'downstream' in by_position:
            relationships['value_chain_flows'].append({
                'from': 'upstream',
                'to': 'downstream',
                'upstream_signals': [s.name for s in by_position['upstream']],
                'downstream_signals': [s.name for s in by_position['downstream']],
                'relationship_type': 'supply_chain_flow'
            })
        
        return relationships
    
    def _create_value_chain_mapping(self, signals: List[Signal]) -> Dict[str, List[str]]:
        """Create a mapping of signals by value chain position"""
        mapping = {
            'upstream': [],
            'midstream': [],
            'downstream': [],
            'unknown': []
        }
        
        for signal in signals:
            position = signal.value_chain_position
            if position in mapping:
                mapping[position].append(signal.name)
            else:
                mapping['unknown'].append(signal.name)
        
        return mapping
    
    def _assess_signal_quality(self, signals: List[Signal]) -> Dict[str, Any]:
        """Assess overall quality of identified signals"""
        if not signals:
            return {'overall_score': 0, 'assessment': 'No signals identified'}
        
        primary_count = len([s for s in signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]])
        total_count = len(signals)
        primary_ratio = primary_count / total_count if total_count > 0 else 0
        
        avg_reliability = sum(s.reliability_score for s in signals) / len(signals)
        
        overall_score = (primary_ratio * 0.6) + (avg_reliability * 0.4)
        
        assessment = "Excellent" if overall_score > 0.8 else \
                    "Good" if overall_score > 0.6 else \
                    "Fair" if overall_score > 0.4 else "Poor"
        
        return {
            'overall_score': round(overall_score, 2),
            'assessment': assessment,
            'primary_signal_ratio': round(primary_ratio, 2),
            'average_reliability': round(avg_reliability, 2),
            'recommendations': self._generate_quality_recommendations(signals, overall_score)
        }
    
    def _generate_quality_recommendations(self, signals: List[Signal], score: float) -> List[str]:
        """Generate recommendations for improving signal quality"""
        recommendations = []
        
        primary_count = len([s for s in signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]])
        total_count = len(signals)
        
        if primary_count / total_count < 0.5:
            recommendations.append("Focus on identifying more Level 0-1 (primary) signals for better predictive power")
        
        if score < 0.6:
            recommendations.append("Consider seeking additional data sources for higher reliability signals")
        
        low_reliability_signals = [s for s in signals if s.reliability_score < 0.4]
        if low_reliability_signals:
            recommendations.append(f"Validate {len(low_reliability_signals)} signals with low reliability scores")
        
        return recommendations
    
    def _recommend_monitoring_strategy(self, signals: List[Signal], focus_primary: bool) -> Dict[str, Any]:
        """Recommend a monitoring strategy based on identified signals"""
        primary_signals = [s for s in signals if s.level in [SignalLevel.LEVEL_0, SignalLevel.LEVEL_1]]
        high_predictive = [s for s in signals if s.predictive_power == "high"]
        
        strategy = {
            'priority_signals': [s.name for s in primary_signals[:5]],  # Top 5 primary signals
            'monitoring_frequency': 'weekly',
            'data_sources_needed': list(set(s.data_source for s in signals)),
            'automation_opportunities': []
        }
        
        # Identify automation opportunities
        frequent_signals = [s for s in signals if s.collection_frequency in ['daily', 'weekly']]
        if frequent_signals:
            strategy['automation_opportunities'] = [s.name for s in frequent_signals[:3]]
        
        return strategy
    
    def _group_signals_by_level(self, signals: List[Signal]) -> Dict[str, List[str]]:
        """Group signals by their classification level"""
        grouped = {}
        for signal in signals:
            level_name = signal.level.value
            if level_name not in grouped:
                grouped[level_name] = []
            grouped[level_name].append(signal.name)
        
        return grouped
    
    def _signal_to_dict(self, signal: Signal) -> Dict[str, Any]:
        """Convert Signal object to dictionary"""
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
            'correlation_signals': signal.correlation_signals or [],
            'collection_frequency': signal.collection_frequency,
            'reliability_score': signal.reliability_score
        }
    
    def _extract_level_0_comprehensive(self, thesis_text: str, processed_documents: List[Dict]) -> List[Dict]:
        """Extract Level 0 (Raw Economic Activity) signals with acquisition guidance"""
        signals = []
        text_lower = thesis_text.lower()
        
        # Energy/Utility specific Level 0 signals
        if any(keyword in text_lower for keyword in ['renewable', 'capacity', 'mw', 'gw', 'wind', 'solar']):
            signals.append({
                'name': 'Quarterly Renewables Capacity Additions (MW)',
                'level': 'Level_0_Raw_Economic',
                'description': 'New renewable capacity (MW) added each quarter',
                'data_source': 'Company Filings/EIA Data',
                'programmatic_feasibility': 'medium',
                'acquisition_method': 'Parse quarterly earnings reports, 10-K filings, EIA Electric Power Monthly',
                'frequency': 'quarterly'
            })
        
        # Production/Volume signals
        if any(keyword in text_lower for keyword in ['units', 'production', 'volume', 'output']):
            signals.append({
                'name': 'Power Generation Volume (MWh)',
                'level': 'Level_0_Raw_Economic',
                'description': 'Direct measurement of electricity production',
                'data_source': 'Company Reports/EIA',
                'programmatic_feasibility': 'medium',
                'acquisition_method': 'Quarterly earnings reports, EIA-923 forms',
                'frequency': 'quarterly'
            })
        
        # Customer/Connection signals
        if any(keyword in text_lower for keyword in ['customer', 'connection', 'account', 'subscriber']):
            signals.append({
                'name': 'Customer Account Growth',
                'level': 'Level_0_Raw_Economic',
                'description': 'Net new customer connections',
                'data_source': 'Utility Commission Filings',
                'programmatic_feasibility': 'medium',
                'acquisition_method': 'State utility commission monthly reports',
                'frequency': 'monthly'
            })
        
        # Pipeline/Project signals
        if any(keyword in text_lower for keyword in ['pipeline', 'project', 'development', 'construction']):
            signals.append({
                'name': 'Project Pipeline Backlog (GW)',
                'level': 'Level_0_Raw_Economic',
                'description': 'Committed renewable projects under development',
                'data_source': 'Company Reports',
                'programmatic_feasibility': 'low',
                'acquisition_method': 'Manual extraction from investor presentations and development updates',
                'alternative_sources': ['Wood Mackenzie Power & Renewables', 'BNEF project database'],
                'frequency': 'quarterly'
            })
            
        return signals
    
    def _extract_level_1_comprehensive(self, thesis_text: str, processed_documents: List[Dict]) -> List[Dict]:
        """Extract Level 1 (Simple Aggregation) signals"""
        signals = []
        text_lower = thesis_text.lower()
        
        # Revenue signals
        if any(keyword in text_lower for keyword in ['revenue', 'sales', 'growth']):
            signals.append({
                'name': 'Quarterly Revenue Growth',
                'level': 'Level_1_Simple_Aggregation',
                'description': 'Revenue growth rate calculation',
                'data_source': 'FactSet Fundamentals',
                'programmatic_feasibility': 'high',
                'factset_identifier': 'FF_SALES(0)/FF_SALES(-1)-1',
                'frequency': 'quarterly'
            })
            
        # Margin signals
        if any(keyword in text_lower for keyword in ['margin', 'profitability', 'efficiency']):
            signals.append({
                'name': 'Operating Margin',
                'level': 'Level_1_Simple_Aggregation', 
                'description': 'Operating income as percentage of revenue',
                'data_source': 'FactSet Fundamentals',
                'programmatic_feasibility': 'high',
                'factset_identifier': 'FF_OPER_INC/FF_SALES',
                'frequency': 'quarterly'
            })
            
        return signals
    
    def _extract_level_2_comprehensive(self, thesis_text: str, processed_documents: List[Dict]) -> List[Dict]:
        """Extract Level 2 (Derived Metrics) signals"""
        signals = []
        text_lower = thesis_text.lower()
        
        # Cost of capital signals (always include for utility analysis)
        signals.append({
            'name': 'Weighted Average Cost of Capital (WACC)',
            'level': 'Level_2_Derived_Metrics',
            'description': "Company's blended cost of debt and equity capital",
            'data_source': 'Bloomberg/S&P Capital IQ',
            'programmatic_feasibility': 'medium',
            'calculation': '(E/V × Re) + (D/V × Rd × (1-Tc))',
            'required_inputs': ['Market Cap', 'Total Debt', 'Risk-free Rate', 'Beta', 'Market Risk Premium', 'Cost of Debt', 'Tax Rate'],
            'acquisition_method': 'Combine FactSet financials with Bloomberg risk metrics and treasury rates',
            'frequency': 'quarterly'
        })
        
        # Return metrics
        if any(keyword in text_lower for keyword in ['return', 'roe', 'roic', 'efficiency', 'capital']):
            signals.append({
                'name': 'Return on Invested Capital (ROIC)',
                'level': 'Level_2_Derived_Metrics',
                'description': 'NOPAT divided by invested capital',
                'data_source': 'FactSet Calculated',
                'programmatic_feasibility': 'medium',
                'calculation': '(Net Income + Interest Expense * (1-Tax Rate)) / Invested Capital',
                'required_inputs': ['Net Income', 'Interest Expense', 'Tax Rate', 'Total Debt', 'Shareholders Equity'],
                'frequency': 'quarterly'
            })
        
        # Regulatory/Rate metrics
        if any(keyword in text_lower for keyword in ['regulatory', 'rate', 'commission', 'utility']):
            signals.append({
                'name': 'Regulatory ROE vs Authorized ROE',
                'level': 'Level_2_Derived_Metrics',
                'description': 'Actual earned ROE relative to utility commission authorized returns',
                'data_source': 'Utility Commission Filings',
                'programmatic_feasibility': 'low',
                'acquisition_method': 'Manual analysis of state utility commission rate case decisions and earnings reports',
                'alternative_sources': ['SNL Energy', 'Regulatory Research Associates', 'State PSC websites'],
                'frequency': 'annual'
            })
            
        # Cash flow efficiency
        if any(keyword in text_lower for keyword in ['cash', 'flow', 'generation', 'conversion']):
            signals.append({
                'name': 'Free Cash Flow Conversion Rate',
                'level': 'Level_2_Derived_Metrics',
                'description': 'Free cash flow as percentage of net income',
                'data_source': 'FactSet Fundamentals',
                'programmatic_feasibility': 'high',
                'factset_identifier': 'FF_FREE_CASH_FLOW / FF_NI',
                'frequency': 'quarterly'
            })
            
        return signals
    
    def _extract_level_3_comprehensive(self, thesis_text: str, processed_documents: List[Dict]) -> List[Dict]:
        """Extract Level 3 (Complex Ratios) signals"""
        signals = []
        text_lower = thesis_text.lower()
        
        # Peer relative performance (always include for comparative thesis)
        if any(keyword in text_lower for keyword in ['peer', 'outperform', 'relative', 'versus', 'compare']):
            signals.append({
                'name': 'Utility Peer Relative Total Shareholder Return',
                'level': 'Level_3_Complex_Ratios',
                'description': 'TSR performance relative to utility peer group',
                'data_source': 'FactSet/Bloomberg',
                'programmatic_feasibility': 'high',
                'calculation': 'NextEra_TSR / Utility_Peer_Group_Average_TSR',
                'required_inputs': ['Price Returns', 'Dividend Yields', 'Peer Group Constituents'],
                'factset_identifier': 'P_TOTAL_RETURN_1YR vs XLU constituents',
                'frequency': 'monthly'
            })
        
        # Valuation multiples
        if any(keyword in text_lower for keyword in ['valuation', 'multiple', 'ev/ebitda', 'p/e', 'premium', 'discount']):
            signals.append({
                'name': 'P/E Ratio vs Utility Sector Median',
                'level': 'Level_3_Complex_Ratios',
                'description': 'Valuation premium/discount to utility sector',
                'data_source': 'FactSet/Bloomberg',
                'programmatic_feasibility': 'medium',
                'calculation': '(NextEra_PE / Utility_Sector_Median_PE) - 1',
                'required_inputs': ['Market Cap', 'Net Income', 'Sector P/E Multiples'],
                'frequency': 'daily'
            })
            
        # Efficiency ratios
        if any(keyword in text_lower for keyword in ['efficiency', 'productivity', 'asset utilization']):
            signals.append({
                'name': 'Asset Turnover vs Regulated Utility Average',
                'level': 'Level_3_Complex_Ratios',
                'description': 'Revenue generation efficiency per dollar of assets',
                'data_source': 'FactSet Calculated',
                'programmatic_feasibility': 'medium',
                'calculation': '(Revenue / Total_Assets) / Regulated_Utility_Average_Asset_Turnover',
                'required_inputs': ['Revenue', 'Total Assets', 'Industry Benchmarks'],
                'frequency': 'quarterly'
            })
            
        # Economic value creation
        if any(keyword in text_lower for keyword in ['value creation', 'economic value', 'eva', 'spread']):
            signals.append({
                'name': 'ROIC vs WACC Spread',
                'level': 'Level_3_Complex_Ratios',
                'description': 'Value creation measured as ROIC minus cost of capital',
                'data_source': 'Manual Calculation Required',
                'programmatic_feasibility': 'low',
                'calculation': 'ROIC - WACC',
                'acquisition_method': 'Combine FactSet ROIC calculation with manual WACC from Bloomberg cost of capital estimates',
                'required_inputs': ['NOPAT', 'Invested Capital', 'Risk-free Rate', 'Beta', 'Market Risk Premium', 'Cost of Debt'],
                'frequency': 'quarterly'
            })
            
        return signals
    
    def _extract_level_4_comprehensive(self, thesis_text: str, processed_documents: List[Dict]) -> List[Dict]:
        """Extract Level 4 (Market Sentiment) signals"""
        signals = []
        text_lower = thesis_text.lower()
        
        # Analyst sentiment
        if any(keyword in text_lower for keyword in ['analyst', 'estimates', 'recommendations']):
            signals.append({
                'name': 'Analyst Estimate Revisions Momentum',
                'level': 'Level_4_Market_Sentiment',
                'description': 'Net upward/downward estimate revisions',
                'data_source': 'Manual Research Required',
                'programmatic_feasibility': 'low',
                'acquisition_method': 'Track estimate changes via Bloomberg IBES, FactSet Estimates, or Refinitiv IBES Detail. Calculate monthly net revision ratio.',
                'alternative_sources': ['Zacks Investment Research', 'Yahoo Finance Analyst Data', 'MarketWatch estimates'],
                'calculation': '(Upward Revisions - Downward Revisions) / Total Analyst Count',
                'frequency': 'monthly'
            })
            
        # Management guidance accuracy
        signals.append({
            'name': 'Management Guidance Accuracy Score',
            'level': 'Level_4_Market_Sentiment',
            'description': 'Historical accuracy of management forecasts',
            'data_source': 'Manual Research Required',
            'programmatic_feasibility': 'low',
            'acquisition_method': 'Extract guidance from earnings transcripts (FactSet Transcripts, Seeking Alpha), compare to actual results over 8 quarters. Calculate accuracy percentage.',
            'alternative_sources': ['Capital IQ Transcripts', 'Thomson Reuters StreetEvents', 'Company IR websites'],
            'calculation': '1 - Average(|Guided_Value - Actual_Value| / Actual_Value)',
            'frequency': 'quarterly'
        })
        
        # Options flow sentiment
        if any(keyword in text_lower for keyword in ['sentiment', 'options', 'volatility']):
            signals.append({
                'name': 'Put/Call Ratio Trend',
                'level': 'Level_4_Market_Sentiment',
                'description': 'Options sentiment indicator',
                'data_source': 'Bloomberg/CBOE',
                'programmatic_feasibility': 'medium',
                'acquisition_method': 'Bloomberg Terminal OMON function or CBOE data feeds. Calculate 20-day moving average.',
                'alternative_sources': ['Yahoo Finance Options', 'Barchart Options Flow', 'TradingView Options Data'],
                'frequency': 'daily'
            })
            
        return signals
    
    def _assess_acquisition_feasibility(self, signal: Dict) -> Dict[str, Any]:
        """Assess how easily a signal can be acquired programmatically"""
        feasibility = signal.get('programmatic_feasibility', 'unknown')
        
        guidance = {
            'feasibility': feasibility,
            'automation_potential': 'high' if feasibility == 'high' else 'low',
            'estimated_setup_time': {
                'high': '1-2 days',
                'medium': '1-2 weeks', 
                'low': '2-4 weeks'
            }.get(feasibility, 'unknown')
        }
        
        if feasibility == 'low':
            guidance['manual_research_required'] = True
            guidance['suggested_workflow'] = signal.get('acquisition_method', 'Research via company reports and industry sources')
            guidance['alternative_sources'] = signal.get('alternative_sources', [])
            
        return guidance
    
    def _categorize_by_feasibility(self, signals: List[Dict]) -> Dict[str, Any]:
        """Categorize signals by acquisition feasibility"""
        high_feasibility = [s for s in signals if s.get('programmatic_feasibility') == 'high']
        medium_feasibility = [s for s in signals if s.get('programmatic_feasibility') == 'medium']
        low_feasibility = [s for s in signals if s.get('programmatic_feasibility') == 'low']
        
        return {
            'programmatic_signals': {
                'count': len(high_feasibility),
                'signals': [s['name'] for s in high_feasibility],
                'description': 'Can be automated via FactSet/Xpressfeed APIs'
            },
            'semi_programmatic_signals': {
                'count': len(medium_feasibility),
                'signals': [s['name'] for s in medium_feasibility],
                'description': 'Require calculation from multiple data sources'
            },
            'manual_research_signals': {
                'count': len(low_feasibility),
                'signals': [s['name'] for s in low_feasibility],
                'description': 'Require manual data collection and analysis'
            }
        }
    
    def _create_acquisition_strategy(self, signals: List[Dict]) -> Dict[str, Any]:
        """Create a strategic plan for acquiring all identified signals"""
        high_priority = [s for s in signals if s.get('level') in ['Level_0_Raw_Economic', 'Level_1_Simple_Aggregation']]
        medium_priority = [s for s in signals if s.get('level') in ['Level_2_Derived_Metrics', 'Level_3_Complex_Ratios']]
        low_priority = [s for s in signals if s.get('level') == 'Level_4_Market_Sentiment']
        
        return {
            'implementation_phases': {
                'Phase_1_Foundation': {
                    'timeline': '1-2 weeks',
                    'signals': [s['name'] for s in high_priority if s.get('programmatic_feasibility') == 'high'],
                    'approach': 'Set up FactSet/Xpressfeed API connections for core financial metrics'
                },
                'Phase_2_Enhanced': {
                    'timeline': '3-4 weeks',
                    'signals': [s['name'] for s in medium_priority],
                    'approach': 'Build calculation engines for derived metrics'
                },
                'Phase_3_Advanced': {
                    'timeline': '6-8 weeks',
                    'signals': [s['name'] for s in low_priority],
                    'approach': 'Establish manual research workflows for sentiment indicators'
                }
            },
            'resource_requirements': {
                'api_subscriptions': ['FactSet Fundamentals', 'Xpressfeed Market Data'],
                'manual_research_tools': ['Bloomberg Terminal', 'Capital IQ', 'Company IR websites'],
                'development_effort': f'{len([s for s in signals if s.get("programmatic_feasibility") == "high"])} automated signals, {len([s for s in signals if s.get("programmatic_feasibility") == "low"])} manual processes'
            }
        }