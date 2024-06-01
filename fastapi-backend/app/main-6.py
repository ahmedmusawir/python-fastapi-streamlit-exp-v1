from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = FastAPI()

# CORS settings for allowing requests from Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    
    try:
        while True:
            user_input = await websocket.receive_text()
            chat_log.append({'role': 'user', 'content': user_input})

            try:
                response = openai.chat.completions.create(
                    model='gpt-4',
                    messages=chat_log,
                    temperature=0.6,
                    stream=True
                )

                ai_response = ''
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        ai_response += chunk.choices[0].delta.content
                        await websocket.send_text(chunk.choices[0].delta.content)
                chat_log.append({'role': 'assistant', 'content': ai_response})

            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
                break
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        await websocket.close()
