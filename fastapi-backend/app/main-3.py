from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

@app.get("/")
async def get():
    return HTMLResponse("""
        <html>
        <head>
            <title>OpenAI WebSocket Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='messages'>
            </ul>
            <script>
                var ws = new WebSocket("ws://localhost:8000/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                function sendMessage(event) {
                    var input = document.getElementById("messageText")
                    ws.send(input.value)
                    input.value = ''
                    event.preventDefault()
                }
            </script>
        </body>
        </html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_log = [{'role': 'system', 'content': 'You are a helpful assistant.'}]
    
    while True:
        data = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': data})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ''
            for chunk in response:
                if chunk['choices'][0]['delta'].get('content') is not None:
                    ai_response += chunk['choices'][0]['delta']['content']
                    await websocket.send_text(chunk['choices'][0]['delta']['content'])
            chat_log.append({'role': 'assistant', 'content': ai_response})

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break
