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

# Import modularized components
from ui_elements import TextBox, Slider, Button
from flag_handler import FlagManager
from physics_core import rebuild_circle_segments, create_circle_body, limit_velocity, spawn_flag
from chat_handler import find_country_code, chat_listener_task
from ui_panels import draw_easter_egg_banner, draw_leaderboard_panel, draw_leaderboard_entry, draw_next_flags_panel
from game_state import *
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

# --- 1. Ekran oluştuktan SONRA bayrakları yükle ---
global flag_manager
flag_manager = FlagManager(FLAGS_FOLDER)

# --- 2. Diğer modüllere bayrak yöneticisini manuel enjekte et ---
import physics_core
physics_core.flag_manager = flag_manager

import ui_panels
ui_panels.flag_manager = flag_manager
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

CHAT_THREAD = None
VIDEO_ID_INPUT = "YT Live Video ID" 

is_round_recorded = False

# --- YARDIMCI: Ülke Bulma ---
# --- CHAT ve COUNTRY CODE FUNCTIONS TAŞINDI (chat_handler.py'ye) ---

# --- UI SINIFLARI TAŞINDI (ui_elements.py'ye) ---

# --- TEXTBOX TAŞINDI (ui_elements.py'ye) ---
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

# Slider class taşındı ui_elements.py'ye
# Button class taşındı ui_elements.py'ye

# --- FLAG MANAGER TAŞINDI (flag_handler.py'ye) ---

# --- FİZİK FONKSIYONLARI TAŞINDI (physics_core.py'ye) ---

# Physics functions moved to physics_core.py

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

# UI panel functions moved to ui_panels.py




# --- OYUN DURUMLARI IMPORT EDİLİYOR ---
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
    INTERNAL_SETTINGS["circle_radius"] = min(250, INTERNAL_SETTINGS["circle_radius"])

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
        draw_easter_egg_banner(screen) # Sadece orada duran yazı

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
        draw_easter_egg_banner(screen) # Sadece orada duran yazı

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
        draw_easter_egg_banner(screen) # Sadece orada duran yazı

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
        draw_easter_egg_banner(screen) # Sadece orada duran yazı

        if time.time() - round_start_time > 4:
            start_game_sequence() 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()