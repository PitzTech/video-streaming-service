from flask_socketio import SocketIO

class ChatHandler:
    def __init__(self, socketio: SocketIO, logger):
        self.socketio = socketio
        self.logger = logger
        self.socketio.on_event('send_message', self.handle_message)

    def handle_message(self, data):
        self.logger.info(f"Mensagem recebida de {data['user_id']}: {data['message']}")
        self.socketio.emit('chat_message', data)
