import pytchat
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import queue
import time
import sys
import signal

class ChatViewer:
    def __init__(self, video_id):
        self.video_id = video_id
        self.window = tk.Tk()
        self.window.title(f"Canlı Sohbet - {video_id}")
        self.window.geometry("500x600")

        # Mesaj kuyruğu ve durdurma olayı
        self.msg_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Kaydırılabilir alan oluştur
        self.canvas = tk.Canvas(self.window)
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Pencere kapatıldığında temizlik yap
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Ctrl+C sinyalini yakala
        signal.signal(signal.SIGINT, self.signal_handler)

        # Sohbet iş parçacığını başlat
        self.start_chat()

        # Kuyruğu işlemeye başla
        self.process_queue()

    def signal_handler(self, sig, frame):
        """Ctrl+C basıldığında pencereyi kapat."""
        print("\nProgram sonlandırılıyor...")
        self.window.after(0, self.on_closing)

    def start_chat(self):
        """Pytchat ile canlı yayına bağlan."""
        try:
            self.chat = pytchat.create(video_id=self.video_id)
        except Exception as e:
            messagebox.showerror("Hata", f"Pytchat başlatılamadı: {e}")
            self.window.quit()
            return

        self.thread = threading.Thread(target=self.chat_worker, daemon=True)
        self.thread.start()

    def chat_worker(self):
        """Sohbet mesajlarını okuyup kuyruğa ekleyen iş parçacığı."""
        while not self.stop_event.is_set() and self.chat.is_alive():
            try:
                for c in self.chat.get().sync_items():
                    if self.stop_event.is_set():
                        break
                    msg_data = {
                        'author_name': c.author.name,
                        'message': c.message,
                        'profile_url': c.author.imageUrl,
                        'type': c.type,
                        'bgColor': getattr(c, 'bgColor', None),
                        'amountString': getattr(c, 'amountString', None),
                        'badge_url': c.author.badgeUrl if hasattr(c.author, 'badgeUrl') else None,
                    }
                    self.msg_queue.put(msg_data)
            except Exception as e:
                print("Sohbet okuma hatası:", e)
                time.sleep(1)

    def process_queue(self):
        """Kuyruktaki mesajları alıp ekrana ekle."""
        try:
            while True:
                msg_data = self.msg_queue.get_nowait()
                self.add_message(msg_data)
        except queue.Empty:
            pass
        finally:
            self.window.after(100, self.process_queue)

    def add_message(self, msg_data):
        """Her mesaj için bir satır oluştur."""
        frame = tk.Frame(self.scrollable_frame, bd=1, relief=tk.SOLID)
        frame.pack(fill=tk.X, padx=5, pady=2)

        # Profil fotoğrafı
        if msg_data['profile_url']:
            try:
                response = requests.get(msg_data['profile_url'], timeout=3)
                img = Image.open(BytesIO(response.content))
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                if not hasattr(self, 'images'):
                    self.images = []
                self.images.append(photo)
                profile_label = tk.Label(frame, image=photo)
                profile_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
            except Exception:
                profile_label = tk.Label(frame, text="[Resim Yok]", width=5)
                profile_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
        else:
            profile_label = tk.Label(frame, text="[Resim Yok]", width=5)
            profile_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5)

        # Yazar adı
        name_label = tk.Label(frame, text=msg_data['author_name'], font=("Arial", 10, "bold"))
        name_label.grid(row=0, column=1, sticky="w")

        # Mesaj metni (Süper Chat ise arka plan renkli)
        msg_text = msg_data['message']
        if msg_data['type'] == 'superChat' and msg_data['bgColor']:
            bg_color = f"#{msg_data['bgColor']:06x}"
            msg_label = tk.Label(frame, text=msg_text, wraplength=400, justify=tk.LEFT, bg=bg_color)
        else:
            msg_label = tk.Label(frame, text=msg_text, wraplength=400, justify=tk.LEFT)
        msg_label.grid(row=1, column=1, sticky="w")

        # Süper Chat miktarı
        if msg_data['amountString']:
            amount_label = tk.Label(frame, text=msg_data['amountString'], font=("Arial", 8, "italic"))
            amount_label.grid(row=0, column=2, padx=5)

        # Rozet
        if msg_data.get('badge_url'):
            try:
                response = requests.get(msg_data['badge_url'], timeout=3)
                badge_img = Image.open(BytesIO(response.content))
                badge_img = badge_img.resize((16, 16), Image.Resampling.LANCZOS)
                badge_photo = ImageTk.PhotoImage(badge_img)
                if not hasattr(self, 'badge_images'):
                    self.badge_images = []
                self.badge_images.append(badge_photo)
                badge_label = tk.Label(frame, image=badge_photo)
                badge_label.grid(row=0, column=3, padx=2)
            except Exception:
                pass

        # Otomatik kaydır
        self.canvas.yview_moveto(1.0)

    def on_closing(self):
        """Pencere kapatılırken kaynakları temizle."""
        self.stop_event.set()
        self.window.quit()
        self.window.destroy()

if __name__ == "__main__":
    # Video ID'sini komut satırından al
    if len(sys.argv) < 2:
        print("Kullanım: python test_pychat.py <video_id>")
        sys.exit(1)

    video_id = sys.argv[1]
    app = ChatViewer(video_id)

    try:
        app.window.mainloop()
    except KeyboardInterrupt:
        # Eğer mainloop sırasında Ctrl+C basılırsa
        print("\nProgram sonlandırılıyor...")
        app.on_closing()