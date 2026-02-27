import pygame
import pymunk
import pymunk.pygame_util
import math
import random
import os
import time
import pycountry
import pygame.gfxdraw
import threading
import pytchat
import json
from settings import *
#exe
import sys
import os
def resource_path(relative_path):
    """PyInstaller ile derlenmiş EXE'de dosya yolunu bulur."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# hatalar kısaltmalar sıkıntılı, gereksiz bayrak birikimi oluyor.
# # --- SABİTLER VE BAŞLANGIÇ AYARLARI ---
# WIDTH, HEIGHT = 1080,1080
# CIRCLE_CENTER = (WIDTH // 2, HEIGHT // 2 - 3) #çemberle lider tablosu arası 7 px dusur artsın.
# FLAGS_FOLDER = "flags"
# BACKGROUND_FILE_NAME = "background.jpg" # Resmin tam adı ve uzantısı bu olmalı!

# # --- ÖNEMLİ AYARLAR ---
# MAX_VELOCITY = 250.0  #200 du

# # Varsayılan Ayarlar
# SETTINGS = {
#     "gravity": 40,    #40      
#     "flag_size": 15,        
#     "initial_gap": 30,      #30
#     "round_time": 20,       
#     "auto_spawn": 30,       #40
#     "rotation_speed": 1.5   #2.0
# }

# # Hesaplanan/Sabit Ayarlar
# INTERNAL_SETTINGS = {
#     "circle_radius": 170,   
#     "elasticity": 1.1,      
#     "wall_thickness": 12
# }

# # Renkler
# COLOR_BG = (20, 20, 20)
# COLOR_TEXT = (255, 255, 255)
# COLOR_ACCENT = (0, 255, 0)
# COLOR_COUNTDOWN = (180, 0, 255) 
# COLOR_GOLD = (255, 215, 0)
# COLOR_SILVER = (192, 192, 192)
# COLOR_BRONZE = (205, 127, 50)
# COLOR_NEXT_FLAG_BG = (30, 30, 60)

# ... (Üstteki importlar ve ayarlar aynı kalsın) ...

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flag Battle Royale - Live Edition")
pygame.scrap.init() 

# --- ARKA PLAN RESMİ YÜKLEME (DEBUG MODU) ---
# background_surface = None
# try:
#     # # 1. game.py dosyasının olduğu gerçek klasörü bul
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     # bg_path = os.path.join(script_dir, BACKGROUND_FILE_NAME)
    
#     #  exe
#     bg_path = resource_path(BACKGROUND_FILE_NAME)   

#     try:
#      bg_img = pygame.image.load(bg_path).convert()
#      background_surface = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
#     except Exception as e:
#      print(f"Arkaplan yüklenemedi: {e}")
#      background_surface = None
#     #  exe
#     print("\n" + "="*40)
#     print("--- ARKA PLAN YÜKLEME RAPORU ---")
#     print(f"1. Oyunun Klasörü: {script_dir}")
#     print(f"2. Aranan Dosya:   {BACKGROUND_FILE_NAME}")
    
#     # 3. Klasördeki dosyaları kontrol et
#     print("3. Bu klasörde bulunan dosyalar:")
#     files_in_dir = os.listdir(script_dir)
#     found = False
#     for f in files_in_dir:
#         # Dosya adını yazdır
#         print(f"   - {f}")
#         if f.lower() == BACKGROUND_FILE_NAME.lower():
#             found = True

#     print("-" * 30)

#     if found:
#         print(f"SONUÇ: Dosya bulundu! Yükleniyor...")
#         bg_img = pygame.image.load(bg_path).convert()
#         background_surface = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
#         print("BAŞARILI: Arka plan oyuna eklendi.")
#     else:
#         print(f"HATA: '{BACKGROUND_FILE_NAME}' dosyası bu klasörde GÖRÜNMÜYOR.")
#         print("İPUCU: Dosya adınız 'background.jpg.jpg' olmuş olabilir mi?")
#         print("       Lütfen yukarıdaki dosya listesini kontrol edin.")
    
#     print("="*40 + "\n")

# except Exception as e:
#     print(f"KRİTİK HATA: Resim yüklenirken şu hata oluştu:\n{e}")
#     background_surface = None
# # ------------------------------------------------

# clock = pygame.time.Clock()

# --- ARKA PLAN RESMİ YÜKLEME ---
background_surface = None
bg_path = resource_path(BACKGROUND_FILE_NAME)
try:
    bg_img = pygame.image.load(bg_path).convert()
    background_surface = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    print("Arka plan başarıyla yüklendi.")
except Exception as e:
    print(f"Arka plan yüklenemedi: {e}")
    background_surface = None

#-FONT
entry_font = pygame.font.SysFont("Courier New", 18, bold=True)
# --- EMOJI DESTEKLİ FONT (Windows: Segoe UI Emoji, macOS: Apple Color Emoji, Linux: Noto Color Emoji) ---
emoji_font = None
emoji_font_paths = [
    "C:/Windows/Fonts/seguiemj.ttf",          # Windows 10/11
   # "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
   # "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"  # Linux
]
for path in emoji_font_paths:
    if os.path.exists(path):
        try:
            emoji_font = pygame.font.Font(path, 20)
            print(f"Emoji font yüklendi: {path}")
            break
        except:
            continue

if emoji_font is None:
    print("Emoji font bulunamadı, yedek font kullanılacak.")
    emoji_font = pygame.font.SysFont("Arial", 20, bold=True)  # yedek
#font

clock = pygame.time.Clock()

pymunk.pygame_util.positive_y_is_up = False
font_small = pygame.font.SysFont("Arial", 12, bold=True)
font_ui = pygame.font.SysFont("Arial", 16, bold=True)
font_big = pygame.font.SysFont("Arial", 60, bold=True)
font_leaderboard = pygame.font.SysFont("Arial", 14, bold=True)

# --- GLOBAL DEĞİŞKENLER ---
LEADERBOARD = {}
NEXT_ROUND_QUEUE = {} 
CHAT_THREAD = None
IS_CHAT_RUNNING = False
VIDEO_ID_INPUT = "YT Live Video ID" 

is_round_recorded = False

# --- YARDIMCI: Ülke Bulma ---
def find_country_code(text):
    if len(text) < 3: return None  # 3 harften kısaysa aramayı iptal et
    text = text.strip().title()
    try:
        return pycountry.countries.lookup(text).alpha_2
    except:
        try:
            res = pycountry.countries.search_fuzzy(text)
            if res: return res[0].alpha_2
        except:
            return None

# --- THREAD: SOHBET DİNLEYİCİ ---
def chat_listener_task(chat_obj):
    global NEXT_ROUND_QUEUE, IS_CHAT_RUNNING
    print("Chat thread basladi...")
    IS_CHAT_RUNNING = True
    
    try:
        while IS_CHAT_RUNNING and chat_obj.is_alive():
            for c in chat_obj.get().sync_items():
                msg = c.message
                code = find_country_code(msg)
                if code:
                    try:
                        std_name = pycountry.countries.get(alpha_2=code).name
                    except:
                        std_name = msg
                    
                    if std_name in NEXT_ROUND_QUEUE:
                        NEXT_ROUND_QUEUE[std_name]["count"] += 1
                    else:
                        NEXT_ROUND_QUEUE[std_name] = {"code": code, "count": 1}
                    
                    print(f"Sıraya eklendi: {std_name} (x{NEXT_ROUND_QUEUE[std_name]['count']})")
            
            time.sleep(0.5) 
    except Exception as e:
        print(f"Chat thread hatasi: {e}")
    finally:
        IS_CHAT_RUNNING = False
        print("Chat thread sonlandi.")

# --- UI SINIFLARI ---

# --- TEXTBOX ---
class TextBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.select_all = False 

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
                self.select_all = False 
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                ctrl_held = (event.mod & pygame.KMOD_CTRL)

                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.select_all = False
                
                elif ctrl_held and event.key == pygame.K_a:
                    self.select_all = True
                
                elif ctrl_held and event.key == pygame.K_c:
                    if self.text:
                        pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode("utf-8"))

                elif ctrl_held and event.key == pygame.K_x:
                    if self.text:
                        pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode("utf-8"))
                        self.text = ""
                        self.select_all = False

                elif ctrl_held and event.key == pygame.K_v:
                    content = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if content:
                        try:
                            paste_text = content.decode("utf-8").strip("\x00")
                            if self.select_all:
                                self.text = paste_text 
                                self.select_all = False
                            else:
                                self.text += paste_text 
                        except:
                            pass 

                elif event.key == pygame.K_BACKSPACE:
                    if self.select_all:
                        self.text = "" 
                        self.select_all = False
                    else:
                        self.text = self.text[:-1]
                
                else:
                    if not ctrl_held:
                        if self.select_all:
                            self.text = event.unicode 
                            self.select_all = False
                        else:
                            self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, (30, 30, 30), self.rect)
        
        if self.select_all and self.active:
            selection_rect = self.rect.inflate(-4, -4)
            pygame.draw.rect(screen, (0, 100, 200), selection_rect)

        txt_surface = font_ui.render(self.text, True, COLOR_TEXT)
        text_y = self.rect.y + (self.rect.height - txt_surface.get_height()) // 2
        screen.blit(txt_surface, (self.rect.x + 5, text_y))
        
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.text = text
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                ratio = (mouse_x - self.rect.x) / self.rect.width
                ratio = max(0, min(1, ratio))
                self.val = self.min_val + (self.max_val - self.min_val) * ratio

    def draw(self, screen):
        val_str = f"{int(self.val)}"
        if "Donme" in self.text: val_str = f"{self.val:.1f}"
        
        label = font_ui.render(f"{self.text}: {val_str}", True, COLOR_TEXT)
        screen.blit(label, (self.rect.x, self.rect.y - 20))
        pygame.draw.rect(screen, (100, 100, 100), self.rect, border_radius=5)
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width * ratio)
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
        pygame.draw.rect(screen, COLOR_ACCENT, handle_rect, border_radius=5)

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_ACCENT, self.rect, border_radius=8)
        label = font_ui.render(self.text, True, (0, 0, 0))
        text_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, text_rect)

# --- FLAG MANAGER ---
class FlagManager:
    def __init__(self, folder_path):
        # self.folder_path = folder_path
        self.folder_path = resource_path(folder_path)   #exe
        self.flags_data = [] 
        self.load_flags()

    def load_flags(self):
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
            return
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".png") or filename.endswith(".jpg"):
                country_code = filename.split(".")[0].upper()
                try:
                    country = pycountry.countries.get(alpha_2=country_code)
                    full_name = country.name if country else country_code
                except:
                    full_name = country_code 
                try:
                    path = os.path.join(self.folder_path, filename)
                    img = pygame.image.load(path).convert_alpha()
                    self.flags_data.append({"raw_img": img, "name": full_name, "code": country_code})
                except Exception as e:
                    print(f"Hata: {filename} {e}")

    def get_flag_by_code(self, code, target_w, target_h):
        code = code.upper()
        for data in self.flags_data:
            if data["code"] == code:
                scaled = pygame.transform.scale(data["raw_img"], (int(target_w), int(target_h)))
                return {"image": scaled, "name": data["name"], "original": data["raw_img"]}
        return self.get_random_flag(target_w, target_h)

    def get_random_flag(self, target_w, target_h):
        if not self.flags_data:
            fallback = pygame.Surface((int(target_w), int(target_h)))
            fallback.fill((200, 200, 200))
            return {"image": fallback, "name": "No Flag"}
        data = random.choice(self.flags_data)
        scaled = pygame.transform.scale(data["raw_img"], (int(target_w), int(target_h)))
        return {"image": scaled, "name": data["name"], "original": data["raw_img"]}

flag_manager = FlagManager(FLAGS_FOLDER)

# --- FİZİK ---
def rebuild_circle_segments(space, body, radius, gap_angle_deg):
    for shape in list(space.shapes):
        if shape.body == body and isinstance(shape, pymunk.Segment):
            space.remove(shape)
    
    res = 120
    gap_start = -gap_angle_deg / 2
    gap_end = gap_angle_deg / 2
    
    for i in range(res):
        angle_start = (i / res) * 360
        angle_end = ((i + 1) / res) * 360
        if gap_start <= (angle_start - 50) <= gap_end:
            continue
        as_rad = math.radians(angle_start)
        ae_rad = math.radians(angle_end)
        p1 = (radius * math.cos(as_rad), radius * math.sin(as_rad))
        p2 = (radius * math.cos(ae_rad), radius * math.sin(ae_rad))
        
        segment = pymunk.Segment(body, p1, p2, INTERNAL_SETTINGS["wall_thickness"])
        segment.elasticity = INTERNAL_SETTINGS["elasticity"]
        segment.friction = 0.5 
        segment.color = (0, 255, 0, 255) 
        space.add(segment)

def create_circle_body(space, pos, rotation_speed):
    body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    body.position = pos
    body.angular_velocity = rotation_speed
    space.add(body)
    return body

def limit_velocity(body, gravity, damping, dt):
    pymunk.Body.update_velocity(body, gravity, damping, dt)
    l = body.velocity.length
    if l > MAX_VELOCITY:
        scale = MAX_VELOCITY / l
        body.velocity = body.velocity * scale

def spawn_flag(space, pos, radius, specific_data=None):
    mass = 10 
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = pos
    body.velocity_func = limit_velocity
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = INTERNAL_SETTINGS["elasticity"]
    shape.friction = 0.5 
    
    w = radius * 2.2
    h = radius * 1.5
    
    if specific_data:
        shape.custom_data = specific_data
    else:
        shape.custom_data = flag_manager.get_random_flag(w, h)
        
    space.add(body, shape)
    return shape

def draw_smooth_segment(screen, p1, p2, thickness, color):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.sqrt(dx*dx + dy*dy)
    if dist == 0: return
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

# --- ARAYÜZ FONKSİYONLARI ---
def draw_leaderboard_panel(screen):
    if not LEADERBOARD:
        return
    #tutulacak top winners sayısı 15
    sorted_winners = sorted(LEADERBOARD.items(), key=lambda item: item[1], reverse=True)[:15]
    total_items = len(sorted_winners)

    MAX_VISIBLE = 10
    ROW_HEIGHT = 20 #32 idi
    HEADER_H = 45
    panel_w = 300
    panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)

    # --- Liderlik Panel Konumu ---
    circle_center_x = CIRCLE_CENTER[0]
    circle_center_y = CIRCLE_CENTER[1]
    circle_radius = INTERNAL_SETTINGS["circle_radius"]
    # panel_x = circle_center_x + circle_radius + 30
    # panel_y = circle_center_y - (panel_h // 2)

    panel_x = (WIDTH - panel_w) // 2   # yatayda ortala
    panel_y = 90                       # üstten 60px boşluk

    if panel_x + panel_w > WIDTH - 20:
        panel_x = WIDTH - panel_w - 20
        

    # --- Hafif yukarı-aşağı salınım ---
    time_ms = pygame.time.get_ticks()
    #dikey eksen
    # float_offset = int(6 * math.sin(time_ms * 0.002))
    # panel_y += float_offset

    #yatay eksen
    h_offset = int(6 * math.sin(time_ms * 0.002))
    panel_x += h_offset

    # --- Gölge + arkaplan ---
    shadow_offset = 5
    s_shadow = pygame.Surface((panel_w, panel_h))
    s_shadow.set_alpha(100)
    s_shadow.fill((0, 0, 0))
    screen.blit(s_shadow, (panel_x + shadow_offset, panel_y + shadow_offset))

    s = pygame.Surface((panel_w, panel_h))
    s.set_alpha(200)
    s.fill((12, 12, 24))
    screen.blit(s, (panel_x, panel_y))

    # --- Başlık (sabit) ---
    # --- Başlık (sabit) ---
    try:
        # Varsa global emoji fontunu kullan (Emoji görünsün diye)
        title = emoji_font.render("👑 TOP WINNERS", True, (255, 220, 40))
    except:
        # Yoksa Arial kullan (Kare görünür ama hata vermez)
        title_font = pygame.font.SysFont("Arial", 22, bold=True)
        title = title_font.render("TOP WINNERS", True, (255, 220, 40)) # Emojiyi sildik burdan
        
    screen.blit(title, (panel_x + 15, panel_y + 8))

    # --- Eğer 10 veya daha az ülke varsa: sabit liste (kaydırma yok) ---
    if total_items <= MAX_VISIBLE:
        start_y = panel_y + HEADER_H
        for i, (country, wins) in enumerate(sorted_winners):
            y_pos = start_y + i * ROW_HEIGHT
            draw_leaderboard_entry(screen, i, country, wins, panel_x + 15, y_pos)
        return

    # --- 10'dan fazla ülke: ÇİFT YÖNLÜ YUMUŞAK KAYDIRMA + BEKLEME ---
    total_scroll = (total_items - MAX_VISIBLE) * ROW_HEIGHT

    # Kalıcı değişkenler
    if not hasattr(draw_leaderboard_panel, "scroll_offset"):
        draw_leaderboard_panel.scroll_offset = 0.0
        draw_leaderboard_panel.direction = 1
        draw_leaderboard_panel.pause_timer = 0
        draw_leaderboard_panel.last_tick = pygame.time.get_ticks()

    current_tick = pygame.time.get_ticks()
    dt = (current_tick - draw_leaderboard_panel.last_tick) / 1000.0
    draw_leaderboard_panel.last_tick = current_tick

    SCROLL_SPEED = 40

    if draw_leaderboard_panel.pause_timer > 0:
        draw_leaderboard_panel.pause_timer -= dt * 1000
        if draw_leaderboard_panel.pause_timer <= 0:
            draw_leaderboard_panel.pause_timer = 0
            draw_leaderboard_panel.direction *= -1
    else:
        draw_leaderboard_panel.scroll_offset += draw_leaderboard_panel.direction * SCROLL_SPEED * dt

        if draw_leaderboard_panel.scroll_offset >= total_scroll and draw_leaderboard_panel.direction == 1:
            draw_leaderboard_panel.scroll_offset = total_scroll
            draw_leaderboard_panel.pause_timer = 3000
        elif draw_leaderboard_panel.scroll_offset <= 0 and draw_leaderboard_panel.direction == -1:
            draw_leaderboard_panel.scroll_offset = 0
            draw_leaderboard_panel.pause_timer = 3000

        draw_leaderboard_panel.scroll_offset = max(0.0, min(draw_leaderboard_panel.scroll_offset, total_scroll))

    # --- Görünür alan (liste satırlarının çizileceği bölge) ---
    view_y_start = panel_y + HEADER_H
    view_y_end = panel_y + panel_h

    # --- ÖNEMLİ: ÇİZİM ALANINI KISITLA (taşmaları engelle) ---
    # Tüm panelin içinde, sadece satırların olması gereken yeri kes
    entry_clip_rect = pygame.Rect(
        panel_x,                # X başlangıcı (tüm panel genişliği)
        view_y_start,          # Y başlangıcı (başlığın hemen altı)
        panel_w,              # genişlik
        panel_h - HEADER_H    # yükseklik (başlık hariç)
    )
    # Hafif iç boşluk ekle (yazıların tam kenarda kesilmesini önler)
    entry_clip_rect.inflate_ip(0, -4)  # dikeyde 2px üst, 2px alt boşluk

    old_clip = screen.get_clip()
    screen.set_clip(entry_clip_rect)

    # --- Satırları çiz (sadece görünür alana yakın olanları) ---
    for i, (country, wins) in enumerate(sorted_winners):
        y = view_y_start + (i * ROW_HEIGHT) - draw_leaderboard_panel.scroll_offset

        # Sadece kesme bölgesinin biraz dışına taşanları da çiz (kesme işlemi zaten yapacak)
        if view_y_start - ROW_HEIGHT < y < view_y_end:
            draw_leaderboard_entry(screen, i, country, wins, panel_x + 15, y)

    # --- Kesme bölgesini eski haline döndür ---
    screen.set_clip(old_clip)

def draw_leaderboard_entry(screen, rank, country, wins, x, y):
    """Verilen sıradaki ülke bilgisini ekrana çizer."""
    if rank == 0:
        medal = "🥇.  "
        color = (255, 200, 50)      # altın
    elif rank == 1:
        medal = "🥈.  "
        color = (22, 164, 224)     # baska
    elif rank == 2:
        medal = "🥉.  "
        color = 224, 22, 76      # baskaa
    else:
        medal = f"{rank+1}. "
        color = (159, 189, 184)

    short_name = country if len(country) <= 14 else country[:11] + "…"
    text_str = f"{medal}{short_name}: {wins}"

   

    # Emoji destekli font ile yazdır
    try:
        text_surf = emoji_font.render(text_str, True, color)
    except:
        entry_font = pygame.font.SysFont("Arial", 15, bold=True)
        text_surf = entry_font.render(text_str, True, color)

    screen.blit(text_surf, (x, y))

    # 1. sıraya hafif parlama efekti
    if rank == 0:
        try:
            glow = emoji_font.render(text_str, True, (255, 255, 180))
            glow.set_alpha(70)
            screen.blit(glow, (x + 2, y + 2))
        except:
            pass


# def draw_next_flags_panel(screen):
#     if not NEXT_ROUND_QUEUE: return
#     bg_h = 60
#     s = pygame.Surface((WIDTH, bg_h))
#     s.set_alpha(200)
#     s.fill(COLOR_NEXT_FLAG_BG)
#     #next flag yeri
#     screen.blit(s, (0, HEIGHT + 245))

#     title = font_small.render("NEXT FLAGS:", True, COLOR_ACCENT)
#     screen.blit(title, (10, 5))
#     start_x = 100
#     gap_x = 70
#     items = list(NEXT_ROUND_QUEUE.items())[:10] 
#     for i, (name, info) in enumerate(items):
#         flag_data = flag_manager.get_flag_by_code(info["code"], 40, 26)
#         img = flag_data["image"]
#         x_pos = start_x + (i * gap_x)
#         screen.blit(img, (x_pos, 5))
#         short_name = name[:7] + "." if len(name) > 7 else name
#         name_surf = font_small.render(short_name, True, (200, 200, 200))
#         screen.blit(name_surf, (x_pos, 35))
#         if info["count"] > 1:
#             count_surf = font_small.render(f"x{info['count']}", True, COLOR_GOLD)
#             screen.blit(count_surf, (x_pos + 42, 5))

def draw_next_flags_panel(screen):
    # if not NEXT_ROUND_QUEUE: #liste varsa göster yoksa
    #     return

    # --- Ayarlar ve Boyutlar ---
    # Top Winners panelinin özelliklerine benzer ayarlar
    items = list(NEXT_ROUND_QUEUE.items())
    total_items = len(items)
    
    MAX_VISIBLE = 5         # Aynı anda görünecek bayrak sayısı
    ROW_HEIGHT = 40         # Bayrak + boşluk yüksekliği (Lider tablosundan biraz daha geniş)
    HEADER_H = 40           # Başlık yüksekliği
    panel_w = 122           # Panel genişliği
    panel_h = HEADER_H + (MAX_VISIBLE * ROW_HEIGHT)

    # --- Konumlandırma Hesapları ---
    # Referans alınan Top Winners paneli (genişliği 300, y=120 varsayıldı)
    # Lider tablosu ekranın ortasında: (WIDTH - 300) // 2
    leaderboard_w = 300
    leaderboard_x = (WIDTH - leaderboard_w) // 2
    leaderboard_y = 120 
    
    # 4. satırın hizası: Lider tablosu Y + Başlık (45) + 3 satır (3*20) = 120 + 45 + 60 = 225
    target_y = leaderboard_y + 45 + 60
    
    panel_y = target_y      # Dikeyde 4. satır hizası
    panel_x = leaderboard_x - panel_w - 20 # Lider tablosunun 20px solu
    
    # Ekran dışına taşmayı önle (sol taraf)
    if panel_x < 10: 
        panel_x = 10

    # --- Animasyon / Salınım (Top Winners ile uyumlu) ---
    time_ms = pygame.time.get_ticks()
    h_offset = int(6 * math.sin(time_ms * 0.002))
    panel_x += h_offset # Hafif yatay salınım

    # --- Gölge ve Arkaplan Çizimi ---
    shadow_offset = 5
    # Gölge
    s_shadow = pygame.Surface((panel_w, panel_h))
    s_shadow.set_alpha(100)
    s_shadow.fill((0, 0, 0))
    screen.blit(s_shadow, (panel_x + shadow_offset, panel_y + shadow_offset))

    # Ana Panel
    s = pygame.Surface((panel_w, panel_h))
    s.set_alpha(200)
    s.fill((12, 12, 24)) # Lider tablosuyla aynı koyu lacivert ton
    screen.blit(s, (panel_x, panel_y))

    # --- Başlık ---
    title_str = "NEXT FLAGS"
    try:
        # Lider tablosundaki font stiliyle uyumlu başlık
        title_surf = font_small.render(title_str, True, COLOR_ACCENT)
    except:
        sys_font = pygame.font.SysFont("Arial", 16, bold=True)
        title_surf = sys_font.render(title_str, True, (255, 255, 255))
    
    screen.blit(title_surf, (panel_x + 15, panel_y + 10))

    
    # --- LİSTE BOŞSA BİLGİLENDİRME MESAJI ---
    
    if len(items) == 0:
        empty_color = (255, 215, 0) # Altın Sarısı
        
        # Panelin boş kısmının tam ortasını bul
        center_x = panel_x + (panel_w // 2)
        center_y = panel_y + HEADER_H + ((panel_h - HEADER_H) // 2)
        
        # 1. Satır: CHAT
        # font_ui (Arial 16 Bold) kullanıyoruz ki kalın olsun
        t1 = font_ui.render("CHAT YOUR", True, empty_color)
        r1 = t1.get_rect(center=(center_x, center_y - 20))
        screen.blit(t1, r1)
        
        # 2. Satır: YOUR COUNTRY
        t2 = font_ui.render("COUNTRY", True, empty_color)
        r2 = t2.get_rect(center=(center_x, center_y))
        screen.blit(t2, r2)
        
        # 3. Satır: Bayrak Emojisi (Emoji fontu varsa)
        try:
            # Emoji font varsa onu, yoksa normal fontu kullan
            ef = emoji_font if emoji_font else font_ui
            t3 = ef.render(". . . ", True, empty_color)
            r3 = t3.get_rect(center=(center_x, center_y + 25))
            screen.blit(t3, r3)
        except:
            pass
        
        # 4. Satır: Kırmızı Çarpı (X)
        try:
            ef = emoji_font if emoji_font else font_ui
            # Parlak Kırmızı
            t4 = ef.render("❌🏳️ EMOJI", True, (255, 50, 50)) 
            # Konum: Bayrağın (center_y + 25) biraz daha altı
            r4 = t4.get_rect(center=(center_x, center_y + 55)) 
            screen.blit(t4, r4)
        except:
            pass
        # ----------------------------------------

    # --- Liste Çizimi (Kaydırma Mantığı) ---
    
    # Eğer liste kısa ise kaydırma yapma
    if total_items <= MAX_VISIBLE:
        scroll_y = 0
    else:
        # --- Kaydırma Hesaplaması (Top Winners ile birebir aynı mantık) ---
        total_scroll = (total_items - MAX_VISIBLE) * ROW_HEIGHT

        if not hasattr(draw_next_flags_panel, "scroll_offset"):
            draw_next_flags_panel.scroll_offset = 0.0
            draw_next_flags_panel.direction = 1
            draw_next_flags_panel.pause_timer = 0
            draw_next_flags_panel.last_tick = pygame.time.get_ticks()

        current_tick = pygame.time.get_ticks()
        dt = (current_tick - draw_next_flags_panel.last_tick) / 1000.0
        draw_next_flags_panel.last_tick = current_tick
        
        SCROLL_SPEED = 30 # Biraz daha yavaş aksın

        if draw_next_flags_panel.pause_timer > 0:
            draw_next_flags_panel.pause_timer -= dt * 1000
            if draw_next_flags_panel.pause_timer <= 0:
                draw_next_flags_panel.pause_timer = 0
                draw_next_flags_panel.direction *= -1
        else:
            draw_next_flags_panel.scroll_offset += draw_next_flags_panel.direction * SCROLL_SPEED * dt
            
            # Aşağı sınır
            if draw_next_flags_panel.scroll_offset >= total_scroll and draw_next_flags_panel.direction == 1:
                draw_next_flags_panel.scroll_offset = total_scroll
                draw_next_flags_panel.pause_timer = 2000 # 2 saniye bekle
            # Yukarı sınır
            elif draw_next_flags_panel.scroll_offset <= 0 and draw_next_flags_panel.direction == -1:
                draw_next_flags_panel.scroll_offset = 0
                draw_next_flags_panel.pause_timer = 2000

            # Güvenlik sınırı
            draw_next_flags_panel.scroll_offset = max(0.0, min(draw_next_flags_panel.scroll_offset, total_scroll))
        
        scroll_y = draw_next_flags_panel.scroll_offset

    # --- Clipping (Kesme) Bölgesi ---
    view_y_start = panel_y + HEADER_H
    view_y_end = panel_y + panel_h
    
    clip_rect = pygame.Rect(panel_x, view_y_start, panel_w, panel_h - HEADER_H)
    clip_rect.inflate_ip(0, -2) # Hafif padding

    old_clip = screen.get_clip()
    screen.set_clip(clip_rect)

    # --- Satırları Çiz ---
    FLAG_W, FLAG_H = 30, 20 # Liste için biraz küçültülmüş bayraklar

    for i, (name, info) in enumerate(items):
        # Y Konumu: Başlangıç + (Sıra * Yükseklik) - Kaydırma Miktarı
        y_pos = view_y_start + (i * ROW_HEIGHT) - scroll_y
        
        # Sadece görünür alandaysa çiz (performans ve görsel temizlik)
        if view_y_start - ROW_HEIGHT < y_pos < view_y_end:
            
            # 1. Bayrak
            flag_data = flag_manager.get_flag_by_code(info["code"], FLAG_W, FLAG_H)
            flag_img = flag_data["image"]
            # Dikey ortala
            img_y = y_pos + (ROW_HEIGHT - FLAG_H) // 2
            screen.blit(flag_img, (panel_x + 15, img_y))

            # 2. İsim Metni
            short_name = name if len(name) <= 15 else name[:13] + ".."
            name_color = (200, 200, 200)
            
            # Font seçimi (Global font_small kullanıyoruz, yoksa yedek)
            try:
                txt_surf = font_small.render(short_name, True, name_color)
            except:
                fnt = pygame.font.SysFont("Arial", 14)
                txt_surf = fnt.render(short_name, True, name_color)
            
            # Yazıyı dikey ortala
            txt_y = y_pos + (ROW_HEIGHT - txt_surf.get_height()) // 2
            screen.blit(txt_surf, (panel_x + 15 + FLAG_W + 10, txt_y))

            # 3. Adet Bilgisi (x2, x3 vb.)
            if info["count"] > 1:
                count_str = f"x{info['count']}"
                count_surf = font_small.render(count_str, True, COLOR_GOLD)
                # Sağa yasla
                c_x = panel_x + panel_w - count_surf.get_width() - 5 
                screen.blit(count_surf, (c_x, txt_y))

    # --- Clipping İptal ---
    screen.set_clip(old_clip)


# --- OYUN DURUMLARI ---
STATE_MENU = 0
STATE_COUNTDOWN = 1
STATE_GAME = 2
STATE_WINNER = 3

current_state = STATE_MENU
game_objects = []
space = None
circle_body = None
round_start_time = 0
winner_obj = None
#baslangic menusu
sliders = [
    Slider(WIDTH//2 - 200, 390, 400, 20, 10, 50, SETTINGS["initial_gap"], "Baslangic Boslugu (%)"), 
    Slider(WIDTH//2 - 200, 460, 400, 20, 10, 60, SETTINGS["round_time"], "Tur Suresi (sn)"),
    Slider(WIDTH//2 - 200, 530, 400, 20, 5, 200, SETTINGS["auto_spawn"], "Baslangic Bayrak Sayisi"),
    Slider(WIDTH//2 - 200, 600, 400, 20, 1, 300, SETTINGS["gravity"], "Gravity (Yercekimi)"),
    Slider(WIDTH//2 - 200, 670, 400, 20, 0.2, 10.0, SETTINGS["rotation_speed"], "Donme Hizi") 
]

video_id_input = TextBox(WIDTH//2 - 200, 300, 400, 40, VIDEO_ID_INPUT)

def start_game_sequence():
    global current_state, round_start_time, space, circle_body, game_objects, winner_obj, is_round_recorded, NEXT_ROUND_QUEUE, CHAT_THREAD, IS_CHAT_RUNNING
    
    # if not IS_CHAT_RUNNING and CHAT_THREAD is None:
    if CHAT_THREAD is None or not CHAT_THREAD.is_alive():
        video_id = video_id_input.text
        if len(video_id) > 5: 
            print(f"Baglaniyor: {video_id}")
            try:
                chat = pytchat.create(video_id=video_id)
                CHAT_THREAD = threading.Thread(target=chat_listener_task, args=(chat,), daemon=True)
                CHAT_THREAD.start()
            except Exception as e:
                print(f"Baglanti hatasi (Main): {e}")

    is_round_recorded = False
    
    SETTINGS["initial_gap"] = sliders[0].val
    SETTINGS["round_time"] = sliders[1].val
    SETTINGS["auto_spawn"] = int(sliders[2].val)
    SETTINGS["gravity"] = sliders[3].val
    SETTINGS["rotation_speed"] = sliders[4].val
    
    SETTINGS["flag_size"] = 15
    INTERNAL_SETTINGS["elasticity"] = 1.1 

    INTERNAL_SETTINGS["circle_radius"] = 170 + (SETTINGS["auto_spawn"] * 1.1)
    INTERNAL_SETTINGS["circle_radius"] = min(170, INTERNAL_SETTINGS["circle_radius"])

    space = pymunk.Space()
    space.gravity = (0, SETTINGS["gravity"])
    space.damping = 0.9 
    
    game_objects = []
    winner_obj = None
    
    circle_body = create_circle_body(space, CIRCLE_CENTER, SETTINGS["rotation_speed"])
    rebuild_circle_segments(space, circle_body, INTERNAL_SETTINGS["circle_radius"], SETTINGS["initial_gap"])
    
    total_slots = SETTINGS["auto_spawn"]
    spawned_count = 0
    spawn_radius_limit = INTERNAL_SETTINGS["circle_radius"] * 0.7 
    
    current_queue = dict(NEXT_ROUND_QUEUE)
    NEXT_ROUND_QUEUE.clear() 
    
    for name, info in current_queue.items():
        count = info["count"]
        code = info["code"]
        
        w = SETTINGS["flag_size"] * 2.2
        h = SETTINGS["flag_size"] * 1.5
        flag_data = flag_manager.get_flag_by_code(code, w, h)
        flag_data["name"] = name 
        
        for _ in range(count):
            rx = CIRCLE_CENTER[0] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
            ry = CIRCLE_CENTER[1] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
            obj = spawn_flag(space, (rx, ry), SETTINGS["flag_size"], specific_data=flag_data)
            game_objects.append(obj) 
            spawned_count += 1
            
    remaining_slots = total_slots - spawned_count
    if remaining_slots < 0: remaining_slots = 0 
    
    for _ in range(remaining_slots):
        rx = CIRCLE_CENTER[0] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
        ry = CIRCLE_CENTER[1] + random.randint(-int(spawn_radius_limit), int(spawn_radius_limit))
        obj = spawn_flag(space, (rx, ry), SETTINGS["flag_size"])
        game_objects.append(obj) 
        
    current_state = STATE_COUNTDOWN
    round_start_time = time.time()

start_btn = Button(WIDTH//2 - 100, 800, 200, 50, "BASLA", start_game_sequence)

running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            IS_CHAT_RUNNING = False 
        if current_state == STATE_MENU:
            for s in sliders: s.handle_event(event)
            video_id_input.handle_event(event)
            start_btn.handle_event(event)
        elif current_state == STATE_GAME:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                obj = spawn_flag(space, CIRCLE_CENTER, SETTINGS["flag_size"])
                game_objects.append(obj)
    
    # --- ARKA PLAN ÇİZİMİ ---
    if background_surface:
        screen.blit(background_surface, (0, 0))
    else:
        screen.fill(COLOR_BG)

    if current_state == STATE_MENU:
        s_bg = pygame.Surface((400, 60))
        s_bg.set_alpha(150)
        s_bg.fill((0,0,0))
        screen.blit(s_bg, (WIDTH//2 - 200, 50))

        title = font_big.render("FLAG BATTLE", True, COLOR_ACCENT)
        title_rect = title.get_rect(center=(WIDTH//2, 230))
        screen.blit(title, title_rect)
        
        lbl = font_ui.render("Youtube Video ID:", True, COLOR_TEXT)
        screen.blit(lbl, (WIDTH//2 - 200, 280))
        video_id_input.draw(screen)
        
        for s in sliders: s.draw(screen)
        start_btn.draw(screen)
        draw_leaderboard_panel(screen)

    elif current_state == STATE_COUNTDOWN:
        elapsed = time.time() - round_start_time
        countdown = 3 - int(elapsed)
        
        for shape in space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
        
        for shape in game_objects:
             data = shape.custom_data
             img = data["image"]
            #  img = data.get("original", data["image"])
             rect = img.get_rect(center=(shape.body.position.x, shape.body.position.y))
             screen.blit(img, rect)

        draw_leaderboard_panel(screen)
        draw_next_flags_panel(screen)

        if countdown > 0:
            count_bg = pygame.Surface((100, 100))
            count_bg.set_alpha(150)
            count_bg.fill((0,0,0))
            count_bg_rect = count_bg.get_rect(center=(WIDTH//2, HEIGHT/2-50))
            screen.blit(count_bg, count_bg_rect)

            count_surf = font_big.render(str(countdown), True, COLOR_COUNTDOWN)
            count_rect = count_surf.get_rect(center=(WIDTH//2, HEIGHT/2-50))
            screen.blit(count_surf, count_rect)
        else:
            current_state = STATE_GAME
            round_start_time = time.time()

    elif current_state == STATE_GAME:
        time_played = time.time() - round_start_time
        time_left = SETTINGS["round_time"] - time_played
        
        progress = min(1.0, time_played / SETTINGS["round_time"])
        current_gap = SETTINGS["initial_gap"] + (progress * 30) #circle gap çember boşluğu zaman
        
        rebuild_circle_segments(space, circle_body, INTERNAL_SETTINGS["circle_radius"], current_gap)
        
        dt = 1.0 / 60.0
        sub_steps = 5 
        for _ in range(sub_steps):
            space.step(dt / sub_steps)
            
        delete_limit = INTERNAL_SETTINGS["circle_radius"] + 50
        for shape in game_objects[:]:
            dx = shape.body.position.x - CIRCLE_CENTER[0]
            dy = shape.body.position.y - CIRCLE_CENTER[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > delete_limit:
                space.remove(shape.body, shape)
                game_objects.remove(shape)
                
        if len(game_objects) == 1:
            winner_obj = game_objects[0]
            current_state = STATE_WINNER
            round_start_time = time.time() 
        elif len(game_objects) == 0 and time_left <= 0:
            start_game_sequence()
            
        for shape in space.shapes:
            if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
        
        for shape in game_objects:
            body = shape.body
            if math.isnan(body.position.x): continue
            data = shape.custom_data
            img = data["image"]
            name = data["name"]
            try:
                rect = img.get_rect(center=(body.position.x, body.position.y))
                screen.blit(img, rect)
                text_surf = font_small.render(name, True, COLOR_TEXT)
                text_rect = text_surf.get_rect(center=(body.position.x, body.position.y + 20))
                bg_rect = text_rect.inflate(4, 2)
                pygame.draw.rect(screen, (0,0,0,150), bg_rect, border_radius=3)
                screen.blit(text_surf, text_rect)
            except: pass
            
        ui_str = f"REST: {len(game_objects)}"
        ui_surf = font_ui.render(ui_str, True, (255, 255, 0))
        s_bar = pygame.Surface((WIDTH, 30))
        s_bar.set_alpha(200)
        s_bar.fill((0,0,0))
        screen.blit(s_bar, (0, HEIGHT-30))
        screen.blit(ui_surf, (10, HEIGHT-25))
        
        draw_leaderboard_panel(screen)
        draw_next_flags_panel(screen)

    elif current_state == STATE_WINNER:
        # --- 1. MANTIK VE PUANLAMA ---
        if winner_obj and not is_round_recorded:
            w_name = winner_obj.custom_data["name"]
            if w_name in LEADERBOARD:
                LEADERBOARD[w_name] += 1
            else:
                LEADERBOARD[w_name] = 1
            is_round_recorded = True

        if winner_obj and winner_obj.body.body_type != pymunk.Body.KINEMATIC:
             winner_obj.body.body_type = pymunk.Body.KINEMATIC
             winner_obj.body.velocity = (0,0)
             circle_body.angular_velocity = 0
             
        # --- 2. ÇEVRE VE UI ÇİZİMİ (Eksik olan kısımlar burasıydı) ---
        # Çember duvarlarını çiz
        for shape in space.shapes:
             if isinstance(shape, pymunk.Segment):
                p1 = shape.a.rotated(shape.body.angle) + shape.body.position
                p2 = shape.b.rotated(shape.body.angle) + shape.body.position
                draw_smooth_segment(screen, p1, p2, INTERNAL_SETTINGS["wall_thickness"], COLOR_ACCENT)
        
        # Panelleri çiz (Arka planda kalsınlar)
        draw_leaderboard_panel(screen)
        draw_next_flags_panel(screen)

        # --- 3. KAZANAN KUTUSU TASARIMI ---
        if winner_obj:
            # -- Kutu Arkaplanı --
            box_w, box_h = 450, 360
            win_bg = pygame.Surface((box_w, box_h))
            win_bg.set_alpha(200)
            win_bg.fill((0,0,0))
            # Kutuyu tam ortaya hizala
            win_bg_rect = win_bg.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(win_bg, win_bg_rect)

            data = winner_obj.custom_data

            # -- "WINNER" Yazısı (Kutunun üst kısmına yakın) --
            lbl_surf = font_big.render("WINNER", True, (252, 3, 244)) # Magenta
            lbl_rect = lbl_surf.get_rect(midtop=(WIDTH//2, win_bg_rect.top + 30))
            screen.blit(lbl_surf, lbl_rect)

            # -- Bayrak (Yazının altı) --
            img = data["image"]
            img = pygame.transform.scale(img, (150, 100))
            img_rect = img.get_rect(midtop=(WIDTH//2, lbl_rect.bottom + 20))
            screen.blit(img, img_rect)
            
            # -- Ülke Adı (Bayrağın altı) --
            # İsim çok uzunsa taşmaması için fontu dinamik küçültebiliriz ama şimdilik standart font_big
            name_surf = font_big.render(data['name'], True, (255, 215, 0)) # Altın Rengi
            name_rect = name_surf.get_rect(midtop=(WIDTH//2, img_rect.bottom + 20))
            screen.blit(name_surf, name_rect)

        # --- 4. RESET ZAMANLAYICISI ---
        if time.time() - round_start_time > 4:
            start_game_sequence()

        draw_leaderboard_panel(screen)
        draw_next_flags_panel(screen)

        if time.time() - round_start_time > 4:
            start_game_sequence() 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()