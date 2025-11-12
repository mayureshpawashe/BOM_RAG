import os
import json
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmbeddingManager:
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Embedding dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Embedding {len(texts)} texts...")
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()


class ChromaVectorStore:
    
    def __init__(self, persist_directory: str, collection_name: str = "loan_products"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Bank of Maharashtra loan products"}
        )
        
        logger.info(f"Collection '{collection_name}' ready with {self.collection.count()} documents")
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        logger.info(f"Adding {len(chunks)} documents to ChromaDB...")
        
        # Prepare data for ChromaDB
        ids = [chunk['chunk_id'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'loan_type': chunk.get('loan_type', 'General'),
                'chunk_index': chunk.get('chunk_index', 0)
            }
            for chunk in chunks
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully added {len(chunks)} documents")
    
    def search(self, query_embedding: List[float], k: int = 3) -> Dict:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        return {
            'documents': results['documents'][0] if results['documents'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else []
        }
    
    def clear(self):
        logger.warning("Clearing all documents from collection...")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Bank of Maharashtra loan products"}
        )
        logger.info("Collection cleared")


class LLMClient:
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized LLM client with model: {model}")
    
    def generate_answer(self, question: str, context: str, max_tokens: int = 2000) -> str:
        # Build prompt
        prompt = self._build_prompt(question, context)
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable banking assistant for Bank of Maharashtra. "
                                   "Provide detailed, comprehensive answers about loan products based on the context provided. "
                                   "Include specific details like interest rates, tenure, eligibility criteria, features, and benefits when available. "
                                   "Structure your answers clearly with relevant details. "
                                   "If the information is not in the context, say so politely."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more factual responses
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_prompt(self, question: str, context: str) -> str:
        prompt = f"""Based on the following information about Bank of Maharashtra loan products, provide a detailed and comprehensive answer to the question.

Context Information:
{context}

Question: {question}

Instructions:
- Provide a detailed answer with specific information from the context
- Include relevant details such as interest rates, tenure, eligibility, features, and benefits
- Structure the answer clearly with key points
- Be specific and informative
- If multiple loan schemes are relevant, mention them

Answer: """
        return prompt


class RAGPipeline:
    
    def __init__(
        self,
        embedding_manager: EmbeddingManager,
        vector_store: ChromaVectorStore,
        llm_client: LLMClient,
        top_k: int = 3
    ):
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.top_k = top_k
        logger.info("RAG Pipeline initialized")
    
    def query(self, question: str) -> Dict:
        logger.info(f"Processing query: {question}")
        
        # 1. Embed the question
        query_embedding = self.embedding_manager.embed_text(question)
        
        # 2. Search for relevant documents
        search_results = self.vector_store.search(query_embedding, k=self.top_k)
        
        if not search_results['documents']:
            return {
                'question': question,
                'answer': "I couldn't find relevant information to answer your question.",
                'sources': [],
                'confidence': 0.0
            }
        
        # 3. Build context from retrieved documents
        context = self._build_context(search_results)
        
        # 4. Generate answer using LLM
        answer = self.llm_client.generate_answer(question, context)
        
        # 5. Prepare response
        response = {
            'question': question,
            'answer': answer,
            'sources': search_results['documents'],
            'metadata': search_results['metadatas'],
            'distances': search_results['distances'],
            'confidence': self._calculate_confidence(search_results['distances'])
        }
        
        logger.info("Query processed successfully")
        return response
    
    def _build_context(self, search_results: Dict) -> str:
        context_parts = []
        for i, doc in enumerate(search_results['documents'], 1):
            context_parts.append(f"[Source {i}]\n{doc}\n")
        
        return "\n".join(context_parts)
    
    def _calculate_confidence(self, distances: List[float]) -> float:
        if not distances:
            return 0.0
        
        # Lower distance = higher confidence
        # Convert distance to confidence (inverse relationship)
        avg_distance = sum(distances) / len(distances)
        confidence = max(0.0, min(1.0, 1.0 - avg_distance))
        
        return round(confidence, 2)


def build_index(chunks_file: str, persist_directory: str, embedding_model: str = "all-MiniLM-L6-v2"):
    logger.info("Building ChromaDB index...")
    
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} chunks")
    
    # Initialize components
    embedding_manager = EmbeddingManager(embedding_model)
    vector_store = ChromaVectorStore(persist_directory)
    
    # Clear existing data
    vector_store.clear()
    
    # Generate embeddings
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedding_manager.embed_batch(texts)
    
    # Add to vector store
    vector_store.add_documents(chunks, embeddings)
    
    logger.info("Index building complete!")
    return vector_store


def main():
    from dotenv import load_dotenv
    load_dotenv()
    
    # Configuration
    chunks_file = 'data/processed/chunks.json'
    persist_directory = os.getenv('CHROMA_PERSIST_DIR', './data/vector_store/chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_model = os.getenv('LLM_MODEL', 'gpt-4')
    top_k = int(os.getenv('TOP_K_RESULTS', 3))
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        return
    
    # Build index
    print("\n🔨 Building ChromaDB index...")
    vector_store = build_index(chunks_file, persist_directory, embedding_model)
    
    # Initialize RAG pipeline
    print("\n🚀 Initializing RAG pipeline...")
    embedding_manager = EmbeddingManager(embedding_model)
    llm_client = LLMClient(openai_api_key, llm_model)
    rag_pipeline = RAGPipeline(embedding_manager, vector_store, llm_client, top_k)
    
    # Test queries
    test_questions = [
        "What are the interest rates for home loans?",
        "What is the maximum tenure for personal loans?",
        "Tell me about gold loan schemes",
    ]
    
    print("\n" + "="*80)
    print("🤖 Testing RAG Pipeline")
    print("="*80)
    
    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 80)
        
        result = rag_pipeline.query(question)
        
        print(f"💡 Answer: {result['answer']}")
        print(f"📊 Confidence: {result['confidence']}")
        print(f"📚 Sources used: {len(result['sources'])}")
        print("="*80)
    
    print("\n✅ RAG Pipeline test complete!")


if __name__ == '__main__':
    main()
