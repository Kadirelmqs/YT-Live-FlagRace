# 🎮 FLAG BATTLE ROYALE - OYUN DOKUMANTASYONU

## 📑 İçindekiler
1. [Oyunun Konsepti](#oyunun-konsepti)
2. [Teknik Mimarı](#teknik-mimarı)
3. [Dosya Yapısı ve Açıklamaları](#dosya-yapısı-ve-açıklamaları)
4. [Oyun Akışı](#oyun-akışı)
5. [Ana Mekanikler](#ana-mekanikler)
6. [Bileşenler Arasındaki İletişim](#bileşenler-arasındaki-iletişim)
7. [Konfigürasyon ve Ayarlar](#konfigürasyon-ve-ayarlar)

---

## 🎯 Oyunun Konsepti

**FLAG BATTLE ROYALE - LIVE EDITION**, YouTube Canlı Yayın entegrasyonlu, interaktif bir bayrak tanıma ve topla oyunudur.

### Ana Özellikler:
- 🌍 Bayrakları dönen çember içinde yakala
- 💬 YouTube sohbetinden katılımcı adlarını ve ülke adlarını oku
- ❤️ Beğeni sayacı ve "Kaos Modu" sistemi
- 💎 Süper Chat yardımcıları oyunu etkile
- 🏆 Liderlik tablosu ve sıralama sistemi
- 📊 Dönem sonunda kazanan belirleme

---

## 🏗️ Teknik Mimarı

### Tasarım Desenleri:
1. **State Pattern**: Oyun durumlarını (Menü, Geri Sayım, Oyun, Kazanan) yönetir
2. **Manager Pattern**: Bayrak, UI, Sohbet yönetimi merkezi noktalardan yapılır
3. **Queue Pattern**: Sohbet ve Süper Chat olayları kuyruğa konur, asenkron işlenir
4. **MVC Ayrışması**: Fizik motoru (Model), Oyun mantığı (Controller), Pygame çizim (View) ayrı

### Katmanlar:

```
┌─────────────────────────────────────────┐
│         PYGAME RENDER LAYER             │ ← UI, Grafikler, Çizim
├─────────────────────────────────────────┤
│       GAME ENGINE (game_engine.py)      │ ← Durum Yönetimi, Kaynaklar
├─────────────────────────────────────────┤
│     STATE MACHINE (game_states.py)      │ ← Menü, Countdown, Oyun, Kazanan
├─────────────────────────────────────────┤
│  PHYSICS ENGINE (pymunk + physics_core) │ ← Fizik Simülasyonu
├─────────────────────────────────────────┤
│    EVENT HANDLERS (chat, like, super)   │ ← YouTubе API, Sohbet
└─────────────────────────────────────────┘
```

---

## 📂 Dosya Yapısı ve Açıklamaları

### 🎬 Ana Dosyalar

#### **1. game.py** (OYUNUN GİRİŞ NOKTASI)
```
Görev: Oyunun başlangıcı
Sorumluluk:
  • Pygame başlatma
  • Pencere oluşturma (WindowManager aracılığı)
  • Ana oyun loop'u çalıştırma (60 FPS)
  • Event handling, update ve draw döngüsü

Ana Loop Mantığı:
  1. Event işle (pencere kapatma, controller input)
  2. Oyun motorunu güncelle (dt bazında)
  3. Ekrana çiz ve flip
  
Dosya İliş:
  - game_engine.py: FlagBattleGame sınıfı
  - window_manager.py: Pencere yönetimi
  - settings.py: Ayarlar
```

---

#### **2. game_engine.py** (MERKEZI OYUN MOTORU)
```
Görev: Oyunun tüm bileşenlerini orkestrasyonu
Sorumluluk: MERKEZİ KONTROL MERKEZİ

A) KAYNAKLAR BAŞLATMA:
   - Bayrakları yükleme (FlagManager)
   - Arka planı yükleme
   - Yazı tiplerini başlatma
   - UI panellerini oluşturma (Liderlik, Beğeni, Sonraki Bayraklar)

B) FİZİK DÜNYASI:
   - Pymunk Space başlatma
   - Yer çekimi ve damping ayarları
   - Çember gövdesi oluşturma
   - Oyun nesneleri klasörü

C) OYUN DURUMU YÖNETİMİ:
   - Durum makinesi (switch_state)
   - Liderlik tablosu
   - Oyun nesneleri listesi

D) SOHBET SİSTEMİ:
   - Chat ile iletişim kuyruk (chat_event_queue)
   - Süper Chat kuyruk (super_chat_queue)
   - Beğeni takipçisi (LikeTracker)
   - Arka planda çalışan sohbet threadı

E) ANA FONKSİYONLAR:
   ```
   update(dt):
     - Fizik simülasyonu güncelle
     - Oyun durumunu güncelle
     - Panelleri güncelle
     
   draw():
     - Çıkış buffer'ına render et (handle_event'te gerçekleşti)
     - Tüm bileşenleri çiz
   ```

Veri Akışı:
  YouTube Chat → (chat_listener_task) → chat_event_queue
                                      → next_round_queue (Sonraki tur için sakla)
  Sohbet olayı → spawn_flag() → game_objects listesi → fizik simulate → liderlik güncelle
```

---

#### **3. game_states.py** (DURUM MAKİNESİ)
```
BASE CLASS: GameState (ABC - Soyut Temel Sınıf)

TÜRETILEN DURUMLAR:
┌──────────────────────────────────────────────────────────────┐
│ 1. MenuState                                                  │
├──────────────────────────────────────────────────────────────┤
│ • Menü ekranı görüntüle                                       │
│ • Sliderlardan ayarları oku (Başlangıç Boşluğu, Tur Süresi)  │
│ • Video ID textbox'ından YouTube ID al                       │
│ • BASLA butonuna basınca oyun başla                          │
│ • Arka plan resmi çerçeveleme                                │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. CountdownState (GERİ SAYIM - 3 SANİYE)                   │
├──────────────────────────────────────────────────────────────┤
│ • 3 saniye geriye doğru geri sayım göster                     │
│ • Çemberi çiz (dönüşüyor)                                     │
│ • Bayrakları çiz                                              │
│ • UI panellerini göster                                       │
│ • Süresi bitince GamePlayState'e geç                         │
│ • Önceki sohbet kuyruğunu temizle                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 3. GamePlayState (ANA OYUN - 20 SANİYE VARSAYILAN)          │
├──────────────────────────────────────────────────────────────┤
│ SORUMLULUKLARI:                                               │
│ • Fizik simülasyonunu güncelle                                │
│ • Sohbet olaylarını işle (chat_event_queue'dan oku)          │
│ • Bayrakları spawn et ve fizik motoruna ekle                  │
│ • İçinde bayrak tutma algılaması                              │
│ • Zaman bittiğinde (play_time > round_time) şunlar:         │
│   - Kazananı belirle (İçinde en fazla bayrak)                │
│   - Liderliği güncelle                                        │
│   - WinnerState'e geç                                         │
│                                                              │
│ KAOS MODU (FEVER MODE):                                       │
│ • Beğeni hedefi tuttuğunda tetiklenir                         │
│ • Çapraz duvarlar eklenir                                     │
│ • Çember sallanır (shake effect)                              │
│ • Bayrak hızı artar                                           │
│ • Renkler değişir                                             │
│                                                              │
│ ALT FONKSIYONLAR:                                            │
│ • _process_chat_events(): Sohbetten gelen olayları işle      │
│ • _update_physics(): Fizik simülasyonunu adımla             │
│ • _check_boundaries(): Sınır kontrolleri                     │
│ • _check_winner(): Kazananı belirle                          │
│ • _draw_circle(): Çemberi çiz                                │
│ • _draw_flags(): Bayrakları çiz                              │
│ • _draw_leaderboard(): Liderlik tablosunu çiz               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 4. WinnerState (KAZANAN GÖSTERME)                           │
├──────────────────────────────────────────────────────────────┤
│ • Kazananın adını ve skoru göster                            │
│ • Büyük metin animasyonu                                      │
│ • Ufak bekletme (1-2 saniye)                                  │
│ • MenuState'e geri dön                                        │
└──────────────────────────────────────────────────────────────┘

DURUM GEÇİŞ DİYAGRAMI:
    ┌─────────────────────────────────────────────────┐
    │                MENU                             │
    │  (Sliders, Video ID, BASLA Butonu)             │
    │                                                  │
    └─────────────┬──────────────────────────────────┘
                  │ (BASLA Butonuna tıkla)
                  ↓
    ┌─────────────────────────────────────────────────┐
    │           COUNTDOWN (3 SANİYE)                  │
    │              3 → 2 → 1                          │
    └─────────────┬──────────────────────────────────┘
                  │ (Süresi bitti)
                  ↓
    ┌─────────────────────────────────────────────────┐
    │       GAMEPLAY (20 SANİYE VARSAYILAN)          │
    │    • Bayraklar yağıyor                          │
    │    • Sohbetten katılımcı adları geliyor        │
    │    • Toplayıp skoru artırıyorsun               │
    │    • Kaos modunda daha hızlı başına yağıyor   │
    └─────────────┬──────────────────────────────────┘
                  │ (Tur süresi bitti)
                  ↓
    ┌─────────────────────────────────────────────────┐
    │          WINNER SCREEN (1-2 SANİYE)            │
    │    📊 [İsim]: Toplam [Skor] Bayrak             │
    └─────────────┬──────────────────────────────────┘
                  │ (Bitti)
                  ↓
              MENU'ye Dön
```

---

#### **4. settings.py** (MERKEZI AYARLAR)
```
Görev: Oyunun tüm parameterlerini bir yerde saklamak

KATEGORİLER:

A) EKRAN AYARLARI:
   WIDTH, HEIGHT = 600, 1066 (Canlı yayın panel boyutu)
   CIRCLE_CENTER = (300, 682.24) (Çemberin merkezi)

B) OYUN MEKANİĞİ AYARLARI (SETTINGS dict):
   - gravity: 200 (Yer çekimi)
   - flag_size: 15 (Bayrak çapı piksel)
   - initial_gap: 30 (Başlangıç boşluğu derece)
   - round_time: 20 (Tur süresi saniye)
   - auto_spawn: 40 (Başlangıç bayrak sayısı)
   - rotation_speed: 1.5 (Çember dönme hızı rad/s)

C) İÇ AYARLAR (INTERNAL_SETTINGS dict):
   - circle_radius: 260 (Çemberin yarıçapı piksel)
   - elasticity: 1.1 (Çarpışma esnekliği)
   - wall_thickness: 8 (Duvar kalınlığı piksel)

D) RENK PALETESİ:
   COLOR_BG: Arka plan siyahı
   COLOR_ACCENT: Yeşil (çember duvarı)
   COLOR_PANEL_BG: Koyu panel rengi
   COLOR_GOLD, SILVER, BRONZE: Madalya renkleri
   vb.

E) UI PANEL AYARLARI:
   LEADERBOARD_PANEL: Liderlik tablosu konumu/boyutu
   LIKE_BAR_SETTINGS: Beğeni barı
   NEXT_FLAGS_PANEL: Sonraki bayraklar paneli
   SUPER_CHAT_UI: Süper Chat banner'ı
   SUPER_CHAT_SETTINGS: Süper Chat kuralları
   vb.

F) YAZITIP AYARLARI:
   Font boyutları ve adları

G) API AYARLARI:
   YOUTUBE_API_KEY: YouTube API anahtarı
   vb.

```

---

### 🎨 UI ve Grafik Dosyaları

#### **5. ui_elements.py** (TEMEL BİLEŞENLER)
```
İçerdikleri Bileşenler:

A) TextBox (Metin Giriş Kutusu):
   • Tuş takımı girişini alıyor
   • Ctrl+A, Ctrl+C, Ctrl+V desteği
   • ENTER ile onaylama
   • Menüde Video ID girileceği zaman kullanılıyor

B) Slider (Kaydırma Çubuğu):
   • Min-Max aralığında değer seçme
   • Mouse dragı ile kontrol
   • Menüde 5 tane slider var:
     1. Başlangıç Boşluğu (10-50)
     2. Tur Süresi (10-30 saniye)
     3. Başlangıç Bayrak Sayısı (0-80)
     4. Gravity (0-400)
     5. Dönme Hızı (0.0-3.0)

C) Button (Buton):
   • Click algılaması
   • Menüde BASLA butonunun kendisi
   • Callback function desteği

KULLANILAN KONUMLAR:
- MenuState'de render edilir
- Slider ve TextBox event handling yapılır
```

---

#### **6. ui_panels.py** (BÖLÜNMÜŞ UI PANELLERİ)
```
Bağımsız panel bileşenleri (Tekrar kullanılabilir Component'ler)

A) LeaderboardPanel (Liderlik Tablosu):
   • En iyi 5 katılımcıyı göster
   • Sırayla puanları liste (Altın/Gümüş/Bronz renkleri)
   • Otomatik kaydırma efekti (Durur → Kaydır → Duraklat → Tekrar)
   • Konumu ayarlanabilir (x, y)
   
   Veri Kaynağı:
     game.leaderboard = {
       "İsim1": 15,  (15 bayrak topladı)
       "İsim2": 12,
       ...
     }

B) NextFlagsPanel (Sonraki Bayraklar):
   • Sıradaki 5 bayrak türünü göster
   • Yatay scroll efekti
   • Gelecek bayrakları ön hazırlamak için
   
   Veri Kaynağı:
     game.next_round_queue = ["TR", "US", "DE", ...]

C) LikeBarPanel (Beğeni Barı):
   • Hedef kırmızı bar göster (TikTok stil)
   • Current likes dolu miktar
   • Target likes hedef miktar
   • Hedef ulaştığında kaos modunu tetikle
   
   Veri Kaynağı:
     game.current_likes = 250

D) EasterEggBanner (Özel Banner - "67 = BAN!"):
   • Kırmızı metin titreşim efekti
   • Spesifik İçerik (Easter Egg)

E) SuperChatBanner (Süper Chat Banner):
   • 💎 SUPER CHAT = CHAOS MODE 🌪️
   • Titreşim ve palsating efekt
   • Süper Chat gelince görünür

ORTAK ÖZELLİKLER:
- set_alpha(): Saydamlık ayarı
- draw(): Kendi ekran koordinatlarında çizim
- update(): Animasyon ve scroll mantığı
```

---

#### **7. window_manager.py** (PENCERE YÖNETİMİ)
```
Görev: Pygame penceresini profesyonel şekilde yönetmek

Özellikler:
• pygame.SCALED: GPU ile pencere ölçekleme (kalite loss yok)
• pygame.RESIZABLE: Pencereyi tutarak büyütüp küçültebilirsin
• Donanım ivmesi (Hardware Acceleration)

Kullanım:
  wm = WindowManager(600, 1066, "Flag Battle Royale")
  screen = wm.create_window()
```

---

### 🌍 İçerik (Bayraklar) Yönetimi

#### **8. flag_handler.py** (BAYRAK YÖNETİCİSİ)
```
Görev: Bayrak resimlerini yükleme, cache'leme ve sağlama

CLASS: FlagManager
  
İnitializasyon:
  • flags/ klasöründeki tüm .png ve .jpg dosyaları tara
  • Dosya adından ülke kodunu çıkar (örn: "us.png" → "US")
  • pycountry kütüphanesi ile ülke adını bul (örn: "United States")
  • Resimleri RAM'e yükle (convert_alpha ile optimize)

KACHESİ (Performans Optimizasyonu):
  cache_key = f"{code}_{width}_{height}"
  • Örn: "TR_33_22" → Türkiye bayrağı 33x22 piksel
  • Aynı boyut tekrar istenirse O(1) hızında döndür
  • Cache'in 500 öğeyi aşması durumunda clear()

FONKSİYONLAR:
  
  get_flag_by_code(code, target_w, target_h):
    • Ülke kodundan (örn "TR") bayrak resmini döndür
    • İstenilen boyuta ölçekle ve cache'le
    • Kod bulunamazsa rastgele bayrak döndür
  
  get_random_flag(w, h):
    • Random bir bayrak resmini döndür
    • Başlangıçta spawn için kullanılır
  
  load_flags():
    • flags/ klasöründen bayrakları yükle
    • Hata durumunda tuple yaz

DOSYA YAPISUNDA:
  flags/
    ├── us.png          (ABD bayrağı)
    ├── tr.png          (Türkiye bayrağı)
    ├── de.png          (Almanya bayrağı)
    └── ... (150+ ülke bayrağı)
```

---

### 💬 Sohbet Sistemi

#### **9. chat_handler.py** (YOUTUBE SOHBET KAYIT ALICI)
```
Görev: YouTube sohbetini dinle ve ülke adlarını çıkar

FONKSİYONLAR:

A) clean_text(text):
   • Metni küçük harfe dönüştür
   • Noktalama işaretlerini boşluk yap (örn: "Türkiye," → "turkiye ")
   • Boşlukları temizle
   
B) find_country_code(text):
   • Gelen metinden ülke kodunu bulmaya çalış
   • Adımlar:
     1. Metni temizle
     2. country_aliases.json'da ara (O(1) lookup)
     3. Bulunursa ülke kodunu döndür (örn: "TR")
   • Örn:
     "türkiye" → "TR"
     "turkey" → "TR"
     "US" → "US"

C) _load_country_lookup():
   • Program başında country_aliases.json yükle
   • dictionary yapısı: {temiz_metin → ülke_kodu, ...}
   • 10,000+ varyasyon var (Tüm diller)

CHAT DINLEME İŞLEMİ:
  1. game_engine.py'dan chat_listener_task() başlatıl
  2. pytchat kütüphanesi YouTube RTMP sohbetine bağlan
  3. Her sohbet mesajı gelince:
     - Mesaj metnini temizle
     - find_country_code() ile ülke kodunu bul
     - (name, code) şeklinde tuple oluştur
     - chat_event_queue'ya ekle (oyun loop'una haber ver)
     - next_round_queue'ya da ekle (Sonraki tur için)

DÖNEM SONU İŞLEMİ:
  • next_round_queue'daki tüm katılımcılar liderliğe kaydedilir
  • İsim → Bayrak Sayısı eşleştirmesi yapılır
```

---

#### **10. build_dict.py** (ÜLKE SÖZLÜĞÜ OLUŞTURMA)
```
Görev: country_aliases.json'ı oluşturmak (Bir kerelik setup)

PROSES:
1. pycountry kütüphanesi'ndeki tüm ülkeleri yükle
2. İngilizce isimler ve ISO kodları kayıt et
3. Babel kütüphanesi ile her ülkenin resmi dilindeki adını çevir
4. 15%+ nüfuz tarafından konuşulan resmi diller seç (Azınlık dillerini hariç tut)
5. Tüm adları temizle (clean_text) ve sözlüğe ekle

SONUÇ (country_aliases.json):
  {
    "tr": "TR",
    "turkey": "TR",
    "türkiye": "TR",
    "turquia": "TR",
    "turkiye": "TR",
    "turquie": "TR",  (Fransızca)
    "türkei": "TR",   (Almanca)
    ...
    10.000+ benzersiz giriş
  }

KULLANIM:
  python build_dict.py  (Bir kerelik çalıştır)
  
```

---

### ❤️ Beğeni ve Hediyelendirme

#### **11. like_handler.py** (YOUTUBE BEĞENI TAKIPÇISI)
```
Görev: YouTube videosunun gerçek zamanında beğeni sayısını takip et

CLASS: LikeTracker

FÖNKSİYON:
  
  __init__(api_key, video_id):
    • YouTube API anahtarını sakla
    • Video ID'yi sakla
    • Başlangıç likes = 0
  
  start():
    • Arka planda çalışan thread başlat (_fetch_likes_loop())
  
  _fetch_likes():
    • YouTube API'sine HTTP GET isteği yap
    • Endpoint: https://www.googleapis.com/youtube/v3/videos
    • Parameters: part=statistics, id=video_id, key=api_key
    • Response: { items: [ { statistics: { likeCount: 12345 } } ] }
    • likeCount çıkar ve döndür
    • HTTP hatası varsa (403, 404) programdan çık
  
  _fetch_likes_loop():
    • 2-3 saniye aralığqmda sürekli _fetch_likes() çağır
    • current_likes güncelle
    • first_sync_done = True (İlk çekim yapıldı)

THREADLEME (ASENKRON):
  • Oyun loop'u bloke edilmediğinden ana thread devam eder
  • Her frame'de game.current_likes okunur (thread-safe)
  • Arka planda likes setbe zamanı gelince güncellenir

HATA YÖNETİMİ:
  • API anahtarı geçersizse 403 → Program kapatılır (os._exit(1))
  • Video ID yanlışsa 404 → Program kapatılır
  • Network hatası → Uyarı yazıp devam
```

---

#### **12. super_handler.py** (SÜPER CHAT YÖNETMAN)
```
Görev: YouTube Süper Chat / Bağış olaylarını işle oyunu etkile

CLASS: SuperChatHandler

KURAL MOTORU:
  Gelen Süper Chat'ın miktarına ve para birimine göre oyuna müdahale et

MEVCUT KURALLARI (Basit):
  • Herhangi bir Süper Chat → KAOSVat Modunu tetikle/uzat
  
GELECEK ÖZELLIKLERI (Planlanmış):
  • USD >= 5 → Boss Modu (Büyük bayraklar)
  • TRY >= 100 → Dev bayrak eki Mod
  • vb.

FONKSİYONLAR:

  __init__(gameplay_state):
    • GamePlayState'e erişim tut
    • super_chat_queue'yu oku

  update():
    • Her frame'de queue'yu kontrol et
    • Yeni Süper Chat gelirse işle

  _route_action(data):
    • Gelen Süper Chat'ı kural motorundan geçir
    • İlgili action fonksiyonunu çağır

  _trigger_chaos_mode():
    • fever_active = True
    • fever_timer uzat
    • Çember merkezine spiral duvarlar ekle
    • Bayrak hızı artar
    • Renkler değişir

VERI YAPISI (super_chat_queue'da):
  {
    "author": "ChatWhoGaveMoney",
    "amount_val": 5.0,
    "currency": "USD",
    "message": "Siz Takip Ettiğim Daha İyi Oyunu Yapın!"
  }
```

---

### 🎮 Fizik Motoru

#### **13. physics_core.py** (FİZİK SİMÜLASYONU)
```
Görev: Pymunk fizik motorunu yönetme

KULLANILAN KÜTÜPHANELER:
  • pymunk: 2D fizik simülasyonu
  • math: Matematik işlemleri (sin, cos, trigonometri)

FONKSİYONLAR:

A) create_circle_body(space, pos, rotation_speed):
   • Dönen çemberin gövdesini oluştur
   • body_type = KINEMATIC (dışından hareket ettirilir)
   • Konum ve açısal hız ayarla
   • space'e ekle
   • Dönen body'yi döndür

B) rebuild_circle_segments(space, body, radius, gap_angle_deg):
   • Çember duvarlarını segment'lerden yeniden oluştur
   • Adımlar:
     1. Daire 360° yi 120 parça böl
     2. Her parçanın başlangıç (as) ve bitiş (ae) açısını hesapla
     3. gap (boşluk) alanını atla
     4. gap_start = -gap_angle_deg/2, gap_end = +gap_angle_deg/2
     5. Her segment için pymunk.Segment oluştur
     6. Esneklik (elasticity) ve friction ayarla
     7. space'e ekle
   
   HUNÎ KOLLARINI EKLE (FUNNEL ARMS):
     • gap_start ve gap_end'den dışarıya doğru V şeklinde kol uzat
     • Bayrağı yakalamadan çıkması engelle
     • funnel_length = 100 piksel
     • funnel_flare = 50 derece

C) spawn_flag(space, pos, radius, specific_data, flag_manager):
   • Yeni bir bayrak fizik nesnesi oluştur
   • Parametreler:
     - space: Fizik dünyası
     - pos: Başlangıç konumu (x, y)
     - radius: Çapı
     - specific_data: Bayrak bilgisi (resim, ülke adı vb)
   • Adımlar:
     1. Kütle ve moment hesapla
     2. pymunk.Body oluştur
     3. pymunk.Circle (dairesel hitbox) añade
     4. Esneklik ve friction ayarla
     5. custom_data'ya bayrak bilgisi ata
     6. space'e ekle

D) limit_velocity(body, gravity, damping, dt):
   • Bayrakların maksimum hızını sınırla (500 px/s)
   • Çok hızlı hareket etmeyi engelle
   • İşlem:
     1. Hız vektörünün uzunluğunu hesapla
     2. MAX_VELOCITY aşarsa normalleştir
     3. Body'nin velocity_func'ı olarak ayarla (custom gravity)

SEGMENT VE SHAPE'LER:

  ┌─────────────────────────────────────────┐
  │         ╔═════════════╗                 │
  │        ╱               ╲ ← Hunî Kolları
  │       │      ○○○       │                │
  │       │     ○     ○     │ ← Segment'ler │
  │       │    ○       ○    │                │
  │       │    ○ BAYRAK ○   │                │
  │       │     ○     ○     │                │
  │       │      ○○○       │                │
  │        ╲               ╱                │
  │         ╚═════════════╝ ← GAP (BOŞLUK) │
  │  200 px çerçevesinde yakalı bayraklar │
  └─────────────────────────────────────────┘

PYMUNK PARAMETRELERI:

  Elasticity (Esneklik): 1.1
    • 1.0 = Normal çarpışma
    • > 1.0 = Daha çok seken, enerji kazanan (Oyunda eğlenceli!)
  
  Friction (Sürtünme): 0.5
    • Düşük = Daha hızlı kaydırma
    • Yüksek = Daha fazla ağırlık
  
  Gravity: 200 (ve değişken)
    • Bayrakları şiddetle aşağı çek
  
  Damping: 0.9
    • Her frame'de hız biraz eksilir (yavaşlama)
    • 1.0 = Azalan yok (sürüp durur)
    • 0.9 = %10 hız kaybı per frame
```

---

## 🔄 Oyun Akışı

### Detaylı Adım Adım İşleyiş:

```
┌──────────────────────────────────────────────────────────────────┐
│ PROGRAM BAŞLANGICI (game.py)                                     │
├──────────────────────────────────────────────────────────────────┤
│ 1. pygame.init()                                                  │
│ 2. WindowManager → Penceresi oluş                                 │
│ 3. FlagBattleGame → oyun motoru init                             │
│ 4. pygame.scrap.init() → Panoya erişim                           │
│ 5. switch_state("menu")                                           │
└─────────────────┬──────────────────────────────────────────────┘
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ ANA OYUN LOOP (game.py - main())                                │
├──────────────────────────────────────────────────────────────────┤
│ while running:                                                    │
│   1. dt = clock.tick(60) / 1000.0  (60 FPS, delta time seconds) │
│   2. For each pygame.event:                                      │
│        • KEYDOWN, MOUSEBUTTONDOWN, QUIT vb.                     │
│        • game.handle_event(event)                                │
│   3. game.update(dt)        (Fizik, lojik, UI)                  │
│   4. game.draw()            (Ekran çiz)                          │
│   5. pygame.display.flip()  (Render et)                          │
└─────────────────┬──────────────────────────────────────────────┘
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ MenuState (Menü Sayfası)                                         │
├──────────────────────────────────────────────────────────────────┤
│ update(): Boş (İşlem yok)                                         │
│ draw():                                                            │
│  • Arka plana çiz                                                │
│  • Başlık yaz ("FLAG BATTLE")                                    │
│  • Video ID TextBox                                              │
│  • 5 adet Slider                                                 │
│    1. Başlangıç Boşluğu                                          │
│    2. Tur Süresi                                                  │
│    3. Başlangıç Bayrak Sayısı                                    │
│    4. Gravity                                                     │
│    5. Dönme Hızı                                                  │
│  • BASLA Buton                                                    │
│                                                                  │
│ Event Handling:                                                   │
│  • Mouse & Keyboard → Slider, TextBox, Button                   │
│  • BASLA Buton → start_new_game() → switch_state("countdown")   │
└─────────────────┬──────────────────────────────────────────────┘
                  │ (BASLA'ya tıkla)
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ start_new_game() (Oyun Başları - game_engine.py)               │
├──────────────────────────────────────────────────────────────────┤
│ 1. Sliderlardan ayarları oku (SETTINGS güncelle)                │
│ 2. _start_chat():                                                 │
│    • Video ID'den YouTube sohbetine bağlan                       │
│    • chat_listener_task() threadını başlat                      │
│    • LikeTracker thread'ini başlat                              │
│ 3. _reset_physics():                                              │
│    • Eski pymunk.Space temizle                                   │
│    • Yeni Space oluştur                                          │
│    • gravity ve damping ayarla                                   │
│    • Dönen çember gövdesi oluştur                               │
│    • Segment'lerden çember duvarı yeniden inşa et              │
│ 4. game_objects = [] (Eski bayrakları temizle)                  │
│ 5. _spawn_initial_flags():                                       │
│    • "auto_spawn" kadar bayrak oluştur                          │
│    • Her birini spawn_flag() ile fizik motoruna ekle            │
│ 6. switch_state("countdown")                                     │
└─────────────────┬──────────────────────────────────────────────┘
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ CountdownState (3 SANİYE GERIYE SAYIM)                          │
├──────────────────────────────────────────────────────────────────┤
│ start_time = time.time()                                          │
│                                                                  │
│ update(dt):                                                       │
│   elapsed = time.time() - start_time                             │
│   if elapsed >= 3:                                               │
│     switch_state("game")                                         │
│                                                                  │
│ draw():                                                            │
│  • Arka plana çiz                                                │
│  • Çemberi draw_circle() ile çiz (yeşil)                        │
│  • Bayrakları çiz                                                │
│  • Panelleri çiz (Liderlik, Beğeni, Next Flags)                │
│  • Geri sayım sayısını ortada yaz (3 → 2 → 1)                  │
│  • Sayı titreyip biçim kaydırma yapabilir                       │
└─────────────────┬──────────────────────────────────────────────┘
                  │ (3 saniye bitti)
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ GamePlayState (ASIL OYUN - 20 SANİYE)                           │
├──────────────────────────────────────────────────────────────────┤
│ start_time = time.time()                                          │
│ super_chat_handler = SuperChatHandler(self)                      │
│                                                                  │
│ update(dt):                                                       │
│  1. _process_chat_events():                                      │
│     • chat_event_queue'dan gelen olayları sırasıyla oku          │
│     • Her olay (name, code) için:                               │
│       - Bayrak resmini al                                        │
│       - spawn_flag() ile fizik motoruna ekle                    │
│       - game_objects'e ekle                                      │
│       - liderlik = {name: skor} güncelle                        │
│                                                                  │
│  2. _update_physics():                                            │
│     • Zaman geçişine göre boşluğu küçült (20 saniye boyunca)    │
│     • Kaos modunu kontrol et (likes hedefi tuttu mu)            │
│     • space.step(dt) çalıştır (pymunk simülasyonunu güncelle)   │
│     • Eski çember body temizle, segment'leri yeniden kurşa      │
│                                                                  │
│  3. super_chat_handler.update():                                 │
│     • super_chat_queue'dan Süper Chat'ları oku                  │
│     • Kaos modunu uzat/tetikle                                   │
│                                                                  │
│  4. _check_boundaries():                                          │
│     • out-of-bounds bayrakları temizle                           │
│                                                                  │
│  5. Zaman kontrolü:                                              │
│     time_played = time.time() - start_time                       │
│     if time_played > SETTINGS["round_time"]:                     │
│       • _check_winner():                                         │
│         - game_objects'i iterate et                              │
│         - Kazananı bul (en fazla bayrak içeren)                 │
│         - next_round_queue'dan liderliği oluştur                │
│       • switch_state("winner")                                   │
│                                                                  │
│ draw():                                                           │
│  • Arka plana çiz                                                │
│  • Çemberi çiz (Kaos modunda kırmızı, normal yeşil)            │
│  • game_objects'teki tüm bayrakları çiz                         │
│  • Panelleri çiz (Liderlik, Beğeni, Next Flags)                │
│  • Kalan zaman sayacı (progress bar)                            │
└─────────────────┬──────────────────────────────────────────────┘
                  │ (20 saniye bitti)
                  ↓

┌──────────────────────────────────────────────────────────────────┐
│ WinnerState (KAZANAN GÖSTERME)                                  │
├──────────────────────────────────────────────────────────────────┤
│ Bir katılımcı oyunun en çok bayrağını topladıktan sonra:        │
│ • Adını buyüterek göster                                         │
│ • Toplam bayrak sayısını göster                                 │
│ • Gold/Silver/Bronze medal emoji'si ile dekorasyon             │
│ • 1-2 saniye beklet                                              │
│ • self.start_time + 1.5s geçince switch_state("menu")          │
└─────────────────┬──────────────────────────────────────────────┘
                  │
                  ↓ (Evet, 2. turunu oynayabilirsiniz!)
                [MENU Sayfasına Dön]
```

---

### YouTube Sohbet Örnekleri:

```
SOHBET KAY DÜŞÜNCELER:

youtube.com/watch?v=VIDEO_ID (Canlı Yayın)
Sohbet Mesajları:
  ├─ UserA: "TURKEY" 
  │  ├─ clean_text: "turkey"
  │  ├─ find_country_code: Dictionary'de ara
  │  └─ → code = "TR" → spawn_flag(x, y, flag_data_TR)
  │
  ├─ UserB: "Almanya"
  │  ├─ clean_text: "almanya"
  │  └─ → code = "DE"
  │
  ├─ UserC: "🇺🇸" (ABD emoji'si)
  │  └─ → code = "US" (emoji handle ediliyor)
  │
  ├─ UserD: "Çek"
  │  └─ → code = "CZ" (Çek Cumhuriyeti)
  │
  └─ Admin: "/mute UserA"
     └─ → Görmezden gelindi (sohbet komutları işlenmez)

Sohbetin oyun motoruna gitmesi:
  
  pytchat.create(video_id="ABC123XYZ")
  → chat_listener_task() threadında döngü
  → Her mesaj: (author_name, country_code) tuple
  → chat_event_queue → push
  → game_engine.update() → _process_chat_events() → oku
  → spawn_flag(), liderlik güncelle
```

---

## 💡 Ana Mekanikler

### 1. 🎯 Bayrak Yakalama Mekanikler

```
TOPLANIM MANTIKLAMASI:

Bir bayrak şu şarttada "içinde tutulmuş" sayılmaktadır:
• Çemberin içinde (boşluk hariç) tam olarak yaşıyor
• Çemberin her hangi bir segment'inin dışında olmadığından
• Belirli bir zaman (tahmin: 0.5 saniye) içto sürmektedir

YANLIŞLıK: Bayraklar çemberin boşluğundan çıkabilir (funnel arms'den)

DOĞRU:Bayra yanını "tutma"
  • Pymunk collision detection
  • Her frame'de game_objects'i kontrol
  • Bayrak segment'den uzaklaştı mı? (distance_from_center > radius)
  • Evet → out_of_bounds → listeden sil
  • Hayır ve iço → leaderboard[author] += 1
```

### 2. 🔥 Kaos Modu (Fever Mode)

```
TETIKLEME ŞARTALARI:
• Beğeni barı hedefine ulaştı (10 → 20 → 30 → 40 → 50 vb)
• Veya Süper Chat geldi:
  - _trigger_chaos_mode()

KAOSVat MODUNDA NE OLUR:

A) ÇEMBER Fiziksel Değişimler:
   • Renk: COLOR_ACCENT (yeşil) → FEVER_MODE["circle_color"] (kırmızı?)
   • Sallanma (Shake): Taraflar boşlukta sin dalgası ile hareket
   • Duvar Hızı: Normal dönüş hızından daha fazla dönüş

B) BAYRAK Davranışı Değişimi:
   • Hız Sınırı: MAX_VELOCITY normal (500) → FEVER_MODE["fever_velocity"] (daha yüksek)
   • Bayraklar daha hızlı hareket
   • Çıkma riski artar (zor oyun)

C) GÖRSEL EFEKTLER:
   • Çemberin etrafında paralel çizgiler titreşim yapar
   • Animasyon parametreleri değişir
   • Pulse/flash efektler

D) SÜRE:
   • fever_duration = FEVER_MODE["duration"] saniye
   • Her Süper Chat'ta fever_timer uzatılır (stacking)
   • Sayaç 0'a ineince normal duruma dön

AYARLAR (settings.py):
  FEVER_MODE = {
    "duration": 5.0,            # Saç saniye dayanır
    "shake_amplitude": 10,      # Sallanan genliş (piksel)
    "shake_frequency": 0.01,    # Sallanma frekans
    "fever_velocity": 600.0,    # Kaos modunda hız sınırı
    "normal_velocity": 500.0,   # Normal hız sınırı
    "circle_color": (255, 0, 0), # Kırmızı
  }
```

### 3. 📊 Liderlik Tablosu

```
YAPISI:
  leaderboard = {
    "Ali": 15,       # 15 bayrak topladı
    "Ayşe": 12,
    "Mehmet": 10,
    "Fatih": 8,
    "Zeynep": 5
  }

GÜNCELLENMESI:
  1. Sohbetten yeni mesaj (name, code) geldi
  2. spawn_flag(name, ...) → fizik motoruna ekle
  3. Her frame'de bayrak çember içinde mi kontrol
  4. Bayrak çemberin içinde kalma hali başarılı
  5. leaderboard[name] += 1

OUTPUT ÖRNEĞİ (Oyun sırasında):
  ┌─────────────────────────┐
  │  LIDER TABLOSU        1.  │
  ├─────────────────────────┤
  │ 🥇 Ali       15         │
  │ 🥈 Ayşe      12         │
  │ 🥉 Mehmet    10         │
  │    Fatih      8         │
  │    Zeynep     5         │
  └─────────────────────────┘

NEXT ROUND'DA TRANSFER:
  • next_round_queue'daki tüm isimleri liderliğe akta
  • İleriye doğru geçişleri yapıldığında skorlar sıfırlanır
  • Madalyalar: 🥇 Altın, 🥈 Gümüş, 🥉 Bronz
```

### 4. 💬 Sohbet İntegrasyonu

```
SOHBET OKUME SÜRECI:

1. Kullanıcı YouTube canlı yayında mesaj yazar:
   "Türkiye"

2. pytchat kütüphanesi API'sini okur

3. chat_listener_task() fonksiyonu çalışır:
   while True:
     for msg in chat.get():  # API'den gelen mesajlar
       author = msg.author.name  # "UserA"
       text = msg.message  # "Türkiye"
       
       code = find_country_code(text)  # "TR"
       
       (author, code) tuple'ını queues'a ekle
       • chat_event_queue (hemen oyna)
       • next_round_queue (liderlik için sakla)

4. game_engine.update() sırasında:
   _process_chat_events() çağrılır
   
5. chat_event_queue'dan oku:
   name, code = queue.get()  # ("UserA", "TR")
   
6. Bayrak spawn et:
   flag_data = flag_manager.get_flag_by_code("TR", ...)
   obj = spawn_flag(space, pos, flag_size, flag_data)
   game_objects.append(obj)

7. Liderlik güncelle:
   if bayrak_çemberin_içinde:
     leaderboard[name] = leaderboard.get(name, 0) + 1

BAŞARIŞSIZ SOHBET ARAMA ÖRNEKLERİ:

"abc123" → find_country_code() → None → ülke bulunamadı
"!!!" → clean_text() → "!" → ülkenin adı değil
"" (Boş mesaj) → skip
```

---

## 🔌 Bileşenler Arasındaki İletişim

### Veri Akış Diyagramı:

```
┌──────────────────────────────────────────────────────────┐
│                  YOUTUBE LIVE STREAM                     │
│              (Sohbet: Ülke Adları)                        │
├──────────────────────────────────────────────────────────┤
│ pytchat (pytchat kütüphanesi)                            │
│ ├─ Message ID | Author Name | Text | Timestamp         │
│ └─ Thread: chat_listener_task() continuously reads      │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼ (Thread)
        ┌────────────────────────────────────────┐
        │    find_country_code(text)             │
        │ country_aliases.json'da ara            │
        │ "turkiye" → "TR" veya None             │
        └────────────────┬───────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
  ┌────────────────────┐    ┌────────────────────┐
  │ chat_event_queue   │    │ next_round_queue   │
  │ (İmmediate Play)   │    │ (End-of-Round)     │
  │ [(name, code), ..] │    │ [(name, code), ..] │
  └────────────────────┘    └────────────────────┘
          │                             │
          │ (game.update())             │
          │                             │ (Oyun bitince)
          ▼                             ▼
  ┌────────────────┐    ┌────────────────────────┐
  │ spawn_flag()   │    │ WinnerState'e Transfer │
  │                │    │ leaderboard oluştur    │
  │ 1. Bayrak      │    │                        │
  │    resmini al  │    └────────────────────────┘
  │ 2. Fizik obj   │
  │    oluştur     │
  │ 3. space'i     │
  │    ekle        │
  └────────────────┘
          │
          ▼
  ┌────────────────────┐
  │  game_objects[]    │
  │ (Aktif Bayraklar)  │
  └────────────────────┘
          │
          │ (Her frame)
          ▼
  ┌────────────────────┐
  │  space.step(dt)    │
  │ (Fizik simülasyon) │
  └────────────────────┘
          │
          ▼
  ┌─────────────────────────────┐
  │ Bayrak çember içinde mi?    │
  └───────┬─────────────────────┘
          │
    ┌─────┴─────┐
    │ Evet  Hayır
    ▼           ▼
 ┌─────┐     ┌─────┐
 │Tut! │     │Çık! │
 │+1   │     │Del  │
 │skor │     │list │
 └─────┘     └─────┘
```

### Event Akışı (Sohbet Komutları Dışında):

```
YouTube Api
    ↓
pytchat.create()
    ↓
pytchat.receive_messages()
    ↓
chat_listener_task():
    for msg in chat:
      author = msg.author.name
      text = msg.message
      code = find_country_code(text)
      ↓
      queue.put((author, code))
    ↓
game_engine.update():
    _process_chat_events():
      while not queue.empty():
        name, code = queue.get()
        flag = flag_manager.get_flag_by_code(code, ...)
        obj = spawn_flag(space, ..., flag)
        game_objects.append(obj)
        ↓
space.step(dt)
    ↓
_check_boundaries()
    if obj_inside_circle:
      leaderboard[name] += 1
    else:
      game_objects.remove(obj)
```

---

## ⚙️ Konfigürasyon ve Ayarlar

### settings.py yönetimi

```
MERKEZI AYARLAR TABLOSU:

┌──────────────────────────────────────────────────────┐
│ 1. EKRAN AYARLARI (Display)                         │
├──────────────────────────────────────────────────────┤
│ WIDTH: 600                                            │
│ HEIGHT: 1066                                          │
│ CIRCLE_CENTER: (300, 682.24)  # Çemberin merkezi    │
│ FLAGS_FOLDER: "flags"                               │
│ BACKGROUND_FILE_NAME: "background.jpg"              │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 2. OYUN AYARLARI (SETTINGS dict)                     │
├──────────────────────────────────────────────────────┤
│ gravity: 200                 # Yer çekimi            │
│ flag_size: 15                # İçeri bayrak çapı    │
│ initial_gap: 30              # Açılış açısı (derece)│
│ round_time: 20               # Başlangıç tur süresi │
│ auto_spawn: 40               # İlk bayrak sayısı    │
│ rotation_speed: 1.5          # Çemberin dönüşü      │
│ MAX_VELOCITY: 500            # Maksimum bayrak hızı │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 3. AYRIT AYARLARI (INTERNAL_SETTINGS dict)          │
├──────────────────────────────────────────────────────┤
│ circle_radius: 260           # Çemberin yarıçapı    │
│ elasticity: 1.1              # Çarpışma esnekliği   │
│ wall_thickness: 8            # Duvar kalınlığı      │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 4. RENK PALETESI (Pygame Color Tuples)              │
├──────────────────────────────────────────────────────┤
│ COLOR_BG: (20, 20, 20)                              │
│ COLOR_ACCENT: (24, 143, 3)   # Yeşil (~Çember)     │
│ COLOR_PANEL_BG: (12, 12, 24) # Koyu mavi panel     │
│ COLOR_GOLD: (255, 215, 0)    # 🥇 Altın            │
│ COLOR_SILVER: (192, 192, 192) # 🥈 Gümüş           │
│ COLOR_BRONZE: (205, 127, 50) # 🥉 Bronz            │
└──────────────────────────────────────────────────────┘

SLIDERS VE AYARLANABILIR PARAMETRELER:

Menü'de sliders var: 1-BASLA butonuna basıldığında
┌────┬─────────────────────┬──────┬──────┬────────┐
│ #  │ Slider Adı          │ Min  │ Max  │Default │
├────┼─────────────────────┼──────┼──────┼────────┤
│ 1  │ Başlangıç Boşluğu   │ 10   │ 50   │ 30     │
│ 2  │ Tur Süresi (sn)     │ 10   │ 30   │ 20     │
│ 3  │ Başlangıç Bayrak    │ 0    │ 80   │ 40     │
│ 4  │ Gravity             │ 0    │ 400  │ 200    │
│ 5  │ Dönme Hızı          │ 0.0  │ 3.0  │ 1.5    │
└────┴─────────────────────┴──────┴──────┴────────┘

YOUTUBE API AYARLARI:
  YOUTUBE_API_KEY: "AIzaSyDO2Dxxxxxxxxxxxxxxxxxxxxxxxx" (gerçek anahtar gerekli)
  
  Beğeni Barı Hedefi (Dynamic):
    def get_next_like_target(current_target):
      if current_target < 50:
          return current_target + 10  # 10, 20, 30...
      elif current_target < 200:
          return current_target + 20  # 70, 90, 110...
      else:
          return current_target + 50+ # 250, 300, 350...
```

---

## 🐛 Yaygın Sorunlar ve Çözümleri

### Sorun 1: YouTube API Anahtarı Eksik/Hatalı
```
Hata: "[HATA] YOUTUBE_API_KEY bulunamadı!"

Çözüm:
  1. YouTube Data API v3'ü etkinleştir (Google Cloud Console)
  2. API anahtarını kopyala
  3. settings.py'da YOUTUBE_API_KEY ayarla:
     YOUTUBE_API_KEY = "AIzaSy..."
```

### Sorun 2: Bayrak Resimleri Yüklenmiyor
```
Hata: "[ERROR] Arka plan yüklenemedi: [Errno 2] No such file or directory"

Çözüm:
  1. flags/ klasörü var mı kontrol et
  2. background.jpg var mı kontrol et
  3. flags/ klasöründeisi .png/.jpg dosyası var mı
  4. File isimlendir doğru mu (iki harf ülke kodu)
    Örn: us.png, tr.png, de.png
```

### Sorun 3: Sohbetten Ülke Bulunamıyor
```
Hata: Sohbet mesajları
 geliyor ama bayraklar spawn olmuyorcompile
Çözüm:
  1. country_aliases.json var mı kontrol et
  2. Boş mu sözlük kontrol:
     python build_dict.py (Yeniden oluştur)
  3. Temizlenmiş metin doğru mu test et:
     clean_text("TURKEY") = "turkey"
```

### Sorun 4: Düşük FPS / Uzun Yükleme
```
Hata: Oyun 60 FPS'den daha düşük çalışıyor

Çözüm:
  1. Bayrak cache'inden optimization
     • cache_key = f"{code}_{w}_{h}"
     • Tekrar istenen bayraklar O(1) olur
  
  2. Surface optimizasyonu:
     • convert_alpha() ile yükle (RAM-Video RAM)
  
  3. Physics optimization:
     • Bellek sızıntısı (memory leak) yamaş
     • Her frame de eski shape'leri silinir
```

---

## 📝 Dosya Bağlantıları Özet

| Dosya | Roller | Bağlı Olduğu |
|-------|--------|-------------|
| **game.py** | Ana entry point, loop | game_engine, settings |
| **game_engine.py** | Merkezi kontrol merkezi | Tüm modüller |
| **game_states.py** | Durum makinası | physics_core, ui_panels |
| **settings.py** | Ayarlar/Konfigürasyon | Tüm katmanlar |
| **ui_elements.py** | Temel UI bileşenleri | Pygame, settings |
| **ui_panels.py** | UI panelleri | ui_elements, settings |
| **window_manager.py** | Pencere yönetimi | Pygame |
| **flag_handler.py** | Bayrak yönetimi | pycountry, Pygame |
| **chat_handler.py** | Sohbet temizleme | country_aliases.json |
| **build_dict.py** | Sözlük oluşturma (Setup) | pycountry, Babel |
| **like_handler.py** | Beğeni takibi (Thread) | requests, YouTube API |
| **super_handler.py** | Süper Chat yönetimi | settings, game_states |
| **physics_core.py** | Fizik simülasyonu | pymunk, math |
| **country_aliases.json** | Ülke lookup tablosu | chat_handler |

---

## 🚀 Başlama Kılavuzu

### İlk Kez Çalıştırma:
```bash
# 1. Bağımlılıkları yükle
pip install pygame pymunk pytchat pycountry babel requests

# 2. Ülke sözlüğünü oluştur
python build_dict.py

# 3. Bayrakları flags/ klasörüne dumpla
#    İndirme: https://flagcdn.com/
#    Yada: "us.png", "tr.png", "de.png" ... (Ülke kodları)

# 4. YouTube API anahtarını ayarla
# settings.py'da: YOUTUBE_API_KEY = "AIzaSy..."

# 5. ÇALIŞTIR
python game.py
```

---

## 🎓 Geliştirme Tüyoları

### Yeni Özellik Ekleme:

1. **Yeni Durum (State) Ekleme:**
   ```python
   # game_states.py'a yeni class ekle
   class MyNewState(GameState):
       def __init__(self, game_engine):
           super().__init__(game_engine)
       
       def handle_event(self, event): pass
       def update(self, dt): pass
       def draw(self, screen): pass
   
   # game_engine.py switch_state'e yeni durum ekle
   elif state_name == "mynew":
       self.current_state = MyNewState(self)
   ```

2. **Yeni Ayar Ekleme:**
   ```python
   # settings.py'a ekle
   MY_NEW_SETTING = {
       "param1": value1,
       "param2": value2
   }
   ```

3. **Yeni Fizik Nesnesi:**
   ```python
   # physics_core.py'a fonksiyon ekle
   def add_custom_body():
       # Pymunk body oluştur
       # space'e ekle
   ```

---

**Dokümantasyon Sonu** 🎉

**Sorularınız Varsa:**
- Kodda yorumlar okuyun (Türkçe!)
- settings.py'dan ayarları inceleyebilirsiniz
- Modüller arası ilişkiyi veri akışı diyagramından izleyebilirsiniz
