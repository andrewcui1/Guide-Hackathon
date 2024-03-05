import os
import time
import boto3
from urllib.parse import parse_qs
from boto3.dynamodb.conditions import Key
from twilio.twiml.messaging_response import MessagingResponse
import openai
from dotenv import load_dotenv

load_dotenv() 

# Initialize OpenAI and DynamoDB clients
openai.api_key = os.environ.get("OPENAI_API_KEY")
print(f"OpenAI API Key: {openai.api_key}")
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
print(f"DynamoDB: {dynamodb}")
users_table = dynamodb.Table('HealthCoachUsers') # Adjust table name as needed
print(f"Users Table: {users_table}")
messages_table = dynamodb.Table('HealthCoachMessages') # Adjust table name as needed
print(f"Messages Table: {messages_table}")
assisstant_id = "asst_btzioFyCYSgWK2mVpVvJukOF"
print(f"Assistant ID: {assisstant_id}")

twilio_number = "+15126018744"
print(f"Twilio number: {twilio_number}")

def lambda_handler(event, context):
    print(event['httpMethod'])
    # Ensure the request is from Twilio
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'body': 'Only POST requests are accepted'
        }
    
    request_body_str = event.get('body', '')  # Get the body as a string
    print(f"Request body string: {request_body_str}")
    request_body = parse_qs(request_body_str)  # Parse the string into a dictionary
    print(f"Request body: {request_body}")
    # Accessing parameters safely
    from_number = request_body.get('From', [''])[0]  # parse_qs wraps values in lists
    print(f"From number: {from_number}")
    sms_body = request_body.get('Body', [''])[0]
    print(f"SMS body: {sms_body}")

    # Log the message FROM user 
    messages_table.put_item(Item={
        'from_phone_number': from_number,
        'content': sms_body
    })

    client = openai.OpenAI()
    print(f"OpenAI client: {client}")

    try:
        print("Before user_response")
        # Check if user exists in DynamoDB
        user_response = users_table.get_item(Key={'phone_number': from_number})
        print(f"User response: {user_response}")
        user_exists = 'Item' in user_response
        print(f"User exists: {user_exists}")

        if user_exists:
            print("User exists")
            user_data = user_response['Item']
            print(f"User data: {user_data}")
            thread_id = user_data['open_ai_assistant_thread_id']
            print(f"Thread ID: {thread_id}")
        else:
            print("User does not exist")
            # If the user is new, create a new thread and save to DynamoDB
            thread = client.beta.threads.create()
            print(f"Thread: {thread}")
            thread_id = thread.id
            print(f"Thread ID: {thread_id}")
            users_table.put_item(Item={
                'phone_number': from_number,
                'open_ai_assistant_thread_id': thread_id,
                'created_tsp': int(time.time())
            })

        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=sms_body
        )
        print("after openai.Message.create")
        print(f"Message: {message}")
        print(f"Message content: {message.content}")

        # Run the assistant to get a response
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assisstant_id
        )
        print("after client.beta.threads.runs.create")

        print(f"Run: {run}")

        # Introduce a delay to allow time for the assistant's response to be generated
        time.sleep(20)  # Adjust the sleep time as needed


        messages = client.beta.threads.messages.list(thread_id=thread_id)
        print(f"Messages: {messages}")

        response_text = "No assistant message found."

        # Iterate through the messages in reverse to find the first assistant message
        for message in messages.data:
            print("in for")
            print(message)
            if message.role == 'assistant' and message.content:
                print("in if")
                # Assuming there is at least one content item and it has a 'text' field
                content_item = message.content[0]
                print(f"Content item: {content_item}")
                response_text = content_item.text.value
                break

        """
        # Assuming the response is synchronous and the last message is from the assistant
        print(f"after openai.Message.list - {messages}")
        # print(f"after openai.Message.list - {messages}")
        assistant_response = messages.data[0].content if messages.data else "Sorry, I couldn't process your request."
        print(f"Assistant response: {assistant_response}")
        response_text = assistant_response[0]['text']['value'] if assistant_response and 'text' in assistant_response[0] else "Sorry, I couldn't process your request."
        print("ASSISTANT", assistant_response[0])
        print(f"assistant_response - {response_text}")  

        
        assistant_response = "Sorry, I couldn't process your request."

        # List messages in the thread
        messages_response = client.beta.threads.messages.list(thread_id=thread_id)
        # Assuming messages_response.data contains the messages, iterate in reverse to find the latest assistant message
        for message in reversed(messages_response.data):
            # Check if the message is from the assistant and has content
            if message.role == "assistant" and message.content:
                # Assuming the content is a list of components (text, etc.)
                for content in message.content:
                    if isinstance(content, dict) and "text" in content:
                        # Return the text value of the content
                        assistant_response = content["text"]
        """

        # Log the message in DynamoDB
        messages_table.put_item(Item={
            'from_phone_number': twilio_number,
            'content': response_text
        })

    except Exception as e:
        print(f"in except block")
        print(f"Error: {e}")
        response_text = "We're sorry, there was an error processing your request."

    print(f"Response text: {response_text}")
    # Prepare the Twilio SMS response
    twiml_response = MessagingResponse()
    print(f"Twilio response: {twiml_response}")
    twiml_response.message(response_text)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/xml'},
        'body': str(twiml_response)
    }
