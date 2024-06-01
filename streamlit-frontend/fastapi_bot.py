import streamlit as st
import httpx
import json
import asyncio

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat"

# Function to fetch streaming data from the backend
def fetch_stream_data(user_input):
    async def fetch():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", API_URL, json={"user_input": user_input}) as response:
                async for chunk in response.aiter_lines():
                    if chunk:
                        chunk_json = json.loads(chunk)
                        content = chunk_json.get("response", "").strip() + " "
                        yield content

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for item in loop.run_until_complete(fetch()):
        yield item

# Streamlit UI
st.title("Streamlit Chat with GPT-4")

user_input = st.text_input("You:")
if st.button("Send") and user_input:
    st.session_state['messages'] = []  # Clear previous messages
    st.session_state['messages'].append({"role": "user", "content": user_input})
    st.write_stream(fetch_stream_data(user_input))

    # Display the chat log
    for message in st.session_state['messages']:
        st.write(f"**{message['role'].capitalize()}:** {message['content']}")
