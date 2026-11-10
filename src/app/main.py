import os
import sys
import time
import uuid
import random
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Tambahkan path root agar modul src.analysis dan src.app dapat diimpor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.app.db import insert_response, fetch_all_responses, get_supabase
from src.analysis.stats_engine import compute_sample_size, analyze_ab_test
from src.analysis.simulate_data import generate_simulated_responses

load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

st.set_page_config(
    page_title="Platform Survei & Uji A/B EduTech",
    page_icon="📊",
    layout="wide"
)

# Inisialisasi Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "variant" not in st.session_state:
    st.session_state.variant = random.choice(["A", "B"])
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "survey_submitted" not in st.session_state:
    st.session_state.survey_submitted = False
if "local_cache_df" not in st.session_state:
    st.session_state.local_cache_df = pd.DataFrame()


# --- SIDEBAR NAVIGASI ---
st.sidebar.title("Navigasi Sistem")
menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Formulir Survei (Pengunjung)", "Dashboard Analisis A/B (Dosen/Admin)"]
)

st.sidebar.markdown("---")
supabase_status = "Terhubung" if get_supabase() is not None else "Mode Mock (Lokal)"
st.sidebar.caption(f"Status Database: **{supabase_status}**")
st.sidebar.caption("Proyek Komputasi Awan — Topik 3")


# ==============================================================================
# HALAMAN 1: FORMULIR SURVEI PUBLIK
# ==============================================================================
if menu == "Formulir Survei (Pengunjung)":
    st.title("Program Sertifikasi: Data Science & Cloud Computing")
    
    variant = st.session_state.variant

    if st.session_state.survey_submitted:
        st.success("Terima kasih! Respon Anda telah berhasil dicatat.")
        st.info("Setiap pengunjung secara acak menerima salah satu varian tampilan untuk keperluan eksperimen A/B testing.")
        if st.button("Isi Ulang (Uji Coba Pengunjung Baru)"):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.variant = random.choice(["A", "B"])
            st.session_state.start_time = time.time()
            st.session_state.survey_submitted = False
            st.rerun()

    else:
        # Render Banner Berdasarkan Varian
        if variant == "A":
            # VARIAN A: KONTROL (Tampilan Standar / Informatif)
            st.subheader("Tingkatkan Keterampilan Cloud & Data Analytics Anda")
            st.write(
                "Program pelatihan komprehensif selama 4 minggu yang mencakup Python, SQL, "
                "dan penggelaran layanan di Google Cloud Platform dan AWS."
            )
            st.markdown(
                """
                **Kurikulum Pelatihan:**
                - Modul 1: Dasar Pemrograman Python & Analisis Data Eksploratif
                - Modul 2: Desain Database Relasional & Query SQL Terapan
                - Modul 3: Arsitektur Cloud Computing & Deployment Container
                """
            )
        else:
            # VARIAN B: TREATMENT (Social Proof & Urgensi)
            st.subheader("🔥 Bergabung dengan 1.250+ Mahasiswa yang Telah Menguasai Cloud")
            st.markdown("⭐ **Rating 4.9/5 dari 320 Alumni Terverifikasi**")
            st.info(
                "💬 *'Materi sangat aplikatif! Membantu saya lolos magang Cloud Architect di perusahaan teknologi terkemuka.'* "
                "— **Rian, Mahasiswa Semester 5**"
            )
            st.warning("⏳ **Sisa 5 Kuota Beasiswa Potongan Biaya untuk Pendaftaran Minggu Ini!**")
            st.markdown(
                """
                **Keunggulan Program:**
                - Kurikulum industri langsung praktik hands-on di konsol cloud nyata
                - Sertifikat kompetensi yang diakui dan portofolio GitHub siap kerja
                """
            )

        st.markdown("---")
        st.write("### Kuesioner Minat & Persepsi Mahasiswa")

        with st.form("survey_form"):
            score_wtp = st.slider(
                "1. Seberapa tinggi minat dan kesediaan Anda mengikuti program ini? (Skala 1 - 10)",
                min_value=1,
                max_value=10,
                value=6,
                help="1 = Sangat tidak berminat, 10 = Sangat berminat dan siap mendaftar."
            )

            perceived_trust = st.select_slider(
                "2. Seberapa percaya Anda terhadap kredibilitas dan kualitas program di atas?",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: f"{x} - " + ["Sangat Ragu", "Ragu", "Netral", "Percaya", "Sangat Percaya"][x-1]
            )

            clicked_signup = st.checkbox(
                "Saya ingin mendaftar sesi webinar pengenalan gratis dan menerima silabus lengkap (Klik Konversi)",
                value=False
            )

            submitted = st.form_submit_button("Kirim Jawaban Survei")

            if submitted:
                elapsed_sec = round(time.time() - st.session_state.start_time, 1)
                payload = {
                    "session_id": st.session_state.session_id,
                    "assigned_variant": variant,
                    "willingness_to_pay": int(score_wtp),
                    "perceived_trust": int(perceived_trust),
                    "clicked_signup": bool(clicked_signup),
                    "time_spent_sec": float(elapsed_sec)
                }

                # Simpan ke Supabase
                success = insert_response(payload)
                
                # Simpan juga ke cache lokal untuk pengujian tanpa DB
                if st.session_state.local_cache_df.empty:
                    st.session_state.local_cache_df = pd.DataFrame([payload])
                else:
                    st.session_state.local_cache_df = pd.concat(
                        [st.session_state.local_cache_df, pd.DataFrame([payload])], 
                        ignore_index=True
                    )

                if success:
                    st.session_state.survey_submitted = True
                    st.rerun()
                else:
                    st.error("Gagal menyimpan data ke database. Silakan coba lagi.")


