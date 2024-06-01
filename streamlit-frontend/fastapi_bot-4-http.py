import streamlit as st
import asyncio
import httpx

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat"

# Initialize chat log as a session state variable
if 'chat_log' not in st.session_state:
    st.session_state['chat_log'] = []

# Function to send user input and receive AI response
async def chat_with_gpt(user_input):
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", API_URL, json={"user_input": user_input}) as response:
            if response.status_code == 200:
                async for chunk in response.aiter_text():
                    if chunk:
                        st.session_state['chat_log'].append(f"AI: {chunk.strip()}")
                        st.rerun()  # Use st.rerun to re-render the UI
            else:
                error_message = await response.aread()
                st.error(f"Error: {error_message}")

# Streamlit UI
st.title("Streamlit Chat with GPT-4")
st.subheader("Type your message below and press Enter")

# Text input for user message
user_input = st.text_input("You:", key="user_input")

# Button to send message
if st.button("Send"):
    if user_input:
        st.session_state['chat_log'].append(f"You: {user_input}")
        asyncio.run(chat_with_gpt(user_input))

# Display chat log
for message in st.session_state['chat_log']:
    st.write(message)
