import socketio
import tkinter as tk
from threading import Thread

class ChatWindow:
    def __init__(self, sio: socketio.Client, user_id: str, logger, parent_frame):
        self.sio = sio
        self.user_id = user_id
        self.logger = logger
        self.root = parent_frame

        self.chat_log = tk.Text(self.root, state='disabled', wrap=tk.WORD)
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.root, command=self.chat_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_log.config(yscrollcommand=scrollbar.set)

        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind('<Return>', self.send_message)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.sio.on('chat_message', self.receive_message)
        Thread(target=self.sio.wait).start()

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            self.sio.emit('send_message', {'user_id': self.user_id, 'message': message})
            self.logger.info(f"Mensagem enviada: {message}")
            self.msg_entry.delete(0, 'end')

    def receive_message(self, data):
        self.chat_log.config(state='normal')
        self.chat_log.insert('end', f"{data['user_id']}: {data['message']}\n")
        self.chat_log.config(state='disabled')
        self.chat_log.see('end')
        self.logger.info(f"Mensagem recebida: {data['message']}")

    def start(self):
        pass  # Nada para fazer aqui, pois o loop principal é gerenciado pela janela principal
