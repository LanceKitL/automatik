from langchain_commnunity.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from lanhchain_chains import RetrievalQA

from services.cache_service import (
    get_cache_response,
    save_cache
)

embedding = OpenAIEmbeddings()

vectorstore = FAISS.load_local(
    "vectorstore"
)