# ==========================================
# OYUN DURUM MAKİNESİ (STATE MACHINE)
# ==========================================
"""
Oyunun farklı durumlarını (Menü, Geri Sayım, Oyunda, Kazanan) yönetir.
Her durum kendi update ve draw mantığına sahiptir.
"""

from abc import ABC, abstractmethod
import pygame
import time
import pymunk
import random
import pycountry
import math
import queue
from settings import *
from physics_core import rebuild_circle_segments, spawn_flag


class GameState(ABC):
    """
    Oyun durumlarının temel sınıfı (State Pattern).
    Her durum kendi event handling, update ve draw metodlarına sahiptir.
    """
    
    def __init__(self, game_engine):
        """
        Parametreler:
            game_engine: FlagBattleGame örneği
        """
        self.game = game_engine
    
    @abstractmethod
    def handle_event(self, event):
        """Olayları (event) işle"""
        pass
    
    @abstractmethod
    def update(self, dt):
        """Oyun mantığını güncelle (dt: delta time)"""
        pass
    
    @abstractmethod
    def draw(self, screen):
        """Ekrana çiz"""
        pass


class MenuState(GameState):
    """
    MENÜ DURUMU: Oyunun başlangıç menüsü.
    Kullanıcı ayarları seçer ve oyun başlatır.
    """
    
    def handle_event(self, event):
        """Menü kontrolleri (sliders, textbox, buton)"""
        for slider in self.game.sliders:
            slider.handle_event(event)
        self.game.video_id_input.handle_event(event)
        self.game.start_btn.handle_event(event)
    
    def update(self, dt):
        """Menüde update yapılmaz"""
        pass
    
    def draw(self, screen):
        """Menüyü çiz"""
        if self.game.background_surface:
            screen.blit(self.game.background_surface, (0, 0))
        else:
            screen.fill(COLOR_BG)
        
        # # Başlık
        # s_bg = pygame.Surface((400, 60))
        # s_bg.set_alpha(150)
        # s_bg.fill((0, 0, 0))
        # screen.blit(s_bg, (WIDTH // 2 - 200, 50))
        
        title = self.game.font_big.render("FLAG BATTLE", True, COLOR_ACCENT)
        title_rect = title.get_rect(center=(WIDTH // 2, 230))
        screen.blit(title, title_rect)
        
        # Video ID Input
        lbl = self.game.font_ui.render("Youtube Video ID:", True, COLOR_TEXT)
        screen.blit(lbl, (WIDTH // 2 - 200, 280))
        self.game.video_id_input.draw(screen)
        
        # Sliders
        for slider in self.game.sliders:
            slider.draw(screen)
        
        # Start Button
        self.game.start_btn.draw(screen)
        
        # NOT: EasterEggBanner ve UI panelleri MenuState'de render edilmez
        # Sadece oyun durumlarında (Countdown, GamePlay, Winner) render edilir


class CountdownState(GameState):
    """
    GERİ SAYIM DURUMU: Oyun başlamadan 3 saniyelik geri sayım.
    """
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.start_time = time.time()
    
    def handle_event(self, event):
        """Geri sayımda event işleme yapılmaz"""
        pass
    
    def update(self, dt):
        """Geri sayımı kontrol et, oyuna geç"""
        elapsed = time.time() - self.start_time
        if elapsed >= 3:
            self.game.switch_state("game")
    
    def draw(self, screen):
        """Çember ve geri sayım sayısını çiz"""
        if self.game.background_surface:
            screen.blit(self.game.background_surface, (0, 0))
        else:
            screen.fill(COLOR_BG)
        
        # Çember çiz
        self._draw_circle(screen)
        
        # Bayrakları çiz
        self._draw_flags(screen)
        
        # Panelleri çiz
        self.game.draw_panels(screen)
        
        # Geri sayım
        elapsed = time.time() - self.start_time
        countdown = 3 - int(elapsed)
        if countdown > 0:
            count_bg = pygame.Surface((100, 100))
            count_bg.set_alpha(150)
            count_bg.fill((0, 0, 0))
            count_bg_rect = count_bg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(count_bg, count_bg_rect)
            
            count_surf = self.game.font_big.render(str(countdown), True, COLOR_COUNTDOWN)
            count_rect = count_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(count_surf, count_rect)
    
    def _draw_circle(self, screen):
        """Çember duvarlarını çiz"""
        for shape in self.game.space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                self.game.draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
    
    def _draw_flags(self, screen):
        """Bayrakları çiz"""
        for shape in self.game.game_objects:
            data = shape.custom_data
            if data.get("image"):
                img = data["image"]
                rect = img.get_rect(center=(shape.body.position.x, shape.body.position.y))
                screen.blit(img, rect)


class GamePlayState(GameState):
    """
    OYUN DURUMU: Asıl oyun mantığı. Bayraklar dönerken kullanıcı skoru
    kazanmaya çalışır.
    
    Ayrık sorumluluk (SRP) ilkesi ile tasarlanmış:
    - Fizik güncelleme: _update_physics()
    - Sınır kontrolü: _check_boundaries()
    - Kazanan belirleme: _check_winner()
    """
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.start_time = time.time()
    
    def handle_event(self, event):
        """Oyun sırasında sadece SPACE tuşu ile bayrak ekle"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            obj = spawn_flag(
                self.game.space, 
                CIRCLE_CENTER, 
                SETTINGS["flag_size"],
                flag_manager=self.game.flag_manager
            )
            self.game.game_objects.append(obj)
    
    def _process_chat_events(self):
        """
        Sohbet kuyruğundan gelen olayları işle.
        Her event (name, code) olarak gelir ve hemen fizik motoruna bayrak
        eklenir.
        """
        while not self.game.chat_event_queue.empty():
            try:
                name, code = self.game.chat_event_queue.get_nowait()
            except queue.Empty:
                break
            # bayrağı spawn et
            w = SETTINGS["flag_size"] * 2.2
            h = SETTINGS["flag_size"] * 1.5
            flag_data = self.game.flag_manager.get_flag_by_code(code, w, h)
            flag_data["name"] = name
            obj = spawn_flag(
                self.game.space,
                CIRCLE_CENTER,
                SETTINGS["flag_size"],
                specific_data=flag_data,
                flag_manager=self.game.flag_manager,
            )
            self.game.game_objects.append(obj)

    def _update_physics(self):
        """
        Fizik simülasyonunu güncelle.
        - Zaman geçişine göre çember boşluğunu küçült
        - Pymunk space'i step et
        """
        time_played = time.time() - self.start_time
        progress = min(1.0, time_played / SETTINGS["round_time"])
        current_gap = SETTINGS["initial_gap"] + (progress * 30)
        
        # Çember boşluğunu güncelle
        rebuild_circle_segments(
            self.game.space, 
            self.game.circle_body, 
            INTERNAL_SETTINGS["circle_radius"], 
            current_gap
        )
        
        # Fizik simülasyonunu step et (sub-stepping ile stabilite)
        dt_physics = 1.0 / 60.0
        sub_steps = 5
        for _ in range(sub_steps):
            self.game.space.step(dt_physics / sub_steps)
    
    def _check_boundaries(self):
        """
        Çember sınırlarını kontrol et.
        Çemberden dışarı çıkan bayrakları sil.
        """
        delete_limit = INTERNAL_SETTINGS["circle_radius"] + 50
        
        for shape in self.game.game_objects[:]:
            dx = shape.body.position.x - CIRCLE_CENTER[0]
            dy = shape.body.position.y - CIRCLE_CENTER[1]
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist > delete_limit:
                self.game.space.remove(shape.body, shape)
                self.game.game_objects.remove(shape)
    
    def _check_winner(self):
        """
        Kazanan belirle ve ilgili state'e geç.
        - 1 bayrak kaldıysa: Winner state'e geç
        - 0 bayrak kaldı ve süre doldu: Yeni oyun başlat
        """
        time_played = time.time() - self.start_time
        time_left = SETTINGS["round_time"] - time_played
        
        if len(self.game.game_objects) == 1:
            self.game.winner_obj = self.game.game_objects[0]
            self.game.switch_state("winner")
        elif len(self.game.game_objects) == 0 and time_left <= 0:
            self.game.start_new_game()
    
    def update(self, dt):
        """
        Oyun frame'ini güncelle.
        Sorumluluğu ayrı metodlara dağıtılmış.
        """
        # sohbetten gelen yeni bayrak olaylarını işle
        self._process_chat_events()
        self._update_physics()
        self._check_boundaries()
        self._check_winner()
    
    def draw(self, screen):
        """Oyun ekranını çiz"""
        if self.game.background_surface:
            screen.blit(self.game.background_surface, (0, 0))
        else:
            screen.fill(COLOR_BG)
        
        # Çember çiz
        for shape in self.game.space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                self.game.draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
        
        # Bayrakları çiz
        for shape in self.game.game_objects:
            body = shape.body
            if math.isnan(body.position.x):
                continue
            data = shape.custom_data
            if data.get("image"):
                img = data["image"]
                name = data["name"]
                rect = img.get_rect(center=(body.position.x, body.position.y))
                screen.blit(img, rect)
                
                # Ülke adını çiz
                text_surf = self.game.font_small.render(name, True, COLOR_TEXT)
                text_rect = text_surf.get_rect(center=(body.position.x, body.position.y + 20))
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(screen, (0, 0, 0, 150), bg_rect, border_radius=3)
                screen.blit(text_surf, text_rect)
        
        # Alt UI (Kalan bayrak sayısı)
        ui_str = f"REST: {len(self.game.game_objects)}"
        ui_surf = self.game.font_ui.render(ui_str, True, (255, 255, 0))
        s_bar = pygame.Surface((WIDTH, 30))
        s_bar.set_alpha(200)
        s_bar.fill((0, 0, 0))
        screen.blit(s_bar, (0, HEIGHT - 30))
        screen.blit(ui_surf, (10, HEIGHT - 25))
        
        # Panelleri çiz
        self.game.draw_panels(screen)


class WinnerState(GameState):
    """
    KAZANAN DURUMU: Bir bayrak kaldığında gösterilir.
    4 saniye sonra otomatik olarak yeni oyuna geçer.
    """
    
    def __init__(self, game_engine):
        super().__init__(game_engine)
        self.start_time = time.time()
    
    def handle_event(self, event):
        """Kazanan ekranında event işleme yapılmaz"""
        pass
    
    def update(self, dt):
        """Kazanan ekranını sabitleyin ve zamanlayıcıyı kontrol et"""
        if self.game.winner_obj and self.game.winner_obj.body.body_type != pymunk.Body.KINEMATIC:
            self.game.winner_obj.body.body_type = pymunk.Body.KINEMATIC
            self.game.winner_obj.body.velocity = (0, 0)
            self.game.circle_body.angular_velocity = 0
        
        # Kazananları kaydet
        if not self.game.is_round_recorded:
            w_name = self.game.winner_obj.custom_data["name"]
            if w_name in self.game.leaderboard:
                self.game.leaderboard[w_name] += 1
            else:
                self.game.leaderboard[w_name] = 1
            self.game.is_round_recorded = True
        
        # 4 saniye sonra oyununa geç
        if time.time() - self.start_time > 4:
            self.game.start_new_game()
    
    def draw(self, screen):
        """Kazanan kutusunu çiz"""
        if self.game.background_surface:
            screen.blit(self.game.background_surface, (0, 0))
        else:
            screen.fill(COLOR_BG)
        
        # Çember çiz
        for shape in self.game.space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                self.game.draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
        
        # Panelleri çiz
        self.game.draw_panels(screen)
        
        # Kazanan kutusunu çiz
        if self.game.winner_obj:
            box_w, box_h = 450, 360
            win_bg = pygame.Surface((box_w, box_h))
            win_bg.set_alpha(200)
            win_bg.fill((0, 0, 0))
            win_bg_rect = win_bg.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(win_bg, win_bg_rect)
            
            data = self.game.winner_obj.custom_data
            
            # "WINNER" yazısı
            lbl_surf = self.game.font_big.render("WINNER", True, (252, 3, 244))
            lbl_rect = lbl_surf.get_rect(midtop=(WIDTH // 2, win_bg_rect.top + 30))
            screen.blit(lbl_surf, lbl_rect)
            
            # Bayrak
            if data.get("image"):
                img = data["image"]
                img = pygame.transform.scale(img, (150, 100))
                img_rect = img.get_rect(midtop=(WIDTH // 2, lbl_rect.bottom + 20))
                screen.blit(img, img_rect)
                
                # Ülke adı
                name_surf = self.game.font_big.render(data['name'], True, COLOR_GOLD)
                name_rect = name_surf.get_rect(midtop=(WIDTH // 2, img_rect.bottom + 20))
                screen.blit(name_surf, name_rect)
