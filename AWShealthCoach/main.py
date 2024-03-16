from prompts import *
from make_assistant import *

from typing import List
from context_management.compression import ContextCompressor
from memory import Memory

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document



def ingest_documents(file_path: str) -> str:
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    raw_text = ""

    for i in range(len(pages) - 1):
        raw_text += pages[i].page_content

    return raw_text

def pratik_patel_response(user_message: str, embedding_provider: str = "openai") -> str:

    instruct_prompt = pratik_patel_instruct()
    document_raw = ingest_documents('text_corpus/survey_questions_and_answers.pdf')
    print(document_raw)
    memory = Memory(embedding_provider)
    context = ContextCompressor(documents=document_raw, embeddings=memory.get_embeddings())

    #TODO adjust max_results arg as needed
    relevant_context = context.get_context(user_message, max_results=5)

    message = [
        {"role": "system", "content": instruct_prompt},
        {"role": "user", "content": relevant_context},
        {"role": "user", "content": user_message},
    ]

    return generate_response(messages=message)

response = pratik_patel_response('Im trying to remember in the survey questions i answered what my starting numbers were. Can you tell me?')
print(response)