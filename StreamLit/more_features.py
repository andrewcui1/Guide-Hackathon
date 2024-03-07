"""Streamlit app with decent features and an inference function interacting with the model."""

import streamlit as st
import time
import torch

# This is the "model" effectively
def model():
    pass

# Inference function
# TODO: (modify this for our code)
def generate_response(model,input_text):
    data = torch.tensor(encode(input_text), dtype=torch.long, device=device)
    data = data.reshape(len(input_text), 1)
    generated_tokens = model.generate(data, max_new_tokens=200)[0].tolist()
    response_text = decode(generated_tokens)
    return response_text

# Define your custom cursor here
CUSTOM_CURSOR = "▐"

# Main Streamlit app
def main():
    st.title("Chatting with Guide")

    # Initialize chat history using st.session_state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("User:")

    if st.button("Send"):
        if user_input:
            # Display user input
            st.session_state.chat_history.append(("user", user_input))

            # Generate and display the chatbot response step by step with a cursor
            bot_response = generate_response(model, user_input)

            # Display the user input immediately
            st.markdown(f'<div style="text-align: left; color: blue;">You: {user_input}</div>', unsafe_allow_html=True)

            # Display the bot's response with the typing effect
            bot_cursor_text = st.empty()
            for i in range(len(bot_response) + 1):
                bot_cursor_text.markdown(f'<div style="text-align: right; color: green;">Bot: {bot_response[:i]}{CUSTOM_CURSOR}</div>', unsafe_allow_html=True)
                time.sleep(0.05)  # Adjust the sleep time to control the typing speed

            # Remove the cursor for the final display
            bot_cursor_text.markdown(f'<div style="text-align: right; color: green;">Bot: {bot_response}</div>', unsafe_allow_html=True)

            # Append the full bot response to the chat history
            st.session_state.chat_history.append(("bot", bot_response))

    # Display the chat history with left and right alignment
    for speaker, message in st.session_state.chat_history:
        if speaker == "user":
            st.markdown(f'<div style="text-align: left; color: blue;">You: {message}</div>', unsafe_allow_html=True)
        elif speaker == "bot":
            # Display the bot's response without the cursor
            st.markdown(f'<div style="text-align: right; color: red;">Bot 😊: {message}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # Run the Streamlit app
    main()
