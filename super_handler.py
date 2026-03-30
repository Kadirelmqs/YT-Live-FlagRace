import queue
import time
import pygame
import random
from settings import SUPER_CHAT_SETTINGS, SETTINGS, CIRCLE_CENTER, INTERNAL_SETTINGS
from physics_core import spawn_flag
from chat_handler import find_country_code

class SuperChatHandler:
    def __init__(self, gameplay_state):
        self.state = gameplay_state
        self.game = gameplay_state.game
        self.queue = self.game.super_chat_queue

    def update(self):
        while not self.queue.empty():
            try:
                sc_data = self.queue.get_nowait()
                self._route_action(sc_data)
            except queue.Empty:
                break

    def _extract_vip_country_code(self, message):
        """1. Emoji kontrolü yapar. 2. Chat handler'daki kelime sözlüğünü kullanır."""
        if not message:
            return None

        # 1. Emoji Kontrolü
        for i in range(len(message) - 1):
            c1, c2 = message[i], message[i+1]
            if '\U0001F1E6' <= c1 <= '\U0001F1FF' and '\U0001F1E6' <= c2 <= '\U0001F1FF':
                return chr(ord(c1) - 0x1F1E6 + 65) + chr(ord(c2) - 0x1F1E6 + 65)

        # 2. Cümle İçinden Akıllı Arama ("add to uk flag please" vb.)
        return find_country_code(message)

    def _route_action(self, data):
        currency = data.get("currency", "").strip()
        amount = data.get("amount_val", 0.0)
        author = data.get("author", "Unknown")
        message = data.get("message", "")
        
        target_code = self._extract_vip_country_code(message)
        
        if target_code:
            print(f"\n💎 [VIP BAYRAK] {author} -> {target_code}")
            self._trigger_terminator_flag(author, target_code)
        else:
            print(f"\n🌪️ [KAOS BOMBASI] {author} -> Ülke bulunamadı, 500 bayrak atılıyor!")
            self._trigger_chaos_mode()
            self._spawn_500_flags()

    def _trigger_chaos_mode(self):
        self.state.fever_active = True
        current_time = time.time()
        if hasattr(self.state, 'fever_end_time') and self.state.fever_end_time > current_time:
             self.state.fever_end_time += SUPER_CHAT_SETTINGS["chaos_duration_add"]
        else:
             self.state.fever_end_time = current_time + self.state.fever_duration

    def _spawn_500_flags(self):
        """Çemberin tam ortasına rastgele 500 bayrak yığar."""
        radius_limit = INTERNAL_SETTINGS["circle_radius"] * 0.7
        for _ in range(500):
            rx = CIRCLE_CENTER[0] + random.uniform(-radius_limit, radius_limit)
            ry = CIRCLE_CENTER[1] + random.uniform(-radius_limit, radius_limit)
            obj = spawn_flag(self.game.space, (rx, ry), SETTINGS["flag_size"], flag_manager=self.game.flag_manager)
            self.game.game_objects.append(obj)

    def _trigger_terminator_flag(self, author_name, country_code):
        """Altın çerçeveli, ölümsüz Terminatör bayrağı yaratır."""
        w = SETTINGS["flag_size"] * 2.2
        h = SETTINGS["flag_size"] * 1.5
        
        # Orijinal bayrağı al
        base_data = self.game.flag_manager.get_flag_by_code(country_code, w, h)
        
        # Altın çerçeve yüzeyini oluştur (Orijinal resimden 6 piksel daha büyük)
        framed_img = pygame.Surface((w + 6, h + 6))
        framed_img.fill((255, 215, 0)) # Altın Rengi
        framed_img.blit(base_data["image"], (3, 3)) # Bayrağı ortala
        
        flag_data = {
            "image": framed_img,
            "original": framed_img,
            "name": f"👑 {author_name}"
        }

        # Çemberin İÇİNDE doğsun
        spawn_pos = (CIRCLE_CENTER[0] + random.uniform(-10, 10), CIRCLE_CENTER[1] - 50)
        
        obj = spawn_flag(
            self.game.space, spawn_pos, SETTINGS["flag_size"],
            specific_data=flag_data, flag_manager=self.game.flag_manager
        )
        
        # Terminatör Kuralları
        obj.custom_data["is_terminator"] = True
        obj.custom_data["is_immortal"] = True
        self.game.game_objects.append(obj)