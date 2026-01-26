# Log Analyzer App - Flow Diagram (ASCII)

## Application Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LOG ANALYZER STREAMLIT APP                           │
│                         app.py Flow Diagram                             │
└─────────────────────────────────────────────────────────────────────────┘

                              START
                               │
                               ▼
                   ┌──────────────────────┐
                   │  Initialize App      │
                   │ Load Environment     │
                   │ Setup Session State  │
                   └──────────────────────┘
                               │
                               ▼
                   ┌──────────────────────┐
                   │  Display UI          │
                   │  Title & Description │
                   └──────────────────────┘
                               │
                               ▼
                   ┌──────────────────────┐
                   │ Prompt File Upload   │
                   └──────────────────────┘
                               │
                      ┌────────┴────────┐
                      ▼                 ▼
                   File?            No File
                     │                 │
                     │                 ▼
                     │         ┌──────────────────┐
                     │         │ Show Waiting     │
                     │         │ Message          │
                     │         └──────────────────┘
                     │
                     ▼
          ┌────────────────────────┐
          │ Read File Bytes        │
          │ Get File Info          │
          │ (filename, size)       │
          └────────────────────────┘
                     │
                     ▼
          ┌────────────────────────┐
          │ Validate File          │
          │ FileValidator.validate │
          │ (filename, size)       │
          └────────────────────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
         Valid?            Invalid
           │                 │
           │                 ▼
           │        ┌──────────────────┐
           │        │ Display Error    │
           │        │ Message          │
           │        └──────────────────┘
           │                 │
           │                 ▼
           │                STOP
           │
           ▼
    ┌────────────────────────┐
    │ Decode File Bytes      │
    │ Try UTF-8              │
    │ Fallback: Latin-1      │
    └────────────────────────┘
           │
           ▼
    ┌────────────────────────┐
    │ Check Analyzer         │
    │ in Session State       │
    └────────────────────────┘
           │
      ┌────┴────┐
      ▼         ▼
   Exists?    None
     │         │
     │         ▼
     │    ┌─────────────────┐
     │    │ Initialize      │
     │    │ LLMVectorAnalyzer
     │    │ - Pinecone      │
     │    │ - ChatOllama    │
     │    │ - Embeddings    │
     │    └─────────────────┘
     │         │
     └────┬────┘
          │
          ▼
    ┌──────────────────────┐
    │ Store in Session     │
    │ Analyzer Ready       │
    └──────────────────────┘
          │
          ▼
    ┌──────────────────────┐
    │ Check skip_ingest    │
    │ Flag                 │
    └──────────────────────┘
          │
      ┌───┴───┐
      ▼       ▼
   False    True
     │       │
     │       ▼
     │   ┌──────────────┐
     │   │ Skip         │
     │   │ Ingestion    │
     │   └──────────────┘
     │
     ▼
┌──────────────────────────────────────────┐
│ PHASE: LOG INGESTION                    │
├──────────────────────────────────────────┤
│                                          │
│  1. Split text into chunks               │
│     RecursiveCharacterTextSplitter      │
│     chunk_size: 50                       │
│                                          │
│  2. Check & Delete old index             │
│     if index exists:                     │
│       Pinecone.delete_index()            │
│                                          │
│  3. Create new Pinecone index            │
│     ServerlessSpec (AWS, us-east-1)     │
│     dimension: 1024                      │
│                                          │
│  4. Add chunks to vector store           │
│     Batch: 95 chunks per request         │
│     PineconeVectorStore.add_texts()      │
│                                          │
│  5. Set skip_ingest = True               │
│                                          │
└──────────────────────────────────────────┘
          │
          ▼
    ┌──────────────────────┐
    │ Log Ingested         │
    │ Ready for Analysis   │
    └──────────────────────┘
          │
          ▼
    ┌──────────────────────────────────┐
    │ THREE PARALLEL FEATURES AVAILABLE│
    └──────────────────────────────────┘
          │
  ┌───────┼───────┐
  │       │       │
  ▼       ▼       ▼
 ┌─┐    ┌─┐    ┌─┐
 │A│    │B│    │C│
 └─┘    └─┘    └─┘
  │       │       │
  ▼       ▼       ▼

════════════════════════════════════════════════════════════════════════════════

FEATURE A: SUMMARIZATION                 FEATURE B: RAG Q&A                    
────────────────────────────             ─────────────────

