import json
import re
import os
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleaner:
    
    def __init__(self):
        pass
    
    def clean_html(self, html_content: str) -> str:
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            return text
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_content
    
    def remove_noise(self, text: str) -> str:
        if not text:
            return ""
        
        # Remove common noise patterns
        noise_patterns = [
            r'Home\s*>\s*.*?>', # Breadcrumbs
            r'Copyright.*?\d{4}', # Copyright notices
            r'All Rights Reserved',
            r'Follow us on.*?(?:\n|$)',
            r'Share on.*?(?:\n|$)',
            r'Click here.*?(?:\n|$)',
            r'Read more.*?(?:\n|$)',
            r'Subscribe.*?newsletter',
            r'Cookie.*?policy',
            r'Privacy.*?policy',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def normalize_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Fix common encoding issues
        text = text.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)
        
        return text.strip()
    
    def clean_text(self, text: str) -> str:
        text = self.remove_noise(text)
        text = self.normalize_text(text)
        return text


class DataConsolidator:
    
    def __init__(self):
        self.cleaner = DataCleaner()
    
    def consolidate_loan_data(self, raw_data: List[Dict]) -> str:
        logger.info("Consolidating loan data...")
        
        # Group by loan type
        grouped_data = self.structure_by_product(raw_data)
        
        # Build consolidated document
        consolidated_text = "# Bank of Maharashtra Loan Products Knowledge Base\n\n"
        consolidated_text += "This document contains comprehensive information about various loan products offered by Bank of Maharashtra.\n\n"
        
        for loan_type, loans in grouped_data.items():
            consolidated_text += f"\n## {loan_type}\n\n"
            
            for loan in loans:
                if not loan.get('success', False):
                    continue
                
                loan_name = loan.get('loan_name', 'Unknown Loan')
                content = loan.get('content', '')
                
                # Clean the content
                if loan.get('raw_html'):
                    content = self.cleaner.clean_html(loan['raw_html'])
                
                content = self.cleaner.clean_text(content)
                
                if content:
                    consolidated_text += f"### {loan_name}\n\n"
                    consolidated_text += f"{content}\n\n"
                    consolidated_text += f"Source: {loan.get('url', 'N/A')}\n\n"
                    consolidated_text += "---\n\n"
        
        logger.info(f"Consolidated {len(raw_data)} loan pages")
        return consolidated_text
    
    def structure_by_product(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = {}
        
        for item in data:
            if not item.get('success', False):
                continue
            
            loan_type = item.get('loan_type', 'Other Loans')
            
            if loan_type not in grouped:
                grouped[loan_type] = []
            
            grouped[loan_type].append(item)
        
        # Sort by loan type
        return dict(sorted(grouped.items()))


class TextChunker:
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Use LangChain's RecursiveCharacterTextSplitter for intelligent splitting
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def chunk_text(self, text: str) -> List[Dict]:
        logger.info(f"Chunking text (size={self.chunk_size}, overlap={self.overlap})...")
        
        # Split text into chunks
        chunks = self.splitter.split_text(text)
        
        # Add metadata to each chunk
        chunked_data = []
        for i, chunk in enumerate(chunks):
            # Extract loan type from chunk if possible
            loan_type = self._extract_loan_type_from_chunk(chunk)
            
            chunked_data.append({
                'chunk_id': f"chunk_{i:04d}",
                'text': chunk,
                'loan_type': loan_type,
                'chunk_index': i,
                'total_chunks': len(chunks)
            })
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunked_data
    
    def _extract_loan_type_from_chunk(self, chunk: str) -> str:
        chunk_lower = chunk.lower()
        
        if 'home loan' in chunk_lower or 'housing loan' in chunk_lower:
            return 'Home Loan'
        elif 'car loan' in chunk_lower or 'vehicle loan' in chunk_lower:
            return 'Vehicle Loan'
        elif 'personal loan' in chunk_lower:
            return 'Personal Loan'
        elif 'education loan' in chunk_lower:
            return 'Education Loan'
        elif 'gold loan' in chunk_lower:
            return 'Gold Loan'
        elif 'agriculture' in chunk_lower or 'kisan' in chunk_lower:
            return 'Agriculture Loan'
        elif 'msme' in chunk_lower or 'business' in chunk_lower:
            return 'MSME Loan'
        elif 'interest rate' in chunk_lower:
            return 'Interest Rates'
        else:
            return 'General'


def process_data(input_file: str, output_file: str, chunks_file: str = None):
    logger.info("Starting data processing...")
    
    # Load raw data
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    logger.info(f"Loaded {len(raw_data)} raw data entries")
    
    # Consolidate data
    consolidator = DataConsolidator()
    consolidated_text = consolidator.consolidate_loan_data(raw_data)
    
    # Save consolidated text
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(consolidated_text)
    
    logger.info(f"Saved consolidated knowledge base to: {output_file}")
    
    # Chunk the text if chunks file is specified
    if chunks_file:
        chunker = TextChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk_text(consolidated_text)
        
        os.makedirs(os.path.dirname(chunks_file), exist_ok=True)
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(chunks)} chunks to: {chunks_file}")
    
    logger.info("Data processing complete!")
    
    return consolidated_text


def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    input_file = 'data/raw/scraped_data.json'
    output_file = 'data/processed/knowledge_base.txt'
    chunks_file = 'data/processed/chunks.json'
    
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run the scraper first: python src/scraper.py")
        return
    
    process_data(input_file, output_file, chunks_file)
    
    print(f"\n✅ Data processing complete!")
    print(f"📄 Knowledge base: {output_file}")
    print(f"📦 Chunks: {chunks_file}")


if __name__ == '__main__':
    main()
