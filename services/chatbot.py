"""Minimal chatbot wrapper.

This keeps the module importable even when optional dependencies are missing.
"""

from typing import Optional

try:
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    from langchain.chains import RetrievalQA
    HAVE_LANGCHAIN = True
except Exception:
    HAVE_LANGCHAIN = False


_qa_chain = None


def _init_chain() -> None:
    global _qa_chain
    if _qa_chain is not None or not HAVE_LANGCHAIN:
        return

    embedding = OpenAIEmbeddings()
    vectorstore = FAISS.load_local("vectorstore", embedding)
    llm = ChatOpenAI()
    _qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())


def get_chatbot_response(prompt: str) -> Optional[str]:
    if not prompt:
        return None

    _init_chain()
    if _qa_chain is None:
        return "Chatbot is unavailable."

    result = _qa_chain.run(prompt)
    return result