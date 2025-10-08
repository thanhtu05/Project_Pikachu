import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


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

        # Status labels
        # Enhanced top bar with neon gradient effect
        self.topbar = self.bg_canvas.create_rectangle(0, 0, 1000, 50, fill="#0B0C10", outline="")
        # Create neon gradient effect similar to pygame version
        try:
            for i in range(50):
                ratio = i / 50
                # Neon blue to purple gradient
                r = int(160 + 80 * ratio)
                g = int(10 + 120 * ratio) 
                b = int(255 - 60 * ratio)
                color = f"#{r:02x}{g:02x}{b:02x}"
                self.bg_canvas.create_line(0, i, 1000, i, fill=color, width=1)
        except Exception:
            pass
            

        self.bg_canvas.create_text(20, 12, text="PIKACHU", fill="#A0E7E5", font=("Arial", 18, "bold"), anchor="nw")

        # Enhanced status labels with text effects
        self.moves_label = tk.Label(self.bg_canvas, text="Cost: 0", fg="#FFD166", bg="#0B0C10",
                                    font=("Arial", 12, "bold"), relief="flat", bd=0)
        self.moves_label_window = self.bg_canvas.create_window(120, 12, window=self.moves_label, anchor="nw")
        
        # Add text shadow effect to cost label
        try:
            self.cost_shadow = self.bg_canvas.create_text(102, 14, text="Cost: 0", fill="#000000", 
                                                         font=("Arial", 12, "bold"), anchor="nw")
            self.bg_canvas.tag_lower(self.cost_shadow)
        except Exception:
            pass

        self.time_label = tk.Label(self.bg_canvas, text="Time: 0s", fg="#06D6A0", bg="#0B0C10",
                                   font=("Arial", 12, "bold"), relief="flat", bd=0)
        self.time_label_window = self.bg_canvas.create_window(220, 12, window=self.time_label, anchor="nw")
        
        # Add text shadow effect to time label
        try:
            self.time_shadow = self.bg_canvas.create_text(222, 14, text="Time: 0s", fill="#000000", 
                                                         font=("Arial", 12, "bold"), anchor="nw")
            self.bg_canvas.tag_lower(self.time_shadow)
        except Exception:
            pass

        # Sound toggle
        self.sound_var = tk.BooleanVar(value=True)
        style.configure("MyCheck.TCheckbutton", background="#0B0C10", foreground="#C5C6C7")
        self.sound_toggle = ttk.Checkbutton(self.bg_canvas, text="🔊 Sound", variable=self.sound_var,
                                            command=self.toggle_sound, style="MyCheck.TCheckbutton", width=12)
        self.sound_toggle_window = self.bg_canvas.create_window(370, 12, window=self.sound_toggle, anchor="nw")

        # Mode selection with rounded background
        self.mode_var = tk.StringVar(value="Manual")
        self.mode_menu = ttk.Combobox(self.bg_canvas, textvariable=self.mode_var, values=["Manual", "Auto"],
                                      state="readonly", width=10, style="Rounded.TCombobox")
        self.mode_menu_window = self.bg_canvas.create_window(520, 12, window=self.mode_menu, anchor="nw")
        
        # Add rounded background for mode dropdown
        try:
            self.mode_bg = self.bg_canvas.create_oval(500, 5, 580, 25, fill="#2D3748", outline="#C8C8DC", width=2)
            self.bg_canvas.tag_lower(self.mode_bg)
        except Exception:
            pass

        # Algorithm selection with rounded background
        self.algo_var = tk.StringVar(value="DFS")
        self.algo_menu = ttk.Combobox(self.bg_canvas, textvariable=self.algo_var,
                                      values=["DFS", "BFS", "UCS", "A*", "HillClimb"], state="readonly", width=10, style="Rounded.TCombobox")
        self.algo_menu_window = self.bg_canvas.create_window(630, 12, window=self.algo_menu, anchor="nw")
        
        # Add framed selector panel for Algorithm (arcade style)
        try:
            self._create_algo_panel(self.algo_menu_window, title="Algorithm", base="#2D3748", border="#66FCF1", glow="#A0E7E5")
        except Exception:
            pass

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

        # Button style
        button_style = {
            "width": 12,
            "height": 2,
            "font": ("Arial", 10, "bold"),
            "relief": "raised",
            "bd": 2,
            "cursor": "hand2",
            "activeforeground": "#0B0C10"
        }

        # Layout buttons
        # Skip button removed -> adjust count to 6
        button_count = 6
        button_width = 12 * 8 + 4
        total_available_width = 1000 - 200
        button_spacing = max(8, (total_available_width - (button_count * button_width)) // (button_count + 1))
        start_x = 60

        self.new_btn = tk.Button(self.bg_canvas, text="🆕 New Game", bg="#118AB2", fg="#FFFFFF",
                                 activebackground="#073B4C", **button_style)
        self.new_btn_window = self.bg_canvas.create_window(start_x + 0 * (button_spacing + button_width), 60, window=self.new_btn, anchor="nw")

        self.auto_btn = tk.Button(self.bg_canvas, text="▶️ Start Auto", bg="#06D6A0", fg="#0B0C10",
                                  activebackground="#118AB2", **button_style)
        self.auto_btn_window = self.bg_canvas.create_window(start_x + 1 * (button_spacing + button_width), 60,
                                                             window=self.auto_btn, anchor="nw")
        # wire to game's start_auto if provided
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'start_auto'):
            try:
                self.auto_btn.config(command=self.game.start_auto)
            except Exception:
                pass

        # Skip button removed per user request

        self.stop_btn = tk.Button(self.bg_canvas, text="⏹️ Stop", bg="#EF476F", fg="#FFFFFF",
                                  activebackground="#D62839", command=self.pause_game,
                                  **button_style)
        self.stop_btn_window = self.bg_canvas.create_window(start_x + 2 * (button_spacing + button_width), 60,
                                                             window=self.stop_btn, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'stop_game'):
            try:
                self.stop_btn.config(command=self.game.stop_game)
            except Exception:
                pass

        self.continue_btn = tk.Button(self.bg_canvas, text="▶️ Continue", bg="#FFD166", fg="#0B0C10",
                                      activebackground="#06D6A0", command=self.resume_game,
                                      **button_style)
        self.continue_btn_window = self.bg_canvas.create_window(start_x + 3 * (button_spacing + button_width), 60,
                                                                 window=self.continue_btn, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'resume_game'):
            try:
                self.continue_btn.config(command=self.game.resume_game)
            except Exception:
                pass

        self.history_btn = tk.Button(self.bg_canvas, text="📊 History", bg="#073B4C", fg="#FFFFFF",
                                     activebackground="#118AB2", **button_style)
        self.history_btn_window = self.bg_canvas.create_window(start_x + 4 * (button_spacing + button_width), 60,
                                                                window=self.history_btn, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'show_history'):
            try:
                self.history_btn.config(command=self.game.show_history)
            except Exception:
                pass

        self.home_btn = tk.Button(self.bg_canvas, text="🏠 Home", bg="#06D6A0", fg="#0B0C10",
                                  activebackground="#118AB2", **button_style)
        self.home_btn_window = self.bg_canvas.create_window(start_x + 5 * (button_spacing + button_width), 60,
                                                            window=self.home_btn, anchor="nw")
        if hasattr(self, 'game') and self.game and hasattr(self.game, 'go_home'):
            try:
                self.home_btn.config(command=self.game.go_home)
            except Exception:
                pass

        # --- Enhance buttons with rounded backgrounds and hover/press effects ---
        try:
            self._button_bg_rects = {}
            self._button_anims = {}
            self._attach_arcade_text(self.new_btn, self.new_btn_window, label="🆕 New Game",
                                      main="#FFFFFF", outline="#000000")

            self._attach_arcade_text(self.auto_btn, self.auto_btn_window, label="▶️ Start Auto",
                                      main="#0B0C10", outline="#FFFFFF")

            # Skip button removed - no attachment here

            self._attach_arcade_text(self.stop_btn, self.stop_btn_window, label="⏹️ Stop",
                                      main="#FFFFFF", outline="#000000")

            self._attach_arcade_text(self.continue_btn, self.continue_btn_window, label="▶️ Continue",
                                      main="#FFFFFF", outline="#000000")

            self._attach_arcade_text(self.history_btn, self.history_btn_window, label="📊 History",
                                      main="#FFFFFF", outline="#000000")

            self._attach_arcade_text(self.home_btn, self.home_btn_window, label="🏠 Home",
                                      main="#0B0C10", outline="#FFFFFF")
            # Start animation loop for pulsing glow
            self._schedule_button_animation()
        except Exception:
            pass

        # --- Game board with enhanced styling ---
        w, h = self.cols * self.cell_size, self.rows * self.cell_size
        self.canvas = tk.Canvas(self.bg_canvas, width=w, height=h, bg="#1A1A2E", borderwidth=0, relief="flat",
                                highlightthickness=2, highlightbackground="#16213E")
        self.canvas_window = self.bg_canvas.create_window(500, 160, window=self.canvas, anchor="n")
        
        # Add neon vertical lines around button area (similar to pygame version)
        self._draw_neon_decorations()

        # Raise widgets to top
        for win in [self.moves_label_window, self.time_label_window, self.sound_toggle_window,
                    self.mode_menu_window, self.algo_menu_window, self.new_btn_window, self.auto_btn_window,
                    self.stop_btn_window, self.continue_btn_window, self.history_btn_window,
                    self.home_btn_window, self.canvas_window]:
            try:
                self.bg_canvas.tag_raise(win)
            except Exception:
                pass

        # Enhanced grid with better visibility
        for r in range(self.rows + 1):
            # More visible grid lines
            self.canvas.create_line(0, r * self.cell_size, w, r * self.cell_size, fill="#2D3748", width=2)
            self.canvas.create_line(0, r * self.cell_size, w, r * self.cell_size, fill="#4A5568", width=1)
        for c in range(self.cols + 1):
            # More visible grid lines
            self.canvas.create_line(c * self.cell_size, 0, c * self.cell_size, h, fill="#2D3748", width=2)
            self.canvas.create_line(c * self.cell_size, 0, c * self.cell_size, h, fill="#4A5568", width=1)

        # Enhanced board border with neon effect
        try:
            # Outer shadow
            self.canvas.create_rectangle(2, 2, w - 2, h - 2, outline="#000000", width=4)
            # Main border
            self.canvas.create_rectangle(4, 4, w - 4, h - 4, outline="#66FCF1", width=2)
            # Inner glow
            self.canvas.create_rectangle(6, 6, w - 6, h - 6, outline="#A0E7E5", width=1)
        except Exception:
            pass

    def toggle_sound(self):
        state = self.sound_var.get()
        self.sound_toggle.config(text="🔊 Sound" if state else "🔇 Sound")

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