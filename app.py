import streamlit as st
from analyzer.llm_vector_analyzer import LLMVectorAnalyzer
import os
from utils.validator import FileValidator
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
index_name = "index-log"

# os.environ["LANGSMITH_TRACING"] = "true"
# os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")

# Initialize session state to keep track of inputs
if 'skip_ingest' not in st.session_state:
    st.session_state.skip_ingest = False
if 'skip_summary' not in st.session_state:
    st.session_state.skip_summary = False
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

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

        # text = text[:1000] #commentout

        if st.session_state.analyzer is None:
            analyzer = LLMVectorAnalyzer(openai_api_key=OPENAI_API_KEY, pinecone_api_key=PINECONE_API_KEY,
                                     index_name=index_name)
            st.session_state.analyzer = analyzer
        else:
            analyzer = st.session_state.analyzer

        if not st.session_state.skip_ingest:
            with st.spinner("Ingesting log"):
                try:
                    analyzer.ingest_log_langchain_llm(text)
                    print("analyzer.ingest_log_langchain_llm(text)")
                    st.session_state.skip_ingest = True
                except Exception as e:
                    print("Error ingesting log file", e)
                    st.error(f"Error ingesting log file {e}")


        if st.button("Summarize") and analyzer:
            if not st.session_state.skip_summary:
                container = st.empty()
                with st.spinner("Summarizing log"):
                    try:
                        container.write(analyzer.summarize(text))
                        print("analyzer.summarize(text)")
                        st.session_state.skip_summary = True
                    except Exception as e:
                        print("Error creating final summary", e)
                        st.error(f"Error creating final summary {e}")

        if analyzer:
            container = st.empty()
            st.header("Ask a question about the uploaded log")
            prompt = st.text_input("Enter a question (e.g., List Top 3 issues which are reoccurring)")
            if prompt:
                try:
                    container.write(analyzer.analyze_log_rag(prompt))
                    print("analyzer.analyze_log_rag(prompt)")
                except Exception as e:
                    print("Error analyzing log", e)
                    st.error(f"Error analyzing log {e}")


else:
    st.info("Waiting for you to upload a .log file (max 100 MB)")
