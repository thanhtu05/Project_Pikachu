#!/usr/bin/env python3
"""
Demo script để test giao diện history mới
"""

import tkinter as tk
from Game import PikachuGame

def main():
    root = tk.Tk()
    game = PikachuGame(root, rows=4, cols=4)  # Tạo game nhỏ để test
    
    # Tạo một số dữ liệu history mẫu
    sample_history = [
        {}
    ]
    
    # Lưu dữ liệu mẫu vào file history
    import json
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(sample_history, f, ensure_ascii=False, indent=2)
    
    print("Demo History UI - Click 'History' button to see the new interface!")
    print("Features:")
    print("✅ Beautiful gradient background")
    print("✅ Statistics overview cards")
    print("✅ Enhanced data table with custom styling")
    print("✅ Filter and sort functionality")
    print("✅ Performance charts")
    print("✅ Export to CSV")
    print("✅ Clear history option")
    
    root.mainloop()

if __name__ == "__main__":
    main()
