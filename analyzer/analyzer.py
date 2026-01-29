from typing import Optional, Any, List

from langchain_aws import BedrockLLM
from langchain_community.embeddings import BedrockEmbeddings
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import TextLoader
from utils.prompts import prompt_template


class Analyzer:

    def __init__(self, openai_api_key: Optional[str] = None, pinecone_api_key: Optional[str] = None, index_name: Optional[str] = None, model_vendor: str = None):
        self.openai_api_key = openai_api_key
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name
        if model_vendor == "ollama":
            self.llm = ChatOllama(model="llama3.2:latest")
            self.embeddings = OllamaEmbeddings(model="embeddinggemma:latest")
        elif model_vendor == 'openai':
            self.llm = ChatOpenAI(model="gpt-4o-mini")
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        elif model_vendor == 'bedrock':
            self.llm = ChatOpenAI(model="gpt-4o-mini")
            self.embeddings = BedrockEmbeddings(credentials_profile_name= 'default', model_id='amazon.titan-embed-text-v1')
            llm = BedrockLLM(
                credentials_profile_name="default",
                model_id="anthropic.claude-v2")

        self.vector_store = None
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.vector_store = PineconeVectorStore(index_name=self.index_name, embedding=self.embeddings)


    def ingest(self, file_path: str) -> int:

        print("ingestion started......")

        loaded_docs :list[Document] = TextLoader(file_path).load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        chunks = splitter.split_documents(loaded_docs)

        if self.pc.has_index(self.index_name):
            self.pc.delete_index(self.index_name)

        self.pc.create_index(
            name=self.index_name,
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            dimension=768
        )

        print(f"chunks to ingest {len(chunks)}")

        self.vector_store.add_documents(chunks)

        print("ingestion completed using langchain llm......")
        return len(chunks)


    def rag(self, prompt: str):
        print("rag flow started......")

        # retrieval
        retriever = self.vector_store.as_retriever(search_type="similarity", k=1000)

        # chain
        qa_chain = create_stuff_documents_chain(self.llm, prompt_template)
        # augmentation (query + context)
        rag_chain = create_retrieval_chain(retriever, qa_chain)

        if prompt:
            response = rag_chain.invoke({"input": prompt})

            answer: str = response["answer"]
            docs: List[Document] = response["context"]

            unique_sources = {d.metadata.get("source") for d in docs if d.metadata.get("source")}
            sources = sorted(unique_sources)

            contexts = []
            for d in docs:
                contexts.append(d.page_content)

            print(f"answer : {answer}")
            print(f"sources : {sources}")
            print(f"contexts : {contexts}")

            print("rag flow completed......")
            return answer, sources, contexts
        return None
