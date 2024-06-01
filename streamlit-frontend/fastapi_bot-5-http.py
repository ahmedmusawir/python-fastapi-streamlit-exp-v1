import openai
import streamlit as st

# Custom Styles Defined
custom_css = """
<style>
    .stDeployButton {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        background-color: #404000;  /* Dark ash background */
        color: white;              /* White text */
    }

     [data-testid="stSidebar"] .stTextInput > label {
        color: white;
    }

    [data-testid="stHeading"] h1 {
        color: white;
    }

    [data-testid="stNotification"] {
        background-color: gray;
        color: white;
    }
    
    
</style>
"""
# Setting up custom CSS for Streamlit App
st.markdown(custom_css, unsafe_allow_html=True)

# Setting up the Sidebar
with st.sidebar:
    st.title('MooseBot OpenAI')

    # Checking and Accepting the OpenAI API Key

    openai.api_key = st.text_input('Enter OpenAI API token:', type='password')

    if not (openai.api_key.startswith('sk') and len(openai.api_key) == 51):
        st.warning('Please enter your credentials!', icon='⚠️')
    
    else:
        st.success('Proceed to your chatbot prompting!', icon='👌')

# Setting up messages to the session variables
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Create messages list 
        messages_list = []

        for m in st.session_state.messages:
            message_dict = {"role": m["role"], "content": m["content"]}
            messages_list.append(message_dict)

        # Call OpenAI API
        for response in openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages_list,
            stream=True
        ):
        # Directly access 'content' from 'message' in 'choices'
            # st.write(response)
            if response.choices and response.choices[0].delta:
                content = response.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    

