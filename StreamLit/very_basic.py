import streamlit as st
import requests

# Define the URL of model endpoint
MODEL_URL = 'http://vance-aws-endpoint-url.com'

def get_model_response(input_text):
    # Make a POST request to model endpoint with the input text
    response = requests.post(MODEL_URL, json={'input': input_text})

    # Check the status of the request
    if response.status_code == 200:
        # If the request was successful, return the model's response
        return response.json()['response']
    else:
        # If the request was not successful, return an error message
        return 'Error: Unable to get response from model'

def main():
    st.title('Chat with our Model')

    # Create a text input for the user's message
    user_input = st.text_input('Enter your message:')

    # When the user presses the 'Send' button, get the model's response
    if st.button('Send'):
        model_response = get_model_response(user_input)
        st.write('Model\'s Response:', model_response)

if __name__ == '__main__':
    main()
