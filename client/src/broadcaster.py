from src.streaming_window import BroadcasterWindow
from threading import Thread
from PIL import Image, ImageTk
import cv2

class BroadcasterWindow(StreamingWindow):
    def __init__(self, sio, user_id, logger):
        super().__init__(sio, user_id, logger)
        self.transmitting = True
        self.sio.emit('start_transmission', {'user_id': self.user_id, 'sid': self.sio.sid})

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
