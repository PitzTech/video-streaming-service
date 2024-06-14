import cv2
import socketio
from dotenv import load_dotenv
import os
import numpy as np
from threading import Thread
from src.streaming_window import ViewerWindow

load_dotenv()

SERVER_URL = os.getenv('SERVER_URL')

class Viewer:
    def __init__(self, sio, logger):
        self.sio = sio
        self.sio.on('broadcast_frame', self.handle_frame)
        self.sio.on('update_transmissions', self.update_transmissions)
        self.sio.on('no_transmissions', self.no_transmissions)
        self.sio.on('joined_transmission', self.joined_transmission)
        self.sio.on('transmission_not_found', self.transmission_not_found)
        self.transmissions = []
        self.logger = logger

    def list_transmissions(self):
        self.logger.info("Listando transmissões")
        self.sio.emit('list_transmissions', {'sid': self.sio.sid})
        self.logger.info("Evento 'list_transmissions' emitido para o servidor")

    def update_transmissions(self, data):
        self.logger.info(f"Transmissões recebidas: {data}")
        self.transmissions = data['transmissions']
        if not self.transmissions:
            self.logger.info("Nenhuma transmissão disponível")
            print("Não há transmissões disponíveis.")
            self.sio.disconnect()
            return
        print("Transmissões disponíveis:")
        for idx, transmission in enumerate(self.transmissions, start=1):
            print(f"{idx}. {transmission}")
        self.prompt_for_transmission()

    def prompt_for_transmission(self):
        choice = input("Escolha uma transmissão para assistir: ")
        if choice.isdigit() and 1 <= int(choice) <= len(self.transmissions):
            transmission_name = self.transmissions[int(choice) - 1]
            self.sio.emit('join_transmission', {'transmission_name': transmission_name, 'sid': self.sio.sid})
            viewer_window = ViewerWindow(self.sio, f"Viewer_{transmission_name}", self.logger)
            viewer_window.start()
        else:
            print("Escolha inválida, tente novamente.")
            self.prompt_for_transmission()

    def no_transmissions(self, data):
        self.logger.info("Nenhuma transmissão disponível")
        print("Não há transmissões disponíveis.")
        self.sio.disconnect()

    def joined_transmission(self, data):
        self.logger.info("Juntou-se à transmissão")

    def transmission_not_found(self, data):
        self.logger.info("Transmissão não encontrada")
        print("Transmissão não encontrada. Tente novamente.")
        self.prompt_for_transmission()

    def handle_frame(self, data):
        frame = cv2.imdecode(np.frombuffer(data['frame'], np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow('Assistindo', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.sio.disconnect()
            cv2.destroyAllWindows()

    def wait_for_events(self):
        self.logger.info("Esperando eventos do servidor")
        self.sio.wait()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    viewer = Viewer(socketio.Client(), logging.getLogger("Viewer"))
    viewer.sio.connect(SERVER_URL)
    viewer.list_transmissions()
    viewer.wait_for_events()