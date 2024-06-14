from src.menu import Menu
import logging
from dotenv import load_dotenv
import os

load_dotenv()
SERVER_URL = os.getenv('SERVER_URL')

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("client.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando o cliente...")
    menu = Menu(SERVER_URL, logger)
    menu.display_menu()

if __name__ == "__main__":
    main()
