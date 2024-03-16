from prompts import *
from make_assistant import *

from typing import List
from context_management.compression import ContextCompressor
from memory import Memory

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document



def ingest_documents(file_path: str) -> Document:
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    return pages

def pratik_patel_response(user_message: str, embedding_provider: str = "openai") -> str:

    instruct_prompt = pratik_patel_instruct()
    document_raw = ingest_documents('text_corpus/survey_questions_and_answers.pdf')
    memory = Memory(embedding_provider)
    context = ContextCompressor(documents=document_raw, embeddings=memory.get_embeddings())

    message = [
        {"role": "system", "content": instruct_prompt},
        {"role": "user", "content": user_message}
    ]

    return generate_response(messages=message)