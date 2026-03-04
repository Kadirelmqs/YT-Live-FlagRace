# ==========================================
# FLAG BATTLE ROYALE - ANA OYUN LOOP
# ==========================================
"""
Oyunun ana giriş noktası.
FlagBattleGame sınıfını başlatır ve render loop'u çalıştırır.
"""

import pygame
import sys
from settings import *
from game_engine import FlagBattleGame
from window_manager import WindowManager

def main():
    """
    Oyunu başlat ve ana loop'u çalıştır.
    """
    pygame.init()
    
    # Ekranı oluştur
    # screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # pygame.display.set_caption("Flag Battle Royale - Live Edition")
    wm = WindowManager(WIDTH, HEIGHT, "Flag Learn Battle Royale - Live Edition")
    screen = wm.create_window()
    
    game = FlagBattleGame(screen)
    clock = pygame.time.Clock()
    
    # Clipboard desteğini başlat (ekrandan SONRA gerekli)
    try:
        pygame.scrap.init()
    except pygame.error:
        print("[WARN] Scrap sistemi başlatılamadı (Headless mod olabilir)")
    
    # Oyun motorunu başlat
    game = FlagBattleGame(screen)
    
    # Saat
    clock = pygame.time.Clock()
    running = True
    
    print("[INFO] Flag Battle Royale başladı!")
    
    # ==========================================
    # ANA OYUN LOOP
    # ==========================================
    while running:
        # FPS kontrolü (60 FPS)
        dt = clock.tick(60) / 1000.0  # delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                if not game.handle_event(event):
                    running = False
        
        # Update
        game.update(dt)
        
        # Draw
        game.draw()
        pygame.display.flip()
    
    # Cleanup
    game.shutdown()
    pygame.quit()
    print("[OK] Oyun sonlandırıldı.")
    sys.exit()

if __name__ == "__main__":
    main()