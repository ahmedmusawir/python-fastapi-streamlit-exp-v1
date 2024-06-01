import time
import streamlit as st

# Sample data generator to mimic backend streaming response
def mock_stream_data():
    response_text = """
    Joe Biden, whose full name is Joseph Robinette Biden Jr., is an American politician
    who is serving as the 46th and current president of the United States. He was
    inaugurated in January 2021. Prior to that, he served as vice president under
    President Barack Obama from 2009 to 2017. Biden also represented Delaware in the
    U.S. Senate from 1973 to 2009. He was born on November 20, 1942, in Scranton,
    Pennsylvania.
    """
    for word in response_text.split():
        yield word + " "
        time.sleep(0.1)  # Simulate delay

# Streamlit UI
st.title("Streamlit Streaming Prototype")

if st.button("Stream data"):
    st.write_stream(mock_stream_data)
