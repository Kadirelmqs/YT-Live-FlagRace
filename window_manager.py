import pygame

class WindowManager:
    """
    Oyun penceresini donanımsal ivmelenme (GPU) ve 
    otomatik ölçekleme ile yöneten profesyonel modül.
    """
    def __init__(self, internal_width, internal_height, title="Flag Battle Royale"):
        self.internal_size = (internal_width, internal_height)
        self.title = title
        self.screen = None

    def create_window(self):
        """
        Pencereyi oluşturur ve ayarlarını yapar.
        pygame.SCALED: Ekran büyütüldüğünde kaliteyi bozmadan Ekran Kartı (GPU) ile sündürür. FPS düşmez.
        pygame.RESIZABLE: Pencere kenarlarından tutup büyütme/küçültme ve X butonunu aktif eder.
        """
        # Sihirli bayraklar (Flags)
        flags = pygame.SCALED | pygame.RESIZABLE 
        
        # Ekranı donanımsal ivmelenme ile başlat
        self.screen = pygame.display.set_mode(self.internal_size, flags)
        
        # Pencere başlığını ayarla
        pygame.display.set_caption(self.title)
        
        return self.screen