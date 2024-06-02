from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]

    try:
        while True:
            user_input = await websocket.receive_text()
            chat_log.append({'role': 'user', 'content': user_input})
            logger.info(f"User Input: {user_input}")

            try:
                async def on_new_token(token: str):
                    await websocket.send_text(token)

                model = ChatOpenAI(
                    openai_api_key=os.getenv('OPENAI_API_KEY'),
                    temperature=0.6,
                    model_name='gpt-4',
                    streaming=True,
                    callbacks=[{
                        "handle_llm_new_token": on_new_token
                    }]
                )

                response = await model.agenerate([
                    SystemMessage(content="You are a helpful assistant."),
                    HumanMessage(content=user_input)
                ])

                ai_response = ''.join([chunk.text for chunk in response])
                chat_log.append({'role': 'assistant', 'content': ai_response})

            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
                break
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
