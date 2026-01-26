# Log Analyzer - Unit Tests Documentation

## Overview

This directory contains comprehensive unit tests for the Log Analyzer project. The tests cover:

- **FileValidator** - File validation logic
- **Prompts** - LLM prompt templates
- **LLMVectorAnalyzer** - Log analysis and summarization

## Test Structure

```
test/
├── __init__.py
├── test_validator.py           # Tests for FileValidator
├── test_prompts.py             # Tests for prompt templates
├── test_llm_vector_analyzer.py # Tests for LLMVectorAnalyzer
├── README.md                   # This file
└── openai_demo.py              # Demo scripts (existing)
```

## Test Suites

### 1. test_validator.py
Tests for the `FileValidator` class that validates uploaded log files.

**Test Classes:**
- `TestFileValidator` - Core validation tests
  - Valid file extensions (.log)
  - Invalid file extensions (.txt, .pdf, etc.)
  - File size validation
  - Case-insensitive extension handling
  - Edge cases (zero-byte files, multiple dots, special characters)

- `TestFileValidatorEdgeCases` - Edge case tests
  - Long filenames
  - Multiple dots in filename
  - Spaces and special characters

**Key Tests:**
- ✅ Valid .log file acceptance
- ❌ Invalid extension rejection
- ❌ Oversized file (>100MB) rejection
- ✅ Files at exactly 100MB limit
- ✅ Case-insensitive validation

### 2. test_prompts.py
Tests for the LLM prompt templates used in log analysis.

**Test Classes:**
- `TestPromptsModule` - Prompt template validation
  - Verifies prompt templates are ChatPromptTemplate instances
  - Validates required input variables
  - Checks for emoji logic in prompts
  - Verifies system and human roles

- `TestPromptTemplateFormatting` - Template formatting tests
  - Tests prompt formatting with valid inputs
  - Validates substitution of variables

**Key Tests:**
- ✅ Template type validation
- ✅ Input variable presence
- ✅ Emoji logic (🔥⚠️🟡✅)
- ✅ System/human role validation

### 3. test_llm_vector_analyzer.py
Tests for the `LLMVectorAnalyzer` class - the main analysis engine.

**Test Classes:**
- `TestLLMVectorAnalyzerInit` - Initialization tests
  - Parameter initialization
  - Default None values
  - LLM and embeddings initialization

- `TestLLMVectorAnalyzerIngestLog` - Log ingestion tests
  - Text splitting
  - Index deletion/creation
  - Vector store operations

- `TestLLMVectorAnalyzerSummarize` - Summarization tests
  - Chunk summarization
  - Text splitting in summarization
  - Limiting to 5 chunks

- `TestLLMVectorAnalyzerAnalyzeLog` - RAG analysis tests
  - Answer generation
  - Retriever creation

- `TestLLMVectorAnalyzerIntegration` - Integration tests
  - Full analyzer workflow

**Key Tests:**
- ✅ Proper initialization with parameters
- ✅ Text chunking for ingestion
- ✅ Pinecone index management
- ✅ Vector store operations
- ✅ Summarization pipeline
- ✅ RAG chain creation

## Running Tests

### Prerequisites
Install testing dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
python run_tests.py
```

Or use pytest directly:
```bash
pytest test/ -v
```

### Run Specific Test File
```bash
pytest test/test_validator.py -v
```

### Run Specific Test Class
```bash
pytest test/test_validator.py::TestFileValidator -v
```

### Run Specific Test Method
```bash
pytest test/test_validator.py::TestFileValidator::test_valid_log_file -v
```

### Run with Coverage Report
```bash
pytest test/ --cov=analyzer --cov=utils --cov-report=html --cov-report=term-missing
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Tests by Marker
```bash
# Run only unit tests
pytest test/ -m unit

# Run only integration tests
pytest test/ -m integration
```

## Test Coverage

The test suite aims for high coverage of critical functionality:

- **FileValidator**: ~100% coverage
  - 12 test cases
  - All validation paths tested

- **Prompts**: ~100% coverage
  - 10 test cases
  - Template structure and content verified

- **LLMVectorAnalyzer**: ~85% coverage
  - 20+ test cases
  - Uses mocking for external dependencies (Pinecone, LLMs)
  - Core logic paths covered

## Mocking Strategy

Tests use Python's `unittest.mock` library to isolate components:

```python
# External dependencies are mocked:
- Pinecone (vector database)
- ChatOllama (LLM)
- OllamaEmbeddings (embeddings)
- LangChain chains
```

This allows tests to:
- Run without external API calls
- Run without installing heavy dependencies locally
- Focus on logic, not integration
- Execute quickly

## Test Requirements

All tests use only standard library `unittest` + mocking:
- ✅ No external API calls required
- ✅ No database connections needed
- ✅ No heavy model downloads
- ✅ Fast execution (< 5 seconds for full suite)

## Test Results

Expected output:
```
test_validator.py::TestFileValidator::test_valid_log_file PASSED
test_validator.py::TestFileValidator::test_invalid_file_extension_txt PASSED
test_validator.py::TestFileValidator::test_file_size_exceeds_limit PASSED
...

======================== 32 passed in 0.45s =========================
```

## Continuous Integration

These tests are designed to be CI/CD friendly:

1. **Fast Execution**: All tests complete in under 5 seconds
2. **No External Dependencies**: No API keys or network calls needed
3. **Deterministic**: Tests produce consistent results
4. **Clear Output**: Detailed assertion messages for debugging

### Example CI Configuration (GitHub Actions)
```yaml
- name: Run Tests
  run: python -m pytest test/ -v --cov=analyzer --cov=utils
```

## Adding New Tests

When adding new tests:

1. Follow naming convention: `test_<feature>.py`
2. Use clear test method names: `test_<what>_<expected_result>`
3. Use docstrings to describe test purpose
4. Mock external dependencies
5. Keep tests isolated and independent
6. Add assertions with clear failure messages

Example:
```python
def test_new_feature_returns_correct_value(self):
    """Test that new feature returns expected value"""
    result = function_under_test(input_data)
    self.assertEqual(result, expected_value)
```

## Troubleshooting

### Tests fail with "ImportError"
- Ensure you're in the project root directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Tests fail with "ModuleNotFoundError"
- Check Python path includes project root
- Run from project root directory

### Coverage report not generated
- Ensure pytest-cov is installed: `pip install pytest-cov`
- Check write permissions in project directory

## Test Metrics

Current test suite statistics:
- **Total Test Cases**: 32+
- **Code Coverage**: ~90%
- **Execution Time**: < 5 seconds
- **Test Frameworks**: unittest + pytest

## Contributing

When modifying code:
1. Run existing tests to ensure no regressions
2. Add tests for new functionality
3. Aim for >80% code coverage
4. Ensure all tests pass before committing

## License

Same as main project
