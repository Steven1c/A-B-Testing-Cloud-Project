"""
main.py
Aplikasi Web Platform Survei & Dashboard Uji A/B (Luring vs Daring).
Mematuhi PRD (docs/prd-web.md) dan Interface Contract v1.1.
Desain UI: Modern Web Clean (Font Inter, Card Kontras Tinggi, Zero Emote Slop).
"""

import os
import sys
import time
import uuid
import random
import base64
from pathlib import Path
from typing import Dict, Any, List

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Tambahkan root path proyek ke sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.contract import ITEM_COLUMNS, PRIMARY_ITEM, MIN_N, TARGET_N, TARGET_TOTAL_N
from src.errors import DuplicateSessionError, IncompleteResponseError, InsufficientSampleError
from src.app.questions import DIMENSIONS
try:
    from src.app.db import (
        get_supabase,
        insert_response,
        fetch_scores,
        fetch_all_responses,
        fetch_all_item_scores,
        reset_database,
    )
except ImportError:
    import importlib
    import src.app.db
    importlib.reload(src.app.db)
    from src.app.db import (
        get_supabase,
        insert_response,
        fetch_scores,
        fetch_all_responses,
        fetch_all_item_scores,
        reset_database,
    )
from src.analysis.stats_engine import run_mann_whitney, describe_items
from src.analysis.simulate_data import generate_responses

