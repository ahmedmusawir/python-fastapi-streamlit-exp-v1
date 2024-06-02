from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# FastAPI app and templates
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_input = await websocket.receive_text()
            logger.info(f"Received user input: {user_input}")

            chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': user_input}]

            response = openai.chat.completions.create(
                model='gpt-4',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )
            logger.info("OpenAI API call successful.")

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    logger.info(f"Sending chunk: {content}")
                    await websocket.send_text(content)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        await websocket.close()
        logger.info("WebSocket disconnected")
