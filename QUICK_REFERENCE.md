# UML Sequence Diagram - Quick Reference Card

## 🎯 At a Glance

```
┌──────────────────────────────────────────────────────────────┐
│           LOG ANALYZER APP - EXECUTION FLOW                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  START                                                       │
│    ↓                                                         │
│  1️⃣ UPLOAD FILE → 2️⃣ VALIDATE → 3️⃣ DECODE                 │
│    ↓                                                         │
│  4️⃣ INITIALIZE ANALYZER                                     │
│    ↓                                                         │
│  5️⃣ INGEST LOG (Split → Embed → Store in Pinecone)          │
│    ↓                                                         │
│  6️⃣ READY FOR ANALYSIS                                      │
│    ├─ SUMMARIZE (Generate summary)                          │
│    └─ Q&A (Answer questions via RAG)                        │
│    ↓                                                         │
│  END / UPLOAD NEW FILE                                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase Checklist

| # | Phase | Actor | Action | Duration |
|---|-------|-------|--------|----------|
| 1 | Initialization | UI | Load config & session state | <1s |
| 2 | Upload | User | Select .log file | User-dependent |
| 3 | Validation | Validator | Check extension & size | <1s |
| 4 | Decoding | UI | Convert bytes to text | ~1s |
| 5 | Analyzer Init | LLMAnalyzer | Create instance & connect | ~2s |
| 6 | Ingestion | Analyzer | Split, embed, store chunks | 5-30s |
| 7a | Summarization | Analyzer | Generate summaries | 10-60s |
| 7b | Q&A | Analyzer | Retrieve & answer | 5-15s |

---

## 🔄 Key Interactions

### Interaction 1: File Validation
```
User ──(upload file)──> UI ──(validate)──> FileValidator
                                               ↓
                          (valid?) ──(yes)──> Continue
                          (valid?) ──(no)──> Show Error → STOP
```

### Interaction 2: Analyzer Initialization
```
UI ──(check session)──> Session
                          ↓
                   (exists?) ──(yes)──> Use cached analyzer
                   (exists?) ──(no)──> Create new
                                          ├─ Init Pinecone
                                          ├─ Init LLM
                                          └─ Init Embeddings
```

### Interaction 3: Log Ingestion
```
UI ──(ingest text)──> Analyzer ──> LangChain
                         ├─ Split chunks
                         └──> Pinecone
                              ├─ Delete old index
                              ├─ Create new index
                              └─ Add chunks
                              
Status: skip_ingest = True (prevent re-run)
```

### Interaction 4: Summarization
```
UI ──(summarize)──> Analyzer ──> LangChain
                      ├─ Chunk summaries (loop 5x)
                      ├─ LLM invoke per chunk
                      └─ Final summary generation
                      
Status: skip_summary = True (prevent re-run)
```

### Interaction 5: RAG Analysis
```
UI ──(question)──> Analyzer ──> Pinecone
                      ├─ Vector search (top 10)
                      └──> LangChain
                           ├─ Create retriever
                           ├─ Build context
                           └─ LLM generation
```

---

## 🎨 Component Roles

### **User** 👤
- Uploads .log file
- Clicks "Summarize" button
- Enters questions
- Views results

### **Streamlit UI** 🖥️
- Displays interface
- Manages widgets
- Handles file upload
- Shows results
- Manages session state

### **FileValidator** ✅
- Validates file extension (.log)
- Checks file size (≤ 100 MB)
- Returns validation result

### **LLMVectorAnalyzer** 🤖
- Orchestrates entire analysis
- Manages Pinecone connection
- Handles text splitting
- Coordinates LLM calls
- Three main methods:
  - `ingest_log_langchain_llm()` - Store embeddings
  - `summarize()` - Generate summaries
  - `analyze_log_rag()` - Answer questions

### **Pinecone** 📦
- Vector database
- Stores embeddings
- Similarity search
- Index management

### **LangChain** ⛓️
- LLM orchestration
- Text splitting
- Chain creation
- Prompt management
- Ollama models:
  - ChatOllama (gemma2:latest)
  - OllamaEmbeddings (mxbai-embed-large:335m)

### **Session State** 💾
- Caches analyzer instance
- Tracks skip_ingest flag
- Tracks skip_summary flag
- Preserves state across reruns

---

## 🔀 Control Flow Decisions

### Decision Point 1: File Validation
```
Is file valid?
├─ YES → Continue to decoding
└─ NO → Show error, STOP
```

### Decision Point 2: Analyzer in Session
```
Does analyzer exist in session?
├─ YES → Use cached instance
└─ NO → Create new instance
```

### Decision Point 3: Skip Ingestion?
```
Has ingestion been done?
├─ YES (skip_ingest=True) → Skip ingestion
└─ NO (skip_ingest=False) → Run ingestion, set flag
```

### Decision Point 4: Skip Summarization?
```
Has summary been generated?
├─ YES (skip_summary=True) → Skip summarization
└─ NO (skip_summary=False) → Run summary, set flag
```

---

## 📊 Data Structures

### File Upload
```python
{
    filename: str,
    size: int (bytes),
    content: bytes
}
```

### Validation Result
```python
(ok: bool, message: str | None)
```

### Analyzer
```python
LLMVectorAnalyzer(
    openai_api_key: str,
    pinecone_api_key: str,
    index_name: str
)
```

### Chunks
```python
[chunk1: str, chunk2: str, ...]
(max 95 per batch for ingestion)
```

### Summaries
```python
[summary1: str, summary2: str, ...]
(max 5 chunks for summarization)
```

### RAG Response
```python
{
    answer: str,
    source_documents: [doc1, doc2, ...]
}
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
```

### Application Constants
```
index_name = "index-log"
max_file_size = 100 MB
chunk_size_ingest = 50 chars
chunk_size_summary = 1000 chars
max_chunks_summary = 5
rag_k = 10  # top-k retrieval
```

### LLM Configuration
```
LLM: ChatOllama
  model: "gemma2:latest"
  temperature: 0

