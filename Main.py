import tkinter as tk
from SplashScreen import ModernSplashScreen   # Import class

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = ModernSplashScreen(splash_root)  # Khởi tạo SplashScreen
    splash_root.mainloop()
