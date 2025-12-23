import tkinter as tk
from tkinter import messagebox, font
import json
import os
import subprocess
from datetime import datetime

# --- PORTABLE PATH LOGIC ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
SETTINGS_FILE = os.path.join(BASE_DIR, 'ugly stuff', 'course_settings.json')

# --- Theme Palette (GUI Colors) ---
E_BG = "#FDF5E6"         
E_SAGE = "#B2AC88"       
E_TERRACOTTA = "#CD5C5C" 
E_MOSS = "#556B2F"       
E_WHITE = "#FFFFFF"
E_CLAY = "#D2B48C"       

# --- NEW: Softer but Pigmented Palette for Excel ---
# These are muted, "dusty" versions of the previous colors
EARTHY_PALETTE = {
    "Dusty Sage": "#C1C6A6",      # Soft herbal green
    "Muted Rose": "#E4C1B9",      # Dusty pigmented pink
    "Desert Sand": "#E8D3B9",     # Warm soft tan
    "Cloudy Blue": "#B9CED1",     # Soft pigmented slate blue
    "Faded Moss": "#A9B399",      # Slightly darker muted green
    "Antique Lace": "#F2E8D5",    # Warm creamy off-white
    "Golden Oat": "#EBD9A0",      # Muted mustard/yellow
    "Twilight Lavender": "#D1C9D9" # Soft dusty purple
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
            if "courses" not in data:
                return {"courses": data, "last_updated": "Never", "auto_sync": False}
            return data
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    return {"courses": {}, "last_updated": "Never", "auto_sync": False}

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

class CourseGui:
    def __init__(self, root):
        self.root = root
        self.root.title("🌿 Canvas Garden 🌿")
        self.root.geometry("550x850")
        self.root.configure(bg=E_BG)
        
        self.full_data = load_settings()
        self.courses = self.full_data["courses"]
        self.is_syncing = self.full_data.get("auto_sync", False)

        # Fonts
        self.header_font = font.Font(family="Georgia", size=22, weight="bold")
        self.label_font = font.Font(family="Verdana", size=10)
        self.btn_font = font.Font(family="Verdana", size=10, weight="bold")

        # --- UI Header ---
        tk.Label(root, text="🍃 Course Oasis 🍃", font=self.header_font, 
                 bg=E_BG, fg=E_MOSS).pack(pady=(25, 5))

        self.status_label = tk.Label(root, text=f"Last bloom: {self.full_data['last_updated']}", 
                                     font=("Verdana", 9, "italic"), bg=E_BG, fg="#8B7E66")
        self.status_label.pack(pady=(0, 15))

        # --- Input Section ---
        input_container = tk.Frame(root, bg=E_BG)
        input_container.pack(pady=10)

        tk.Label(input_container, text="Course ID", font=self.label_font, bg=E_BG, fg=E_MOSS).pack()
        self.id_entry = tk.Entry(input_container, width=35, bd=0, highlightthickness=1, 
                                 highlightbackground=E_SAGE)
        self.id_entry.pack(pady=5)

        tk.Label(input_container, text="Class Nickname", font=self.label_font, bg=E_BG, fg=E_MOSS).pack()
        self.name_entry = tk.Entry(input_container, width=35, bd=0, highlightthickness=1, 
                                   highlightbackground=E_SAGE)
        self.name_entry.pack(pady=5)

        # --- Dropdown Color Selector ---
        tk.Label(root, text="Select Course Bloom Tone:", font=self.label_font, bg=E_BG, fg=E_MOSS).pack(pady=(10, 0))
        
        self.color_var = tk.StringVar(root)
        self.color_var.set("Dusty Sage") # Default
        
        self.color_menu = tk.OptionMenu(root, self.color_var, *EARTHY_PALETTE.keys(), command=self.update_preview)
        self.color_menu.config(bg=E_WHITE, fg=E_MOSS, font=self.label_font, relief="flat", width=20)
        self.color_menu.pack(pady=5)
        
        self.selected_color = EARTHY_PALETTE["Dusty Sage"]
        self.color_preview = tk.Label(root, text="Row Highlight Preview", bg=self.selected_color, 
                                      width=30, font=("Verdana", 8), fg=E_MOSS)
        self.color_preview.pack(pady=5)

        tk.Button(root, text="✨ Plant New Course ✨", font=self.btn_font, 
                  command=self.add_course, bg=E_TERRACOTTA, fg=E_WHITE, 
                  relief="flat", pady=12, padx=40, cursor="hand2").pack(pady=20)
        
        # --- Listbox ---
        tk.Label(root, text="Your Academic Garden 🪴", font=self.btn_font, bg=E_BG, fg=E_MOSS).pack()
        self.course_listbox = tk.Listbox(root, width=65, height=8, bd=0, font=("Verdana", 9),
                                         highlightthickness=1, highlightbackground=E_SAGE,
                                         selectbackground=E_SAGE, selectforeground=E_WHITE)
        self.course_listbox.pack(pady=10, padx=20)

        self.sync_var = tk.BooleanVar(value=self.is_syncing)
        self.sync_check = tk.Checkbutton(root, text="Automatic Growth (15m Sync) 🕰️", font=self.label_font,
                                        variable=self.sync_var, command=self.toggle_sync,
                                        bg=E_BG, activebackground=E_BG, fg=E_MOSS)
        self.sync_check.pack()

        # --- Footer ---
        btn_frame = tk.Frame(root, bg=E_BG)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Remove", command=self.delete_course, 
                  bg=E_CLAY, fg=E_WHITE, width=12, relief="flat", cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Harvest Excel 📝", font=self.btn_font, command=self.run_export, 
                  bg=E_SAGE, fg=E_WHITE, width=20, relief="flat", pady=8, cursor="hand2").pack(side=tk.LEFT, padx=10)

        self.refresh_list()
        if self.is_syncing:
            self.auto_sync_loop()

    def update_preview(self, choice):
        self.selected_color = EARTHY_PALETTE[choice]
        self.color_preview.config(bg=self.selected_color)

    def toggle_sync(self):
        self.is_syncing = self.sync_var.get()
        self.full_data["auto_sync"] = self.is_syncing
        save_settings(self.full_data)
        if self.is_syncing:
            self.auto_sync_loop()

    def auto_sync_loop(self):
        if self.is_syncing:
            self.run_export(silent=True)
            self.root.after(900000, self.auto_sync_loop)

    def add_course(self):
        cid, name = self.id_entry.get().strip(), self.name_entry.get().strip()
        if cid and name:
            self.courses[cid] = {"name": name, "color": self.selected_color}
            self.full_data["courses"] = self.courses
            save_settings(self.full_data)
            self.refresh_list()
            self.id_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.id_entry.focus()

    def delete_course(self):
        selected = self.course_listbox.curselection()
        if selected:
            item_text = self.course_listbox.get(selected[0])
            cid = item_text.split("|")[0].replace("ID: ", "").strip()
            if cid in self.courses:
                del self.courses[cid]
                save_settings(self.full_data)
                self.refresh_list()

    def run_export(self, silent=False):
        try:
            script_path = os.path.join(CURRENT_DIR, "canvas.py")
            try:
                subprocess.run(["python", script_path], check=True)
            except:
                subprocess.run(["python3", script_path], check=True)

            now = datetime.now().strftime("%b %d, %I:%M %p")
            self.full_data["last_updated"] = now
            save_settings(self.full_data)
            self.status_label.config(text=f"Last bloom: {now}")
            
            if not silent:
                messagebox.showinfo("Success 🌿", "Your garden has been harvested!")
                excel_file = os.path.join(BASE_DIR, "Canvas_Assignments.xlsx")
                if os.path.exists(excel_file):
                    os.startfile(excel_file)
        except Exception as e:
            if not silent:
                messagebox.showerror("Error 🍂", f"The harvest failed: {e}")

    def refresh_list(self):
        self.course_listbox.delete(0, tk.END)
        for cid, info in self.courses.items():
            self.course_listbox.insert(tk.END, f"ID: {cid}  |  🌿 {info['name']}  |  🎨 {info['color']}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseGui(root)
    root.mainloop()