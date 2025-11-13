# Bank of Maharashtra Loan Product Assistant

**Technical Assessment Project for EncureIT Systems Pvt Ltd**  
**Role:** Generative AI Developer  
**Candidate:** Mayuresh  
**Submission Date:** November 2025

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Detailed Setup Instructions](#detailed-setup-instructions)
- [Usage Guide](#usage-guide)
- [Project Architecture](#project-architecture)
- [Architectural Decisions](#architectural-decisions)
- [AI Tools Used](#ai-tools-used)
- [Challenges & Solutions](#challenges--solutions)
- [Potential Improvements](#potential-improvements)
- [Testing & Results](#testing--results)
- [Project Statistics](#project-statistics)

---

## 🎯 Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** based question-answering system that provides accurate, contextual information about Bank of Maharashtra's loan products. The system can answer complex queries about:

- 🏠 **Home Loans** (7 schemes including Green Housing, Flexi Loans, Top-Up)
- 🚗 **Vehicle Loans** (8 schemes including Electric Cars, Farmer Vehicles)
- 💼 **Personal Loans** (7 schemes for Salaried, Professionals, Business Class)
- 🎓 **Education Loans** (3 schemes including Model, Skill Development)
- 💰 **Gold Loans** (3 schemes for Retail, Agriculture, MSME)
- 🌞 **Solar/Green Loans** (Rooftop Solar, Pumpsets)
- 👨‍⚕️ **Professional Loans** (Doctors, CA/CS/CMA)
- 🏭 **MSME Loans** (9 schemes including GST Credit, Mudra, Stand-Up India)
- 🌾 **Agriculture Loans** (8 schemes including KCC, Land Purchase)
- 🦠 **COVID-19 Support Loans** (2 schemes for affected sectors)

**Total Coverage:** 53 loan product pages, 778 knowledge chunks, 100% scraping success rate

## ✨ Key Features

### 🕷️ **Intelligent Web Scraping**
- Automated data collection from 53 loan product pages
- 100% success rate with retry logic and error handling
- Rate limiting to respect server resources
- Sitemap-based URL discovery for comprehensive coverage

### 🔄 **Advanced Data Processing**
- HTML cleaning and noise removal
- Intelligent text chunking (500 chars with 50 char overlap)
- Metadata preservation (loan types, source URLs)
- Consolidated knowledge base (~10,000+ lines)

### 🤖 **Production-Ready RAG Pipeline**
- **Vector Database:** ChromaDB with 778 embeddings
- **Embedding Model:** Sentence Transformers (all-MiniLM-L6-v2, 384D)
- **LLM:** OpenAI GPT-4 for accurate answer generation
- **Retrieval:** TOP_K=10 for comprehensive context
- **Response:** Up to 2000 tokens for detailed answers

### 💻 **Dual Interface**
- **CLI Application:** Full-featured command-line interface
- **Web UI:** Clean Streamlit interface with source citations

### 📊 **Transparency & Traceability**
- Source citations for every answer
- Confidence scoring
- Expandable source documents
- Query history tracking

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd asessment_EncureIT
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the system (data already included!)
streamlit run app.py
```

**Note:** Pre-processed data is included, so you can start querying immediately!

---

## 📦 Detailed Setup Instructions

### Prerequisites

- **Python:** 3.8 or higher
- **OpenAI API Key:** Required for GPT-4 access
- **Internet Connection:** For initial package installation
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** ~500MB for dependencies and data

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd asessment_EncureIT
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- `requests` + `beautifulsoup4` + `lxml` - Web scraping
- `langchain` + `langchain-text-splitters` - Text processing
- `sentence-transformers` - Embeddings
- `chromadb` - Vector database
- `openai` - GPT-4 API
- `streamlit` - Web interface
- `python-dotenv` - Environment management

#### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K_RESULTS=10
```

#### 5. Verify Installation
```bash
python main.py --help
```

You should see the CLI help menu.

## 📖 Usage Guide

### Option 1: Web Interface (Recommended)

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
- Clean chat interface
- Real-time query processing
- Source citations with expandable view
- Query history
- Mobile-responsive design

### Option 2: Command Line Interface

#### Query the System
```bash
python main.py query "What are the interest rates for home loans?"
```

#### Run Demo Queries
```bash
python main.py demo
```

This will run 4 pre-configured queries demonstrating the system's capabilities.

### Advanced Usage: Rebuild from Scratch

If you want to re-scrape and rebuild the entire knowledge base:

#### Step 1: Scrape Loan Data
```bash
python main.py scrape
```
- Scrapes 53 loan product pages
- Saves to `data/raw/scraped_data.json`
- Takes ~3-5 minutes with rate limiting

#### Step 2: Process and Consolidate Data
```bash
python main.py process
```
- Cleans HTML and removes noise
- Creates 778 text chunks
- Generates `data/processed/knowledge_base.txt`
- Generates `data/processed/chunks.json`

#### Step 3: Build Vector Index
```bash
python main.py build-index
```
- Creates embeddings for all 778 chunks
- Builds ChromaDB vector database
- Saves to `data/vector_store/chroma_db/`
- Takes ~15-20 seconds

#### Step 4: Query
```bash
python main.py query "Your question here"
```

### Sample Queries

Try these queries to test the system:

```bash
# Interest rates
python main.py query "What are the interest rates for home loans?"

# Loan schemes
python main.py query "Tell me about the Maha Super Flexi Housing Loan Scheme"

# Eligibility
python main.py query "What is the maximum tenure for personal loans?"

# Concessions
python main.py query "Are there processing fee concessions for women?"

# Green loans
python main.py query "Tell me about solar and green loans"

# Professional loans
python main.py query "What loans are available for doctors?"
```

## 📁 Project Structure

```
asessment_EncureIT/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── scraper.py               # Web scraping (53 URLs, 100% success)
│   ├── data_processor.py        # Data cleaning & chunking (778 chunks)
│   └── rag_pipeline.py          # RAG implementation (ChromaDB + GPT-4)
│
├── data/
│   ├── raw/
│   │   └── scraped_data.json    # Raw scraped data (53 pages)
│   ├── processed/
│   │   ├── knowledge_base.txt   # Consolidated text (~10K lines)
│   │   └── chunks.json          # Text chunks (778 chunks)
│   └── vector_store/
│       └── chroma_db/           # ChromaDB vector database (778 embeddings)
│
├── main.py                      # CLI application (5 commands)
├── app.py                       # Streamlit web interface
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Configuration (not in git)
├── .gitignore                   # Git ignore rules
├── README.md                    # This file
├── FINAL_SUMMARY.md            # Project completion summary
├── ACTUAL_LOAN_URLS.md         # URL discovery documentation
└── SCRAPING_SUMMARY.md         # Scraping process documentation
```

### Key Files Explained

**Source Code:**
- `src/scraper.py` - Handles web scraping with retry logic, rate limiting, and error handling
- `src/data_processor.py` - Cleans HTML, consolidates data, creates chunks
- `src/rag_pipeline.py` - Implements embedding, vector search, and LLM integration

**Applications:**
- `main.py` - CLI with 5 commands: scrape, process, build-index, query, demo
- `app.py` - Streamlit web UI with chat interface and source citations

**Data Files:**
- `data/raw/scraped_data.json` - Raw HTML and text from 53 pages
- `data/processed/knowledge_base.txt` - Clean, consolidated loan information
- `data/processed/chunks.json` - 778 chunks with metadata
- `data/vector_store/chroma_db/` - Persistent vector database

## 🏗️ Project Architecture

### System Flow Diagram

```
User Query
    ↓
[Streamlit UI / CLI]
    ↓
[RAG Pipeline]
    ↓
1. Query Embedding (Sentence Transformers)
    ↓
2. Vector Search (ChromaDB) → Retrieve TOP 10 chunks
    ↓
3. Context Building (Combine chunks)
    ↓
4. LLM Generation (GPT-4) → Generate answer
    ↓
5. Response with Sources
    ↓
User receives detailed answer + source citations
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│  ┌──────────────┐              ┌──────────────┐        │
│  │ Streamlit UI │              │  CLI (main.py)│        │
│  └──────────────┘              └──────────────┘        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   RAG Pipeline                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │  EmbeddingManager (Sentence Transformers)        │  │
│  │  - Model: all-MiniLM-L6-v2                       │  │
│  │  - Dimension: 384                                │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ChromaVectorStore                               │  │
│  │  - 778 embeddings                                │  │
│  │  - Persistent storage                            │  │
│  │  - Cosine similarity search                      │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  LLMClient (OpenAI GPT-4)                        │  │
│  │  - Max tokens: 2000                              │  │
│  │  - Temperature: 0.3                              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Knowledge Base                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  53 Loan Product Pages                           │  │
│  │  778 Text Chunks (500 chars, 50 overlap)         │  │
│  │  ~10,000+ lines of loan information              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 System Data Flow

### **STEP 1: WEB SCRAPING**
```
Bank of Maharashtra Website (53 pages)
    ↓
[scraper.py]
    ↓
data/raw/scraped_data.json (Raw HTML + Text)
```

### **STEP 2: DATA PROCESSING**
```
data/raw/scraped_data.json
    ↓
[data_processor.py - Clean & Consolidate]
    ↓
data/processed/knowledge_base.txt (Clean Text)
    ↓
[data_processor.py - Chunk]
    ↓
data/processed/chunks.json (778 chunks)
```

### **STEP 3: VECTOR INDEXING**
```
data/processed/chunks.json
    ↓
[rag_pipeline.py - Create Embeddings]
    ↓
data/vector_store/chroma_db/ (778 embeddings)
```

### **STEP 4: QUERY PROCESSING**
```
User Question
    ↓
[Convert to Embedding]
    ↓
[Search ChromaDB → TOP 10 chunks]
    ↓
[Send to GPT-4]
    ↓
Answer with Sources
```

---

## 📊 Complete Pipeline Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE                             │
└─────────────────────────────────────────────────────────────────┘

COLLECTION → PROCESSING → INDEXING → RETRIEVAL → GENERATION
    ↓            ↓           ↓           ↓            ↓
  Scraper    Processor   Embeddings   Search       GPT-4
  53 pages   778 chunks   ChromaDB    TOP 10      Answer
```

---


---

## 🎨 Architectural Decisions

### 1. Library Selection & Rationale

#### **Web Scraping**
**Choice:** `requests` + `BeautifulSoup4` + `lxml`

**Why:**
- ✅ **Simplicity:** Bank of Maharashtra uses server-side rendered HTML (no JavaScript rendering needed)
- ✅ **Reliability:** Mature, well-tested libraries with excellent documentation
- ✅ **Performance:** lxml parser is fast and memory-efficient
- ✅ **Flexibility:** Easy to handle inconsistent HTML structures across pages

**Implementation Highlights:**
- Retry logic with exponential backoff (3 attempts)
- Rate limiting (1.5s delay) to respect server resources
- Comprehensive error handling and logging
- Sitemap-based URL discovery for 100% coverage

#### **Data Processing**
**Choice:** `LangChain` + `langchain-text-splitters`

**Why:**
- ✅ **Semantic Chunking:** RecursiveCharacterTextSplitter preserves context better than naive splitting
- ✅ **Flexibility:** Easy to adjust chunk size and overlap
- ✅ **Industry Standard:** Widely used in production RAG systems
- ✅ **Metadata Support:** Preserves source URLs and loan types

**Alternative Considered:** Manual splitting with regex - Rejected due to poor context preservation

#### **Vector Database**
**Choice:** `ChromaDB` (instead of FAISS as suggested)

**Why:**
- ✅ **Persistence:** Saves embeddings to disk (no need to rebuild on restart)
- ✅ **Simplicity:** Easy setup with minimal configuration
- ✅ **Metadata Support:** Stores chunk metadata alongside vectors
- ✅ **Production Ready:** Can scale to millions of documents
- ✅ **Local First:** No external dependencies or cloud services

**Why Not FAISS:**
- ❌ In-memory only (loses data on restart)
- ❌ Requires manual metadata management
- ❌ More complex serialization/deserialization

#### **Embedding Model**
**Choice:** `sentence-transformers/all-MiniLM-L6-v2`

**Why:**
- ✅ **Lightweight:** Only 80MB, fast inference
- ✅ **Quality:** Good semantic understanding for domain-specific text
- ✅ **Dimension:** 384D vectors - optimal balance of quality vs speed
- ✅ **Free:** No API costs, runs locally
- ✅ **Proven:** Widely used in production RAG systems

**Alternatives Considered:**
- OpenAI embeddings (ada-002) - Rejected due to API costs
- Larger models (768D) - Rejected due to slower inference

#### **Large Language Model**
**Choice:** `OpenAI GPT-4`

**Why:**
- ✅ **Accuracy:** Best-in-class for complex reasoning
- ✅ **Instruction Following:** Excellent at following detailed prompts
- ✅ **Domain Knowledge:** Strong understanding of financial/banking terminology
- ✅ **Reliability:** Consistent, high-quality responses
- ✅ **Context Window:** 8K tokens - handles 10 chunks easily

**Configuration:**
- Temperature: 0.3 (lower = more factual, less creative)
- Max tokens: 2000 (allows detailed, comprehensive answers)

**Alternatives Considered:**
- GPT-3.5-turbo - Rejected due to lower accuracy
- Local LLMs (Llama, Mistral) - Rejected due to hardware requirements

#### **Web Framework**
**Choice:** `Streamlit`

**Why:**
- ✅ **Rapid Development:** Build UI in minutes, not hours
- ✅ **Python Native:** No JavaScript required
- ✅ **Chat Interface:** Built-in chat components
- ✅ **Deployment Ready:** Easy to deploy on Streamlit Cloud
- ✅ **Professional Look:** Clean, modern UI out of the box

---

### 2. Data Strategy & Chunking Approach

#### **Chunking Parameters**
```python
CHUNK_SIZE = 500 characters
CHUNK_OVERLAP = 50 characters
```

#### **Why These Values?**

**Chunk Size: 500 characters**
- ✅ **Context Preservation:** Large enough to contain complete information (e.g., interest rate + eligibility)
- ✅ **Retrieval Precision:** Small enough for focused, relevant results
- ✅ **LLM Efficiency:** 10 chunks × 500 chars = ~5000 chars fits comfortably in GPT-4's context
- ✅ **Tested Optimal:** Experimented with 300, 500, 1000 - 500 gave best results

**Chunk Overlap: 50 characters**
- ✅ **No Information Loss:** Prevents splitting sentences/concepts at boundaries
- ✅ **Context Continuity:** Ensures smooth transitions between chunks
- ✅ **Redundancy Balance:** 10% overlap is optimal (not too much, not too little)

#### **Chunking Strategy**

**Method:** LangChain's `RecursiveCharacterTextSplitter`

**Why Recursive?**
1. Tries to split on paragraphs first (`\n\n`)
2. Falls back to sentences (`.`)
3. Falls back to words (` `)
4. Last resort: character-level split

This preserves semantic meaning better than naive character splitting.

#### **Example:**
```
Original Text (1200 chars):
"Home Loan Interest Rate: 7.35% P.A. Eligibility: Salaried employees..."

Chunked:
Chunk 1 (500 chars): "Home Loan Interest Rate: 7.35%... [complete info]"
Chunk 2 (500 chars): "...7.35% P.A. Eligibility: Salaried... [overlap + new info]"
```

---

### 3. Retrieval Strategy

#### **TOP_K = 10 chunks**

**Why 10?**
- ✅ **Comprehensive Coverage:** Captures multiple aspects of a loan (rates, eligibility, tenure, fees)
- ✅ **Cross-Scheme Information:** Can compare multiple loan schemes
- ✅ **Redundancy Handling:** Multiple chunks about same topic increase confidence
- ✅ **GPT-4 Context:** 10 × 500 chars = 5000 chars fits well in 8K context window

**Tested Values:**
- K=3: Too narrow, missed details
- K=5: Better, but still incomplete
- K=10: **Optimal** - comprehensive without noise
- K=20: Too much irrelevant information

#### **Similarity Search**

**Method:** Cosine similarity on 384D vectors

**Process:**
1. User query → Embedding (384D vector)
2. Compare with 778 stored embeddings
3. Return TOP 10 most similar chunks
4. Chunks sorted by similarity score

---

### 4. Prompt Engineering

#### **System Prompt**
```
You are a knowledgeable banking assistant for Bank of Maharashtra.
Provide detailed, comprehensive answers about loan products based on context.
Include specific details like interest rates, tenure, eligibility, features, benefits.
Structure answers clearly with relevant details.
If information is not in context, say so politely.
```

**Why This Prompt:**
- ✅ Sets clear role and expectations
- ✅ Emphasizes detail and comprehensiveness
- ✅ Requests structured responses
- ✅ Handles missing information gracefully

#### **User Prompt Template**
```
Based on the following information about Bank of Maharashtra loan products,
provide a detailed and comprehensive answer to the question.

Context Information:
[10 retrieved chunks]

Question: [User's question]

Instructions:
- Provide detailed answer with specific information
- Include rates, tenure, eligibility, features, benefits
- Structure answer clearly with key points
- Be specific and informative
- If multiple schemes relevant, mention them

Answer:
```

**Why This Structure:**
- ✅ Clear context separation
- ✅ Explicit instructions for detail
- ✅ Guides LLM to comprehensive responses
- ✅ Encourages structured output

## Tools Used

During development, the following AI tools were leveraged:

1. **Vs Code**: For project planning, code generation, and architecture design
2. **GitHub Copilot (Claude Sonnet 4.5)**: For code completion and boilerplate generation
3. **OpenAI GPT-4**: Deep Learning LLM Model
4. **Streamlit**: For UI design and development
5. **LangChain**: For data processing and embedding generation
6. **ChromaDB**: For vector storage and retrieval
7. **BeautifulSoup4**: For web scraping and HTML parsing


## Challenges Faced

### 1. Website Structure Complexity
**Challenge:** Bank of Maharashtra's website has dynamic content and inconsistent HTML structure across different loan pages.

**Solution:** Implemented flexible parsing logic with fallback mechanisms. Used multiple CSS selectors and regex patterns to handle variations.

### 2. Data Quality
**Challenge:** Scraped data contained noise (navigation elements, ads, footers).

**Solution:** Created a comprehensive cleaning pipeline with multiple filters to remove irrelevant content while preserving important information.

### 3. Chunking Strategy
**Challenge:** Finding the right balance between chunk size and context preservation.

**Solution:** Experimented with different chunk sizes and settled on 500 tokens with 50-token overlap based on retrieval quality tests.

## Potential Improvements

Given more time, the following enhancements would be valuable:

### Short-term Improvements
1. **Caching**: Implement query caching to reduce API costs and improve response time
2. **Better Error Handling**: More granular error messages and recovery mechanisms
3. **Logging**: Structured logging with different levels for debugging
4. **Async Scraping**: Use `aiohttp` for concurrent scraping to speed up data collection

### Long-term Improvements
1. **Production Vector Database**: Migrate from FAISS to Pinecone or Weaviate for scalability
2. **Web Interface**: Build a FastAPI backend with React frontend
3. **Multi-language Support**: Add support for regional languages
4. **Incremental Updates**: Implement scheduled re-scraping to keep data fresh
5. **Advanced RAG**: Implement hybrid search (keyword + semantic) for better retrieval
6. **Fine-tuning**: Fine-tune embedding model on banking domain data
7. **Monitoring**: Add metrics collection and performance monitoring

## Testing

The system has been tested with the following demonstration queries:

1. "What are the interest rates for a Bank of Maharashtra home loan?"
2. "What is the maximum tenure for a personal loan if my salary account is with the bank?"
3. "Tell me about the Maha Super Flexi Housing Loan Scheme."
4. "Are there any processing fee concessions for women or defence personnel on home loans?"

All queries return accurate, contextual answers based on the scraped data.



---

**Note:** This is a proof-of-concept project. Always verify loan information directly with Bank of Maharashtra before making financial decisions.
