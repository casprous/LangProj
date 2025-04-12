# Using the LangProg.py Tool

In conjunction with all the linguistic design above, you can use a Python program called **LangProg.py** to draw and store custom symbol images. You can then import/export these PNG symbols to share with others or import into a font creation tool such as **FontForge**.

---

## 1. Installation and Setup

### Install Python 3
- Download and install from the official [Python website](https://www.python.org/) if you do not have it already.

### Install Ghostscript (required for converting the canvas drawings to PNG)
- Download from the official [Ghostscript website]([https://ghostscript.com/](https://www.ghostscript.com/releases/gsdnld.html)).
- After installing, ensure the Ghostscript `bin` folder is in your system’s PATH. On Windows, this might look like: C:\Program Files\gs\gs10.05.0\bin
- If needed, open **LangProg.py** in a text editor, then update the `gs_path` variable near the top of the file to match your Ghostscript install location.

### Install required Python packages
- **Pillow** (for image processing) and **Tkinter** (for GUI).
- In a terminal or command prompt, run: pip install pillow
- Tkinter is typically included with Python on Windows and macOS. On Linux, you might need to install it via your package manager, for example: sudo apt-get install python3-tk

---

## 2. Running LangProg.py

1. Place **LangProg.py** in a folder of your choice.
2. Open a terminal (or command prompt) in that folder.
3. Run: python LangProg.py
4. A window titled **"Imaginary Language Builder"** should open.

---

## 3. Creating Symbols

1. Click **“Create New Symbol.”**
2. A drawing window will appear with a canvas where you can sketch your symbol.
3. Use **Zoom In** or **Zoom Out** to change the canvas size as needed.
4. Enter details about the symbol (e.g., type: “Character,” “Letter,” or “Both”), the IPA pronunciation, and an optional meaning.
5. Click **“Save Symbol”** to store the symbol as a PNG in the **characters** folder. Related metadata (type, sound, meaning) is saved in **metadata.json**.

---

## 4. Editing Existing Symbols

1. Scroll through symbols using the **Next** or **Previous** buttons on the main screen.
2. When you find the symbol you want to update, click **“Edit Symbol.”**
3. This opens the same drawing interface, letting you redraw or annotate the symbol and update its sound or meaning.
4. Click **“Save Changes.”**

---

## 5. Exporting and Importing Symbols

- **Import Symbol**:  
If you have a PNG created in FontForge or another graphics tool, click **“Import Symbol.”** Browse to the PNG, and **LangProg.py** will add it to the **characters** folder and **metadata.json** for you to edit.

- **Export Symbol**:  
Select a symbol in **LangProg.py**, then click **“Export Symbol.”** Choose a filename and location. The resulting PNG can be loaded into FontForge or shared elsewhere.

---

## 6. Saving Symbols as PNG for FontForge

1. By default, any symbol you create or edit in **LangProg.py** is stored as a PNG in the **characters** folder.
2. To rename or move it, select the symbol in **LangProg.py** and choose **“Export Symbol.”**
3. You can then import the exported PNG into **FontForge**, mapping it to a glyph in your custom font.

---

## 7. Sentence Builder

1. To try out sentence construction, click **“Open Sentence Builder.”** on the main screen.
2. A new window shows all available symbols. You can click them to add symbols to a sentence canvas.
3. Switch direction between **Left-to-Right** or **Right-to-Left** to preview different writing directions.
4. Use **“Clear Sentence.”** to remove all symbols and start over.





