from typing import Optional, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_ollama import ChatOllama, OllamaEmbeddings

from utils.prompts import prompt_template_summary, prompt_template, prompt_template_chunk_summary


class LLMVectorAnalyzer:

    def __init__(self, openai_api_key: Optional[str] = None, pinecone_api_key: Optional[str] = None, index_name: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        # self.llm = ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key)
        self.llm = ChatOllama(model="gemma2:latest", temperature=0)
        # self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large:335m")
        self.vector_store = None
        self.pc = Pinecone(api_key=self.pinecone_api_key)


    def ingest_log_langchain_llm(self, text: str) -> None:

        print("ingestion started......")

        text_splitter = RecursiveCharacterTextSplitter(["\n"], chunk_size=50, chunk_overlap=0)
        chunks = text_splitter.split_text(text)

        if self.pc.has_index(self.index_name):
            self.pc.delete_index(self.index_name)

        self.pc.create_index(
            name=self.index_name,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            dimension=1024
        )

        print(f"chunks to ingest {len(chunks)}")
        self.vector_store = PineconeVectorStore(index_name=self.index_name, embedding=self.embeddings)
        [self.vector_store.add_texts(chunks[i:i + 95]) for i in range(0, len(chunks), 95)]

        print("ingestion completed using langchain llm......")


    def ingest_log_pinecone(self, text: str) -> None:

        print("ingestion started......")

        text_splitter = RecursiveCharacterTextSplitter(["\n"], chunk_size=50, chunk_overlap=0)
        chunks = text_splitter.split_text(text)

        # Convert chunks to list of dictionaries
        chunks_dict = [{"chunk_text": chunk, "_id": f"rec{i}"} for i, chunk in enumerate(chunks)]

        if self.pc.has_index(self.index_name):
            self.pc.delete_index(self.index_name)

        self.pc.create_index_for_model(
            name=self.index_name,
            cloud="aws",
            region="us-east-1",
            embed={
                "model": "llama-text-embed-v2",
                "field_map": {"text": "chunk_text"}
            }
        )

        index = self.pc.Index(self.index_name)

        print(f"chunks to ingest {len(chunks_dict)}")
        [index.upsert_records("log", chunks_dict[i:i + 95]) for i in range(0, 95, 95)]
        # index.upsert_records("log", chunks_dict[:50])
        print("ingestion completed using native pinecone......")


    def analyze_log_rag(self, prompt: str) -> str:
        response = []

        print("analyzing log started......")

        # retrieval
        index = self.pc.Index(self.index_name)
        self.vector_store = PineconeVectorStore(index=index, embedding=self.embeddings)
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

        print("retrieval completed......")

        # generation
        qa_chain = create_stuff_documents_chain(self.llm, prompt_template)
        # augmentation (query + context)
        rag_chain = create_retrieval_chain(retriever, qa_chain)

        print("rag defined......")

        if prompt:
            response = rag_chain.invoke({"input": prompt})
            print(response)

        print("analyzing log completed......")
        return response['answer']

    def summarize(self, log: str) -> str:
        final_summary = None
        print("summarizing log started......")

        if log:
            summarized_log = self.summarize_chunks(log)
            chain = prompt_template_summary | self.llm | StrOutputParser()
            final_summary = chain.invoke({"log": summarized_log})
            print(final_summary)

        print("summarizing log completed......")
        return final_summary

    def summarize_chunks(self, chunk_log: str) -> list[Any]:
        chunk_summaries = []

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        chunks = text_splitter.split_text(chunk_log)

        for i, chunk in enumerate(chunks[:5]):
            print(f"processing chunks {i+1}/{len(chunks)}")

            chain = prompt_template_chunk_summary | self.llm | StrOutputParser()
            chunk_summary = chain.invoke({"log_chunks": chunk})
            chunk_summaries.append(chunk_summary)

        return chunk_summaries