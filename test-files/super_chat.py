import pytchat

# Çok izlenen ve Super Chat yağan bir yayının veya VOD'un ID'sini gir
VIDEO_ID = "YwwBGa4MYOQ" 

chat = pytchat.create(video_id=VIDEO_ID)

print(f"[{VIDEO_ID}] Yayını dinleniyor... Sadece Super Chat'ler filtrelenecek.\n")

while chat.is_alive():
    for c in chat.get().sync_items():
        # Sadece bağışları filtrele
        if c.type in ["superChat", "superSticker"]:
            print("="*40)
            print(f"TÜR: {c.type}")
            print(f"GÖNDEREN: {c.author.name}")
            print(f"MESAJ: {c.message}")
            print(f"MİKTAR STRING: {c.amountString}")
            print(f"MİKTAR DEĞER: {c.amountValue}")
            print(f"PARA BİRİMİ: {c.currency}")
            print("="*40)