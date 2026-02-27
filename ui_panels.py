import pygame
import math
import os
from settings import *
from game_state import *
# from flag_handler import flag_manager

# --- FONT INITIALIZATION ---
pygame.font.init()
font_small = pygame.font.SysFont("Arial", 12, bold=True)
font_ui = pygame.font.SysFont("Arial", 16, bold=True)

emoji_font = None
emoji_font_paths = [
    "C:/Windows/Fonts/seguiemj.ttf",          # Windows
    "/System/Library/Fonts/Apple Color Emoji.ttc",  # macOS
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"  # Linux
]
for path in emoji_font_paths:
    if os.path.exists(path):
        try:
            emoji_font = pygame.font.Font(path, 20)
            break
        except:
            continue

if emoji_font is None:
    emoji_font = pygame.font.SysFont("Arial", 20, bold=True)

# --- UI PANEL FUNCTIONS ---

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
        t1 = font_ui.render("TYPE YOUR", True, empty_color)
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
            t4 = ef.render("NO EMOJI", True, (255, 50, 50)) 
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
