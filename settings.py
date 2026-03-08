# ==========================================
# FLAG BATTLE ROYALE - MERKEZI AYARLAR
# ==========================================

# --- EKRAN AYARLARI ---
WIDTH, HEIGHT = 600, 1066
CIRCLE_CENTER = (WIDTH // 2, HEIGHT*0.64)
FLAGS_FOLDER = "flags"
BACKGROUND_FILE_NAME = "background.jpg"

# --- MAKSİMUM VELOSİTE (Bayrakların hızı sınırı) ---
MAX_VELOCITY = 500.0

# --- OYUN MEKANİĞİ AYARLARI ---
SETTINGS = {
    "gravity": 40,
    "flag_size": 15,
    "initial_gap": 30,
    "round_time": 20,
    "auto_spawn": 40,
    "rotation_speed": 1.5
}

# --- İÇ AYARLAR (Dinamik olarak hesaplanır) ---
INTERNAL_SETTINGS = {
    "circle_radius": 270,
    "elasticity": 1.1,
    "wall_thickness": 8
}

# ==========================================
# RENK PALETESI
# ==========================================
COLOR_BG = (20, 20, 20) 
COLOR_TEXT = (255, 255, 255)#
COLOR_ACCENT = (24, 143, 3)
COLOR_COUNTDOWN = (180, 0, 255)
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (192, 192, 192)
COLOR_BRONZE = (205, 127, 50)
COLOR_PANEL_BG = (12, 12, 24)
COLOR_NEXT_FLAG_BG = (30, 30, 60)
COLOR_SHADOW = (0, 0, 0)
COLOR_EMPTY_MSG = (255, 215, 0)


# ==========================================
# UI PANELLERİ AYARLARI
# ==========================================
# Liderlik Paneli
LEADERBOARD_PANEL = {
    "width": 200,
    "x_position": WIDTH//2 - 300,          # Sağa çektik 
    "y_position": 90,
    "max_visible_items": 5,
    "row_height": 20,
    "header_height": 35,
    # "shadow_offset": -5,
    # "shadow_alpha": 100,
    "panel_alpha": 200,
    "title_color_lb": (255, 220, 40),
    "title_offset_x": 15,
    "title_offset_y": 8,
    # "horizontal_oscillation_amplitude": 6,
    # "oscillation_frequency": 0.002,
}

# Beğeni Barı Ayarları
LIKE_BAR_SETTINGS = {
    "width": 400,
    "height": 25,
    "y_position": HEIGHT*0.23,#
    "bg_color": (30, 30, 35), # Daha koyu, şık bir arka plan
    "fill_color": (235, 20, 75), # Tatlı ve canlı bir TikTok/Kalp kırmızısı
    "text_color": (255, 255, 255),
    "alpha": 200,
    "border_radius": 13,  # Tamamen yuvarlak köşeler (Kapsül görünümü)
    "initial_target": 10
}
#Beğeni hedeflerini belirleyen fonksiyon
def get_next_like_target(current_target):
    """Mevcut hedefe göre bir sonraki ulaşılabilir hedefi belirler."""
    if current_target < 50:
        return current_target + 10    # 10, 20, 30, 40, 50
    elif current_target < 200:
        return current_target + 20    # 70, 90, 110...
    elif current_target < 500:
        return current_target + 50    # 250, 300, 350...
    elif current_target < 1000:
        return current_target + 100   # 600, 700, 800...
    else:
        return current_target + 250   # 1250, 1500, 1750... 250 iditest için 1 yaptım

# # Sonraki Bayraklar Paneli
# NEXT_FLAGS_PANEL = {
#     "width": 140,#122
#     "max_visible_items": 5,
#     "row_height": 40,
#     "header_height": 40,
#     "shadow_offset": -5,
#     "shadow_alpha": 100,
#     "panel_alpha": 200,
#     "title_color_nf": (5, 179, 2),
#     "title_offset_x": 15,
#     "title_offset_y": 10,
#     "scroll_speed": 30,
#     "scroll_pause_duration_ms": 2000,
#     "horizontal_offset_x": -20,
# }

# Sonraki Bayraklar Paneli (YATAY TASARIM)
NEXT_FLAGS_PANEL = {
    "width": WIDTH-20,               # Panelin toplam genişliği
    "height": 110,              # Panelin toplam yüksekliği
    "y_position": HEIGHT* 0.28,           # Çemberin üstünde duracağı dikey konum yukardan uzaklık
    "x_position": (WIDTH - (WIDTH-20)) // 2,          #(Sağ-sol konumu)
    "item_width": 100,          # Her bir bayrak kutusunun genişliği
    "header_height": 30,        # Başlık kısmının yüksekliği
    # "shadow_offset": 5,         # Gölge derinliği
    # "shadow_alpha": 100,
    "panel_alpha": 200,
    "title_color_nf": (5, 179, 2),
    "scroll_speed": 40,         # Sağa sola kayma hızı
    "scroll_pause_duration_ms": 2000,
    # "vertical_oscillation_amplitude": 4, # Aşağı yukarı salınım genliği
    # "oscillation_frequency": 0.002,
}

# ==========================================
# YAZITIP AYARLARI
# ==========================================
FONTS = {
    "small": {"name": "Arial", "size": 16, "bold": True},
    "ui": {"name": "Arial", "size": 16, "bold": True},
    "big": {"name": "Arial", "size": 60, "bold": True},
    "leaderboard": {"name": "Arial", "size": 14, "bold": True},
    "emoji": {"size": 20},
}

# Emoji Font Yolları (Platform-bağlısız)
EMOJI_FONT_PATHS = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
]

# ==========================================
# SOHBET AYARLARI
# ==========================================
CHAT = {
    "check_interval_ms": 500,
    "max_message_length": 100,
}

# ==========================================
# ANİMASYON AYARLARI
# ==========================================
ANIMATIONS = {
    "panel_oscillation": {
        "amplitude": 6,
        "frequency": 0.002,
    },
    "countdown_box": {
        "size": 100,
        "alpha": 150,
    }
}

# ==========================================
# EASTER EGG BANNER AYARLARI
# ==========================================
EASTER_EGG = {
    "text": "67 = BAN!",
    "font_name": "Arial Black",
    "font_size": 15,
    "color": (250, 0, 0),
    "bg_color": (10, 10, 10),
    "bg_alpha": 190,
    "offset_y": HEIGHT * 0.65,
}

YOUTUBE_API_KEY = "AIzaSyBx5GR7JooHT4zb0IEcoB9QV-C7lIcq290"

# --- KAOS MODU (FEVER MODE) AYARLARI ---
FEVER_MODE = {
    "duration": 10.0,               # Kaos modunun saniye cinsinden süresi
    "circle_color": (220, 20, 20),  # Çemberin kaos modundaki rengi (Kırmızımsı)
    "shake_amplitude": 15,          # Çemberin yukarı-aşağı titreme şiddeti (piksel)
    "shake_frequency": 0.05,        # Çemberin titreme hızı
    "fever_velocity": 1500,         # Bayrakların kaos modundaki uçuş hızı
    "normal_velocity": 500,         # Bayrakların normal uçuş hızı
    "text_color": (255, 50, 50),    # Ekranda çıkan yazının rengi
    "text_template": "🔥 CHAOS MODE {time} 🔥", # Ekranda çıkacak yazı
    "text_pos": (WIDTH // 2, HEIGHT* 0.40)  # Yazının ekrandaki merkez koordinatı (X, Y)
}