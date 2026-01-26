# Log Analyzer App - UML Sequence Diagram Documentation

## Overview
This document describes the UML Sequence Diagram for the Log Analyzer Streamlit application (`app.py`). The diagram illustrates the interactions between the user, Streamlit UI, validators, analyzers, and external services (Pinecone, LangChain).

## File Location
- **PlantUML Diagram**: `app_sequence_diagram.puml`
- **To view**: Use PlantUML editor, VS Code extension, or online PlantUML viewer (plantuml.com)

## Main Actors/Participants

```
1. User              - The end user interacting with the Streamlit app
2. Streamlit UI      - Web interface and application logic
3. FileValidator     - Validates uploaded log files
4. LLMVectorAnalyzer - Main analysis engine
5. Pinecone          - Vector database for embeddings
6. LangChain         - LLM orchestration and chain creation
7. Session State     - Streamlit session state management
```

## Sequence Flow

### Phase 1: Initialization
```
User → UI: Load App
UI → Session: Initialize session_state (skip_ingest, skip_summary, analyzer)
UI → User: Display title and description
```

**Key Variables Initialized:**
- `skip_ingest` = False (ingestion not done yet)
- `skip_summary` = False (summary not generated yet)
- `analyzer` = None (not yet created)

---

### Phase 2: File Upload & Validation
```
User → UI: Upload .log file
UI → FileValidator: validate(filename, size)
FileValidator → UI: Return (ok, error_message)
```

**Validation Checks:**
1. File extension must be `.log`
2. File size must not exceed 100 MB

**Outcomes:**
- ✅ Valid → Proceed to decoding
- ❌ Invalid → Display error message and stop

**File Decoding:**
```
UI: Decode file bytes to text
   Try: UTF-8 encoding
   Catch: Fall back to Latin-1 encoding
```

---

### Phase 3: Analyzer Initialization
```
if analyzer not in session_state:
    UI → LLMVectorAnalyzer: Create new instance
        LLMVectorAnalyzer → Pinecone: Initialize Pinecone client
        LLMVectorAnalyzer → LangChain: Initialize LLMs and embeddings
    LLMVectorAnalyzer → UI: Return analyzer instance
    Session → Session: Store analyzer in session_state
else:
    Session → UI: Retrieve cached analyzer from session_state
```

**Analyzer Initialization Parameters:**
- `openai_api_key` - From environment variable
- `pinecone_api_key` - From environment variable
- `index_name` - "index-log" (hardcoded)

**Initialized Components:**
- LLM: ChatOllama (model: "gemma2:latest", temperature: 0)
- Embeddings: OllamaEmbeddings (model: "mxbai-embed-large:335m")
- Pinecone Client: For vector database operations

---

### Phase 4: Log Ingestion
```
if not skip_ingest:
    UI → Analyzer: ingest_log_langchain_llm(text)
        
        Analyzer → LangChain: RecursiveCharacterTextSplitter
            chunk_size: 50
            chunk_overlap: 0
            delimiter: "\n"
        LangChain → Analyzer: Return list of chunks
        
        Analyzer → Pinecone: Check if index exists
            if exists:
                Analyzer → Pinecone: Delete existing index
        
        Analyzer → Pinecone: Create new index
            name: index_name
            spec: ServerlessSpec (AWS, us-east-1)
            dimension: 1024
        
        Analyzer → Pinecone: Add chunks to vector store
            batch_size: 95 chunks per batch
        
    UI: Set skip_ingest = True (prevent re-ingestion)
```

**Key Points:**
- ✅ Only runs once per session (skip_ingest flag)
- 🔄 Chunks are batched in groups of 95
- 📦 Uses Pinecone Serverless for cost efficiency
- 🗑️ Deletes and recreates index (fresh state)

---

