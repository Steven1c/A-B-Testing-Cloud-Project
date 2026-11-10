# Proyek Kelompok Komputasi Awan (Topik 3: Platform Survei & Uji A/B)

Repositori ini memuat implementasi *end-to-end* layanan platform survei daring terintegrasi dengan mesin pengujian hipotesis inferensial A/B testing secara *real-time*.

- **Program Studi:** Statistika & Sistem Teknologi dan Informasi
- **Mata Kuliah:** Komputasi Awan (1519600054)
- **Service Model:** PaaS (Platform as a Service) & Managed Database
- **Stack Utama:** Python, Streamlit, Supabase (PostgreSQL), SciPy, Statsmodels

---

## Struktur Direktori Repositori

```text
Project/
|-- docs/                         # Laporan komprehensif proyek
|   |-- architecture.md           # Diagram arsitektur PaaS & justifikasi service model
|   |-- interface-contract.md     # Kontrak skema data & signature fungsi antar-layer
|   |-- analysis-report.md        # Laporan hipotesis, power analysis & uji inferensial
|   |-- runbook.md                # Panduan langkah operasional & deployment cloud
|   |-- cost-report.md            # Rincian estimasi vs realisasi tagihan biaya ($0.00)
|   |-- security-scalability.md   # Analisis least privilege, SSL & keputusan autoscaling
|   |-- cross-review.md           # Evaluasi silang antar kedua layer di Minggu 3
|   |-- role-log.md               # Catatan kontribusi mingguan per anggota + commit Git
|   |-- ai-disclosure.md          # Catatan transparansi penggunaan alat bantu AI
|   `-- evidence/                 # Screenshot monitoring, uji beban, dan bukti teardown
|-- src/
|   |-- analysis/                 # Modul analisis data & simulasi Monte Carlo
|   |   |-- stats_engine.py       # Engine Welch's t-test, Z-test, dan selang kepercayaan
|   |   `-- simulate_data.py      # Generator data responden sintetis (target N)
|   |-- app/                      # Aplikasi web survei & dashboard admin
|   |   |-- db.py                 # Klien integrasi database Supabase PostgreSQL
|   |   `-- main.py               # Aplikasi Streamlit (Halaman survei + Analisis)
|   |-- infra/                    # Infrastruktur & skema database
|   |   `-- schema.sql            # Skema DDL tabel PostgreSQL untuk Supabase
|   `-- config/                   # Template konfigurasi non-rahasia
|       `-- .env.example          # Contoh format variabel lingkungan lokal
|-- .gitignore                    # Pengecualian file sensitif (.env, cache, venv)
|-- requirements.txt              # Daftar dependensi library Python
`-- README.md                     # Panduan utama proyek
```

---

## Cara Menjalankan di Komputer Lokal

1. **Clone Repositori & Pasang Dependensi:**
   ```bash
   git clone <URL_REPOSITORY>
   cd Project
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Setup Konfigurasi (.env):**
   Salin file `src/config/.env.example` menjadi `.env`:
   ```bash
   copy src\config\.env.example .env   # Windows
   cp src/config/.env.example .env      # Linux/macOS
   ```
   *(Catatan: Aplikasi memiliki mode mock bawaan, sehingga tetap dapat dijalankan secara lokal meskipun belum dihubungkan ke akun Supabase).*

3. **Jalankan Aplikasi Streamlit:**
   ```bash
   streamlit run src/app/main.py
   ```
   Akses antarmuka di peramban pada alamat `http://localhost:8501`.

---

## Tautan Dokumen Utama

* [Dokumen Arsitektur Sistem](docs/architecture.md)
* [Interface Contract (Minggu 1)](docs/interface-contract.md)
* [Laporan Analisis Statistik](docs/analysis-report.md)
* [Runbook & Deployment Guide](docs/runbook.md)
* [Laporan Biaya Cloud](docs/cost-report.md)
