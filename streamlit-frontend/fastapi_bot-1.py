import streamlit as st
import asyncio
import websockets

# Set the WebSocket server URL
WEBSOCKET_URL = "ws://localhost:8000/ws"

# Initialize chat log
chat_log = []

# Function to connect to WebSocket and send/receive messages
async def chat_with_gpt(user_input):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        await websocket.send(user_input)
        async for message in websocket:
            if message.startswith("Error:"):
                st.error(message)
                break
            chat_log.append(message)
            # Rerun Streamlit to update the chat log
            st.experimental_rerun()

# Streamlit UI
st.title("Streamlit Chat with GPT-4")
st.subheader("Type your message below and press Enter")

# Text input for user message
user_input = st.text_input("You:", key="user_input")

# Button to send message
if st.button("Send"):
    if user_input:
        chat_log.append(f"You: {user_input}")
        asyncio.run(chat_with_gpt(user_input))

# Display chat log
for message in chat_log:
    st.write(message)