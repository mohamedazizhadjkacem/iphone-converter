import io
import subprocess
import tempfile
import zipfile
from pathlib import Path

import pillow_heif
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="iConvert — iPhone to Windows",
    page_icon="📲",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Outfit', sans-serif !important; background: #080b14 !important; color: #e2e8f0 !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stHeader"]     { display: none !important; }
[data-testid="stToolbar"]    { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.main .block-container { padding-top: 2rem !important; padding-bottom: 4rem !important; padding-left: 2rem !important; padding-right: 2rem !important; max-width: 1200px !important; }
.stApp::before { content:''; position:fixed; inset:0; pointer-events:none; z-index:0; background: radial-gradient(ellipse 70% 45% at 15% 0%, rgba(56,189,248,0.06) 0%, transparent 60%), radial-gradient(ellipse 55% 40% at 85% 100%, rgba(99,102,241,0.06) 0%, transparent 60%); }
.iconvert-header { text-align:center; padding:1rem 0 2.5rem; }
.logo-pill { display:inline-flex; align-items:center; gap:8px; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.2); border-radius:100px; padding:5px 16px; font-size:0.72rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#38bdf8; margin-bottom:1.2rem; }
.iconvert-header h1 { font-size:clamp(2rem,4vw,3.2rem); font-weight:800; letter-spacing:-1.5px; line-height:1.1; color:#f8fafc; margin-bottom:0.7rem; }
.iconvert-header h1 span { background:linear-gradient(135deg,#38bdf8,#818cf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.iconvert-header p { font-size:1rem; color:#64748b; max-width:440px; margin:0 auto 1.2rem; line-height:1.6; }
.fmt-row { display:flex; justify-content:center; gap:6px; flex-wrap:wrap; }
.fmt-chip { background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:3px 11px; font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#94a3b8; }
.fmt-chip.arrow { background:none; border:none; color:#38bdf8; font-size:1rem; padding:0 2px; }
.step-card { background:rgba(15,23,42,0.9); border:1px solid rgba(255,255,255,0.07); border-radius:16px; padding:1.6rem 1.2rem; text-align:center; height:100%; min-height:180px; }
.step-num { font-size:0.65rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#38bdf8; margin-bottom:0.7rem; }
.step-icon { font-size:1.8rem; margin-bottom:0.6rem; }
.step-title { font-size:0.95rem; font-weight:700; color:#f1f5f9; margin-bottom:0.35rem; }
.step-desc { font-size:0.78rem; color:#475569; line-height:1.5; }
.upload-card-label { font-size:0.65rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#38bdf8; margin-bottom:0.5rem; }
div[data-testid="stFileUploader"] { background:rgba(15,23,42,0.9) !important; border:1px solid rgba(56,189,248,0.25) !important; border-radius:16px !important; padding:1rem !important; }
div[data-testid="stFileUploader"]:hover { border-color:rgba(56,189,248,0.5) !important; }
div[data-testid="stFileDropzone"] { background:rgba(56,189,248,0.03) !important; border:2px dashed rgba(56,189,248,0.2) !important; border-radius:10px !important; }
.section-lbl { font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#334155; margin:1.4rem 0 0.7rem; display:flex; align-items:center; gap:8px; }
.section-lbl::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.05); }
.file-item { display:flex; align-items:center; gap:10px; padding:0.75rem 0.9rem; background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.05); border-radius:10px; margin-bottom:7px; }
.ficon { width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:1rem; flex-shrink:0; }
.ficon-photo   { background:rgba(56,189,248,0.12); }
.ficon-video   { background:rgba(129,140,248,0.12); }
.ficon-unknown { background:rgba(239,68,68,0.1); }
.fname { font-size:0.88rem; font-weight:500; color:#e2e8f0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; min-width:0; }
.fmeta { font-size:0.7rem; color:#475569; font-family:'JetBrains Mono',monospace; }
.fbadge { font-size:0.62rem; font-weight:700; letter-spacing:0.07em; padding:3px 8px; border-radius:5px; flex-shrink:0; }
.bp { background:rgba(56,189,248,0.1);  color:#38bdf8; }
.bv { background:rgba(129,140,248,0.1); color:#818cf8; }
.bu { background:rgba(239,68,68,0.1);   color:#f87171; }
.bo { background:rgba(34,197,94,0.1);   color:#4ade80; }
.bf { background:rgba(239,68,68,0.1);   color:#f87171; }
.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:1.2rem 0; }
.stat-box { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:1rem; text-align:center; }
.snum { font-size:2rem; font-weight:800; line-height:1; margin-bottom:3px; }
.slbl { font-size:0.65rem; font-weight:600; letter-spacing:0.09em; text-transform:uppercase; color:#475569; }
.sc-blue   { color:#38bdf8; }
.sc-violet { color:#818cf8; }
.sc-white  { color:#f1f5f9; }
div[data-testid="stButton"] > button { width:100% !important; background:linear-gradient(135deg,#0ea5e9,#6366f1) !important; color:#fff !important; font-family:'Outfit',sans-serif !important; font-size:1rem !important; font-weight:700 !important; border:none !important; border-radius:12px !important; padding:0.8rem 2rem !important; box-shadow:0 4px 24px rgba(14,165,233,0.22) !important; margin-top:0.8rem !important; }
div[data-testid="stButton"] > button:hover { opacity:0.88 !important; }
div[data-testid="stDownloadButton"] > button { background:rgba(255,255,255,0.05) !important; color:#e2e8f0 !important; border:1px solid rgba(255,255,255,0.1) !important; font-family:'Outfit',sans-serif !important; font-size:0.8rem !important; font-weight:600 !important; border-radius:8px !important; width:100% !important; }
div[data-testid="stDownloadButton"] > button:hover { background:rgba(255,255,255,0.09) !important; }
.res-item { display:flex; align-items:center; gap:10px; padding:0.75rem 0.9rem; border-radius:10px; margin-bottom:7px; border:1px solid; }
.res-ok   { background:rgba(34,197,94,0.04);  border-color:rgba(34,197,94,0.15); }
.res-fail { background:rgba(239,68,68,0.04);  border-color:rgba(239,68,68,0.15); }
.res-dest { font-size:0.78rem; color:#4ade80; font-family:'JetBrains Mono',monospace; }
.res-err  { font-size:0.72rem; color:#f87171; font-family:'JetBrains Mono',monospace; }
.ok-banner { background:rgba(34,197,94,0.06); border:1px solid rgba(34,197,94,0.18); border-radius:12px; padding:1rem 1.4rem; display:flex; align-items:center; gap:12px; margin-bottom:1rem; }
.okt { font-size:0.95rem; font-weight:700; color:#4ade80; }
.oks { font-size:0.78rem; color:#475569; margin-top:2px; }
.hdiv { border:none; border-top:1px solid rgba(255,255,255,0.05); margin:1.2rem 0; }
.zip-btn div[data-testid="stDownloadButton"] > button { background:linear-gradient(135deg,rgba(14,165,233,0.15),rgba(99,102,241,0.15)) !important; border-color:rgba(56,189,248,0.3) !important; color:#38bdf8 !important; font-size:0.95rem !important; padding:0.7rem !important; border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

PHOTO_EXTENSIONS = {".heic",".heif",".jpg",".jpeg",".png",".bmp",".tiff",".webp"}
VIDEO_EXTENSIONS = {".mov",".mp4",".avi",".mkv",".m4v",".3gp"}
VIDEO_CRF = 18
pillow_heif.register_heif_opener()

def fmt_size(b):
    return f"{b/1024:.0f} KB" if b < 1024*1024 else f"{b/1024/1024:.1f} MB"

def convert_photo_bytes(file_bytes, filename):
    suffix = Path(filename).suffix.lower()
    if suffix in {".heic",".heif"}:
        hf = pillow_heif.read_heif(file_bytes)
        img = Image.frombytes("RGB", hf.size, hf.data, "raw", hf.mode)
    else:
        img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as ti:
        img.save(ti.name, "PNG", icc_profile=None); tip = ti.name
    with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as to:
        top = to.name
    r = subprocess.run(["ffmpeg","-y","-i",tip,"-vf","scale=iw:ih","-pix_fmt","yuvj420p","-q:v","2","-map_metadata","-1",top], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    Path(tip).unlink(missing_ok=True)
    if r.returncode != 0:
        Path(top).unlink(missing_ok=True)
        raise RuntimeError(r.stderr.decode()[-300:])
    data = Path(top).read_bytes(); Path(top).unlink(missing_ok=True)
    return data

def convert_video_bytes(file_bytes, filename):
    suffix = Path(filename).suffix.lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as ti:
        ti.write(file_bytes); tip = ti.name
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as to:
        top = to.name
    r = subprocess.run(["ffmpeg","-y","-i",tip,"-c:v","libx264","-crf",str(VIDEO_CRF),"-preset","medium","-c:a","aac","-b:a","192k","-movflags","+faststart","-map_metadata","-1",top], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    Path(tip).unlink(missing_ok=True)
    if r.returncode != 0:
        Path(top).unlink(missing_ok=True)
        raise RuntimeError(r.stderr.decode()[-300:])
    data = Path(top).read_bytes(); Path(top).unlink(missing_ok=True)
    return data

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="iconvert-header">
    <div class="logo-pill">📲 &nbsp;iConvert</div>
    <h1>iPhone files,<br><span>ready for Windows</span></h1>
    <p>Drop your HEIC photos and MOV videos — get back JPEGs and MP4s that open anywhere on Windows.</p>
    <div class="fmt-row">
        <span class="fmt-chip">HEIC</span><span class="fmt-chip">HEIF</span><span class="fmt-chip">MOV</span>
        <span class="fmt-chip arrow">→</span>
        <span class="fmt-chip">JPEG</span><span class="fmt-chip">MP4</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 3-COLUMN ROW: step cards ──────────────────────────────────────────────────
col1, col2, col3 = st.columns(3, gap="small")

with col1:
    st.markdown('<div class="step-card"><div class="step-num">Step 01</div><div class="step-icon">📂</div><div class="step-title">Drop your files</div><div class="step-desc">Drag & drop iPhone photos or videos straight from File Explorer</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="step-card"><div class="step-num">Step 02</div><div class="step-icon">⚙️</div><div class="step-title">One click convert</div><div class="step-desc">Strips iPhone-only codecs and color profiles Windows cannot read</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="step-card"><div class="step-num">Step 03</div><div class="step-icon">💾</div><div class="step-title">Download & open</div><div class="step-desc">Clean JPEGs and MP4s — download one by one or grab a ZIP</div></div>', unsafe_allow_html=True)

# ── UPLOAD CARD — full width below the steps ──────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="upload-card-label">Your iPhone files</div>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Drop files here",
    accept_multiple_files=True,
    type=["heic","heif","jpg","jpeg","png","bmp","tiff","webp","mov","mp4","avi","mkv","m4v","3gp"],
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if not uploaded_files:
    st.markdown('<div style="text-align:center;color:#334155;font-size:0.8rem;padding:0.2rem 0 1rem;">Drag your iPhone photos and videos into the box above to get started</div>', unsafe_allow_html=True)
    st.stop()

# ── FILE LIST ─────────────────────────────────────────────────────────────────
photos  = [f for f in uploaded_files if Path(f.name).suffix.lower() in PHOTO_EXTENSIONS]
videos  = [f for f in uploaded_files if Path(f.name).suffix.lower() in VIDEO_EXTENSIONS]
unknown = [f for f in uploaded_files if f not in photos + videos]

st.markdown(f'<div class="stat-grid"><div class="stat-box"><div class="snum sc-blue">{len(photos)}</div><div class="slbl">Photos</div></div><div class="stat-box"><div class="snum sc-violet">{len(videos)}</div><div class="slbl">Videos</div></div><div class="stat-box"><div class="snum sc-white">{len(uploaded_files)}</div><div class="slbl">Total</div></div></div>', unsafe_allow_html=True)

if photos:
    st.markdown('<div class="section-lbl">Photos</div>', unsafe_allow_html=True)
    for f in photos:
        st.markdown(f'<div class="file-item"><div class="ficon ficon-photo">🖼️</div><div style="flex:1;min-width:0"><div class="fname">{f.name}</div><div class="fmeta">{fmt_size(f.size)} &nbsp;·&nbsp; → JPEG</div></div><span class="fbadge bp">PHOTO</span></div>', unsafe_allow_html=True)

if videos:
    st.markdown('<div class="section-lbl">Videos</div>', unsafe_allow_html=True)
    for f in videos:
        st.markdown(f'<div class="file-item"><div class="ficon ficon-video">🎬</div><div style="flex:1;min-width:0"><div class="fname">{f.name}</div><div class="fmeta">{fmt_size(f.size)} &nbsp;·&nbsp; → MP4</div></div><span class="fbadge bv">VIDEO</span></div>', unsafe_allow_html=True)

if unknown:
    st.markdown('<div class="section-lbl">Unrecognised</div>', unsafe_allow_html=True)
    for f in unknown:
        st.markdown(f'<div class="file-item"><div class="ficon ficon-unknown">❓</div><div style="flex:1;min-width:0"><div class="fname">{f.name}</div><div class="fmeta">Will be skipped</div></div><span class="fbadge bu">SKIP</span></div>', unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    convert = st.button("Convert all files  →", use_container_width=True)

if not convert:
    st.stop()

# ── CONVERSION ────────────────────────────────────────────────────────────────
to_convert = photos + videos
results    = {}
total      = len(to_convert)

st.markdown('<hr class="hdiv">', unsafe_allow_html=True)
st.markdown('<div class="section-lbl">Converting</div>', unsafe_allow_html=True)
progress  = st.progress(0)
status_ph = st.empty()

for i, f in enumerate(to_convert):
    is_video = Path(f.name).suffix.lower() in VIDEO_EXTENSIONS
    note     = " — may take a moment" if is_video else ""
    status_ph.markdown(f'<div style="font-size:0.82rem;color:#64748b;padding:3px 0">Converting <b style="color:#e2e8f0">{f.name}</b>{note}…</div>', unsafe_allow_html=True)
    try:
        if is_video:
            ob = convert_video_bytes(f.read(), f.name); on = Path(f.name).stem + ".mp4";  mi = "video/mp4"
        else:
            ob = convert_photo_bytes(f.read(), f.name); on = Path(f.name).stem + ".jpeg"; mi = "image/jpeg"
        results[f.name] = (on, ob, mi, "ok", "")
    except Exception as e:
        results[f.name] = (None, None, None, "error", str(e)[:120])
    progress.progress((i + 1) / total)

status_ph.empty(); progress.empty()

# ── RESULTS ───────────────────────────────────────────────────────────────────
ok_count  = sum(1 for v in results.values() if v[3] == "ok")
err_count = sum(1 for v in results.values() if v[3] == "error")

st.markdown(f'<div class="ok-banner"><div style="font-size:1.4rem">{"✅" if ok_count else "❌"}</div><div><div class="okt">{ok_count} file{"s" if ok_count!=1 else ""} converted successfully</div><div class="oks">{err_count} failed &nbsp;·&nbsp; Download files below</div></div></div>', unsafe_allow_html=True)
st.markdown('<div class="section-lbl">Your converted files</div>', unsafe_allow_html=True)

for orig, (on, ob, mi, status, err) in results.items():
    if status == "ok":
        c1, c2 = st.columns([4, 1])
        with c1:
            icon = "🎬" if mi == "video/mp4" else "🖼️"
            ic   = "ficon-video" if mi == "video/mp4" else "ficon-photo"
            st.markdown(f'<div class="res-item res-ok"><div class="ficon {ic}">{icon}</div><div style="flex:1;min-width:0"><div class="fname">{orig}</div><div class="fmeta">→ <span class="res-dest">{on}</span> &nbsp;·&nbsp; {fmt_size(len(ob))}</div></div><span class="fbadge bo">DONE</span></div>', unsafe_allow_html=True)
        with c2:
            st.download_button("⬇ Download", data=ob, file_name=on, mime=mi, key=f"dl_{orig}", use_container_width=True)
    else:
        st.markdown(f'<div class="res-item res-fail"><div class="ficon ficon-unknown">❌</div><div style="flex:1;min-width:0"><div class="fname">{orig}</div><div class="res-err">{err}</div></div><span class="fbadge bf">FAILED</span></div>', unsafe_allow_html=True)

ok_files = [(on, ob, mi) for (on, ob, mi, s, _) in results.values() if s == "ok"]
if len(ok_files) > 1:
    st.markdown('<hr class="hdiv">', unsafe_allow_html=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for on, ob, _ in ok_files:
            zf.writestr(on, ob)
    _, zc, _ = st.columns([1, 2, 1])
    with zc:
        st.markdown('<div class="zip-btn">', unsafe_allow_html=True)
        st.download_button(f"⬇  Download all {len(ok_files)} files as ZIP", data=buf.getvalue(), file_name="iphone_converted.zip", mime="application/zip", key="zip_all", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)