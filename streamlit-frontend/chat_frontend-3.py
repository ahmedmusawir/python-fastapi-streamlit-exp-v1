import streamlit as st
import httpx
import json
import asyncio

# Function to fetch streaming data from FastAPI
async def fetch_stream_data(prompt):
    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("POST", "http://127.0.0.1:8000/chat", json={"user_input": prompt}, timeout=60.0) as response:
                async for chunk in response.aiter_text():
                    if chunk:
                        yield json.loads(chunk)["response"]
        except httpx.ReadTimeout:
            st.error("The request timed out. Please try again.")

def fetch_stream_data_sync(prompt):
    async def stream_data():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("POST", "http://127.0.0.1:8000/chat", json={"user_input": prompt}, timeout=60.0) as response:
                    async for chunk in response.aiter_text():
                        if chunk:
                            yield json.loads(chunk)["response"]
            except httpx.ReadTimeout:
                st.error("The request timed out. Please try again.")

    async def async_generator_wrapper():
        async for item in stream_data():
            yield item

    def sync_generator():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        iterator = async_generator_wrapper()
        while True:
            try:
                yield loop.run_until_complete(iterator.__anext__())
            except StopAsyncIteration:
                break
        loop.close()

    return sync_generator()

# Streamlit UI
st.title("Streamlit Chat with GPT-4 via FastAPI")

prompt = st.text_input("You:")
if st.button("Send") and prompt:
    st.session_state['messages'] = []  # Clear previous messages
    st.session_state['messages'].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream AI response
    with st.chat_message("assistant"):
        st.write_stream(fetch_stream_data_sync(prompt))

    st.session_state['messages'].append({"role": "assistant", "content": "Streaming..."})

    # Display the chat log
    for message in st.session_state['messages']:
        st.write(f"**{message['role'].capitalize()}:** {message['content']}")
