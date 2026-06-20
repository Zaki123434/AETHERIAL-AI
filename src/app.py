"""
app.py — Antarmuka Streamlit untuk Asisten Personal Multi-Mode
Desain: Aetherial AI (light mode)
Jalankan dengan: streamlit run src/app.py
"""
import sys
import os
import base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from agen import jalankan_agen
from memory import muat_memori, simpan_memori, _struktur_memori_kosong

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "assets", "aetherial-logo.png")


def _image_data_uri(path: str) -> str:
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


LOGO_DATA_URI = _image_data_uri(LOGO_PATH)

st.set_page_config(
    page_title="Aetherial AI",
    page_icon=LOGO_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)

if "chat_history"  not in st.session_state: st.session_state.chat_history  = []
if "mode_aktif"    not in st.session_state: st.session_state.mode_aktif    = "belajar"
if "mode_manual"   not in st.session_state: st.session_state.mode_manual   = False
if "memori"        not in st.session_state: st.session_state.memori        = muat_memori()
if "input_counter" not in st.session_state: st.session_state.input_counter = 0

# ─────────────────────────────────────────────
# TEMA WARNA — LIGHT MODE PERMANEN
# ─────────────────────────────────────────────
bg_main     = "#050b1a"
bg_sidebar  = "#111827"
bg_card     = "#20283a"
bg_input    = "#2d354a"
bg_user_msg = "#8186ff"
bg_ai_msg   = "#222b3d"
text_main   = "#e6e8ff"
text_sub    = "#9ca3c7"
text_user   = "#111827"
text_ai     = "#e6e8ff"
border      = "#30384d"
accent      = "#b9b7ff"
danger      = "#ffb4a9"
mode_colors = {"belajar": "#b9b7ff", "produktivitas": "#7dd3fc", "curhat": "#fca5a5"}

