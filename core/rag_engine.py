import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda,RunnablePassthrough
from core.llm import get_llm
from core.vector_store import (build_vector_store,get_vector_store,get_retriever)
load_dotenv()

llm=get_llm()


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(transcript:str)->str:
    vector_store=build_vector_store(transcript)
    retriever=get_retriever(vector_store)
    prompt = ChatPromptTemplate.from_messages(
        [("system",
          """You are an expert meeting assistant. Answer the user's question 
          based ONLY on the meeting transcript context provided below.
          If the answer is not found in the context, say: 
          "I could not find this information in the meeting transcript."
          Always be concise and precise. If quoting someone, mention it clearly.
          Context from meeting transcript:
          {context}""",
        ),
        ("human", "{question}"),
    ]
    )
    chain=  (
        {
            "context":retriever | RunnableLambda(format_docs),
            "question":RunnablePassthrough()
        }
    ) | prompt | llm | StrOutputParser()

    return chain

def get_rag_chain():
    vector_store=get_vector_store()
    retriever=get_retriever(vector_store)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
            based ONLY on the meeting transcript context provided below.
            If the answer is not found in the context, say: 
            "I could not find this information in the meeting transcript."
            Always be concise and precise. If quoting someone, mention it clearly.
            Context from meeting transcript:
            {context}""",
        ),
        ("human", "{question}"),
    ])

    chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer