import requests
import time
import sys

API_KEY = "AIzaSyBx5GR7JooHT4zb0IEcoB9QV-C7lIcq290"  # Buraya anahtarınızı girin

if len(sys.argv) > 1:
    VIDEO_ID = sys.argv[1]
else:
    VIDEO_ID = input("Lütfen video ID'sini girin: ").strip()

def get_like_count(video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {'part': 'statistics', 'id': video_id, 'key': API_KEY}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data.get('items'):
            return None
        return int(data['items'][0]['statistics'].get('likeCount', 0))
    except Exception as e:
        print(f"Hata: {e}")
        return None

if __name__ == "__main__":
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ API anahtarını girmelisiniz.")
        sys.exit(1)

    print(f"🟢 YouTube Canlı Yayın Beğeni Takipçisi Başlatıldı.")
    print(f"📺 Video ID: {VIDEO_ID}")
    print("⏳ Her 10 saniyede bir sorgulanıyor. (Çıkmak için Ctrl+C)\n")

    last_count = None
    try:
        while True:
            current = get_like_count(VIDEO_ID)
            if current is not None:
                if current != last_count:
                    print(f"[{time.strftime('%H:%M:%S')}] 👍 Beğeni: {current}")
                    last_count = current
                else:
                    # Değişim yoksa nokta koy (çalıştığını göster)
                    print(".", end="", flush=True)
            else:
                print("!")  # Hata durumunda ünlem
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Durduruldu.")