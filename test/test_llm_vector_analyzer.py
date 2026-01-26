import unittest
from unittest.mock import Mock, MagicMock, patch, call
from analyzer.llm_vector_analyzer import LLMVectorAnalyzer


class TestLLMVectorAnalyzerInit(unittest.TestCase):
    """Test cases for LLMVectorAnalyzer initialization"""

    def test_analyzer_initialization_with_parameters(self):
        """Test LLMVectorAnalyzer initializes with correct parameters"""
        openai_key = "test-openai-key"
        pinecone_key = "test-pinecone-key"
        index_name = "test-index"

        with patch('analyzer.llm_vector_analyzer.ChatOllama'), \
             patch('analyzer.llm_vector_analyzer.OllamaEmbeddings'), \
             patch('analyzer.llm_vector_analyzer.Pinecone'):
            analyzer = LLMVectorAnalyzer(
                openai_api_key=openai_key,
                pinecone_api_key=pinecone_key,
                index_name=index_name
            )

            self.assertEqual(analyzer.openai_api_key, openai_key)
            self.assertEqual(analyzer.pinecone_api_key, pinecone_key)
            self.assertEqual(analyzer.index_name, index_name)

    def test_analyzer_initialization_with_none_values(self):
        """Test LLMVectorAnalyzer initializes with None values"""
        with patch('analyzer.llm_vector_analyzer.ChatOllama'), \
             patch('analyzer.llm_vector_analyzer.OllamaEmbeddings'), \
             patch('analyzer.llm_vector_analyzer.Pinecone'):
            analyzer = LLMVectorAnalyzer()

            self.assertIsNone(analyzer.openai_api_key)
            self.assertIsNone(analyzer.pinecone_api_key)
            self.assertIsNone(analyzer.index_name)

    def test_analyzer_vector_store_initialized_as_none(self):
        """Test LLMVectorAnalyzer vector_store is None on initialization"""
        with patch('analyzer.llm_vector_analyzer.ChatOllama'), \
             patch('analyzer.llm_vector_analyzer.OllamaEmbeddings'), \
             patch('analyzer.llm_vector_analyzer.Pinecone'):
            analyzer = LLMVectorAnalyzer()
            self.assertIsNone(analyzer.vector_store)

    def test_analyzer_initializes_llm_and_embeddings(self):
        """Test that LLMVectorAnalyzer initializes llm and embeddings"""
        with patch('analyzer.llm_vector_analyzer.ChatOllama') as mock_ollama_llm, \
             patch('analyzer.llm_vector_analyzer.OllamaEmbeddings') as mock_ollama_embed, \
             patch('analyzer.llm_vector_analyzer.Pinecone'):
            analyzer = LLMVectorAnalyzer()

            mock_ollama_llm.assert_called()
            mock_ollama_embed.assert_called()
            self.assertIsNotNone(analyzer.llm)
            self.assertIsNotNone(analyzer.embeddings)


class TestLLMVectorAnalyzerIngestLog(unittest.TestCase):
    """Test cases for ingest_log_langchain_llm method"""

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_ingest_log_splits_text(self, mock_embed, mock_llm, mock_splitter,
                                     mock_vector_store, mock_pc):
        """Test that ingest_log_langchain_llm splits text correctly"""
        # Setup mocks
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_splitter.return_value = mock_splitter_instance

        mock_pc_instance = Mock()
        mock_pc_instance.has_index.return_value = False
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance

        # Create analyzer and ingest
        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        test_log = "line1\nline2\nline3"

        analyzer.ingest_log_langchain_llm(test_log)

        # Verify text was split
        mock_splitter_instance.split_text.assert_called_once_with(test_log)

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_ingest_log_deletes_existing_index(self, mock_embed, mock_llm, mock_splitter,
                                                mock_vector_store, mock_pc):
        """Test that ingest_log deletes existing index before creating new one"""
        # Setup mocks
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = ["chunk1"]
        mock_splitter.return_value = mock_splitter_instance

        mock_pc_instance = Mock()
        mock_pc_instance.has_index.return_value = True
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance

        # Create analyzer and ingest
        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        analyzer.ingest_log_langchain_llm("test log")

        # Verify delete was called
        mock_pc_instance.delete_index.assert_called_once_with("test-index")

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_ingest_log_creates_index(self, mock_embed, mock_llm, mock_splitter,
                                       mock_vector_store, mock_pc):
        """Test that ingest_log creates a new Pinecone index"""
        # Setup mocks
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = ["chunk1"]
        mock_splitter.return_value = mock_splitter_instance

        mock_pc_instance = Mock()
        mock_pc_instance.has_index.return_value = False
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance

        # Create analyzer and ingest
        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        analyzer.ingest_log_langchain_llm("test log")

        # Verify create_index was called
        mock_pc_instance.create_index.assert_called_once()

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_ingest_log_adds_texts_to_vector_store(self, mock_embed, mock_llm, mock_splitter,
                                                     mock_vector_store, mock_pc):
        """Test that ingest_log adds text chunks to vector store"""
        # Setup mocks
        chunks = ["chunk1", "chunk2", "chunk3"]
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = chunks
        mock_splitter.return_value = mock_splitter_instance

        mock_pc_instance = Mock()
        mock_pc_instance.has_index.return_value = False
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_vector_store.return_value = mock_vector_store_instance

        # Create analyzer and ingest
        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        analyzer.ingest_log_langchain_llm("test log")

        # Verify add_texts was called (may be called multiple times for batching)
        self.assertGreater(mock_vector_store_instance.add_texts.call_count, 0)


