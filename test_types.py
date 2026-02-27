import pytchat
import time

# Test etmek istediğiniz yayının ID'sini buraya girin (veya input ile alın)
print("Youtube Canlı Yayın ID'sini (URL sonundaki v= kısmı) girin:")
video_id = input("> ")

chat = pytchat.create(video_id=video_id)
print(f"\n'{video_id}' dinleniyor... (Durdurmak için CTRL+C)")

try:
    while chat.is_alive():
        for c in chat.get().sync_items():
            
            # --- DURUM 1: SUPER CHAT (Para) ---
            # c.amountString doluysa bu bir para gönderimidir.
            if c.amountString:
                print(f"\n[💰 SUPER CHAT] {c.author.name} -> {c.amountString} gönderdi!")
                print(f"   Mesajı: {c.message}")
                # BURAYA: pyautogui.press('k') gibi bir kod gelecek (Özel güç)

            # --- DURUM 2: SUPER STICKER (Çıkartma) ---
            elif c.type == 'superSticker':
                print(f"\n[🏷️ STICKER] {c.author.name} bir çıkartma attı!")
                # BURAYA: pyautogui.press('s') (Görsel efekt)

            # --- DURUM 3: YENİ ÜYE (Katıl Butonu) ---
            # pytchat'te 'newSponsor' genellikle yeni üyeliği temsil eder
            elif c.type == 'newSponsor':
                print(f"\n[🌟 YENİ ÜYE] {c.author.name} kanala üye oldu!")
                # BURAYA: pyautogui.press('u') (Yeni karakter doğsun)

            # --- DURUM 4: NORMAL MESAJ ---
            else:
                # Sadece mesajı yazdıralım
                print(f"[💬] {c.author.name}: {c.message}")
                
                # Basit Komut Testi
                if c.message.lower().strip() == "zıpla":
                    print("   >>> TETİKLEME: Zıplama komutu algılandı!")

        time.sleep(0.5) # CPU'yu yormamak için küçük bekleme

except KeyboardInterrupt:
    print("Program sonlandırıldı.")
except Exception as e:
    print(f"Hata: {e}")