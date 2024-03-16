from litellm import completion
import os
from typing import List, Dict

from prompts import *
from make_assistant import *

from context_management.compression import ContextCompressor
from memory import Memory

from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document


# from dotenv import load_dotenv
# load_dotenv()

# from openai import OpenAI
# client = OpenAI()

"""
Litellm: https://github.com/BerriAI/litellm allows us to retain the OpenAI API format but support different models.

Example completion method: 

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion(model="gpt-3.5-turbo", messages=messages)
"""

# redundancy
def check_env_key():
  if "OPENAI_API_KEY" not in os.environ:
    import yaml
    with open("AWShealthCoach/template.yaml", "r") as file:
      template_data = yaml.safe_load(file)
      os.environ["OPENAI_API_KEY"] = template_data["Resources"]["TwilioWebhookFunction"]["Properties"]["Environment"]["Variables"]["OPENAI_API_KEY"]
  if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("OPENAI_API_KEY is not set in environment variables.")

# putting messages first so we can support a default model
def generate_response(messages: List[Dict[str, str]], model: str = "gpt-4-0125-preview"):
  check_env_key()
  response = completion(messages=messages, model=model)
  return response

# # Upload the document
# file = client.files.create(
#   file=open("Health-Goals-and-Recommendation-Template.docx", "rb"),
#   purpose='assistants'
# )

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
        {"role": "user", "content": relevant_context},
        {"role": "user", "content": user_message},
    ]
    return generate_response(messages=message)

my_assistant = client.beta.assistants.create(
    instructions=instructions_str,
    name="Guide v3",
    tools=[{
        "type": "function",
      "function": {
      "name": "pratik_patel_response",
      "description": "Generate an answer as Pratik Patel given a user's input question.",
      "parameters": {
        "type": "object",
        "properties": {
          "user_message": {"type": "string", "description": "The user's input question."},
          "embedding_provider": {"type": "string", "enum": ["openai"], "default": "openai", "description": "The embedding provider to use."}
        },
        "required": ["user_message"]
        }
      }
    }],
    model="gpt-4-turbo-preview",
    file_ids=[file.id]
)
print(my_assistant)


# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")
