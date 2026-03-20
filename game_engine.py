# ==========================================
# OYUN ENGİNESİ KÖKLÜKLÜTÜRÜ (GAME ENGINE)
# ==========================================
"""
FlagBattleGame sınıfı: Oyunun tüm mantığını, durumlarını ve
kaynakları merkezi bir noktadan yönetir.
"""

import pygame
import pymunk
import random
import threading
import pytchat
import time
import os
import queue
import queue
from settings import *
from flag_handler import FlagManager
from ui_elements import TextBox, Slider, Button
from physics_core import create_circle_body, rebuild_circle_segments
from chat_handler import chat_listener_task
from like_handler import LikeTracker#like eventini takip etmek için gerekli sınıf
from game_states import MenuState, CountdownState, GamePlayState, WinnerState


class FlagBattleGame:
    """
    Oyunun ana sınıfı. Tüm durum yönetimi, kaynaklar, fizik ve UI
    bu sınıfta merkezi olarak yönetilir.
    """
    
    def __init__(self, screen):
        """
        Oyunu başlatır.
        
        Parametreler:
            screen: Pygame ekranı
        """
        self.screen = screen
        
        # ==========================================
        # KAYNAKLAR
        # ==========================================
        self.flag_manager = FlagManager(self._resource_path(FLAGS_FOLDER))
        self._load_background()
        self._initialize_fonts()

        # bağımsız UI panel component'leri
        from ui_panels import LeaderboardPanel, NextFlagsPanel, EasterEggBanner,LikeBarPanel, SuperChatBanner
        lb_x = LEADERBOARD_PANEL["x_position"]
        lb_y = LEADERBOARD_PANEL["y_position"]
        self.leaderboard_panel = LeaderboardPanel(lb_x, lb_y)

        # lb_x = (WIDTH - LEADERBOARD_PANEL["width"]) // 2
        # lb_y = LEADERBOARD_PANEL["y_position"]
        # self.leaderboard_panel = LeaderboardPanel(lb_x, lb_y)
        # nf_x = lb_x - NEXT_FLAGS_PANEL["width"] + NEXT_FLAGS_PANEL["horizontal_offset_x"]
        # nf_y = lb_y + LEADERBOARD_PANEL["header_height"] #liderlik panelinin hemen altına hizala
        # self.next_flags_panel = NextFlagsPanel(nf_x, nf_y)
        nf_x = NEXT_FLAGS_PANEL["x_position"]
        nf_y = NEXT_FLAGS_PANEL["y_position"]
        self.next_flags_panel = NextFlagsPanel(nf_x, nf_y)

        eg_x = WIDTH // 2
        eg_y = EASTER_EGG["offset_y"]
        self.easter_egg = EasterEggBanner(eg_x, eg_y)

        # Süper Chat Banner'ı başlat
        sc_y = SUPER_CHAT_UI.get("y_position", 380) # Settings'ten çeker
        self.sc_banner = SuperChatBanner(WIDTH // 2, sc_y, self)
        
        bar_x = (WIDTH - LIKE_BAR_SETTINGS["width"]) // 2
        bar_y = LIKE_BAR_SETTINGS["y_position"]
        self.like_bar = LikeBarPanel(bar_x, bar_y)
        
        self.current_likes = 0  # API bağlanana kadar 0'da duracak
        self.like_tracker = None
        self.likes_synced = False # İlk senkronizasyon yapıldı mı kontrolü


        # ==========================================
        # FİZİK DÜNYASI
        # ==========================================
        self.space = pymunk.Space()
        self.space.gravity = (0, SETTINGS["gravity"])
        self.space.damping = 0.9
        self.circle_body = None
        self.game_objects = []
        
        # ==========================================
        # OYUN DURUMU
        # ==========================================
        self.current_state = None
        self.leaderboard = {}
        self.next_round_queue = {}
        self.winner_obj = None
        self.is_round_recorded = False
        
        # ==========================================
        # UI BİLEŞENLERİ
        # ==========================================
        self.video_id_input = TextBox(WIDTH // 2 - 200, 300, 400, 40, "YT Live Video ID")
        self.sliders = self._create_sliders()
        self.start_btn = Button(WIDTH // 2 - 100, 800, 200, 50, "BASLA", self.start_new_game)
        
        # ==========================================
        # SOHBET
        # ==========================================
        self.chat_thread = None
        self.is_chat_running = False
        self.chat_event_queue = queue.Queue()
        
        # ==========================================
        # DURUM MAKİNESİ BAŞLANGICI
        # ==========================================
        self.switch_state("menu")
        #debug
        self.last_debug_time = time.time()
    
    # ==========================================
    # BAŞLATMA VE KAYNAKLAR
    # ==========================================
    
    def _load_background(self):
        """Arka plan resmini yükle"""
        self.background_surface = None
        bg_path = self._resource_path(BACKGROUND_FILE_NAME)
        try:
            bg_img = pygame.image.load(bg_path).convert()
            self.background_surface = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
            print("[OK] Arka plan başarıyla yüklendi.")
        except Exception as e:
            # include the attempted path for easier debugging
            print(f"[ERROR] Arka plan yüklenemedi: {e} - aranıyor: {bg_path}")
    
    def _initialize_fonts(self):
        """Yazıtiplerini başlat"""
        def _load_emoji_font():
            """Emoji fontunu sistemi platformları destekleyerek yükle"""
            for path in EMOJI_FONT_PATHS:
                if os.path.exists(path):
                    try:
                        return pygame.font.Font(path, FONTS["emoji"]["size"])
                    except:
                        continue
            print("⚠ Emoji font bulunamadı, yedek kullanılacak.")
            return pygame.font.SysFont("Arial", FONTS["emoji"]["size"], bold=True)
        
        self.emoji_font = _load_emoji_font()
        self.font_small = pygame.font.SysFont(
            FONTS["small"]["name"], 
            FONTS["small"]["size"], 
            bold=FONTS["small"]["bold"]
        )
        self.font_ui = pygame.font.SysFont(
            FONTS["ui"]["name"], 
            FONTS["ui"]["size"], 
            bold=FONTS["ui"]["bold"]
        )
        self.font_big = pygame.font.SysFont(
            FONTS["big"]["name"], 
            FONTS["big"]["size"], 
            bold=FONTS["big"]["bold"]
        )
        self.font_leaderboard = pygame.font.SysFont(
            FONTS["leaderboard"]["name"],
            FONTS["leaderboard"]["size"],
            bold=FONTS["leaderboard"]["bold"]
        )
    
    def _create_sliders(self):
        """Menü sliderlarını oluştur (Varsayılan değerler tam ortada olacak şekilde ayarlandı)"""
        return [
            # 1. Başlangıç Boşluğu: 30 (Min:10 + Max:50 = 60 / 2 = 30) - Zaten Mükemmeldi
            Slider(WIDTH // 2 - 200, 390, 400, 20, 10, 50, SETTINGS["initial_gap"], "Baslangic Boslugu (%)"),
            
            # 2. Tur Süresi: 20 (Min:10 + Max:30 = 40 / 2 = 20)
            Slider(WIDTH // 2 - 200, 460, 400, 20, 10, 30, SETTINGS["round_time"], "Tur Suresi (sn)"),
            
            # 3. Başlangıç Bayrak: 40 (Min:0 + Max:80 = 80 / 2 = 40)
            Slider(WIDTH // 2 - 200, 530, 400, 20, 0, 80, SETTINGS["auto_spawn"], "Baslangic Bayrak Sayisi"),
            
            # 4. Gravity: 40 (Min:0 + Max:80 = 80 / 2 = 40)
            Slider(WIDTH // 2 - 200, 600, 400, 20, 0, 80, SETTINGS["gravity"], "Gravity (Yercekimi)"),
            
            # 5. Dönme Hızı: 1.5 (Min:0.0 + Max:3.0 = 3.0 / 2 = 1.5)
            Slider(WIDTH // 2 - 200, 670, 400, 20, 0.0, 3.0, SETTINGS["rotation_speed"], "Donme Hizi"),
        ]

        # ==========================================
    # DIŞARDAN DOSYA ALMA
    # ==========================================
    
    @staticmethod
    def _resource_path(relative_path):
        import sys
        import os
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_path, relative_path)
        # Hata ayıklama için terminale yolu yazdıralım
        print(f"[DEBUG] Aranan Yol: {full_path}")
        return full_path
    # ==========================================
    # DURUM MAKİNESİ
    # ==========================================
    
    def switch_state(self, state_name):
        """
        Oyun durumunu değiştir.
        
        Parametreler:
            state_name: "menu", "countdown", "game", "winner"
        """
        if state_name == "menu":
            self.current_state = MenuState(self)
        elif state_name == "countdown":
            self.current_state = CountdownState(self)
        elif state_name == "game":
            self.current_state = GamePlayState(self)
        elif state_name == "winner":
            self.current_state = WinnerState(self)
    
    # ==========================================
    # OYUN BAŞLATMA VE YÖNETİMİ
    # ==========================================
    
    def start_new_game(self):
        """
        Yeni bir oyun turu başlat.
        - Ayarları sliderlardan okuya
        - Fizik dünyasını yeniden kur
        - Sohbeti başlat (eğer URL varsa)
        - Sayım durumuna geç
        """
        # Ayarları güncelle
        self._update_settings_from_sliders()
        
        # Sohbeti başlat (eğer URL geçerliyse)
        self._start_chat()
        
        # Fizik dünyasını temizle ve yeniden kur
        self._reset_physics()
        
        # Kalan bayrakları ve durumları temizle
        self.game_objects = []
        self.winner_obj = None
        self.is_round_recorded = False
        
        # İlk bayrakları oluştur
        self._spawn_initial_flags()
        
        # Sayım durumuna geç
        self.switch_state("countdown")
    
    def _update_settings_from_sliders(self):
        """Menü sliderlarından ayarları oku"""
        SETTINGS["initial_gap"] = self.sliders[0].val
        SETTINGS["round_time"] = self.sliders[1].val
        SETTINGS["auto_spawn"] = int(self.sliders[2].val)
        SETTINGS["gravity"] = self.sliders[3].val
        SETTINGS["rotation_speed"] = self.sliders[4].val
        
        SETTINGS["flag_size"] = 15
        INTERNAL_SETTINGS["elasticity"] = 1.1
        
        # # Çember yarıçapını bayrak sayısına göre dinamik olarak ayarla
        # INTERNAL_SETTINGS["circle_radius"] = 170 + (SETTINGS["auto_spawn"] * 1.5)
        # INTERNAL_SETTINGS["circle_radius"] = min(240, INTERNAL_SETTINGS["circle_radius"])
        # Çember yarıçapını bayrak sayısına göre dinamik olarak ayarla (Maksimum 240)
        INTERNAL_SETTINGS["circle_radius"] = min(240, 170 + (SETTINGS["auto_spawn"] * 1.5))
    
    def _start_chat(self):
        """
        YouTube sohbetini dinlemeye başla (eğer URL geçerliyse).
        Sohbetten ülke adlarını önce event kuyruğuna, sonra next_round_queue'ye ekle.
        """
        video_id = self.video_id_input.text
        if len(video_id) > 5:
            if self.chat_thread is None or not self.chat_thread.is_alive():
                try:
                    print(f"📡 Bağlanıyor: {video_id}")
                    chat = pytchat.create(video_id=video_id)
                    self.chat_thread = threading.Thread(
                        target=chat_listener_task,
                        args=(chat, self.chat_event_queue, self.next_round_queue),
                        daemon=True
                    )
                    self.chat_thread.start()

                   # Beğeni takipçisini başlat
                    if YOUTUBE_API_KEY:
                        self.like_tracker = LikeTracker(YOUTUBE_API_KEY, video_id)
                        self.like_tracker.start()
                    else:
                        print("[HATA] YOUTUBE_API_KEY bulunamadı!")

                    self.is_chat_running = True
                except Exception as e:
                    print(f"[ERROR] Bağlantı hatası: {e}")
    
    def _reset_physics(self):
        """
        Fizik dünyasını sıfırla.
        - Eski kaynakları temizle
        - Yeni çember gövdesini oluştur
        - Segment'leri yeniden inşa et
        """
        self.space = pymunk.Space()
        self.space.gravity = (0, SETTINGS["gravity"])
        self.space.damping = 0.9
        
        self.circle_body = create_circle_body(
            self.space, 
            CIRCLE_CENTER, 
            SETTINGS["rotation_speed"]
        )
        rebuild_circle_segments(
            self.space, 
            self.circle_body, 
            INTERNAL_SETTINGS["circle_radius"], 
            SETTINGS["initial_gap"]
        )
    
    def _spawn_initial_flags(self):
        """
        Şimdiye kadar kuyruktaki bayrakları spawn et.
        Eğer kuyruktakiler yeterli değilse rastgele bayraklar ekle.
        """
        from physics_core import spawn_flag
        
        total_slots = SETTINGS["auto_spawn"]
        spawned_count = 0
        spawn_radius_limit = INTERNAL_SETTINGS["circle_radius"] * 0.7
        
        # Kuyruktaki bayrakları spawn et
        current_queue = dict(self.next_round_queue)
        self.next_round_queue.clear()
        
        for name, info in current_queue.items():
            count = info["count"]
            code = info["code"]
            
            w = SETTINGS["flag_size"] * 2.2
            h = SETTINGS["flag_size"] * 1.5
            flag_data = self.flag_manager.get_flag_by_code(code, w, h)
            flag_data["name"] = name
            
            for _ in range(count):
                rx = CIRCLE_CENTER[0] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
                ry = CIRCLE_CENTER[1] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
                obj = spawn_flag(self.space, (rx, ry), SETTINGS["flag_size"], specific_data=flag_data, flag_manager=self.flag_manager)
                self.game_objects.append(obj)
                spawned_count += 1
        
        # Eksik slotları rastgele bayraklarla doldur
        remaining_slots = total_slots - spawned_count
        if remaining_slots < 0:
            remaining_slots = 0
        
        for _ in range(remaining_slots):
            rx = CIRCLE_CENTER[0] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
            ry = CIRCLE_CENTER[1] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
            obj = spawn_flag(
                self.space, 
                (rx, ry), 
                SETTINGS["flag_size"],
                flag_manager=self.flag_manager
            )
            self.game_objects.append(obj)
    
    # ==========================================
    # OLAY VE GÜNCELLEMELERİ
    # ==========================================
    
    def handle_event(self, event):
        """Oyun olaylarını işle (event'leri duruma ilet)"""
        if event.type == pygame.QUIT:
            return False
        self.current_state.handle_event(event)
        return True
    
    def update(self, dt):
        """Oyun durumunu güncelle (update'i duruma ilet)"""
        self.current_state.update(dt)

        # API'den gelen veriyi kontrol et ve barı güncelle
        if self.like_tracker and self.like_tracker.first_sync_done:
            self.current_likes = self.like_tracker.current_likes
            
            # İlk bağlantı anındaki devasa sayıyı sessizce ileri sar
            if not self.likes_synced:
                self.like_bar.sync_initial_likes(self.current_likes)
                self.likes_synced = True
                print(f"[SYNC] Başlangıç beğenisi senkronize edildi: {self.current_likes}, Hedef: {self.like_bar.current_target}")
            else:
                pass
                # # Normal oyun içi seviye atlama (Level Up) kontrolü
                # if self.like_bar.check_level_up(self.current_likes):
                #     print(f">>> BEĞENİ HEDEFİNE ULAŞILDI! YENİ HEDEF: {self.like_bar.current_target} <<<")
                #     # 1. Ekranı 1 saniye boyunca sallandır (Screen Shake)
                #     # 2. Rastgele 5 tane altın renkli dev bayrak spawn et
                #     # 3. Şakşak/Alkış ses efekti oynat

        # Her 5 saniyede bir RAM analizi için terminale çıktı ver
        # current_time = time.time()
        # if current_time - self.last_debug_time >= 25.0:
        #     print(f"\n--- [DEBUG] SİSTEM DURUMU ---")
        #     print(f"Chat Event Kuyruğu: {self.chat_event_queue.qsize()} öğe")
        #     print(f"Next Flags Sözlüğü: {len(self.next_round_queue)} benzersiz ülke")
        #     print(f"Aktif Fizik Objeleri: {len(self.game_objects)} bayrak")
        #     print(f"FlagManager Cache: {len(self.flag_manager.image_cache)} yüzey")
        #     print(f"-----------------------------\n")
        #     self.last_debug_time = current_time
    def draw(self):
        """Ekrana çiz (draw'ı duruma ilet)"""
        self.current_state.draw(self.screen)
    
    # ==========================================
    # YÖNETİM HİZMETLERİ
    # ==========================================
    
    def draw_panels(self, screen):
        """
        UI panellerini ekrana çizmek için çağrılır.
        Her panel kendi x/y konumuna göre render olur.
        """
        self.leaderboard_panel.draw(screen, self.leaderboard, self.font_small, self.emoji_font)
        self.next_flags_panel.draw(screen, self.next_round_queue, self.font_small, self.emoji_font, self.flag_manager)
        #self.easter_egg.draw(screen) #easter egg banner'ını çiz (aktif değil, istenirse açılabilir)
        #self.sc_banner.draw(screen) #superchat banner'ını çiz (aktif değil, istenirse açılabilir)

        #like barı
        self.like_bar.draw(screen, self.current_likes, self.font_ui, self.emoji_font)
    
    @staticmethod
    def draw_smooth_segment(screen, p1, p2, thickness, color):
        """
        Yuvarlak uçlu çizgi çiz (çember segment'leri için).
        
        Parametreler:
            screen: Pygame ekranı
            p1, p2: Başlangıç ve bitiş noktaları
            thickness: Kalınlık
            color: RGB rengi
        """
        import math
        import pygame.gfxdraw
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return
        
        norm_x = -dy / dist
        norm_y = dx / dist
        half_thickness = thickness / 2.0
        corners = [
            (p1[0] + norm_x * half_thickness, p1[1] + norm_y * half_thickness),
            (p1[0] - norm_x * half_thickness, p1[1] - norm_y * half_thickness),
            (p2[0] - norm_x * half_thickness, p2[1] - norm_y * half_thickness),
            (p2[0] + norm_x * half_thickness, p2[1] + norm_y * half_thickness)
        ]
        pygame.gfxdraw.filled_polygon(screen, corners, color)
        pygame.gfxdraw.aapolygon(screen, corners, color)
    
    def shutdown(self):
        """Oyunu temiz bir şekilde kapat"""
        self.is_chat_running = False
        if self.chat_thread and self.chat_thread.is_alive():
            self.chat_thread.join(timeout=1)

        if self.like_tracker:
            self.like_tracker.stop()