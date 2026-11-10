# Catatan Peran & Kontribusi Individu (Role Log)

Dokumen pelaporan kontribusi mingguan per anggota sesuai rubrik *Individual Contribution (5%)*.

---

## Daftar Anggota & Pembagian Layer

| Nama Anggota | NIM | Layer Penugasan | Peran Utama |
| :--- | :--- | :--- | :--- |
| **[Nama Anggota 1]** | [NIM 1] | Infrastructure & Operations (STI) | Web Developer & Repo Setup |
| **[Nama Anggota 2]** | [NIM 2] | Infrastructure & Operations (STI) | Database Architect & Cloud Deployer |
| **[Nama Anggota 3]** | [NIM 3] | Analysis Layer (STAT) | Lead Statistician (Hypothesis & Power Analysis) |
| **Aufar Radifan** | 1314624044 | Analysis Layer (STAT) | Data Simulation & Statistical Diagnostics |

---

## Log Kontribusi Mingguan

### Minggu 1: Perencanaan, Inisialisasi & Interface Contract
* **[Nama Anggota 1]:** Inisialisasi struktur repositori, konfigurasi `.gitignore`, setup `requirements.txt`, dan menyusun kerangka Interface Contract. *(Tautan Commit: `commit-hash-01`)*
* **[Nama Anggota 2]:** Setup proyek Supabase, menyusun `schema.sql`, dan mengonfigurasi Row Level Security (RLS). *(Tautan Commit: `commit-hash-02`)*
* **[Nama Anggota 3]:** Merumuskan hipotesis formal `H₀` dan `H₁`, menghitung Power Analysis untuk ukuran sampel `N`. *(Tautan Commit: `commit-hash-03`)*
* **[Nama Anggota 4]:** Menulis modul pengujian asumsi (Shapiro-Wilk dan Levene) di `stats_engine.py`. *(Tautan Commit: `commit-hash-04`)*

---

### Minggu 2: Eksekusi, Integrasi & Konsultasi
* **[Nama Anggota 1]:** Mengembangkan antarmuka web Streamlit (Halaman survei Varian A/B dan form input). *(Tautan Commit: `commit-hash-05`)*
* **[Nama Anggota 2]:** Menghubungkan client Supabase ke Streamlit (`db.py`) dan menerapkan proteksi password halaman admin. *(Tautan Commit: `commit-hash-06`)*
* **[Nama Anggota 3]:** Mengembangkan script simulasi data Monte Carlo `simulate_data.py`. *(Tautan Commit: `commit-hash-07`)*
* **[Nama Anggota 4]:** Mengintegrasikan komputasi Welch's t-test dan Z-test proporsi ke dashboard. *(Tautan Commit: `commit-hash-08`)*

---

### Minggu 3: Pengujian, Evaluasi Silang, Demo & Teardown
* **[Nama Anggota 1 & 2]:** Deployment web ke PaaS publik, pencatatan bukti monitoring, dan penulisan `docs/runbook.md` & `docs/cost-report.md`. *(Tautan Commit: `commit-hash-09`)*
* **[Nama Anggota 3 & 4]:** Finalisasi `docs/analysis-report.md`, eksekusi evaluasi silang `docs/cross-review.md`. *(Tautan Commit: `commit-hash-10`)*
* **Seluruh Anggota:** Perekaman video demo YouTube dan pelaksanaan prosedur *teardown* cloud.
