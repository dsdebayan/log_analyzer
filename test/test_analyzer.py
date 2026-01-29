"""
Unit tests for the Analyzer class in analyzer/analyzer.py
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from analyzer.analyzer import Analyzer
from langchain_core.documents import Document


class TestAnalyzerInitialization:
    """Tests for Analyzer initialization"""

    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_analyzer_initialization_openai(self, mock_vector_store, mock_pinecone,
                                             mock_embeddings, mock_llm):
        """Test Analyzer initialization with OpenAI model vendor"""
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        assert analyzer.openai_api_key == "test-key"
        assert analyzer.pinecone_api_key == "test-pinecone-key"
        assert analyzer.index_name == "test-index"
        mock_llm.assert_called_once_with(model="gpt-4o-mini")
        mock_embeddings.assert_called_once_with(model="text-embedding-3-large")

    @patch('analyzer.analyzer.ChatOllama')
    @patch('analyzer.analyzer.OllamaEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_analyzer_initialization_ollama(self, mock_vector_store, mock_pinecone,
                                             mock_embeddings, mock_llm):
        """Test Analyzer initialization with Ollama model vendor"""
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="ollama"
        )

        mock_llm.assert_called_once_with(model="llama3.2:latest")
        mock_embeddings.assert_called_once_with(model="embeddinggemma:latest")

    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_analyzer_initialization_with_none_keys(self, mock_vector_store, mock_pinecone):
        """Test Analyzer initialization with None API keys"""
        analyzer = Analyzer(
            openai_api_key=None,
            pinecone_api_key=None,
            index_name="test-index",
            model_vendor="openai"
        )

        assert analyzer.openai_api_key is None
        assert analyzer.pinecone_api_key is None

    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_analyzer_vector_store_initialization(self, mock_vector_store_class,
                                                   mock_pinecone, mock_embeddings,
                                                   mock_llm):
        """Test that vector store is initialized correctly"""
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        # Verify vector store was created
        mock_vector_store_class.assert_called_once()


class TestAnalyzerIngestion:
    """Tests for the ingest method"""

    @patch('analyzer.analyzer.TextLoader')
    @patch('analyzer.analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_ingest_success(self, mock_vector_store_class, mock_pinecone_class,
                            mock_embeddings, mock_llm, mock_splitter_class,
                            mock_loader_class):
        """Test successful ingestion of log file"""
        # Setup mocks
        mock_doc = Document(page_content="test log content")
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        mock_chunks = [Document(page_content="chunk1"), Document(page_content="chunk2")]
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = mock_chunks
        mock_splitter_class.return_value = mock_splitter

        mock_pinecone = MagicMock()
        mock_pinecone.has_index.return_value = False
        mock_pinecone_class.return_value = mock_pinecone

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Create analyzer and ingest
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        result = analyzer.ingest("/path/to/test.log")

        # Assertions
        assert result == 2  # Should return number of chunks
        mock_loader_class.assert_called_once_with("/path/to/test.log")
        mock_vector_store.add_documents.assert_called_once_with(mock_chunks)

    @patch('analyzer.analyzer.TextLoader')
    @patch('analyzer.analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_ingest_deletes_existing_index(self, mock_vector_store_class,
                                            mock_pinecone_class, mock_embeddings,
                                            mock_llm, mock_splitter_class,
                                            mock_loader_class):
        """Test that existing index is deleted before ingestion"""
        # Setup mocks
        mock_doc = Document(page_content="test log content")
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        mock_chunks = [Document(page_content="chunk1")]
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = mock_chunks
        mock_splitter_class.return_value = mock_splitter

        mock_pinecone = MagicMock()
        mock_pinecone.has_index.return_value = True  # Index already exists
        mock_pinecone_class.return_value = mock_pinecone

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Create analyzer and ingest
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        analyzer.ingest("/path/to/test.log")

        # Verify index was deleted
        mock_pinecone.delete_index.assert_called_once_with("test-index")

    @patch('analyzer.analyzer.TextLoader')
    @patch('analyzer.analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_ingest_creates_index(self, mock_vector_store_class, mock_pinecone_class,
                                   mock_embeddings, mock_llm, mock_splitter_class,
                                   mock_loader_class):
        """Test that index is created during ingestion"""
        # Setup mocks
        mock_doc = Document(page_content="test log content")
        mock_loader = MagicMock()
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        mock_chunks = [Document(page_content="chunk1")]
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = mock_chunks
        mock_splitter_class.return_value = mock_splitter

        mock_pinecone = MagicMock()
        mock_pinecone.has_index.return_value = False
        mock_pinecone_class.return_value = mock_pinecone

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Create analyzer and ingest
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        analyzer.ingest("/path/to/test.log")

        # Verify index was created with correct parameters
        mock_pinecone.create_index.assert_called_once()
        call_kwargs = mock_pinecone.create_index.call_args[1]
        assert call_kwargs['name'] == "test-index"
        assert call_kwargs['dimension'] == 768

    @patch('analyzer.analyzer.TextLoader')
    @patch('analyzer.analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_ingest_with_empty_file(self, mock_vector_store_class, mock_pinecone_class,
                                     mock_embeddings, mock_llm, mock_splitter_class,
                                     mock_loader_class):
        """Test ingestion with an empty log file"""
        # Setup mocks
        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_class.return_value = mock_loader

        mock_chunks = []
        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = mock_chunks
        mock_splitter_class.return_value = mock_splitter

        mock_pinecone = MagicMock()
        mock_pinecone.has_index.return_value = False
        mock_pinecone_class.return_value = mock_pinecone

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        # Create analyzer and ingest
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        result = analyzer.ingest("/path/to/empty.log")

        # Should return 0 chunks
        assert result == 0


class TestAnalyzerRAGFlow:
    """Tests for the RAG (Retrieval-Augmented Generation) method"""

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_success(self, mock_vector_store_class, mock_pinecone_class,
                         mock_embeddings, mock_llm, mock_qa_chain_class,
                         mock_rag_chain_class):
        """Test successful RAG flow"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        # Setup chain mocks
        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        mock_doc1 = Document(page_content="error log entry",
                            metadata={"source": "application.log"})
        mock_doc2 = Document(page_content="another error",
                            metadata={"source": "application.log"})

        mock_rag_chain = MagicMock()
        mock_rag_chain.invoke.return_value = {
            "answer": "The error occurred due to...",
            "context": [mock_doc1, mock_doc2]
        }
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        answer, sources, contexts = analyzer.rag("What caused the error?")

        # Assertions
        assert answer == "The error occurred due to..."
        assert "application.log" in sources
        assert len(contexts) == 2
        assert contexts[0] == "error log entry"
        assert contexts[1] == "another error"

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_with_multiple_sources(self, mock_vector_store_class,
                                        mock_pinecone_class, mock_embeddings,
                                        mock_llm, mock_qa_chain_class,
                                        mock_rag_chain_class):
        """Test RAG flow with multiple document sources"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        # Documents from different sources
        mock_doc1 = Document(page_content="error in file 1",
                            metadata={"source": "log1.log"})
        mock_doc2 = Document(page_content="error in file 2",
                            metadata={"source": "log2.log"})

        mock_rag_chain = MagicMock()
        mock_rag_chain.invoke.return_value = {
            "answer": "Multiple errors found",
            "context": [mock_doc1, mock_doc2]
        }
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        answer, sources, contexts = analyzer.rag("Find all errors")

        # Assertions
        assert len(sources) == 2
        assert "log1.log" in sources
        assert "log2.log" in sources

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_with_duplicate_sources(self, mock_vector_store_class,
                                         mock_pinecone_class, mock_embeddings,
                                         mock_llm, mock_qa_chain_class,
                                         mock_rag_chain_class):
        """Test RAG flow deduplicates sources"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        # Multiple documents from the same source
        mock_doc1 = Document(page_content="error 1",
                            metadata={"source": "application.log"})
        mock_doc2 = Document(page_content="error 2",
                            metadata={"source": "application.log"})

        mock_rag_chain = MagicMock()
        mock_rag_chain.invoke.return_value = {
            "answer": "Multiple errors in same file",
            "context": [mock_doc1, mock_doc2]
        }
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        answer, sources, contexts = analyzer.rag("Analyze errors")

        # Sources should be deduplicated
        assert len(sources) == 1
        assert sources[0] == "application.log"

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_with_empty_prompt(self, mock_vector_store_class, mock_pinecone_class,
                                    mock_embeddings, mock_llm, mock_qa_chain_class,
                                    mock_rag_chain_class):
        """Test RAG flow with empty prompt returns None"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        mock_rag_chain = MagicMock()
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG with empty prompt
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        result = analyzer.rag("")

        # Should return None for empty prompt
        assert result is None

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_with_none_prompt(self, mock_vector_store_class, mock_pinecone_class,
                                   mock_embeddings, mock_llm, mock_qa_chain_class,
                                   mock_rag_chain_class):
        """Test RAG flow with None prompt returns None"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        mock_rag_chain = MagicMock()
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG with None prompt
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        result = analyzer.rag(None)

        # Should return None for None prompt
        assert result is None

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_retriever_search_k_value(self, mock_vector_store_class,
                                          mock_pinecone_class, mock_embeddings,
                                          mock_llm, mock_qa_chain_class,
                                          mock_rag_chain_class):
        """Test that RAG retriever uses correct k value for similarity search"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        mock_doc = Document(page_content="test", metadata={"source": "test.log"})
        mock_rag_chain = MagicMock()
        mock_rag_chain.invoke.return_value = {
            "answer": "test answer",
            "context": [mock_doc]
        }
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        analyzer.rag("Test query")

        # Verify retriever was created with k=1000
        mock_vector_store.as_retriever.assert_called_once_with(
            search_type="similarity", k=1000
        )

    @patch('analyzer.analyzer.create_retrieval_chain')
    @patch('analyzer.analyzer.create_stuff_documents_chain')
    @patch('analyzer.analyzer.ChatOpenAI')
    @patch('analyzer.analyzer.OpenAIEmbeddings')
    @patch('analyzer.analyzer.Pinecone')
    @patch('analyzer.analyzer.PineconeVectorStore')
    def test_rag_with_documents_without_metadata(self, mock_vector_store_class,
                                                  mock_pinecone_class, mock_embeddings,
                                                  mock_llm, mock_qa_chain_class,
                                                  mock_rag_chain_class):
        """Test RAG handles documents without source metadata gracefully"""
        # Setup mocks
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_vector_store_class.return_value = mock_vector_store

        mock_pinecone = MagicMock()
        mock_pinecone_class.return_value = mock_pinecone

        mock_qa_chain = MagicMock()
        mock_qa_chain_class.return_value = mock_qa_chain

        # Document without source metadata
        mock_doc = Document(page_content="test content", metadata={})

        mock_rag_chain = MagicMock()
        mock_rag_chain.invoke.return_value = {
            "answer": "test answer",
            "context": [mock_doc]
        }
        mock_rag_chain_class.return_value = mock_rag_chain

        # Create analyzer and run RAG
        analyzer = Analyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-pinecone-key",
            index_name="test-index",
            model_vendor="openai"
        )

        answer, sources, contexts = analyzer.rag("Query")

        # Should handle gracefully - sources should be empty
        assert len(sources) == 0
        assert len(contexts) == 1