### Phase 5: Log Summarization
```
if User clicks "Summarize" button:
    if not skip_summary:
        UI → Analyzer: summarize(text)
            
            Analyzer → Analyzer: summarize_chunks(text)
                Analyzer → LangChain: RecursiveCharacterTextSplitter
                    chunk_size: 1000
                    chunk_overlap: 10
                LangChain → Analyzer: Return chunks
                
                for chunk in chunks[:5]:  # Process max 5 chunks
                    Analyzer → LangChain: prompt_template_chunk_summary
                    Analyzer → LangChain: ChatOllama.invoke(chunk)
                    LangChain → Analyzer: chunk_summary
                    Analyzer: Append to chunk_summaries list
                
                Analyzer → Analyzer: Return chunk_summaries (list)
            
            Analyzer → LangChain: prompt_template_summary
            Analyzer → LangChain: ChatOllama.invoke(all_summaries)
            LangChain → Analyzer: final_summary
            
        UI: Set skip_summary = True (prevent re-summarization)
        UI → User: Display final summary
```

**Summarization Pipeline:**
1. **Chunk Summary Phase**
   - Split log into 1000-char chunks (10-char overlap)
   - Generate summary for first 5 chunks only
   - Output: List of chunk summaries

2. **Final Summary Phase**
   - Combine all chunk summaries
   - Generate consolidated summary
   - Output: Single final summary text

**Prompts Used:**
- `prompt_template_chunk_summary` - Summarize individual chunks
- `prompt_template_summary` - Create final summary from chunks

---

### Phase 6: Log Analysis (RAG - Retrieval Augmented Generation)
```
if User enters a question:
    UI → Analyzer: analyze_log_rag(prompt)
        
        Analyzer → Pinecone: Initialize vector store with index
        
        Analyzer → Pinecone: Create retriever
            search_type: "similarity"
            search_kwargs: {k: 10}  # Retrieve top 10 similar chunks
        
        Analyzer → LangChain: create_stuff_documents_chain
            template: prompt_template
        
        Analyzer → LangChain: create_retrieval_chain
            retriever: vector_store_retriever
            qa_chain: stuff_documents_chain
        
        Analyzer → LangChain: rag_chain.invoke({input: prompt})
            LangChain → Pinecone: Similarity search
            Pinecone → LangChain: Return top 10 chunks
            LangChain → LLM: Invoke with context and prompt
            LLM → LangChain: Generate answer
        
        LangChain → Analyzer: Return {answer: response}
        
    UI → User: Display answer
```

**RAG Pipeline Steps:**
1. **Retrieval**: Find most relevant chunks from vector store (top 10)
2. **Context Building**: Create prompt with retrieved chunks as context
3. **Generation**: Use LLM to generate answer based on context + user question

**Prompt Template Used:**
- `prompt_template` - System: Analyzes logs and counts issues
- Emoji logic: 🔥 (count > 5), ⚠️ (count > 3), 🟡 (count ≤ 3), ✅ (no issues)

---

## State Management

### Session State Variables
```python
st.session_state.skip_ingest = False/True
    - Tracks if log has been ingested
    - Prevents re-ingestion on re-runs
    - Reset on new file upload

st.session_state.skip_summary = False/True
    - Tracks if summary has been generated
    - Prevents re-summarization on re-runs
    - Reset on new file upload

st.session_state.analyzer = None/LLMVectorAnalyzer
    - Caches analyzer instance
    - Reuses same analyzer for multiple operations
    - Preserves Pinecone index connection
```

---

## Error Handling

The app implements error handling at multiple levels:

### 1. File Validation Errors
```
if not ok:
    UI → User: Display error message
    Stop execution
```

### 2. File Decoding Errors
```
try:
    text = file_bytes.decode("utf-8")
except:
    text = file_bytes.decode("latin-1")
```

### 3. Ingestion Errors
```
try:
    analyzer.ingest_log_langchain_llm(text)
except Exception as e:
    UI → User: Display error message
    Log error to console
```

