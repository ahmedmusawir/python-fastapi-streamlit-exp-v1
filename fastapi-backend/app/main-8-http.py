from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
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

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_input = data.get("user_input")
        logger.info(f"Received user input: {user_input}")

        chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
        chat_log.append({'role': 'user', 'content': user_input})

        response = openai.chat.completions.create(
            model='gpt-4',
            messages=chat_log,
            temperature=0.6,
        )
        logger.info("OpenAI API call successful.")

        ai_response = response.choices[0].message.content
        chat_log.append({'role': 'assistant', 'content': ai_response})
        logger.info(f"Generated AI response: {ai_response}")

        return JSONResponse(content={"response": ai_response})
    except Exception as e:
        logger.error(f"Error during OpenAI call: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