Embeddings: OllamaEmbeddings
  model: "mxbai-embed-large:335m"
```

### Pinecone Index
```
Spec: ServerlessSpec
  cloud: "aws"
  region: "us-east-1"
dimension: 1024
```

---

## 🛡️ Error Handling

```
Try Block 1: File Validation
  └─ Catch: Show error message

Try Block 2: File Decoding
  └─ Except UTF-8: Try Latin-1

Try Block 3: Log Ingestion
  └─ Catch Exception: Log + Show error

Try Block 4: Summarization
  └─ Catch Exception: Log + Show error

Try Block 5: RAG Analysis
  └─ Catch Exception: Log + Show error
```

---

## 📈 Sequence Timing

```
Timeline (with typical durations):

T+0s     Load app, initialize session state
T+0.5s   Display UI
T+1s     User uploads file (~varies)
T+2s     Validation & decoding complete
T+4s     Analyzer initialized (if new)
T+34s    Ingestion complete (if large file)
T+35s    Ready for summarization/Q&A
T+95s    Summarization complete (if clicked)
T+110s   Or Q&A responses ready
```

---

## 🔗 Method Call Chain

### Ingestion Chain
```
UI.ingest_log_langchain_llm(text)
  ├─ RecursiveCharacterTextSplitter.split_text()
  ├─ Pinecone.has_index()
  ├─ Pinecone.delete_index()
  ├─ Pinecone.create_index()
  └─ PineconeVectorStore.add_texts()
```

### Summarization Chain
```
UI.summarize(text)
  ├─ Analyzer.summarize_chunks(text)
  │   ├─ RecursiveCharacterTextSplitter.split_text()
  │   └─ for each chunk[0:5]:
  │       └─ prompt_template_chunk_summary | llm | parser
  └─ prompt_template_summary | llm | parser
```

### RAG Analysis Chain
```
UI.analyze_log_rag(prompt)
  ├─ Pinecone.Index()
  ├─ PineconeVectorStore.as_retriever()
  ├─ create_stuff_documents_chain()
  ├─ create_retrieval_chain()
  └─ rag_chain.invoke()
      ├─ retriever.get_relevant_documents()
      └─ llm.invoke(context + prompt)
```

---

## 🎓 Learning Path

**Beginner**: Start with ASCII diagrams
→ Quick understanding of overall flow

**Intermediate**: Read SEQUENCE_DIAGRAM_DOCS.md
→ Understand each phase in detail

**Advanced**: Study the PlantUML diagram
→ Formal UML notation and interactions

**Expert**: Read app.py code + diagrams
→ Full implementation details

---

## 📱 Mobile/UX Considerations

```
Phase 1: Upload (~1 second)
  └─ Simple file picker

Phase 2: Processing (5-30 seconds)
  └─ Show spinner + "Ingesting log"

Phase 3: Results (interactive)
  ├─ Summary button
  └─ Question input field

Phase 4: Streaming Results
  └─ Display results in container
```

---

## 🔐 Security Flow

```
1. Load env vars (not hardcoded keys)
2. Validate file (extension + size)
3. Decode safely (UTF-8 → Latin-1)
4. Process in sandbox (LangChain isolation)
5. Store securely (Pinecone encryption)
6. Return sanitized results
```

---

## 📚 File Reference Guide

| File | Purpose | Read Time |
|------|---------|-----------|
| `app_sequence_diagram.puml` | Formal UML diagram | 10 min |
| `SEQUENCE_DIAGRAM_DOCS.md` | Detailed explanation | 20 min |
| `FLOW_DIAGRAM_ASCII.md` | Visual ASCII flows | 10 min |
| `UML_DIAGRAMS_README.md` | Complete overview | 10 min |
| **This file** | **Quick reference** | **5 min** |

---

## 🎯 Quick Answers

**Q: How long does ingestion take?**
A: 5-30 seconds depending on file size

**Q: Can I ask multiple questions?**
A: Yes! Once ingested, ask unlimited questions

**Q: What formats are supported?**
A: Only .log files (max 100 MB)

**Q: Is data stored permanently?**
A: Only in Pinecone index (session-specific)

**Q: Can I re-summarize?**
A: No (skip_summary flag prevents it)

**Q: How many chunks are processed for summary?**
A: Maximum 5 chunks

**Q: What's the RAG retrieval size?**
A: Top 10 most similar chunks

---

**Quick Reference Card v1.0**
**Generated**: January 26, 2026
**Format**: Markdown
**Status**: ✅ Complete
