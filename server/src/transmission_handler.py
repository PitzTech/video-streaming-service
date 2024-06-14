from flask_socketio import SocketIO

class TransmissionHandler:
    def __init__(self, socketio, logger):
        """
        Inicializa o TransmissionHandler com os eventos SocketIO necessários.

        Args:
            socketio (SocketIO): Instância do SocketIO.
            logger (Logger): Instância do logger para registro de logs.
        """
        self.socketio = socketio
        self.transmissions = {}
        self.watchers = {}
        self.logger = logger
        self.socketio.on_event('start_transmission', self.start_transmission)
        self.socketio.on_event('stop_transmission', self.stop_transmission)
        self.socketio.on_event('broadcast_frame', self.handle_frame)
        self.socketio.on_event('list_transmissions', self.list_transmissions)
        self.socketio.on_event('join_transmission', self.join_transmission)

    def start_transmission(self, data):
        """
        Inicia uma transmissão e notifica os clientes.

        Args:
            data (dict): Dados da transmissão.
        """
        sid = data.get('sid')
        user_id = data.get('user_id', sid)
        name = data.get('user_name', user_id)
        self.transmissions[user_id] = name
        self.logger.info(f"Transmissão iniciada por {name} ({user_id})")
        self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())})

    def stop_transmission(self, data):
        """
        Encerra uma transmissão e notifica os clientes.

        Args:
            data (dict): Dados da transmissão.
        """
        sid = data.get('sid')
        user_id = data.get('user_id', sid)
        name = data.get('user_name', user_id)

        if user_id in self.transmissions:
            del self.transmissions[user_id]
            self.logger.info(f"Transmissão encerrada por {name} ({user_id})")
        self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())})

    def handle_frame(self, data):
        """
        Lida com os frames transmitidos e os envia para os espectadores.

        Args:
            data (dict): Dados do frame.
        """
        user_id = data['user_id']
        if user_id in self.watchers:
            for watcher in self.watchers[user_id]:
                self.socketio.emit('broadcast_frame', {'frame': data['frame']}, room=watcher['sid'])

    def list_transmissions(self, data):
        """
        Lista as transmissões ativas e notifica os clientes.

        Args:
            data (dict): Dados da solicitação.
        """
        sid = data.get('sid')
        if not self.transmissions:
            self.socketio.emit('no_transmissions', room=sid)
        else:
            self.socketio.emit('update_transmissions', {'transmissions': list(self.transmissions.values())}, room=sid)

    def join_transmission(self, data):
        """
        Permite que um espectador se junte a uma transmissão.

        Args:
            data (dict): Dados da solicitação.
        """
        sid = data.get('sid')
        user_id = data.get('user_id')
        transmission_name = data.get('transmission_name')
        for tid, name in self.transmissions.items():
            if name == transmission_name:
                if tid not in self.watchers:
                    self.watchers[tid] = []
                self.watchers[tid].append({'sid': sid, 'user_id': user_id})
                self.socketio.emit('joined_transmission', room=sid)
                return
        self.socketio.emit('transmission_not_found', room=sid)
