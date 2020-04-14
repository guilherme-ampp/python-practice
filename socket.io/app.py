import json
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import render_template, request
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

connected_clients = {}

global stop_event
stop_event = threading.Event()

def long_running_task():
    for _ in range(1000):
        socketio.emit('count', json.dumps({'count': _}), namespace='/count')
        socketio.sleep(1)
        print('Counting', _)
        if stop_event.is_set():
            break


@app.route('/', methods=['GET'])
def handle_root():
    return render_template('index.html')


@app.route('/push', methods=['GET'])
def handle_push():
    return json.dumps([str(v) for k, v in connected_clients.items()])


@app.route('/push/<client_id>', methods=['GET'])
def handle_push_message(client_id):
    if client_id not in connected_clients.values():
        raise Exception('Client is offline')
    message = request.args.to_dict()['message']
    print('Send [{}] message[{}]'.format(client_id, message))
    socketio.emit('chat message', message, room=client_id, namespace='/chat')
    return 'OK'


@socketio.on('connect', namespace='/chat')
def handle_chat_connect():
    print('Received connect: ' + str(request.sid))


@socketio.on('disconnect', namespace='/chat')
def handle_chat_disconnect():
    if request.sid in connected_clients:
        username = connected_clients[request.sid]
        leave_room(username)
        del connected_clients[request.sid]
        socketio.emit('chat message', '{} has left the chat'.format(username), 
                      namespace='/chat', broadcast=True)
    print('Received disconnect: ' + str(request.sid))


@socketio.on('chat join', namespace='/chat')
def handle_chat_join(data):
    print('Joined chat: ' + str(data))
    if data and 'username' in data:
        username = data['username']
        connected_clients[request.sid] = username
        join_room(username)
    
        socketio.emit('chat message', '{} joined the chat'.format(username), 
                      namespace='/chat', broadcast=True)


@socketio.on('chat message', namespace='/chat')
def handle_chat_message(data):
    print('Received chat message: ' + str(data))
    if data:
        socketio.emit('chat message', "{}: {}".format(data['username'], data['message']),
                      namespace='/chat', broadcast=True)


@socketio.on('connect', namespace='/count')
def handle_counter_connect():
    if not connected_clients:
        global stop_event
        stop_event = threading.Event()
        t = socketio.start_background_task(long_running_task)
        print('Listening to the counter: {} on Thread[{}]'.format(request.sid, t))
    else:
        print('Listening to the counter: {}'.format(request.sid))
    connected_clients[request.sid] = request.sid


@socketio.on('disconnect', namespace='/count')
def handle_counter_disconnect():
    if request.sid in connected_clients:
        del connected_clients[request.sid]
    if not connected_clients:
        stop_event.set()
    print('Stopped listening to the counter: ' + str(request.sid))


@app.teardown_appcontext
def _teardown(*args, **kwargs):
    yield
    stop_event.set()

if __name__ == '__main__':
    socketio.run(app)
