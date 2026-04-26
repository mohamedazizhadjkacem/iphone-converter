# ── iPhone Converter - One Click Setup & Launch ───────────────────────────────

Write-Host ""
Write-Host "==============================" -ForegroundColor DarkGray
Write-Host "  iPhone -> Windows Converter" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor DarkGray
Write-Host ""

# ── Step 1: Check Python ───────────────────────────────────────────────────────
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "      FAIL: Python not found." -ForegroundColor Red
    Write-Host "      Install it from https://python.org then re-run this script." -ForegroundColor DarkYellow
    pause
    exit 1
}
Write-Host "      OK: $pythonVersion" -ForegroundColor Green

# ── Step 2: Create virtual environment ────────────────────────────────────────
Write-Host ""
Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Yellow

# If venv exists, verify it is healthy by checking pip works inside it
if (Test-Path "venv") {
    $pipCheck = & ".\venv\Scripts\python.exe" -m pip --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      WARN: Existing venv is broken, rebuilding it..." -ForegroundColor DarkYellow
        Remove-Item -Recurse -Force venv
    }
}

if (-Not (Test-Path "venv")) {
    # --copies fixes the Python 3.13 Windows bug where venv can't find stdlib
    python -m venv venv --copies
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      FAIL: Could not create virtual environment." -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "      OK: Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "      OK: Virtual environment is healthy" -ForegroundColor Green
}

# Use venv Python directly by full path — no activation needed
$PYTHON = ".\venv\Scripts\python.exe"

# ── Step 3: Install dependencies inside venv ──────────────────────────────────
Write-Host ""
Write-Host "[3/5] Checking dependencies..." -ForegroundColor Yellow

# Upgrade pip first to avoid outdated pip warnings
& $PYTHON -m pip install --upgrade pip --quiet 2>$null

$packages = @("pillow", "pillow-heif", "tqdm", "streamlit")
foreach ($pkg in $packages) {
    $installed = & $PYTHON -m pip show $pkg 2>$null
    if ($installed -match "Name:") {
        Write-Host "      OK: $pkg already installed" -ForegroundColor Green
    } else {
        Write-Host "      Installing $pkg..." -ForegroundColor DarkYellow
        & $PYTHON -m pip install $pkg --quiet 2>$null
        # Verify it actually installed
        $verify = & $PYTHON -m pip show $pkg 2>$null
        if ($verify -match "Name:") {
            Write-Host "      OK: $pkg installed" -ForegroundColor Green
        } else {
            Write-Host "      FAIL: Could not install $pkg" -ForegroundColor Red
            Write-Host "      Try running manually: .\venv\Scripts\python.exe -m pip install $pkg" -ForegroundColor DarkYellow
            pause
            exit 1
        }
    }
}

# ── Step 4: Create folders if missing ─────────────────────────────────────────
Write-Host ""
Write-Host "[4/5] Checking folders..." -ForegroundColor Yellow
if (-Not (Test-Path "input"))  { New-Item -ItemType Directory -Path "input"  | Out-Null }
if (-Not (Test-Path "output")) { New-Item -ItemType Directory -Path "output" | Out-Null }
Write-Host "      OK: input\ and output\ are ready" -ForegroundColor Green

# ── Step 5: Check FFmpeg ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "[5/5] Checking FFmpeg..." -ForegroundColor Yellow
ffmpeg -version 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "      FAIL: FFmpeg not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "      To install FFmpeg:" -ForegroundColor DarkYellow
    Write-Host "        1. Go to https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor DarkYellow
    Write-Host "        2. Download ffmpeg-release-essentials.zip" -ForegroundColor DarkYellow
    Write-Host "        3. Extract to C:\ffmpeg\" -ForegroundColor DarkYellow
    Write-Host "        4. Add C:\ffmpeg\bin to your system PATH" -ForegroundColor DarkYellow
    Write-Host "        5. Restart this terminal and re-run run.ps1" -ForegroundColor DarkYellow
    Write-Host ""
    pause
    exit 1
}
Write-Host "      OK: FFmpeg found" -ForegroundColor Green

# ── Check app.py exists ───────────────────────────────────────────────────────
if (-Not (Test-Path "app.py")) {
    Write-Host ""
    Write-Host "      FAIL: app.py not found in this folder!" -ForegroundColor Red
    Write-Host "      Make sure app.py is in the same folder as run.ps1" -ForegroundColor DarkYellow
    pause
    exit 1
}

# ── Launch Streamlit via venv Python directly ─────────────────────────────────
Write-Host ""
Write-Host "==============================" -ForegroundColor DarkGray
Write-Host "  All checks passed!" -ForegroundColor Green
Write-Host "  Launching web app..." -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  The app will open in your browser at:" -ForegroundColor White
Write-Host "  http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C in this terminal to stop the app." -ForegroundColor DarkGray
Write-Host ""

& $PYTHON -m streamlit run app.py