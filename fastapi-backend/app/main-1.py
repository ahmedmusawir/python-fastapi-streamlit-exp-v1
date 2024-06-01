from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from openai import OpenAI

# Set up OpenAI client
client = OpenAI(api_key='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')

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
    while True:
        data = await websocket.receive_text()

        # Create OpenAI response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0301",  # Use the latest model if available
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data}
            ],
            stream=True
        )

        # Stream response and send to WebSocket
        for message in response:
            await websocket.send_text(message['choices'][0]['delta'].get('content', ''))

