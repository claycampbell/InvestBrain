import os
import logging
import pandas as pd
import PyPDF2
from openpyxl import load_workbook
from services.azure_openai_service import AzureOpenAIService

class DocumentProcessor:
    def __init__(self):
        self.openai_service = AzureOpenAIService()
        self.supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']
    
    def process_document(self, file_path):
        """
        Process uploaded research documents and extract key data
        """
        try:
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")
            
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return self._process_excel(file_path)
            elif file_extension == '.csv':
                return self._process_csv(file_path)
            else:
                raise Exception(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logging.error(f"Error processing document {file_path}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'data': None
            }
    
    def _process_pdf(self, file_path):
        """Extract text content from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                # Limit text length for processing
                if len(text_content) > 10000:
                    text_content = text_content[:10000] + "... [truncated]"
                
                # Extract key insights using AI if available
                insights = self._extract_insights(text_content, 'pdf')
                
                return {
                    'status': 'success',
                    'file_type': 'pdf',
                    'text_content': text_content,
                    'insights': insights,
                    'metadata': {
                        'pages': len(pdf_reader.pages),
                        'file_size': os.path.getsize(file_path)
                    }
                }
                
        except Exception as e:
            logging.error(f"Error processing PDF {file_path}: {str(e)}")
            return {
                'status': 'error',
                'message': f"PDF processing failed: {str(e)}",
                'data': None
            }
    
    def _process_excel(self, file_path):
        """Extract data from Excel files"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=None)
            
            processed_sheets = {}
            summary_data = []
            
            for sheet_name, sheet_data in df.items():
                # Process each sheet
                sheet_summary = {
                    'sheet_name': sheet_name,
                    'rows': len(sheet_data),
                    'columns': len(sheet_data.columns),
                    'column_names': list(sheet_data.columns)
                }
                
                # Extract numeric data for analysis
                numeric_columns = sheet_data.select_dtypes(include=['number']).columns
                if len(numeric_columns) > 0:
                    sheet_summary['numeric_summary'] = sheet_data[numeric_columns].describe().to_dict()
                
                processed_sheets[sheet_name] = sheet_summary
                summary_data.append(f"Sheet '{sheet_name}': {len(sheet_data)} rows, {len(sheet_data.columns)} columns")
            
            # Generate insights from the data
            data_summary = "; ".join(summary_data)
            insights = self._extract_insights(data_summary, 'excel')
            
            return {
                'status': 'success',
                'file_type': 'excel',
                'sheets': processed_sheets,
                'insights': insights,
                'metadata': {
                    'sheet_count': len(df),
                    'file_size': os.path.getsize(file_path)
                }
            }
            
        except Exception as e:
            logging.error(f"Error processing Excel {file_path}: {str(e)}")
            return {
                'status': 'error',
                'message': f"Excel processing failed: {str(e)}",
                'data': None
            }
    
    def _process_csv(self, file_path):
        """Extract data from CSV files"""
        try:
            df = pd.read_csv(file_path)
            
            # Basic data analysis
            data_summary = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            }
            
            # Numeric data summary
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                data_summary['numeric_summary'] = df[numeric_columns].describe().to_dict()
            
            # Generate insights
            summary_text = f"CSV with {len(df)} rows and {len(df.columns)} columns: {', '.join(df.columns[:5])}"
            insights = self._extract_insights(summary_text, 'csv')
            
            return {
                'status': 'success',
                'file_type': 'csv',
                'data_summary': data_summary,
                'insights': insights,
                'metadata': {
                    'file_size': os.path.getsize(file_path)
                }
            }
            
        except Exception as e:
            logging.error(f"Error processing CSV {file_path}: {str(e)}")
            return {
                'status': 'error',
                'message': f"CSV processing failed: {str(e)}",
                'data': None
            }
    
    def _extract_insights(self, content, file_type):
        """Extract key insights from document content using AI"""
        if not self.openai_service.is_available():
            return ["Document processed successfully but AI analysis unavailable"]
        
        try:
            prompt = f"""Analyze this {file_type} document content and extract key investment-relevant insights:

{content}

Please provide:
1. Key financial metrics or data points
2. Important trends or patterns
3. Relevant market information
4. Investment implications

Keep the response concise and actionable."""

            response = self.openai_service.generate_completion([
                {"role": "system", "content": "You are a financial analyst extracting key insights from research documents."},
                {"role": "user", "content": prompt}
            ], temperature=0.3)
            
            return [response] if response else ["Document processed but no insights extracted"]
            
        except Exception as e:
            logging.error(f"Error extracting insights: {str(e)}")
            return [f"Document processed successfully ({file_type})"]
    
    def get_supported_formats(self):
        """Return list of supported file formats"""
        return self.supported_formats