import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
import functions_framework
from twilio.twiml.messaging_response import MessagingResponse
import openai
from openai import OpenAI

# Initialize Firebase Admin SDK
firebase_admin.initialize_app()

# OpenAI setup
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Assuming the assistant is already created and its ID is known
ASSISTANT_ID = "asst_OQTVP3y0yBqzsUtyOl5HmiHY"

@functions_framework.http
def handle_sms(request):
    print(request.method)
    # Ensure the request is from Twilio
    if request.method != 'POST':
        return "Only POST requests are accepted", 405

    request_form = request.form
    from_number = request_form.get('From')
    sms_body = request_form.get('Body')
    db = firestore.client()
    client = OpenAI()

    print(f"Received message from {from_number}: {sms_body}")
    print(f"Twilio request form: {request_form}")
    print("before try")
    try:
        # Retrieve or create a user document in Firestore
        users_ref = db.collection('Users')
        user_doc = users_ref.document(from_number).get()

        print("after user_doc")
        if user_doc.exists:
            print("user_doc exists")
            user_data = user_doc.to_dict()
            thread_id = user_data['open_ai_assistant_thread_id']
        else:
            print("user_doc does not exist")
            # If the user is new, create a new thread
            thread = client.beta.threads.create()
            thread_id = thread.id
            users_ref.document(from_number).set({
                'phone_number': from_number,
                'created_tsp': firestore.SERVER_TIMESTAMP,
                'open_ai_assistant_thread_id': thread_id
            })

        print("before openai.Message.create")
        # Add the user's message to the thread

        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=sms_body
        )
        print("after openai.Message.create")

        # Run the assistant to get a response
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Assuming the response is synchronous and the last message is from the assistant
        messages = openai.Message.list(thread_id=thread_id)
        assistant_response = messages.data[-1].content if messages.data else "Sorry, I couldn't process your request."

        # Log the message in Firestore under "Messages"
        messages_ref = db.collection('Messages')
        messages_ref.add({
            'to_phone_number': os.environ.get("TWILIO_PHONE_NUMBER"),
            'from_phone_number': from_number,
            'content': sms_body,  # Log the user's message
            'sent_tsp': firestore.SERVER_TIMESTAMP
        })

    except Exception as e:
        # Error handling: Log the exception in Firestore
        error_log_ref = db.collection('ErrorLogs')
        error_log_ref.add({
            'error': str(e),
            'from_phone_number': from_number,
            'to_phone_number': os.environ.get("TWILIO_PHONE_NUMBER", "Unknown"),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Prepare an error message response
        assistant_response = "We're sorry, there was an error processing your request."

    # Prepare the Twilio SMS response with either the assistant's response or an error message
    twiml_response = MessagingResponse()
    twiml_response.message(assistant_response)

    return str(twiml_response), 200