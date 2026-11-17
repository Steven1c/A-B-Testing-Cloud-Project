# Catatan Peran & Kontribusi Individu (Role Log)

---

## Daftar Anggota & Pembagian Layer

| Nama Anggota         | NIM        | Layer Penugasan             | Peran Utama                                     |
| :-------------------- | :---------- | :--------------------------- | :----------------------------------------------- |
| **Muhammad Hafiz**    | 1314624047 | Infrastructure & Operations | Web Developer & Repo Setup                      |
| **Rizki Annisa** | 1314624051 | Infrastructure & Operations | Database Architect & Cloud Deployer             |
| **Musthafa Kamal** | 1314624013 | Analysis Layer              | Lead Statistician (Hypothesis & Power Analysis) |
| **Aufar Radifan**    | 1314624044 | Analysis Layer              | Data Simulation & Statistical Diagnostics       |

---

## Log Kontribusi Mingguan

### Minggu 1: Perencanaan, Inisialisasi & Interface Contract
- **Muhammad Hafiz:** Inisialisasi struktur repositori, konfigurasi `.gitignore`, setup `requirements.txt`, dan menyusun kerangka Interface Contract.
- **Rizki Annisa:** Setup proyek Supabase, menyusun `schema.sql`, dan mengonfigurasi Row Level Security (RLS).
- **Musthafa Kamal:** Merumuskan hipotesis formal `H₀` dan `H₁`, menghitung Power Analysis untuk ukuran sampel `N`.
- **Aufar Raifan:** Menulis modul pengujian asumsi (mann whitney) di `stats_engine.py`.

---

### Minggu 2: Eksekusi, Integrasi & Konsultasi
* **Muhammad Hafiz:** Merencanakan dan mengembangkan frontend web Streamlit (Halaman survei Varian A/B dan form input) dan scenario tiap varian.
* **Rizki Annisa:** Menghubungkan client Supabase ke Streamlit (`db.py`) dan menerapkan proteksi password halaman admin. 
* **Musthafa Kamal:** Mengembangkan script simulasi data Monte Carlo `simulate_data.py`.
* **Aufar Raifan:** Mengintegrasikan komputasi Welch's t-test dan Z-test proporsi ke dashboard.

---

### Minggu 3: Pengujian, Evaluasi Silang, Demo & Teardown
* **Muhammad Hafiz & Rizki Annisa:** Deployment web ke PaaS publik, pencatatan bukti monitoring, dan penulisan `docs/runbook.md` & `docs/cost-report.md`.
* **Musthafa Kamal & Aufar Raifan:** Finalisasi `docs/analysis-report.md`, eksekusi evaluasi silang `docs/cross-review.md`.
* **Rizki Annisa:** Perekaman video demo YouTube dan pelaksanaan prosedur *teardown* cloud.
