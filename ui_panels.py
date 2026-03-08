import pygame
import math
from settings import *

# ==========================================
# BAĞIMSIZ UI PANEL SINIFLARI
# ==========================================

class LeaderboardPanel:
    """Liderlik paneli componenti.

    Konumu ve konfigürasyonu dışarıdan verilir. İçerik
    çizimi tüm koordinatları panelin kendi x/y'sine göre
    mutlaklama sağlar.
    """

    def __init__(self, x, y, config=None):
        self.x = x
        self.y = y
        self.cfg = config or LEADERBOARD_PANEL

        # scroll durumu
        self.scroll_offset = 0.0
        self.direction = 1
        self.pause_timer = 0
        self.last_tick = pygame.time.get_ticks()
        
        # STATIK ARKA PLAN VE GÖLGESİ (1 kez oluştur)
        cfg = self.cfg
        panel_w = cfg["width"]
        MAX_VISIBLE = cfg["max_visible_items"]
        ROW_HEIGHT = cfg["row_height"]
        HEADER_H = cfg["header_height"]
        panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)
        
        # Gölge surface'i
        # self.shadow_surf = pygame.Surface((panel_w, panel_h))
        # self.shadow_surf.set_alpha(cfg["shadow_alpha"])
        # self.shadow_surf.fill(COLOR_SHADOW)
        
        # Arka plan surface'i
        self.bg_surf = pygame.Surface((panel_w, panel_h))
        self.bg_surf.set_alpha(cfg["panel_alpha"])
        self.bg_surf.fill(COLOR_PANEL_BG)
        
        # Başlık yazısı
        try:
            self.title_surf = pygame.font.SysFont("segoeuiemoji", 22, bold=True).render("👑 TOP WINNERS", True, cfg["title_color_lb"])
        except:
            self.title_surf = pygame.font.SysFont("Arial", 22, bold=True).render("TOP WINNERS", True, cfg["title_color_lb"])

    def draw(self, screen, leaderboard, font_small, emoji_font):
        if not leaderboard:
            return

        cfg = self.cfg
        sorted_winners = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:10]
        total_items = len(sorted_winners)

        MAX_VISIBLE = cfg["max_visible_items"]
        ROW_HEIGHT = cfg["row_height"]
        HEADER_H = cfg["header_height"]
        panel_w = cfg["width"]
        panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)

        panel_x = self.x
        panel_y = self.y

        if panel_x + panel_w > WIDTH - 20:
            panel_x = WIDTH - panel_w - 20

        # yatay salınım animasyonu (sadece render pozisyonini etkiler)
        # time_ms = pygame.time.get_ticks()
        # h_offset = int(
        #     cfg["horizontal_oscillation_amplitude"] *
        #     math.sin(time_ms * cfg["oscillation_frequency"])
        # )
        # panel_x += h_offset

        # STATIK GÖLGEYİ BLITLEY
        # screen.blit(self.shadow_surf, (panel_x + cfg["shadow_offset"], panel_y + cfg["shadow_offset"]))

        # STATIK ARKA PLANI BLITLE
        screen.blit(self.bg_surf, (panel_x, panel_y))

        # STATIK BAŞLIK YAZISINI BLITLE
        screen.blit(self.title_surf, (panel_x + cfg["title_offset_x"], panel_y + cfg["title_offset_y"]))

        # İçeriği çiz (dinamik veri)
        if total_items <= MAX_VISIBLE:
            start_y = panel_y + HEADER_H
            for i, (country, wins) in enumerate(sorted_winners[:MAX_VISIBLE]):
                y_pos = start_y + i * ROW_HEIGHT
                self._draw_entry(screen, i, country, wins, panel_x + 15, y_pos, font_small, emoji_font)
            return

        # kaydırma
        total_scroll = (total_items - MAX_VISIBLE) * ROW_HEIGHT
        current_tick = pygame.time.get_ticks()
        dt = (current_tick - self.last_tick) / 1000.0
        self.last_tick = current_tick

        if self.pause_timer > 0:
            self.pause_timer -= dt * 1000
            if self.pause_timer <= 0:
                self.direction *= -1
        else:
            SCROLL_SPEED = cfg.get("scroll_speed", 40)
            self.scroll_offset += self.direction * SCROLL_SPEED * dt
            if self.scroll_offset >= total_scroll and self.direction == 1:
                self.scroll_offset = total_scroll
                self.pause_timer = cfg.get("scroll_pause_duration_ms", 3000)
            elif self.scroll_offset <= 0 and self.direction == -1:
                self.scroll_offset = 0
                self.pause_timer = cfg.get("scroll_pause_duration_ms", 3000)
            self.scroll_offset = max(0.0, min(self.scroll_offset, total_scroll))

        view_y_start = panel_y + HEADER_H
        view_y_end = panel_y + panel_h
        entry_clip = pygame.Rect(panel_x, view_y_start, panel_w, panel_h - HEADER_H)
        entry_clip.inflate_ip(0, -4)

        old_clip = screen.get_clip()
        screen.set_clip(entry_clip)

        for i, (country, wins) in enumerate(sorted_winners):
            y = view_y_start + i * ROW_HEIGHT - self.scroll_offset
            if view_y_start - ROW_HEIGHT < y < view_y_end:
                self._draw_entry(screen, i, country, wins, panel_x + 15, y, font_small, emoji_font)

        screen.set_clip(old_clip)

    def _draw_entry(self, screen, rank, country, wins, x, y, font_small, emoji_font):
        if rank == 0:
            medal = "🥇.  "
            color = (255, 200, 50)
        elif rank == 1:
            medal = "🥈.  "
            color = (22, 164, 224)
        elif rank == 2:
            medal = "🥉.  "
            color = (224, 22, 76)
        else:
            medal = f"{rank+1}. "
            color = (159, 189, 184)

        short_name = country if len(country) <= 14 else country[:11] + "…"
        text_str = f"{medal}{short_name}: {wins}"
        try:
            text_surf = emoji_font.render(text_str, True, color)
        except:
            text_surf = font_small.render(text_str, True, color)
        screen.blit(text_surf, (x, y))
        if rank == 0:
            try:
                glow = emoji_font.render(text_str, True, (255, 255, 180))
                glow.set_alpha(70)
                screen.blit(glow, (x + 2, y + 2))
            except:
                pass

