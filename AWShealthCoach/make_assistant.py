from litellm import completion
import os
from typing import List, Dict

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

# my_assistant = client.beta.assistants.create(
#     instructions=instructions_str,
#     name="Guide v3",
#     tools=[{"type": "retrieval"}],
#     model="gpt-4-turbo-preview",
#     file_ids=[file.id]
# )
# print(my_assistant)


# initialize_app()
#
#
# @https_fn.on_request()
# def on_request_example(req: https_fn.Request) -> https_fn.Response:
#     return https_fn.Response("Hello world!")