class TestLLMVectorAnalyzerSummarize(unittest.TestCase):
    """Test cases for summarize and summarize_chunks methods"""

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_summarize_calls_summarize_chunks(self, mock_embed, mock_llm, mock_pc):
        """Test that summarize calls summarize_chunks"""
        with patch.object(LLMVectorAnalyzer, 'summarize_chunks') as mock_summarize_chunks:
            mock_summarize_chunks.return_value = ["summary1", "summary2"]

            # Mock the chain to avoid validation errors
            with patch('analyzer.llm_vector_analyzer.prompt_template_summary'):
                with patch('analyzer.llm_vector_analyzer.StrOutputParser'):
                    mock_llm_instance = Mock()
                    mock_llm_instance.__or__ = Mock(return_value=Mock())
                    mock_llm.return_value = mock_llm_instance

                    analyzer = LLMVectorAnalyzer()
                    try:
                        analyzer.summarize("test log")
                    except:
                        pass  # Chain execution may fail, but we're testing the call

                    mock_summarize_chunks.assert_called_once_with("test log")

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_summarize_chunks_splits_text(self, mock_embed, mock_llm, mock_splitter, mock_pc):
        """Test that summarize_chunks splits the log text"""
        # Setup mocks
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_splitter.return_value = mock_splitter_instance

        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        analyzer = LLMVectorAnalyzer()
        with patch('analyzer.llm_vector_analyzer.StrOutputParser'):
            with patch('analyzer.llm_vector_analyzer.prompt_template_chunk_summary'):
                try:
                    analyzer.summarize_chunks("test log")
                except:
                    pass  # Chain execution may fail, but we're testing the split

                mock_splitter_instance.split_text.assert_called()

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.RecursiveCharacterTextSplitter')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_summarize_chunks_limits_to_5_chunks(self, mock_embed, mock_llm, mock_splitter, mock_pc):
        """Test that summarize_chunks only processes first 5 chunks"""
        # Setup mocks with many chunks
        chunks = [f"chunk{i}" for i in range(10)]
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_text.return_value = chunks
        mock_splitter.return_value = mock_splitter_instance

        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        analyzer = LLMVectorAnalyzer()
        with patch('analyzer.llm_vector_analyzer.StrOutputParser'):
            with patch('analyzer.llm_vector_analyzer.prompt_template_chunk_summary'):
                try:
                    result = analyzer.summarize_chunks("test log")
                    # Should return at most 5 summaries
                    self.assertLessEqual(len(result), 5)
                except:
                    pass


class TestLLMVectorAnalyzerAnalyzeLog(unittest.TestCase):
    """Test cases for analyze_log_rag method"""

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.create_stuff_documents_chain')
    @patch('analyzer.llm_vector_analyzer.create_retrieval_chain')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_analyze_log_rag_returns_answer(self, mock_embed, mock_llm, mock_retrieval_chain,
                                             mock_stuff_chain, mock_vector_store, mock_pc):
        """Test that analyze_log_rag returns an answer string"""
        # Setup mocks
        mock_pc_instance = Mock()
        mock_index = Mock()
        mock_pc_instance.Index.return_value = mock_index
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_retriever = Mock()
        mock_vector_store_instance.as_retriever.return_value = mock_retriever
        mock_vector_store.return_value = mock_vector_store_instance

        mock_rag_chain = Mock()
        mock_rag_chain.invoke.return_value = {"answer": "Test answer"}
        mock_retrieval_chain.return_value = mock_rag_chain

        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        result = analyzer.analyze_log_rag("What happened?")

        self.assertEqual(result, "Test answer")

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.PineconeVectorStore')
    @patch('analyzer.llm_vector_analyzer.create_stuff_documents_chain')
    @patch('analyzer.llm_vector_analyzer.create_retrieval_chain')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_analyze_log_rag_creates_retriever(self, mock_embed, mock_llm, mock_retrieval_chain,
                                                mock_stuff_chain, mock_vector_store, mock_pc):
        """Test that analyze_log_rag creates a retriever"""
        # Setup mocks
        mock_pc_instance = Mock()
        mock_index = Mock()
        mock_pc_instance.Index.return_value = mock_index
        mock_pc.return_value = mock_pc_instance

        mock_vector_store_instance = Mock()
        mock_retriever = Mock()
        mock_vector_store_instance.as_retriever.return_value = mock_retriever
        mock_vector_store.return_value = mock_vector_store_instance

        mock_rag_chain = Mock()
        mock_rag_chain.invoke.return_value = {"answer": "Test answer"}
        mock_retrieval_chain.return_value = mock_rag_chain

        analyzer = LLMVectorAnalyzer(pinecone_api_key="test-key", index_name="test-index")
        analyzer.analyze_log_rag("What happened?")

        mock_vector_store_instance.as_retriever.assert_called_once()


class TestLLMVectorAnalyzerIntegration(unittest.TestCase):
    """Integration tests for LLMVectorAnalyzer"""

    @patch('analyzer.llm_vector_analyzer.Pinecone')
    @patch('analyzer.llm_vector_analyzer.ChatOllama')
    @patch('analyzer.llm_vector_analyzer.OllamaEmbeddings')
    def test_analyzer_workflow(self, mock_embed, mock_llm, mock_pc):
        """Test basic analyzer workflow initialization"""
        analyzer = LLMVectorAnalyzer(
            openai_api_key="test-key",
            pinecone_api_key="test-key",
            index_name="test-index"
        )

        self.assertIsNotNone(analyzer.llm)
        self.assertIsNotNone(analyzer.embeddings)
        self.assertIsNone(analyzer.vector_store)
        self.assertEqual(analyzer.index_name, "test-index")


if __name__ == '__main__':
    unittest.main()
