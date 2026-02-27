import pytchat

# Buraya ŞU AN CANLI OLAN bir yayının ID'sini girin
# Örnek: https://www.youtube.com/watch?v=Hu_jH22g_8E ise ID: Hu_jH22g_8E
video_id = "8f9eG7QS5jg"

try:
    chat = pytchat.create(video_id=video_id)
    print(f"Bağlantı kuruldu: {video_id}")
    
    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"{c.datetime} [{c.author.name}]- {c.message}")
            
except Exception as e:
    print(f"Hata oluştu: {e}")