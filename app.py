import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_pipeline import (
    EmbeddingManager,
    ChromaVectorStore,
    LLMClient,
    RAGPipeline
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Bank of Maharashtra Loan Assistant",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag_pipeline():
    persist_directory = os.getenv('CHROMA_PERSIST_DIR', './data/vector_store/chroma_db')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm_model = os.getenv('LLM_MODEL', 'gpt-4')
    top_k = int(os.getenv('TOP_K_RESULTS', 3))
    
    if not openai_api_key:
        st.error("❌ OPENAI_API_KEY not found in .env file")
        st.stop()
    
    if not os.path.exists(persist_directory):
        st.error(f"❌ ChromaDB index not found at {persist_directory}")
        st.info("Please run: `python main.py build-index` first")
        st.stop()
    
    # Initialize components
    embedding_manager = EmbeddingManager(embedding_model)
    vector_store = ChromaVectorStore(persist_directory)
    llm_client = LLMClient(openai_api_key, llm_model)
    rag_pipeline = RAGPipeline(embedding_manager, vector_store, llm_client, top_k)
    
    return rag_pipeline


def main():
    
    # Header
    st.markdown('<div class="main-header">🏦 Bank of Maharashtra Loan Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about loan products and get instant answers</div>', unsafe_allow_html=True)
    
    # Initialize RAG pipeline
    with st.spinner("Loading..."):
        rag_pipeline = initialize_rag_pipeline()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.caption(f"**Source {i}:**")
                        st.caption(source[:200] + "..." if len(source) > 200 else source)
                        if i < len(message["sources"]):
                            st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask about loans, interest rates, eligibility..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = rag_pipeline.query(prompt)
                    response = result['answer']
                    sources = result.get('sources', [])
                    
                    st.markdown(response)
                    
                    # Display sources
                    if sources:
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(sources, 1):
                                st.caption(f"**Source {i}:**")
                                st.caption(source[:200] + "..." if len(source) > 200 else source)
                                if i < len(sources):
                                    st.divider()
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "sources": sources
                    })
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.divider()
    st.caption("⚠️ Please verify information with Bank of Maharashtra before making decisions.")


if __name__ == '__main__':
    main()