Trigger: Click "Summarize"               Trigger: Enter Question

│                                        │
▼                                        ▼
┌──────────────────────────┐             ┌──────────────────────┐
│ Check skip_summary Flag  │             │ Get User Input       │
└──────────────────────────┘             │ (Question/Prompt)    │
      │                                  └──────────────────────┘
      ▼                                        │
┌──────────────────────────┐                  ▼
│ summarize(text)          │             ┌──────────────────────┐
│                          │             │ analyze_log_rag()    │
│ ┌────────────────────┐   │             │                      │
│ │summarize_chunks()  │   │             │ 1. Create Retriever │
│ │                    │   │             │    similarity search │
│ │ Split chunks:      │   │             │    k=10              │
│ │ chunk_size: 1000   │   │             │                      │
│ │ overlap: 10        │   │             │ 2. Create RAG Chain  │
│ │                    │   │             │    Retrieval chain   │
│ │ For each chunk[0:5]│   │             │    Stuff documents   │
│ │  - invoke LLM      │   │             │                      │
│ │  - get summary     │   │             │ 3. Invoke Chain      │
│ │  - append to list  │   │             │    rag_chain.invoke()
│ │                    │   │             │                      │
│ │ Return: list of    │   │             │ 4. Return answer     │
│ │ 5 summaries        │   │             │    response['answer']
│ └────────────────────┘   │             │                      │
│                          │             └──────────────────────┘
│ ┌────────────────────┐   │                  │
│ │Final Summary:      │   │                  ▼
│ │                    │   │             ┌──────────────────────┐
│ │ Combine all        │   │             │ Display Answer       │
│ │ summaries          │   │             │ to User              │
│ │                    │   │             └──────────────────────┘
│ │ Invoke LLM again   │   │
│ │ final_summary =    │   │
│ │ chain.invoke()     │   │
│ │                    │   │
│ │ Return: 1 summary  │   │
│ └────────────────────┘   │
│                          │
│ Set skip_summary = True  │
└──────────────────────────┘
      │
      ▼
┌──────────────────────────┐
│ Display Summary to User  │
└──────────────────────────┘


════════════════════════════════════════════════════════════════════════════════

FEATURE C: USER CONTINUES OR EXITS
──────────────────────────────────

User can:
  1. Ask another question (feature B repeats)
  2. Click Summarize again (skipped due to flag)
  3. Upload new file (reset state)
  4. Close app (end)

════════════════════════════════════════════════════════════════════════════════

END OF APPLICATION
```

---

## Detailed Component Interaction

### File Upload to Ingestion Path

```
User                  Streamlit            FileValidator      LLMVectorAnalyzer
 │                        │                     │                    │
 ├─ Upload file ────────>  │                     │                    │
 │                        │                     │                    │
 │                        ├─ validate() ─────>  │                    │
 │                        │  (filename, size)  │                    │
 │                        │  <─ (ok, msg) ─────┤                    │
 │                        │                     │                    │
 │  ┌─ if not ok ─┐                             │                    │
 │  │             ├─ Show Error                 │                    │
 │  │             │  end                        │                    │
 │  └─ if ok ────┘                              │                    │
 │                        │                     │                    │
 │  ┌─ Decode ───────────────┐                 │                    │
 │  │ bytes to text          │                 │                    │
 │  │ UTF-8 or Latin-1       │                 │                    │
 │  └────────────────────────┘                 │                    │
 │                        │                     │                    │
 │                        ├─ if analyzer None ──────────┐           │
 │                        │                     │        │           │
 │                        │                     │        ├─ init ──>  │
 │                        │                     │        │  Pinecone  │
 │                        │                     │        │  ChatOllama│
 │                        │                     │        │  Embeddings
 │                        │                     │        │<─ ready ──┤
 │                        │  <─ store analyzer ─────────┤           │
 │                        │                     │                    │
 │                        ├─ ingest_log_langchain_llm ────────────>  │
 │                        │                     │        chunk text  │
 │                        │                     │        split text  │
 │                        │                     │        delete index│
 │                        │                     │        create index│
 │                        │                     │        add chunks  │
 │                        │  <─ ingestion done ─────────────────────┤
 │                        │                     │                    │
 │  ◄─ Ready for query ───┤                     │                    │
