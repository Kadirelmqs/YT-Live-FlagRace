import requests
import time
import threading

class LikeTracker:
    """
    Arka planda YouTube API'sine bağlanıp belirli aralıklarla beğeni sayısını çeker.
    Oyun motoru sadece 'current_likes' değişkenini okur.
    """
    def __init__(self, api_key, video_id):
        self.api_key = api_key
        self.video_id = video_id
        self.current_likes = 0
        self.is_running = False
        self.first_sync_done = False  # İlk çekim yapıldı mı?
        self._thread = None

    def _fetch_likes(self):
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {'part': 'statistics', 'id': self.video_id, 'key': self.api_key}
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('items'):
                return int(data['items'][0]['statistics'].get('likeCount', 0))
        except Exception as e:
            print(f"[LIKE API ERROR] {e}")
        return None

    def _track_loop(self):
        print(f"👍 Beğeni takipçisi başlatıldı (Video ID: {self.video_id})")
        while self.is_running:
            likes = self._fetch_likes()
            if likes is not None:
                self.current_likes = likes
                self.first_sync_done = True
            
            # API kotasını doldurmamak için her sorgu arası 10 saniye bekle
            # Beklemeyi 1'er saniyelik dilimlere böldük ki kapatılmak istendiğinde anında kapansın
            for _ in range(10):
                if not self.is_running:
                    break
                time.sleep(1)

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(target=self._track_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            print("🛑 Beğeni takipçisi durduruldu.")