# Muat environment variable
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Platform Survei dan Uji AB Pembelajaran",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ------------------------------------------------------------------------------
# Injeksi Tema UI Neumorphism Murni (Soft UI, Zero Slop)
# ------------------------------------------------------------------------------
def apply_custom_style():
    """Menginjeksi CSS Neumorphism murni dengan latar belakang tekstur kain sutra dan shadow kuat."""
    bg_path = Path(__file__).parent / "assets" / "silk_bg.png"
    silk_bg_css = ""
    if bg_path.exists():
        try:
            b64_data = base64.b64encode(bg_path.read_bytes()).decode("utf-8")
            silk_bg_css = f"""
            html, body, .stApp {{
                background-color: #f2f2f5 !important;
                background-image: 
                    linear-gradient(135deg, rgba(245, 245, 248, 0.40) 0%, rgba(238, 238, 242, 0.60) 100%),
                    url("data:image/png;base64,{b64_data}") !important;
                background-size: cover !important;
                background-position: center center !important;
                background-repeat: no-repeat !important;
                background-attachment: fixed !important;
                color: #1e293b !important;
            }}
            """
        except Exception:
            silk_bg_css = ""

    if not silk_bg_css:
        silk_bg_css = """
        html, body, .stApp {
            background-color: #f2f2f5 !important;
            background-image: 
                radial-gradient(ellipse 90% 65% at 20% 30%, rgba(255, 255, 255, 0.95) 0%, transparent 55%),
                radial-gradient(ellipse 85% 60% at 80% 75%, rgba(215, 215, 226, 0.55) 0%, transparent 60%),
                linear-gradient(135deg, #fdfdfd 0%, #f3f3f6 35%, #e7e7ed 70%, #dcdce2 100%) !important;
            background-attachment: fixed !important;
            color: #1e293b !important;
        }
        """

    st.markdown(f"<style>{silk_bg_css}</style>", unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Tipografi Inter untuk elemen konten teks */
        html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, label {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Proteksi mutlak font icon Material Streamlit agar ligatur tidak bocor menjadi teks */
        [data-testid="stIconMaterial"], 
        .material-symbols-rounded, 
        .material-icons, 
        [class*="material-icons"],
        [data-testid="stExpanderToggleIcon"] span,
        [data-baseweb="icon"] {
            font-family: "Material Symbols Rounded", "Material Icons" !important;
            font-style: normal !important;
        }

        /* Tembuskan seluruh container pembungkus bawaan Streamlit agar background sutra terlihat */
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"], 
        section[data-testid="stMain"], 
        [data-testid="stMainBlockContainer"],
        .block-container {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* 2. Sidebar Neumorphic (Kunci lebar minimal saat terbuka, resize handle disembunyikan) */
        section[data-testid="stSidebar"]:not([data-collapsed="true"]) {
            min-width: 300px !important;
            width: 310px !important;
        }

        section[data-testid="stSidebar"] {
            background: rgba(248, 248, 251, 0.90) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border-right: 1px solid rgba(220, 220, 230, 0.5) !important;
            box-shadow: 4px 0 20px rgba(180, 180, 192, 0.25) !important;
        }

        [data-testid="stSidebarResizeHandle"] {
            display: none !important;
        }

        /* 3. Card Neumorphic (Shadow Lembut Silk, Tanpa Garis Solid) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(242, 242, 245, 0.94) !important;
            backdrop-filter: blur(6px) !important;
            border: none !important;
            border-radius: 20px !important;
            box-shadow: 
                0 12px 24px rgba(180, 180, 192, 0.45),
                8px 8px 18px rgba(180, 180, 192, 0.5),
                -6px 8px 16px rgba(180, 180, 192, 0.25),
                -8px -8px 20px rgba(255, 255, 255, 0.98) !important;
            padding: 22px !important;
            margin-bottom: 20px !important;
        }

        /* 4. Expander Neumorphic */
        div[data-testid="stExpander"] {
            background: #f2f2f5 !important;
            border-radius: 18px !important;
            border: none !important;
            box-shadow: 
                0 10px 20px rgba(180, 180, 192, 0.4),
                6px 6px 14px rgba(180, 180, 192, 0.45),
                -5px 6px 12px rgba(180, 180, 192, 0.2),
                -6px -6px 16px rgba(255, 255, 255, 0.98) !important;
            margin-bottom: 16px !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] details {
            border: none !important;
        }

        div[data-testid="stExpander"] summary {
            background: #f2f2f5 !important;
            border: none !important;
            font-weight: 600 !important;
            color: #0f172a !important;
            padding: 14px 20px !important;
        }

        /* 5. Metric KPI Cards Neumorphic (Tinggi Seragam, Vertikal Rata Tengah) */
        div[data-testid="stColumn"] {
            display: flex !important;
            flex-direction: column !important;
        }

        div[data-testid="stColumn"] > div {
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 auto !important;
        }

        div[data-testid="stMetric"] {
            background: #f2f2f5 !important;
            border-radius: 18px !important;
            border: none !important;
            box-shadow: 
                0 10px 20px rgba(180, 180, 192, 0.4),
                6px 6px 14px rgba(180, 180, 192, 0.45),
                -5px 6px 12px rgba(180, 180, 192, 0.2),
                -6px -6px 16px rgba(255, 255, 255, 0.98) !important;
            padding: 16px 20px !important;
            min-height: 95px !important;
            height: 100% !important;
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #475569 !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-weight: 700 !important;
            font-size: 1.55rem !important;
            line-height: 1.2 !important;
        }

        /* 6. Tombol Reguler Neumorphic */
        div.stButton > button {
            background: #f2f2f5 !important;
            color: #1e293b !important;
            border: none !important;
            border-radius: 14px !important;
            box-shadow: 
                5px 5px 12px rgba(180, 180, 192, 0.45),
                -5px -5px 12px rgba(255, 255, 255, 0.98) !important;
            font-weight: 600 !important;
            padding: 10px 22px !important;
            transition: all 0.15s ease-in-out !important;
        }

        div.stButton > button:hover {
            color: #4f46e5 !important;
            box-shadow: 
                3px 3px 8px rgba(180, 180, 192, 0.45),
                -3px -3px 8px rgba(255, 255, 255, 0.98) !important;
        }

        div.stButton > button:active {
            box-shadow: 
                inset 3px 3px 6px rgba(180, 180, 192, 0.45),
                inset -3px -3px 6px rgba(255, 255, 255, 0.98) !important;
        }

        /* 7. Tombol Aksi Utama (Accent Neumorphic) */
        div.stButton > button[kind="primary"] {
            background: #4f46e5 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 14px !important;
            box-shadow: 
                5px 5px 14px rgba(79, 70, 229, 0.35),
                -3px -3px 10px rgba(255, 255, 255, 0.9) !important;
            font-weight: 600 !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: #4338ca !important;
            box-shadow: 
                3px 3px 10px rgba(79, 70, 229, 0.45),
                -2px -2px 8px rgba(255, 255, 255, 0.9) !important;
            color: #ffffff !important;
        }

        div.stButton > button[kind="primary"]:active {
            box-shadow: 
                inset 3px 3px 8px rgba(49, 46, 129, 0.6) !important;
        }

        /* 8. Radio Button Likert Options (Neumorphic Chips) */
        div[role="radiogroup"] {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding: 8px 0;
        }

        div[role="radiogroup"] > label {
            background: #f2f2f5 !important;
            border-radius: 14px !important;
            padding: 10px 18px !important;
            border: none !important;
            box-shadow: 
                4px 4px 10px rgba(180, 180, 192, 0.45),
                -4px -4px 10px rgba(255, 255, 255, 0.98) !important;
            transition: all 0.15s ease !important;
            cursor: pointer !important;
            color: #1e293b !important;
            font-size: 0.9rem !important;
        }

        div[role="radiogroup"] > label:hover {
            color: #4f46e5 !important;
            box-shadow: 
                2px 2px 6px rgba(180, 180, 192, 0.45),
                -2px -2px 6px rgba(255, 255, 255, 0.98) !important;
        }

        /* 9. Input Fields (Sunken Neumorphic) */
        div[data-baseweb="input"] {
            background-color: #eeeff3 !important;
            border-radius: 14px !important;
            border: none !important;
            box-shadow: 
                inset 4px 4px 8px rgba(180, 180, 192, 0.4),
                inset -4px -4px 8px rgba(255, 255, 255, 0.98) !important;
        }

        input[type="password"], input[type="text"] {
            background-color: transparent !important;
            color: #0f172a !important;
            font-weight: 500 !important;
        }

        /* 10. Alert Boxes Neumorphic */
        div[data-testid="stAlert"] {
            background: #f2f2f5 !important;
            border-radius: 16px !important;
            border: none !important;
            box-shadow: 
                0 8px 18px rgba(180, 180, 192, 0.35),
                5px 5px 12px rgba(180, 180, 192, 0.4),
                -5px -5px 14px rgba(255, 255, 255, 0.98) !important;
            padding: 16px !important;
        }

        /* 11. Progress Bar Hijau (Sunken Track + Elevated Bar) */
        div[data-testid="stProgress"] {
            margin: 14px 0 !important;
        }

        div[data-testid="stProgress"] p, div[data-testid="stProgress"] span {
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }

        div[data-testid="stProgressBarTrack"] {
            background-color: #dcdcdf !important;
            border-radius: 12px !important;
            height: 16px !important;
            padding: 0 !important;
            border: none !important;
            box-shadow: 
                inset 2px 2px 5px rgba(180, 180, 192, 0.45),
                inset -2px -2px 5px rgba(255, 255, 255, 0.95) !important;
            overflow: hidden !important;
        }

        /* HANYA fill bar langsung (child pertama dari stProgressBarTrack) */
        div[data-testid="stProgressBarTrack"] > div {
            background-color: #10b981 !important;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
            border-radius: 10px !important;
            height: 100% !important;
            box-shadow: none !important;
        }

        /* 12. Tabs Neumorphic */
        button[data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 12px !important;
            padding: 8px 18px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            border: none !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: #f2f2f5 !important;
            border: none !important;
            color: #4f46e5 !important;
            box-shadow: 
                inset 3px 3px 6px rgba(180, 180, 192, 0.4),
                inset -3px -3px 6px rgba(255, 255, 255, 0.98) !important;
        }

        /* Clean Neumorphic Badge */
        .clean-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 10px;
            background: #f2f2f5;
            border: none;
            box-shadow: 
                3px 3px 7px rgba(180, 180, 192, 0.4),
                -3px -3px 7px rgba(255, 255, 255, 0.98);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: #4f46e5;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Terapkan styling
apply_custom_style()

# ------------------------------------------------------------------------------
# Inisialisasi Session State
# ------------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4().hex[:16]
if "variant" not in st.session_state:
    st.session_state["variant"] = random.choice(["A", "B"])
if "step" not in st.session_state:
    st.session_state["step"] = "scenario"
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "answers" not in st.session_state:
    st.session_state["answers"] = {}
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "last_result_time" not in st.session_state:
    st.session_state["last_result_time"] = 0
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False


# ------------------------------------------------------------------------------
# Navigasi Sidebar
# ------------------------------------------------------------------------------
st.sidebar.markdown('<span class="clean-badge">NAVIGASI SISTEM</span>', unsafe_allow_html=True)
st.sidebar.title(":material/tune: Platform A/B Testing")
menu = st.sidebar.radio(
    "Menu:",
    ["Formulir Survei", "Dashboard Analisis"],
    format_func=lambda x: f":material/assignment: {x}" if "Formulir" in x else f":material/query_stats: {x}",
)

# Panel Akun Admin & Tombol Sign Out
if st.session_state.get("admin_logged_in", False):
    st.sidebar.markdown("---")
    with st.sidebar.expander(":material/verified_user: Status Admin", expanded=True):
        st.write("Masuk sebagai: **Dosen / Admin**")
        if st.button("Keluar (Sign Out)", icon=":material/logout:", use_container_width=True):
            st.session_state["admin_logged_in"] = False
            st.toast("Berhasil keluar dari sesi admin.")
            st.rerun()


# ------------------------------------------------------------------------------
# AREA 1: FORMULIR SURVEI PUBLIK
# ------------------------------------------------------------------------------
if menu == "Formulir Survei":
    variant = st.session_state["variant"]
    variant_label = "Pembelajaran Luring (Tatap Muka)" if variant == "A" else "Pembelajaran Daring (Online LMS & Video)"

    # Sub-view A: Halaman Terima Kasih
    if st.session_state["submitted"]:
        st.markdown('<span class="clean-badge">STATUS PENGIRIMAN</span>', unsafe_allow_html=True)
        st.success("Jawaban survei tersimpan di database.")

        with st.container(border=True):
            st.markdown("### Ringkasan Sesi")
            st.write(f"- ID Sesi: `{st.session_state['session_id']}`")
            st.write(f"- Metode Dinilai: **{variant_label}**")
            q1_score = st.session_state["answers"].get(PRIMARY_ITEM, "-")
            st.write(f"- Skor Kepuasan Keseluruhan (Q1): `{q1_score} / 5`")
            st.caption("Data tersimpan anonim tanpa identitas pribadi untuk evaluasi statistik eksperimen.")

        st.markdown("")
        if st.button("Mulai Sesi Baru", type="primary", icon=":material/refresh:"):
            st.session_state["session_id"] = uuid.uuid4().hex[:16]
            st.session_state["variant"] = random.choice(["A", "B"])
            st.session_state["step"] = "scenario"
            st.session_state["submitted"] = False
            st.session_state["answers"] = {}
            st.rerun()

    # Sub-view B: Step 1 — Halaman Stimulus Skenario
    elif st.session_state["step"] == "scenario":
        st.markdown('<span class="clean-badge">TAHAP 1 DARI 2: SKENARIO</span>', unsafe_allow_html=True)
        st.title(":material/menu_book: Survei Kepuasan Pembelajaran")
        st.write("Perhatikan konteks metode pembelajaran yang Anda terima berikut ini:")

        if variant == "A":
            st.markdown("### Varian A: Pembelajaran Luring (Tatap Muka)")
            st.info(
                """
                **Konteks Skenario: Pembelajaran Luring (Tatap Muka di Kampus)**
                * Perkuliahan berlangsung tatap muka langsung di ruang kelas kampus sesuai jadwal tetap.
                * Materi disampaikan via papan tulis dan proyektor dengan diskusi fisik bersama dosen dan rekan mahasiswa.
                * Presensi, tanya jawab, pengerjaan tugas, dan evaluasi berlangsung di ruang kelas fisik.
                """
            )
        else:
            st.markdown("### Varian B: Pembelajaran Daring (Online)")
            st.info(
                """
                **Konteks Skenario: Pembelajaran Daring (Online Jarak Jauh)**
                * Perkuliahan berlangsung jarak jauh melalui platform konferensi video (Zoom/Meet) dan LMS.
                * Materi disampaikan via berbagi layar (screen sharing) presentasi dan rekaman video yang dapat diakses ulang.
                * Presensi otomatis, diskusi melalui mikrofon/chat, dan pengumpulan tugas berlangsung daring.
                """
            )

        st.markdown("#### Aktivitas Pembelajaran")
        # Grid Foto Stimulus 2x2 dengan fallback informatif
        asset_subfolder = "variant_a" if variant == "A" else "variant_b"
        base_asset_dir = os.path.join(os.path.dirname(__file__), "assets", asset_subfolder)

        items_meta = [
            {
                "filename": "1_lecture.jpg",
                "title": "1. Pemaparan Materi",
                "desc": (
                    "Dosen menjelaskan materi langsung di depan kelas memakai proyektor dan papan tulis."
                    if variant == "A"
                    else "Dosen membagikan layar materi slide presentasi via konferensi video."
                ),
            },
            {
                "filename": "2_discussion.jpg",
                "title": "2. Diskusi Kelompok",
                "desc": (
                    "Diskusi kelompok tatap muka bersama rekan satu meja di kelas."
                    if variant == "A"
                    else "Kolaborasi virtual di breakout room dan penyuntingan dokumen daring bersama."
                ),
            },
            {
                "filename": "3_qa.jpg",
                "title": "3. Sesi Tanya Jawab",
                "desc": (
                    "Mahasiswa mengacungkan tangan dan berdialog langsung dengan dosen di kelas."
                    if variant == "A"
                    else "Mahasiswa bertanya melalui fitur raise hand, mikrofon, atau kolom obrolan."
                ),
            },
            {
                "filename": "4_assignment.jpg",
                "title": "4. Pengerjaan Tugas",
                "desc": (
                    "Pengerjaan tugas atau kuis secara tertulis di lembar fisik di ruangan kelas."
                    if variant == "A"
                    else "Pengumpulan tugas mandiri dan kuis digital melalui portal LMS kampus."
                ),
            },
        ]

        col1, col2 = st.columns(2)
        for idx, item in enumerate(items_meta):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    base_name = os.path.splitext(item["filename"])[0]
                    found_img = None
                    for ext in (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".PNG"):
                        candidate = os.path.join(base_asset_dir, base_name + ext)
                        if os.path.exists(candidate):
                            found_img = candidate
                            break
                    if found_img:
                        st.image(found_img, use_container_width=True)
                    st.markdown(f"**{item['title']}**")
                    st.write(item["desc"])
        
        st.markdown("---")
        st.write(
            "Perhatikan skenario di atas. Bayangkan Anda mengikuti perkuliahan dengan metode tersebut, "
            "lalu klik tombol di bawah untuk mengisi evaluasi kepuasan."
        )

        if st.button("Mulai Kuesioner", type="primary", icon=":material/arrow_forward:", use_container_width=True):
            st.session_state["step"] = "questions"
            st.rerun()

    # Sub-view C: Step 2 — Halaman Kuesioner (20 Butir)
    elif st.session_state["step"] == "questions":
        st.markdown('<span class="clean-badge">TAHAP 2 DARI 2: KUESIONER</span>', unsafe_allow_html=True)
        st.title(":material/assignment: Kuesioner Kepuasan Pembelajaran")
        st.caption(f"Metode yang dievaluasi: **{variant_label}**")

        c_back, c_status = st.columns([1, 4])
        with c_back:
            if st.button("Kembali ke Skenario", icon=":material/arrow_back:"):
                st.session_state["step"] = "scenario"
                st.rerun()

        # Skala Likert Legenda
        st.info(
            "**Panduan Skala Penilaian:** 1 = Sangat Tidak Puas | 2 = Tidak Puas | 3 = Netral | 4 = Puas | 5 = Sangat Puas"
        )

        likert_options = [1, 2, 3, 4, 5]
        likert_labels = {
            1: "1 - Sangat Tidak Puas",
            2: "2 - Tidak Puas",
            3: "3 - Netral",
            4: "4 - Puas",
            5: "5 - Sangat Puas",
        }

        # Cari pertanyaan Q1
        q1_item = None
        for dim_title, items in DIMENSIONS:
            for item in items:
                if item[1] == PRIMARY_ITEM:
                    q1_item = item
                    break
            if q1_item:
                break

        # Render Q1 (Metrik Utama)
        with st.container(border=True):
            st.markdown('<span class="clean-badge">METRIK UTAMA HIPOTESIS</span>', unsafe_allow_html=True)
            st.markdown("### Pertanyaan Utama: Kepuasan Keseluruhan")
            q1_text = q1_item[2] if variant == "A" else q1_item[3]
            st.markdown(f"**{q1_item[0]}. {q1_text}**")
            
            cur_q1 = st.session_state["answers"].get(PRIMARY_ITEM)
            idx_q1 = likert_options.index(cur_q1) if cur_q1 in likert_options else None
            val_q1 = st.radio(
                label=q1_text,
                options=likert_options,
                index=idx_q1,
                format_func=lambda x: likert_labels[x],
                horizontal=True,
                key=f"radio_{PRIMARY_ITEM}",
                label_visibility="collapsed",
            )
            if val_q1 is not None:
                st.session_state["answers"][PRIMARY_ITEM] = val_q1

        st.markdown("---")
        st.markdown("### Butir Evaluasi Diagnostik")

        # Render Q2 s.d. Q20 dalam expander per dimensi
        for dim_title, items in DIMENSIONS:
            with st.expander(f"Dimensi: {dim_title}", expanded=True):
                for no_str, col_name, text_a, text_b in items:
                    if col_name == PRIMARY_ITEM:
                        continue
                    q_text = text_a if variant == "A" else text_b
                    st.markdown(f"**{no_str}. {q_text}**")

                    cur_val = st.session_state["answers"].get(col_name)
                    idx_val = likert_options.index(cur_val) if cur_val in likert_options else None
                    val = st.radio(
                        label=q_text,
                        options=likert_options,
                        index=idx_val,
                        format_func=lambda x: likert_labels[x],
                        horizontal=True,
                        key=f"radio_{col_name}",
                        label_visibility="collapsed",
                    )
                    if val is not None:
                        st.session_state["answers"][col_name] = val
                    st.write("")

        # Evaluasi kelengkapan jawaban
        total_items = len(ITEM_COLUMNS)
        filled_items = sum(1 for c in ITEM_COLUMNS if st.session_state["answers"].get(c) in (1, 2, 3, 4, 5))
        is_complete = filled_items == total_items

        st.markdown("---")
        st.caption(f"Kelengkapan pengisian: **{filled_items} dari {total_items} butir** dijawab.")

        if not is_complete:
            st.warning("Jawab seluruh 20 pertanyaan sebelum mengirimkan formulir.")

        if st.button("Kirim Jawaban", type="primary", icon=":material/send:", disabled=not is_complete, use_container_width=True):
            try:
                insert_response(
                    session_id=st.session_state["session_id"],
                    variant=variant,
                    answers=st.session_state["answers"],
                )
                st.session_state["submitted"] = True
                st.rerun()
            except DuplicateSessionError:
                st.error("Sesi ini sudah pernah mengirimkan jawaban survei.")
            except IncompleteResponseError as e:
                st.error(f"Pengiriman ditolak: {e}")
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")


# ------------------------------------------------------------------------------
# AREA 2: DASHBOARD ANALISIS A/B (ADMIN / DOSEN)
# ------------------------------------------------------------------------------
elif menu == "Dashboard Analisis":
    st.markdown('<span class="clean-badge">PANEL ANALITIK</span>', unsafe_allow_html=True)
    st.title(":material/query_stats: Dashboard Analisis Mann-Whitney U")
    st.caption("Evaluasi perbedaan kepuasan pembelajaran Luring vs Daring.")

    # Proteksi Autentikasi Admin Berbasis Sesi
    if not st.session_state.get("admin_logged_in", False):
        with st.container(border=True):
            st.subheader(":material/lock: Autentikasi Administrator")
            st.write("Masukkan password untuk mengakses dashboard evaluasi inferensial.")
            pwd_input = st.text_input("Password Admin:", type="password", key="admin_auth_pwd")
            if st.button("Masuk", type="primary", icon=":material/login:", use_container_width=True):
                if pwd_input == ADMIN_PASSWORD:
                    st.session_state["admin_logged_in"] = True
                    st.toast("Autentikasi admin berhasil.")
                    st.rerun()
                else:
                    st.error("Password salah. Silakan coba lagi.")
        st.stop()

    # Tombol Operasional & Sinkronisasi Data (3 Tombol Sejajar Proporsional)
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("Perbarui Data", icon=":material/refresh:", use_container_width=True):
            st.session_state["last_result_time"] = 0
            st.toast("Memuat data terbaru...")
            st.rerun()

    with col_btn2:
        if st.button("Injeksi Data Uji (N=70/grup)", icon=":material/database:", use_container_width=True):
            df_sim = generate_responses(
                n_a=70,
                n_b=70,
                seed=time.time_ns() % (2**32),
                scenario="random",
            )
            injected_count = 0
            for _, row in df_sim.iterrows():
                ans = {c: int(row[c]) for c in ITEM_COLUMNS}
                try:
                    insert_response(
                        session_id=str(row["session_id"]),
                        variant=str(row["variant_group"]),
                        answers=ans,
                    )
                    injected_count += 1
                except Exception:
                    pass
            st.session_state["last_result_time"] = 0
            st.toast(f"{injected_count} baris data simulasi berhasil diinjeksi.")
            st.rerun()

    with col_btn3:
        if st.button("Reset Data (Hapus Semua)", icon=":material/delete_sweep:", use_container_width=True):
            reset_database()
            st.session_state["last_result"] = None
            st.session_state["last_result_time"] = 0
            st.toast("Seluruh data respons berhasil dibersihkan.")
            st.rerun()

    # Ambil skor aktual
    scores_dict = fetch_scores()
    scores_a = scores_dict.get("A", [])
    scores_b = scores_dict.get("B", [])
    n_a = len(scores_a)
    n_b = len(scores_b)
    total_n = n_a + n_b

    st.markdown("---")
    st.subheader(":material/timeline: Progres Pengumpulan Sampel")

    # Progress bar ketercapaian sampel (Warna Hijau)
    pct_achieved = (total_n / TARGET_TOTAL_N) * 100 if TARGET_TOTAL_N > 0 else 0.0
    progress_val = min(total_n / TARGET_TOTAL_N, 1.0) if TARGET_TOTAL_N > 0 else 0.0
    st.progress(progress_val, text=f"Total Sampel Masuk: {total_n} / {TARGET_TOTAL_N} ({pct_achieved:.1f}%)")

    # 4 Metric KPI Cards Neumorphic (Proporsional, Rapi, Sejajar)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric(
        "Target Power Analysis",
        f"{TARGET_TOTAL_N} Total",
        delta=f"{TARGET_N} / varian",
        delta_color="off",
    )
    m_col2.metric(
        "Total Responden",
        f"{total_n} / {TARGET_TOTAL_N}",
        delta=f"{pct_achieved:.1f}%",
    )
    m_col3.metric(
        "Kelompok Luring (A)",
        f"{n_a} / {TARGET_N}",
        delta="Tercapai" if n_a >= TARGET_N else f"Kurang {TARGET_N - n_a}",
    )
    m_col4.metric(
        "Kelompok Daring (B)",
        f"{n_b} / {TARGET_N}",
        delta="Tercapai" if n_b >= TARGET_N else f"Kurang {TARGET_N - n_b}",
    )

    # Gatekeeping Sampel
    if min(n_a, n_b) < MIN_N:
        st.error(
            f"Sampel belum mencukupi untuk menjalankan uji Mann-Whitney U (minimum {MIN_N} per varian).  \n"
            f"Kondisi saat ini: Luring n={n_a}, Daring n={n_b}.  \n"
            "Isi kuesioner pada tab formulir survei atau gunakan tombol 'Injeksi Data Uji' di atas."
        )
    else:
        if min(n_a, n_b) < TARGET_N:
            st.warning(
                f"Ukuran sampel (Luring: {n_a}, Daring: {n_b}) belum mencapai target Power Analysis (minimum {TARGET_N} per varian). "
                "Hasil inferensial masih bersifat tentatif."
            )

        # Caching hasil uji 60 detik
        now = time.time()
        if (
            st.session_state["last_result"] is None
            or (now - st.session_state["last_result_time"]) > 60
        ):
            res = run_mann_whitney(scores_a, scores_b, alpha=0.05)
            st.session_state["last_result"] = res
            st.session_state["last_result_time"] = now
        else:
            res = st.session_state["last_result"]

        st.markdown("---")
        st.subheader(":material/calculate: Hasil Uji Hipotesis Utama (Mann-Whitney U)")
        st.caption(f"Kolom Metrik: {res.outcome_column} | Taraf Signifikansi alpha = {res.alpha}")

        # KPI Cards (2 baris x 4 kolom - ukuran seragam proporsional)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Median Luring (A)", f"{res.median_a:.1f}", help="Skala Likert 1-5")
        kpi2.metric("Median Daring (B)", f"{res.median_b:.1f}", help="Skala Likert 1-5")
        kpi3.metric("Statistik Uji (U)", f"{res.statistic:.1f}", help="Statistik peringkat Mann-Whitney U")
        p_val_display = f"{res.p_value:.4f}" if res.p_value >= 0.0001 else "< 0.0001"
        kpi4.metric(
            "p-value (Dua Arah)",
            p_val_display,
            help=f"Taraf signifikansi alpha = {res.alpha} | Status: {'Signifikan (p < 0.05)' if res.p_value < res.alpha else 'Tidak Signifikan'}",
        )

        kpi5, kpi6, kpi7, kpi8 = st.columns(4)
        kpi5.metric("Effect Size (r_B)", f"{res.effect_size:+.3f}", help="Korelasi Rank-Biserial (-1 s.d. +1)")
        kpi6.metric("95% CI (Hodges-Lehmann)", f"[{res.ci_lower:+.2f}, {res.ci_upper:+.2f}]", help="Bootstrap Resampling")
        kpi7.metric("Sampel Varian A (Luring)", f"N = {res.n_a}")
        kpi8.metric("Sampel Varian B (Daring)", f"N = {res.n_b}")

        # Keputusan Formal
        st.markdown("")
        if res.decision == "tolak H0":
            st.success(
                f"### Keputusan: Tolak H0  \n\n"
                f"{res.interpretation}  \n"
                f"Median Luring ({res.median_a}) berbeda nyata dengan Median Daring ({res.median_b}) pada tingkat kepercayaan 95%."
            )
        else:
            st.info(
                f"### Keputusan: Gagal Menolak H0  \n\n"
                f"{res.interpretation}  \n"
                f"Data empiris belum cukup untuk menunjukkan perbedaan kepuasan belajar antara metode Luring dan Daring pada alpha 0.05."
            )

        st.markdown("---")
        st.subheader(":material/bar_chart: Distribusi Skor Kepuasan")

        tab_viz1, tab_viz2 = st.tabs([":material/bar_chart: Distribusi Frekuensi (%)", ":material/ssid_chart: Box Plot Sebaran"])

        df_plot = pd.DataFrame(
            [{"Varian": "Varian A (Luring)", "Skor": s} for s in scores_a]
            + [{"Varian": "Varian B (Daring)", "Skor": s} for s in scores_b]
        )

        with tab_viz1:
            dist_data = []
            for v_name, s_list in [("Varian A (Luring)", scores_a), ("Varian B (Daring)", scores_b)]:
                n_total = len(s_list)
                for score_val in [1, 2, 3, 4, 5]:
                    cnt = s_list.count(score_val)
                    pct = (cnt / n_total * 100) if n_total > 0 else 0
                    dist_data.append({"Varian": v_name, "Skor": f"Skor {score_val}", "Proporsi (%)": pct, "Jumlah": cnt})

            df_dist = pd.DataFrame(dist_data)
            fig_bar = px.bar(
                df_dist,
                x="Skor",
                y="Proporsi (%)",
                color="Varian",
                barmode="group",
                color_discrete_map={"Varian A (Luring)": "#4f46e5", "Varian B (Daring)": "#0284c7"},
                hover_data=["Jumlah"],
                title="Distribusi Proporsi Skor Likert (sat_overall)",
            )
            # Garis horizontal saja yang jelas dan kontras di atas background neumorphic
            fig_bar.update_xaxes(
                showgrid=False,
                linecolor="#94a3b8",
            )
            fig_bar.update_yaxes(
                showgrid=True,
                gridcolor="#cbd0d8",
                gridwidth=1.3,
                griddash="dot",
                zeroline=True,
                zerolinecolor="#64748b",
                linecolor="#94a3b8",
            )
            fig_bar.update_layout(
                yaxis_title="Proporsi (%)",
                xaxis_title="Tingkat Skor",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1e293b", family="Inter, sans-serif"),
                legend=dict(bgcolor="rgba(242, 242, 245, 0.85)", bordercolor="rgba(180, 180, 192, 0.4)", borderwidth=1),
                margin=dict(t=40, b=40, l=40, r=40),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab_viz2:
            fig_box = px.box(
                df_plot,
                x="Varian",
                y="Skor",
                color="Varian",
                points="all",
                color_discrete_map={"Varian A (Luring)": "#4f46e5", "Varian B (Daring)": "#0284c7"},
                title="Sebaran Skor Kepuasan Keseluruhan",
            )
            fig_box.update_yaxes(
                showgrid=True,
                gridcolor="#cbd0d8",
                gridwidth=1.3,
                griddash="dot",
                linecolor="#94a3b8",
                range=[0.5, 5.5],
            )
            fig_box.update_xaxes(
                showgrid=False,
                linecolor="#94a3b8",
            )
            fig_box.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1e293b", family="Inter, sans-serif"),
                legend=dict(bgcolor="rgba(242, 242, 245, 0.85)", bordercolor="rgba(180, 180, 192, 0.4)", borderwidth=1),
                margin=dict(t=40, b=40, l=40, r=40),
            )
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("---")
        st.subheader(":material/table_chart: Analisis Diagnostik Butir Evaluasi")

        all_item_scores = fetch_all_item_scores()
        item_rows = describe_items(all_item_scores)

        # Mapping metadata butir
        item_meta_dict = {}
        for dim_title, items in DIMENSIONS:
            for no_str, col_name, ta, tb in items:
                item_meta_dict[col_name] = {"no": no_str, "dimensi": dim_title}

        desc_table_data = []
        for r in item_rows:
            col_id = r["item"]
            meta = item_meta_dict.get(col_id, {"no": "-", "dimensi": "-"})
            desc_table_data.append({
                "No": meta["no"],
                "Kode Kolom": col_id,
                "Dimensi": meta["dimensi"],
                "N Luring": r["n_a"],
                "Median A": r["median_a"],
                "N Daring": r["n_b"],
                "Median B": r["median_b"],
                "Selisih (A - B)": (r["median_a"] - r["median_b"]) if r["median_a"] is not None and r["median_b"] is not None else None,
            })

        df_desc = pd.DataFrame(desc_table_data)
        st.dataframe(df_desc, use_container_width=True, hide_index=True)

        st.markdown("---")
        with st.expander(":material/table_rows: Data Mentah Responden"):
            df_raw = fetch_all_responses()
            if not df_raw.empty:
                st.dataframe(df_raw.tail(50), use_container_width=True)
            else:
                st.caption("Data mentah kosong.")
