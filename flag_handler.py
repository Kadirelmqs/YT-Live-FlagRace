import os
import sys
import random
import pygame
import pycountry
from settings import *

def resource_path(relative_path):
    # When the application is frozen by PyInstaller we can't rely on
    # sys._MEIPASS (it may not exist on all platforms). Instead use the
    # directory of the executable. For normal execution fall back to the
    # source file location.
    if getattr(sys, "frozen", False):
        # frozen executable (exe) - resources live alongside the exe
        base_path = os.path.dirname(sys.executable)
    else:
        # running from source
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# --- FLAG MANAGER ---
class FlagManager:
    def __init__(self, folder_path):
        # self.folder_path = folder_path
        self.folder_path = resource_path(folder_path)   #exe
        self.flags_data = [] 
        self.image_cache = {}  # O(1) görüntü önbelleği: key="CODE_W_H", value=pygame.Surface
        self.load_flags()

    def load_flags(self):
        # debug: show which folder is being scanned for flags
        print(f"Aranan Bayrak Dizini: {self.folder_path}")
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
        target_w = int(target_w)
        target_h = int(target_h)
        
        # Cache key: CODE_WINDOW_WIDTH_WINDOW_HEIGHT
        cache_key = f"{code}_{target_w}_{target_h}"
        
        # Eğer cache'te varsa hemen döndür (O(1))
        if cache_key in self.image_cache:
            return {
                "image": self.image_cache[cache_key],
                "name": self._get_country_name(code),
                "original": None
            }
        
        # Bayrak dosyasını bul
        for data in self.flags_data:
            if data["code"] == code:
                scaled = pygame.transform.scale(data["raw_img"], (target_w, target_h))
                self.image_cache[cache_key] = scaled  # Cache'e sakla
                return {"image": scaled, "name": data["name"], "original": data["raw_img"]}
        
        # Tidak ditemukan, rastgele bayrak kullan
        return self.get_random_flag(target_w, target_h)
    
    def _get_country_name(self, code):
        """Ülke kodundan adını al (cache sonrası hızlı isim döndürmek için)"""
        code = code.upper()
        for data in self.flags_data:
            if data["code"] == code:
                return data["name"]
        return code

    def get_random_flag(self, target_w, target_h):
        target_w = int(target_w)
        target_h = int(target_h)
        
        if not self.flags_data:
            fallback = pygame.Surface((target_w, target_h))
            fallback.fill((200, 200, 200))
            return {"image": fallback, "name": "No Flag"}
        
        data = random.choice(self.flags_data)
        code = data["code"]
        
        # Cache key kontrol et
        cache_key = f"{code}_{target_w}_{target_h}"
        
        # Eğer cache'te varsa döndür
        if cache_key in self.image_cache:
            return {
                "image": self.image_cache[cache_key],
                "name": data["name"],
                "original": data["raw_img"]
            }
        
        # Yoksa oluştur ve cache'e sakla
        scaled = pygame.transform.scale(data["raw_img"], (target_w, target_h))
        self.image_cache[cache_key] = scaled
        return {"image": scaled, "name": data["name"], "original": data["raw_img"]}

# --- FLAG MANAGER INSTANCE ---
# flag_manager = FlagManager(FLAGS_DIRECTORY_PATH)

