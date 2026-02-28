# --- SABİTLER VE BAŞLANGIÇ AYARLARI ---
WIDTH, HEIGHT = 1080,1080
CIRCLE_CENTER = (WIDTH // 2, HEIGHT // 2 - 3) #çemberle lider tablosu arası 7 px dusur artsın.
FLAGS_FOLDER = "flags"
BACKGROUND_FILE_NAME = "background.jpg" # Resmin tam adı ve uzantısı bu olmalı!

# --- ÖNEMLİ AYARLAR ---
MAX_VELOCITY = 250.0  #200 du

# Varsayılan Ayarlar
SETTINGS = {
    "gravity": 40,    #40      
    "flag_size": 15,        
    "initial_gap": 30,      #30
    "round_time": 20,       
    "auto_spawn": 40,       #40
    "rotation_speed": 1.5   #2.0
}

# Hesaplanan/Sabit Ayarlar
INTERNAL_SETTINGS = {
    "circle_radius": 270,  #170 idi 
    "elasticity": 1.1,      
    "wall_thickness": 8
}


# Renkler
COLOR_BG = (20, 20, 20)
COLOR_TEXT = (255, 255, 255)
# COLOR_ACCENT = (20, 122, 2)# 
COLOR_ACCENT = (24, 143, 3)# 
COLOR_COUNTDOWN = (180, 0, 255) 
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (192, 192, 192)
COLOR_BRONZE = (205, 127, 50)
COLOR_NEXT_FLAG_BG = (30, 30, 60)