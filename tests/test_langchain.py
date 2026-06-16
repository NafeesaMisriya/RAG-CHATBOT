from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

prompt = ChatPromptTemplate.from_template(
    """
Question:
{question}

Answer:
"""
)

chain = prompt | llm

response = chain.invoke(
    {
        "question":
        "What is DNA?"
    }
)

print(
    response.content
)