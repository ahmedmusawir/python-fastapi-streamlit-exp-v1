from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import json

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
            response = openai.chat.completions.create(
                model='gpt-4',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        ai_response += content
                        await websocket.send_text(json.dumps({"response": content}))

            chat_log.append({'role': 'assistant', 'content': ai_response})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        await websocket.close()
