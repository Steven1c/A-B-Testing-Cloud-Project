# Dokumen Arsitektur & Justifikasi Service Model

## 1. Diagram Arsitektur Sistem

Sistem ini dirancang sebagai platform survei daring berbasis komputasi awan yang terintegrasi langsung dengan mesin analisis statistik inferensial (A/B testing).

```text
       [Pengguna / Responden]
                 │
                 ▼ (HTTPS / Port 443)
       ┌──────────────────────────────────────────┐
       │   PaaS: Streamlit Community / Render     │
       │   - Hosting Web Frontend & Backend       │
       │   - Randomizer Varian A/B (50:50)        │
       │   - Autentikasi Dasar Halaman Admin      │
       └──────────────────┬───────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │ (REST API / SSL Pool)         │ (In-memory Python Engine)
          ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│ Managed DB: Supabase Postgres │   │ stats_engine.py (SciPy/Stats) │
│ - Tabel: survey_responses     │   │ - Power Analysis (G*Power)    │
│ - Automated Daily Backups     │   │ - Welch's t-test & Z-test     │
│ - SSL Enforced Connection     │   │ - 95% Confidence Interval     │
└───────────────────────────────┘   └───────────────────────────────┘
```

---

## 2. Pilihan Service Model: PaaS & Managed Database

Proyek ini memilih model layanan **Platform as a Service (PaaS)** yang dipadukan dengan **Managed Relational Database**:

* **PaaS untuk Web Application (Streamlit Cloud / Render):**
  Mengeliminasi kompleksitas manajemen sistem operasi, patch keamanan kernel, konfigurasi web server (seperti Nginx reverse proxy), dan routing port manual. Kode Python di-deploy langsung dari repositori Git.
* **Managed Database (Supabase PostgreSQL):**
  Menyediakan database PostgreSQL production-ready dengan koneksi terenkripsi (SSL), antarmuka web table editor, dan fitur *automated backup* tanpa perlu instalasi dan pemeliharaan server database mandiri.

---

## 3. Perbandingan dengan Alternatif Service Model

| Aspek Penilaian | PaaS + Managed DB (Pilihan Proyek) | Alternatif: IaaS murni (VM / EC2 / Compute Engine) |
| :--- | :--- | :--- |
| **Beban Operasional DevOps** | **Sangat Rendah:** Fokus 100% pada logika aplikasi & statistik | **Tinggi:** Wajib konfigurasi OS Linux, firewall, Nginx, Systemd, dan secure DB |
| **Biaya Idle (Non-aktif)** | **\$0.00 (Free Tier):** Container sleep otomatis saat sepi | **Berbayar:** VM tetap menagih jam nyala meskipun tidak ada pengunjung |
| **Kesiapan Backup & DR** | **Otomatis:** Snapshots harian bawaan platform cloud | **Manual:** Wajib menulis script cron dump PostgreSQL mandiri |
| **Kecepatan Deployment** | Hitungan menit via integrasi Git push | Berjam-jam untuk provisioning dan hardening server |
| **Justifikasi Pemilihan** | Optimal untuk siklus proyek 3 minggu dengan tim homogen Statistika | Terlalu membuang waktu pada administrasi sistem yang tidak dinilai |
