from prompts import *
from make_assistant import *

from typing import List
from context_management.compression import ContextCompressor
from memory import Memory

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document



def ingest_documents(file_paths: List[str]) -> List[Document]:
    documents_list = []
    for file_path in file_paths:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            documents_list.extend(pages)
        else:
            raise ValueError(f"File {file_path} must be a PDF.")
    return documents_list

def pratik_patel_response(user_message: str, embedding_provider: str = "openai") -> str:

    instruct_prompt = pratik_patel_instruct()

    #TODO probably need to parameterize file inputs
    documents = ingest_documents(['text_corpus/survey_questions_and_answers.pdf'])
    memory = Memory(embedding_provider)
    context = ContextCompressor(documents=documents, embeddings=memory.get_embeddings())

    #TODO adjust max_results arg as needed
    relevant_context = context.get_context(user_message, max_results=5)

    message = [
        {"role": "system", "content": instruct_prompt},
        {"role": "user", "content": relevant_context},
        {"role": "user", "content": user_message},
    ]
    return generate_response(messages=message)