### 4. Summarization Errors
```
try:
    analyzer.summarize(text)
except Exception as e:
    UI → User: Display error message
    Log error to console
```

### 5. Analysis (RAG) Errors
```
try:
    analyzer.analyze_log_rag(prompt)
except Exception as e:
    UI → User: Display error message
    Log error to console
```

---

## Key Design Patterns

### 1. **Session State Caching**
- Analyzer instance cached to avoid re-initialization
- Skip flags prevent redundant processing

### 2. **Lazy Initialization**
- Analyzer created only when needed
- API keys loaded from environment

### 3. **Fallback Handling**
- UTF-8 → Latin-1 for file decoding
- Prevents encoding errors

### 4. **Batching**
- Chunks batched in groups of 95 for Pinecone ingestion
- Improves performance and prevents API limits

### 5. **Multi-Stage Processing**
- Ingestion (text → embeddings → vector DB)
- Summarization (chunking → individual summaries → final summary)
- Analysis (question → retrieval → context-aware answer)

---

## Data Flow Summary

```
INPUT: Log file (.log)
    ↓
VALIDATION: Check extension & size
    ↓
DECODING: Convert bytes to text
    ↓
INGESTION: Create embeddings & store in Pinecone
    ↓
┌─────────────────────────────────────┐
│   THREE PARALLEL FEATURES:          │
├─────────────────────────────────────┤
│ 1. SUMMARIZATION                    │
│    Log → Chunks → Summaries →       │
│    Final Summary                    │
│                                     │
│ 2. RAG ANALYSIS (Q&A)              │
│    Question → Retrieval →           │
│    Context-aware Answer             │
│                                     │
│ 3. DISPLAY                          │
│    Results shown to user            │
└─────────────────────────────────────┘
    ↓
OUTPUT: Summaries & Answers displayed
```

---

## Interaction Sequences by User Action

### Scenario 1: First Time Upload
```
1. Load app
2. Upload log file
3. Validate file
4. Decode text
5. Initialize analyzer
6. Ingest log to Pinecone
7. Ready for summarization/analysis
```

### Scenario 2: User Asks Question
```
1. (Analyzer already initialized)
2. (Log already ingested)
3. Enter question
4. Retrieve relevant chunks from Pinecone
5. Generate answer using RAG
6. Display answer
```

### Scenario 3: User Clicks Summarize
```
1. (Analyzer already initialized)
2. (Log already ingested)
3. Click "Summarize" button
4. Generate chunk summaries (max 5)
5. Generate final consolidated summary
6. Display summary
```

---

## Performance Considerations

| Operation | Time | Notes |
|-----------|------|-------|
| File Upload | ~1s | Depends on file size |
| Validation | <1s | Fast check |
| Decoding | ~1s | UTF-8 or Latin-1 |
| Ingestion | ~5-30s | Depends on file size & chunk count |
| Summarization | ~10-60s | LLM inference time |
| Analysis (RAG) | ~5-15s | Vector search + LLM inference |

---

## Security Notes

- API keys loaded from `.env` file (not hardcoded)
- File size limited to 100 MB
- Only `.log` files accepted
- Error messages sanitized before display

---

## Future Enhancements

Potential improvements to the sequence flow:

1. **Async Processing**
   - Process large files asynchronously
   - Non-blocking UI updates

2. **Batch Q&A**
   - Ask multiple questions without re-ingestion

3. **Index Persistence**
   - Reuse existing indexes instead of recreating

4. **Progress Tracking**
   - More detailed progress bars during ingestion

5. **Caching**
   - Cache summaries and answers
   - Avoid redundant LLM calls

---

## Diagram Legend

```
→     Synchronous call (blocking)
-->   Return value
[]    Decision point (alt block)
loop  Repetition
opt   Optional operation
par   Parallel execution
```

---

**Generated**: January 26, 2026
**File**: app_sequence_diagram.puml
**Format**: PlantUML
