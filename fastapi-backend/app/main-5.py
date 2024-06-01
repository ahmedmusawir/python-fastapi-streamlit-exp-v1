from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})

        # Send the user input back to the frontend to display it
        await websocket.send_text(f"User: {user_input}")

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
            await websocket.send_text(f'Error: {str(e)}')
            break