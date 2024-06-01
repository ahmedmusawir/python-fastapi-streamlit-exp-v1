from fastapi import WebSocket
from app.services.openai_service import get_openai_response

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = get_openai_response(data)
        await websocket.send_text(response)