# ==============================================================================
# HALAMAN 2: DASHBOARD ANALISIS A/B (ADMIN / DOSEN)
# ==============================================================================
elif menu == "Dashboard Analisis A/B (Dosen/Admin)":
    st.title("Dashboard Analisis Inferensial A/B Testing")
    st.caption("Panel Evaluasi Hipotesis Statistik & Kontrak Antar-Layer")

    # Autentikasi Dasar
    st.sidebar.subheader("Autentikasi Akses")
    pwd_input = st.sidebar.text_input("Password Admin:", type="password", value="")

    if pwd_input != ADMIN_PASSWORD:
        st.warning("Halaman ini diproteksi. Masukkan password admin pada panel sidebar kiri untuk membuka hasil analisis.")
        st.info("Petunjuk evaluasi: Password default lokal adalah `admin123`.")
    else:
        st.success("Autentikasi berhasil. Akses penuh ke data analitik dibuka.")

        # Tombol aksi sinkronisasi data
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 3])
        with col_btn1:
            if st.button("Tarik Data dari Supabase"):
                df_cloud = fetch_all_responses()
                if not df_cloud.empty:
                    st.session_state.local_cache_df = df_cloud
                    st.toast(f"Berhasil memuat {len(df_cloud)} baris dari cloud.")
                else:
                    st.warning("Database Supabase masih kosong atau belum terhubung.")

        with col_btn2:
            if st.button("Injeksi Data Simulasi (N=260)"):
                df_sim = generate_simulated_responses(n_per_variant=130)
                st.session_state.local_cache_df = df_sim
                st.toast("Data simulasi N=260 berhasil dimuat ke cache analisis.")

        with col_btn3:
            target_n_per_variant = compute_sample_size(effect_size=0.35, alpha=0.05, power=0.80)
            st.metric("Target Sampel Minimum (Power Analysis)", f"{target_n_per_variant} per varian (Total {target_n_per_variant*2})")

        df_current = st.session_state.local_cache_df

        if df_current.empty or len(df_current) < 6:
            st.info("Data belum cukup untuk menjalankan uji statistik. Silakan isi survei beberapa kali atau tekan tombol 'Injeksi Data Simulasi (N=260)' di atas.")
        else:
            # Eksekusi Analisis Statistik via stats_engine.py
            results = analyze_ab_test(df_current, alpha=0.05)

            if results.get("status") == "success":
                st.markdown("---")
                st.subheader("1. Ringkasan Sampel & Statistik Deskriptif")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Responden", results["sample_size"]["total"])
                m2.metric("Sampel Varian A (Kontrol)", results["sample_size"]["n_a"])
                m3.metric("Sampel Varian B (Treatment)", results["sample_size"]["n_b"])
                diff = results["descriptive"]["diff_mean"]
                m4.metric("Selisih Rata-rata (B - A)", f"{diff:+.2f}")

                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.markdown("**Varian A (Kontrol - Polos):**")
                    st.write(f"- Rata-rata Minat: **{results['descriptive']['mean_a']}** (SD: {results['descriptive']['std_a']})")
                    st.write(f"- Conversion Rate Klik: **{results['proportion_test']['cr_a']}%**")
                with col_stat2:
                    st.markdown("**Varian B (Treatment - Social Proof):**")
                    st.write(f"- Rata-rata Minat: **{results['descriptive']['mean_b']}** (SD: {results['descriptive']['std_b']})")
                    st.write(f"- Conversion Rate Klik: **{results['proportion_test']['cr_b']}%**")

                st.markdown("---")
                st.subheader("2. Pemeriksaan Asumsi Statistik")
                asm = results["assumptions"]
                c_asm1, c_asm2 = st.columns(2)
                with c_asm1:
                    st.markdown("**Uji Normalitas (Shapiro-Wilk):**")
                    st.write(f"- p-value Grup A: `{asm['shapiro_a_p']}`")
                    st.write(f"- p-value Grup B: `{asm['shapiro_b_p']}`")
                    st.caption("Asumsi terpenuhi jika p-value > 0.05.")
                with c_asm2:
                    st.markdown("**Uji Homogenitas Varians (Levene's Test):**")
                    st.write(f"- p-value Levene: `{asm['levene_p']}`")
                    st.write(f"- Varians Homogen: `{'Ya' if asm['is_equal_var'] else 'Tidak (Pakai Koreksi Welch)'}`")

                st.markdown("---")
                st.subheader("3. Uji Hipotesis Utama (Two-Sample Welch's t-test)")
                test_c = results["continuous_test"]

                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric("Statistik Uji (t)", test_c["t_statistic"])
                col_res2.metric("p-value (One-tailed)", test_c["p_value"])
                ci = test_c["ci_95"]
                col_res3.metric("95% Confidence Interval", f"[{ci[0]}, {ci[1]}]")

                # Box Keputusan Formal Wajib Sesuai Rubrik
                if test_c["decision"] == "Tolak H₀":
                    st.success(f"### Keputusan: {test_c['decision']}\n\n{test_c['conclusion']}")
                else:
                    st.warning(f"### Keputusan: {test_c['decision']}\n\n{test_c['conclusion']}")

                st.markdown("---")
                st.subheader("4. Uji Proporsi Konversi Klik (Z-Test)")
                prop = results["proportion_test"]
                st.write(f"- Statistik Z: `{prop['z_statistic']}` | p-value: `{prop['p_value']}`")
                st.write(f"- Keputusan Uji Proporsi: **{prop['decision']}**")

                st.markdown("---")
                with st.expander("Lihat Data Mentah (50 Baris Terakhir)"):
                    st.dataframe(df_current.tail(50), use_container_width=True)

            else:
                st.warning(results.get("message", "Perhitungan statistik tidak dapat diselesaikan."))