class LikeBarPanel:

    """
    Dinamik ve Animasyonlu Beğeni Barı.
    Hedefe ulaşınca parlar, yeni hedef belirlendiğinde akıcı bir şekilde (Lerp) geri kayar.
    """
    def sync_initial_likes(self, start_likes):
        while start_likes >= self.current_target:
            self.prev_target = self.current_target
            self.current_target = get_next_like_target(self.current_target)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cfg = LIKE_BAR_SETTINGS
        self.prev_target = 0
        self.current_target = self.cfg["initial_target"]

        # Görsel animasyon değişkenleri
        self.visual_width = 0.0  # Barın ekranda çizilen gerçek genişliği (Akıcılık için)
        self.flash_timer = 0     # Hedef dolduğunda parlaması için sayaç
        
        # Bellek sızıntısını önlemek için önbellek (cache) değişkenleri
        self.bar_surface = pygame.Surface((self.cfg["width"], self.cfg["height"]), pygame.SRCALPHA)
        self.cached_likes = -1
        self.cached_target = -1
        self.like_surf = None
        self.target_surf = None
        self.cta_surf = None
        self.shadow_surf = None

    def check_level_up(self, current_likes):
        if current_likes >= self.current_target:
            self.prev_target = self.current_target
            self.current_target = get_next_like_target(self.current_target)
            self.flash_timer = 15  # 15 frame boyunca (yaklaşık 0.25 sn) beyaz parlama animasyonu
            return True
        return False

    def draw(self, screen, current_likes, font_small, emoji_font):
        w, h = self.cfg["width"], self.cfg["height"]
        
        safe_likes = max(self.prev_target, min(current_likes, self.current_target))
        range_total = self.current_target - self.prev_target
        progress = safe_likes - self.prev_target
        # target_width = w * (progress / range_total if range_total > 0 else 0)

        # --- PSİKOLOJİK TEŞVİK (Minimum %15 Doluluk) ---
        # target_width = w * (progress / range_total if range_total > 0 else 0)
        actual_ratio = progress / range_total if range_total > 0 else 0
        min_width = w * 0.15  # %15'lik minimum başlangıç
        target_width = min_width + ((w - min_width) * actual_ratio)
        # -----------------------------------------------
        
        self.visual_width += (target_width - self.visual_width) * 0.1
        
        # HER FRAME YENİ YÜZEY YARATMAK YERİNE VAR OLANI TEMİZLE (Memory Leak Çözümü)
        self.bar_surface.fill((0, 0, 0, 0))
        
        bg_rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(self.bar_surface, (*self.cfg["bg_color"], self.cfg["alpha"]), bg_rect, border_radius=self.cfg["border_radius"])
        
        current_fill = max(0, int(self.visual_width))
        if current_fill > 0:
            fill_rect = pygame.Rect(0, 0, current_fill, h)
            fill_color = (255, 255, 255) if self.flash_timer > 0 else self.cfg["fill_color"]
            if self.flash_timer > 0: self.flash_timer -= 1
            pygame.draw.rect(self.bar_surface, (*fill_color, self.cfg["alpha"]), fill_rect, border_radius=self.cfg["border_radius"])
        
        screen.blit(self.bar_surface, (self.x, self.y))
        
        # FONT CACHE SİSTEMİ: Sadece sayılar değiştiğinde render et
        if self.cached_target != self.current_target:
            self.target_surf = font_small.render(str(self.current_target), True, (200, 200, 200))
            self.cached_target = self.current_target
            
        if self.cached_likes != current_likes:
            try:
                self.like_surf = emoji_font.render(f"{current_likes} ❤️", True, (200, 200, 200))
            except:
                self.like_surf = font_small.render(f"LIKE {current_likes}", True, (200, 200, 200))
            self.cached_likes = current_likes
        
        t_rect = self.target_surf.get_rect(midright=(self.x + w - 15, self.y + h // 2))
        screen.blit(self.target_surf, t_rect)
        
        like_x = max(self.x + 35, self.x + current_fill - 10)
        like_rect = self.like_surf.get_rect(midright=(like_x, self.y + h // 2))
        screen.blit(self.like_surf, like_rect)
        
        # SABİT CTA YAZISINI SADECE İLK ÇAĞRIDA BİR KEZ RENDER ET
        if self.cta_surf is None:
            cta_text, cta_color = "❤️ DOUBLE TAP! 👍", (179, 5, 5)
            try:
                self.cta_surf = emoji_font.render(cta_text, True, cta_color)
                self.shadow_surf = emoji_font.render(cta_text, True, (0, 0, 0))
            except:
                self.cta_surf = font_small.render(cta_text, True, cta_color)
                self.shadow_surf = font_small.render(cta_text, True, (0, 0, 0))
        
        time_ms = pygame.time.get_ticks()
        pulse_alpha = int(217 + 38 * math.sin(time_ms * 0.006)) 
        
        self.cta_surf.set_alpha(pulse_alpha)
        self.shadow_surf.set_alpha(pulse_alpha)
        
        cta_rect = self.cta_surf.get_rect(midbottom=(self.x + w // 2, self.y - 5))
        for ox, oy in [(-1, 1), (1, 1), (0, 2)]:
            screen.blit(self.shadow_surf, (cta_rect.x + ox, cta_rect.y + oy))
        screen.blit(self.cta_surf, cta_rect)

# class NextFlagsPanel:
#     """Next flags panel independent component"""

#     def __init__(self, x, y, config=None):
#         self.x = x
#         self.y = y
#         self.cfg = config or NEXT_FLAGS_PANEL
#         self.scroll_offset = 0.0
#         self.direction = 1
#         self.pause_timer = 0
#         self.last_tick = pygame.time.get_ticks()
        
#         # STATIK ARKA PLAN VE GÖLGESİ (1 kez oluştur)
#         cfg = self.cfg
#         panel_w = cfg["width"]
#         MAX_VISIBLE = cfg["max_visible_items"]
#         ROW_HEIGHT = cfg["row_height"]
#         HEADER_H = cfg["header_height"]
#         panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)
        
#         # Gölge surface'i
#         self.shadow_surf = pygame.Surface((panel_w, panel_h))
#         self.shadow_surf.set_alpha(cfg["shadow_alpha"])
#         self.shadow_surf.fill(COLOR_SHADOW)
        
#         # Arka plan surface'i
#         self.bg_surf = pygame.Surface((panel_w, panel_h))
#         self.bg_surf.set_alpha(cfg["panel_alpha"])
#         self.bg_surf.fill(COLOR_PANEL_BG)
        
#         # Başlık yazısı
#         try:
#             self.title_surf = pygame.font.SysFont("segoeuiemoji", 16, bold=True).render("🚩 NEXT FLAGS", True, cfg["title_color_nf"])
#         except:
#             self.title_surf = pygame.font.SysFont("Arial", 16, bold=True).render("NEXT FLAGS", True, cfg["title_color_nf"])

#     def draw(self, screen, next_round_queue, font_small, emoji_font, flag_manager=None):
#         if next_round_queue is None or flag_manager is None:
#             return
#         cfg = self.cfg
#         items = list(next_round_queue.items())
#         total_items = len(items)
#         MAX_VISIBLE = cfg["max_visible_items"]
#         ROW_HEIGHT = cfg["row_height"]
#         HEADER_H = cfg["header_height"]
#         panel_w = cfg["width"]
#         panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)
#         panel_x = self.x
#         panel_y = self.y

#         # animation
#         time_ms = pygame.time.get_ticks()
#         h_offset = int(
#             ANIMATIONS["panel_oscillation"]["amplitude"] *
#             math.sin(time_ms * ANIMATIONS["panel_oscillation"]["frequency"])
#         )
#         panel_x += h_offset

#         # STATIK GÖLGEYİ VE ARKA PLANI BLITLE
#         screen.blit(self.shadow_surf, (panel_x + cfg["shadow_offset"], panel_y + cfg["shadow_offset"]))
#         screen.blit(self.bg_surf, (panel_x, panel_y))

#         # STATIK BAŞLIK YAZISINI BLITLE
#         screen.blit(self.title_surf, (panel_x + cfg["title_offset_x"], panel_y + cfg["title_offset_y"]))

#         if len(items) == 0:
#             center_x = panel_x + (panel_w // 2)
#             center_y = panel_y + HEADER_H + ((panel_h - HEADER_H) // 2)
#             t1 = font_small.render("TYPE YOUR", True, COLOR_EMPTY_MSG)
#             r1 = t1.get_rect(center=(center_x, center_y - 20))
#             screen.blit(t1, r1)
#             t2 = font_small.render("COUNTRY", True, COLOR_EMPTY_MSG)
#             r2 = t2.get_rect(center=(center_x, center_y))
#             screen.blit(t2, r2)
#             t3 = font_small.render(". . .", True, COLOR_EMPTY_MSG)
#             r3 = t3.get_rect(center=(center_x, center_y+30))
#             screen.blit(t3, r3)
#             t4 = font_small.render("NO EMOJİ", True, EASTER_EGG["color"])
#             r4 = t4.get_rect(center=(center_x, center_y+60))
#             screen.blit(t4, r4)
#             return

#         # scrolling logic
#         if total_items <= MAX_VISIBLE:
#             scroll_y = 0
#         else:
#             total_scroll = (total_items - MAX_VISIBLE) * ROW_HEIGHT
#             current_tick = pygame.time.get_ticks()
#             dt = (current_tick - self.last_tick) / 1000.0
#             self.last_tick = current_tick
#             if self.pause_timer > 0:
#                 self.pause_timer -= dt * 1000
#                 if self.pause_timer <= 0:
#                     self.direction *= -1
#             else:
#                 SCROLL_SPEED = cfg["scroll_speed"]
#                 self.scroll_offset += self.direction * SCROLL_SPEED * dt
#                 if self.scroll_offset >= total_scroll and self.direction == 1:
#                     self.scroll_offset = total_scroll
#                     self.pause_timer = cfg["scroll_pause_duration_ms"]
#                 elif self.scroll_offset <= 0 and self.direction == -1:
#                     self.scroll_offset = 0
#                     self.pause_timer = cfg["scroll_pause_duration_ms"]
#                 self.scroll_offset = max(0.0, min(self.scroll_offset, total_scroll))
#             scroll_y = self.scroll_offset

#         view_y_start = panel_y + HEADER_H
#         view_y_end = panel_y + panel_h
#         clip = pygame.Rect(panel_x, view_y_start, panel_w, panel_h - HEADER_H)
#         clip.inflate_ip(0, -2)
#         old_clip = screen.get_clip()
#         screen.set_clip(clip)

#         FLAG_W, FLAG_H = 30, 20
#         for i, (name, info) in enumerate(items):
#             y_pos = view_y_start + i * ROW_HEIGHT - scroll_y
#             if view_y_start - ROW_HEIGHT < y_pos < view_y_end:
#                 flag_data = flag_manager.get_flag_by_code(info["code"], FLAG_W, FLAG_H)
#                 if flag_data.get("image"):
#                     flag_img = flag_data["image"]
#                     img_y = y_pos + (ROW_HEIGHT - FLAG_H) // 2
#                     screen.blit(flag_img, (panel_x + 15, img_y))
#                 short_name = name if len(name) <= 15 else name[:13] + ".."
#                 name_color = (200, 200, 200)
#                 try:
#                     txt_surf = font_small.render(short_name, True, name_color)
#                 except:
#                     txt_surf = pygame.font.SysFont("Arial", 14).render(short_name, True, name_color)
#                 txt_y = y_pos + (ROW_HEIGHT - txt_surf.get_height()) // 2
#                 screen.blit(txt_surf, (panel_x + 15 + FLAG_W + 10, txt_y))
#                 if info["count"] > 1:
#                     count_str = f"x{info['count']}"
#                     count_surf = font_small.render(count_str, True, COLOR_GOLD)
#                     c_x = panel_x + panel_w - count_surf.get_width() - 5
#                     screen.blit(count_surf, (c_x, txt_y))
#         screen.set_clip(old_clip)


class NextFlagsPanel:
    """Yatay Next Flags Paneli (Çemberin Üzerinde)"""

    def __init__(self, x, y, config=None):
        self.x = x  # Panelimizin X koordinatı
        self.y = y  # Panelimizin Y koordinatı

        self.cfg = config or NEXT_FLAGS_PANEL
        self.scroll_offset = 0.0
        self.direction = 1
        self.pause_timer = 0
        self.last_tick = pygame.time.get_ticks()
        
        # STATIK ARKA PLAN VE GÖLGESİ (1 kez oluştur)
        cfg = self.cfg
        self.panel_w = cfg["width"]
        self.panel_h = cfg["height"]
        self.header_h = cfg["header_height"]
        
        # Gölge surface'i
        # self.shadow_surf = pygame.Surface((self.panel_w, self.panel_h))
        # self.shadow_surf.set_alpha(cfg["shadow_alpha"])
        # self.shadow_surf.fill(COLOR_SHADOW)
        
        # Arka plan surface'i
        self.bg_surf = pygame.Surface((self.panel_w, self.panel_h))
        self.bg_surf.set_alpha(cfg["panel_alpha"])
        self.bg_surf.fill(COLOR_PANEL_BG)
        
        # Başlık yazısı
        try:
            self.title_surf = pygame.font.SysFont("segoeuiemoji", 16, bold=True).render("🚩 NEXT FLAGS", True, cfg["title_color_nf"])
        except:
            self.title_surf = pygame.font.SysFont("Arial", 16, bold=True).render("NEXT FLAGS", True, cfg["title_color_nf"])

            # Bellek sızıntısını önlemek için yedek fontu bir kez belleğe al
        self.fallback_font = pygame.font.SysFont("Arial", 12)

    def draw(self, screen, next_round_queue, font_small, emoji_font, flag_manager=None):
        if next_round_queue is None or flag_manager is None:
            return
            
        cfg = self.cfg
        items = list(next_round_queue.items())
        total_items = len(items)
        
       # 1. KONUMLANDIRMA VE AŞAĞI-YUKARI SALINIM
        panel_x = self.x
        panel_y = self.y
        # Aşağı-yukarı salınım animasyonu
        # time_ms = pygame.time.get_ticks()
        # v_offset = int(
        #     cfg["vertical_oscillation_amplitude"] *
        #     math.sin(time_ms * cfg["oscillation_frequency"])
        # )
        # panel_y += v_offset

        # 2. STATİK ÇİZİMLER (Gölge, Arka plan, Başlık)
        # screen.blit(self.shadow_surf, (panel_x + cfg["shadow_offset"], panel_y + cfg["shadow_offset"]))
        screen.blit(self.bg_surf, (panel_x, panel_y))
        
        title_rect = self.title_surf.get_rect(center=(panel_x + self.panel_w // 2, panel_y + self.header_h // 2))
        screen.blit(self.title_surf, title_rect)

        # 3. LİSTE BOŞSA
        if total_items == 0:
            center_x = panel_x + (self.panel_w // 2)
            center_y = panel_y + self.header_h + ((self.panel_h - self.header_h) // 2)
            t1 = font_small.render("TYPE YOUR COUNTRY", True, COLOR_EMPTY_MSG)
            r1 = t1.get_rect(center=(center_x, center_y - 10))
            screen.blit(t1, r1)
            t2 = font_small.render("NO EMOJI", True, (255, 100, 100))
            r2 = t2.get_rect(center=(center_x, center_y + 10))
            screen.blit(t2, r2)
            return

        # 4. YATAY KAYDIRMA (SCROLL) MANTIĞI
        item_w = cfg["item_width"]
        content_width = total_items * item_w
        view_w = self.panel_w - 20 # Sağ ve soldan 10'ar px boşluk

        if content_width <= view_w:
            scroll_x = 0
        else:
            total_scroll = content_width - view_w
            current_tick = pygame.time.get_ticks()
            dt = (current_tick - self.last_tick) / 1000.0
            self.last_tick = current_tick
            
            if self.pause_timer > 0:
                self.pause_timer -= dt * 1000
                if self.pause_timer <= 0:
                    self.direction *= -1
            else:
                SCROLL_SPEED = cfg["scroll_speed"]
                self.scroll_offset += self.direction * SCROLL_SPEED * dt
                if self.scroll_offset >= total_scroll and self.direction == 1:
                    self.scroll_offset = total_scroll
                    self.pause_timer = cfg["scroll_pause_duration_ms"]
                elif self.scroll_offset <= 0 and self.direction == -1:
                    self.scroll_offset = 0
                    self.pause_timer = cfg["scroll_pause_duration_ms"]
                self.scroll_offset = max(0.0, min(self.scroll_offset, total_scroll))
            scroll_x = self.scroll_offset

        # 5. KIRPMA (CLIPPING) ALANI YATAY UYGULA
        view_x_start = panel_x + 10
        view_y_start = panel_y + self.header_h
        clip = pygame.Rect(view_x_start, view_y_start, view_w, self.panel_h - self.header_h)
        
        old_clip = screen.get_clip()
        screen.set_clip(clip)

        # 6. ÖGELERİ (KAPSAYICI KUTULARLA BİRLİKTE) YATAY DİZ
        FLAG_W, FLAG_H = 45, 30
        # for i, (name, info) in enumerate(items):
        #     item_x = view_x_start + (i * item_w) - scroll_x
            
        #     # Eğer kutu ekran (kırpma alanı) dışındaysa çizimle vakit kaybetme
        #     if item_x + item_w < view_x_start or item_x > view_x_start + view_w:
        #         continue
                
        #     # A) Kapsayıcı Kutu (Item Container)
        #     box_rect = pygame.Rect(item_x + 5, view_y_start + 5, item_w - 10, self.panel_h - self.header_h - 15)
        #     pygame.draw.rect(screen, (50, 50, 50), box_rect, border_radius=8) # İç zemin
        #     pygame.draw.rect(screen, (100, 100, 100), box_rect, width=1, border_radius=8) # Çerçeve
            
        #     # B) Bayrak Resmi (Kutunun üstünde ortalı)
        #     flag_data = flag_manager.get_flag_by_code(info["code"], FLAG_W, FLAG_H)
        #     if flag_data.get("image"):
        #         flag_img = flag_data["image"]
        #         img_rect = flag_img.get_rect(midtop=(box_rect.centerx, box_rect.top + 8))
        #         screen.blit(flag_img, img_rect)
                
        #         # C) Sayı (x2) - Kutunun sağ kenarına
        #         if info["count"] > 1:
        #             count_str = f"x{info['count']}"
        #             count_surf = font_small.render(count_str, True, (255, 215, 0)) # COLOR_GOLD
        #             c_rect = count_surf.get_rect(bottomright=(box_rect.right - 5, img_rect.bottom + 5))
                    
        #             # Okunabilirliği artırmak için küçük siyah arka plan
        #             c_bg = c_rect.inflate(4, 2)
        #             pygame.draw.rect(screen, (0, 0, 0, 180), c_bg, border_radius=3)
        #             screen.blit(count_surf, c_rect)

        #     # D) Ülke Adı (Kutunun altında ortalı)
        #     short_name = name if len(name) <= 12 else name[:10] + ".."
        #     try:
        #         txt_surf = font_small.render(short_name, True, (220, 220, 220))
        #     except:
        #         txt_surf = pygame.font.SysFont("Arial", 12).render(short_name, True, (220, 220, 220))
            
        #     txt_rect = txt_surf.get_rect(midbottom=(box_rect.centerx, box_rect.bottom - 5))
        #     screen.blit(txt_surf, txt_rect)

        # --- BELLEK VE RENDER OPTİMİZASYONU ---
        start_idx = max(0, int(scroll_x // item_w))
        visible_count = (view_w // item_w) + 2 
        end_idx = min(total_items, start_idx + visible_count)

        for i in range(start_idx, end_idx):
            name, info = items[i]
            item_x = view_x_start + (i * item_w) - scroll_x
            
            if item_x + item_w < view_x_start or item_x > view_x_start + view_w:
                continue
                
            box_rect = pygame.Rect(item_x + 5, view_y_start + 5, item_w - 10, self.panel_h - self.header_h - 15)
            pygame.draw.rect(screen, (50, 50, 50), box_rect, border_radius=8)
            pygame.draw.rect(screen, (100, 100, 100), box_rect, width=1, border_radius=8)
            
            flag_data = flag_manager.get_flag_by_code(info["code"], FLAG_W, FLAG_H)
            if flag_data.get("image"):
                flag_img = flag_data["image"]
                img_rect = flag_img.get_rect(midtop=(box_rect.centerx, box_rect.top + 8))
                screen.blit(flag_img, img_rect)
                
                if info["count"] > 1:
                    count_str = f"x{info['count']}"
                    count_surf = font_small.render(count_str, True, (255, 215, 0))
                    c_rect = count_surf.get_rect(bottomright=(box_rect.right - 5, img_rect.bottom + 5))
                    c_bg = c_rect.inflate(4, 2)
                    pygame.draw.rect(screen, (0, 0, 0, 180), c_bg, border_radius=3)
                    screen.blit(count_surf, c_rect)

            short_name = name if len(name) <= 12 else name[:10] + ".."
            try:
                txt_surf = font_small.render(short_name, True, (220, 220, 220))
            except:
                # RAM sızıntısını önlemek için önceden yüklenmiş fontu kullan
                txt_surf = self.fallback_font.render(short_name, True, (220, 220, 220))
            
            txt_rect = txt_surf.get_rect(midbottom=(box_rect.centerx, box_rect.bottom - 5))
            screen.blit(txt_surf, txt_rect)

        screen.set_clip(old_clip)
        

class EasterEggBanner:
    """
    Basit metin banner componenti - TAMAMEN STATIK
    
    __init__'de tüm arka plan, gölge, yazı ve çerçeveyi tek bir Surface'te 
    oluşturur. draw() metodunda sadece bu hazır Surface'i blit eder.
    """

    def __init__(self, x, y, config=None):
        self.x = x
        self.y = y
        cfg = config or EASTER_EGG
        self.text = cfg.get("text", "67 = BAN!")
        
        # Yazı oluştur
        font = pygame.font.SysFont(cfg["font_name"], cfg["font_size"])
        text_surf = font.render(self.text, True, cfg["color"])
        text_rect = text_surf.get_rect()
        
        # Arka plan ve padding hesapla
        bg_rect = text_rect.inflate(6, 2)
        
        # TAMAMEN STATIK SURFACE: arka plan + yazı + gölge
        # İşlem sırası: gölge -> arka plan -> yazı
        self.static_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        
        # Arka plan
        bg_surf_temp = pygame.Surface((bg_rect.width, bg_rect.height))
        bg_surf_temp.set_alpha(cfg["bg_alpha"])
        bg_surf_temp.fill(cfg["bg_color"])
        self.static_surface.blit(bg_surf_temp, (0, 0))
        
        # Yazı (merkeze)
        text_offset_x = (bg_rect.width - text_rect.width) // 2
        text_offset_y = (bg_rect.height - text_rect.height) // 2
        self.static_surface.blit(text_surf, (text_offset_x, text_offset_y))
        
        # Merkez noktası (0,0)'da olacak şekilde rect'i oluştur
        self.rect = self.static_surface.get_rect(center=(0, 0))

    def draw(self, screen):
        """
        Hazır statik surface'i ekrana blit et.
        Hesaplama yok, sadece tek bir blit işlemi.
        """
        screen.blit(self.static_surface, (self.x - self.rect.width // 2, self.y - self.rect.height // 2))