```

---

### Summarization Path

```
User                  Streamlit            LLMVectorAnalyzer        LangChain
 │                        │                     │                      │
 │  Click Summarize ────>  │                     │                      │
 │                        │                     │                      │
 │                        ├─ summarize(text) ───────────────────────>  │
 │                        │                     │                      │
 │                        │  summarize_chunks() │                      │
 │                        │  ┌────────────────┐ │                      │
 │                        │  │ Split 1000 ch  │ │                      │
 │                        │  │ overlap: 10    │ │                      │
 │                        │  │ Process 5 max  │ │                      │
 │                        │  │ For each:      │ │                      │
 │                        │  │  invoke LLM ───────────────────────────>│
 │                        │  │  get summary   │ │<─ chunk summary ────┤
 │                        │  │ Append list    │ │                      │
 │                        │  └────────────────┘ │                      │
 │                        │                     │                      │
 │                        │  Final Summary:     │                      │
 │                        │  invoke LLM ───────────────────────────────>│
 │                        │  on all summaries   │<─ final summary ─────┤
 │                        │                     │                      │
 │                        │  <─ final_summary ──┤                      │
 │  <─ Display Summary ────┤                     │                      │
```

---

### RAG Analysis Path

```
User                  Streamlit            LLMVectorAnalyzer      Pinecone + LangChain
 │                        │                     │                      │
 │  Enter Question ─────>  │                     │                      │
 │                        │                     │                      │
 │                        ├─ analyze_log_rag() ───────────────────────>│
 │                        │  (prompt)            │                      │
 │                        │                     │                      │
 │                        │  Create Retriever    │                      │
 │                        │  ┌────────────────┐  │                      │
 │                        │  │ similarity      │  ├─ Search (k=10) ────>│
 │                        │  │ search k=10    │  │<─ top 10 chunks ────┤
 │                        │  └────────────────┘  │                      │
 │                        │                     │                      │
 │                        │  Create RAG Chain    │                      │
 │                        │  ┌────────────────┐  │                      │
 │                        │  │stuff_documents │  │                      │
 │                        │  │retrieval_chain │  │                      │
 │                        │  └────────────────┘  │                      │
 │                        │                     │                      │
 │                        │  invoke chain ──────────────────────────────>│
 │                        │  context+prompt     │  invoke LLM  ────────>
 │                        │                     │  <─ answer ──────────┤
 │                        │                     │<─ {answer: text} ────┤
 │                        │                     │                      │
 │  <─ Display Answer ─────┤                     │                      │
```

---

## State Transitions

```
                    ┌─────────────────────┐
                    │ Initial State       │
                    │                     │
                    │ skip_ingest: False  │
                    │ skip_summary: False │
                    │ analyzer: None      │
                    └─────────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ File Uploaded       │
                    │ Validated           │
                    │ Decoded             │
                    └─────────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Analyzer Created    │
                    │ in Session State    │
                    └─────────────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ Ingestion Completed │
                    │ skip_ingest: True   │
                    │ Index Created       │
                    │ Chunks Stored       │
                    └─────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            Click Summarize    Enter Question
                    │                 │
                    ▼                 ▼
            Summary Generated  Answer Generated
                    │                 │
                    ▼                 ▼
        skip_summary: True      Cache in session
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
                ┌─────────────────────────┐
                │ Ready for More Queries  │
                │ (Reuse Analyzer Index)  │
                └─────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
            Upload New File      Close App
                    │                 │
                    ▼                 ▼
            Reset All Flags        END
```

---

## Error Handling Flow

```
Any Operation
      │
      ▼
   ┌─────────────┐
   │ Try Block   │
   └─────────────┘
      │
   ┌──┴──┐
   ▼     ▼
Success Error
   │     │
   │     ▼
   │  ┌──────────────────┐
   │  │ Catch Exception  │
   │  └──────────────────┘
   │     │
   │     ▼
   │  ┌──────────────────┐
   │  │ Print to Console │
   │  │ (Debug Info)     │
   │  └──────────────────┘
   │     │
   │     ▼
   │  ┌──────────────────┐
   │  │ Display to User  │
   │  │ st.error()       │
   │  └──────────────────┘
   │     │
   └─────┴─> Continue or End
```

---

**Generated**: January 26, 2026
**Format**: ASCII Diagram
**Purpose**: Visual representation of app.py flow
