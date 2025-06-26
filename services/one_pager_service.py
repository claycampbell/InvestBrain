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
        Generate comprehensive one-pager report consolidating all analysis data
        """
        try:
            # 1. Executive Summary
            executive_summary = self._generate_executive_summary(thesis)
            
            # 2. Key Findings & Insights
            key_findings = self._extract_key_findings(thesis)
            
            # 3. Company Metrics Overview
            company_metrics = self._get_company_metrics_overview(thesis)
            
            # 4. Research & Document Analysis
            research_analysis = self._analyze_research_documents(thesis)
            
            # 5. Signal & Sentiment Analysis
            signal_analysis = self._analyze_signals_sentiment(thesis)
            
            # 6. Thesis Structure & Logic
            thesis_structure = self._extract_thesis_structure(thesis)
            
            # 7. Monitoring & Recommendations
            monitoring_plan = self._compile_monitoring_recommendations(thesis)
            
            # 8. Alternative Investment Ideas
            alternative_investments = self._get_alternative_investments(thesis)
            
            # 9. Evaluation Criteria for PMs/Analysts
            evaluation_criteria = self._generate_evaluation_criteria(thesis)
            
            # Compile comprehensive report
            report_data = {
                'generated_at': datetime.utcnow().isoformat(),
                'thesis_id': thesis.id,
                'thesis_title': thesis.title,
                'executive_summary': executive_summary,
                'key_findings': key_findings,
                'company_metrics': company_metrics,
                'research_analysis': research_analysis,
                'signal_analysis': signal_analysis,
                'thesis_structure': thesis_structure,
                'monitoring_plan': monitoring_plan,
                'alternative_investments': alternative_investments,
                'evaluation_criteria': evaluation_criteria
            }
            
            return report_data
            
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
            return self._generate_fallback_report(thesis)
    
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
        """Analyze signals and market sentiment"""
        try:
            # Get signals from thesis data
            signals_data = self._extract_signals_from_thesis(thesis)
            
            # Get market sentiment
            market_sentiment = self._get_market_sentiment(thesis.id)
            
            # Count signals by level
            signals_by_level = self._count_signals_by_level(signals_data)
            
            return {
                'total_signals_identified': len(signals_data),
                'signals_by_level': signals_by_level,
                'signal_details': signals_data[:10],  # Top 10 signals
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
                'signal_details': [],
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