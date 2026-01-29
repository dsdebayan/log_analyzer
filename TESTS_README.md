# Unit Test Quick Reference

## Test Execution

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Category
```bash
# File validation tests
python -m pytest test/test_validator.py -v

# Prompt template tests
python -m pytest test/test_prompts.py -v

# Analyzer and RAG tests
python -m pytest test/test_analyzer.py -v
```

### Run Specific Test
```bash
python -m pytest test/test_validator.py::TestFileValidatorValidation::test_valid_log_file -v
```

### View Coverage Report
After running tests, open:
```
htmlcov/index.html
```

## Test Summary

| Module | Tests | Coverage | Status |
|--------|-------|----------|--------|
| analyzer.py | 15 | 94% | ✅ All Pass |
| validator.py | 22 | 100% | ✅ All Pass |
| prompts.py | 12 | 100% | ✅ All Pass |
| **TOTAL** | **49** | **95%** | **✅ All Pass** |

## Test Files

| File | Purpose |
|------|---------|
| `test/test_validator.py` | File validation tests (22 tests) |
| `test/test_prompts.py` | Prompt template tests (12 tests) |
| `test/test_analyzer.py` | Analyzer and RAG flow tests (15 tests) |

## Key Testing Areas

### ✅ File Validator
- Extension validation (.log files only)
- File size validation (max 100 MB)
- Edge cases (special characters, multiple dots, empty files)

### ✅ Prompts
- Template structure validation
- Message configuration
- Variable substitution

### ✅ Analyzer (RAG Focus)
- Model initialization (OpenAI, Ollama, Bedrock)
- File ingestion and chunking
- **RAG flow** (retrieval, augmentation, generation)
- Source tracking and deduplication
- Error handling

## Notes

- All external dependencies are mocked (no real API calls)
- Tests run in ~10 seconds
- No external files or services required
- 100% of validation and prompt logic covered
- 94% of analyzer logic covered (Bedrock optional code excluded)
