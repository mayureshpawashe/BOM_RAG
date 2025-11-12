import os
import sys
import argparse
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import BankOfMaharashtraScraper
from data_processor import process_data
from rag_pipeline import (
    EmbeddingManager,
    ChromaVectorStore,
    LLMClient,
    RAGPipeline,
    build_index
)

# Load environment variables
load_dotenv()


def cmd_scrape(args):
    print("\n🕷️  Starting web scraping...")
    print("=" * 80)
    
    base_url = os.getenv('BASE_URL', 'https://bankofmaharashtra.bank.in')
    delay = float(os.getenv('REQUEST_DELAY', 1.5))
    max_retries = int(os.getenv('MAX_RETRIES', 3))
    
    scraper = BankOfMaharashtraScraper(base_url, delay, max_retries)
    data = scraper.scrape_loan_products()
    scraper.save_raw_data(data, 'data/raw/scraped_data.json')
    
    print("\n✅ Scraping complete!")
    print(f"📊 Total pages scraped: {len(data)}")
    print(f"✓ Successful: {sum(1 for d in data if d.get('success', False))}")
    print(f"✗ Failed: {sum(1 for d in data if not d.get('success', False))}")
    print(f"💾 Data saved to: data/raw/scraped_data.json")


def cmd_process(args):
    print("\n🔄 Processing scraped data...")
    print("=" * 80)
    
    input_file = 'data/raw/scraped_data.json'
    output_file = 'data/processed/knowledge_base.txt'
    chunks_file = 'data/processed/chunks.json'
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        print("Please run 'python main.py scrape' first")
        return
    
    process_data(input_file, output_file, chunks_file)
    
    print("\n✅ Data processing complete!")
    print(f"📄 Knowledge base: {output_file}")
    print(f"📦 Chunks: {chunks_file}")


def cmd_build_index(args):
    print("\n🔨 Building ChromaDB index...")
    print("=" * 80)
    
    chunks_file = 'data/processed/chunks.json'
    persist_directory = os.getenv('CHROMA_PERSIST_DIR', './data/vector_store/chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    if not os.path.exists(chunks_file):
        print(f"❌ Error: {chunks_file} not found!")
        print("Please run 'python main.py process' first")
        return
    
    build_index(chunks_file, persist_directory, embedding_model)
    
    print("\n✅ Index building complete!")
    print(f"💾 ChromaDB saved to: {persist_directory}")


def cmd_query(args):
    print("\n🤖 Bank of Maharashtra Loan Assistant")
    print("=" * 80)
    
    # Load configuration
    persist_directory = os.getenv('CHROMA_PERSIST_DIR', './data/vector_store/chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_model = os.getenv('LLM_MODEL', 'gpt-4')
    top_k = int(os.getenv('TOP_K_RESULTS', 3))
    
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    if not os.path.exists(persist_directory):
        print(f"❌ Error: ChromaDB index not found at {persist_directory}")
        print("Please run 'python main.py build-index' first")
        return
    
    # Initialize RAG pipeline
    print("Loading RAG pipeline...")
    embedding_manager = EmbeddingManager(embedding_model)
    vector_store = ChromaVectorStore(persist_directory)
    llm_client = LLMClient(openai_api_key, llm_model)
    rag_pipeline = RAGPipeline(embedding_manager, vector_store, llm_client, top_k)
    
    print("✅ Ready! Ask questions about Bank of Maharashtra loan products.")
    print("Type 'exit' or 'quit' to stop.\n")
    
    # If question provided as argument
    if args.question:
        result = rag_pipeline.query(args.question)
        print(f"\n❓ Question: {result['question']}")
        print(f"\n💡 Answer:\n{result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']}")
        print(f"📚 Sources: {len(result['sources'])} documents")
        return
    
    # Interactive mode
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🔍 Searching...")
            result = rag_pipeline.query(question)
            
            print(f"\n💡 Answer:\n{result['answer']}")
            print(f"\n📊 Confidence: {result['confidence']}")
            print(f"📚 Sources: {len(result['sources'])} documents")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def cmd_demo(args):
    print("\n🎬 Running Demo - Bank of Maharashtra Loan Assistant")
    print("=" * 80)
    
    # Load configuration
    persist_directory = os.getenv('CHROMA_PERSIST_DIR', './data/vector_store/chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_model = os.getenv('LLM_MODEL', 'gpt-4')
    top_k = int(os.getenv('TOP_K_RESULTS', 3))
    
    if not openai_api_key:
        print("❌ Error: OPENAI_API_KEY not found in .env file")
        return
    
    if not os.path.exists(persist_directory):
        print(f"❌ Error: ChromaDB index not found at {persist_directory}")
        print("Please run 'python main.py build-index' first")
        return
    
    # Initialize RAG pipeline
    print("\n📦 Loading RAG pipeline...")
    embedding_manager = EmbeddingManager(embedding_model)
    vector_store = ChromaVectorStore(persist_directory)
    llm_client = LLMClient(openai_api_key, llm_model)
    rag_pipeline = RAGPipeline(embedding_manager, vector_store, llm_client, top_k)
    
    # Test questions (required by assessment)
    test_questions = [
        "What are the interest rates for a Bank of Maharashtra home loan?",
        "What is the maximum tenure for a personal loan if my salary account is with the bank?",
        "Tell me about the Maha Super Flexi Housing Loan Scheme.",
        "Are there any processing fee concessions for women or defence personnel on home loans?"
    ]
    
    print("\n✅ Ready! Testing with 4 demonstration queries...\n")
    
    for i, question in enumerate(test_questions, 1):
        print("=" * 80)
        print(f"\n🔍 Query {i}/{len(test_questions)}")
        print(f"❓ Question: {question}")
        print("-" * 80)
        
        result = rag_pipeline.query(question)
        
        print(f"\n💡 Answer:\n{result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']}")
        print(f"📚 Sources used: {len(result['sources'])} documents")
        
        if i < len(test_questions):
            print("\n" + "=" * 80)
    
    print("\n" + "=" * 80)
    print("\n✅ Demo complete! All 4 test queries executed successfully.")


def main():
    parser = argparse.ArgumentParser(
        description='Bank of Maharashtra Loan Assistant - RAG-based Q&A System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py scrape              # Scrape loan data from website
  python main.py process             # Process and consolidate data
  python main.py build-index         # Build ChromaDB vector index
  python main.py query               # Interactive query mode
  python main.py query "What are home loan rates?"  # Single query
  python main.py demo                # Run demonstration queries
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    parser_scrape = subparsers.add_parser('scrape', help='Scrape loan data from Bank of Maharashtra website')
    parser_scrape.set_defaults(func=cmd_scrape)
    
    # Process command
    parser_process = subparsers.add_parser('process', help='Process and consolidate scraped data')
    parser_process.set_defaults(func=cmd_process)
    
    # Build-index command
    parser_build = subparsers.add_parser('build-index', help='Build ChromaDB vector index')
    parser_build.set_defaults(func=cmd_build_index)
    
    # Query command
    parser_query = subparsers.add_parser('query', help='Query the loan assistant')
    parser_query.add_argument('question', nargs='?', help='Question to ask (optional, interactive if not provided)')
    parser_query.set_defaults(func=cmd_query)
    
    # Demo command
    parser_demo = subparsers.add_parser('demo', help='Run demonstration with test queries')
    parser_demo.set_defaults(func=cmd_demo)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
