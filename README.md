# iPhone Converter (Folder Mode + Web App)

Convert iPhone photos and videos into Windows-friendly formats.

- Photos: HEIC/HEIF/JPG/PNG/BMP/TIFF/WEBP -> JPEG
- Videos: MOV/MP4/AVI/MKV/M4V/3GP -> MP4 (H.264 + AAC)

This project includes two ways to use the converter:

1. **Folder mode** with `convert.py` (drop files into `input/`, results are written to `output/`).
2. **Drag-and-drop web app** with `app.py` (upload in browser, then download converted files).

---

## Project structure

```text
iphone-converter/
|- app.py
|- convert.py
|- run.ps1
|- input/
\- output/
```

---

## Requirements

1. **Python 3.10+** installed
2. **FFmpeg** installed and available in `PATH`
3. Python packages:
   - `pillow`
   - `pillow-heif`
   - `tqdm`
   - `streamlit`

Check FFmpeg:

```powershell
ffmpeg -version
```

If PowerShell says `ffmpeg` is not recognized, install FFmpeg and add this folder to your `PATH`:

```text
C:\ffmpeg\bin
```

Temporary fix for current terminal session:

```powershell
$env:Path += ';C:\ffmpeg\bin'
```

---

## Quick start (Windows, easiest)

Run the launcher script:

```powershell
./run.ps1
```

What `run.ps1` does automatically:

1. Checks Python
2. Creates/repairs `venv`
3. Installs required Python packages
4. Ensures `input/` and `output/` folders exist
5. Checks FFmpeg
6. Starts the Streamlit web app

---

## Option A: Folder mode (`convert.py`)

Use this if you want a simple batch workflow with `input/` and `output/` folders.

### Step-by-step

1. Open terminal in project folder.
2. Create and activate a virtual environment (recommended).

```powershell
python -m venv venv --copies
./venv/Scripts/Activate.ps1
```

3. Install dependencies.

```powershell
python -m pip install --upgrade pip
python -m pip install pillow pillow-heif tqdm streamlit
```

4. Put your iPhone files inside `input/`.
   - Example: `.HEIC`, `.HEIF`, `.MOV`

5. Run the converter:

```powershell
python convert.py
```

6. Open `output/` to find converted files.

### How output naming works

1. Photos are saved as `.jpeg`.
2. Videos are saved as `.mp4`.
3. If a filename already exists, a suffix is added: `name_1.jpeg`, `name_2.jpeg`, etc.
4. If a matching converted file already exists, it is skipped.

### What the script does

1. Scans `input/`.
2. Detects photos, videos, and unknown file types.
3. Converts supported files with FFmpeg.
4. Strips metadata from outputs (`-map_metadata -1`).
5. Prints progress and summary in terminal.

### Expected result

If you place:

```text
input/IMG_9473.HEIC
input/IMG_9480.MOV
```

You should get:

```text
output/IMG_9473.jpeg
output/IMG_9480.mp4
```

---

## Option B: Web app mode (`app.py`) - drag and drop

Use this if you want a GUI in browser.

### Step-by-step

1. Open terminal in project folder.
2. Activate virtual environment.

```powershell
./venv/Scripts/Activate.ps1
```

3. Start Streamlit:

```powershell
streamlit run app.py
```

4. Open the URL shown in terminal (usually `http://localhost:8501`).
5. Drag and drop photos/videos into the upload area.
6. Click **Convert all files**.
7. Download converted files one by one, or use **Download all as ZIP**.

### Important difference vs folder mode

1. `convert.py` writes files to `output/` automatically.
2. `app.py` keeps files in memory and gives download buttons.
3. In web mode, files are saved where your browser downloads them (not automatically to `output/`).

---

## Extra method: iPhone <-> Windows transfer without iTunes/iCloud

If you want direct file transfer between your iPhone and Windows PC (both directions), you can also use a shared folder over your local network.

This section is a practical summary inspired by:

- Video: [How to Transfer Photos, Videos & Music Between iPhone & Windows PC | No iTunes or iCloud](https://www.youtube.com/watch?v=4QkmEVkMHKc)
- Creator: Kevin Stratvert

### Step-by-step

1. Create a dedicated local Windows account for sharing (recommended for security).
2. Create a folder on Windows and enable sharing permissions for that account.
3. Find your PC local IPv4 address.
4. On iPhone, open Files app and connect to the Windows shared folder (SMB).
5. Transfer files from iPhone to PC, or from PC to iPhone.

### Useful Windows commands

Create local account:

```cmd
net user "USERNAME" "PASSWORD" /add
```

Delete local account:

```cmd
net user "USERNAME" /delete
```

Find local IPv4 address:

```cmd
ipconfig | find "IPv4"
```

### Suggested SMB path from iPhone Files app

Use your PC IP or hostname in Files app > Connect to Server:

```text
smb://192.168.x.x
```

or

```text
smb://YOUR-PC-NAME
```

### Video timeline (quick navigation)

1. `00:00` Introduction
2. `00:24` Create local account in Windows
3. `01:47` Create shared folder and permissions
4. `04:05` Connect iPhone Files app to shared folder
5. `05:29` Transfer iPhone -> PC
6. `06:31` Transfer PC -> iPhone
7. `07:51` Wrap up

### Security tips

1. Use a strong password for the dedicated share account.
2. Share only one specific folder, not your entire user profile.
3. Remove sharing or delete the account when you no longer need transfer access.

---

## Supported formats

### Input photos

`heic`, `heif`, `jpg`, `jpeg`, `png`, `bmp`, `tiff`, `webp`

### Input videos

`mov`, `mp4`, `avi`, `mkv`, `m4v`, `3gp`

### Output formats

1. Photos -> `jpeg`
2. Videos -> `mp4`

---

## Troubleshooting

### 1) `ffmpeg` is not recognized

1. Confirm FFmpeg exists on disk (example: `C:\ffmpeg\bin\ffmpeg.exe`).
2. Add `C:\ffmpeg\bin` to your user/system `PATH`.
3. Restart terminal and run:

```powershell
ffmpeg -version
```

### 2) Streamlit command not found

Make sure venv is activated, then install again:

```powershell
python -m pip install streamlit
```

### 3) HEIC conversion fails

Reinstall related packages in the active environment:

```powershell
python -m pip install --upgrade pillow pillow-heif
```

### 4) Nothing happens in folder mode

1. Make sure files are in `input/` (not nested subfolders).
2. Ensure file extensions are supported.
3. Check terminal output for skipped/failed items.

---

## Notes

1. Video quality is controlled with CRF (currently `18` in code).
2. Photo conversion targets high-quality JPEG output.
3. Metadata is removed from output files.
