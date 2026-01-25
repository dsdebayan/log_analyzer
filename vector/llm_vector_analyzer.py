from typing import Optional
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_ollama import ChatOllama, OllamaEmbeddings


prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a log analyzer and you will analyze the log and answer questions.
            Use the provided context to respond. If the question is about top 3 recurring issues, return issues with count. If count is greater than 5 use emoji 🔥,
            if count is greater than 3 use emoji ⚠️, If count is greater than 3 use emoji 🟡 else use emoji ✅.
            If the answer is outside the context, acknowledge that you don't know.
            isn't clear, acknowledge that you don't know. 
            Limit your response to three concise sentences.
            {context}

            """),
                ("human", "{input}")
            ]
        )

prompt_template_summary = ChatPromptTemplate.from_template(
           """You are log analyzer that summarizes logs. Identify top 3 issues with count. Add emoji based on each issue count.
            If count is greater than 5 use emoji 🔥, if count is greater than 3 use emoji ⚠️, If count is greater than 3 use emoji 🟡 else use emoji ✅.
            Limit your response to three concise sentences.
            Summarize the following log clearly:
            {log}
            """
        )

class LLMVectorAnalyzer:

    def __init__(self, openai_api_key: Optional[str] = None, pinecone_api_key: Optional[str] = None, index_name: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        # self.llm = ChatOpenAI(model="gpt-4o", api_key=self.openai_api_key)
        self.llm = ChatOllama(model="gemma2:latest", temperature=0)
        # self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
        self.vector_store = None
        self.pc = Pinecone(api_key=self.pinecone_api_key)


    def ingest_log_langchain_llm(self, text: str) -> None:

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        chunks = text_splitter.split_text(text)

        index = self.pc.Index(self.index_name)
        self.vector_store = PineconeVectorStore(index=index, embedding=self.embeddings)
        self.vector_store.add_texts(chunks[:50])

        print("ingestion completed using langchain llm......")

    def ingest_log_pinecone(self, text: str) -> None:

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
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
        index.upsert_records("log", chunks_dict[:50])
        print("ingestion completed using native pinecone......")

    def analyze_log_rag(self, prompt: str) -> str:
        response = []

        # retrieval
        index = self.pc.Index(self.index_name)
        self.vector_store = PineconeVectorStore(index=index, embedding=self.embeddings)
        retriever = self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})


        # generation
        qa_chain = create_stuff_documents_chain(self.llm, prompt_template)
        # augmentation (query + context)
        rag_chain = create_retrieval_chain(retriever, qa_chain)

        if prompt:
            response = rag_chain.invoke({"input": prompt})
            print(response)
        return response['answer']

    def summarize(self, log: str) -> str:
        response = []

        if log:
            chain = prompt_template_summary | self.llm
            response = chain.invoke({"log": log[:len(log)//10]})
            print(response)
        return response.text