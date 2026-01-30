import streamlit as st
from analyzer.analyzer import Analyzer
import os
from utils.validator import FileValidator
from dotenv import load_dotenv
import tempfile

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("INDEX_LOG")
model_vendor = os.getenv("MODEL_VENDOR")
llm_model = os.getenv("LLM_MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")

if 'skip_ingest' not in st.session_state:
    st.session_state.skip_ingest = False
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None

st.set_page_config(page_title="Log Analyzer", layout="wide")

st.title("Log Analyzer — Upload .log files and ask questions")

st.markdown("""
This app uses langchain based RAG flow to analyze log files. Tech stack used : Python, Streamlit, langchain, Pinecone embedding vector db and llm models for chat.""")

uploaded_file = st.file_uploader("Upload a .log file (max 100 MB)", type=["log"], accept_multiple_files=False)

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    size = len(file_bytes)

    ok, msg = FileValidator.validate(filename, size)
    st.session_state.skip_ingest = False
    if not ok:
        st.error(msg)
    else:

        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, uploaded_file.name)

        with open(path, "wb") as f:
            f.write(uploaded_file.getvalue())

        if st.session_state.analyzer is None:
            analyzer = Analyzer(openai_api_key=OPENAI_API_KEY, pinecone_api_key=PINECONE_API_KEY,
                                index_name=index_name, model_vendor=model_vendor,
                                llm_model=llm_model, embedding_model=embedding_model)
            st.session_state.analyzer = analyzer
        else:
            analyzer = st.session_state.analyzer

        if not st.session_state.skip_ingest:
            with st.spinner("Ingesting log"):
                try:
                    chunk_size = analyzer.ingest(path)
                    st.success(f"Chunks ingested : {chunk_size}")
                    st.session_state.skip_ingest = True
                except Exception as e:
                    print("Error ingesting log file", e)
                    st.error(f"Error ingesting log file {e}")

        if analyzer:
            st.header("Ask a question about the uploaded log")
            prompt = st.text_input("Enter a question")
            if prompt:
                try:
                    answer, sources , contexts = analyzer.rag(prompt)
                    container = st.empty()
                    container.write(f"{answer}")
                except Exception as e:
                    print("Error analyzing log", e)
                    st.error(f"Error analyzing log {e}")

else:
    st.info("Waiting for you to upload a .log file (max 100 MB)")
