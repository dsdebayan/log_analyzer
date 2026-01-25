import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm=ChatOllama(model="gemma3:4b", temperature=0)

question = input("Enter the question")
response = llm.invoke(question)
print(response.content)