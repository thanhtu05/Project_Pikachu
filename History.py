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
        {
            "rows": 4, "cols": 4, "algo": "DFS", "mode": "Manual",
            "cost": 12, "time": 45, "steps": 8, "visited": 25, "generated": 45, "time_ms": 2.5
        },
        {
            "rows": 4, "cols": 4, "algo": "BFS", "mode": "Auto",
            "cost": 10, "time": 38, "steps": 6, "visited": 18, "generated": 32, "time_ms": 1.8
        },
        {
            "rows": 4, "cols": 4, "algo": "A*", "mode": "Auto",
            "cost": 8, "time": 32, "steps": 4, "visited": 12, "generated": 20, "time_ms": 1.2
        },
        {
            "rows": 4, "cols": 4, "algo": "UCS", "mode": "Manual",
            "cost": 14, "time": 52, "steps": 10, "visited": 35, "generated": 58, "time_ms": 3.1
        },
        {
            "rows": 4, "cols": 4, "algo": "DFS", "mode": "Auto",
            "cost": 11, "time": 41, "steps": 7, "visited": 22, "generated": 38, "time_ms": 2.0
        }
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
