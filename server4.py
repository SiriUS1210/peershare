from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import base64


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Set maximum payload size to 100MB
socketio = SocketIO(app, cors_allowed_origins='*')

# Dictionary to hold client names
client_names = {}

# Function to handle a client connection
@socketio.on('connect')
def handle_connect():
    emit('message', {'content': 'Enter your name:', 'type': 'info'})


@socketio.on('name')
def handle_name(name):
    client_names[request.sid] = name
    emit('message', {'content': f'{name} has joined the chat.', 'type': 'info'}, broadcast=True)
    emit('message', {'content': 'Welcome to the chat!', 'type': 'info'}, broadcast=True)
    emit('message', {'content': 'You can now start chatting.', 'type': 'info'})
    emit('message', {'content': '--------------------------------', 'type': 'info'})


@socketio.on('message')
def handle_message(message):
    sender_name = client_names[request.sid]

    if isinstance(message, dict) and message.get('type') == 'file':
        file_name = message.get('name')
        file_content = message.get('content')
        emit('file', {
            'sender_name': sender_name,
            'file_name': file_name,
            'file_content': file_content,
        }, broadcast=True, include_self=False)
    else:
        emit('message', {'content': f'{sender_name}: {message}', 'type': 'message'}, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    sender_name = client_names.pop(request.sid, None)
    if sender_name:
        emit('message', {'content': f'{sender_name} has left the chat.', 'type': 'info'}, broadcast=True)


@app.route('/')
def index():
    max_file_size = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)  # Convert max payload size to MB
    return render_template('index.html', max_file_size=max_file_size)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9999)
