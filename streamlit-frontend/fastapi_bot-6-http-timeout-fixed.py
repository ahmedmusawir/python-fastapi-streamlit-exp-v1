import streamlit as st
import asyncio
import httpx
import json

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat"

# Initialize chat log as a session state variable
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Function to send user input and receive AI response
async def chat_with_gpt(user_input):
    async with httpx.AsyncClient(timeout=None) as client:  # Disable timeout
        try:
            async with client.stream("POST", API_URL, json={"user_input": user_input}) as response:
                if response.status_code == 200:
                    full_response = ""
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        async for chunk in response.aiter_lines():
                            if chunk:
                                chunk_json = json.loads(chunk)
                                content = chunk_json.get("response", "").strip()
                                full_response += content
                                message_placeholder.markdown(full_response + "▌")
                    st.session_state['messages'].append({"role": "assistant", "content": full_response})
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
