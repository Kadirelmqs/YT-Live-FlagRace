import time
import pycountry
from game_state import *

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
