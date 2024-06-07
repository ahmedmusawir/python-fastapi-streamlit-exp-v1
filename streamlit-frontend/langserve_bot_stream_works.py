import streamlit as st
import asyncio
import httpx
import json

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat/stream"

# Initialize chat log as a session state variable
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to send user input and receive AI response
async def chat_with_gpt(user_input):
    async with httpx.AsyncClient(timeout=None) as client:  # Disable timeout
        try:
            async with client.stream("POST", API_URL, json={"input": {"input": user_input}}) as response:
                if response.status_code == 200:
                    full_response = ""
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        async for line in response.aiter_lines():
                            if line:
                                # Skip non-data events
                                if line.startswith("data: "):
                                    chunk_json = json.loads(line[6:])  # Skip the "data: " part
                                    output_content = chunk_json.get("content", "").strip() + ' '  # Extract the content
                                    full_response += output_content
                                    message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response.strip())  # Remove trailing space
                    st.session_state['messages'].append({"role": "assistant", "content": full_response.strip()})
                else:
                    error_message = await response.aread()
                    st.error(f"Error: {error_message}")
        except httpx.ReadTimeout:
            st.error("ReadTimeout: The request took too long to complete.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Streamlit UI
st.title("Streamlit Chat with GPT-4")
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

    asyncio.run(chat_with_gpt(prompt))
