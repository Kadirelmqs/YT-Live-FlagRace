import json
import re
import pycountry
from babel import Locale
from babel.core import get_global

def clean_text(text):
    if not text:
        return ""
    cleaned = text.lower()
    # Sadece belirli noktalama işaretlerini boşluğa çevir, alfabeye dokunma
    cleaned = re.sub(r'[.,&\-\'()\[\]/]', ' ', cleaned)
    return re.sub(r'\s+', ' ', cleaned).strip()

def generate_native_dictionary():
    country_lookup = {}

    # 1. Standart kısaltmalar ve İngilizce isimler (pycountry)
    for country in pycountry.countries:
        alpha_2 = country.alpha_2
        # alpha_2 ve alpha_3 kodlarını ekle
        country_lookup[alpha_2.lower()] = alpha_2
        if hasattr(country, 'alpha_3'):
            country_lookup[country.alpha_3.lower()] = alpha_2
            
        # İngilizce tam isimleri temizleyerek ekle
        name_clean = clean_text(country.name)
        if name_clean:
            country_lookup[name_clean] = alpha_2
        
        if hasattr(country, 'official_name'):
            off_clean = clean_text(country.official_name)
            if off_clean:
                country_lookup[off_clean] = alpha_2

    # 2. Ülkelerin SADECE ana resmi dillerindeki isimleri (Babel)
    territory_languages = get_global('territory_languages')
    
    for territory_code, languages in territory_languages.items():
        if not isinstance(territory_code, str) or len(territory_code) != 2:
            continue
            
        for lang_code, info in languages.items():
            # KURAL: Sadece ÜLKE ÇAPINDA resmi (official) olan ve
            # nüfusun en az %15'i tarafından konuşulan dilleri al.
            # Bu filtre, Avusturya'daki Macarca gibi bölgesel/azınlık dillerini eler.
            is_official = info.get('official_status') == 'official'
            pop_percent = info.get('population_percent', 0)
            
            if is_official and pop_percent > 15:
                try:
                    loc = Locale(lang_code)
                    native_name = loc.territories.get(territory_code)
                    if native_name:
                        cleaned_native = clean_text(native_name)
                        if cleaned_native:
                            country_lookup[cleaned_native] = territory_code
                except Exception:
                    continue

    # 3. Manuel Eklemeler (Canlı yayınlar için elzem olan özel kısaltmalar)
    # Bunlar en son döngüde eklenir ki asla üzerine yazılıp kaybolmasın.
    custom_aliases = {
        "uk": "GB", 
        "usa": "US", 
        "us": "US", 
        "uae": "AE", 
        "turkiye": "TR", 
        "türkiye": "TR", 
        "turkey": "TR",
        "polska": "PL",
        "deutschland": "DE",
        "russia": "RU",
        "korea": "KR",
        "japan": "JP",
        "brasil": "BR",
        "spain": "ES",
        "italy": "IT",
        "france": "FR"
    }
    
    for alias, code in custom_aliases.items():
        cleaned_alias = clean_text(alias)
        if cleaned_alias:
            country_lookup[cleaned_alias] = code

    # JSON olarak dışa aktar
    with open('country_aliases.json', 'w', encoding='utf-8') as f:
        json.dump(country_lookup, f, ensure_ascii=False, indent=4)
        
    print(f"Başarılı! Toplam {len(country_lookup)} benzersiz, temizlenmiş ve filtrelenmiş eşleşme bulundu.")
    print("country_aliases.json dosyasına kaydedildi.")

if __name__ == "__main__":
    generate_native_dictionary()