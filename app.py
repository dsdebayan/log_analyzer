import streamlit as st
from vector.llm_vector_analyzer import LLMVectorAnalyzer
import os
from analyzer.validator import FileValidator
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
index_name = "index-log-analyzer"

# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")

st.set_page_config(page_title="Log Analyzer", layout="wide")

st.title("Log Analyzer — Upload .log files and ask questions")

st.markdown("""
This app uses OpenAI embeddings + LangChain + PineCone + OpenAI llm to index uploaded .log files and answer questions about them.
""")

uploaded_file = st.file_uploader("Upload a .log file (max 100 MB)", type=["log"], accept_multiple_files=False)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    size = len(file_bytes)

    ok, msg = FileValidator.validate(filename, size)
    if not ok:
        st.error(msg)
    else:
        try:
            text = file_bytes.decode("utf-8")
        except Exception:
            text = file_bytes.decode("latin-1")


        analyzer = LLMVectorAnalyzer(openai_api_key=OPENAI_API_KEY, pinecone_api_key=PINECONE_API_KEY, index_name=index_name)
        # analyzer.ingest_log_pinecone(text)

        st.header("Summary :")
        # st.write(analyzer.summarize(text))

        st.markdown("---")

        st.header("Ask a question about the uploaded log")
        prompt = st.text_input("Enter a question (e.g., List Top 3 issues which are reoccurring)")
        if prompt:
            st.write(analyzer.analyze_log_rag(prompt))


else:
    st.info("Waiting for you to upload a .log file (max 100 MB)")
