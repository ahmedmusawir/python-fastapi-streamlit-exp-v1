from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import json

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

# Home page
@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("user_input")
    logger.info(f"Received user input: {user_input}")

    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    chat_log.append({'role': 'user', 'content': user_input})

    # Make streaming API call
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=chat_log,
        temperature=0.6,
        stream=True
    )
    logger.info("OpenAI API call successful.")

    async def generate():
        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                if content:
                    logger.info(f"Received chunk: {content}")
                    yield json.dumps({"response": content}) + "\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
