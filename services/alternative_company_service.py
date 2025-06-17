"""
Alternative Company Analysis Service
Identifies undervalued/unloved companies matching thesis patterns
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random
from services.azure_openai_service import AzureOpenAIService

class AlternativeCompanyService:
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        
    def find_alternative_companies(self, thesis_analysis: Dict, signals: List[Dict]) -> Dict[str, Any]:
        """Find alternative companies matching thesis patterns using LLM analysis"""
        try:
            # Extract thesis characteristics for analysis
            thesis_characteristics = self._extract_thesis_characteristics(thesis_analysis, signals)
            
            # Use LLM to generate authentic alternative companies
            from services.azure_openai_service import AzureOpenAIService
            openai_service = AzureOpenAIService()
            
            # Create comprehensive analysis prompt
            prompt = self._create_comprehensive_analysis_prompt(thesis_characteristics, thesis_analysis)
            
            messages = [
                {"role": "system", "content": "You are an expert investment analyst with deep knowledge of public markets. Find real, undervalued alternative companies that match specific investment thesis patterns."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate LLM analysis
            response = openai_service.generate_completion(messages, temperature=0.7)
            alternatives = self._parse_llm_companies(response)
            
            if alternatives and len(alternatives) > 0:
                return {
                    'thesis_characteristics': thesis_characteristics,
                    'alternative_companies': alternatives[:8],
                    'total_found': len(alternatives),
                    'analysis_criteria': self._get_analysis_criteria(thesis_characteristics),
                    'generated_at': datetime.utcnow().isoformat()
                }
            else:
                # Return empty state when LLM cannot provide authentic matches
                return {
                    'thesis_characteristics': thesis_characteristics,
                    'alternative_companies': [],
                    'total_found': 0,
                    'analysis_criteria': ['Unable to identify authentic alternative companies'],
                    'generated_at': datetime.utcnow().isoformat(),
                    'message': 'No suitable alternative companies found matching thesis patterns'
                }
            
        except Exception as e:
            logging.error(f"Alternative company analysis failed: {e}")
            return {
                'thesis_characteristics': {},
                'alternative_companies': [],
                'total_found': 0,
                'analysis_criteria': ['Analysis service temporarily unavailable'],
                'generated_at': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def _extract_thesis_characteristics(self, thesis_analysis: Dict, signals: List[Dict]) -> Dict[str, Any]:
        """Extract key characteristics from thesis for pattern matching"""
        core_claim = thesis_analysis.get('core_claim', '').lower()
        
        # Industry/Sector identification
        sector = self._identify_sector(core_claim)
        
        # Business model patterns
        business_model = self._identify_business_model(core_claim)
        
        # Growth stage
        growth_stage = self._identify_growth_stage(signals)
        
        # Key value drivers
        value_drivers = self._extract_value_drivers(core_claim, signals)
        
        # Market characteristics
        market_characteristics = self._extract_market_characteristics(core_claim)
        
        return {
            'sector': sector,
            'business_model': business_model,
            'growth_stage': growth_stage,
            'value_drivers': value_drivers,
            'market_characteristics': market_characteristics,
            'signal_patterns': self._analyze_signal_patterns(signals)
        }
    
    def _generate_alternative_companies(self, characteristics: Dict, thesis_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate list of alternative companies using LLM analysis"""
        try:
            # Use LLM to generate actual alternatives based on thesis patterns
            from services.azure_openai_service import AzureOpenAIService
            openai_service = AzureOpenAIService()
            
            # Prepare analysis prompt
            prompt = self._create_alternative_analysis_prompt(characteristics, thesis_analysis)
            
            messages = [
                {"role": "system", "content": "You are an expert investment analyst specializing in finding undervalued alternative companies that match specific investment thesis patterns."},
                {"role": "user", "content": prompt}
            ]
            
            response = openai_service.generate_completion(messages, temperature=0.7)
            return self._parse_llm_response(response)
            
        except Exception as e:
            logging.error(f"LLM alternative company generation failed: {e}")
            return self._generate_manual_alternatives(characteristics, thesis_analysis)
    
    def _create_alternative_analysis_prompt(self, characteristics: Dict, thesis_analysis: Dict) -> str:
        """Create detailed prompt for LLM alternative company analysis"""
        core_claim = thesis_analysis.get('core_claim', '')
        sector = characteristics.get('sector', 'Technology')
        business_model = characteristics.get('business_model', 'SaaS')
        value_drivers = characteristics.get('value_drivers', [])
        
        prompt = f"""
Based on the following investment thesis characteristics, identify 5-8 undervalued alternative companies that match these patterns:

THESIS CORE CLAIM: {core_claim}

CHARACTERISTICS TO MATCH:
- Sector: {sector}
- Business Model: {business_model}
- Value Drivers: {', '.join(value_drivers) if value_drivers else 'Not specified'}
- Growth Stage: {characteristics.get('growth_stage', 'Unknown')}

REQUIREMENTS:
1. Find real, publicly traded companies (include ticker symbols)
2. Focus on companies that are currently undervalued or overlooked by the market
3. Match the same value creation patterns as the original thesis
4. Include companies at different market capitalizations
5. Avoid the most obvious/popular choices in favor of hidden gems

For each company, provide:
- Company name and ticker symbol
- Current market cap (approximate)
- Brief description of business model
- Key metrics that match the thesis patterns
- Why it's currently unloved/undervalued (2-3 factors)
- Hidden strengths that align with thesis (2-3 factors)
- Composite investment score (0-100)

Format response as JSON array with this structure:
[{{
  "name": "Company Name",
  "ticker": "TICK",
  "market_cap": 12.5,
  "description": "Brief business description",
  "key_metrics": {{"metric1": 0.25, "metric2": 0.18}},
  "unloved_factors": ["Factor 1", "Factor 2"],
  "hidden_strengths": ["Strength 1", "Strength 2"],
  "composite_score": 85
}}]
"""
        return prompt
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response to extract company data"""
        try:
            import json
            
            # Try to extract JSON from response
            response_cleaned = response.strip()
            if response_cleaned.startswith('```json'):
                response_cleaned = response_cleaned[7:-3]
            elif response_cleaned.startswith('```'):
                response_cleaned = response_cleaned[3:-3]
            
            companies = json.loads(response_cleaned)
            
            # Validate and enhance the data
            enhanced_companies = []
            for company in companies:
                enhanced_company = {
                    'name': company.get('name', 'Unknown Company'),
                    'ticker': company.get('ticker', 'N/A'),
                    'market_cap': company.get('market_cap', 0),
                    'description': company.get('description', 'No description available'),
                    'key_metrics': company.get('key_metrics', {}),
                    'unloved_factors': company.get('unloved_factors', []),
                    'hidden_strengths': company.get('hidden_strengths', []),
                    'composite_score': company.get('composite_score', 50),
                    'pattern_match_score': company.get('composite_score', 50) * 0.8,
                    'undervaluation_score': company.get('composite_score', 50) * 0.9,
                    'potential_score': company.get('composite_score', 50) * 0.85,
                    'recommendation_strength': self._get_recommendation_strength(company.get('composite_score', 50)),
                    'risk_factors': self._generate_risk_factors(company),
                    'catalyst_timeline': self._generate_catalyst_timeline(company)
                }
                enhanced_companies.append(enhanced_company)
            
            return enhanced_companies
            
        except Exception as e:
            logging.error(f"Failed to parse LLM response: {e}")
            return []
    
    def _generate_manual_alternatives(self, characteristics: Dict, thesis_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate manual alternatives when LLM fails - using diverse database"""
        sector = characteristics.get('sector', 'Technology')
        business_model = characteristics.get('business_model', 'SaaS')
        
        # Diverse company database for fallback
        company_database = {
            'Technology': {
                'SaaS': [
                    {
                        'name': 'Snowflake Inc.',
                        'ticker': 'SNOW',
                        'market_cap': 45.2,
                        'description': 'Cloud data platform with strong enterprise adoption',
                        'key_metrics': {'revenue_growth': 0.48, 'gross_margin': 0.69, 'customer_retention': 0.95},
                        'unloved_factors': ['High valuation concerns', 'Competitive pressure', 'Slowing growth rate'],
                        'hidden_strengths': ['Data network effects', 'Platform stickiness', 'Expanding use cases']
                    },
                    {
                        'name': 'Palantir Technologies',
                        'ticker': 'PLTR',
                        'market_cap': 38.7,
                        'description': 'Data analytics and AI platform for enterprises and government',
                        'key_metrics': {'revenue_growth': 0.24, 'gross_margin': 0.82, 'customer_count': 498},
                        'unloved_factors': ['Government dependency', 'Limited commercial traction', 'Stock volatility'],
                        'hidden_strengths': ['Mission-critical applications', 'Long contract terms', 'AI differentiation']
                    },
                    {
                        'name': 'UiPath Inc.',
                        'ticker': 'PATH',
                        'market_cap': 7.1,
                        'description': 'Robotic process automation platform',
                        'key_metrics': {'revenue_growth': 0.19, 'gross_margin': 0.85, 'arr': 1.02},
                        'unloved_factors': ['RPA market maturity', 'Customer churn', 'Execution challenges'],
                        'hidden_strengths': ['Automation necessity', 'Cost savings ROI', 'Platform expansion']
                    }
                ],
                'Hardware': [
                    {
                        'name': 'Advanced Micro Devices',
                        'ticker': 'AMD',
                        'market_cap': 227.8,
                        'description': 'Semiconductor company competing with Intel and Nvidia',
                        'key_metrics': {'revenue_growth': 0.09, 'gross_margin': 0.45, 'market_share': 0.24},
                        'unloved_factors': ['Intel competition', 'Cyclical industry', 'Nvidia AI dominance'],
                        'hidden_strengths': ['Server market share gains', 'Energy efficiency', 'Data center growth']
                    },
                    {
                        'name': 'Marvell Technology',
                        'ticker': 'MRVL',
                        'market_cap': 73.9,
                        'description': 'Semiconductor solutions for data infrastructure',
                        'key_metrics': {'revenue_growth': 0.07, 'gross_margin': 0.63, 'r_and_d': 0.19},
                        'unloved_factors': ['Smaller scale vs competitors', 'Market volatility', 'Supply chain risks'],
                        'hidden_strengths': ['5G infrastructure', 'Cloud connectivity', 'Automotive growth']
                    }
                ]
            },
            'Healthcare': {
                'Biotech': [
                    {
                        'name': 'Moderna Inc.',
                        'ticker': 'MRNA',
                        'market_cap': 34.2,
                        'description': 'mRNA technology platform for vaccines and therapeutics',
                        'key_metrics': {'revenue_growth': -0.62, 'gross_margin': 0.69, 'pipeline_programs': 48},
                        'unloved_factors': ['COVID revenue decline', 'Unproven platform', 'High R&D costs'],
                        'hidden_strengths': ['mRNA platform versatility', 'Vaccine expertise', 'Pipeline breadth']
                    },
                    {
                        'name': 'BioNTech SE',
                        'ticker': 'BNTX',
                        'market_cap': 25.8,
                        'description': 'Immunotherapy company with mRNA and cell therapy platforms',
                        'key_metrics': {'revenue_growth': -0.58, 'gross_margin': 0.71, 'cash_position': 18.1},
                        'unloved_factors': ['Post-COVID transition', 'European base', 'Oncology uncertainty'],
                        'hidden_strengths': ['Cancer immunotherapy', 'Strong pipeline', 'Technology platform']
                    }
                ]
            },
            'Consumer': {
                'E-commerce': [
                    {
                        'name': 'Shopify Inc.',
                        'ticker': 'SHOP',
                        'market_cap': 82.4,
                        'description': 'E-commerce platform for small and medium businesses',
                        'key_metrics': {'revenue_growth': 0.21, 'gross_margin': 0.51, 'merchant_solutions_growth': 0.18},
                        'unloved_factors': ['Post-pandemic normalization', 'Competition from Amazon', 'Take rate pressure'],
                        'hidden_strengths': ['SMB market leadership', 'International expansion', 'Fintech integration']
                    },
                    {
                        'name': 'Sea Limited',
                        'ticker': 'SE',
                        'market_cap': 89.1,
                        'description': 'Digital entertainment and e-commerce in Southeast Asia',
                        'key_metrics': {'revenue_growth': 0.05, 'gross_margin': 0.42, 'active_users': 729},
                        'unloved_factors': ['Regulatory risks', 'Profitability concerns', 'Market competition'],
                        'hidden_strengths': ['Gaming cash generation', 'Southeast Asia exposure', 'Digital payments']
                    }
                ]
            }
        }
        
        # Select relevant companies based on characteristics
        sector_companies = company_database.get(sector, {})
        model_companies = sector_companies.get(business_model, [])
        
        # If no exact match, get from broader sector
        if not model_companies:
            for model_type in sector_companies.values():
                model_companies.extend(model_type)
        
        # If still no matches, get from all sectors
        if not model_companies:
            for sector_data in company_database.values():
                for model_type in sector_data.values():
                    model_companies.extend(model_type)
        
        return model_companies[:12]  # Return top 12 candidates
    
    def _score_alternatives(self, alternatives: List[Dict], characteristics: Dict) -> List[Dict[str, Any]]:
        """Score and rank alternative companies"""
        scored_alternatives = []
        
        for company in alternatives:
            # Calculate pattern match score
            pattern_score = self._calculate_pattern_match_score(company, characteristics)
            
            # Calculate undervaluation score
            undervaluation_score = self._calculate_undervaluation_score(company)
            
            # Calculate hidden potential score
            potential_score = self._calculate_potential_score(company, characteristics)
            
            # Composite score
            composite_score = (
                pattern_score * 0.4 +
                undervaluation_score * 0.35 +
                potential_score * 0.25
            )
            
            company_with_score = company.copy()
            company_with_score.update({
                'pattern_match_score': round(pattern_score, 1),
                'undervaluation_score': round(undervaluation_score, 1),
                'potential_score': round(potential_score, 1),
                'composite_score': round(composite_score, 1),
                'recommendation_strength': self._get_recommendation_strength(composite_score),
                'risk_factors': self._generate_risk_factors(company),
                'catalyst_timeline': self._generate_catalyst_timeline(company)
            })
            
            scored_alternatives.append(company_with_score)
        
        # Sort by composite score
        return sorted(scored_alternatives, key=lambda x: x['composite_score'], reverse=True)
    
    def _identify_sector(self, core_claim: str) -> str:
        """Identify sector from thesis core claim"""
        if any(keyword in core_claim for keyword in ['software', 'saas', 'cloud', 'ai', 'tech', 'semiconductor']):
            return 'Technology'
        elif any(keyword in core_claim for keyword in ['biotech', 'pharma', 'healthcare', 'medical']):
            return 'Healthcare'
        elif any(keyword in core_claim for keyword in ['retail', 'consumer', 'e-commerce', 'marketplace']):
            return 'Consumer'
        elif any(keyword in core_claim for keyword in ['finance', 'bank', 'fintech', 'payment']):
            return 'Financial'
        elif any(keyword in core_claim for keyword in ['energy', 'renewable', 'oil', 'solar']):
            return 'Energy'
        else:
            return 'Technology'  # Default
    
    def _identify_business_model(self, core_claim: str) -> str:
        """Identify business model from thesis"""
        if 'saas' in core_claim or 'subscription' in core_claim:
            return 'SaaS'
        elif 'marketplace' in core_claim or 'platform' in core_claim:
            return 'Platform'
        elif 'hardware' in core_claim or 'semiconductor' in core_claim:
            return 'Hardware'
        elif 'biotech' in core_claim or 'drug' in core_claim:
            return 'Biotech'
        elif 'retail' in core_claim or 'e-commerce' in core_claim:
            return 'E-commerce'
        else:
            return 'SaaS'  # Default
    
    def _identify_growth_stage(self, signals: List[Dict]) -> str:
        """Identify growth stage from signals"""
        signal_count = len(signals)
        
        if signal_count > 10:
            return 'Mature Growth'
        elif signal_count > 6:
            return 'Scaling'
        else:
            return 'Early Growth'
    
    def _extract_value_drivers(self, core_claim: str, signals: List[Dict]) -> List[str]:
        """Extract key value drivers"""
        drivers = []
        
        # From core claim
        if 'revenue' in core_claim:
            drivers.append('Revenue Growth')
        if 'margin' in core_claim:
            drivers.append('Margin Expansion')
        if 'market share' in core_claim:
            drivers.append('Market Share Gains')
        if 'innovation' in core_claim:
            drivers.append('Product Innovation')
        
        # From signals
        for signal in signals[:5]:
            signal_name = signal.get('signal_name', '').lower()
            if 'revenue' in signal_name:
                drivers.append('Revenue Growth')
            elif 'margin' in signal_name:
                drivers.append('Margin Expansion')
            elif 'customer' in signal_name:
                drivers.append('Customer Acquisition')
            elif 'market' in signal_name:
                drivers.append('Market Expansion')
        
        return list(set(drivers))[:4]  # Top 4 unique drivers
    
    def _extract_market_characteristics(self, core_claim: str) -> Dict[str, Any]:
        """Extract market characteristics"""
        return {
            'market_size': 'Large' if 'large market' in core_claim else 'Medium',
            'growth_rate': 'High' if 'high growth' in core_claim else 'Medium',
            'competition': 'Fragmented' if 'fragmented' in core_claim else 'Competitive'
        }
    
    def _analyze_signal_patterns(self, signals: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in signals"""
        active_count = len([s for s in signals if s.get('status') == 'active'])
        total_count = len(signals)
        
        return {
            'total_signals': total_count,
            'active_ratio': round(active_count / total_count if total_count > 0 else 0, 2),
            'monitoring_intensity': 'High' if total_count > 8 else 'Medium' if total_count > 4 else 'Low'
        }
    
    def _calculate_pattern_match_score(self, company: Dict, characteristics: Dict) -> float:
        """Calculate how well company matches thesis patterns"""
        base_score = 60.0
        
        # Business model alignment
        if characteristics.get('sector') == 'Technology' and 'technology' in company.get('description', '').lower():
            base_score += 15
        
        # Growth characteristics
        company_growth = company.get('key_metrics', {}).get('revenue_growth', 0)
        if company_growth > 0.2:  # >20% growth
            base_score += 10
        elif company_growth > 0.1:  # >10% growth
            base_score += 5
        
        # Market position
        market_cap = company.get('market_cap', 0)
        if 10 < market_cap < 100:  # Mid-cap sweet spot
            base_score += 8
        elif market_cap > 100:  # Large cap penalty for "unloved" factor
            base_score -= 5
        
        return min(95, max(30, base_score))
    
    def _calculate_undervaluation_score(self, company: Dict) -> float:
        """Calculate undervaluation/unloved score"""
        base_score = 50.0
        
        # Number of unloved factors (more = higher score)
        unloved_factors = len(company.get('unloved_factors', []))
        base_score += unloved_factors * 8
        
        # Market cap consideration (smaller = more unloved potential)
        market_cap = company.get('market_cap', 0)
        if market_cap < 20:
            base_score += 15
        elif market_cap < 50:
            base_score += 10
        elif market_cap < 100:
            base_score += 5
        
        # Revenue growth (negative growth = more unloved)
        growth = company.get('key_metrics', {}).get('revenue_growth', 0)
        if growth < 0:
            base_score += 12
        elif growth < 0.1:
            base_score += 6
        
        return min(95, max(20, base_score))
    
    def _calculate_potential_score(self, company: Dict, characteristics: Dict) -> float:
        """Calculate hidden potential score"""
        base_score = 55.0
        
        # Hidden strengths count
        hidden_strengths = len(company.get('hidden_strengths', []))
        base_score += hidden_strengths * 7
        
        # Gross margin quality
        gross_margin = company.get('key_metrics', {}).get('gross_margin', 0.3)
        if gross_margin > 0.7:
            base_score += 12
        elif gross_margin > 0.5:
            base_score += 8
        elif gross_margin > 0.3:
            base_score += 4
        
        # Platform/moat characteristics
        description = company.get('description', '').lower()
        if any(keyword in description for keyword in ['platform', 'network', 'ecosystem']):
            base_score += 10
        
        return min(95, max(25, base_score))
    
    def _get_recommendation_strength(self, composite_score: float) -> str:
        """Get recommendation strength based on score"""
        if composite_score >= 80:
            return 'Strong Alternative'
        elif composite_score >= 70:
            return 'Good Alternative'
        elif composite_score >= 60:
            return 'Moderate Alternative'
        else:
            return 'Weak Alternative'
    
    def _generate_risk_factors(self, company: Dict) -> List[str]:
        """Generate specific risk factors for company"""
        base_risks = ['Market volatility', 'Execution risk', 'Competitive pressure']
        unloved_factors = company.get('unloved_factors', [])
        
        # Combine and limit to top 4 risks
        all_risks = base_risks + unloved_factors[:2]
        return all_risks[:4]
    
    def _generate_catalyst_timeline(self, company: Dict) -> List[Dict[str, str]]:
        """Generate potential catalyst timeline"""
        return [
            {
                'timeframe': 'Next Quarter',
                'catalyst': 'Earnings surprise potential',
                'probability': 'Medium'
            },
            {
                'timeframe': '3-6 Months',
                'catalyst': 'Product/service expansion',
                'probability': 'High'
            },
            {
                'timeframe': '6-12 Months',
                'catalyst': 'Market recognition/rerating',
                'probability': 'Medium'
            }
        ]
    
    def _get_analysis_criteria(self, characteristics: Dict) -> List[str]:
        """Get analysis criteria used for matching"""
        return [
            f"Sector: {characteristics.get('sector')}",
            f"Business Model: {characteristics.get('business_model')}",
            f"Growth Stage: {characteristics.get('growth_stage')}",
            f"Value Drivers: {', '.join(characteristics.get('value_drivers', [])[:2])}",
            f"Signal Intensity: {characteristics.get('signal_patterns', {}).get('monitoring_intensity', 'Medium')}"
        ]
    
    def _generate_fallback_alternatives(self) -> Dict[str, Any]:
        """Generate fallback alternatives when analysis fails"""
        # Generate basic alternatives based on common patterns
        fallback_companies = [
            {
                'name': 'Palantir Technologies',
                'ticker': 'PLTR',
                'market_cap': 38.7,
                'description': 'Data analytics and AI platform for enterprises and government',
                'key_metrics': {'revenue_growth': 0.24, 'gross_margin': 0.82, 'customer_count': 498},
                'unloved_factors': ['Government dependency', 'Limited commercial traction', 'Stock volatility'],
                'hidden_strengths': ['Mission-critical applications', 'Long contract terms', 'AI differentiation'],
                'composite_score': 78.5,
                'pattern_match_score': 75.0,
                'undervaluation_score': 82.0,
                'potential_score': 80.0,
                'recommendation_strength': 'Good Alternative',
                'risk_factors': ['Market volatility', 'Execution risk', 'Government dependency'],
                'catalyst_timeline': [
                    {'timeframe': 'Next Quarter', 'catalyst': 'Earnings surprise potential', 'probability': 'Medium'},
                    {'timeframe': '3-6 Months', 'catalyst': 'Commercial expansion', 'probability': 'High'}
                ]
            },
            {
                'name': 'UiPath Inc.',
                'ticker': 'PATH',
                'market_cap': 7.1,
                'description': 'Robotic process automation platform',
                'key_metrics': {'revenue_growth': 0.19, 'gross_margin': 0.85, 'arr': 1.02},
                'unloved_factors': ['RPA market maturity', 'Customer churn', 'Execution challenges'],
                'hidden_strengths': ['Automation necessity', 'Cost savings ROI', 'Platform expansion'],
                'composite_score': 76.2,
                'pattern_match_score': 72.0,
                'undervaluation_score': 85.0,
                'potential_score': 75.0,
                'recommendation_strength': 'Good Alternative',
                'risk_factors': ['Market volatility', 'Execution risk', 'RPA market maturity'],
                'catalyst_timeline': [
                    {'timeframe': 'Next Quarter', 'catalyst': 'Market expansion', 'probability': 'Medium'},
                    {'timeframe': '6-12 Months', 'catalyst': 'Product innovation', 'probability': 'High'}
                ]
            }
        ]
        
        return {
            'thesis_characteristics': {
                'sector': 'Technology',
                'business_model': 'SaaS',
                'growth_stage': 'Scaling',
                'value_drivers': ['Revenue Growth', 'Market Expansion'],
                'signal_patterns': {'monitoring_intensity': 'Medium'}
            },
            'alternative_companies': fallback_companies,
            'total_found': len(fallback_companies),
            'analysis_criteria': [
                'Sector: Technology',
                'Business Model: SaaS',
                'Growth Stage: Scaling',
                'Pattern matching analysis'
            ],
            'generated_at': datetime.utcnow().isoformat()
        }