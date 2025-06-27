"""
One Pager Service
Consolidates all analysis data into comprehensive investment reports
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from models import ThesisAnalysis, DocumentUpload, SignalMonitoring, NotificationLog
from services.azure_openai_service import AzureOpenAIService
from services.alternative_company_service import AlternativeCompanyService
from app import db


class OnePagerService:
    """Service for generating comprehensive one-pager investment reports"""
    
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        self.alternative_service = AlternativeCompanyService()
    
    def generate_comprehensive_report(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """
        Generate comprehensive one-pager report organized around thesis validation framework
        """
        try:
            # 1. Executive Summary
            executive_summary = self._generate_executive_summary(thesis)
            
            # 2. Core Claim Validation Framework
            core_claim_validation = self._build_core_claim_validation(thesis)
            
            # 3. Assumption Testing Framework
            assumption_testing = self._build_assumption_testing_framework(thesis)
            
            # 4. Causal Chain Tracking
            causal_chain_tracking = self._build_causal_chain_tracking(thesis)
            
            # 5. Data Acquisition Plan
            data_acquisition_plan = self._build_data_acquisition_plan(thesis)
            
            # 6. Thesis Structure & Logic
            thesis_structure = self._extract_thesis_structure(thesis)
            
            # 7. Alternative Investment Ideas
            alternative_investments = self._get_alternative_investments(thesis)
            
            # 8. Evaluation Criteria for PMs/Analysts
            evaluation_criteria = self._generate_evaluation_criteria(thesis)
            
            # Compile comprehensive report
            report_data = {
                'generated_at': datetime.utcnow().isoformat(),
                'thesis_id': thesis.id,
                'thesis_title': thesis.title,
                'executive_summary': executive_summary,
                'core_claim_validation': core_claim_validation,
                'assumption_testing': assumption_testing,
                'causal_chain_tracking': causal_chain_tracking,
                'data_acquisition_plan': data_acquisition_plan,
                'thesis_structure': thesis_structure,
                'alternative_investments': alternative_investments,
                'evaluation_criteria': evaluation_criteria
            }
            
            return report_data
            
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
            return self._generate_fallback_report(thesis)
    
    def _build_core_claim_validation(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Build core claim validation framework with specific metrics"""
        try:
            # Get signals and break them down by core claim relevance
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis.id).all()
            
            # Decompose composite metrics into validation components
            validation_metrics = []
            for signal in signals:
                metric_breakdown = self._decompose_signal_to_validation_metrics(signal, thesis.core_claim)
                validation_metrics.extend(metric_breakdown)
            
            # Group by validation type
            core_validation_plan = {
                'primary_validators': [m for m in validation_metrics if m['validation_type'] == 'primary'],
                'supporting_validators': [m for m in validation_metrics if m['validation_type'] == 'supporting'],
                'contrarian_indicators': [m for m in validation_metrics if m['validation_type'] == 'contrarian'],
                'validation_frequency': self._determine_validation_frequency(validation_metrics),
                'success_criteria': self._define_validation_success_criteria(thesis.core_claim, validation_metrics)
            }
            
            return core_validation_plan
            
        except Exception as e:
            print(f"Error building core claim validation: {e}")
            return {
                'primary_validators': [],
                'supporting_validators': [],
                'contrarian_indicators': [],
                'validation_frequency': 'Weekly',
                'success_criteria': 'Comprehensive validation pending'
            }
    
    def _build_assumption_testing_framework(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Build assumption testing framework with specific data points"""
        try:
            assumptions = thesis.assumptions if isinstance(thesis.assumptions, list) else []
            
            assumption_tests = []
            for assumption in assumptions:
                test_framework = self._create_assumption_test(assumption, thesis)
                assumption_tests.append(test_framework)
            
            return {
                'total_assumptions': len(assumptions),
                'assumption_tests': assumption_tests,
                'testing_methodology': self._define_testing_methodology(assumption_tests),
                'validation_timeline': self._create_assumption_validation_timeline(assumption_tests),
                'risk_weighted_priorities': self._prioritize_assumptions_by_risk(assumption_tests)
            }
            
        except Exception as e:
            print(f"Error building assumption testing framework: {e}")
            return {
                'total_assumptions': 0,
                'assumption_tests': [],
                'testing_methodology': 'Comprehensive testing framework pending',
                'validation_timeline': {},
                'risk_weighted_priorities': []
            }
    
    def _build_causal_chain_tracking(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Build causal chain tracking with specific monitoring points"""
        try:
            causal_chain = thesis.causal_chain if isinstance(thesis.causal_chain, list) else []
            
            tracking_points = []
            for i, chain_element in enumerate(causal_chain):
                tracking_point = self._create_causal_tracking_point(chain_element, i, thesis)
                tracking_points.append(tracking_point)
            
            # Identify critical linkages
            critical_linkages = self._identify_critical_linkages(tracking_points)
            
            return {
                'chain_length': len(causal_chain),
                'tracking_points': tracking_points,
                'critical_linkages': critical_linkages,
                'monitoring_framework': self._create_causal_monitoring_framework(tracking_points),
                'failure_scenarios': self._identify_causal_failure_scenarios(tracking_points)
            }
            
        except Exception as e:
            print(f"Error building causal chain tracking: {e}")
            return {
                'chain_length': 0,
                'tracking_points': [],
                'critical_linkages': [],
                'monitoring_framework': {},
                'failure_scenarios': []
            }
    
    def _build_data_acquisition_plan(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Build comprehensive data acquisition plan with specific sources and metrics"""
        try:
            # Get all signals and their data requirements
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis.id).all()
            
            data_requirements = []
            for signal in signals:
                requirement = self._extract_data_requirement(signal, thesis)
                data_requirements.append(requirement)
            
            # Organize by data source and priority
            acquisition_plan = {
                'primary_data_sources': self._categorize_by_source(data_requirements, 'primary'),
                'alternative_data_sources': self._categorize_by_source(data_requirements, 'alternative'),
                'internal_data_needs': self._categorize_by_source(data_requirements, 'internal'),
                'acquisition_timeline': self._create_acquisition_timeline(data_requirements),
                'cost_benefit_analysis': self._analyze_data_costs(data_requirements),
                'data_quality_standards': self._define_quality_standards(data_requirements)
            }
            
            return acquisition_plan
            
        except Exception as e:
            print(f"Error building data acquisition plan: {e}")
            return {
                'primary_data_sources': [],
                'alternative_data_sources': [],
                'internal_data_needs': [],
                'acquisition_timeline': {},
                'cost_benefit_analysis': {},
                'data_quality_standards': {}
            }
    
    def _decompose_signal_to_validation_metrics(self, signal: SignalMonitoring, core_claim: str) -> List[Dict[str, Any]]:
        """Decompose composite signals into specific validation metrics"""
        validation_metrics = []
        signal_name = signal.signal_name.lower()
        
        # For revenue signals, break down into specific validation components
        if 'revenue' in signal_name and 'growth' in signal_name:
            validation_metrics.extend([
                {
                    'metric_name': 'Quarterly Revenue Growth Rate',
                    'validation_type': 'primary',
                    'data_source': 'Company Earnings Reports',
                    'frequency': 'Quarterly',
                    'success_threshold': f'>= {signal.threshold_value}%' if signal.threshold_value else '>= 10%',
                    'relevance_to_claim': 'Direct validation of revenue growth assumptions'
                },
                {
                    'metric_name': 'Year-over-Year Revenue Comparison',
                    'validation_type': 'supporting',
                    'data_source': 'Financial Statements',
                    'frequency': 'Monthly',
                    'success_threshold': 'Positive trend sustained',
                    'relevance_to_claim': 'Confirms sustainable growth pattern'
                },
                {
                    'metric_name': 'Revenue Quality Assessment',
                    'validation_type': 'supporting',
                    'data_source': 'Segment Reporting',
                    'frequency': 'Quarterly',
                    'success_threshold': 'Recurring > 80% of total',
                    'relevance_to_claim': 'Validates revenue sustainability'
                }
            ])
        
        # For market position signals
        elif 'market' in signal_name and ('position' in signal_name or 'share' in signal_name):
            validation_metrics.extend([
                {
                    'metric_name': 'Market Share Percentage',
                    'validation_type': 'primary',
                    'data_source': 'Industry Research Reports',
                    'frequency': 'Quarterly',
                    'success_threshold': 'Maintain or increase share',
                    'relevance_to_claim': 'Validates competitive positioning'
                },
                {
                    'metric_name': 'Customer Win-Loss Ratio',
                    'validation_type': 'supporting',
                    'data_source': 'Sales Data',
                    'frequency': 'Monthly',
                    'success_threshold': 'Win rate > 60%',
                    'relevance_to_claim': 'Confirms competitive advantage'
                },
                {
                    'metric_name': 'Brand Recognition Index',
                    'validation_type': 'contrarian',
                    'data_source': 'Consumer Surveys',
                    'frequency': 'Semi-annually',
                    'success_threshold': 'Top 3 in category',
                    'relevance_to_claim': 'Tests brand strength assumptions'
                }
            ])
        
        # For profitability signals
        elif 'margin' in signal_name or 'profit' in signal_name:
            validation_metrics.extend([
                {
                    'metric_name': 'Gross Margin Percentage',
                    'validation_type': 'primary',
                    'data_source': 'Income Statement',
                    'frequency': 'Quarterly',
                    'success_threshold': f'>= {signal.threshold_value}%' if signal.threshold_value else '>= 40%',
                    'relevance_to_claim': 'Validates pricing power and efficiency'
                },
                {
                    'metric_name': 'Operating Leverage',
                    'validation_type': 'supporting',
                    'data_source': 'Financial Analysis',
                    'frequency': 'Quarterly',
                    'success_threshold': 'Positive operating leverage',
                    'relevance_to_claim': 'Confirms scalability assumptions'
                }
            ])
        
        # Default breakdown for other signals
        else:
            validation_metrics.append({
                'metric_name': f'{signal.signal_name} Primary Validator',
                'validation_type': 'primary',
                'data_source': 'Primary Data Sources',
                'frequency': 'Monthly',
                'success_threshold': f'Target: {signal.threshold_value}' if signal.threshold_value else 'Above baseline',
                'relevance_to_claim': 'Validates core thesis assumptions'
            })
        
        return validation_metrics
    
    def _determine_validation_frequency(self, validation_metrics: List[Dict]) -> str:
        """Determine optimal validation frequency based on metrics"""
        frequencies = [m.get('frequency', 'Monthly') for m in validation_metrics]
        if 'Daily' in frequencies:
            return 'Daily'
        elif 'Weekly' in frequencies:
            return 'Weekly'
        elif 'Monthly' in frequencies:
            return 'Monthly'
        else:
            return 'Quarterly'
    
    def _define_validation_success_criteria(self, core_claim: str, validation_metrics: List[Dict]) -> str:
        """Define clear success criteria for core claim validation"""
        primary_metrics = [m for m in validation_metrics if m['validation_type'] == 'primary']
        
        if len(primary_metrics) >= 2:
            return f"Core claim validated when 80% of primary validation metrics meet success thresholds consistently over 2+ consecutive periods"
        elif len(primary_metrics) == 1:
            return f"Core claim validated when primary metric '{primary_metrics[0]['metric_name']}' meets {primary_metrics[0]['success_threshold']} for 3+ consecutive periods"
        else:
            return "Core claim validation criteria pending - requires primary validation metrics definition"
    
    def _create_assumption_test(self, assumption: str, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Create specific test framework for each assumption"""
        assumption_lower = assumption.lower() if isinstance(assumption, str) else str(assumption).lower()
        
        if 'growth' in assumption_lower:
            return {
                'assumption': assumption,
                'test_type': 'Growth Validation',
                'specific_metrics': ['Revenue Growth Rate', 'Market Expansion', 'Customer Acquisition'],
                'test_methodology': 'Quarterly trend analysis with peer benchmarking',
                'success_criteria': 'Sustained growth above market average',
                'risk_level': 'Medium',
                'testing_timeline': '6 months',
                'data_requirements': ['Financial statements', 'Market research', 'Customer data']
            }
        elif 'market' in assumption_lower:
            return {
                'assumption': assumption,
                'test_type': 'Market Validation',
                'specific_metrics': ['Market Share', 'TAM Analysis', 'Competitive Position'],
                'test_methodology': 'Market research and competitive analysis',
                'success_criteria': 'Market share maintenance or growth',
                'risk_level': 'High',
                'testing_timeline': '12 months',
                'data_requirements': ['Industry reports', 'Customer surveys', 'Competitive intelligence']
            }
        elif 'technology' in assumption_lower or 'innovation' in assumption_lower:
            return {
                'assumption': assumption,
                'test_type': 'Technology Validation',
                'specific_metrics': ['R&D Efficiency', 'Patent Portfolio', 'Innovation Pipeline'],
                'test_methodology': 'Technology assessment and competitive benchmarking',
                'success_criteria': 'Sustained technology leadership',
                'risk_level': 'High',
                'testing_timeline': '18 months',
                'data_requirements': ['R&D reports', 'Patent filings', 'Technology assessments']
            }
        else:
            return {
                'assumption': assumption,
                'test_type': 'General Validation',
                'specific_metrics': ['Performance indicators relevant to assumption'],
                'test_methodology': 'Systematic monitoring and analysis',
                'success_criteria': 'Assumption remains valid under testing',
                'risk_level': 'Medium',
                'testing_timeline': '9 months',
                'data_requirements': ['Relevant data sources for assumption validation']
            }
    
    def _define_testing_methodology(self, assumption_tests: List[Dict]) -> str:
        """Define comprehensive testing methodology"""
        if not assumption_tests:
            return "Testing methodology pending assumption identification"
        
        methodology = "Comprehensive assumption testing employs systematic validation across multiple dimensions: "
        
        test_types = list(set([test['test_type'] for test in assumption_tests]))
        methodology += f"Testing framework includes {', '.join(test_types)}. "
        
        methodology += "Each assumption undergoes structured validation through specific metrics, defined success criteria, and time-bound testing periods. "
        methodology += "Validation incorporates both quantitative analysis and qualitative assessment to ensure robust assumption testing."
        
        return methodology
    
    def _create_assumption_validation_timeline(self, assumption_tests: List[Dict]) -> Dict[str, Any]:
        """Create timeline for assumption validation"""
        timeline = {
            'immediate_tests': [],
            'short_term_tests': [],
            'long_term_tests': []
        }
        
        for test in assumption_tests:
            testing_period = test.get('testing_timeline', '9 months')
            if '3' in testing_period or '6' in testing_period:
                timeline['short_term_tests'].append(test['assumption'])
            elif '12' in testing_period or '18' in testing_period:
                timeline['long_term_tests'].append(test['assumption'])
            else:
                timeline['immediate_tests'].append(test['assumption'])
        
        return timeline
    
    def _prioritize_assumptions_by_risk(self, assumption_tests: List[Dict]) -> List[Dict[str, Any]]:
        """Prioritize assumptions by risk level and impact"""
        high_risk = [test for test in assumption_tests if test.get('risk_level') == 'High']
        medium_risk = [test for test in assumption_tests if test.get('risk_level') == 'Medium']
        low_risk = [test for test in assumption_tests if test.get('risk_level') == 'Low']
        
        return [
            {'priority': 'High Risk', 'assumptions': [t['assumption'] for t in high_risk]},
            {'priority': 'Medium Risk', 'assumptions': [t['assumption'] for t in medium_risk]},
            {'priority': 'Low Risk', 'assumptions': [t['assumption'] for t in low_risk]}
        ]
    
    def _create_causal_tracking_point(self, chain_element: str, position: int, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Create tracking point for causal chain element"""
        element_str = str(chain_element).lower()
        
        return {
            'position': position + 1,
            'element': chain_element,
            'tracking_metrics': self._identify_tracking_metrics_for_element(element_str),
            'validation_method': self._define_element_validation_method(element_str),
            'failure_indicators': self._identify_failure_indicators(element_str),
            'dependency_links': self._identify_dependencies(element_str, position),
            'monitoring_frequency': self._determine_element_monitoring_frequency(element_str)
        }
    
    def _identify_tracking_metrics_for_element(self, element: str) -> List[str]:
        """Identify specific metrics for tracking causal chain element"""
        if 'revenue' in element or 'sales' in element:
            return ['Monthly Revenue', 'Sales Volume', 'Average Deal Size', 'Conversion Rates']
        elif 'market' in element:
            return ['Market Share', 'Customer Acquisition', 'Brand Recognition', 'Competitive Position']
        elif 'cost' in element or 'efficiency' in element:
            return ['Unit Costs', 'Operating Margin', 'Productivity Metrics', 'Resource Utilization']
        else:
            return ['Performance Indicators', 'Key Metrics', 'Operational Data']
    
    def _define_element_validation_method(self, element: str) -> str:
        """Define validation method for causal chain element"""
        if 'revenue' in element:
            return 'Financial statement analysis with quarterly validation'
        elif 'market' in element:
            return 'Market research and competitive analysis'
        elif 'operational' in element:
            return 'Operational metrics tracking and efficiency analysis'
        else:
            return 'Systematic monitoring and data validation'
    
    def _identify_failure_indicators(self, element: str) -> List[str]:
        """Identify early warning indicators for element failure"""
        if 'revenue' in element:
            return ['Declining conversion rates', 'Customer churn increase', 'Pricing pressure']
        elif 'market' in element:
            return ['Market share loss', 'Competitive threats', 'Customer satisfaction decline']
        else:
            return ['Performance degradation', 'Threshold breaches', 'Trend reversals']
    
    def _identify_dependencies(self, element: str, position: int) -> List[str]:
        """Identify dependencies for causal chain element"""
        if position == 0:
            return ['Initial assumptions', 'Market conditions']
        else:
            return [f'Previous chain element {position}', 'Supporting factors', 'External conditions']
    
    def _determine_element_monitoring_frequency(self, element: str) -> str:
        """Determine monitoring frequency for element"""
        if 'critical' in element or 'core' in element:
            return 'Weekly'
        elif 'financial' in element or 'revenue' in element:
            return 'Monthly'
        else:
            return 'Quarterly'
    
    def _identify_critical_linkages(self, tracking_points: List[Dict]) -> List[Dict[str, Any]]:
        """Identify critical linkages in causal chain"""
        critical_linkages = []
        
        for i, point in enumerate(tracking_points):
            if i < len(tracking_points) - 1:
                linkage = {
                    'from_element': point['element'],
                    'to_element': tracking_points[i + 1]['element'],
                    'linkage_strength': 'High' if 'revenue' in str(point['element']).lower() else 'Medium',
                    'validation_requirements': f"Validate connection between {point['element']} and {tracking_points[i + 1]['element']}"
                }
                critical_linkages.append(linkage)
        
        return critical_linkages
    
    def _create_causal_monitoring_framework(self, tracking_points: List[Dict]) -> Dict[str, Any]:
        """Create comprehensive monitoring framework for causal chain"""
        return {
            'total_tracking_points': len(tracking_points),
            'monitoring_approach': 'Sequential validation of causal linkages',
            'validation_frequency': 'Monthly for critical points, quarterly for supporting elements',
            'escalation_triggers': 'Two consecutive failures or critical linkage break',
            'success_criteria': 'All tracking points maintain positive trends'
        }
    
    def _identify_causal_failure_scenarios(self, tracking_points: List[Dict]) -> List[Dict[str, Any]]:
        """Identify potential failure scenarios in causal chain"""
        scenarios = []
        
        for point in tracking_points:
            scenario = {
                'failure_point': point['element'],
                'failure_scenario': f"Breakdown in {point['element']} performance",
                'impact_assessment': 'Disruption to downstream causal elements',
                'mitigation_strategy': f"Alternative validation and contingency planning for {point['element']}"
            }
            scenarios.append(scenario)
        
        return scenarios
    
    def _extract_data_requirement(self, signal: SignalMonitoring, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Extract specific data requirements for signal monitoring"""
        signal_name = signal.signal_name.lower()
        
        if 'revenue' in signal_name:
            return {
                'signal_name': signal.signal_name,
                'primary_data_source': 'Financial Statements',
                'data_type': 'Financial',
                'frequency': 'Quarterly',
                'specific_requirements': ['Revenue by segment', 'Geographic revenue', 'Recurring vs one-time'],
                'data_provider': 'Company Reports',
                'cost_estimate': 'Low',
                'criticality': 'High'
            }
        elif 'market' in signal_name:
            return {
                'signal_name': signal.signal_name,
                'primary_data_source': 'Market Research',
                'data_type': 'Market Intelligence',
                'frequency': 'Monthly',
                'specific_requirements': ['Market share data', 'Competitive landscape', 'Industry trends'],
                'data_provider': 'Third-party Research',
                'cost_estimate': 'Medium',
                'criticality': 'High'
            }
        else:
            return {
                'signal_name': signal.signal_name,
                'primary_data_source': 'Multiple Sources',
                'data_type': 'Mixed',
                'frequency': 'Monthly',
                'specific_requirements': ['Relevant performance metrics'],
                'data_provider': 'Various',
                'cost_estimate': 'Medium',
                'criticality': 'Medium'
            }
    
    def _categorize_by_source(self, data_requirements: List[Dict], source_type: str) -> List[Dict[str, Any]]:
        """Categorize data requirements by source type"""
        if source_type == 'primary':
            return [req for req in data_requirements if req['data_provider'] in ['Company Reports', 'Financial Statements']]
        elif source_type == 'alternative':
            return [req for req in data_requirements if req['data_provider'] in ['Third-party Research', 'Market Intelligence']]
        elif source_type == 'internal':
            return [req for req in data_requirements if req['data_provider'] in ['Internal Analysis', 'Proprietary Data']]
        else:
            return data_requirements
    
    def _create_acquisition_timeline(self, data_requirements: List[Dict]) -> Dict[str, Any]:
        """Create timeline for data acquisition"""
        immediate = [req for req in data_requirements if req['criticality'] == 'High']
        short_term = [req for req in data_requirements if req['criticality'] == 'Medium']
        long_term = [req for req in data_requirements if req['criticality'] == 'Low']
        
        return {
            'immediate_priorities': [req['signal_name'] for req in immediate],
            'short_term_goals': [req['signal_name'] for req in short_term],
            'long_term_objectives': [req['signal_name'] for req in long_term]
        }
    
    def _analyze_data_costs(self, data_requirements: List[Dict]) -> Dict[str, Any]:
        """Analyze cost-benefit of data acquisition"""
        total_cost = sum(1 for req in data_requirements if req['cost_estimate'] == 'High') * 3 + \
                    sum(1 for req in data_requirements if req['cost_estimate'] == 'Medium') * 2 + \
                    sum(1 for req in data_requirements if req['cost_estimate'] == 'Low') * 1
        
        high_value = [req for req in data_requirements if req['criticality'] == 'High']
        
        return {
            'estimated_total_cost': f"Cost Score: {total_cost}",
            'high_value_data': [req['signal_name'] for req in high_value],
            'cost_optimization': 'Prioritize high-criticality, low-cost data sources',
            'roi_assessment': f"{len(high_value)} high-value signals justify investment"
        }
    
    def _define_quality_standards(self, data_requirements: List[Dict]) -> Dict[str, Any]:
        """Define data quality standards"""
        return {
            'accuracy_requirements': 'Financial data: 99%+ accuracy, Market data: 95%+ accuracy',
            'timeliness_standards': 'Financial: T+1 day, Market: Real-time to T+1 week',
            'completeness_criteria': 'All critical signals: 100% data availability',
            'validation_protocols': 'Automated quality checks with manual validation for anomalies'
        }

    def _generate_executive_summary(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Generate executive summary with core claim and investment recommendation"""
        try:
            # Get market sentiment data
            market_sentiment = self._get_market_sentiment(thesis.id)
            
            # Extract LLM analysis for investment recommendation
            llm_analysis = self._extract_llm_analysis(thesis)
            
            return {
                'core_claim': thesis.core_claim or "Core investment thesis analysis",
                'investment_recommendation': llm_analysis.get('investment_recommendation', 'Hold'),
                'confidence_score': market_sentiment.get('confidence_score', 0.75),
                'summary': f"Investment thesis analysis for {thesis.title}",
                'risk_level': llm_analysis.get('risk_level', 'Medium'),
                'time_horizon': llm_analysis.get('time_horizon', '12-18 months')
            }
            
        except Exception as e:
            print(f"Error generating executive summary: {e}")
            return {
                'core_claim': thesis.core_claim or "Analysis pending",
                'investment_recommendation': 'Hold',
                'confidence_score': 0.5,
                'summary': f"Investment analysis for {thesis.title}",
                'risk_level': 'Medium',
                'time_horizon': '12 months'
            }
    
    def _extract_key_findings(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Extract key findings, risk assessment, and counter-thesis"""
        try:
            llm_analysis = self._extract_llm_analysis(thesis)
            counter_thesis_data = thesis.counter_thesis if isinstance(thesis.counter_thesis, dict) else {}
            
            return {
                'key_findings': llm_analysis.get('key_findings', [
                    "Investment thesis demonstrates strong fundamentals",
                    "Market positioning appears favorable",
                    "Risk factors identified and manageable"
                ]),
                'risk_assessment': llm_analysis.get('risk_assessment', {
                    'overall_risk': 'Medium',
                    'key_risks': ['Market volatility', 'Regulatory changes', 'Competition'],
                    'mitigation_strategies': ['Diversification', 'Monitoring', 'Risk management']
                }),
                'supporting_rationale': llm_analysis.get('supporting_rationale', [
                    "Strong market position",
                    "Favorable industry trends",
                    "Sound financial metrics"
                ]),
                'counter_thesis': counter_thesis_data.get('scenarios', [])
            }
            
        except Exception as e:
            print(f"Error extracting key findings: {e}")
            return {
                'key_findings': ["Analysis in progress"],
                'risk_assessment': {'overall_risk': 'Medium', 'key_risks': [], 'mitigation_strategies': []},
                'supporting_rationale': ["Comprehensive analysis pending"],
                'counter_thesis': []
            }
    
    def _get_company_metrics_overview(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Get comprehensive company metrics overview"""
        try:
            # Extract company ticker from thesis
            company_ticker = self._extract_company_ticker(thesis)
            
            # Get Eagle API metrics if available
            eagle_metrics = self._get_eagle_metrics(company_ticker)
            
            # Get metric coverage score
            coverage_score = self._calculate_metric_coverage(eagle_metrics)
            
            return {
                'company_ticker': company_ticker,
                'metrics_summary': {
                    'total_metrics': len(eagle_metrics.get('metrics', [])),
                    'coverage_categories': eagle_metrics.get('categories', [])
                },
                'coverage_score': coverage_score,
                'eagle_api_metrics': eagle_metrics,
                'metric_insights': self._generate_metric_insights(eagle_metrics)
            }
            
        except Exception as e:
            print(f"Error getting company metrics: {e}")
            return {
                'company_ticker': 'N/A',
                'metrics_summary': {'total_metrics': 0, 'coverage_categories': []},
                'coverage_score': 0.0,
                'eagle_api_metrics': {},
                'metric_insights': []
            }
    
    def _analyze_research_documents(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Analyze research documents and extract insights"""
        try:
            # Get associated documents
            documents = DocumentUpload.query.filter_by(thesis_analysis_id=thesis.id).all()
            
            document_insights = []
            themes_sentiment = {}
            
            for doc in documents:
                if doc.processed_data:
                    insights = {
                        'filename': doc.filename,
                        'file_type': doc.file_type,
                        'key_insights': doc.processed_data.get('key_insights', []),
                        'sentiment_score': doc.processed_data.get('sentiment_score', 0.5)
                    }
                    document_insights.append(insights)
            
            # Aggregate themes and sentiment
            if document_insights:
                themes_sentiment = {
                    'primary_themes': self._extract_primary_themes(document_insights),
                    'overall_sentiment': self._calculate_overall_sentiment(document_insights),
                    'confidence_level': 'High' if len(document_insights) >= 3 else 'Medium'
                }
            
            return {
                'documents_processed': len(documents),
                'document_insights': document_insights,
                'themes_sentiment': themes_sentiment,
                'research_quality_score': self._calculate_research_quality_score(documents)
            }
            
        except Exception as e:
            print(f"Error analyzing research documents: {e}")
            return {
                'documents_processed': 0,
                'document_insights': [],
                'themes_sentiment': {},
                'research_quality_score': 0.0
            }
    
    def _analyze_signals_sentiment(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Analyze signals and market sentiment with detailed descriptions"""
        try:
            # Get all signals for comprehensive analysis
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis.id).all()
            
            # Enhanced signal processing with detailed descriptions
            detailed_signals = []
            for signal in signals:
                signal_dict = signal.to_dict()
                enhanced_signal = self._enhance_signal_with_description(signal_dict, thesis)
                detailed_signals.append(enhanced_signal)
            
            # Get market sentiment
            market_sentiment = self._get_market_sentiment(thesis.id)
            
            # Categorize signals by level with detailed analysis
            signals_by_level = self._categorize_signals_with_details(detailed_signals)
            
            # Generate comprehensive signal insights
            signal_insights = self._generate_signal_insights(detailed_signals, thesis)
            
            return {
                'total_signals_identified': len(detailed_signals),
                'signals_by_level': signals_by_level,
                'detailed_signal_analysis': detailed_signals,
                'signal_insights': signal_insights,
                'tracking_methodology': self._describe_tracking_methodology(detailed_signals),
                'validation_approach': self._describe_validation_approach(detailed_signals),
                'market_sentiment': {
                    'recommendation': market_sentiment.get('recommendation', 'Hold'),
                    'avg_price_target': market_sentiment.get('price_target', 'N/A'),
                    'sentiment_trend': market_sentiment.get('trend', 'Neutral'),
                    'confidence_score': market_sentiment.get('confidence_score', 0.5)
                }
            }
            
        except Exception as e:
            print(f"Error analyzing signals sentiment: {e}")
            return {
                'total_signals_identified': 0,
                'signals_by_level': {},
                'detailed_signal_analysis': [],
                'signal_insights': {},
                'tracking_methodology': 'Signal tracking methodology not available',
                'validation_approach': 'Validation approach not available',
                'market_sentiment': {
                    'recommendation': 'Hold',
                    'avg_price_target': 'N/A',
                    'sentiment_trend': 'Neutral',
                    'confidence_score': 0.5
                }
            }
    
    def _extract_thesis_structure(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Extract thesis structure and logic"""
        return {
            'causal_chain': thesis.causal_chain if isinstance(thesis.causal_chain, list) else [],
            'assumptions': thesis.assumptions if isinstance(thesis.assumptions, list) else [],
            'mental_model': thesis.mental_model or 'Growth-oriented investment approach',
            'logical_flow_score': self._calculate_logical_flow_score(thesis)
        }
    
    def _compile_monitoring_recommendations(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Compile monitoring plan and recommendations"""
        try:
            # Get active signals
            active_signals = SignalMonitoring.query.filter_by(
                thesis_analysis_id=thesis.id,
                status='active'
            ).all()
            
            # Get recent notifications
            recent_notifications = db.session.query(NotificationLog)\
                .join(SignalMonitoring)\
                .filter(SignalMonitoring.thesis_analysis_id == thesis.id)\
                .order_by(NotificationLog.sent_at.desc())\
                .limit(10).all()
            
            return {
                'metrics_to_track': thesis.metrics_to_track if isinstance(thesis.metrics_to_track, list) else [],
                'monitoring_plan': thesis.monitoring_plan if isinstance(thesis.monitoring_plan, dict) else {},
                'active_signals_count': len(active_signals),
                'signal_monitoring_events': [
                    {
                        'signal_name': signal.signal_name,
                        'current_value': signal.current_value,
                        'threshold_value': signal.threshold_value,
                        'status': signal.status
                    }
                    for signal in active_signals[:5]  # Top 5 active signals
                ],
                'notification_events': [
                    {
                        'message': notif.message,
                        'sent_at': notif.sent_at.isoformat() if notif.sent_at else None,
                        'acknowledged': notif.acknowledged
                    }
                    for notif in recent_notifications[:5]  # Recent 5 notifications
                ]
            }
            
        except Exception as e:
            print(f"Error compiling monitoring recommendations: {e}")
            return {
                'metrics_to_track': [],
                'monitoring_plan': {},
                'active_signals_count': 0,
                'signal_monitoring_events': [],
                'notification_events': []
            }
    
    def _get_alternative_investments(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Get alternative investment ideas and analysis"""
        try:
            # Get signals for alternative company analysis
            signals = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis.id).all()
            thesis_dict = thesis.to_dict()
            signals_dict = [signal.to_dict() for signal in signals]
            
            # Get alternative companies using the correct method
            alternative_companies_list = self.alternative_service.find_alternative_companies(thesis_dict, signals_dict)
            alternative_companies = {
                'alternative_companies': alternative_companies_list
            }
            
            # Calculate pattern match score
            pattern_match_score = self._calculate_pattern_match_score(alternative_companies)
            
            return {
                'alternative_companies': alternative_companies.get('alternative_companies', [])[:6],
                'pattern_match_score': pattern_match_score,
                'comparison_metrics': self._generate_comparison_metrics(alternative_companies),
                'diversification_score': self._calculate_diversification_score(alternative_companies)
            }
            
        except Exception as e:
            print(f"Error getting alternative investments: {e}")
            return {
                'alternative_companies': [],
                'pattern_match_score': 0.0,
                'comparison_metrics': {},
                'diversification_score': 0.0
            }
    
    def _generate_evaluation_criteria(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Generate evaluation criteria scorecard for PMs/Analysts"""
        return {
            'scorecard_criteria': [
                {
                    'criterion': 'Alignment with Thesis Goals',
                    'weight': 0.20,
                    'score': self._score_thesis_alignment(thesis),
                    'notes': 'Investment logic coherence and goal alignment'
                },
                {
                    'criterion': 'Accuracy of Extracted Insights',
                    'weight': 0.18,
                    'score': self._score_insight_accuracy(thesis),
                    'notes': 'Quality and relevance of analytical insights'
                },
                {
                    'criterion': 'Completeness of Data Coverage',
                    'weight': 0.16,
                    'score': self._score_data_completeness(thesis),
                    'notes': 'Breadth and depth of data analysis'
                },
                {
                    'criterion': 'Relevance of Signals and Sentiment',
                    'weight': 0.15,
                    'score': self._score_signal_relevance(thesis),
                    'notes': 'Signal quality and market sentiment alignment'
                },
                {
                    'criterion': 'Usefulness of Monitoring Recommendations',
                    'weight': 0.15,
                    'score': self._score_monitoring_usefulness(thesis),
                    'notes': 'Practicality and effectiveness of monitoring plan'
                },
                {
                    'criterion': 'Risk Assessment Quality',
                    'weight': 0.16,
                    'score': self._score_risk_assessment(thesis),
                    'notes': 'Thoroughness and accuracy of risk analysis'
                }
            ],
            'overall_score': self._calculate_overall_evaluation_score(thesis),
            'recommendation': self._generate_evaluation_recommendation(thesis)
        }
    
    # Helper methods
    def _extract_company_ticker(self, thesis: ThesisAnalysis) -> str:
        """Extract company ticker from thesis text"""
        # Simple extraction - could be enhanced with NLP
        text = thesis.original_thesis.upper()
        common_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NVO', 'NOVO']
        for ticker in common_tickers:
            if ticker in text:
                return ticker
        return 'N/A'
    
    def _get_market_sentiment(self, thesis_id: int) -> Dict[str, Any]:
        """Get market sentiment data"""
        try:
            response = requests.get(f'http://localhost:5000/get_market_sentiment/{thesis_id}', timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {'recommendation': 'Hold', 'confidence_score': 0.5, 'trend': 'Neutral'}
    
    def _extract_llm_analysis(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Extract LLM analysis results from thesis"""
        # Parse core analysis or generate basic analysis
        if thesis.core_analysis:
            try:
                # Try to parse as JSON first
                if isinstance(thesis.core_analysis, str):
                    return json.loads(thesis.core_analysis)
                return thesis.core_analysis
            except:
                pass
        
        # Return structured fallback
        return {
            'investment_recommendation': 'Hold',
            'key_findings': ["Analysis in progress"],
            'risk_assessment': {'overall_risk': 'Medium'},
            'supporting_rationale': ["Detailed analysis pending"]
        }
    
    def _get_eagle_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get Eagle API metrics for company"""
        if ticker == 'N/A':
            return {}
        
        try:
            response = requests.get(f'http://localhost:5000/get_company_metrics/{ticker}', timeout=3)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}
    
    def _enhance_signal_with_description(self, signal_dict: Dict, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Enhance signal with comprehensive description and context"""
        signal_name = signal_dict.get('signal_name', 'Unknown Signal')
        signal_type = signal_dict.get('signal_type', 'Unknown')
        current_value = signal_dict.get('current_value', 'N/A')
        threshold_value = signal_dict.get('threshold_value', 'N/A')
        
        # Generate comprehensive descriptions
        detailed_description = self._generate_comprehensive_description(signal_name, signal_type, thesis)
        tracking_rationale = self._generate_tracking_rationale(signal_name, signal_type)
        validation_approach = self._generate_validation_method(signal_name, signal_type)
        
        enhanced_signal = signal_dict.copy()
        enhanced_signal.update({
            'detailed_description': detailed_description,
            'tracking_rationale': tracking_rationale,
            'validation_approach': validation_approach,
            'importance_score': self._calculate_importance_score(signal_name, signal_type),
            'monitoring_frequency': self._get_monitoring_frequency(signal_name, signal_type),
            'data_sources': self._get_data_sources(signal_name, signal_type),
            'success_criteria': self._define_success_criteria(signal_name, current_value, threshold_value)
        })
        
        return enhanced_signal
    
    def _generate_comprehensive_description(self, signal_name: str, signal_type: str, thesis: ThesisAnalysis) -> str:
        """Generate comprehensive description for each signal"""
        signal_lower = signal_name.lower()
        
        if 'revenue' in signal_lower and 'growth' in signal_lower:
            return f"{signal_name} serves as the primary validation metric for the investment thesis, directly measuring the company's ability to sustain revenue expansion and capture market opportunities. This signal tracks quarterly revenue performance, year-over-year growth rates, and sequential growth trends to validate assumptions about market demand, competitive positioning, and business model scalability. Revenue growth validation is critical because it directly reflects whether the core value proposition is resonating with customers and generating sustainable business momentum. The signal monitors both absolute revenue figures and growth acceleration patterns, providing early indicators of market acceptance, pricing power effectiveness, and competitive advantage sustainability."
        
        elif 'market' in signal_lower and ('position' in signal_lower or 'share' in signal_lower):
            return f"{signal_name} evaluates the company's competitive positioning and market leadership within its industry ecosystem. This signal validates thesis assumptions about the company's ability to maintain or expand market share, defend competitive advantages, and capitalize on industry growth trends. Market position analysis encompasses customer retention rates, competitive win-loss ratios, pricing power indicators, and brand recognition metrics. The signal is essential for confirming whether the company's strategic moat is widening or narrowing, and whether competitive advantages outlined in the investment thesis remain sustainable. It provides insights into long-term competitive dynamics and the company's ability to maintain premium positioning in evolving market conditions."
        
        elif 'tech' in signal_lower or 'innovation' in signal_lower:
            return f"{signal_name} assesses the company's technological leadership and innovation capabilities, validating assumptions about R&D effectiveness and technology-driven competitive advantages. This signal tracks patent applications, product development cycles, technology adoption rates, and innovation pipeline strength. For technology-focused investment theses, this signal is crucial for confirming that the company maintains its technological edge and can continue driving innovation-led growth. The validation includes assessment of R&D spending efficiency, time-to-market for new products, and technology partnership effectiveness. This signal helps identify whether the company's innovation engine remains competitive and capable of defending against technological disruption."
        
        elif 'demand' in signal_lower or 'market demand' in signal_lower:
            return f"{signal_name} monitors underlying market demand indicators and customer adoption patterns that drive business performance. This signal validates assumptions about total addressable market size, market growth rates, and customer behavior trends. It tracks leading indicators such as customer inquiry volumes, sales pipeline development, market research data, and industry demand forecasts. Market demand validation is fundamental because it confirms whether the market opportunity assumptions underlying the investment thesis remain valid. The signal provides early warning indicators about potential shifts in customer preferences, economic conditions, or industry dynamics that could impact long-term growth prospects."
        
        elif 'margin' in signal_lower or 'profitability' in signal_lower:
            return f"{signal_name} tracks operational efficiency and profitability trends, validating assumptions about the company's ability to maintain or improve profit margins while scaling operations. This signal monitors gross margins, operating margins, and EBITDA margins across different business segments and time periods. Profitability tracking is essential for confirming that the business model can generate sustainable returns and that unit economics remain favorable as the company grows. The signal helps validate assumptions about operational leverage, cost structure optimization, and pricing power sustainability. It provides insights into whether the company can maintain profitability during competitive pressures or economic downturns."
        
        elif 'peer' in signal_lower or 'comparison' in signal_lower:
            return f"{signal_name} provides comprehensive benchmarking against industry peers and competitors, validating assumptions about relative performance and competitive positioning. This signal compares financial metrics, operational indicators, and strategic execution across peer companies to assess whether the investment thesis assumptions about competitive advantages are materializing. Peer comparison analysis includes revenue growth rates, profitability metrics, market share trends, and strategic initiative effectiveness. This validation method helps confirm whether the company is executing better than competitors and maintaining the differentiated positioning outlined in the investment case."
        
        else:
            return f"{signal_name} represents a key validation component within the comprehensive thesis monitoring framework. This signal provides critical data points and insights that help assess whether core investment assumptions remain valid and the thesis continues to hold strength. The signal tracks specific performance indicators relevant to the investment case, offering both quantitative metrics and qualitative insights into thesis execution. Regular monitoring of this signal ensures that any deviations from expected performance are identified early, allowing for proactive investment management and decision-making adjustments as market conditions evolve."
    
    def _generate_tracking_rationale(self, signal_name: str, signal_type: str) -> str:
        """Generate detailed rationale for tracking this signal"""
        if 'Level 0' in signal_type or 'Core Validation' in signal_type:
            return f"{signal_name} is designated as a Level 0 Core Validation signal, representing the most critical validation mechanism for fundamental thesis assumptions. This signal classification indicates direct relevance to core investment premises and requires the highest monitoring priority. Core validation signals provide immediate feedback on thesis validity and serve as primary decision-making inputs for investment management. The tracking rationale centers on ensuring that foundational assumptions underlying the investment decision remain accurate and that any material changes are identified immediately for strategic response."
        
        elif 'Metrics Tracking' in signal_type or 'Level 1' in signal_type:
            return f"{signal_name} functions as a Metrics Tracking signal, providing systematic quantitative validation of thesis assumptions through measurable performance indicators. This tracking approach focuses on objective, data-driven assessment of investment performance across key financial and operational metrics. The rationale for metrics tracking lies in establishing clear, measurable benchmarks that can validate or contradict numerical assumptions embedded in the thesis. This systematic approach enables evidence-based investment management and provides concrete data points for ongoing thesis assessment."
        
        elif 'Peer Comparison' in signal_type or 'Level 3' in signal_type:
            return f"{signal_name} serves as a Peer Comparison signal, ensuring relative performance validation against industry standards and competitive benchmarks. The tracking rationale focuses on maintaining perspective on competitive positioning and validating assumptions about relative market performance. This approach recognizes that investment success often depends on outperforming competitors and maintaining competitive advantages. Peer comparison tracking provides context for absolute performance metrics and helps identify whether superior performance reflects company-specific strengths or broader industry trends."
        
        else:
            return f"{signal_name} contributes to the comprehensive thesis validation framework by tracking specific indicators that inform investment decision-making. The tracking rationale emphasizes systematic monitoring of relevant performance indicators that support thesis validation and risk management. This signal provides valuable context and supporting evidence for overall investment assessment, contributing to a holistic understanding of investment performance and market dynamics."
    
    def _generate_validation_method(self, signal_name: str, signal_type: str) -> str:
        """Generate detailed validation method for the signal"""
        signal_lower = signal_name.lower()
        
        if 'revenue' in signal_lower:
            return "Revenue validation employs comprehensive financial analysis including quarterly earnings review, segment performance breakdown, geographic revenue assessment, and forward guidance evaluation. The validation process incorporates year-over-year growth analysis, sequential quarterly trends, revenue quality assessment through recurring versus one-time components, and comparison against management guidance and analyst expectations. Additional validation includes customer concentration analysis, average selling price trends, and volume growth decomposition to ensure sustainable revenue expansion."
        
        elif 'market' in signal_lower:
            return "Market position validation utilizes multi-dimensional competitive analysis including third-party market share data, customer satisfaction surveys, brand recognition studies, and competitive win-loss analysis. The validation approach incorporates pricing power assessment, customer retention metrics, and distribution channel effectiveness evaluation. Market position validation also includes strategic positioning analysis through product differentiation assessment, barriers to entry evaluation, and competitive moat sustainability analysis."
        
        elif 'margin' in signal_lower or 'profit' in signal_lower:
            return "Profitability validation employs detailed margin analysis across product lines, operating leverage assessment, and cost structure evaluation. The validation method includes gross margin trend analysis, operating efficiency metrics, and economies of scale assessment. Profitability validation incorporates peer margin comparison, industry benchmarking, and sustainability analysis to ensure margin improvements are sustainable and not driven by temporary factors."
        
        elif 'peer' in signal_lower:
            return "Peer comparison validation utilizes systematic benchmarking against carefully selected peer groups based on business model similarity, market positioning, and operational scale. The validation approach includes comprehensive financial metrics comparison, operational efficiency benchmarking, and strategic initiative assessment. Peer validation incorporates relative valuation analysis, market performance comparison, and competitive positioning evaluation with regular peer group updates as companies evolve."
        
        else:
            return "Signal validation employs systematic data collection from authoritative sources including company reports, industry research, and third-party data providers. The validation process includes automated threshold monitoring, trend analysis with statistical significance testing, and qualitative assessment through expert analysis. Regular validation includes data quality verification, methodology consistency checks, and threshold recalibration based on changing market conditions."
    
    def _categorize_signals_with_details(self, detailed_signals: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize signals by validation level with detailed analysis"""
        categories = {
            'Level 0 - Core Validation': [],
            'Level 1 - Metrics Tracking': [],
            'Level 2 - Complex Analysis': [],
            'Level 3 - Peer Comparison': [],
            'Other Signals': []
        }
        
        for signal in detailed_signals:
            signal_type = signal.get('signal_type', 'Unknown')
            signal_name = signal.get('signal_name', '').lower()
            
            if 'Level 0' in signal_type or 'Core Validation' in signal_type:
                categories['Level 0 - Core Validation'].append(signal)
            elif 'Level 1' in signal_type or 'Metrics Tracking' in signal_type:
                categories['Level 1 - Metrics Tracking'].append(signal)
            elif 'Level 2' in signal_type or 'Complex Analysis' in signal_type:
                categories['Level 2 - Complex Analysis'].append(signal)
            elif 'Level 3' in signal_type or 'Peer Comparison' in signal_type:
                categories['Level 3 - Peer Comparison'].append(signal)
            elif 'revenue' in signal_name or 'growth' in signal_name:
                categories['Level 0 - Core Validation'].append(signal)
            elif 'peer' in signal_name or 'comparison' in signal_name:
                categories['Level 3 - Peer Comparison'].append(signal)
            else:
                categories['Other Signals'].append(signal)
        
        return categories
    
    def _generate_signal_insights(self, detailed_signals: List[Dict], thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Generate comprehensive insights about the signal monitoring framework"""
        total_signals = len(detailed_signals)
        
        # Analyze signal distribution
        signal_types = {}
        for signal in detailed_signals:
            signal_type = signal.get('signal_type', 'Unknown')
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        # Calculate coverage metrics
        coverage_analysis = self._analyze_signal_coverage(detailed_signals)
        
        return {
            'total_signals': total_signals,
            'signal_distribution': signal_types,
            'coverage_analysis': coverage_analysis,
            'monitoring_scope': f"Comprehensive {total_signals}-signal monitoring framework covering core validation, metrics tracking, peer comparison, and complex analysis across multiple investment dimensions",
            'validation_strength': self._assess_validation_strength(detailed_signals),
            'risk_coverage': self._assess_risk_coverage(detailed_signals)
        }
    
    def _describe_tracking_methodology(self, detailed_signals: List[Dict]) -> str:
        """Describe comprehensive tracking methodology"""
        if not detailed_signals:
            return "Tracking methodology information unavailable due to insufficient signal data."
        
        methodology_components = []
        
        # Analyze signal composition
        has_core = any('Core Validation' in s.get('signal_type', '') for s in detailed_signals)
        has_metrics = any('Metrics Tracking' in s.get('signal_type', '') for s in detailed_signals)
        has_peer = any('Peer Comparison' in s.get('signal_type', '') for s in detailed_signals)
        
        if has_core:
            methodology_components.append("Core Validation Methodology employs direct validation of fundamental thesis assumptions through primary data sources and real-time monitoring systems. This approach ensures critical investment premises are continuously validated against actual performance with immediate alert protocols for threshold breaches.")
        
        if has_metrics:
            methodology_components.append("Metrics Tracking Methodology utilizes systematic quantitative monitoring of key performance indicators through automated data collection and statistical analysis. This approach provides objective, measurable validation of thesis assumptions with regular reporting cycles and variance analysis.")
        
        if has_peer:
            methodology_components.append("Peer Comparison Methodology implements comprehensive benchmarking against industry peers through multi-dimensional analysis including financial metrics, operational indicators, and strategic positioning assessment.")
        
        if not methodology_components:
            methodology_components.append("Standard monitoring methodology employs systematic data collection and regular performance review across multiple signal categories.")
        
        return " ".join(methodology_components)
    
    def _describe_validation_approach(self, detailed_signals: List[Dict]) -> str:
        """Describe comprehensive validation approach"""
        if not detailed_signals:
            return "Validation approach information unavailable due to insufficient signal data."
        
        # Analyze validation requirements
        quantitative_count = sum(1 for s in detailed_signals if any(kw in s.get('signal_name', '').lower() for kw in ['revenue', 'margin', 'growth']))
        qualitative_count = sum(1 for s in detailed_signals if any(kw in s.get('signal_name', '').lower() for kw in ['position', 'innovation', 'market']))
        comparative_count = sum(1 for s in detailed_signals if any(kw in s.get('signal_name', '').lower() for kw in ['peer', 'comparison']))
        
        validation_components = []
        
        if quantitative_count > 0:
            validation_components.append(f"Quantitative Validation across {quantitative_count} signals employs statistical analysis, trend evaluation, and mathematical modeling to validate numerical thesis assumptions. This approach includes regression analysis and predictive modeling to ensure quantitative assumptions remain valid under various market conditions.")
        
        if qualitative_count > 0:
            validation_components.append(f"Qualitative Assessment incorporates {qualitative_count} signals through fundamental analysis and strategic evaluation. This validation includes competitive positioning analysis and strategic execution assessment to validate non-quantitative thesis assumptions.")
        
        if comparative_count > 0:
            validation_components.append(f"Comparative Analysis utilizes {comparative_count} signals for systematic benchmarking against industry peers and competitive standards to validate assumptions about competitive advantages and relative market performance.")
        
        if not validation_components:
            validation_components.append("Multi-faceted validation approach combining quantitative analysis, qualitative assessment, and comparative benchmarking to ensure comprehensive thesis validation.")
        
        return " ".join(validation_components)
    
    def _calculate_importance_score(self, signal_name: str, signal_type: str) -> float:
        """Calculate importance score for signal prioritization"""
        importance = 0.5  # Base score
        
        # Type-based scoring
        if 'Level 0' in signal_type or 'Core Validation' in signal_type:
            importance = 0.95
        elif 'Metrics Tracking' in signal_type:
            importance = 0.85
        elif 'Peer Comparison' in signal_type:
            importance = 0.75
        
        # Name-based adjustments
        signal_lower = signal_name.lower()
        if 'revenue' in signal_lower:
            importance = min(1.0, importance + 0.15)
        elif 'growth' in signal_lower:
            importance = min(1.0, importance + 0.12)
        elif 'margin' in signal_lower:
            importance = min(1.0, importance + 0.10)
        
        return round(importance, 2)
    
    def _get_monitoring_frequency(self, signal_name: str, signal_type: str) -> str:
        """Determine appropriate monitoring frequency"""
        if 'Core Validation' in signal_type:
            return "Daily monitoring with real-time alerts and immediate escalation"
        elif 'revenue' in signal_name.lower():
            return "Weekly monitoring with monthly comprehensive analysis"
        elif 'Metrics Tracking' in signal_type:
            return "Bi-weekly monitoring with quarterly deep analysis"
        elif 'Peer Comparison' in signal_type:
            return "Monthly monitoring with quarterly peer assessment"
        else:
            return "Monthly monitoring with quarterly comprehensive review"
    
    def _get_data_sources(self, signal_name: str, signal_type: str) -> List[str]:
        """Identify comprehensive data sources for validation"""
        sources = []
        signal_lower = signal_name.lower()
        
        if 'revenue' in signal_lower or 'financial' in signal_lower:
            sources.extend([
                "Company quarterly earnings reports",
                "SEC filings and regulatory documents",
                "Financial data providers (Bloomberg, FactSet)",
                "Management guidance and investor communications"
            ])
        
        if 'market' in signal_lower or 'competitive' in signal_lower:
            sources.extend([
                "Industry research reports",
                "Market intelligence platforms",
                "Competitor analysis and filings",
                "Third-party market research"
            ])
        
        if 'peer' in signal_lower:
            sources.extend([
                "Peer company financial reports",
                "Industry benchmarking databases",
                "Competitive intelligence platforms"
            ])
        
        if not sources:
            sources = [
                "Company financial reports",
                "Industry research",
                "Third-party data providers",
                "Regulatory filings"
            ]
        
        return list(set(sources))
    
    def _define_success_criteria(self, signal_name: str, current_value, threshold_value) -> str:
        """Define clear success criteria for signal performance"""
        if current_value != 'N/A' and threshold_value != 'N/A':
            return f"Success criteria: Maintain {signal_name} performance above {threshold_value} threshold (currently at {current_value}). Target consistent positive trends with quarterly improvements and sustained performance above benchmark levels."
        else:
            return f"Success criteria: Establish quantitative benchmarks for {signal_name} based on thesis assumptions and implement systematic threshold monitoring with clear performance targets aligned with investment objectives."
    
    def _analyze_signal_coverage(self, detailed_signals: List[Dict]) -> Dict[str, Any]:
        """Analyze comprehensive signal coverage across investment dimensions"""
        coverage_areas = {
            'revenue_growth': False,
            'profitability': False,
            'market_position': False,
            'competitive_advantage': False,
            'innovation': False,
            'operational_efficiency': False
        }
        
        for signal in detailed_signals:
            signal_name = signal.get('signal_name', '').lower()
            
            if 'revenue' in signal_name or 'growth' in signal_name:
                coverage_areas['revenue_growth'] = True
            if 'margin' in signal_name or 'profit' in signal_name:
                coverage_areas['profitability'] = True
            if 'market' in signal_name or 'position' in signal_name:
                coverage_areas['market_position'] = True
            if 'peer' in signal_name or 'competitive' in signal_name:
                coverage_areas['competitive_advantage'] = True
            if 'tech' in signal_name or 'innovation' in signal_name:
                coverage_areas['innovation'] = True
            if 'efficiency' in signal_name or 'operational' in signal_name:
                coverage_areas['operational_efficiency'] = True
        
        coverage_score = sum(coverage_areas.values()) / len(coverage_areas)
        
        return {
            'coverage_areas': coverage_areas,
            'coverage_score': coverage_score,
            'coverage_percentage': f"{coverage_score * 100:.0f}%"
        }
    
    def _assess_validation_strength(self, detailed_signals: List[Dict]) -> str:
        """Assess overall validation framework strength"""
        total_signals = len(detailed_signals)
        core_signals = sum(1 for s in detailed_signals if 'Core Validation' in s.get('signal_type', ''))
        
        if total_signals >= 8 and core_signals >= 3:
            return f"Strong validation framework with {total_signals} total signals including {core_signals} core validation signals, providing comprehensive thesis validation with robust risk monitoring."
        elif total_signals >= 5:
            return f"Adequate validation framework with {total_signals} signals providing solid thesis validation coverage."
        else:
            return f"Basic validation framework with {total_signals} signals requiring enhancement for comprehensive validation."
    
    def _assess_risk_coverage(self, detailed_signals: List[Dict]) -> str:
        """Assess risk coverage across investment dimensions"""
        risk_areas = set()
        
        for signal in detailed_signals:
            signal_name = signal.get('signal_name', '').lower()
            if 'revenue' in signal_name:
                risk_areas.add("Revenue Risk")
            if 'margin' in signal_name:
                risk_areas.add("Profitability Risk")
            if 'market' in signal_name:
                risk_areas.add("Market Risk")
            if 'competitive' in signal_name:
                risk_areas.add("Competitive Risk")
        
        risk_count = len(risk_areas)
        
        if risk_count >= 3:
            return f"Comprehensive risk coverage across {risk_count} major risk categories providing early warning indicators for potential investment threats."
        elif risk_count >= 2:
            return f"Good risk coverage across {risk_count} risk categories with adequate risk monitoring."
        else:
            return "Basic risk coverage requiring expansion for comprehensive risk management."
    
    def _calculate_metric_coverage(self, eagle_metrics: Dict) -> float:
        """Calculate metric coverage score"""
        if not eagle_metrics or 'metrics' not in eagle_metrics:
            return 0.0
        
        total_possible = 155  # Eagle API has 155+ metrics
        actual_metrics = len(eagle_metrics.get('metrics', []))
        return min(actual_metrics / total_possible, 1.0)
    
    def _generate_metric_insights(self, eagle_metrics: Dict) -> List[str]:
        """Generate insights from Eagle metrics"""
        if not eagle_metrics:
            return ["Metric analysis pending"]
        
        insights = []
        metrics = eagle_metrics.get('metrics', [])
        
        if len(metrics) > 50:
            insights.append("Comprehensive metric coverage available")
        if len(metrics) > 100:
            insights.append("Extensive financial data depth")
        
        return insights or ["Basic metric analysis available"]
    
    def _extract_signals_from_thesis(self, thesis: ThesisAnalysis) -> List[Dict]:
        """Extract signals from thesis analysis"""
        # This would integrate with the actual signal extraction results
        # For now, return a structured placeholder
        return [
            {
                'signal_name': 'Revenue Growth',
                'signal_type': 'Level 1',
                'strength': 'High',
                'description': 'Strong revenue growth indicators'
            }
        ]
    
    def _count_signals_by_level(self, signals_data: List[Dict]) -> Dict[str, int]:
        """Count signals by classification level"""
        counts = {}
        for signal in signals_data:
            level = signal.get('signal_type', 'Unknown')
            counts[level] = counts.get(level, 0) + 1
        return counts
    
    def _calculate_pattern_match_score(self, alternative_companies: Dict) -> float:
        """Calculate pattern matching score for alternatives"""
        companies = alternative_companies.get('alternative_companies', [])
        if not companies:
            return 0.0
        
        # Average composite scores
        scores = [comp.get('composite_score', 0) for comp in companies]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_comparison_metrics(self, alternative_companies: Dict) -> Dict:
        """Generate comparison metrics for alternatives"""
        companies = alternative_companies.get('alternative_companies', [])
        if not companies:
            return {}
        
        return {
            'avg_score': sum(c.get('composite_score', 0) for c in companies) / len(companies),
            'top_performer': max(companies, key=lambda x: x.get('composite_score', 0), default={}),
            'sector_diversity': len(set(c.get('sector', 'Unknown') for c in companies))
        }
    
    def _calculate_diversification_score(self, alternative_companies: Dict) -> float:
        """Calculate diversification score"""
        companies = alternative_companies.get('alternative_companies', [])
        if not companies:
            return 0.0
        
        sectors = set(comp.get('sector', 'Unknown') for comp in companies)
        return min(len(sectors) / 6.0, 1.0)  # Normalize to 6 sectors max
    
    # Scoring methods for evaluation criteria
    def _score_thesis_alignment(self, thesis: ThesisAnalysis) -> float:
        """Score thesis alignment with goals"""
        score = 0.7  # Base score
        if thesis.core_claim:
            score += 0.1
        if thesis.mental_model:
            score += 0.1
        if thesis.causal_chain:
            score += 0.1
        return min(score, 1.0)
    
    def _score_insight_accuracy(self, thesis: ThesisAnalysis) -> float:
        """Score accuracy of extracted insights"""
        score = 0.6  # Base score
        if thesis.core_analysis:
            score += 0.2
        if thesis.assumptions:
            score += 0.1
        if thesis.metrics_to_track:
            score += 0.1
        return min(score, 1.0)
    
    def _score_data_completeness(self, thesis: ThesisAnalysis) -> float:
        """Score completeness of data coverage"""
        score = 0.5  # Base score
        
        # Check for various data elements
        if thesis.causal_chain:
            score += 0.1
        if thesis.assumptions:
            score += 0.1
        if thesis.counter_thesis:
            score += 0.1
        if thesis.metrics_to_track:
            score += 0.1
        if thesis.monitoring_plan:
            score += 0.1
        
        # Check for associated documents
        doc_count = DocumentUpload.query.filter_by(thesis_analysis_id=thesis.id).count()
        if doc_count > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_signal_relevance(self, thesis: ThesisAnalysis) -> float:
        """Score relevance of signals and sentiment"""
        score = 0.6  # Base score
        
        # Check for active signals
        signal_count = SignalMonitoring.query.filter_by(thesis_analysis_id=thesis.id).count()
        if signal_count > 0:
            score += 0.2
        if signal_count > 3:
            score += 0.1
        if signal_count > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_monitoring_usefulness(self, thesis: ThesisAnalysis) -> float:
        """Score usefulness of monitoring recommendations"""
        score = 0.5  # Base score
        if thesis.monitoring_plan:
            score += 0.2
        if thesis.metrics_to_track:
            score += 0.2
        
        # Check for active monitoring
        active_signals = SignalMonitoring.query.filter_by(
            thesis_analysis_id=thesis.id,
            status='active'
        ).count()
        if active_signals > 0:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_risk_assessment(self, thesis: ThesisAnalysis) -> float:
        """Score quality of risk assessment"""
        score = 0.6  # Base score
        if thesis.counter_thesis:
            score += 0.2
        if thesis.assumptions:
            score += 0.1
        if isinstance(thesis.counter_thesis, dict) and thesis.counter_thesis.get('scenarios'):
            score += 0.1
        return min(score, 1.0)
    
    def _calculate_overall_evaluation_score(self, thesis: ThesisAnalysis) -> float:
        """Calculate overall evaluation score"""
        criteria_scores = [
            self._score_thesis_alignment(thesis) * 0.20,
            self._score_insight_accuracy(thesis) * 0.18,
            self._score_data_completeness(thesis) * 0.16,
            self._score_signal_relevance(thesis) * 0.15,
            self._score_monitoring_usefulness(thesis) * 0.15,
            self._score_risk_assessment(thesis) * 0.16
        ]
        return sum(criteria_scores)
    
    def _generate_evaluation_recommendation(self, thesis: ThesisAnalysis) -> str:
        """Generate evaluation recommendation"""
        overall_score = self._calculate_overall_evaluation_score(thesis)
        
        if overall_score >= 0.8:
            return "Excellent - Ready for institutional review"
        elif overall_score >= 0.7:
            return "Good - Minor refinements recommended"
        elif overall_score >= 0.6:
            return "Satisfactory - Some improvements needed"
        else:
            return "Needs Work - Significant enhancements required"
    
    # Additional helper methods
    def _extract_primary_themes(self, document_insights: List[Dict]) -> List[str]:
        """Extract primary themes from document insights"""
        themes = []
        for doc in document_insights:
            insights = doc.get('key_insights', [])
            themes.extend(insights[:2])  # Top 2 insights per document
        return themes[:5]  # Top 5 themes overall
    
    def _calculate_overall_sentiment(self, document_insights: List[Dict]) -> float:
        """Calculate overall sentiment from documents"""
        if not document_insights:
            return 0.5
        
        scores = [doc.get('sentiment_score', 0.5) for doc in document_insights]
        return sum(scores) / len(scores)
    
    def _calculate_research_quality_score(self, documents: List) -> float:
        """Calculate research quality score"""
        if not documents:
            return 0.0
        
        # Base score for having documents
        score = 0.3
        
        # Add points for different document types
        doc_types = set(doc.file_type for doc in documents)
        score += min(len(doc_types) * 0.1, 0.3)
        
        # Add points for number of documents
        score += min(len(documents) * 0.05, 0.4)
        
        return min(score, 1.0)
    
    def _calculate_logical_flow_score(self, thesis: ThesisAnalysis) -> float:
        """Calculate logical flow score for thesis structure"""
        score = 0.4  # Base score
        
        if thesis.causal_chain and len(thesis.causal_chain) > 0:
            score += 0.2
        if thesis.assumptions and len(thesis.assumptions) > 0:
            score += 0.2
        if thesis.core_claim:
            score += 0.1
        if thesis.mental_model:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_fallback_report(self, thesis: ThesisAnalysis) -> Dict[str, Any]:
        """Generate fallback report when comprehensive analysis fails"""
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'thesis_id': thesis.id,
            'thesis_title': thesis.title,
            'status': 'Partial analysis available',
            'executive_summary': {
                'core_claim': thesis.core_claim or "Analysis in progress",
                'investment_recommendation': 'Hold',
                'confidence_score': 0.5
            },
            'note': 'Complete analysis pending - partial data available'
        }