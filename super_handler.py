import queue
import time
from settings import SUPER_CHAT_SETTINGS

class SuperChatHandler:
    """
    Süper Chat ve Bağış olaylarını yöneten izole sınıf.
    Kuyruktan veriyi alır, kuralları uygular ve oyun motoruna müdahale eder.
    """
    def __init__(self, gameplay_state):
        self.state = gameplay_state # GamePlayState'in kendisine erişim
        self.game = gameplay_state.game # Ana FlagBattleGame objesine erişim
        self.queue = self.game.super_chat_queue

    def update(self):
        """Her frame'de kuyruğu kontrol eder."""
        while not self.queue.empty():
            try:
                sc_data = self.queue.get_nowait()
                self._route_action(sc_data)
            except queue.Empty:
                break

    def _route_action(self, data):
        """
        KURAL MOTORU (RULE ENGINE):
        Gelen miktara, para birimine veya isme göre farklı aksiyonların
        yönlendirildiği tek yer burasıdır.
        """
        # Veriyi temizle ve güvene al (Örn: "TRY " yerine "TRY")
        currency = data.get("currency", "").strip()
        amount = data.get("amount_val", 0.0)
        author = data.get("author", "Unknown")
        
        print(f"\n💎 [SUPER CHAT] {author} - {amount} {currency} 💎")

        # --- GÜNCEL KURAL: MİKTAR FARK ETMEKSİZİN KAOS MODU ---
        self._trigger_chaos_mode()

        # --- İLERİDE KULLANACAĞIN ÖRNEK KURAL YAPISI ---
        # if currency == "USD" and amount >= SUPER_CHAT_SETTINGS["vip_threshold_usd"]:
        #     self._trigger_boss_mode(author)
        # elif currency == "TRY" and amount >= SUPER_CHAT_SETTINGS["vip_threshold_try"]:
        #     self._drop_giant_flag(author)
        # else:
        #     self._trigger_chaos_mode()

    def _trigger_chaos_mode(self):
        """Kaos modunu başlatan/uzatan fonksiyon."""
        print("🌪️ Super Chat: Kaos Modu Tetiklendi/Uzatıldı!")
        self.state.fever_active = True
        
        current_time = time.time()
        # Eğer kaos modu zaten aktifse sürenin üstüne ekle (Stacking)
        if hasattr(self.state, 'fever_end_time') and self.state.fever_end_time > current_time:
             self.state.fever_end_time += SUPER_CHAT_SETTINGS["chaos_duration_add"]
        else:
             self.state.fever_end_time = current_time + self.state.fever_duration