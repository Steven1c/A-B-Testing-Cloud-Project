# Platform Survei & Uji A/B Pembelajaran (Luring vs Daring)

Repositori ini memuat implementasi *end-to-end* layanan platform survei daring terintegrasi dengan mesin inferensial A/B testing non-parametrik secara *real-time*.

* **Program Studi:** Statistika & Sistem Teknologi Informasi
* **Mata Kuliah:** Komputasi Awan (1519600054) — Topik 3: Platform Survei & Uji A/B
* **Service Model:** PaaS (Platform as a Service) & Managed Database
* **Stack Utama:** Python 3.10+, Streamlit, Supabase (PostgreSQL 15), SciPy, Statsmodels, Plotly
* **Demo Video:** https://youtu.be/85sa6K5kzkM
* **Link Web:** https://01a20719-e42a-7eb2-9ac3-c43af8d8dce0.share.connect.posit.cloud/

---

## Fitur Utama Platform

1. **Survei Pembelajaran & Traffic Splitting Acak:**
   * **Alokasi Acak Otomatis (50:50):** Responden dialokasikan secara independen ke **Varian A (Pembelajaran Luring/Tatap Muka)** atau **Varian B (Pembelajaran Daring/Online)**.
   * **Stimulus Skenario 2x2:** Sebelum mengisi instrumen, responden diberikan konteks skenario perkuliahan lengkap dengan 4 foto representatif (Pemaparan Materi, Diskusi Kelompok, Tanya Jawab, Pengerjaan Tugas).
   * **Instrumen Evaluasi 20 Butir Likert (1–5):** Mencakup 5 dimensi evaluasi pembelajaran (Kepuasan Keseluruhan, Pemahaman Materi, Interaksi & Keterlibatan, Fleksibilitas Lingkungan, Dukungan Teknis).
   * **Pencegahan Respon Ganda:** Setiap sesi responden dikunci dengan `session_id` unik (UUID 16 karakter).

2. **Dashboard Analisis Inferensial Real-Time (Khusus Admin):**
   * **Autentikasi Sesi:** Dilindungi password administrator dengan status login persisten di `st.session_state`.
   * **Pelacakan Target Sampel (Power Analysis):** Progress bar interaktif dan 4 KPI metrics yang melacak ketercapaian sampel terhadap batas target (N = 64/varian, Total N = 128) serta rasio persentase riil.
   * **Uji Hipotesis Utama (Mann-Whitney U Test):** Komputasi statistik *U*, *p-value* dua arah, ukuran efek *Rank-Biserial Correlation* (*r_B*), dan selang kepercayaan 95% selisih median Hodges-Lehmann via *bootstrap resampling*.
   * **Visualisasi Distribusi Plotly:** Grafik batang proporsi frekuensi skor 1–5 per varian serta Box Plot sebaran data ordinal dengan gridline kontras.
   * **Analisis Diagnostik 20 Butir:** Tabel komparasi nilai median dan selisih (A - B) untuk seluruh butir evaluasi secara terperinci.
   * **Akses Data Mentah:** Panel inspeksi data mentah (*raw responses*) yang dapat diekspor langsung.

3. **Toolbar Pengujian & Simulasi Instan:**
   * **Injeksi Data Uji (N=70 per varian):** Memasukkan 140 sampel sintetis Monte Carlo realistis dalam satu klik untuk keperluan pengujian dan live demo tanpa harus mengisi formulir manual.
   * **Reset Data (Hapus Semua):** Mengosongkan data respons seketika baik pada database Supabase maupun local in-memory storage.
   * **Perbarui Data:** Menjalankan sinkronisasi dan pengambilan data terbaru secara manual.

4. **Desain Antarmuka Neumorphic Modern (Soft UI):**
   * Latar belakang gradasi tekstur kain sutra (*silk fabric drape*) monokrom netral.
   * Card Neumorphic elevasi lembut tanpa garis solid kaku.
   * Tipografi modern menggunakan font **Inter**.
   * Proteksi integrasi ikon bawaan **Material Symbols**.
   * Sidebar navigasi terkunci pada lebar optimal yang tetap fleksibel disembunyikan (*collapsible*).

---

## Struktur Direktori Repositori

