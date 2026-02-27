import os
import sys
import random
import pygame
import pycountry
from settings import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

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

# --- FLAG MANAGER INSTANCE ---
# flag_manager = FlagManager(FLAGS_FOLDER)
