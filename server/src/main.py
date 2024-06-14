from flask import Flask, request
from flask_socketio import SocketIO, emit
from src.transmission_handler import TransmissionHandler
from src.chat_handler import ChatHandler
from dotenv import load_dotenv
import os
import logging

load_dotenv()

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("server.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app)
transmission_handler = TransmissionHandler(socketio, logger)
chat_handler = ChatHandler(socketio, logger)

def main():
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    logger.info("Iniciando o servidor...")
    socketio.run(app, host=host, port=port, debug=True)

if __name__ == "__main__":
    main()
