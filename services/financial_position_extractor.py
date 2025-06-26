"""
Financial Position Extractor Service
Extracts key financial positions and thesis statements from research documents
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from services.azure_openai_service import AzureOpenAIService


class FinancialPositionExtractor:
    """Extract financial positions and investment recommendations from research documents"""
    
    def __init__(self):
        self.azure_service = AzureOpenAIService()
        self.position_keywords = {
            'buy': ['buy', 'strong buy', 'outperform', 'overweight', 'positive', 'bullish', 'long'],
            'sell': ['sell', 'strong sell', 'underperform', 'underweight', 'negative', 'bearish', 'short'],
            'hold': ['hold', 'neutral', 'maintain', 'stable', 'fair value'],
            'trim': ['trim', 'reduce', 'take profits', 'partial sale', 'rotation']
        }
        
    def extract_financial_position(self, document_content: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract the primary financial position from research document content
        
        Args:
            document_content: Text content from research document
            filename: Optional filename for context
            
        Returns:
            Dictionary containing extracted thesis statement and position details
        """
        try:
            # First, try to extract position using AI analysis
            ai_position = self._extract_position_with_ai(document_content, filename)
            
            if ai_position:
                # Validate and enhance with rule-based extraction
                rule_based_position = self._extract_position_with_rules(document_content)
                
                # Combine AI and rule-based results
                return self._combine_extraction_results(ai_position, rule_based_position, document_content)
            else:
                # Fallback to rule-based extraction
                logging.warning("AI extraction failed, using rule-based approach")
                return self._extract_position_with_rules(document_content)
                
        except Exception as e:
            logging.error(f"Financial position extraction failed: {str(e)}")
            return self._create_fallback_position(document_content)
    
    def _extract_position_with_ai(self, content: str, filename: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Use Azure OpenAI to extract financial position from document"""
        try:
            extraction_prompt = f"""
            Analyze this investment research document and extract the key financial position or investment thesis.
            
            Look for:
            1. Investment recommendation (BUY/SELL/HOLD/TRIM/etc.)
            2. Price targets and expected returns
            3. Core investment thesis or key message
            4. Key supporting arguments
            5. Risk factors and scenarios
            6. Time horizon for the position
            
            Document Content:
            {content[:4000]}  # Limit content to avoid token limits
            
            Return a JSON response with this structure:
            {{
                "investment_position": "BUY/SELL/HOLD/TRIM",
                "confidence_level": "HIGH/MEDIUM/LOW",
                "thesis_statement": "Clear, concise investment thesis statement",
                "expected_return": "Expected return percentage or target price",
                "time_horizon": "Investment time frame",
                "key_arguments": ["argument1", "argument2", "argument3"],
                "risk_factors": ["risk1", "risk2"],
                "company_name": "Primary company being analyzed",
                "sector": "Industry sector",
                "price_target": "Target price if mentioned",
                "current_price": "Current price if mentioned"
            }}
            
            Focus on extracting the most prominent investment position. If multiple positions exist, prioritize the primary recommendation.
            Ensure the thesis_statement is concise but comprehensive, capturing the core investment rationale.
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert financial analyst specializing in extracting investment positions from research documents. Return only valid JSON responses."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ]
            
            response = self.azure_service.generate_completion(messages, temperature=0.3, max_tokens=2000)
            
            if response:
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    logging.warning("AI response was not valid JSON, attempting to parse")
                    return self._parse_ai_response_text(response)
            
            return None
            
        except Exception as e:
            logging.error(f"AI position extraction failed: {str(e)}")
            return None
    
    def _extract_position_with_rules(self, content: str) -> Dict[str, Any]:
        """Extract financial position using rule-based pattern matching"""
        content_lower = content.lower()
        
        # Extract investment position
        position = self._identify_investment_position(content_lower)
        
        # Extract company name
        company_name = self._extract_company_name(content)
        
        # Extract price targets and returns
        price_info = self._extract_price_information(content)
        
        # Extract key sentences that contain investment rationale
        thesis_statement = self._extract_thesis_statement(content, position, company_name or "the company")
        
        # Extract supporting arguments
        key_arguments = self._extract_key_arguments(content)
        
        # Extract time horizon
        time_horizon = self._extract_time_horizon(content)
        
        return {
            "investment_position": position,
            "confidence_level": "MEDIUM",  # Rule-based has medium confidence
            "thesis_statement": thesis_statement,
            "expected_return": price_info.get('expected_return'),
            "time_horizon": time_horizon,
            "key_arguments": key_arguments,
            "risk_factors": self._extract_risk_factors(content),
            "company_name": company_name,
            "sector": self._extract_sector(content),
            "price_target": price_info.get('price_target'),
            "current_price": price_info.get('current_price')
        }
    
    def _identify_investment_position(self, content_lower: str) -> str:
        """Identify the primary investment position from content"""
        position_scores = {pos: 0 for pos in self.position_keywords.keys()}
        
        for position, keywords in self.position_keywords.items():
            for keyword in keywords:
                # Count occurrences, giving more weight to phrases at the beginning
                matches = content_lower.count(keyword)
                if matches > 0:
                    # Give extra weight if keyword appears in first 500 characters
                    if keyword in content_lower[:500]:
                        position_scores[position] += matches * 2
                    else:
                        position_scores[position] += matches
        
        # Return the position with highest score
        max_score = max(position_scores.values())
        if max_score > 0:
            for position, score in position_scores.items():
                if score == max_score:
                    return position.upper()
        
        return "HOLD"  # Default if no clear position found
    
    def _extract_company_name(self, content: str) -> Optional[str]:
        """Extract primary company name from content"""
        # Look for ticker symbols in parentheses
        ticker_pattern = r'\(([A-Z]{1,5})\)'
        tickers = re.findall(ticker_pattern, content)
        
        if tickers:
            return tickers[0]
        
        # Look for company names in titles or headers
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if ':' in line and len(line) < 100:
                # Potential company name in title
                parts = line.split(':')
                if len(parts) >= 2:
                    potential_name = parts[0].strip()
                    if len(potential_name) > 3 and len(potential_name) < 50:
                        return potential_name
        
        return None
    
    def _extract_price_information(self, content: str) -> Dict[str, Optional[str]]:
        """Extract price targets, current prices, and expected returns"""
        # Look for price targets
        price_target_patterns = [
            r'price target[s]?[:\s]+\$?(\d+(?:\.\d+)?)',
            r'target price[s]?[:\s]+\$?(\d+(?:\.\d+)?)',
            r'fair value[:\s]+\$?(\d+(?:\.\d+)?)'
        ]
        
        # Look for return percentages
        return_patterns = [
            r'(\d+(?:\.\d+)?)%\s+(?:return|upside|tsr)',
            r'(?:return|upside|tsr)[:\s]+(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s+(?:cagr|growth)'
        ]
        
        price_target = None
        expected_return = None
        
        for pattern in price_target_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                price_target = f"${match.group(1)}"
                break
        
        for pattern in return_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                expected_return = f"{match.group(1)}%"
                break
        
        return {
            "price_target": price_target,
            "expected_return": expected_return,
            "current_price": None  # Could be enhanced with current price extraction
        }
    
    def _extract_thesis_statement(self, content: str, position: str, company_name: str) -> str:
        """Generate a concise thesis statement from document content"""
        sentences = content.split('.')
        
        # Look for sentences containing key thesis indicators
        thesis_indicators = [
            'investment thesis', 'key message', 'bottom line', 'summary',
            'positioned', 'opportunity', 'expects', 'believes', 'view'
        ]
        
        candidate_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 300:
                sentence_lower = sentence.lower()
                if any(indicator in sentence_lower for indicator in thesis_indicators):
                    candidate_sentences.append(sentence)
        
        if candidate_sentences:
            # Return the first relevant sentence
            return candidate_sentences[0]
        
        # Fallback: create thesis statement from extracted information
        company_ref = company_name if company_name else "the company"
        return f"{position}: {company_ref} presents an attractive investment opportunity based on fundamental analysis"
    
    def _extract_key_arguments(self, content: str) -> List[str]:
        """Extract key supporting arguments from content"""
        # Look for numbered lists, bullet points, or key sections
        arguments = []
        
        # Pattern for numbered arguments
        numbered_pattern = r'^\s*\d+[\.\)]\s+(.+?)(?=\n\s*\d+[\.\)]|\n\n|\Z)'
        numbered_matches = re.findall(numbered_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in numbered_matches[:5]:  # Limit to 5 arguments
            clean_arg = re.sub(r'\s+', ' ', match.strip())
            if len(clean_arg) > 20 and len(clean_arg) < 200:
                arguments.append(clean_arg)
        
        # If no numbered arguments, look for bullet points or key phrases
        if not arguments:
            key_phrases = [
                'driven by', 'expected to', 'positioned for', 'benefits from',
                'strong', 'growth', 'margin expansion', 'market share'
            ]
            
            sentences = content.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and len(sentence) < 150:
                    if any(phrase in sentence.lower() for phrase in key_phrases):
                        arguments.append(sentence)
                        if len(arguments) >= 3:
                            break
        
        return arguments[:5]  # Return maximum 5 arguments
    
    def _extract_risk_factors(self, content: str) -> List[str]:
        """Extract risk factors from content"""
        risks = []
        
        # Look for risk sections
        risk_indicators = ['risk', 'concern', 'challenge', 'threat', 'downside']
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 150:
                sentence_lower = sentence.lower()
                if any(indicator in sentence_lower for indicator in risk_indicators):
                    risks.append(sentence)
                    if len(risks) >= 3:
                        break
        
        return risks
    
    def _extract_sector(self, content: str) -> Optional[str]:
        """Extract industry sector from content"""
        sectors = [
            'technology', 'healthcare', 'financial', 'energy', 'utilities',
            'consumer', 'industrial', 'materials', 'telecommunications', 'real estate'
        ]
        
        content_lower = content.lower()
        for sector in sectors:
            if sector in content_lower:
                return sector.title()
        
        return None
    
    def _extract_time_horizon(self, content: str) -> Optional[str]:
        """Extract investment time horizon from content"""
        time_patterns = [
            r'(\d+)\s*(?:year|yr)s?',
            r'(\d+)\s*month',
            r'(?:over|within)\s+(\d+)\s*(?:year|yr)s?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return f"{match.group(1)} years"
        
        return None
    
    def _combine_extraction_results(self, ai_result: Dict, rule_result: Dict, content: str) -> Dict[str, Any]:
        """Combine AI and rule-based extraction results"""
        # Prioritize AI results but fill gaps with rule-based results
        combined = ai_result.copy()
        
        for key, value in rule_result.items():
            if not combined.get(key) and value:
                combined[key] = value
        
        # Ensure we have a thesis statement
        if not combined.get('thesis_statement'):
            combined['thesis_statement'] = self._create_fallback_thesis(content, combined)
        
        # Set confidence based on availability of key fields
        key_fields = ['investment_position', 'thesis_statement', 'company_name']
        available_fields = sum(1 for field in key_fields if combined.get(field))
        
        if available_fields >= 3:
            combined['confidence_level'] = 'HIGH'
        elif available_fields >= 2:
            combined['confidence_level'] = 'MEDIUM'
        else:
            combined['confidence_level'] = 'LOW'
        
        return combined
    
    def _create_fallback_position(self, content: str) -> Dict[str, Any]:
        """Create a fallback position when extraction fails"""
        return {
            "investment_position": "HOLD",
            "confidence_level": "LOW",
            "thesis_statement": "Investment analysis based on research document review",
            "expected_return": None,
            "time_horizon": None,
            "key_arguments": ["Fundamental analysis conducted", "Research document reviewed"],
            "risk_factors": ["Market volatility", "Execution risk"],
            "company_name": None,
            "sector": None,
            "price_target": None,
            "current_price": None
        }
    
    def _create_fallback_thesis(self, content: str, position_data: Dict) -> str:
        """Create a fallback thesis statement"""
        position = position_data.get('investment_position', 'HOLD')
        company = position_data.get('company_name', 'the analyzed company')
        
        return f"{position}: {company} presents an investment opportunity based on comprehensive research analysis"
    
    def _parse_ai_response_text(self, response: str) -> Optional[Dict[str, Any]]:
        """Attempt to parse AI response when JSON parsing fails"""
        try:
            # Try to extract key information from text response
            lines = response.split('\n')
            result = {}
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip().strip('"\'')
                    
                    if key in ['investment_position', 'thesis_statement', 'company_name']:
                        result[key] = value
            
            if result:
                return result
            
        except Exception:
            pass
        
        return None