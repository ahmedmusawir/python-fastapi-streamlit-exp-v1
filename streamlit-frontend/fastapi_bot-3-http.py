import streamlit as st
import requests

# Set the FastAPI server URL
API_URL = "http://localhost:8000/chat"

# Initialize chat log
chat_log = []

# Function to send user input and receive AI response
def chat_with_gpt(user_input):
    response = requests.post(API_URL, json={"user_input": user_input})
    if response.status_code == 200:
        data = response.json()
        if "response" in data:
            chat_log.append(f"AI: {data['response']}")
        elif "error" in data:
            st.error(data["error"])
    else:
        st.error(f"Error: {response.status_code}")

# Streamlit UI
st.title("Streamlit Chat with GPT-4")
st.subheader("Type your message below and press Enter")

# Text input for user message
user_input = st.text_input("You:", key="user_input")

# Button to send message
if st.button("Send"):
    if user_input:
        chat_log.append(f"You: {user_input}")
        chat_with_gpt(user_input)

# Display chat log
for message in chat_log:
    st.write(message)
