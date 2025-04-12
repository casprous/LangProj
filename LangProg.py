import os
# Update the following path to where Ghostscript is installed on your system.
gs_path = r"C:\Program Files\gs\gs10.05.0\bin"
os.environ["PATH"] += os.pathsep + gs_path

import json
import time
import io
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk

# Helper functions for math-bold conversion using Unicode Mathematical Bold letters.
def to_bold(text):
    result = ""
    for ch in text:
        if 'a' <= ch <= 'z':
            result += chr(ord(ch) - ord('a') + 0x1D41A)
        elif 'A' <= ch <= 'Z':
            result += chr(ord(ch) - ord('A') + 0x1D400)
        else:
            result += ch
    return result

# Invert bolding: Bold the parts that were NOT highlighted and leave the highlighted substring normal.
def invert_bold(text, sub):
    idx = text.lower().find(sub.lower())
    if idx == -1:
        return to_bold(text)
    prefix = text[:idx]
    match = text[idx:idx+len(sub)]
    suffix = text[idx+len(sub):]
    return to_bold(prefix) + match + to_bold(suffix)

# Main application window.
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Imaginary Language Builder")
        self.geometry("600x750")
        self.characters_folder = "characters"
        self.metadata_file = os.path.join(self.characters_folder, "metadata.json")
        self.metadata = {}
        self.characters_list = []  # List of image filenames
        self.current_index = 0

        self.create_widgets()
        self.load_data()
        self.update_display()

    def create_widgets(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)
        self.create_button = tk.Button(control_frame, text="Create New Symbol", command=self.open_draw_window)
        self.create_button.grid(row=0, column=0, padx=5)
        self.edit_button = tk.Button(control_frame, text="Edit Symbol", command=self.edit_symbol)
        self.edit_button.grid(row=0, column=1, padx=5)
        self.import_button = tk.Button(control_frame, text="Import Symbol", command=self.import_symbol)
        self.import_button.grid(row=0, column=2, padx=5)
        self.export_button = tk.Button(control_frame, text="Export Symbol", command=self.export_symbol)
        self.export_button.grid(row=0, column=3, padx=5)
        self.sentence_builder_button = tk.Button(control_frame, text="Open Sentence Builder", command=self.open_sentence_builder)
        self.sentence_builder_button.grid(row=0, column=4, padx=5)

        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)
        self.info_label = tk.Label(self, text="", font=("Arial", 12))
        self.info_label.pack(pady=5)

        nav_frame = tk.Frame(self)
        nav_frame.pack(pady=10)
        self.prev_button = tk.Button(nav_frame, text="<< Previous", command=self.prev_symbol)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        self.next_button = tk.Button(nav_frame, text="Next >>", command=self.next_symbol)
        self.next_button.pack(side=tk.LEFT, padx=10)
        self.delete_button = tk.Button(self, text="Delete Symbol", command=self.delete_symbol)
        self.delete_button.pack(pady=5)

    def load_data(self):
        if not os.path.exists(self.characters_folder):
            os.makedirs(self.characters_folder)
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
        self.characters_list = sorted([fname for fname in os.listdir(self.characters_folder) if fname.endswith(".png")])
        self.current_index = 0 if self.characters_list else -1

    def update_display(self):
        if self.current_index == -1 or not self.characters_list:
            self.image_label.config(image="", text="No symbols available.")
            self.info_label.config(text="")
        else:
            filename = self.characters_list[self.current_index]
            image_path = os.path.join(self.characters_folder, filename)
            try:
                image = Image.open(image_path)
                image.thumbnail((400, 400))
                self.tk_image = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.tk_image, text="")
            except Exception as e:
                self.image_label.config(text="Error loading image.")
            meta = self.metadata.get(filename, {})
            type_val = meta.get("type", "")
            sound = meta.get("sound", "")
            meaning = meta.get("meaning", "")
            info_text = f"Type: {type_val}\nSound: {sound}"
            if type_val != "Letter":
                info_text += f"\nMeaning: {meaning}"
            self.info_label.config(text=info_text)

    def prev_symbol(self):
        if self.characters_list:
            self.current_index = (self.current_index - 1) % len(self.characters_list)
            self.update_display()

    def next_symbol(self):
        if self.characters_list:
            self.current_index = (self.current_index + 1) % len(self.characters_list)
            self.update_display()

    def open_draw_window(self):
        draw_window = DrawWindow(self)
        self.wait_window(draw_window)
        self.load_data()
        self.update_display()

    def edit_symbol(self, filename=None):
        if filename is None:
            if self.current_index == -1 or not self.characters_list:
                messagebox.showinfo("Edit", "No symbol available to edit.")
                return
            filename = self.characters_list[self.current_index]
        edit_window = EditSymbolWindow(self, filename)
        self.wait_window(edit_window)
        self.load_data()
        self.update_display()

    def import_symbol(self):
        file_path = filedialog.askopenfilename(title="Import Symbol from FontForge", filetypes=[("PNG Files", "*.png")])
        if file_path:
            timestamp = int(time.time() * 1000)
            new_filename = f"character_{timestamp}.png"
            new_filepath = os.path.join(self.characters_folder, new_filename)
            try:
                shutil.copyfile(file_path, new_filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Error importing symbol: {e}")
                return
            self.metadata[new_filename] = {"type": "Character", "sound": "", "meaning": ""}
            self.save_metadata()
            self.load_data()
            if new_filename in self.characters_list:
                self.current_index = self.characters_list.index(new_filename)
            self.edit_symbol(new_filename)

    def export_symbol(self):
        if self.current_index == -1 or not self.characters_list:
            messagebox.showinfo("Export", "No symbol available to export.")
            return
        filename = self.characters_list[self.current_index]
        current_filepath = os.path.join(self.characters_folder, filename)
        export_path = filedialog.asksaveasfilename(title="Export Symbol to FontForge", defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if export_path:
            try:
                shutil.copyfile(current_filepath, export_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting symbol: {e}")

    def save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def delete_symbol(self):
        if not self.characters_list:
            messagebox.showinfo("Delete", "No symbol available to delete.")
            return
        filename = self.characters_list[self.current_index]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this symbol?"):
            file_path = os.path.join(self.characters_folder, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
                return
            if filename in self.metadata:
                del self.metadata[filename]
                self.save_metadata()
            self.characters_list.remove(filename)
            if self.characters_list:
                self.current_index %= len(self.characters_list)
            else:
                self.current_index = -1
            self.update_display()
            messagebox.showinfo("Deleted", "Symbol deleted successfully!")

    def open_sentence_builder(self):
        SentenceBuilderWindow(self)

# DrawWindow with a tabbed interface for creation and IPA keyboard.
class DrawWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Draw Symbol")
        self.base_window_width = 500
        self.base_window_height = 950
        self.base_canvas_width = 400
        self.base_canvas_height = 400
        self.base_ipa_font_size = 16
        self.base_eng_font_size = 10
        self.scale = 1.0
        self.geometry(f"{self.base_window_width}x{self.base_window_height}")
        self.last_x, self.last_y = None, None
        self.ipa_key_widgets = []
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        # Creation tab.
        self.creation_frame = tk.Frame(self.notebook)
        self.notebook.add(self.creation_frame, text="Creation")
        # IPA Keyboard tab.
        self.keyboard_tab = tk.Frame(self.notebook)
        self.notebook.add(self.keyboard_tab, text="IPA Keyboard")

        # --- In the Creation Tab ---
        zoom_frame = tk.Frame(self.creation_frame)
        zoom_frame.pack(pady=5)
        zoom_in_btn = tk.Button(zoom_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        zoom_out_btn = tk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.creation_frame, bg="white",
                                width=int(self.base_canvas_width * self.scale),
                                height=int(self.base_canvas_height * self.scale))
        self.canvas.pack(pady=10)

        tk.Label(self.creation_frame, text="Select Type:").pack()
        self.type_var = tk.StringVar(value="Character")
        self.type_menu = tk.OptionMenu(self.creation_frame, self.type_var, "Character", "Letter", "Both")
        self.type_menu.pack()
        self.type_var.trace("w", self.type_changed)

        tk.Label(self.creation_frame, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display = tk.Label(self.creation_frame, text="", relief="sunken",
                                    width=int(30 * self.scale), anchor="w")
        self.ipa_display.pack(pady=5)
        self.clear_btn = tk.Button(self.creation_frame, text="Clear IPA", command=self.clear_ipa)
        self.clear_btn.pack(pady=5)

        tk.Label(self.creation_frame, text="Meaning:").pack(pady=(10, 0))
        self.meaning_entry = tk.Entry(self.creation_frame)
        self.meaning_entry.pack()

        self.save_button = tk.Button(self.creation_frame, text="Save Symbol", command=self.save_symbol)
        self.save_button.pack(pady=10)

        # --- In the IPA Keyboard Tab ---
        tk.Label(self.keyboard_tab, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display_copy = tk.Label(self.keyboard_tab, text="", relief="sunken",
                                         width=int(30 * self.scale), anchor="w")
        self.ipa_display_copy.pack(pady=5)
        # Create a subframe for keys using grid.
        keys_frame = tk.Frame(self.keyboard_tab)
        keys_frame.pack(pady=5)
        self.ipa_keys = [
            ("p", "pea", "p"), ("b", "bee", "b"), ("t", "tea", "t"), ("d", "deed", "d"),
            ("k", "key", "k"), ("g", "geese", "g"), ("f", "fee", "f"), ("v", "vee", "v"),
            ("θ", "thing", "th"), ("ð", "this", "th"), ("s", "see", "s"), ("z", "zebra", "z"),
            ("ʃ", "she", "sh"), ("ʒ", "vision", "sion"), ("h", "hat", "h"), ("m", "map", "m"),
            ("n", "nap", "n"), ("ŋ", "sing", "ng"), ("l", "lip", "l"), ("r", "red", "r"),
            ("j", "yes", "y"), ("w", "we", "w"), ("tʃ", "church", "ch"), ("dʒ", "judge", "j"),
            ("i", "beet", "ee"), ("ɪ", "bit", "i"), ("eɪ", "bait", "ai"), ("ɛ", "bed", "e"),
            ("æ", "cat", "a"), ("ɑ", "father", "a"), ("ɒ", "pot", "o"), ("ɔ", "saw", "aw"),
            ("oʊ", "go", "o"), ("ʊ", "book", "oo"), ("u", "food", "oo"), ("ʌ", "cup", "u"),
            ("ə", "about", "a"), ("ɜ", "nurse", "ur"), ("ɚ", "butter", "er"), ("aɪ", "bite", "i"),
            ("aʊ", "bout", "ou"), ("ɔɪ", "boy", "oy")
        ]
        columns = 6
        for index, key in enumerate(self.ipa_keys):
            ipa_symbol, eng_word, highlight = key
            key_frame = tk.Frame(keys_frame, bd=1, relief="raised",
                                 padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label = tk.Label(key_frame, text=ipa_symbol, font=("Arial", int(self.base_ipa_font_size * self.scale)))
            ipa_label.pack()
            eng_display = invert_bold(eng_word, highlight)
            eng_label = tk.Label(key_frame, text=eng_display, font=("Arial", int(self.base_eng_font_size * self.scale)))
            eng_label.pack()
            # Bind click events: add IPA symbol to both displays.
            key_frame.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            ipa_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            eng_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            row = index // columns
            col = index % columns
            key_frame.grid(row=row, column=col, padx=3, pady=3)
            self.ipa_key_widgets.append((key_frame, ipa_label, eng_label))

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.last_x, self.last_y = event.x, event.y

    def on_move_press(self, event):
        x, y = event.x, event.y
        self.canvas.create_line(self.last_x, self.last_y, x, y, width=3, fill="black",
                                  capstyle=tk.ROUND, smooth=True)
        self.last_x, self.last_y = x, y

    def on_button_release(self, event):
        self.last_x, self.last_y = None, None

    def add_ipa(self, sym):
        current = self.ipa_display.cget("text")
        new_text = current + sym
        self.ipa_display.config(text=new_text)
        self.ipa_display_copy.config(text=new_text)

    def clear_ipa(self):
        self.ipa_display.config(text="")
        self.ipa_display_copy.config(text="")

    def zoom_in(self):
        self.scale *= 1.1
        self.update_scale()

    def zoom_out(self):
        self.scale /= 1.1
        self.update_scale()

    def update_scale(self):
        new_width = int(self.base_window_width * self.scale)
        new_height = int(self.base_window_height * self.scale)
        self.geometry(f"{new_width}x{new_height}")
        self.canvas.config(width=int(self.base_canvas_width * self.scale),
                           height=int(self.base_canvas_height * self.scale))
        self.ipa_display.config(width=int(30 * self.scale))
        self.ipa_display_copy.config(width=int(30 * self.scale))
        for key_frame, ipa_label, eng_label in self.ipa_key_widgets:
            key_frame.config(padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label.config(font=("Arial", int(self.base_ipa_font_size * self.scale)))
            eng_label.config(font=("Arial", int(self.base_eng_font_size * self.scale)))

    def type_changed(self, *args):
        if self.type_var.get() == "Letter":
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.config(state="disabled")
        else:
            self.meaning_entry.config(state="normal")

    def save_symbol(self):
        timestamp = int(time.time() * 1000)
        filename = f"character_{timestamp}.png"
        filepath = os.path.join("characters", filename)
        if not os.path.exists("characters"):
            os.makedirs("characters")
        try:
            ps = self.canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img = img.convert("RGBA")
            img.save(filepath, "png")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {e}")
            return
        meta = {
            "type": self.type_var.get(),
            "sound": self.ipa_display.cget("text"),
            "meaning": self.meaning_entry.get() if self.type_var.get() != "Letter" else ""
        }
        self.master.metadata[filename] = meta
        self.master.save_metadata()
        messagebox.showinfo("Saved", "Symbol saved successfully!")
        self.destroy()

# EditSymbolWindow allows editing an existing symbol.
class EditSymbolWindow(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.title("Edit Symbol")
        self.filename = filename
        self.characters_folder = master.characters_folder
        self.base_window_width = 500
        self.base_window_height = 950
        self.base_canvas_width = 400
        self.base_canvas_height = 400
        self.base_ipa_font_size = 16
        self.base_eng_font_size = 10
        self.scale = 1.0
        self.geometry(f"{self.base_window_width}x{self.base_window_height}")
        self.last_x, self.last_y = None, None
        self.ipa_key_widgets = []
        self.create_widgets()
        self.bind_events()
        self.load_existing_data()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        self.creation_frame = tk.Frame(self.notebook)
        self.notebook.add(self.creation_frame, text="Edit")
        self.keyboard_tab = tk.Frame(self.notebook)
        self.notebook.add(self.keyboard_tab, text="IPA Keyboard")

        zoom_frame = tk.Frame(self.creation_frame)
        zoom_frame.pack(pady=5)
        zoom_in_btn = tk.Button(zoom_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        zoom_out_btn = tk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.creation_frame, bg="white",
                                width=int(self.base_canvas_width * self.scale),
                                height=int(self.base_canvas_height * self.scale))
        self.canvas.pack(pady=10)
        self.clear_canvas_btn = tk.Button(self.creation_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_canvas_btn.pack(pady=5)

        tk.Label(self.creation_frame, text="Select Type:").pack()
        self.type_var = tk.StringVar(value="Character")
        self.type_menu = tk.OptionMenu(self.creation_frame, self.type_var, "Character", "Letter", "Both")
        self.type_menu.pack()
        self.type_var.trace("w", self.type_changed)

        tk.Label(self.creation_frame, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display = tk.Label(self.creation_frame, text="", relief="sunken",
                                    width=int(30 * self.scale), anchor="w")
        self.ipa_display.pack(pady=5)
        self.clear_ipa_btn = tk.Button(self.creation_frame, text="Clear IPA", command=self.clear_ipa)
        self.clear_ipa_btn.pack(pady=5)

        tk.Label(self.creation_frame, text="Meaning:").pack(pady=(10, 0))
        self.meaning_entry = tk.Entry(self.creation_frame)
        self.meaning_entry.pack()

        self.save_button = tk.Button(self.creation_frame, text="Save Changes", command=self.save_changes)
        self.save_button.pack(pady=10)

        # --- IPA Keyboard Tab ---
        tk.Label(self.keyboard_tab, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display_copy = tk.Label(self.keyboard_tab, text="", relief="sunken",
                                         width=int(30 * self.scale), anchor="w")
        self.ipa_display_copy.pack(pady=5)
        keys_frame = tk.Frame(self.keyboard_tab)
        keys_frame.pack(pady=5)
        self.ipa_keys = [
            ("p", "pea", "p"), ("b", "bee", "b"), ("t", "tea", "t"), ("d", "deed", "d"),
            ("k", "key", "k"), ("g", "geese", "g"), ("f", "fee", "f"), ("v", "vee", "v"),
            ("θ", "thing", "th"), ("ð", "this", "th"), ("s", "see", "s"), ("z", "zebra", "z"),
            ("ʃ", "she", "sh"), ("ʒ", "vision", "sion"), ("h", "hat", "h"), ("m", "map", "m"),
            ("n", "nap", "n"), ("ŋ", "sing", "ng"), ("l", "lip", "l"), ("r", "red", "r"),
            ("j", "yes", "y"), ("w", "we", "w"), ("tʃ", "church", "ch"), ("dʒ", "judge", "j"),
            ("i", "beet", "ee"), ("ɪ", "bit", "i"), ("eɪ", "bait", "ai"), ("ɛ", "bed", "e"),
            ("æ", "cat", "a"), ("ɑ", "father", "a"), ("ɒ", "pot", "o"), ("ɔ", "saw", "aw"),
            ("oʊ", "go", "o"), ("ʊ", "book", "oo"), ("u", "food", "oo"), ("ʌ", "cup", "u"),
            ("ə", "about", "a"), ("ɜ", "nurse", "ur"), ("ɚ", "butter", "er"), ("aɪ", "bite", "i"),
            ("aʊ", "bout", "ou"), ("ɔɪ", "boy", "oy")
        ]
        columns = 6
        for index, key in enumerate(self.ipa_keys):
            ipa_symbol, eng_word, highlight = key
            key_frame = tk.Frame(keys_frame, bd=1, relief="raised",
                                 padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label = tk.Label(key_frame, text=ipa_symbol, font=("Arial", int(self.base_ipa_font_size * self.scale)))
            ipa_label.pack()
            eng_display = invert_bold(eng_word, highlight)
            eng_label = tk.Label(key_frame, text=eng_display, font=("Arial", int(self.base_eng_font_size * self.scale)))
            eng_label.pack()
            key_frame.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            ipa_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            eng_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            row = index // columns
            col = index % columns
            key_frame.grid(row=row, column=col, padx=3, pady=3)
            self.ipa_key_widgets.append((key_frame, ipa_label, eng_label))

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.last_x, self.last_y = event.x, event.y

    def on_move_press(self, event):
        x, y = event.x, event.y
        self.canvas.create_line(self.last_x, self.last_y, x, y, width=3, fill="black",
                                  capstyle=tk.ROUND, smooth=True)
        self.last_x, self.last_y = x, y

    def on_button_release(self, event):
        self.last_x, self.last_y = None, None

    def add_ipa(self, sym):
        current = self.ipa_display.cget("text")
        new_text = current + sym
        self.ipa_display.config(text=new_text)
        self.ipa_display_copy.config(text=new_text)

    def clear_ipa(self):
        self.ipa_display.config(text="")
        self.ipa_display_copy.config(text="")

    def clear_canvas(self):
        self.canvas.delete("all")

    def zoom_in(self):
        self.scale *= 1.1
        self.update_scale()

    def zoom_out(self):
        self.scale /= 1.1
        self.update_scale()

    def update_scale(self):
        new_width = int(self.base_window_width * self.scale)
        new_height = int(self.base_window_height * self.scale)
        self.geometry(f"{new_width}x{new_height}")
        self.canvas.config(width=int(self.base_canvas_width * self.scale),
                           height=int(self.base_canvas_height * self.scale))
        self.ipa_display.config(width=int(30 * self.scale))
        self.ipa_display_copy.config(width=int(30 * self.scale))
        for key_frame, ipa_label, eng_label in self.ipa_key_widgets:
            key_frame.config(padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label.config(font=("Arial", int(self.base_ipa_font_size * self.scale)))
            eng_label.config(font=("Arial", int(self.base_eng_font_size * self.scale)))

    def type_changed(self, *args):
        if self.type_var.get() == "Letter":
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.config(state="disabled")
        else:
            self.meaning_entry.config(state="normal")

    def save_symbol(self):
        timestamp = int(time.time() * 1000)
        filename = f"character_{timestamp}.png"
        filepath = os.path.join("characters", filename)
        if not os.path.exists("characters"):
            os.makedirs("characters")
        try:
            ps = self.canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img = img.convert("RGBA")
            img.save(filepath, "png")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {e}")
            return
        meta = {
            "type": self.type_var.get(),
            "sound": self.ipa_display.cget("text"),
            "meaning": self.meaning_entry.get() if self.type_var.get() != "Letter" else ""
        }
        self.master.metadata[filename] = meta
        self.master.save_metadata()
        messagebox.showinfo("Saved", "Symbol saved successfully!")
        self.destroy()

# EditSymbolWindow allows editing an existing symbol.
class EditSymbolWindow(tk.Toplevel):
    def __init__(self, master, filename):
        super().__init__(master)
        self.title("Edit Symbol")
        self.filename = filename
        self.characters_folder = master.characters_folder
        self.base_window_width = 500
        self.base_window_height = 950
        self.base_canvas_width = 400
        self.base_canvas_height = 400
        self.base_ipa_font_size = 16
        self.base_eng_font_size = 10
        self.scale = 1.0
        self.geometry(f"{self.base_window_width}x{self.base_window_height}")
        self.last_x, self.last_y = None, None
        self.ipa_key_widgets = []
        self.create_widgets()
        self.bind_events()
        self.load_existing_data()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")
        self.creation_frame = tk.Frame(self.notebook)
        self.notebook.add(self.creation_frame, text="Edit")
        self.keyboard_tab = tk.Frame(self.notebook)
        self.notebook.add(self.keyboard_tab, text="IPA Keyboard")

        zoom_frame = tk.Frame(self.creation_frame)
        zoom_frame.pack(pady=5)
        zoom_in_btn = tk.Button(zoom_frame, text="Zoom In", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)
        zoom_out_btn = tk.Button(zoom_frame, text="Zoom Out", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=5)

        self.canvas = tk.Canvas(self.creation_frame, bg="white",
                                width=int(self.base_canvas_width * self.scale),
                                height=int(self.base_canvas_height * self.scale))
        self.canvas.pack(pady=10)
        self.clear_canvas_btn = tk.Button(self.creation_frame, text="Clear Canvas", command=self.clear_canvas)
        self.clear_canvas_btn.pack(pady=5)

        tk.Label(self.creation_frame, text="Select Type:").pack()
        self.type_var = tk.StringVar(value="Character")
        self.type_menu = tk.OptionMenu(self.creation_frame, self.type_var, "Character", "Letter", "Both")
        self.type_menu.pack()
        self.type_var.trace("w", self.type_changed)

        tk.Label(self.creation_frame, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display = tk.Label(self.creation_frame, text="", relief="sunken",
                                    width=int(30 * self.scale), anchor="w")
        self.ipa_display.pack(pady=5)
        self.clear_ipa_btn = tk.Button(self.creation_frame, text="Clear IPA", command=self.clear_ipa)
        self.clear_ipa_btn.pack(pady=5)

        tk.Label(self.creation_frame, text="Meaning:").pack(pady=(10, 0))
        self.meaning_entry = tk.Entry(self.creation_frame)
        self.meaning_entry.pack()

        self.save_button = tk.Button(self.creation_frame, text="Save Changes", command=self.save_changes)
        self.save_button.pack(pady=10)

        # --- IPA Keyboard Tab ---
        tk.Label(self.keyboard_tab, text="Pronunciation (IPA):").pack(pady=(10, 0))
        self.ipa_display_copy = tk.Label(self.keyboard_tab, text="", relief="sunken",
                                         width=int(30 * self.scale), anchor="w")
        self.ipa_display_copy.pack(pady=5)
        keys_frame = tk.Frame(self.keyboard_tab)
        keys_frame.pack(pady=5)
        self.ipa_keys = [
            ("p", "pea", "p"), ("b", "bee", "b"), ("t", "tea", "t"), ("d", "deed", "d"),
            ("k", "key", "k"), ("g", "geese", "g"), ("f", "fee", "f"), ("v", "vee", "v"),
            ("θ", "thing", "th"), ("ð", "this", "th"), ("s", "see", "s"), ("z", "zebra", "z"),
            ("ʃ", "she", "sh"), ("ʒ", "vision", "sion"), ("h", "hat", "h"), ("m", "map", "m"),
            ("n", "nap", "n"), ("ŋ", "sing", "ng"), ("l", "lip", "l"), ("r", "red", "r"),
            ("j", "yes", "y"), ("w", "we", "w"), ("tʃ", "church", "ch"), ("dʒ", "judge", "j"),
            ("i", "beet", "ee"), ("ɪ", "bit", "i"), ("eɪ", "bait", "ai"), ("ɛ", "bed", "e"),
            ("æ", "cat", "a"), ("ɑ", "father", "a"), ("ɒ", "pot", "o"), ("ɔ", "saw", "aw"),
            ("oʊ", "go", "o"), ("ʊ", "book", "oo"), ("u", "food", "oo"), ("ʌ", "cup", "u"),
            ("ə", "about", "a"), ("ɜ", "nurse", "ur"), ("ɚ", "butter", "er"), ("aɪ", "bite", "i"),
            ("aʊ", "bout", "ou"), ("ɔɪ", "boy", "oy")
        ]
        columns = 6
        for index, key in enumerate(self.ipa_keys):
            ipa_symbol, eng_word, highlight = key
            key_frame = tk.Frame(keys_frame, bd=1, relief="raised",
                                 padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label = tk.Label(key_frame, text=ipa_symbol, font=("Arial", int(self.base_ipa_font_size * self.scale)))
            ipa_label.pack()
            eng_display = invert_bold(eng_word, highlight)
            eng_label = tk.Label(key_frame, text=eng_display, font=("Arial", int(self.base_eng_font_size * self.scale)))
            eng_label.pack()
            key_frame.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            ipa_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            eng_label.bind("<Button-1>", lambda event, sym=ipa_symbol: self.add_ipa(sym))
            row = index // columns
            col = index % columns
            key_frame.grid(row=row, column=col, padx=3, pady=3)
            self.ipa_key_widgets.append((key_frame, ipa_label, eng_label))

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_existing_data(self):
        filepath = os.path.join(self.characters_folder, self.filename)
        try:
            image = Image.open(filepath)
            image.thumbnail((int(self.base_canvas_width * self.scale), int(self.base_canvas_height * self.scale)))
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading symbol image: {e}")
        meta = self.master.metadata.get(self.filename, {})
        self.type_var.set(meta.get("type", "Character"))
        self.ipa_display.config(text=meta.get("sound", ""))
        self.ipa_display_copy.config(text=meta.get("sound", ""))
        self.meaning_entry.delete(0, tk.END)
        self.meaning_entry.insert(0, meta.get("meaning", ""))

    def on_button_press(self, event):
        self.last_x, self.last_y = event.x, event.y

    def on_move_press(self, event):
        x, y = event.x, event.y
        self.canvas.create_line(self.last_x, self.last_y, x, y, width=3, fill="black",
                                  capstyle=tk.ROUND, smooth=True)
        self.last_x, self.last_y = x, y

    def on_button_release(self, event):
        self.last_x, self.last_y = None, None

    def add_ipa(self, sym):
        current = self.ipa_display.cget("text")
        new_text = current + sym
        self.ipa_display.config(text=new_text)
        self.ipa_display_copy.config(text=new_text)

    def clear_ipa(self):
        self.ipa_display.config(text="")
        self.ipa_display_copy.config(text="")

    def clear_canvas(self):
        self.canvas.delete("all")

    def zoom_in(self):
        self.scale *= 1.1
        self.update_scale()

    def zoom_out(self):
        self.scale /= 1.1
        self.update_scale()

    def update_scale(self):
        new_width = int(self.base_window_width * self.scale)
        new_height = int(self.base_window_height * self.scale)
        self.geometry(f"{new_width}x{new_height}")
        self.canvas.config(width=int(self.base_canvas_width * self.scale),
                           height=int(self.base_canvas_height * self.scale))
        self.ipa_display.config(width=int(30 * self.scale))
        self.ipa_display_copy.config(width=int(30 * self.scale))
        for key_frame, ipa_label, eng_label in self.ipa_key_widgets:
            key_frame.config(padx=int(5 * self.scale), pady=int(5 * self.scale))
            ipa_label.config(font=("Arial", int(self.base_ipa_font_size * self.scale)))
            eng_label.config(font=("Arial", int(self.base_eng_font_size * self.scale)))

    def type_changed(self, *args):
        if self.type_var.get() == "Letter":
            self.meaning_entry.delete(0, tk.END)
            self.meaning_entry.config(state="disabled")
        else:
            self.meaning_entry.config(state="normal")

    def save_changes(self):
        filepath = os.path.join(self.characters_folder, self.filename)
        try:
            ps = self.canvas.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img = img.convert("RGBA")
            img.save(filepath, "png")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving image: {e}")
            return
        meta = {
            "type": self.type_var.get(),
            "sound": self.ipa_display.cget("text"),
            "meaning": self.meaning_entry.get() if self.type_var.get() != "Letter" else ""
        }
        self.master.metadata[self.filename] = meta
        self.master.save_metadata()
        messagebox.showinfo("Saved", "Changes saved successfully!")
        self.destroy()

# Sentence Builder window.
class SentenceBuilderWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Sentence Builder")
        self.geometry("800x600")
        self.characters_folder = "characters"
        self.max_cols = 20  # Maximum symbols per row
        self.sentence = []  # List of PhotoImage objects for symbols in the sentence
        self.symbol_images = {}  # Mapping from filename -> small PhotoImage
        self.load_symbols()
        self.create_widgets()

    def load_symbols(self):
        files = sorted([fname for fname in os.listdir(self.characters_folder) if fname.endswith(".png")])
        for fname in files:
            path = os.path.join(self.characters_folder, fname)
            try:
                image = Image.open(path)
                image.thumbnail((40, 40))
                photo = ImageTk.PhotoImage(image)
                self.symbol_images[fname] = photo
            except Exception as e:
                print(f"Error loading symbol {fname}: {e}")

    def create_widgets(self):
        direction_frame = tk.Frame(self)
        direction_frame.pack(pady=5)
        tk.Label(direction_frame, text="Insertion Direction:").pack(side=tk.LEFT)
        self.direction_var = tk.StringVar(value="Left-to-Right")
        # When changed, re-render the sentence.
        self.direction_menu = tk.OptionMenu(direction_frame, self.direction_var, "Left-to-Right", "Right-to-Left", command=lambda _: self.render_sentence())
        self.direction_menu.pack(side=tk.LEFT)
        
        self.sentence_frame = tk.Frame(self, bg="white", width=760, height=200)
        self.sentence_frame.pack(pady=10)
        self.sentence_frame.grid_propagate(False)
        # Ensure grid columns expand evenly.
        for i in range(self.max_cols):
            self.sentence_frame.grid_columnconfigure(i, weight=1)
        
        clear_btn = tk.Button(self, text="Clear Sentence", command=self.clear_sentence)
        clear_btn.pack(pady=5)
        
        self.keyboard_frame = tk.Frame(self)
        self.keyboard_frame.pack(pady=10)
        self.populate_keyboard()

    def populate_keyboard(self):
        col = 0
        row = 0
        for fname, photo in self.symbol_images.items():
            btn = tk.Button(self.keyboard_frame, image=photo, command=lambda fname=fname: self.add_symbol(fname))
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col >= 10:
                col = 0
                row += 1

    def add_symbol(self, fname):
        photo = self.symbol_images.get(fname)
        # If Right-to-Left is selected, insert the new symbol at the beginning; otherwise, append.
        if self.direction_var.get() == "Right-to-Left":
            self.sentence.insert(0, photo)
        else:
            self.sentence.append(photo)
        self.render_sentence()

    def render_sentence(self):
        for widget in self.sentence_frame.winfo_children():
            widget.destroy()
        if self.direction_var.get() == "Left-to-Right":
            for index, photo in enumerate(self.sentence):
                row = index // self.max_cols
                col = index % self.max_cols
                lbl = tk.Label(self.sentence_frame, image=photo, bg="white")
                lbl.grid(row=row, column=col, padx=2, pady=2, sticky="e")
        else:
            # For Right-to-Left, place symbols in order so that the first symbol is at the far right.
            for index, photo in enumerate(self.sentence):
                row = index // self.max_cols
                # Calculate column so that symbols appear flush right.
                col = (self.max_cols - 1) - (index % self.max_cols)
                lbl = tk.Label(self.sentence_frame, image=photo, bg="white")
                lbl.grid(row=row, column=col, padx=2, pady=2, sticky="e")
        for i in range(self.max_cols):
            self.sentence_frame.grid_columnconfigure(i, weight=1)

    def clear_sentence(self):
        self.sentence = []
        self.render_sentence()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
