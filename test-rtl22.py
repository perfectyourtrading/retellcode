#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sock import Sock
import requests
import websocket
import threading
import json
import retellclient
from retellclient.models import operations, components

app = Flask(__name__)
sock = Sock(app)

api_key = '*'
agent_id = '*'
client = retellclient.RetellClient(api_key='4fd9cbbe-6883-4d3a-ad27-bb55ee06129f')
# RETELL_WS_URL = f'wss://api.re-tell.ai/create-web-call?api_key={api_key}&agent_id={agent_id}'


@app.route("/webhooks/answer")
def answer_call():
    ncco = [
        {
            "action": "talk",
            "text": "Connecting you to our service, please wait.",
        },
        {
            "action": "connect",
            "from": "Vonage",
            "endpoint": [
                {
                    "type": "websocket",
                    "uri": f"wss://{request.host}/socket",
                    "content-type": "audio/l16;rate=16000",
                }
            ],
        },
    ]
    return jsonify(ncco)

@app.route("/webhooks/events", methods=["POST"])
def events():
    return "200"

def on_message(ws, message):
    # Handle incoming messages from Re-Tell and forward them
    # This part depends on the specifics of how you want to handle Re-Tell's responses
    def run(*args):
        # Send a 'READY' message or similar if required by the Re-Tell API
        ws.send(json.dumps({'status': 'READY'}))
        # Other code for on_open, if any
    # Indentation for run function ends here

    thread = threading.Thread(target=run)
    thread.start()
# Indentation for on_open function ends here
    # Handle incoming messages from Re-Tell and forward them
    # This part depends on the specifics of how you want to handle Re-Tell's responses

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    def run(*args):
        # Send a 'READY' message or similar if required by the Re-Tell API
        ws.send(json.dumps({'status': 'READY'}))
    thread = threading.Thread(target=run)
    thread.start()


@sock.route('/socket')
async def setup_live_client():
    params = operations.CreateWebCallParams(
        agent_id='39e3d19cefdf3fb089c1183c325e71d4',
        sample_rate='audio/l16;rate=16000'
    )
    live_client = await client.create_web_call(params=params)

    def on_audio_received(message):
        # play or process audio here
        pass

    def on_error_received(message):
        print("error", message)

    def on_close_received():
        print("websocket closed")
        # cleanup here

    live_client.on("audio", on_audio_received)
    live_client.on("error", on_error_received)
    live_client.on("close", on_close_received)


    try:
        while True:
            data = ws.receive()
            if data:
                # Forward data received from Vonage to Re-Tell
                # ws_retell.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
                await live_client.send(audio_chunk)
    except websocket.WebSocketConnectionClosedException:
        pass
    finally:
        ws_retell.close()

if __name__ == "__main__":
    app.run(port=5000)


