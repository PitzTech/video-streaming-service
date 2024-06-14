import cv2
import socketio
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk
import numpy as np
import os
import socket
from src.chat import ChatWindow

def get_ip():
    # Obtém o IP do usuário
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Não se conecta realmente, apenas obtém o IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

class StreamingWindow:
    def __init__(self, sio, user_id, logger):
        self.sio = sio
        self.user_id = user_id
        self.logger = logger
        self.transmitting = False

        # Cria a janela do tkinter
        self.root = tk.Tk()
        self.root.title(f"Streaming - {user_id}")

        # Cria um frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configura as colunas para terem o mesmo tamanho
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Coluna esquerda
        left_frame = tk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Frame de vídeo
        self.video_label = tk.Label(left_frame, bg="black", fg="white", text="Camera carregando, aguarde...")
        self.video_label.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Adiciona um botão para encerrar
        self.end_button = tk.Button(left_frame, text="Encerrar", command=self.stop_stream)
        self.end_button.pack(side=tk.TOP, pady=10)

        # Coluna direita
        right_frame = tk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

        # Frame de chat com rolagem
        chat_frame = tk.Frame(right_frame)
        chat_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.chat_log = tk.Text(chat_frame, state='disabled', wrap=tk.WORD)
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(chat_frame, command=self.chat_log.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_log.config(yscrollcommand=scrollbar.set)

        # Frame para entrada de mensagens e botão "Send"
        input_frame = tk.Frame(right_frame)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.msg_entry = tk.Entry(input_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind('<Return>', self.send_message)

        self.send_button = tk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

        self.sio.on('chat_message', self.receive_message)

        # Configura a janela para estar em destaque
        self.root.lift()
        self.root.attributes('-topmost', 1)
        self.root.after_idle(self.root.attributes, '-topmost', 0)
        self.root.focus_force()

    def start(self):
        # Inicia o loop principal do tkinter
        self.root.mainloop()

    def stop_stream(self):
        if self.transmitting:
            self.transmitting = False
            self.sio.emit('stop_transmission', {'user_id': self.user_id})
        self.sio.disconnect()
        self.logger.info("Transmissão encerrada")
        self.root.quit()
        self.root.destroy()
        os._exit(0)  # Termina o processo imediatamente

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

class BroadcasterWindow(StreamingWindow):
    def __init__(self, sio, user_name, logger):
        ip = get_ip()
        user_id = f"{ip}_{user_name}"
        self.name = user_name
        super().__init__(sio, user_id, logger)
        self.transmitting = True
        self.sio.emit('start_transmission', {'sid': self.sio.sid, 'user_name': self.name})

        # Executa a captura de vídeo em uma thread separada
        video_thread = Thread(target=self.capture_video)
        video_thread.start()

    def capture_video(self):
        cap = cv2.VideoCapture(0)
        while self.transmitting:
            ret, frame = cap.read()
            if not ret:
                continue

            # Converte o frame para ImageTk
            img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

            # Atualiza a imagem no label
            self.video_label.config(image=img, text="")
            self.video_label.image = img

            _, buffer = cv2.imencode('.jpg', frame)
            self.sio.emit('broadcast_frame', {'user_id': self.user_id, 'frame': buffer.tobytes()})

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        self.stop_stream()

class ViewerWindow(StreamingWindow):
    def __init__(self, sio, user_name, logger):
        ip = get_ip()
        user_id = f"{ip}_{user_name}"
        super().__init__(sio, user_id, logger)
        self.sio.on('broadcast_frame', self.handle_frame)

    def handle_frame(self, data):
        frame = cv2.imdecode(np.frombuffer(data['frame'], np.uint8), cv2.IMREAD_COLOR)
        img = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.video_label.config(image=img, text="")
        self.video_label.image = img

    def stop_stream(self):
        super().stop_stream()
        self.logger.info("Espectador desconectado")
        os._exit(0)  # Termina o processo imediatamente
