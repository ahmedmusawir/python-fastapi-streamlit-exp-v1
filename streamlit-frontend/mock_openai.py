import openai
import streamlit as st
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to stream data from OpenAI
def stream_openai_response(prompt):
    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': prompt}]

    # Make streaming API call
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=chat_log,
        temperature=0.6,
        stream=True
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            content = chunk.choices[0].delta.content
            if content:
                yield content + " "
                time.sleep(0.05)  # Simulate delay for streaming effect

# Streamlit UI
st.title("Streamlit Chat with GPT-4")

prompt = st.text_input("You:")
if st.button("Send") and prompt:
    st.session_state['messages'] = []  # Clear previous messages
    st.session_state['messages'].append({"role": "user", "content": prompt})
    print(stream_openai_response(prompt))
    st.write_stream(stream_openai_response(prompt))

    # Display the chat log
    for message in st.session_state['messages']:
        st.write(f"**{message['role'].capitalize()}:** {message['content']}")
