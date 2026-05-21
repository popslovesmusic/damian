import tkinter as tk
from engine.runtime.playable_slice_manager import PlayableSliceManager

class WindowedInputLoop:
    def __init__(self, psm):
        self.psm = psm
        self.root = tk.Tk()
        self.root.title("Tower Prototype")
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="black")
        self.canvas.pack()
        
        self.text_id = self.canvas.create_text(400, 300, text="", fill="white", font=("Courier", 12))
        
        self.root.bind("<Key>", self.handle_keypress)
        self.update_display()
        
    def handle_keypress(self, event):
        key = event.keysym.upper()
        if key == "ESCAPE":
            self.root.quit()
        
        action = None
        if key in ["W", "A", "S", "D"]:
            action = "MOVE"
            # Map to dir
            dirs = {"W": "NORTH", "A": "WEST", "S": "SOUTH", "D": "EAST"}
            value = dirs[key]
        elif key == "E":
            action = "DOOR"
            value = "OPEN"
        
        if action:
            self.psm.simulate_player_input(action, value)
            self.update_display()
            
    def update_display(self):
        frame = self.psm.visual_log[-1]["isometric"] if self.psm.visual_log else "Initializing..."
        self.canvas.itemconfig(self.text_id, text=frame)
        
    def run(self):
        self.root.mainloop()
