import os
import logging
import pandas as pd
from datetime import datetime
import pypdf
import openpyxl
from pathlib import Path

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = {'.pdf', '.xlsx', '.xls', '.csv'}
    
    def process_document(self, file_path):
        """
        Process a document and extract structured data
        """
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            logging.info(f"Processing document: {file_path.name}")
            
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return self._process_excel(file_path)
            elif file_extension == '.csv':
                return self._process_csv(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logging.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def _process_pdf(self, file_path):
        """Process PDF document and extract text and tables"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'document_type': 'pdf',
                    'page_count': len(pdf_reader.pages),
                    'file_size': os.path.getsize(file_path),
                    'processed_at': datetime.utcnow().isoformat()
                }
                
                # Extract text content
                text_content = ""
                tables = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                    
                    # Try to extract table-like data from text
                    page_tables = self._extract_tables_from_text(page_text)
                    if page_tables:
                        tables.extend(page_tables)
                
                # Analyze content for key financial terms
                key_metrics = self._extract_financial_metrics(text_content)
                
                return {
                    'text_content': text_content.strip(),
                    'tables': tables,
                    'key_metrics': key_metrics,
                    'document_metadata': metadata,
                    'summary': self._create_document_summary(text_content, tables, metadata)
                }
                
        except Exception as e:
            logging.error(f"Error processing PDF {file_path}: {str(e)}")
            raise
    
    def _process_excel(self, file_path):
        """Process Excel document and extract data from all sheets"""
        try:
            # Load workbook
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            
            metadata = {
                'document_type': 'excel',
                'sheet_count': len(workbook.sheetnames),
                'sheet_names': workbook.sheetnames,
                'file_size': os.path.getsize(file_path),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            sheets_data = {}
            all_tables = []
            
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                
                # Convert sheet to DataFrame
                data = []
                for row in sheet.iter_rows(values_only=True):
                    data.append(row)
                
                if data:
                    # Create DataFrame and clean it
                    df = pd.DataFrame(data)
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    if not df.empty:
                        # Convert to dictionary format
                        sheet_dict = df.to_dict('records')
                        sheets_data[sheet_name] = sheet_dict
                        
                        # Add to tables list
                        all_tables.append({
                            'sheet_name': sheet_name,
                            'data': sheet_dict,
                            'shape': df.shape,
                            'columns': list(df.columns) if hasattr(df, 'columns') else []
                        })
            
            # Extract key metrics from numerical data
            key_metrics = self._extract_metrics_from_tables(all_tables)
            
            return {
                'sheets_data': sheets_data,
                'tables': all_tables,
                'key_metrics': key_metrics,
                'document_metadata': metadata,
                'summary': self._create_excel_summary(sheets_data, metadata)
            }
            
        except Exception as e:
            logging.error(f"Error processing Excel file {file_path}: {str(e)}")
            raise
    
    def _process_csv(self, file_path):
        """Process CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            metadata = {
                'document_type': 'csv',
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'file_size': os.path.getsize(file_path),
                'processed_at': datetime.utcnow().isoformat()
            }
            
            # Convert to dictionary format
            data = df.to_dict('records')
            
            # Create table structure
            table = {
                'data': data,
                'shape': df.shape,
                'columns': list(df.columns)
            }
            
            # Extract key metrics
            key_metrics = self._extract_metrics_from_dataframe(df)
            
            return {
                'data': data,
                'tables': [table],
                'key_metrics': key_metrics,
                'document_metadata': metadata,
                'summary': self._create_csv_summary(df, metadata)
            }
            
        except Exception as e:
            logging.error(f"Error processing CSV file {file_path}: {str(e)}")
            raise
    
    def _extract_tables_from_text(self, text):
        """Extract table-like structures from text"""
        tables = []
        lines = text.split('\n')
        
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_table and in_table:
                    tables.append(current_table)
                    current_table = []
                    in_table = False
                continue
            
            # Check if line looks like a table row (contains multiple columns)
            if '\t' in line or '  ' in line:
                if not in_table:
                    in_table = True
                
                # Split by tabs or multiple spaces
                columns = [col.strip() for col in line.replace('\t', '|').split('|') if col.strip()]
                if len(columns) > 1:
                    current_table.append(columns)
        
        # Add the last table if exists
        if current_table:
            tables.append(current_table)
        
        return tables
    
    def _extract_financial_metrics(self, text):
        """Extract financial metrics and key numbers from text"""
        import re
        
        metrics = {}
        
        # Common financial patterns
        patterns = {
            'revenue': r'revenue[:\s]+\$?([\d,\.]+)',
            'profit': r'profit[:\s]+\$?([\d,\.]+)',
            'margin': r'margin[:\s]+([\d,\.]+)%?',
            'growth': r'growth[:\s]+([\d,\.]+)%?',
            'price': r'price[:\s]+\$?([\d,\.]+)',
            'volume': r'volume[:\s]+([\d,\.]+)',
            'eps': r'eps[:\s]+\$?([\d,\.]+)',
            'pe_ratio': r'p/e[:\s]+([\d,\.]+)'
        }
        
        for metric_name, pattern in patterns.items():
            matches = re.findall(pattern, text.lower())
            if matches:
                # Take the first match and clean it
                value = matches[0].replace(',', '')
                try:
                    metrics[metric_name] = float(value)
                except ValueError:
                    metrics[metric_name] = value
        
        return metrics
    
    def _extract_metrics_from_tables(self, tables):
        """Extract key metrics from table data"""
        metrics = {}
        
        for table in tables:
            if 'data' in table:
                for row in table['data']:
                    if isinstance(row, dict):
                        for key, value in row.items():
                            if isinstance(value, (int, float)):
                                # Store numeric values with their context
                                metric_key = f"{table.get('sheet_name', 'table')}_{key}"
                                metrics[metric_key] = value
        
        return metrics
    
    def _extract_metrics_from_dataframe(self, df):
        """Extract key metrics from a pandas DataFrame"""
        metrics = {}
        
        # Get numeric columns
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        for col in numeric_columns:
            series = df[col].dropna()
            if not series.empty:
                metrics[f"{col}_mean"] = series.mean()
                metrics[f"{col}_max"] = series.max()
                metrics[f"{col}_min"] = series.min()
                if len(series) > 1:
                    metrics[f"{col}_std"] = series.std()
        
        return metrics
    
    def _create_document_summary(self, text_content, tables, metadata):
        """Create a summary of the PDF document"""
        word_count = len(text_content.split())
        table_count = len(tables)
        
        return {
            'word_count': word_count,
            'table_count': table_count,
            'page_count': metadata.get('page_count', 0),
            'has_financial_data': bool(tables),
            'content_preview': text_content[:200] + '...' if len(text_content) > 200 else text_content
        }
    
    def _create_excel_summary(self, sheets_data, metadata):
        """Create a summary of the Excel document"""
        total_rows = sum(len(sheet_data) for sheet_data in sheets_data.values())
        
        return {
            'sheet_count': metadata.get('sheet_count', 0),
            'total_rows': total_rows,
            'sheet_names': metadata.get('sheet_names', []),
            'has_data': total_rows > 0
        }
    
    def _create_csv_summary(self, df, metadata):
        """Create a summary of the CSV file"""
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'numeric_columns': list(df.select_dtypes(include=['number']).columns),
            'has_data': len(df) > 0
        }
    
    def get_supported_formats(self):
        """Return list of supported file formats"""
        return list(self.supported_formats)