```text
Project/
|-- .streamlit/
|   `-- config.toml              # Konfigurasi tema Streamlit (warna dasar, tipografi)
|-- docs/                        # Dokumentasi komprehensif proyek
|   |-- architecture.md          # Diagram arsitektur PaaS, aliran data & justifikasi cloud
|   |-- interface-contract.md    # Kontrak skema data & signature fungsi antar-layer v1.1
|   |-- analysis-report.md       # Laporan metodologi inferensial, hipotesis & Power Analysis
|   |-- runbook.md               # Panduan operasional sistem, deployment & pengujian
|   |-- cost-report.md           # Laporan estimasi vs realisasi biaya cloud ($0.00 Free Tier)
|   |-- security-scalability.md  # Analisis keamanan, least privilege & keputusan arsitektur
|   |-- cross-review.md          # Evaluasi silang antar Layer STI dan Layer STAT
|   |-- role-log.md              # Catatan kontribusi mingguan per anggota + commit Git
|   |-- ai-disclosure.md         # Catatan transparansi pemanfaatan alat bantu AI
|   |-- prd-web.md               # Product Requirement Document (PRD) aplikasi web
|   `-- evidence/                # Folder artefak screenshot pengujian & monitoring
|-- src/
|   |-- analysis/                # Modul analisis data & simulasi Monte Carlo
|   |   |-- stats_engine.py      # Engine Mann-Whitney U, rank-biserial & bootstrap CI
|   |   `-- simulate_data.py     # Generator data survei Monte Carlo Likert 1-5
|   |-- app/                     # Aplikasi web survei & dashboard analitik
|   |   |-- assets/              # Aset visual foto stimulus skenario (Varian A & B) + background
|   |   |-- db.py                # Klien database Supabase dengan fallback in-memory storage
|   |   |-- questions.py         # Definisi 20 butir instrumen evaluasi pembelajaran
|   |   `-- main.py              # Entrypoint utama antarmuka Streamlit
|   |-- config/                  # Konfigurasi lingkungan non-rahasia
|   |   `-- .env.example         # Template variabel lingkungan lokal
|   |-- errors.py                # Definisi exception domain & validasi data
|   `-- contract.py              # Interface contract konstanta & tipe data resmi
|-- tests/                       # Automated test suite (Pytest)
|   `-- test_contract.py         # 37 unit test memverifikasi kontrak, DB & analisis
|-- .gitignore                   # Pengecualian berkas sensitif (.env, venv, cache)
|-- requirements.txt             # Dependensi pustaka Python
`-- README.md                    # Dokumentasi utama proyek
```

---

## Panduan Menjalankan di Komputer Lokal

### 1. Prasyarat Sistem
* Python versi 3.10 atau yang lebih baru.
* Git terpasang di sistem operasi.

### 2. Kloning Repositori & Instalasi Dependensi
```bash
# Clone repositori
git clone https://github.com/Steven1c/A-B-Testing-Cloud-Project
cd Platform-Survei-Uji-AB

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Pasang dependensi
pip install -r requirements.txt
```

### 3. Setup Variabel Lingkungan (.env)
Salin berkas template konfigurasi:
```bash
# Windows:
copy src\config\.env.example .env

# Linux / macOS:
cp src/config/.env.example .env
```

Isi berkas `.env` sesuai kebutuhan:
```ini
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-public-key"
ADMIN_PASSWORD="admin123"
```
> **Catatan Ketahanan Sistem:** Jika `SUPABASE_URL` atau `SUPABASE_KEY` dibiarkan kosong, aplikasi otomatis beralih ke mode **Mock In-Memory Storage**. Seluruh fitur survei, validasi duplikasi sesi, dan dashboard analisis tetap berfungsi 100% tanpa error koneksi.

### 4. Jalankan Aplikasi Web Streamlit
```bash
streamlit run src/app/main.py
```
Aplikasi akan terbuka otomatis di peramban pada alamat `http://localhost:8501`.
* **Menu Formulir Survei:** Terbuka untuk umum (menguji alokasi varian dan pengisian kuesioner).
* **Menu Dashboard Analisis:** Memerlukan password admin (default: `admin123`).

---

## Verifikasi Otomatis (Testing Suite)

Proyek ini dilengkapi dengan 37 pengujian otomatis yang memverifikasi kepatuhan terhadap Interface Contract, validasi data, serta ketahanan modul analisis:

```bash
# Menjalankan pengujian unit & kontrak:
pytest -v

# Menjalankan pengujian lengkap termasuk integrasi database lokal:
# Windows (PowerShell):
Set-Item -Path env:RUN_DB_TESTS -Value 1; pytest -v
# Linux / macOS:
RUN_DB_TESTS=1 pytest -v
```

Hasil verifikasi:
```text
============================= 37 passed in 3.02s ==============================
```

---

## Panduan Penggelaran Cloud (PaaS)

Layanan dideploy secara gratis menggunakan **Postit Connect Cloud**:
1. Hubungkan repositori GitHub `Steven1c/A-B-Testing-Cloud-Project` ke Posit Connect Cloud melalui menu **Integrations**.
2. Tentukan konfigurasi aplikasi:
   - **Runtime:** Python 3.10+
   - **Main file path:** `src/app/main.py`
3. Masukkan kredensial pada menu **Settings -> Variables**:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ADMIN_PASSWORD`
4. Publish/Deploy aplikasi. Layanan otomatis berjalan di endpoint publik dengan protokol HTTPS aktif.

---

## Tautan Dokumen Pendukung

* [Arsitektur Cloud & Diagram Sistem](docs/architecture.md)
* [Interface Contract v1.1](docs/interface-contract.md)
* [Laporan Metodologi & Hasil Analisis Statistik](docs/analysis-report.md)
* [Runbook Operasional & Deployment Guide](docs/runbook.md)
* [Laporan Realisasi Biaya Cloud ($0.00)](docs/cost-report.md)
* [Analisis Keamanan & Skalabilitas Sistem](docs/security-scalability.md)
* [Product Requirement Document (PRD Web)](docs/prd-web.md)
* [Catatan Evaluasi Silang (Cross-Review)](docs/cross-review.md)
* [Log Peran & Kontribusi Anggota (Role Log)](docs/role-log.md)
* [Pengungkapan Penggunaan AI (AI Disclosure)](docs/ai-disclosure.md)
