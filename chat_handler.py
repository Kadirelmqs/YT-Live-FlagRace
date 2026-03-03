import time
import re
import json
import os
import pycountry

# ==========================================
# ÜLKE KODU BULMA (LOOKUP TABLE)
# ==========================================

def clean_text(text):
    """
    Metni standardize et.
    - Küçük harf yap
    - Özel karakterleri kaldır
    - Boşlukları normalize et
    """
    if not text:
        return ""
    cleaned = text.lower()
    cleaned = re.sub(r'[.,&\-\'()\[\]/]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()

def _load_country_lookup():
    """
    JSON dosyasından ülke alias'larını yükle.
    Döner: dict veya boş dict (hata durumunda)
    """
    try:
        import sys
        # When frozen by PyInstaller, read from exe directory; otherwise from source
        if getattr(sys, "frozen", False):
            # frozen executable - resources alongside exe
            base_path = os.path.dirname(sys.executable)
        else:
            # running from source
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        json_path = os.path.join(base_path, 'country_aliases.json')
        print(f"[DEBUG] JSON Dosyası Aranıyor: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            lookup = json.load(f)
        print(f"[OK] Hızlı Arama Sözlüğü Yüklendi ({len(lookup)} kayıt)")
        return lookup
    except Exception as e:
        print(f"[ERROR] Hızlı Arama Sözlüğü Yüklenemedi: {e}")
        return {}

COUNTRY_LOOKUP = _load_country_lookup()

def find_country_code(text):
    """
    Metinden ülke kodunu bul.
    
    Parametreler:
        text: Kullanıcı metni
    
    Döner:
        Ülke kodu (örn "TR") veya None
    """
    if not text or len(text) > 100:
        return None  # Flood korumasi
    
    cleaned = clean_text(text)
    words = cleaned.split()
    
    if not words:
        return None
    
    # Adayları O(1) hızında sözlükte ara
    candidates = [cleaned]
    for i in range(1, min(5, len(words) + 1)):
        candidates.append(" ".join(words[:i]))
    
    for candidate in candidates:
        if candidate in COUNTRY_LOOKUP:
            return COUNTRY_LOOKUP[candidate]
    
    return None

# ==========================================
# SOHBET DİNLEYİCİ (CHAT LISTENER THREAD)
# ==========================================

def chat_listener_task(chat_obj, event_queue, next_round_queue):
    """
    YouTube sohbetini dinler ve ülke adlarını iki farklı yola iletir.
    1. `event_queue` üzerinden anında oyun döngüsüne bayrak spawn etme olayları.
    2. `next_round_queue` üzerinden yeni turun bayrak sayısını tutma.

    Parametreler:
        chat_obj: pytchat sohbet nesnesi
        event_queue: threading-safe olay kuyruğu (queue.Queue)
        next_round_queue: Sonraki turdaki bayraklar sözlüğü (referans olarak geçilir)
    """
    print("📡 Sohbet thread'i başladı...")
    
    try:
        while chat_obj.is_alive():
            try:
                for c in chat_obj.get().sync_items():
                    msg = c.message
                    code = find_country_code(msg)
                    
                    if code:
                        try:
                            std_name = pycountry.countries.get(alpha_2=code).name
                        except:
                            std_name = msg
                        
                        # oyun döngüsüne olay olarak bildir
                        try:
                            event_queue.put_nowait((std_name, code))
                        except Exception:
                            pass
                        
                        # aynı zamanda bir sonraki tura ekle
                        if std_name in next_round_queue:
                            next_round_queue[std_name]["count"] += 1
                        else:
                            next_round_queue[std_name] = {"code": code, "count": 1}
                        
                        print(f"[OK] Sohbet -> event kuyruğuna eklendi: {std_name} (x{next_round_queue[std_name]['count']})")
                
                time.sleep(0.5)
            except Exception as e:
                print(f"⚠ Sohbet işleme hatası: {e}")
                break
    except Exception as e:
        print(f"[ERROR] Sohbet thread hatası: {e}")
    finally:
        print("[OK] Sohbet thread'i sonlandı.")

