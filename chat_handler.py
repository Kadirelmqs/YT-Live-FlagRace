import time
import re
import json
import os
import pycountry
from game_state import *

# --- HIZLI ARAMA SÖZLÜĞÜ ---
def clean_text(text):
    if not text: return ""
    cleaned = text.lower()
    cleaned = re.sub(r'[.,&\-\'()\[\]/]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()

COUNTRY_LOOKUP = {}
try:
    import sys
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    json_path = os.path.join(base_path, 'country_aliases.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        COUNTRY_LOOKUP = json.load(f)
    print(f"Hızlı Arama Sözlüğü Yüklendi ({len(COUNTRY_LOOKUP)} kayıt)")
except Exception as e:
    print(f"Hızlı Arama Sözlüğü Yüklenemedi! Hata: {e}")
# --- YARDIMCI: Ülke Bulma ---
def find_country_code(text):
    if not text or len(text) > 100: 
        return None # Çok uzun spamları (flood) baştan reddet

    # Normalize and clean using shared clean_text
    cleaned = clean_text(text)
    words = cleaned.split()

    if not words: return None

    # Spam tekrarlarını ve çok kelimeli ülkeleri yakalamak için adaylar oluştur
    # Örn: "saudi arabia 🇸🇦 saudi arabia" -> Adaylar: "saudi", "saudi arabia", "saudi arabia saudi"
    candidates = [cleaned] # Önce tüm temizlenmiş metni dene
    for i in range(1, min(5, len(words) + 1)):
        candidates.append(" ".join(words[:i]))

    # Adayları O(1) hızında sözlükte ara
    for candidate in candidates:
        if candidate in COUNTRY_LOOKUP:
            return COUNTRY_LOOKUP[candidate]

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
