import streamlit as st
import asyncio
import httpx
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat"

# Asynchronous function to fetch data from FastAPI
async def fetch_data(prompt):
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("POST", API_URL, json={"user_input": prompt}) as response:
                if response.status_code == 200:
                    async for chunk in response.aiter_lines():
                        if chunk:
                            chunk_json = json.loads(chunk)
                            content = chunk_json.get("response", "").strip()
                            yield content + " "
        except httpx.ReadTimeout:
            st.error("ReadTimeout: The request took too long to complete.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Synchronous generator wrapper
def stream_fastapi_response(prompt):
    async_gen = fetch_data(prompt)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            chunk = loop.run_until_complete(async_gen.__anext__())
            yield chunk
            time.sleep(0.05)  # Simulate delay for streaming effect
        except StopAsyncIteration:
            break

# Initialize chat log as a session state variable
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Streamlit UI
st.title("Streamlit Chat with FastAPI and GPT-4")
st.subheader("Type your message below and press Enter")

# Display existing chat log
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Text input for user message
if prompt := st.chat_input("You:"):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Placeholder for assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_text = ""

        # Display spinner while waiting for the response
        with st.spinner("Waiting for response..."):
            # Stream the response
            for content in stream_fastapi_response(prompt):
                response_text += content
                message_placeholder.markdown(response_text + "▌")
        
        # Finalize the response text
        message_placeholder.markdown(response_text.strip())

    # Append the response to the chat log
    st.session_state['messages'].append({"role": "assistant", "content": response_text.strip()})
