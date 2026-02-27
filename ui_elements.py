import pygame
from settings import *

pygame.font.init()
font_ui = pygame.font.SysFont("Arial", 16, bold=True)

# --- TEXTBOX ---
class TextBox:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.active = False
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive
        self.select_all = False 

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
                self.select_all = False 
            self.color = self.color_active if self.active else self.color_inactive

        if event.type == pygame.KEYDOWN:
            if self.active:
                ctrl_held = (event.mod & pygame.KMOD_CTRL)

                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.select_all = False
                
                elif ctrl_held and event.key == pygame.K_a:
                    self.select_all = True
                
                elif ctrl_held and event.key == pygame.K_c:
                    if self.text:
                        pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode("utf-8"))

                elif ctrl_held and event.key == pygame.K_x:
                    if self.text:
                        pygame.scrap.put(pygame.SCRAP_TEXT, self.text.encode("utf-8"))
                        self.text = ""
                        self.select_all = False

                elif ctrl_held and event.key == pygame.K_v:
                    content = pygame.scrap.get(pygame.SCRAP_TEXT)
                    if content:
                        try:
                            paste_text = content.decode("utf-8").strip("\x00")
                            if self.select_all:
                                self.text = paste_text 
                                self.select_all = False
                            else:
                                self.text += paste_text 
                        except:
                            pass 

                elif event.key == pygame.K_BACKSPACE:
                    if self.select_all:
                        self.text = "" 
                        self.select_all = False
                    else:
                        self.text = self.text[:-1]
                
                else:
                    if not ctrl_held:
                        if self.select_all:
                            self.text = event.unicode 
                            self.select_all = False
                        else:
                            self.text += event.unicode

    def draw(self, screen):
        pygame.draw.rect(screen, (30, 30, 30), self.rect)
        
        if self.select_all and self.active:
            selection_rect = self.rect.inflate(-4, -4)
            pygame.draw.rect(screen, (0, 100, 200), selection_rect)

        txt_surface = font_ui.render(self.text, True, COLOR_TEXT)
        text_y = self.rect.y + (self.rect.height - txt_surface.get_height()) // 2
        screen.blit(txt_surface, (self.rect.x + 5, text_y))
        
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.text = text
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_x = event.pos[0]
                ratio = (mouse_x - self.rect.x) / self.rect.width
                ratio = max(0, min(1, ratio))
                self.val = self.min_val + (self.max_val - self.min_val) * ratio

    def draw(self, screen):
        val_str = f"{int(self.val)}"
        if "Donme" in self.text: val_str = f"{self.val:.1f}"
        
        label = font_ui.render(f"{self.text}: {val_str}", True, COLOR_TEXT)
        screen.blit(label, (self.rect.x, self.rect.y - 20))
        pygame.draw.rect(screen, (100, 100, 100), self.rect, border_radius=5)
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + (self.rect.width * ratio)
        handle_rect = pygame.Rect(handle_x - 10, self.rect.y - 5, 20, self.rect.height + 10)
        pygame.draw.rect(screen, COLOR_ACCENT, handle_rect, border_radius=5)

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_ACCENT, self.rect, border_radius=8)
        label = font_ui.render(self.text, True, (0, 0, 0))
        text_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, text_rect)
