# 🌿 Canvas Garden 🌿
A cute, customizable tool to harvest your Canvas assignments into a cozy Excel sheet.

## ✨ For users looking to just use the gui
2. Go to the [Releases] section on the right side of this repository page.
3. Click on the latest version (it will usually be at the top).
4. Under the Assets section, click on the .zip file (or the .exe file) to download it.

## ✨ For my programmers
1. **Clone the repo** to your computer.
2. **Install requirements**: `pip install pandas requests openpyxl python-dotenv`
3. **Set up your secret garden**:
   - Create a file named `.env`.
   - Copy the contents of `.env.example` into it.
   - Add your own Canvas API Token (Found in Canvas Settings).
4. **Run the GUI**: `python gui.py`
5. **Plant your courses** by adding your Course IDs and picking your favorite colors.
6. **Harvest!** Click "Generate Excel" to see your assignments.

## 🪴 Privacy
Your API keys and Course IDs are stored locally on your machine and are never uploaded to GitHub.
