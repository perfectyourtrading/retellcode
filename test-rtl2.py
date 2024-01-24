#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_sock import Sock
import requests
import websocket
import threading
import json

app = Flask(__name__)
sock = Sock(app)

api_key = '*'
agent_id = '*'
RETELL_WS_URL = f'wss://api.re-tell.ai/create-web-call?api_key={api_key}&agent_id={agent_id}'


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
def vonage_socket(ws):
    def on_open_retell(ws_retell):
        print("WebSocket connection to Re-Tell opened")
        ws_retell.send(json.dumps({'status': 'READY'}))

    def on_message_retell(ws_retell, message):
        # Handle messages from Re-Tell here
        pass

    def on_error_retell(ws_retell, error):
        print("WebSocket error with Re-Tell:", error)

    def on_close_retell(ws_retell, close_status_code, close_msg):
        print("WebSocket with Re-Tell closed:", close_status_code, close_msg)

    ws_retell = websocket.WebSocketApp(RETELL_WS_URL,
                                       on_open=on_open_retell,
                                       on_message=on_message_retell,
                                       on_error=on_error_retell,
                                       on_close=on_close_retell)

    ws_thread = threading.Thread(target=ws_retell.run_forever)
    ws_thread.start()

    try:
        while True:
            data = ws.receive()
            if data:
                # Forward data received from Vonage to Re-Tell
                ws_retell.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
    except websocket.WebSocketConnectionClosedException:
        pass
    finally:
        ws_retell.close()

if __name__ == "__main__":
    app.run(port=5000)



# @sock.route('/socket')
# def vonage_socket(ws):
#     ws_retell = websocket.WebSocketApp(RETELL_WS_URL,
#                                        on_open=on_open,
#                                        on_message=on_message,
#                                        on_error=on_error,
#                                        on_close=on_close)
#     ws_thread = threading.Thread(target=ws_retell.run_forever)
#     ws_thread.start()

#     try:
#         while True:
#             data = ws.receive()
#             if data:
#                 # Forward data received from Vonage to Re-Tell
#                 ws_retell.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
#     except websocket.WebSocketConnectionClosedException:
#         pass
#     finally:
#         ws_retell.close()

# if __name__ == "__main__":
#     app.run(port=5000)

