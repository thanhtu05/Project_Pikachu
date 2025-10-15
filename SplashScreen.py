import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import pygame
import sys

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None,
                 width=180, height=60, radius=30,
                 bg_color="#4F46E5", hover_color="#3730A3",
                 text_color="white", font=("Arial", 16, "bold")):
        super().__init__(parent,
                         borderwidth=0,
                         relief="flat",
                         highlightthickness=0,
                         bg=parent.cget("bg"))

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.radius = radius
        self.text = text
        self.font = font

        self.is_pressed = False
        self.is_hovered = False

        self.configure(width=width, height=height)
        self.draw_button()

        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def draw_button(self):
        self.delete("all")

        # Simple shadow
        self.create_rounded_rect(
            2, 2, self.width + 2, self.height + 2,
            self.radius, fill="#000000", outline=""
        )

        y_offset = 2 if self.is_pressed else 0
        current_color = self.hover_color if self.is_hovered else self.bg_color

        # Simple button body
        self.create_rounded_rect(
            0, y_offset, self.width, self.height + y_offset,
            self.radius, fill=current_color, outline=""
        )

        # Simple border
        self.create_rounded_rect(
            0, y_offset, self.width, self.height + y_offset,
            self.radius, fill="", outline="#FFFFFF", width=2
        )

        # Simple text
        text_y = (self.height // 2) + y_offset
        text_x = self.width // 2
        
        self.create_text(
            text_x, text_y,
            text=self.text, fill=self.text_color, font=self.font
        )

    def create_rounded_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_press(self, event):
        self.is_pressed = True
        self.draw_button()

    def _on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command:
            self.command()

    def _on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.configure(cursor="hand2")

    def _on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
        self.configure(cursor="")

class PygameSplashScreen:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 900, 600
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pikachu Game")

        # Colors - Màu sắc hài hòa với nền
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 230, 0)
        self.BLUE = (74, 144, 226)      # #4A90E2 - xanh dương nhạt hơn
        self.ORANGE = (255, 200, 120)   # Cam pastel nhẹ nhàng hơn
        self.RED = (233, 78, 119)       # #E94E77 - đỏ hồng
        self.DARK_GRAY = (30, 30, 30)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Hover colors - Màu hover sáng hơn 10%
        self.BLUE_HOVER = (94, 164, 246)
        self.ORANGE_HOVER = (255, 220, 140)  # Cam pastel sáng hơn
        self.RED_HOVER = (253, 98, 139)

        # Font - Sử dụng font game style
        try:
            # Thử load font Pokemon style
            self.title_font = pygame.font.Font("fonts/FredokaOne-Regular.ttf", 72)
            self.text_font = pygame.font.Font("fonts/Poppins-SemiBold.ttf", 36)
        except:
            # Fallback fonts
            self.title_font = pygame.font.SysFont("Arial", 72, bold=True)
            self.text_font = pygame.font.SysFont("Arial", 36, bold=True)
        
        self.tip_font = pygame.font.SysFont("Arial", 18)  # Font nhỏ hơn

        # Background Image
        try:
            self.background = pygame.image.load("background/background.jpg")
            self.background = pygame.transform.scale(self.background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        except FileNotFoundError:
            # Fallback background if image not found
            self.background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.background.fill((50, 50, 100))  # Dark blue background

        # Create buttons với màu sắc tinh tế
        self.buttons = [
            Button("EASY", 200, 300, 150, 70, self.BLUE, self.BLUE_HOVER, self.start_easy),
            Button("MEDIUM", 375, 300, 150, 70, self.ORANGE, self.ORANGE_HOVER, self.start_medium),
            Button("HARD", 550, 300, 150, 70, self.RED, self.RED_HOVER, self.start_hard)
        ]

        self.clock = pygame.time.Clock()
        self.running = True
        
        # Thêm import cho hiệu ứng
        import math
        import time
        self.math = math
        self.time = time

    def start_easy(self):
        print("Starting EASY mode (8x8 Grid)")
        self.running = False
        self.start_game(8, 8)

    def start_medium(self):
        print("Starting MEDIUM mode (8x12 Grid)")
        self.running = False
        self.start_game(8, 12)

    def start_hard(self):
        print("Starting HARD mode (10x12 Grid)")
        self.running = False
        self.start_game(10, 12)

    def start_game(self, rows, cols):
        pygame.quit()
        
        # Start Tkinter game
        import tkinter as tk
        from Game import PikachuGame

        game_root = tk.Tk()
        game = PikachuGame(game_root, rows, cols)
        try:
            game_root.mainloop()
        except KeyboardInterrupt:
            try:
                game_root.destroy()
            except Exception:
                pass

    def run(self):
        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons:
                            button.click(mouse_pos)

            # Update
            for button in self.buttons:
                button.update(mouse_pos)

            # Draw
            try:
                self.screen.blit(self.background, (0, 0))
            except pygame.error:
                # Screen was closed, exit gracefully
                self.running = False
                break
            
            # Thêm gradient overlay để chữ dễ đọc hơn
            self.draw_gradient_overlay()

            # Title với hiệu ứng NEON GLOW
            self.draw_neon_title()

            # Subtitle với viền trắng mỏng
            subtitle_text = self.tip_font.render("Choose your difficulty level and start matching!", True, self.WHITE)
            subtitle_rect = subtitle_text.get_rect(center=(self.SCREEN_WIDTH // 2, 190))
            
            # Viền trắng mỏng cho subtitle
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    outline_text = self.tip_font.render("Choose your difficulty level and start matching!", True, (255, 255, 255))
                    outline_rect = subtitle_rect.move(dx, dy)
                    self.screen.blit(outline_text, outline_rect)
            
            # Shadow nhẹ cho subtitle
            subtitle_shadow = self.tip_font.render("Choose your difficulty level and start matching!", True, (0, 0, 0, 120))
            subtitle_shadow_rect = subtitle_text.get_rect(center=(self.SCREEN_WIDTH // 2 + 2, 192))
            self.screen.blit(subtitle_shadow, subtitle_shadow_rect)
            self.screen.blit(subtitle_text, subtitle_rect)

            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen)

            # Tip không có nền, chỉ có text shadow để nổi bật
            tip_text = self.tip_font.render("💡 Tip: Match identical Pikachu pairs by connecting them with a clear path!", True, (255, 255, 255))  # Trắng sáng
            tip_rect = tip_text.get_rect(center=(self.SCREEN_WIDTH // 2, 550))
            
            # Text shadow đậm hơn để nổi bật trên nền
            tip_shadow = self.tip_font.render("💡 Tip: Match identical Pikachu pairs by connecting them with a clear path!", True, (0, 0, 0))
            shadow_rect = tip_rect.move(2, 2)
            self.screen.blit(tip_shadow, shadow_rect)
            
            # Text chính
            self.screen.blit(tip_text, tip_rect)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
    
    def draw_gradient_overlay(self):
        """Vẽ gradient overlay nhẹ nhàng để chữ dễ đọc hơn"""
        # Tạo gradient nhẹ từ trong suốt đến đen nhạt
        overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for y in range(self.SCREEN_HEIGHT):
            # Gradient nhẹ hơn - chỉ 40% opacity max
            alpha = int(40 * (y / self.SCREEN_HEIGHT))
            alpha = min(40, alpha)
            color = (0, 0, 0, alpha)
            pygame.draw.line(overlay, color, (0, y), (self.SCREEN_WIDTH, y))
        
        self.screen.blit(overlay, (0, 0))
    
    def draw_neon_title(self):
        """Vẽ title mượt mà và chuyên nghiệp"""
        # Font đẹp hơn
        try:
            title_font = pygame.font.Font("fonts/FredokaOne-Regular.ttf", 72)
        except:
            title_font = pygame.font.SysFont("Arial", 72, bold=True)
        
        text = "PIKACHU GAME"
        title_rect = title_font.render(text, True, (255, 255, 0)).get_rect(center=(self.SCREEN_WIDTH // 2, 120))
        
        # 1. Drop shadow nhẹ màu vàng
        yellow_shadow = title_font.render(text, True, (255, 255, 150))
        self.screen.blit(yellow_shadow, (title_rect.x + 2, title_rect.y + 2))
        
        # 2. Stroke đen mỏng hơn (1.5px)
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                stroke_text = title_font.render(text, True, (0, 0, 0))
                stroke_rect = title_rect.move(dx, dy)
                self.screen.blit(stroke_text, stroke_rect)
        
        # 3. Text chính
        main_text = title_font.render(text, True, (255, 255, 0))
        self.screen.blit(main_text, title_rect)
        
        # 4. Thêm sparkle effects
        self.draw_sparkle_effects(title_rect)
    
    def draw_sparkle_effects(self, title_rect):
        """Vẽ hiệu ứng sparkle quanh title"""
        import random
        import time
        
        # Tạo một vài sparkle ngẫu nhiên
        for _ in range(5):
            # Vị trí ngẫu nhiên quanh title
            angle = random.uniform(0, 2 * 3.14159)
            distance = random.uniform(40, 80)
            
            x = title_rect.centerx + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            y = title_rect.centery + int(distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            
            # Sparkle nhấp nháy
            import math
            sparkle_alpha = int(100 + 155 * abs(math.sin(time.time() * 3 + x + y)))
            sparkle_color = (255, 255, 255, sparkle_alpha)
            
            # Vẽ sparkle nhỏ
            sparkle_font = pygame.font.SysFont("Arial", 16, bold=True)
            sparkle_text = sparkle_font.render("✨", True, sparkle_color[:3])
            sparkle_rect = sparkle_text.get_rect(center=(x, y))
            self.screen.blit(sparkle_text, sparkle_rect)

class Button:
    def __init__(self, text, x, y, width, height, base_color, hover_color, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = hover_color
        self.current_color = base_color
        self.action = action
        self.is_hovered = False
        self.is_clicked = False

    def draw(self, surface):
        # Button với hiệu ứng 3D chuyên nghiệp
        draw_rect = self.rect
        if self.is_hovered:
            # Nảy lên khi hover
            draw_rect = self.rect.inflate(6, 6)
        
        # 1. Bóng đổ mềm mại xuống dưới (3D effect)
        shadow_rect = draw_rect.move(0, 2)
        pygame.draw.rect(surface, (0, 0, 0, 50), shadow_rect, border_radius=12)
        
        # 2. Button body
        pygame.draw.rect(surface, self.current_color, draw_rect, border_radius=12)
        
        # 3. Viền sáng ở trên (ánh sáng chiếu vào)
        highlight_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, draw_rect.height // 3)
        highlight_color = tuple(min(255, c + 30) for c in self.current_color)
        pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=12)
        
        # 4. Viền trắng mỏng
        pygame.draw.rect(surface, (255, 255, 255), draw_rect, width=1, border_radius=12)
        
        # 5. Text với font đẹp hơn
        try:
            text_font = pygame.font.Font("fonts/Poppins-Bold.ttf", 20)
        except:
            text_font = pygame.font.SysFont("Arial", 20, bold=True)
        
        text_surface = text_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=draw_rect.center)
        
        # Text shadow nhẹ
        text_shadow = text_font.render(self.text, True, (0, 0, 0, 100))
        shadow_text_rect = text_rect.move(1, 1)
        surface.blit(text_shadow, shadow_text_rect)
        
        surface.blit(text_surface, text_rect)
    

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.is_hovered = True
        else:
            self.current_color = self.base_color
            self.is_hovered = False

    def click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.is_clicked = True
            # Hiệu ứng click đơn giản - tối màu nhẹ
            self.current_color = tuple(max(0, c - 20) for c in self.current_color)
            
            if self.action:
                self.action()

class ModernSplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Pikachu Game - Pham Thi Van Anh - Hoang Thanh Tu")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.center_window()

        # Use Canvas as the main background
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="#E5E7EB", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background image with error handling
        try:
            self.bg_image = Image.open("background/background.jpg").resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(400, 300, image=self.bg_photo)  # Center the background image
        except FileNotFoundError as e:
            print(f"Error loading background image: {e}")

        # Chỉ tạo một panel chính duy nhất với Dark Glassmorphism
        self.main_panel = self.create_dark_glassmorphism_frame(100, 150, 600, 350, radius=25, alpha=120)
        self.footer_frame = self.create_dark_glassmorphism_frame(150, 520, 530, 50, radius=15, alpha=100)
        
        # Track selected button
        self.selected_button = None

        self.create_title_section()
        self.create_level_selection()
        self.create_footer()

    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")

    def create_transparent_frame(self, x, y, width, height, radius=25, alpha=120):
        # Tạo ảnh RGBA trong suốt với hiệu ứng glassmorphism
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Tạo gradient background cho glassmorphism
        for i in range(height):
            # Tạo gradient từ trong suốt đến trắng mờ
            gradient_alpha = int(alpha * (1 - i / height * 0.3))
            gradient_alpha = max(0, min(255, gradient_alpha))
            
            # Màu glassmorphism: trắng với độ trong suốt
            color = (255, 255, 255, gradient_alpha)
            draw.rectangle([(0, i), (width, i + 1)], fill=color)

        # Vẽ khung bo góc với viền trắng mỏng
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=(255, 255, 255, alpha)
        )
        
        # Thêm viền trắng mỏng cho hiệu ứng kính
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            outline=(255, 255, 255, 200),
            width=2
        )

        frame_img = ImageTk.PhotoImage(img)

        if not hasattr(self, "_frame_cache"):
            self._frame_cache = []
        self._frame_cache.append(frame_img)

        # Đặt ảnh vào canvas
        self.canvas.create_image(x, y, anchor="nw", image=frame_img)
    
    def create_dark_glassmorphism_frame(self, x, y, width, height, radius=25, alpha=120):
        """Tạo frame Dark Glassmorphism phù hợp với background tối"""
        # Tạo ảnh RGBA với màu tối
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Tạo gradient tối từ xanh than đến tím đậm
        for i in range(height):
            # Gradient từ xanh than đậm đến tím đậm
            ratio = i / height
            r = int(26 + (30 - 26) * ratio)  # 26 -> 30
            g = int(32 + (48 - 32) * ratio)  # 32 -> 48  
            b = int(53 + (80 - 53) * ratio)  # 53 -> 80
            
            # Áp dụng alpha
            gradient_alpha = int(alpha * (0.8 + 0.2 * ratio))
            gradient_alpha = max(0, min(255, gradient_alpha))
            
            color = (r, g, b, gradient_alpha)
            draw.rectangle([(0, i), (width, i + 1)], fill=color)

        # Vẽ khung bo góc với viền trắng mỏng
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            fill=(26, 32, 53, alpha)
        )
        
        # Thêm viền trắng mỏng cho hiệu ứng kính
        draw.rounded_rectangle(
            [(0, 0), (width, height)],
            radius=radius,
            outline=(255, 255, 255, 150),
            width=1
        )

        frame_img = ImageTk.PhotoImage(img)

        if not hasattr(self, "_frame_cache"):
            self._frame_cache = []
        self._frame_cache.append(frame_img)

        # Đặt ảnh vào canvas
        self.canvas.create_image(x, y, anchor="nw", image=frame_img)

    def draw_text_with_outline(self, x, y, text, font,
                               fill="white", outline="black", outline_width=2):
        """Vẽ chữ có viền và shadow đẹp mắt với hiệu ứng 3D"""
        
        # 1. Tạo shadow chính (bóng đổ lớn)
        shadow_offset = 3
        self.canvas.create_text(
            x + shadow_offset, y + shadow_offset,
            text=text, font=font, fill="#333333"
        )
        
        # 2. Tạo shadow phụ (bóng đổ nhỏ hơn)
        shadow_offset2 = 1
        self.canvas.create_text(
            x + shadow_offset2, y + shadow_offset2,
            text=text, font=font, fill="#666666"
        )
        
        # 3. Tạo outline với 4 góc (hiệu ứng outline mượt mà)
        outline_positions = [
            (x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y+1),
            (x-1, y), (x+1, y), (x, y-1), (x, y+1)
        ]
        
        for ox, oy in outline_positions:
            self.canvas.create_text(
                ox, oy, text=text, font=font, fill=outline
            )
        
        # 4. Tạo outline dày hơn cho text lớn
        if outline_width > 2:
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0 and (dx, dy) not in outline_positions:
                        self.canvas.create_text(
                            x + dx, y + dy, text=text, font=font, fill=outline
                        )
        
        # 5. Vẽ chữ chính đè lên (layer cuối cùng)
        self.canvas.create_text(x, y, text=text, font=font, fill=fill)


    def create_title_section(self):
        # Title với hiệu ứng 3D và shadow đẹp mắt, phù hợp với theme đêm
        self.draw_text_with_outline(
            400, 50,
            text="⚡ PIKACHU GAME ⚡",
            font=("Arial", 40, "bold"),  # Font lớn hơn nữa
            fill="#FFD700",  # Màu vàng Pikachu
            outline="#1A1A1A",  # Viền đen đậm cho contrast
            outline_width=5
        )

        self.draw_text_with_outline(
            400, 100,
            text="Choose your difficulty level and start matching!",
            font=("Arial", 20, "italic"),  # Font lớn hơn
            fill="#E8F4FD",  # Màu xanh nhạt phù hợp với đêm
            outline="#2C3E50",
            outline_width=2
        )

    def create_level_selection(self):
        # Bảng màu mới phù hợp với theme đêm tối
        levels = [
            {"name": "EASY", "desc": "8x8 Grid", "color": "#3A5A9D", "hover": "#2A4A8D", "rows": 8, "cols": 8},  # Xanh dương đậm bầu trời đêm
            {"name": "MEDIUM", "desc": "8x12 Grid", "color": "#F2C144", "hover": "#E6B800", "rows": 8, "cols": 12},  # Vàng sao (giữ nguyên)
            {"name": "HARD", "desc": "10x12 Grid", "color": "#D96F4E", "hover": "#C95F3E", "rows": 10, "cols": 12},  # Cam/đỏ hoàng hôn
        ]

        # Layout mới: đặt trực tiếp lên panel chính, không có khung con
        start_x = 200  # Bắt đầu từ vị trí panel chính
        for i, level in enumerate(levels):
            x_pos = start_x + i * 200  # Space buttons 200px apart
            y_pos = 250  # Vertical position trong panel chính

            # Add level name với hiệu ứng 3D đẹp mắt
            self.draw_text_with_outline(
                x_pos, y_pos,
                text=level["name"],
                font=("Arial", 24, "bold"),
                fill="#FFFFFF",
                outline="#1A1A1A",
                outline_width=3
            )
            # Add description với shadow effect
            self.draw_text_with_outline(
                x_pos, y_pos + 40,
                text=level["desc"],
                font=("Arial", 16, "bold"),
                fill="#E8F4FD",
                outline="#2C3E50",
                outline_width=1
            )
            # Add button với kích thước chuẩn và đẹp hơn
            button = ModernButton(
                self.canvas,
                text="PLAY",
                command=lambda r=level["rows"], c=level["cols"]: self.start_game(r, c),
                width=200,  # Kích thước lớn hơn
                height=70,  # Cao hơn
                bg_color=level["color"],
                hover_color=level["hover"],
                font=("Arial", 20, "bold")
            )
            button_window = self.canvas.create_window(
                x_pos, y_pos + 90,  # Position below description
                window=button
            )

    def create_footer(self):
        self.draw_text_with_outline(
            400, 550,
            text="💡 Tip: Match identical Pikachu pairs by connecting them with a clear path!",
            font=("Arial", 14, "bold"),
            fill="#FFFFFF",
            outline="#2C3E50",
            outline_width=2
        )


    def start_game(self, rows, cols):
        # Highlight selected button
        self.selected_button = (rows, cols)
        print(f"Selected difficulty: {rows}x{cols}")
        
        self.root.destroy()  # Close SplashScreen

        import tkinter as tk
        from Game import PikachuGame

        game_root = tk.Tk()
        game = PikachuGame(game_root, rows, cols)
        try:
            game_root.mainloop()
        except KeyboardInterrupt:
            # Allow Ctrl+C to stop the GUI loop cleanly
            try:
                game_root.destroy()
            except Exception:
                pass

    def on_game_close(self, game_root):
        """Xử lý khi cửa sổ game bị đóng, quay về SplashScreen."""
        game_root.destroy()
        self.root.deiconify()  # Hiển thị lại SplashScreen

    def show(self):
        """Hiển thị SplashScreen."""
        self.root.deiconify()

    def close(self):
        """Ẩn SplashScreen."""
        self.root.withdraw()

if __name__ == "__main__":
    # Use pygame splash screen
    app = PygameSplashScreen()
    app.run()