from src.viewer import Viewer
from src.streaming_window import BroadcasterWindow
import socketio

class Menu:
    def __init__(self, server_url, logger):
        self.logger = logger
        self.sio = socketio.Client()
        self.server_url = server_url

    def display_menu(self):
        name = input("Digite seu nome: ")
        self.logger.info(f"Nome do usuário: {name}")
        print("1. Transmitir")
        print("2. Assistir")
        choice = input("Escolha uma opção: ")

        self.sio.connect(self.server_url)
        self.logger.info("Conectado ao servidor SocketIO")

        if choice == "1":
            self.logger.info("Usuário escolheu transmitir")
            broadcaster_window = BroadcasterWindow(self.sio, name, self.logger)
            broadcaster_window.start()
        elif choice == "2":
            self.logger.info("Usuário escolheu assistir")
            viewer = Viewer(self.sio, self.logger)
            viewer.list_transmissions()
            viewer.wait_for_events()
        else:
            self.logger.warning("Opção inválida")
            print("Opção inválida")

        self.sio.disconnect()
