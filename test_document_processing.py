"""
Test document processing to identify the content extraction issue
"""

import os
from services.document_processor import DocumentProcessor

def test_document_processing():
    """Test document processing with sample content"""
    
    # Create test content file
    test_content = """
Investment Thesis: BUY CARR (99% 3-yr base case return): a historically starved business with leading HVAC market 
share, now regaining its focus on growth (with a Gitlin leading the turnaround).

I view Carrier as a fundamentally undervalued business trading at trough valuations and trough volumes – primarily 
due to high leverage and partially due to underinvestment in R&D and sales (as a subsidiary of UTC). As management 
executes on its 3-year supply chain cost-out/reinvestment plan and deleverages, I project a 90% base case return – even 
on a modest volume rebound (base case assumes 2024 revenues at 2019 levels).

Price Target: $65 (current: $43)
Expected Return: 90% over 3 years
Risk: High leverage, cyclical exposure
"""
    
    # Create a test PDF-like file (text file for testing)
    test_filename = "test_research.txt"
    try:
        with open(test_filename, 'w') as f:
            f.write(test_content)
        
        processor = DocumentProcessor()
        
        # Check if txt files are supported
        print(f"Supported formats: {processor.supported_formats}")
        
        # For now, let's create a simple CSV for testing
        csv_filename = "test_research.csv"
        with open(csv_filename, 'w') as f:
            f.write("Content\n")
            f.write(f'"{test_content}"\n')
        
        try:
            result = processor.process_document(csv_filename)
            print("Document processing result keys:", list(result.keys()))
            
            for key, value in result.items():
                if isinstance(value, str):
                    print(f"{key}: {value[:100]}...")
                else:
                    print(f"{key}: {type(value)} - {value}")
                    
        except Exception as e:
            print(f"Document processing failed: {e}")
        
        # Clean up
        os.remove(csv_filename)
        
    except Exception as e:
        print(f"Test failed: {e}")
    
    finally:
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    test_document_processing()