mode_label = {"belajar": "Belajar", "produktivitas": "Produktivitas", "curhat": "Curhat"}
mode_aktif = st.session_state.mode_aktif

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: {bg_main}; color: {text_main}; }}
  .stApp {{ background-color: {bg_main}; }}

  section[data-testid="stSidebar"] {{
    background-color: {bg_sidebar} !important;
    border-right: 1px solid {border};
  }}
  section[data-testid="stSidebar"] * {{ color: {text_main} !important; }}

  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1rem; padding-bottom: 0; }}

  .bubble-user {{
    background: {bg_user_msg}; color: {text_user};
    padding: 12px 18px; border-radius: 18px 18px 4px 18px;
    margin: 8px 0 8px 20%; max-width: 78%;
    float: right; clear: both; font-size: 0.95rem; line-height: 1.5;
  }}
  .bubble-ai {{
    background: {bg_ai_msg}; color: {text_ai};
    padding: 14px 18px; border-radius: 18px 18px 18px 4px;
    margin: 8px 20% 8px 0; max-width: 78%;
    float: left; clear: both; font-size: 0.95rem; line-height: 1.5;
    border: 1px solid {border};
  }}
  .clearfix {{ clear: both; }}
  .ai-row {{ display:flex; gap:10px; align-items:flex-start; clear:both; }}
  .ai-avatar-img {{
    width:32px; height:32px; border-radius:50%; flex-shrink:0;
    border:1px solid {border}; object-fit:cover;
  }}

  .mode-badge {{
    display: inline-block; padding: 5px 14px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600;
    background: {mode_colors.get(mode_aktif, accent)}22;
    color: {mode_colors.get(mode_aktif, accent)};
    border: 1px solid {mode_colors.get(mode_aktif, accent)}55;
  }}

  .stTextInput input {{
    background: {bg_input} !important; color: {text_main} !important;
    border: 1px solid {border} !important; border-radius: 12px !important;
    padding: 12px 16px !important; font-size: 0.95rem !important;
  }}
  .stTextInput input:focus {{ border-color: {accent} !important; box-shadow: 0 0 0 2px {accent}33 !important; }}

  .stButton > button {{
    background: {accent} !important; color: #ffffff !important;
    border: 2px solid {accent} !important; border-radius: 12px !important;
    padding: 10px 22px !important; font-weight: 600 !important; font-size: 0.9rem !important;
    min-height: 46px !important; min-width: 80px !important;
    opacity: 1 !important; visibility: visible !important;
  }}
  .stButton > button:hover {{ background: {accent}dd !important; opacity: 1 !important; }}
  .stButton > button p {{ color: #ffffff !important; }}

  section[data-testid="stSidebar"] .stButton > button {{
    background: {accent}22 !important;
    color: {accent} !important;
    border: 1px solid {accent}55 !important;
    text-align: left !important;
    font-weight: 600 !important;
  }}
  section[data-testid="stSidebar"] .stButton > button p {{ color: {accent} !important; }}
  section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {accent}44 !important;
  }}

  .riwayat-item {{
    padding: 10px 14px; border-radius: 10px; margin: 6px 0;
    font-size: 0.85rem; border: 1px solid {border};
    background: {bg_card}; color: {text_main};
  }}
  .riwayat-item.active {{ background: {accent}22; border-color: {accent}55; }}
  .riwayat-item-sub {{ font-size: 0.75rem; color: {text_sub}; margin-top: 2px; }}

  hr {{ border-color: {border} !important; margin: 12px 0 !important; }}
  .app-header {{ font-size: 1.5rem; font-weight: 700; color: {text_main}; margin-bottom: 0; display:flex; align-items:center; gap:10px; }}
  .app-header img {{ width: 32px; height: 32px; }}
  .profil-nama {{ font-size: 1rem; font-weight: 700; color: {text_main}; }}
  .profil-sub  {{ font-size: 0.78rem; color: {text_sub}; }}
  .section-label {{ font-size: 0.68rem; font-weight: 700; color: {text_sub}; letter-spacing: 1px; margin: 4px 0 6px 0; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    memori = st.session_state.memori
    nama   = memori.get("user_profile", {}).get("nama", "Pengguna")

    logo_col, brand_col = st.columns([1, 3])
    with logo_col:
        st.image(LOGO_PATH, width=54)
    with brand_col:
        st.markdown("""
        <div style="padding-top:8px">
          <div class="profil-nama">AETHERIAL AI</div>
          <div class="profil-sub">Personal Assistant</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">MODE CHAT</div>', unsafe_allow_html=True)

    for mode_key, mode_lbl in mode_label.items():
        if st.button(mode_lbl, key=f"mode_{mode_key}", use_container_width=True):
            st.session_state.mode_aktif  = mode_key
            st.session_state.mode_manual = True
            st.rerun()

    indikator_warna = "#d97706" if st.session_state.mode_manual else "#059669"
    indikator_teks  = "🔒 Mode dipilih manual" if st.session_state.mode_manual else "🤖 Mode otomatis (dari AI)"
    st.markdown(f'<div style="font-size:0.75rem;color:{indikator_warna};margin:8px 0 4px 2px">{indikator_teks}</div>', unsafe_allow_html=True)

    if st.session_state.mode_manual:
        if st.button("↩️ Kembali ke Otomatis", use_container_width=True, key="reset_auto"):
            st.session_state.mode_manual = False
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Riwayat Chat (dipindah ke sidebar) ──
    st.markdown('<div class="section-label">RIWAYAT CHAT</div>', unsafe_allow_html=True)

    chat_history    = st.session_state.memori.get("chat_history", [])
    pesan_user_list = [p for p in chat_history if p["role"] == "user"][-6:]

    if not pesan_user_list:
        st.markdown(f'<div style="font-size:0.8rem;color:{text_sub}">Belum ada riwayat percakapan.</div>', unsafe_allow_html=True)
    else:
        for i, pesan in enumerate(reversed(pesan_user_list)):
            is_last    = i == 0
            css_active = "active" if is_last else ""
            preview    = pesan["content"][:32] + "..." if len(pesan["content"]) > 32 else pesan["content"]
            waktu      = pesan.get("timestamp", "")[:10]
            status     = "Sedang aktif" if is_last else waktu
            st.markdown(f"""
            <div class="riwayat-item {css_active}">
              {preview}
              <div class="riwayat-item-sub">{status}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button(" Hapus Riwayat", use_container_width=True, key="hapus"):
        st.session_state.chat_history = []
        st.session_state.memori       = _struktur_memori_kosong()
        st.session_state.mode_manual  = False
        simpan_memori(st.session_state.memori)
        st.rerun()

# ─────────────────────────────────────────────
# KONTEN UTAMA
# ─────────────────────────────────────────────
col_title, col_badge = st.columns([2, 1])
with col_title:
    st.markdown(
        f'<div class="app-header"><img src="{LOGO_DATA_URI}">Aetherial AI</div>',
        unsafe_allow_html=True,
    )
with col_badge:
    indikator = "🔒 Manual" if st.session_state.mode_manual else "🤖 Otomatis"
    st.markdown(f"""
    <div style="text-align:right;padding-top:6px">
      <span class="mode-badge">● {mode_label.get(mode_aktif, mode_aktif)} Aktif</span><br>
      <span style="font-size:0.7rem;color:{text_sub}">{indikator}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

chat_container = st.container(height=520)
with chat_container:
    if not st.session_state.chat_history:
        st.markdown(f"""
        <div class="ai-row">
          <img src="{LOGO_DATA_URI}" class="ai-avatar-img">
          <div class="bubble-ai" style="margin-left:0">
            Halo <b>{nama}</b>! Ada yang bisa saya bantu hari ini? 😊<br><br>
            Saya bisa otomatis mendeteksi apakah kamu mau <b>belajar</b>,
            mengatur <b>produktivitas</b>, atau sekadar <b>curhat</b>.<br><br>
            <span style="font-size:0.82rem;color:{text_sub}">
              💡 Atau pilih mode sendiri lewat sidebar kiri.
            </span>
          </div>
        </div>
        <div class="clearfix"></div>
        """, unsafe_allow_html=True)
    else:
        for pesan in st.session_state.chat_history:
            if pesan["role"] == "user":
                st.markdown(f'<div class="bubble-user">{pesan["content"]}</div><div class="clearfix"></div>', unsafe_allow_html=True)
            else:
                mode_p     = pesan.get("mode", "")
                label_mode = f'<span style="font-size:0.75rem;color:{mode_colors.get(mode_p, text_sub)};font-weight:600">{mode_label.get(mode_p,"")} &nbsp;·&nbsp; </span>' if mode_p else ""
                st.markdown(f"""
                <div class="ai-row">
                  <img src="{LOGO_DATA_URI}" class="ai-avatar-img">
                  <div class="bubble-ai" style="margin-left:0">{label_mode}{pesan["content"]}</div>
                </div>
                <div class="clearfix"></div>
                """, unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        label="pesan",
        placeholder="Ketik pesan...",
        label_visibility="collapsed",
        key=f"input_chat_{st.session_state.input_counter}",
    )
with col_btn:
    kirim = st.button("➤ Kirim", key="btn_kirim")

if kirim:
    if user_input and user_input.strip():
        pesan_dikirim = user_input.strip()

        with st.spinner(" Asisten sedang mengetik, mohon tunggu..."):
            mode_pilihan = mode_aktif if st.session_state.mode_manual else None
            hasil = jalankan_agen(pesan_dikirim, mode_manual=mode_pilihan)

        st.session_state.chat_history.append({"role": "user", "content": pesan_dikirim})
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": hasil["respons"],
            "mode": hasil["mode"],
        })

        if not st.session_state.mode_manual:
            st.session_state.mode_aktif = hasil["mode"]

        st.session_state.memori = muat_memori()
        st.session_state.input_counter += 1
        st.rerun()

st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:{text_sub};margin-top:6px">Aetherial AI dapat membuat kesalahan. Pertimbangkan untuk memeriksa informasi penting.</div>', unsafe_allow_html=True)