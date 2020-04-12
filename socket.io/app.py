import json
import service
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask import render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

connected_clients = {}
backend_service = None


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
    print('received connect: ' + str(request.sid))


@socketio.on('disconnect', namespace='/chat')
def handle_chat_disconnect():
    if request.sid in connected_clients:
        username = connected_clients[request.sid]
        leave_room(username)
        del connected_clients[request.sid]
        socketio.emit('chat message', '{} has left the chat'.format(username), 
                      namespace='/chat', broadcast=True)
    print('received disconnect: ' + str(request.sid))


@socketio.on('chat join', namespace='/chat')
def handle_chat_join(data):
    print('joined chat: ' + str(data))
    if data and 'username' in data:
        username = data['username']
        connected_clients[request.sid] = username
        join_room(username)
    
        socketio.emit('chat message', '{} joined the chat'.format(username), 
                      namespace='/chat', broadcast=True)


@socketio.on('chat message', namespace='/chat')
def handle_chat_message(data):
    print('received chat message: ' + str(data))
    if data:
        socketio.emit('chat message', "{}: {}".format(data['username'], data['message']),
                      namespace='/chat', broadcast=True)


@socketio.on('connect', namespace='/counter')
def handle_counter_connect():
    print('listening to the counter: ' + str(request.sid))


@socketio.on('disconnect', namespace='/counter')
def handle_counter_disconnect():
    print('stopped listening to the counter: ' + str(request.sid))


@socketio.on('echo', namespace='/chat')
def handle_echo(data):
    print('received echo: ' + str(data))


@app.teardown_appcontext
def _teardown(*args, **kwargs):
    yield

    backend_service.stop()

if __name__ == '__main__':
    def _callback_counter(json_data):
        print('emit count:', json_data)
        socketio.emit('count', json_data, namespace='/counter',
                      broadcast=True)

    backend_service = service.LongRunningTask(_callback_counter)
    socketio.run(app)
