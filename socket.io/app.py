import json
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from flask import render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

connected_clients = {}

@app.route('/', methods=['GET'])
def handle_root():
    return render_template('index.html')

@app.route('/push', methods=['GET'])
def handle_push():
    return json.dumps(connected_clients)

@app.route('/push/<client_id>', methods=['GET'])
def handle_push_message(client_id):
    print(request.args.to_dict())
    if client_id not in connected_clients:
        raise Exception('Client is offline')
    data = request.args.to_dict()
    message = data['message']
    print('Send message to: ' + client_id)
    send(message, room=client_id)

@socketio.on('connect')
def handle_connect():
    connected_clients[request.sid] = request.sid
    print('received connect: ' + str(request.sid))

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_clients[request.sid]:
        del connected_clients[request.sid]
    print('received disconnect: ' + str(request.sid))

@socketio.on('echo')
def handle_echo(data):
    print('received echo: ' + str(data))

@socketio.on('chat message')
def handle_chat_message(data):
    print('received chat message: ' + str(data))

if __name__ == '__main__':
    socketio.run(app)
