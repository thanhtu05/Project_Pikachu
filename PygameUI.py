import pygame
import sys
import math

class PygameButton:
    """Pygame button with raised 3D effect"""
    
    def __init__(self, x, y, width, height, text, color, text_color=(0, 0, 0), font_size=16):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_pressed = False
        
        # Calculate bright and dark colors for 3D effect
        self.bright_color = tuple(min(255, c + 40) for c in color)
        self.dark_color = tuple(max(0, c - 40) for c in color)
        
    def draw(self, surface):
        """Draw the raised button with 3D effect"""
        x, y, w, h = self.rect
        
        # Main button background
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        
        if self.is_pressed:
            # When pressed, reverse the light/dark effect
            top_color = self.dark_color
            bottom_color = self.bright_color
        else:
            # Normal raised effect
            top_color = self.bright_color
            bottom_color = self.dark_color
        
        # Draw bright top border (raised effect)
        pygame.draw.line(surface, top_color, (x, y), (x + w, y), 3)
        pygame.draw.line(surface, top_color, (x, y), (x, y + h), 3)
        
        # Draw dark bottom border (raised effect)
        pygame.draw.line(surface, bottom_color, (x, y + h), (x + w, y + h), 3)
        pygame.draw.line(surface, bottom_color, (x + w, y), (x + w, y + h), 3)
        
        # Add outer shadow for depth
        shadow_rect = pygame.Rect(x + 2, y + 2, w, h)
        pygame.draw.rect(surface, (0, 0, 0, 50), shadow_rect, border_radius=12)
        
        # When hovered, add glow effect
        if self.is_hovered:
            glow_rect = pygame.Rect(x - 2, y - 2, w + 4, h + 4)
            pygame.draw.rect(surface, (255, 255, 255, 30), glow_rect, border_radius=14)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False

class PygameGameUI:
    """Pygame-based game UI with raised buttons"""
    
    def __init__(self, width=1000, height=700):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pikachu Game - Pygame UI")
        self.clock = pygame.time.Clock()
        self.width = width
        self.height = height
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 215, 0)  # Pikachu yellow
        self.GREEN = (50, 205, 50)   # Mint green
        self.RED = (255, 69, 58)     # Red
        self.ORANGE = (255, 165, 0)  # Orange
        self.BLUE = (100, 180, 255)  # Light blue
        self.GRAY = (200, 200, 200)  # Light gray
        
        # Load background
        try:
            self.background = pygame.image.load("background/backgroundmain.jpg")
            self.background = pygame.transform.scale(self.background, (width, height))
        except:
            self.background = pygame.Surface((width, height))
            self.background.fill((30, 30, 50))
        
        # Create buttons with raised effect
        self.buttons = []
        button_width = 120
        button_height = 50
        button_spacing = 20
        start_x = 50
        start_y = 100
        
        # Button colors and texts
        button_configs = [
            (self.YELLOW, "⚡ New Game", (40, 40, 40)),
            (self.GREEN, "🚀 Start Auto", (40, 40, 40)),
            (self.RED, "⏹️ Stop", (255, 255, 255)),
            (self.ORANGE, "▶️ Continue", (40, 40, 40)),
            (self.BLUE, "📊 History", (40, 40, 40)),
            (self.GRAY, "🏠 Home", (40, 40, 40))
        ]
        
        for i, (color, text, text_color) in enumerate(button_configs):
            x = start_x + i * (button_width + button_spacing)
            button = PygameButton(x, start_y, button_width, button_height, text, color, text_color, 18)
            self.buttons.append(button)
        
        # Status labels
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Game state
        self.cost = 0
        self.time = 0
        self.sound_on = True
        self.mode = "Manual"
        self.algorithm = "DFS"
        
    def draw_header(self):
        """Draw the game header with glassmorphism effect"""
        # Header background with glassmorphism
        header_rect = pygame.Rect(0, 0, self.width, 60)
        overlay = pygame.Surface((self.width, 60))
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_large.render("⚡ PIKACHU ⚡", True, self.YELLOW)
        self.screen.blit(title_text, (20, 15))
        
        # Status info with glassmorphism containers
        status_items = [
            (f"⚡ Cost: {self.cost}", (220, 15), self.YELLOW),
            (f"⏱️ Time: {self.time}s", (360, 15), self.ORANGE),
            (f"🔈 Sound: {'ON' if self.sound_on else 'OFF'}", (500, 15), self.BLUE),
            (f"Mode: {self.mode}", (650, 15), self.WHITE),
            (f"Algo: {self.algorithm}", (780, 15), self.WHITE)
        ]
        
        for text, pos, color in status_items:
            # Glassmorphism container
            container_rect = pygame.Rect(pos[0] - 10, pos[1] - 5, 80, 25)
            container_surface = pygame.Surface((80, 25))
            container_surface.set_alpha(50)
            container_surface.fill((255, 255, 255))
            self.screen.blit(container_surface, container_rect)
            
            # Text
            text_surface = self.font_medium.render(text, True, color)
            self.screen.blit(text_surface, pos)
    
    def draw_game_board(self):
        """Draw the game board area"""
        board_rect = pygame.Rect(50, 200, 900, 450)
        
        # Board background
        pygame.draw.rect(self.screen, (26, 26, 46), board_rect, border_radius=10)
        
        # Board border with raised effect
        pygame.draw.rect(self.screen, (100, 144, 255), board_rect, 3, border_radius=10)
        
        # Grid lines
        cell_size = 50
        rows = 8
        cols = 8
        
        for i in range(rows + 1):
            y = board_rect.y + i * cell_size
            pygame.draw.line(self.screen, (68, 68, 68), 
                           (board_rect.x, y), (board_rect.x + cols * cell_size, y), 2)
        
        for i in range(cols + 1):
            x = board_rect.x + i * cell_size
            pygame.draw.line(self.screen, (68, 68, 68), 
                           (x, board_rect.y), (x, board_rect.y + rows * cell_size), 2)
        
        # Sample Pikachu icons (placeholder)
        for row in range(rows):
            for col in range(cols):
                x = board_rect.x + col * cell_size + 5
                y = board_rect.y + row * cell_size + 5
                icon_rect = pygame.Rect(x, y, cell_size - 10, cell_size - 10)
                pygame.draw.rect(self.screen, self.YELLOW, icon_rect, border_radius=5)
                
                # Pikachu emoji placeholder
                icon_text = self.font_small.render("⚡", True, (0, 0, 0))
                icon_text_rect = icon_text.get_rect(center=icon_rect.center)
                self.screen.blit(icon_text, icon_text_rect)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle button clicks
            for i, button in enumerate(self.buttons):
                if button.handle_event(event):
                    self.handle_button_click(i)
        
        return True
    
    def handle_button_click(self, button_index):
        """Handle button click events"""
        button_names = ["New Game", "Start Auto", "Stop", "Continue", "History", "Home"]
        print(f"Clicked: {button_names[button_index]}")
        
        if button_index == 0:  # New Game
            self.cost = 0
            self.time = 0
        elif button_index == 1:  # Start Auto
            print("Starting auto mode...")
        elif button_index == 2:  # Stop
            print("Stopping...")
        elif button_index == 3:  # Continue
            print("Continuing...")
        elif button_index == 4:  # History
            print("Showing history...")
        elif button_index == 5:  # Home
            print("Going home...")
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Draw everything
            self.screen.blit(self.background, (0, 0))
            
            # Draw header
            self.draw_header()
            
            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen)
            
            # Draw game board
            self.draw_game_board()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PygameGameUI()
    game.run()

