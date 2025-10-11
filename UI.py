import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math
import pygame


class PygameButton:
    """Pygame button with raised 3D effect for Tkinter integration"""
    
    def __init__(self, parent, text, command=None, button_type="primary", **kwargs):
        self.parent = parent
        self.text = self._clean_text(text)  # Clean Unicode characters
        self.command = command
        self.button_type = button_type
        self.kwargs = kwargs
        
        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()
        
        # Modern button colors with clear hierarchy and 3D-friendly tones
        self.colors = {
            "primary": {"bg": "#2196F3", "fg": "#FFFFFF"},       # Blue - Primary actions (New Game, Continue)
            "success": {"bg": "#4CAF50", "fg": "#FFFFFF"},       # Green - Start actions
            "danger": {"bg": "#F44336", "fg": "#FFFFFF"},        # Red - Stop/Danger actions
            "info": {"bg": "#9C27B0", "fg": "#FFFFFF"},          # Purple - Info actions (History)
            "warning": {"bg": "#FF9800", "fg": "#FFFFFF"},       # Orange - Warning actions
            "secondary": {"bg": "#607D8B", "fg": "#FFFFFF"}      # Blue Gray - Secondary actions (Home)
        }
        
        self.color_scheme = self.colors.get(button_type, self.colors["primary"])
        self.is_hovered = False
        self.is_pressed = False
        
        # Create pygame surface for button
        self.width = kwargs.get('width', 14) * 8 + 4
        self.height = kwargs.get('height', 2) * 20 + 4
        self.pygame_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create the button
        self.create_button()
    
    def _clean_text(self, text):
        """Clean text to handle Unicode characters properly"""
        try:
            # Try to keep Unicode characters if possible
            return text
        except:
            # Fallback: remove non-ASCII characters
            return text.encode("ascii", "ignore").decode()
    
    def create_button(self):
        """Create the pygame button with 3D effect"""
        # Get default button style
        button_style = {
            "width": 14,
            "height": 2,
            "font": ("Comic Sans MS", 11, "bold"),
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2"
        }
        
        # Update with custom kwargs
        button_style.update(self.kwargs)
        
        # Create a tkinter button as placeholder with proper configuration
        self.button = tk.Button(
            self.parent,
            text="",  # Empty text, we'll use image instead
            command=self.command,
            relief="flat",
            bd=0,
            cursor="hand2",
            highlightthickness=0,
            activebackground=self.color_scheme["bg"],
            bg=self.color_scheme["bg"]
        )
        
        # Bind events
        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)
        self.button.bind("<Button-1>", self.on_press)
        self.button.bind("<ButtonRelease-1>", self.on_release)
        
        # Update pygame button and convert to PhotoImage
        self.update_pygame_button()
        self.update_button_image()
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def update_pygame_button(self):
        """Update pygame button with enhanced visual effects"""
        import math
        
        # Clear surface
        self.pygame_surface.fill((0, 0, 0, 0))
        
        # Get button dimensions from instance variables
        w, h = self.width, self.height
        rect = pygame.Rect(0, 0, w, h)
        
        # Convert hex to RGB
        base_color = self.hex_to_rgb(self.color_scheme["bg"])
        
        # All text white for better visibility
        text_color = (255, 255, 255)  # Always white text
        
        # Calculate bright and dark colors for 3D effect
        bright_color = tuple(min(255, c + 40) for c in base_color)
        dark_color = tuple(max(0, c - 40) for c in base_color)
        
        # Hover effect - scale up slightly
        if self.is_hovered:
            scale_factor = 1.03
            w_scaled = int(w * scale_factor)
            h_scaled = int(h * scale_factor)
            rect_scaled = pygame.Rect(0, 0, w_scaled, h_scaled)
            # Center the scaled rect
            rect_scaled.center = (w//2, h//2)
        else:
            rect_scaled = rect
        
        if self.is_pressed:
            # When pressed, reverse the light/dark effect and move down
            top_color = dark_color
            bottom_color = bright_color
            rect_scaled = rect_scaled.move(2, 2)  # Move down more when pressed
            # Click feedback - darken the button significantly
            base_color = tuple(max(0, c - 50) for c in base_color)
            # Reduce shadow when pressed
            shadow_rect = rect_scaled.move(2, 2)  # Closer shadow
        else:
            # Normal raised effect
            top_color = bright_color
            bottom_color = dark_color
        
        # 1. Draw shadow (behind everything) - deeper shadow for 3D effect
        shadow_rect = rect_scaled.move(4, 4)
        pygame.draw.rect(self.pygame_surface, (0, 0, 0, 60), shadow_rect, border_radius=12)
        
        # 2. Draw main button background with smooth gradient
        self.draw_smooth_gradient_rect(self.pygame_surface, rect_scaled, base_color, bright_color)
        
        # 3. Draw raised 3D effect with rounded corners
        border_radius = 12
        border_thickness = 3
        
        # Create raised effect with multiple border layers
        # Outer dark border (bottom-right shadow)
        pygame.draw.rect(self.pygame_surface, dark_color, rect_scaled, border_thickness, border_radius=border_radius)
        
        # Inner bright border (top-left highlight)
        inner_rect = rect_scaled.inflate(-2, -2)
        pygame.draw.rect(self.pygame_surface, top_color, inner_rect, 2, border_radius=border_radius-1)
        
        # 4. Add subtle inner highlight for extra depth
        highlight_rect = pygame.Rect(rect_scaled.left + 2, rect_scaled.top + 2, 
                                   rect_scaled.width - 4, rect_scaled.height // 3)
        highlight_color = tuple(min(255, c + 60) for c in base_color)
        pygame.draw.rect(self.pygame_surface, highlight_color, highlight_rect, border_radius=border_radius-2)
        
        # 5. Enhanced hover glow effect - raised button style
        if self.is_hovered:
            # Multiple glow layers for depth
            glow_rect1 = rect.inflate(8, 8)
            glow_rect2 = rect.inflate(12, 12)
            glow_rect3 = rect.inflate(16, 16)
            
            # Outer glow (softest)
            pygame.draw.rect(self.pygame_surface, (255, 255, 255, 20), glow_rect3, border_radius=16)
            # Middle glow
            pygame.draw.rect(self.pygame_surface, (255, 255, 255, 40), glow_rect2, border_radius=14)
            # Inner glow (brightest)
            pygame.draw.rect(self.pygame_surface, (255, 255, 255, 60), glow_rect1, border_radius=12)
        
        # 6. Draw text with enhanced positioning and contrast
        try:
            # Try Unicode-supporting fonts first
            font = pygame.font.SysFont("Segoe UI Symbol", 16, bold=True)
        except:
            try:
                font = pygame.font.SysFont("Arial Unicode MS", 16, bold=True)
            except:
                try:
                    font = pygame.font.SysFont("Poppins", 16, bold=True)
                except:
                    try:
                        font = pygame.font.SysFont("Arial", 16, bold=True)
                    except:
                        font = pygame.font.Font(None, 16)
        
        # Text shadow for better readability - always dark shadow for white text
        shadow_color = (0, 0, 0)  # Dark shadow for white text
        
        text_shadow = font.render(self.text, True, shadow_color)
        shadow_rect = text_shadow.get_rect(center=(w//2 + 1, h//2 + 1))
        self.pygame_surface.blit(text_shadow, shadow_rect)
        
        # Main text - positioned slightly higher for better balance
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=(w//2, h//2 - 2))
        self.pygame_surface.blit(text_surface, text_rect)
    
    def update_button_image(self):
        """Convert pygame surface to PhotoImage and update button"""
        try:
            # Convert pygame surface to string
            pygame_string = pygame.image.tostring(self.pygame_surface, "RGBA")
            
            # Create PIL Image from string
            from PIL import Image
            pil_image = Image.frombytes("RGBA", (self.width, self.height), pygame_string)
            
            # Convert PIL Image to PhotoImage
            from PIL import ImageTk
            self.photo_image = ImageTk.PhotoImage(pil_image)
            
            # Update button with image - ensure proper configuration
            self.button.config(
                image=self.photo_image, 
                compound="center",
                text="",  # Clear text since we're using image
                relief="flat",
                bd=0,
                highlightthickness=0,
                activebackground=self.color_scheme["bg"],
                cursor="hand2"
            )
            
        except Exception as e:
            print(f"Error updating button image: {e}")
            # Fallback to text button with proper styling
            self.button.config(
                text=self.text, 
                image="",
                bg=self.color_scheme["bg"],
                fg=self.color_scheme["fg"],
                relief="raised",
                bd=2,
                cursor="hand2"
            )
    
    def _get_button_glow_color(self, base_color):
        """Get appropriate glow color for buttons"""
        # Convert RGB to hex for lookup
        hex_color = f"#{base_color[0]:02x}{base_color[1]:02x}{base_color[2]:02x}"
        glow_colors = {
            "#FFD600": (255, 229, 92),   # Yellow glow
            "#4CAF50": (129, 199, 132),  # Green glow
            "#E53935": (255, 138, 101),  # Red glow
            "#42A5F5": (144, 202, 249),  # Blue glow
            "#FF8C00": (255, 183, 77),   # Orange glow
            "#757575": (189, 189, 189)   # Gray glow
        }
        return glow_colors.get(hex_color, (255, 255, 255))
    
    def draw_gradient_rect(self, surface, rect, color1, color2):
        """Draw a gradient rectangle"""
        for i in range(rect.height):
            color = [
                int(color1[j] + (color2[j] - color1[j]) * (i / rect.height))
                for j in range(3)
            ]
            pygame.draw.line(surface, color, 
                           (rect.x, rect.y + i), 
                           (rect.x + rect.width, rect.y + i))
    
    def draw_smooth_gradient_rect(self, surface, rect, color1, color2):
        """Draw a smooth gradient rectangle with enhanced 3D depth"""
        for y in range(rect.height):
            ratio = y / rect.height
            # Create more pronounced gradient for 3D effect
            # Top: very bright, Bottom: darker
            brightness_factor = 0.7 + 0.3 * ratio  # From 0.7 to 1.0
            color = tuple(int(color1[i] * brightness_factor) for i in range(3))
            pygame.draw.line(surface, color, 
                           (rect.x, rect.y + y), 
                           (rect.x + rect.width, rect.y + y))
    
    def draw_pygame_button(self, surface, rect):
        """Draw raised button effect using pygame"""
        # This method is kept for compatibility but not used in Tkinter integration
        pass
    
    def on_enter(self, event):
        """Handle mouse enter event"""
        self.is_hovered = True
        self.update_pygame_button()
        self.update_button_image()
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.is_hovered = False
        self.update_pygame_button()
        self.update_button_image()
    
    def on_press(self, event):
        """Handle button press event"""
        self.is_pressed = True
        self.update_pygame_button()
        self.update_button_image()
    
    def on_release(self, event):
        """Handle button release event"""
        self.is_pressed = False
        self.update_pygame_button()
        self.update_button_image()
    
    def config(self, **kwargs):
        """Configure button properties"""
        self.button.config(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the button"""
        return self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the button"""
        return self.button.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place the button"""
        return self.button.place(**kwargs)


class PokemonButton_OLD:
    """Custom Pokemon-themed button with 3D effects, gradient borders and animations"""
    
    def __init__(self, parent, text, command=None, button_type="primary", **kwargs):
        self.parent = parent
        self.text = text
        self.command = command
        self.button_type = button_type
        self.kwargs = kwargs
        
        # Enhanced Pokemon color schemes with neumorphism effects
        self.colors = {
            "primary": {
                "bg": "#FFD93D",  # Pikachu yellow soft
                "fg": "#3E3E3E",  # Dark text
                "hover_bg": "#FFE66D",  # Light yellow hover
                "active_bg": "#FFC107",  # Darker yellow press
                "glow": "#FFF59D",  # Light yellow glow
                "shadow": "#E6B800",  # Soft yellow shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#B8860B",  # Dark bottom border
                "gradient_start": "#FFD93D",  # Gradient start
                "gradient_end": "#FFE66D",  # Gradient end
                "text_shadow": "#000000",  # Text shadow
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#B8860B"  # Dark shadow
            },
            "success": {
                "bg": "#6ECB63",  # Mint green
                "fg": "#2B2B2B",  # Dark text
                "hover_bg": "#8FDF82",  # Light mint hover
                "active_bg": "#4CAF50",  # Darker green press
                "glow": "#C8E6C9",  # Light green glow
                "shadow": "#4CAF50",  # Soft green shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#2E7D32",  # Dark bottom border
                "gradient_start": "#6ECB63",  # Gradient start
                "gradient_end": "#8FDF82",  # Gradient end
                "text_shadow": "#000000",
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#2E7D32"  # Dark shadow
            },
            "danger": {
                "bg": "#FF6B6B",  # Soft red
                "fg": "#FFFFFF",  # White text
                "hover_bg": "#FF8C8C",  # Light red hover
                "active_bg": "#E53E3E",  # Darker red press
                "glow": "#FED7D7",  # Light red glow
                "shadow": "#E53E3E",  # Soft red shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#C53030",  # Dark bottom border
                "gradient_start": "#FF6B6B",  # Gradient start
                "gradient_end": "#FF8C8C",  # Gradient end
                "text_shadow": "#000000",
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#C53030"  # Dark shadow
            },
            "info": {
                "bg": "#9ADCFF",  # Soft blue
                "fg": "#2B2B2B",  # Dark text
                "hover_bg": "#BDE0FE",  # Light blue hover
                "active_bg": "#64B5F6",  # Darker blue press
                "glow": "#E3F2FD",  # Light blue glow
                "shadow": "#64B5F6",  # Soft blue shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#1976D2",  # Dark bottom border
                "gradient_start": "#9ADCFF",  # Gradient start
                "gradient_end": "#BDE0FE",  # Gradient end
                "text_shadow": "#000000",
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#1976D2"  # Dark shadow
            },
            "warning": {
                "bg": "#FFB562",  # Soft orange
                "fg": "#3E3E3E",  # Dark text
                "hover_bg": "#FFD166",  # Light orange hover
                "active_bg": "#FF9800",  # Darker orange press
                "glow": "#FFF3E0",  # Light orange glow
                "shadow": "#FF9800",  # Soft orange shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#F57C00",  # Dark bottom border
                "gradient_start": "#FFB562",  # Gradient start
                "gradient_end": "#FFD166",  # Gradient end
                "text_shadow": "#000000",
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#F57C00"  # Dark shadow
            },
            "secondary": {
                "bg": "#F9F9F9",  # Very light gray
                "fg": "#2B2B2B",  # Dark text
                "hover_bg": "#FFFFFF",  # White hover
                "active_bg": "#E0E0E0",  # Darker gray press
                "glow": "#FAFAFA",  # Very light gray glow
                "shadow": "#E0E0E0",  # Soft gray shadow
                "border_light": "#FFFFFF",  # Bright top border
                "border_dark": "#757575",  # Dark bottom border
                "gradient_start": "#F9F9F9",  # Gradient start
                "gradient_end": "#FFFFFF",  # Gradient end
                "text_shadow": "#000000",
                "neumorphism_light": "#FFFFFF",  # Bright highlight
                "neumorphism_dark": "#757575"  # Dark shadow
            }
        }
        
        self.color_scheme = self.colors.get(button_type, self.colors["primary"])
        self.is_hovered = False
        self.is_pressed = False
        
        # Create the button
        self.create_button()
    
    def _clean_text(self, text):
        """Clean text to handle Unicode characters properly"""
        try:
            # Try to keep Unicode characters if possible
            return text
        except:
            # Fallback: remove non-ASCII characters
            return text.encode("ascii", "ignore").decode()
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_button(self):
        """Create the Pokemon-style button with 3D effects"""
        # Get default button style with rounded font
        button_style = {
            "width": 14,
            "height": 2,
            "font": ("Comic Sans MS", 11, "bold"),
            "relief": "raised",
            "bd": 3,
            "cursor": "hand2",
            "activeforeground": self.color_scheme["fg"]
        }
        
        # Update with custom kwargs
        button_style.update(self.kwargs)
        
        # Create the button
        self.button = tk.Button(
            self.parent,
            text=self.text,
            command=self.command,
            bg=self.color_scheme["bg"],
            fg=self.color_scheme["fg"],
            activebackground=self.color_scheme["active_bg"],
            highlightbackground=self.color_scheme["border_light"],
            highlightcolor=self.color_scheme["border_light"],
            highlightthickness=2,
            **button_style
        )
        
        # Bind events for hover and press effects
        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)
        self.button.bind("<Button-1>", self.on_press)
        self.button.bind("<ButtonRelease-1>", self.on_release)
        
        # Create 3D effect elements
        self.glow_id = None
        self.shadow_id = None
        self.border_light_id = None
        self.border_dark_id = None
        self.gradient_ids = []  # List of gradient rectangle IDs
        self.text_shadow_id = None
    
    def on_enter(self, event):
        """Handle mouse enter event"""
        self.is_hovered = True
        self.update_pygame_button()
    
    def on_leave(self, event):
        """Handle mouse leave event"""
        self.is_hovered = False
        self.update_pygame_button()
    
    def on_press(self, event):
        """Handle button press event"""
        self.is_pressed = True
        self.update_pygame_button()
    
    def on_release(self, event):
        """Handle button release event"""
        self.is_pressed = False
        self.update_pygame_button()
    
    def create_3d_effect(self):
        """Create raised button effect with bright top border and dark bottom border"""
        try:
            # Get button position and size
            x = self.button.winfo_x()
            y = self.button.winfo_y()
            width = self.button.winfo_width()
            height = self.button.winfo_height()
            
            # Create outer shadow for depth (behind everything)
            self.shadow_id = self.parent.create_rectangle(
                x + 3, y + 3, x + width + 3, y + height + 3,
                fill="#000000",
                outline="",
                width=0
            )
            
            # Create main button background with gradient
            gradient_steps = 8
            for i in range(gradient_steps):
                ratio = i / (gradient_steps - 1)
                # Interpolate between start and end colors for smooth gradient
                start_color = self.hex_to_rgb(self.color_scheme["gradient_start"])
                end_color = self.hex_to_rgb(self.color_scheme["gradient_end"])
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                
                color = f"#{r:02x}{g:02x}{b:02x}"
                
                gradient_rect = self.parent.create_rectangle(
                    x, y + int(height * i / gradient_steps),
                    x + width, y + int(height * (i + 1) / gradient_steps),
                    fill=color,
                    outline="",
                    width=0
                )
                self.gradient_ids.append(gradient_rect)
                self.parent.tag_lower(gradient_rect)
            
            # Create bright top border (raised effect) - thicker
            self.border_light_id = self.parent.create_rectangle(
                x, y, x + width, y + 3,
                fill=self.color_scheme["neumorphism_light"],
                outline="",
                width=0
            )
            self.parent.create_rectangle(
                x, y, x + 3, y + height,
                fill=self.color_scheme["neumorphism_light"],
                outline="",
                width=0
            )
            
            # Create dark bottom border (raised effect) - thicker
            self.border_dark_id = self.parent.create_rectangle(
                x, y + height - 3, x + width, y + height,
                fill=self.color_scheme["neumorphism_dark"],
                outline="",
                width=0
            )
            self.parent.create_rectangle(
                x + width - 3, y, x + width, y + height,
                fill=self.color_scheme["neumorphism_dark"],
                outline="",
                width=0
            )
            
            # Create text shadow for depth
            self.text_shadow_id = self.parent.create_text(
                x + width // 2 + 2, y + height // 2 + 2,
                text=self.text,
                fill=self.color_scheme["text_shadow"],
                font=("Comic Sans MS", 11, "bold"),
                anchor="center"
            )
            
            # Lower all effects below button
            for effect_id in [self.shadow_id] + self.gradient_ids + [self.border_light_id, self.border_dark_id, self.text_shadow_id]:
                if effect_id:
                    self.parent.tag_lower(effect_id)
            
        except Exception:
            pass
    
    def remove_3d_effect(self):
        """Remove the 3D effect"""
        try:
            # Remove gradient rectangles
            for gradient_id in self.gradient_ids:
                if gradient_id:
                    self.parent.delete(gradient_id)
            self.gradient_ids = []
            
            # Remove other effects
            effect_ids = [self.glow_id, self.shadow_id, self.border_light_id, 
                         self.border_dark_id, self.text_shadow_id]
            for effect_id in effect_ids:
                if effect_id:
                    self.parent.delete(effect_id)
            
            # Reset all IDs
            self.glow_id = None
            self.shadow_id = None
            self.border_light_id = None
            self.border_dark_id = None
            self.text_shadow_id = None
        except Exception:
            pass
    
    def create_press_effect(self):
        """Create pressed effect (inverted 3D)"""
        try:
            # Get button position and size
            x = self.button.winfo_x()
            y = self.button.winfo_y()
            width = self.button.winfo_width()
            height = self.button.winfo_height()
            
            # Create pressed shadow (top-left)
            self.shadow_id = self.parent.create_rectangle(
                x - 2, y - 2, x + width - 2, y + height - 2,
                fill=self.color_scheme["shadow"],
                outline="",
                width=0
            )
            
            # Create pressed glow
            self.glow_id = self.parent.create_rectangle(
                x - 1, y - 1, x + width + 1, y + height + 1,
                fill=self.color_scheme["glow"],
                outline="",
                width=0
            )
            
            # Lower effects below button
            for effect_id in [self.shadow_id, self.glow_id]:
                if effect_id:
                    self.parent.tag_lower(effect_id)
            
        except Exception:
            pass
    
    def config(self, **kwargs):
        """Configure button properties"""
        self.button.config(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the button"""
        return self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the button"""
        return self.button.grid(**kwargs)
    
    def place(self, **kwargs):
        """Place the button"""
        return self.button.place(**kwargs)


class GameUI:
    def __init__(self, root, rows, cols, cell_size, game=None):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.game = game

        # Load background image (best-effort)
        try:
            self.bg_image = Image.open("background/backgroundmain.jpg")
            self.bg_image = self.bg_image.resize((1000, 1000))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except Exception:
            self.bg_photo = None

        # Main canvas
        self.bg_canvas = tk.Canvas(self.root, width=1000, height=700, highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)
        if self.bg_photo:
            self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            
        # Add subtle dark overlay to improve text readability
        self.overlay = self.bg_canvas.create_rectangle(0, 0, 1000, 700, fill="#000000", outline="", stipple="gray25")
        self.bg_canvas.tag_lower(self.overlay)

        # --- Overlay (for pause and background reveal) ---
        self.background_overlay = None
        self.overlay_rect = None
        
        # Initialize background overlay for fade effect
        try:
            board_w, board_h = self.cols * self.cell_size, self.rows * self.cell_size
            self.background_overlay = tk.Canvas(self.bg_canvas, width=board_w, height=board_h, bg="", highlightthickness=0)
            self.overlay_rect = self.background_overlay.create_rectangle(0, 0, board_w, board_h, fill="#0B0C10", outline="")
            # Position overlay over the game board
            self.overlay_window = self.bg_canvas.create_window(500, 160, window=self.background_overlay, anchor="n")
        except Exception:
            pass

        # Style
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        # Dark arcade theme inspired styling
        style.configure("TLabel", font=("Arial", 12, "bold"), background="#0B0C10", foreground="#66FCF1")
        
        # Rounded dropdown styling like the second image
        style.configure("TCombobox", 
                       font=("Arial", 10, "bold"), 
                       fieldbackground="#2D3748", 
                       background="#2D3748", 
                       foreground="#FFFFFF",
                       borderwidth=0,
                       relief="flat")
        style.map("TCombobox", 
                 fieldbackground=[("readonly", "#2D3748")],
                 background=[("readonly", "#2D3748")])
        
        # Create custom rounded combobox
        style.configure("Rounded.TCombobox",
                       fieldbackground="#2D3748",
                       background="#2D3748", 
                       foreground="#FFFFFF",
                       borderwidth=0,
                       relief="flat")
        
        style.configure("TCheckbutton", font=("Arial", 10), background="#0B0C10", foreground="#C5C6C7")

        # Modern pill-style header with glassmorphism
        # Create semi-transparent background with rounded corners
        self.topbar = self.bg_canvas.create_rectangle(10, 10, 990, 50, fill="#1A1A2E", outline="", stipple="gray12")
        
        # Add glassmorphism effect with rounded corners
        self._create_glassmorphism_header()
        
        # Title with modern pill design
        self._create_title_pill()

        # Create pill-style info boxes
        self._create_info_pills()
        
        # Add sound toggle functionality
        self.sound_var = tk.BooleanVar(value=True)
        self.toggle_sound()
        
        # Add mode and algorithm variables
        self.mode_var = tk.StringVar(value="Manual")
        self.algo_var = tk.StringVar(value="DFS")
        
        # Create dropdown menus for mode and algorithm
        self._create_dropdown_menus()

        # React to dropdown changes - stop auto when algorithm or mode changes
        def _on_mode_change(*_):
            mode_value = self.mode_var.get()
            # show Skip only in Auto
            try:
                if mode_value.lower() == "auto":
                    self.bg_canvas.itemconfigure(self.skip_btn_window, state="normal")
                else:
                    self.bg_canvas.itemconfigure(self.skip_btn_window, state="hidden")
            except Exception:
                pass
            
            # Stop auto if running when mode changes
            if hasattr(self, 'game') and self.game and hasattr(self.game, 'auto_running') and self.game.auto_running:
                self.game.stop_game()
                print(f"[DEBUG] Auto stopped due to mode change to: {mode_value}")
            
            # notify game
            if hasattr(self, 'game') and self.game:
                if hasattr(self.game, 'on_mode_change') and callable(getattr(self.game, 'on_mode_change')):
                    try:
                        self.game.on_mode_change(mode_value)
                    except Exception:
                        pass

        def _on_algo_change(*_):
            algo_value = self.algo_var.get()
            # Stop auto if running when algorithm changes
            if hasattr(self, 'game') and self.game and hasattr(self.game, 'auto_running') and self.game.auto_running:
                self.game.stop_game()
                print(f"[DEBUG] Auto stopped due to algorithm change to: {algo_value}")
            
            if hasattr(self, 'game') and self.game:
                if hasattr(self.game, 'on_algo_change') and callable(getattr(self.game, 'on_algo_change')):
                    try:
                        self.game.on_algo_change(algo_value)
                    except Exception:
                        pass

        try:
            self.mode_var.trace_add('write', _on_mode_change)
            self.algo_var.trace_add('write', _on_algo_change)
            # Initialize once
            _on_mode_change()
            _on_algo_change()
        except Exception:
            pass

        # Enhanced button configuration with unified Pokemon theme
        button_style = {
            "width": 14,
            "height": 2,
            "font": ("Comic Sans MS", 11, "bold"),
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2"
        }

        # Layout buttons with improved spacing (neumorphism style)
        button_count = 6
        button_width = 14 * 8 + 4
        total_available_width = 1000 - 80
        button_spacing = max(20, (total_available_width - (button_count * button_width)) // (button_count + 1))
        start_x = 40

        # Create unified Pygame-style buttons with raised 3D effect - increased spacing
        self.new_btn = PygameButton(self.bg_canvas, text="⚡ New Game", button_type="primary", **button_style)
        self.new_btn_window = self.bg_canvas.create_window(start_x + 0 * (button_spacing + button_width), 95, window=self.new_btn.button, anchor="nw")

        self.auto_btn = PygameButton(self.bg_canvas, text="🚀 Start Auto", button_type="success", **button_style)
        self.auto_btn_window = self.bg_canvas.create_window(start_x + 1 * (button_spacing + button_width), 95,
                                                             window=self.auto_btn.button, anchor="nw")
        # wire to game's start_auto if provided
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'start_auto'):
            try:
                self.auto_btn.config(command=self.game.start_auto)
            except Exception:
                pass

        self.stop_btn = PygameButton(self.bg_canvas, text="⏹️ Stop", button_type="danger", command=self.pause_game, **button_style)
        self.stop_btn_window = self.bg_canvas.create_window(start_x + 2 * (button_spacing + button_width), 95,
                                                             window=self.stop_btn.button, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'stop_game'):
            try:
                self.stop_btn.config(command=self.game.stop_game)
            except Exception:
                pass

        self.continue_btn = PygameButton(self.bg_canvas, text="▶️ Continue", button_type="warning", command=self.resume_game, **button_style)
        self.continue_btn_window = self.bg_canvas.create_window(start_x + 3 * (button_spacing + button_width), 95,
                                                                 window=self.continue_btn.button, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'resume_game'):
            try:
                self.continue_btn.config(command=self.game.resume_game)
            except Exception:
                pass

        self.history_btn = PygameButton(self.bg_canvas, text="📊 History", button_type="info", **button_style)
        self.history_btn_window = self.bg_canvas.create_window(start_x + 4 * (button_spacing + button_width), 95,
                                                                window=self.history_btn.button, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'show_history'):
            try:
                self.history_btn.config(command=self.game.show_history)
            except Exception:
                pass

        self.home_btn = PygameButton(self.bg_canvas, text="🏠 Home", button_type="secondary", **button_style)
        self.home_btn_window = self.bg_canvas.create_window(start_x + 5 * (button_spacing + button_width), 95,
                                                            window=self.home_btn.button, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'go_home'):
            try:
                self.home_btn.config(command=self.game.go_home)
            except Exception:
                pass

        # Pokemon buttons are now self-contained with their own effects
        # No need for additional arcade text or animation loops

        # --- Game board with enhanced styling ---
        w, h = self.cols * self.cell_size, self.rows * self.cell_size
        self.canvas = tk.Canvas(self.bg_canvas, width=w, height=h, bg="#1A1A2E", borderwidth=0, relief="flat",
                                highlightthickness=3, highlightbackground="#4A90E2")
        self.canvas_window = self.bg_canvas.create_window(500, 180, window=self.canvas, anchor="n")
        
        # Add neon vertical lines around button area (similar to pygame version)
        self._draw_neon_decorations()

        # Raise widgets to top
        for win in [self.new_btn_window, self.auto_btn_window,
                    self.stop_btn_window, self.continue_btn_window, self.history_btn_window,
                    self.home_btn_window, self.canvas_window]:
            try:
                self.bg_canvas.tag_raise(win)
            except Exception:
                pass

        # Enhanced grid with better visibility and softer colors
        for r in range(self.rows + 1):
            # Softer grid lines with glow effect
            self.canvas.create_line(0, r * self.cell_size, w, r * self.cell_size, fill="#444444", width=2)
            self.canvas.create_line(0, r * self.cell_size, w, r * self.cell_size, fill="#666666", width=1)
        for c in range(self.cols + 1):
            # Softer grid lines with glow effect
            self.canvas.create_line(c * self.cell_size, 0, c * self.cell_size, h, fill="#444444", width=2)
            self.canvas.create_line(c * self.cell_size, 0, c * self.cell_size, h, fill="#666666", width=1)

        # Enhanced board border with softer glow effect
        try:
            # Outer shadow
            self.canvas.create_rectangle(2, 2, w - 2, h - 2, outline="#000000", width=3)
            # Main border with softer color
            self.canvas.create_rectangle(4, 4, w - 4, h - 4, outline="#4A90E2", width=2)
            # Inner glow
            self.canvas.create_rectangle(6, 6, w - 6, h - 6, outline="#87CEEB", width=1)
        except Exception:
            pass

    def toggle_sound(self):
        state = self.sound_var.get()
        try:
            # Update sound pill text
            sound_text = "🎵 Sound" if state else "🔇 Sound"
            self.bg_canvas.itemconfig(self.sound_text_shadow_dark, text=sound_text)
            self.bg_canvas.itemconfig(self.sound_text_shadow_light, text=sound_text)
            self.bg_canvas.itemconfig(self.sound_text_main, text=sound_text)
        except Exception:
            pass
    
    def toggle_sound_click(self):
        """Handle sound pill click"""
        self.sound_var.set(not self.sound_var.get())
        self.toggle_sound()

    def pause_game(self):
        """Show overlay when paused"""
        if self.background_overlay is not None:
            self.background_overlay.lift()
            self.background_overlay.itemconfig(self.overlay_rect, fill="black")
            self.background_overlay.itemconfig(self.overlay_rect, stipple="gray50")

    def resume_game(self):
        """Hide overlay when resumed"""
        if self.background_overlay is not None:
            self.background_overlay.lower()
            self.background_overlay.itemconfig(self.overlay_rect, fill="")
            self.background_overlay.itemconfig(self.overlay_rect, stipple="")

    # ----------------- UI helpers -----------------
    def _create_round_rect(self, x1, y1, x2, y2, r=20, **kwargs):
        # Create perfect pill shape using tkinter's built-in rounded rectangle
        try:
            # Use tkinter's create_round_rectangle if available, otherwise use oval
            return self.bg_canvas.create_oval(x1, y1, x2, y2, **kwargs)
        except Exception:
            # Fallback to simple rounded rectangle
            return self.bg_canvas.create_oval(x1, y1, x2, y2, **kwargs)

    def _schedule_button_animation(self):
        try:
            for btn, st in list(self._button_anims.items()):
                st["phase"] = (st.get("phase", 0.0) + 0.18) % 6.283
                info = self._button_bg_rects.get(btn)
                if not info:
                    continue
                glow_id = info["glow"]
                rect_id = info["rect"]
                window_id = st.get("window")
                # Pulse only when hovered
                if st.get("hover"):
                    # Adjust glow size subtly
                    try:
                        bbox = self.bg_canvas.bbox(window_id)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            pad = 15
                            pulse = 3 + int(2 * (1 + __import__("math").sin(st["phase"])) )
                            self.bg_canvas.coords(glow_id, x1 - pad - pulse, y1 - pad - pulse, x2 + pad + pulse, y2 + pad + pulse)
                    except Exception:
                        pass
                else:
                    # Reset to default size
                    try:
                        bbox = self.bg_canvas.bbox(window_id)
                        if bbox:
                            x1, y1, x2, y2 = bbox
                            pad = 15
                            self.bg_canvas.coords(glow_id, x1 - pad - 6, y1 - pad - 6, x2 + pad + 6, y2 + pad + 6)
                    except Exception:
                        pass
        except Exception:
            pass
        # Schedule next frame and keep the id to allow cancellation on destroy
        try:
            self._anim_after_id = self.root.after(33, self._schedule_button_animation)
        except Exception:
            pass

    def destroy(self):
        """Cancel scheduled animations before destroying to avoid invalid callbacks."""
        try:
            if hasattr(self, '_anim_after_id') and self._anim_after_id:
                self.root.after_cancel(self._anim_after_id)
        except Exception:
            pass

    def _attach_arcade_text(self, btn, window_id, label, main="#FFFFFF", outline="#000000"):
        """Overlay outlined text on top of a button, similar to Pac-Man UI. Stored for hover color tweaks."""
        try:
            if not hasattr(self, "_button_texts"):
                self._button_texts = {}
            self.root.update_idletasks()
            bbox = self.bg_canvas.bbox(window_id)
            if not bbox:
                return
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            # Create outline layers
            font = ("Arial", 11, "bold")
            ids = []
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                tid = self.bg_canvas.create_text(cx + dx, cy + dy, text=label, fill=outline, font=font, state="disabled")
                ids.append(tid)
            main_id = self.bg_canvas.create_text(cx, cy, text=label, fill=main, font=font, state="disabled")
            ids.append(main_id)
            for tid in ids:
                self.bg_canvas.tag_raise(tid)
            self._button_texts[btn] = {"ids": ids, "main": main, "outline": outline, "window": window_id, "label": label}

            # Sync position on enter/leave in case of minor animations
            def refresh_position():
                try:
                    bbox2 = self.bg_canvas.bbox(window_id)
                    if not bbox2:
                        return
                    xx1, yy1, xx2, yy2 = bbox2
                    ccx = (xx1 + xx2) // 2
                    ccy = (yy1 + yy2) // 2
                    for i, (dx, dy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
                        self.bg_canvas.coords(ids[i], ccx + dx, ccy + dy)
                    self.bg_canvas.coords(ids[-1], ccx, ccy)
                except Exception:
                    pass

            def on_enter(_e):
                refresh_position()
            def on_leave(_e):
                refresh_position()
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        except Exception:
            pass

    def _draw_neon_decorations(self):
        """Draw neon vertical lines around button area similar to pygame version"""
        try:
            # Button area coordinates
            btn_top = 60
            btn_bot = 120
            line_h = btn_bot - btn_top
            
            # Left neon line with gradient
            for y in range(line_h):
                ratio = y / line_h
                r = int(160 + 80 * ratio)
                g = int(10 + 120 * ratio)
                b = int(255 - 60 * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                # Multiple layers for glow effect
                self.bg_canvas.create_line(60, btn_top + y, 60, btn_top + y, fill=color, width=8, state="disabled")
                self.bg_canvas.create_line(63, btn_top + y, 63, btn_top + y, fill=color, width=4, state="disabled")
                self.bg_canvas.create_line(65, btn_top + y, 65, btn_top + y, fill=color, width=2, state="disabled")
            
            # Right neon line with different gradient
            for y in range(line_h):
                ratio = y / line_h
                r = int(255 - 60 * ratio)
                g = int(160 + 80 * ratio)
                b = int(220 + 30 * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                # Multiple layers for glow effect
                self.bg_canvas.create_line(940, btn_top + y, 940, btn_top + y, fill=color, width=8, state="disabled")
                self.bg_canvas.create_line(937, btn_top + y, 937, btn_top + y, fill=color, width=4, state="disabled")
                self.bg_canvas.create_line(935, btn_top + y, 935, btn_top + y, fill=color, width=2, state="disabled")
        except Exception:
            pass

    def _create_button_panel(self, x, y, w, h):
        """Create button panel with shadow and glow effects"""
        try:
            # Shadow effect
            shadow = self.bg_canvas.create_rectangle(x+4, y+4, x+w+4, y+h+4, fill="#323232", outline="")
            self.bg_canvas.tag_lower(shadow)
            
            # Main panel
            panel = self.bg_canvas.create_rectangle(x, y, x+w, y+h, fill="#F5F5FF", outline="#C8C8DC", width=3)
            self.bg_canvas.tag_lower(panel)
            return panel
        except Exception:
            return None

    def _create_glassmorphism_header(self):
        """Create modern glassmorphism effect for header background"""
        try:
            # Create dark overlay for better contrast
            self.bg_canvas.create_rectangle(0, 0, 1000, 70, fill="#000000", outline="", stipple="gray25")
            
            # Create main header background with glassmorphism
            self.bg_canvas.create_rectangle(20, 15, 980, 55, fill="#1A1A2E", outline="", stipple="gray12")
            
            # Add subtle glow effect
            for i in range(2):
                alpha = 20 - i * 8
                glow_rect = self.bg_canvas.create_rectangle(
                    20 - i, 15 - i, 980 + i, 55 + i,
                    fill="#FFFFFF", outline="", stipple="gray12"
                )
                self.bg_canvas.tag_lower(glow_rect)
        except Exception:
            pass
    
    def _create_title_pill(self):
        """Create modern title with electric theme and glow effect"""
        # Title pill background with gradient effect
        self.title_pill_bg = self.bg_canvas.create_rectangle(30, 20, 220, 50, fill="#FFD600", outline="", stipple="gray12")
        
        # Add shadow for depth
        self.title_shadow_bg = self.bg_canvas.create_rectangle(32, 22, 222, 52, fill="#B8860B", outline="", stipple="gray12")
        self.bg_canvas.tag_lower(self.title_shadow_bg)
        
        # Add electric glow effect
        self.title_glow = self.bg_canvas.create_rectangle(25, 15, 225, 55, fill="", outline="#FFE55C", width=3)
        self.bg_canvas.tag_lower(self.title_glow)
        
        # Title text with enhanced styling
        self.title_shadow = self.bg_canvas.create_text(127, 37, text="⚡ PIKACHU ⚡", fill="#B8860B", 
                                                      font=("Poppins", 16, "bold"), anchor="center")
        self.title_text = self.bg_canvas.create_text(126, 36, text="⚡ PIKACHU ⚡", fill="#FFFFFF", 
                                                    font=("Poppins", 16, "bold"), anchor="center")
        
        # Add subtle border
        self.title_border = self.bg_canvas.create_rectangle(30, 20, 220, 50, fill="", outline="#FFE55C", width=1)
    
    def _create_info_pills(self):
        """Create modern pill-style info boxes with proper spacing"""
        # Cost pill - Primary yellow
        self._create_modern_pill(250, 22, 320, 48, "💰 Cost: 0", "#FFD600", "#FFFFFF", "cost")
        
        # Time pill - Orange accent
        self._create_modern_pill(340, 22, 410, 48, "⏱️ Time: 0s", "#FF8C00", "#FFFFFF", "time")
        
        # Sound pill - Blue accent with click functionality
        self._create_modern_pill(430, 22, 500, 48, "🔈 Sound", "#42A5F5", "#FFFFFF", "sound")
        # Make sound pill clickable
        self.bg_canvas.tag_bind(self.sound_text_main, "<Button-1>", lambda e: self.toggle_sound_click())
        self.bg_canvas.tag_bind(self.sound_text_shadow_light, "<Button-1>", lambda e: self.toggle_sound_click())
        self.bg_canvas.tag_bind(self.sound_text_shadow_dark, "<Button-1>", lambda e: self.toggle_sound_click())
        
        # Mode pill - Green accent (clickable)
        self._create_clickable_pill(520, 22, 590, 48, "📋 Manual", "#4CAF50", "#FFFFFF", "mode")
        
        # Algorithm pill - Purple accent (clickable)
        self._create_clickable_pill(610, 22, 680, 48, "🧠 DFS", "#9C27B0", "#FFFFFF", "algo")
    
    def _create_modern_pill(self, x1, y1, x2, y2, text, bg_color, text_color, pill_type):
        """Create a modern pill with enhanced readability and glow effects"""
        # Add shadow for depth
        shadow_bg = self.bg_canvas.create_rectangle(x1 + 2, y1 + 2, x2 + 2, y2 + 2, fill="#000000", outline="", stipple="gray25")
        self.bg_canvas.tag_lower(shadow_bg)
        
        # Main pill background
        pill_bg = self.bg_canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="", stipple="gray12")
        
        # Add glow effect instead of hard border
        glow_color = self._get_glow_color(bg_color)
        pill_glow = self.bg_canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1, fill="", outline=glow_color, width=2)
        
        # Enhanced text with better shadow for readability
        text_shadow_dark = self.bg_canvas.create_text((x1+x2)//2 + 2, (y1+y2)//2 + 2, text=text, fill="#000000", 
                                                     font=("Poppins", 10, "bold"), anchor="center")
        text_shadow_light = self.bg_canvas.create_text((x1+x2)//2 + 1, (y1+y2)//2 + 1, text=text, fill="#FFFFFF", 
                                                      font=("Poppins", 10, "bold"), anchor="center")
        text_main = self.bg_canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, fill=text_color, 
                                              font=("Poppins", 10, "bold"), anchor="center")
        
        # Store references for updates
        if pill_type == "cost":
            self.cost_pill_bg = pill_bg
            self.cost_pill_glow = pill_glow
            self.cost_text_shadow_dark = text_shadow_dark
            self.cost_text_shadow_light = text_shadow_light
            self.cost_text_main = text_main
        elif pill_type == "time":
            self.time_pill_bg = pill_bg
            self.time_pill_glow = pill_glow
            self.time_text_shadow_dark = text_shadow_dark
            self.time_text_shadow_light = text_shadow_light
            self.time_text_main = text_main
        elif pill_type == "sound":
            self.sound_pill_bg = pill_bg
            self.sound_pill_glow = pill_glow
            self.sound_text_shadow_dark = text_shadow_dark
            self.sound_text_shadow_light = text_shadow_light
            self.sound_text_main = text_main
        elif pill_type == "mode":
            self.mode_pill_bg = pill_bg
            self.mode_pill_glow = pill_glow
            self.mode_text_shadow_dark = text_shadow_dark
            self.mode_text_shadow_light = text_shadow_light
            self.mode_text_main = text_main
        elif pill_type == "algo":
            self.algo_pill_bg = pill_bg
            self.algo_pill_glow = pill_glow
            self.algo_text_shadow_dark = text_shadow_dark
            self.algo_text_shadow_light = text_shadow_light
            self.algo_text_main = text_main
    
    def _get_glow_color(self, bg_color):
        """Get appropriate glow color based on background color"""
        glow_colors = {
            "#FFD600": "#FFE55C",  # Yellow glow
            "#FF8C00": "#FFB74D",  # Orange glow
            "#42A5F5": "#90CAF9",  # Blue glow
            "#4CAF50": "#81C784",  # Green glow
            "#9C27B0": "#BA68C8"   # Purple glow
        }
        return glow_colors.get(bg_color, "#FFFFFF")
    
    def _create_dropdown_menus(self):
        """Create dropdown menus for mode and algorithm selection"""
        # Dropdown menus are now replaced by clickable pills
        pass
    
    def _create_clickable_pill(self, x1, y1, x2, y2, text, bg_color, text_color, pill_type):
        """Create a clickable pill that cycles through values when clicked"""
        # Add shadow for depth
        shadow_bg = self.bg_canvas.create_rectangle(x1 + 2, y1 + 2, x2 + 2, y2 + 2, fill="#000000", outline="", stipple="gray25")
        self.bg_canvas.tag_lower(shadow_bg)
        
        # Main pill background
        pill_bg = self.bg_canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="", stipple="gray12")
        
        # Add glow effect instead of hard border
        glow_color = self._get_glow_color(bg_color)
        pill_glow = self.bg_canvas.create_rectangle(x1-1, y1-1, x2+1, y2+1, fill="", outline=glow_color, width=2)
        
        # Enhanced text with better shadow for readability
        text_shadow_dark = self.bg_canvas.create_text((x1+x2)//2 + 2, (y1+y2)//2 + 2, text=text, fill="#000000", 
                                                     font=("Poppins", 10, "bold"), anchor="center")
        text_shadow_light = self.bg_canvas.create_text((x1+x2)//2 + 1, (y1+y2)//2 + 1, text=text, fill="#FFFFFF", 
                                                      font=("Poppins", 10, "bold"), anchor="center")
        text_main = self.bg_canvas.create_text((x1+x2)//2, (y1+y2)//2, text=text, fill=text_color, 
                                              font=("Poppins", 10, "bold"), anchor="center")
        
        # Store references for updates
        if pill_type == "mode":
            self.mode_pill_bg = pill_bg
            self.mode_pill_glow = pill_glow
            self.mode_text_shadow_dark = text_shadow_dark
            self.mode_text_shadow_light = text_shadow_light
            self.mode_text_main = text_main
            self.mode_values = ["Manual", "Auto"]
            self.mode_current_index = 0
        elif pill_type == "algo":
            self.algo_pill_bg = pill_bg
            self.algo_pill_glow = pill_glow
            self.algo_text_shadow_dark = text_shadow_dark
            self.algo_text_shadow_light = text_shadow_light
            self.algo_text_main = text_main
            self.algo_values = ["DFS", "BFS", "A*"]
            self.algo_current_index = 0
        
        # Make pill clickable
        self.bg_canvas.tag_bind(text_main, "<Button-1>", lambda e, ptype=pill_type: self._cycle_pill_value(ptype))
        self.bg_canvas.tag_bind(text_shadow_light, "<Button-1>", lambda e, ptype=pill_type: self._cycle_pill_value(ptype))
        self.bg_canvas.tag_bind(text_shadow_dark, "<Button-1>", lambda e, ptype=pill_type: self._cycle_pill_value(ptype))
    
    def _cycle_pill_value(self, pill_type):
        """Cycle through values when pill is clicked"""
        if pill_type == "mode":
            self.mode_current_index = (self.mode_current_index + 1) % len(self.mode_values)
            new_value = self.mode_values[self.mode_current_index]
            self.mode_var.set(new_value)
            self._update_pill_text("mode", f"📋 {new_value}")
        elif pill_type == "algo":
            self.algo_current_index = (self.algo_current_index + 1) % len(self.algo_values)
            new_value = self.algo_values[self.algo_current_index]
            self.algo_var.set(new_value)
            self._update_pill_text("algo", f"🧠 {new_value}")
    
    def _update_pill_text(self, pill_type, new_text):
        """Update pill text when value changes"""
        try:
            if pill_type == "mode":
                self.bg_canvas.itemconfig(self.mode_text_shadow_dark, text=new_text)
                self.bg_canvas.itemconfig(self.mode_text_shadow_light, text=new_text)
                self.bg_canvas.itemconfig(self.mode_text_main, text=new_text)
            elif pill_type == "algo":
                self.bg_canvas.itemconfig(self.algo_text_shadow_dark, text=new_text)
                self.bg_canvas.itemconfig(self.algo_text_shadow_light, text=new_text)
                self.bg_canvas.itemconfig(self.algo_text_main, text=new_text)
        except Exception:
            pass

    def _create_pill(self, x1, y1, x2, y2, text, bg_color, text_color, pill_type):
        """Create a single pill with glassmorphism effect (legacy method)"""
        # This method is kept for compatibility but not used
        pass

    def _create_glassmorphism_containers(self):
        """Create glassmorphism containers for info boxes"""
        # This method is now replaced by _create_info_pills
        pass
    
    def update_moves(self, moves):
        """Update cost display"""
        try:
            text = f"💰 Cost: {moves}"
            self.bg_canvas.itemconfig(self.cost_text_shadow_dark, text=text)
            self.bg_canvas.itemconfig(self.cost_text_shadow_light, text=text)
            self.bg_canvas.itemconfig(self.cost_text_main, text=text)
        except Exception:
            pass
    
    def update_time(self, time_str):
        """Update time display"""
        try:
            text = f"⏱️ Time: {time_str}"
            self.bg_canvas.itemconfig(self.time_text_shadow_dark, text=text)
            self.bg_canvas.itemconfig(self.time_text_shadow_light, text=text)
            self.bg_canvas.itemconfig(self.time_text_main, text=text)
        except Exception:
            pass
    
    def update_mode(self, mode):
        """Update mode display"""
        try:
            text = f"📋 {mode}"
            self.bg_canvas.itemconfig(self.mode_text_shadow_dark, text=text)
            self.bg_canvas.itemconfig(self.mode_text_shadow_light, text=text)
            self.bg_canvas.itemconfig(self.mode_text_main, text=text)
        except Exception:
            pass
    
    def update_algorithm(self, algo):
        """Update algorithm display"""
        try:
            text = f"🧠 {algo}"
            self.bg_canvas.itemconfig(self.algo_text_shadow_dark, text=text)
            self.bg_canvas.itemconfig(self.algo_text_shadow_light, text=text)
            self.bg_canvas.itemconfig(self.algo_text_main, text=text)
        except Exception:
            pass

    def _create_algo_panel(self, combo_window_id, title="Algorithm", base="#2D3748", border="#66FCF1", glow="#A0E7E5"):
        """Draw a rounded framed panel behind the algorithm combobox with outlined title and glow on focus."""
        # Measure combobox bbox and draw a pill panel a bit larger with title at left
        self.root.update_idletasks()
        bbox = self.bg_canvas.bbox(combo_window_id)
        if not bbox:
            return
        x1, y1, x2, y2 = bbox
        pad_x, pad_y = 18, 10
        panel_x1 = x1 - pad_x
        panel_y1 = y1 - pad_y
        panel_x2 = x2 + pad_x
        panel_y2 = y2 + pad_y

        # Shadow
        shadow = self._create_round_rect(panel_x1 + 3, panel_y1 + 3, panel_x2 + 3, panel_y2 + 3, fill="#000000", outline="")
        self.bg_canvas.tag_lower(shadow)
        # Base
        panel = self._create_round_rect(panel_x1, panel_y1, panel_x2, panel_y2, fill=base, outline="")
        self.bg_canvas.tag_lower(panel)
        # Border
        border_id = self._create_round_rect(panel_x1, panel_y1, panel_x2, panel_y2, fill="", outline=border, width=2)
        self.bg_canvas.tag_lower(border_id)
        # Glow (hidden)
        glow_id = self._create_round_rect(panel_x1 - 6, panel_y1 - 6, panel_x2 + 6, panel_y2 + 6, fill=glow, outline="")
        self.bg_canvas.tag_lower(glow_id)
        self.bg_canvas.itemconfig(glow_id, state="hidden")

        # Outlined title text on left
        title_x = panel_x1 + 12
        title_y = (panel_y1 + panel_y2) // 2
        outline_ids = []
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            outline_ids.append(self.bg_canvas.create_text(title_x + dx, title_y + dy, text=title, fill="#000000", font=("Arial", 10, "bold"), anchor="w"))
        title_id = self.bg_canvas.create_text(title_x, title_y, text=title, fill="#FFFFFF", font=("Arial", 10, "bold"), anchor="w")
        for tid in outline_ids + [title_id]:
            self.bg_canvas.tag_raise(tid)

        # Keep references for interaction
        self._algo_panel = {"panel": panel, "border": border_id, "glow": glow_id, "title": title_id, "outline": outline_ids}

        # Bind focus/hover to show glow
        def show_glow(_=None):
            try:
                self.bg_canvas.itemconfig(glow_id, state="normal")
            except Exception:
                pass
        def hide_glow(_=None):
            try:
                self.bg_canvas.itemconfig(glow_id, state="hidden")
            except Exception:
                pass
        # Attach to combobox events
        try:
            widget = self.algo_menu
            widget.bind("<Enter>", show_glow)
            widget.bind("<Leave>", hide_glow)
            widget.bind("<FocusIn>", show_glow)
            widget.bind("<FocusOut>", hide_glow)
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = GameUI(root, 4, 4, 100)
    root.mainloop()