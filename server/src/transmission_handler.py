import logging
from flask_socketio import SocketIO

class TransmissionHandler:
    def __init__(self, socketio: SocketIO, logger):
        self.socketio = socketio
        self.transmissions = {}
        self.watchers = {}
        self.logger = logger

        # Registrar eventos Socket.IO
        self.socketio.on_event('start_transmission', self.start_transmission)
        self.socketio.on_event('stop_transmission', self.stop_transmission)
        self.socketio.on_event('broadcast_frame', self.handle_frame)
        self.socketio.on_event('list_transmissions', self.list_transmissions)
        self.socketio.on_event('join_transmission', self.join_transmission)

    def start_transmission(self, data):
        sid = data.get('sid')
        user_name = data.get('user_name')
        user_id = data.get('user_id')

        self.transmissions[user_id] = user_name
        self.logger.info(f"Transmissão iniciada por {user_name} ({user_id})")
        self.logger.info(f"Emitindo update_transmissions com transmissões: {list(self.transmissions.values())}")
        self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())})

    def stop_transmission(self, data):
        sid = data.get('sid')
        user_name = data.get('user_name')
        ip = self.socketio.server.environ[sid]['REMOTE_ADDR']
        user_id = f"{ip}_{user_name}"

        if user_id in self.transmissions:
            del self.transmissions[user_id]
            self.logger.info(f"Transmissão encerrada por {user_name} ({user_id})")
        self.logger.info(f"Emitindo update_transmissions com transmissões: {list(self.transmissions.values())}")
        self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())})

    def handle_frame(self, data):
        user_id = data['user_id']
        if user_id in self.watchers:
            for watcher in self.watchers[user_id]:
                self.logger.info(f"Emitindo frame para: user_id: {watcher}")
                self.socketio.emit('broadcast_frame', {'frame': data['frame']}, room=watcher)

    def list_transmissions(self, data):
        sid = data.get('sid')
        self.logger.info("Recebido pedido de listagem de transmissões")
        if not self.transmissions:
            self.logger.info("Nenhuma transmissão disponível.")
            self.socketio.emit('no_transmissions', room=sid)
        else:
            self.logger.info(f"Transmissões ativas: {self.transmissions}")
            self.logger.info(f"Emitindo update_transmissions com transmissões: {list(self.transmissions.values())}")
            self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())})

    def join_transmission(self, data):
        sid = data.get('sid')
        user_id = data.get('user_id')
        transmission_name = data.get('transmission_name')
        for tid, name in self.transmissions.items():
            if name == transmission_name:
                if tid not in self.watchers:
                    self.watchers[tid] = []
                self.watchers[tid].append(sid)
                self.socketio.emit('joined_transmission', room=sid)
                self.logger.info(f"Usuário {sid} juntou-se à transmissão {transmission_name}")
                return
        self.logger.info(f"Transmissão {transmission_name} não encontrada para {sid}")
        self.socketio.emit('transmission_not_found', room=sid)
