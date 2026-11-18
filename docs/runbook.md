# Runbook Operasional & Panduan Penggelaran (Infrastructure Layer)

Dokumen ini adalah panduan teknis operasional untuk mereproduksi, menguji, mengoperasikan, menggelar (*deploy*), dan membersihkan (*teardown*) seluruh sistem Platform Survei & Uji A/B dari awal.

---

## 1. Menjalankan di Lingkungan Lokal

### 1.1 Prasyarat Sistem
* **Python:** Versi 3.10 atau lebih baru (direkomendasikan Python 3.11 atau 3.12).
* **Git:** Versi 2.30+.
* **OS:** Windows, Linux, atau macOS.

### 1.2 Langkah Instalasi & Menjalankan
1. **Kloning Repositori:**
   ```bash
   git clone https://github.com/mhmdhafiz07/Platform-Survei-Uji-AB.git
   cd Platform-Survei-Uji-AB
   ```

2. **Buat & Aktifkan Virtual Environment:**
   ```bash
   python -m venv .venv

   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1

   # Windows (Command Prompt):
   .venv\Scripts\activate.bat

   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Pasang Seluruh Dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Variabel Lingkungan (.env):**
   Salin berkas template konfigurasi:
   ```bash
   # Windows:
   copy src\config\.env.example .env

   # Linux / macOS:
   cp src/config/.env.example .env
   ```

   Buka berkas `.env` dan sesuaikan nilainya:
   ```ini
   SUPABASE_URL="https://your-project.supabase.co"
   SUPABASE_KEY="your-anon-public-key"
   ADMIN_PASSWORD="admin123"
   ```
   *(Jika nilai `SUPABASE_URL` atau `SUPABASE_KEY` dibiarkan kosong, sistem otomatis berjalan dalam mode In-Memory Mock Storage).*

5. **Jalankan Aplikasi Streamlit:**
   ```bash
   streamlit run src/app/main.py
   ```
   Aplikasi akan terbuka otomatis pada peramban di alamat `http://localhost:8501`.

---

## 2. Prosedur Pengujian Otomatis (Automated Testing)

Sebelum melakukan deployment atau demonstrasi, jalankan automated test suite untuk memastikan seluruh kontrak data dan modul inferensial valid:

```bash
# Pengujian standar unit dan kontrak antarmuka:
pytest -v

# Pengujian komprehensif termasuk integrasi database dan validasi error:
# Windows (PowerShell):
Set-Item -Path env:RUN_DB_TESTS -Value 1; pytest -v

# Linux / macOS:
RUN_DB_TESTS=1 pytest -v
```

### Cakupan Pengujian (37 Test Cases):
* **Integritas Kontrak Data:** 20 butir unik, kecocokan instrumen pertanyaan, konsistensi skema SQL DDL, dan rentang skor 1–5.
* **Simulasi Monte Carlo:** Validasi kolom hasil simulasi, keunikan `session_id`, alokasi varian A/B, dan batasan nilai Likert.
* **Mesin Analisis Statistik:** Uji Mann-Whitney U, p-value range `[0, 1]`, Effect Size Rank-Biserial `[-1, 1]`, Hodges-Lehmann Bootstrap CI, dan evaluasi aturan keputusan hipotesis.
* **Validasi Database:** Penolakan nilai di luar skala (skor < 1 atau > 5), penolakan varian tidak valid, penolakan survei tidak lengkap, pencegahan sesi duplikat, dan kebenaran bentuk data pengambilan skor.

---

## 3. Setup Database Supabase Cloud (Managed PostgreSQL)

1. Buka konsol [supabase.com](https://supabase.com) dan buat proyek baru (*Region: Southeast Asia - Singapore*).
2. Masuk ke menu **SQL Editor**, buka file `src/infra/schema.sql`, salin seluruh kueri DDL, lalu klik tombol **Run**.
   * Skema akan membuat tabel `survey_responses` lengkap dengan 20 kolom butir ordinal (`q01_sat_satisfaction` s.d. `q20_tec_attendance`), kolom agregat `score`, index performa, trigger sinkronisasi otomatis, dan kebijakan Row Level Security (RLS).
3. Buka menu **Project Settings -> API**:
   * Salin nilai **Project URL** ke variabel `SUPABASE_URL` di berkas `.env`.
   * Salin nilai **Project API Keys (anon public)** ke variabel `SUPABASE_KEY` di berkas `.env`.

---

## 4. Panduan Operasional Dashboard & Skenario Live Demo

Bagi dosen penguji atau tim penilai yang ingin menguji alur kerja sistem:

### 4.1 Mengakses Halaman Administrator
1. Buka aplikasi web di `http://localhost:8501`.
2. Pada sidebar navigasi kiri, pilih opsi **Dashboard Analisis**.
3. Masukkan password admin (default: `admin123`) lalu klik **Masuk**. Sesi login tersimpan secara persisten selama peramban aktif.

### 4.2 Skenario Pengujian Cepat Menggunakan Toolbar Admin
Untuk mendemokan kalkulasi inferensial tanpa harus mengisi survei manual sebanyak 128 kali:
1. **Injeksi Data Uji (N=70/varian):**
   * Klik tombol **Injeksi Data Uji (N=70/grup)** di bagian atas dashboard.
   * Sistem akan meng-generate 140 data respons simulasi realistis (70 Luring, 70 Daring) ke dalam database.
   * Progress bar ketercapaian sampel otomatis terisi penuh dan menampilkan rasio **140 / 128 (109.4%)**.
   * Panel inferensial langsung menampilkan statistik Mann-Whitney U, p-value dua arah, ukuran efek *r_B*, selang kepercayaan Hodges-Lehmann, grafik distribusi Plotly, dan tabel diagnostik 20 butir.
2. **Uji Gatekeeping Sampel:**
   * Klik tombol **Reset Data (Hapus Semua)**.
   * Seluruh data terhapus. Dashboard seketika menampilkan banner penolakan inferensi karena sampel belum memenuhi batas minimum (N < 10 per varian).
3. **Pengisian Survei Mandiri:**
   * Pindah ke menu **Formulir Survei**.
   * Perhatikan stimulus visual dan narasi perkuliahan Varian A atau B yang terpilih secara acak.
   * Lengkapi seluruh 20 butir pertanyaan dan klik **Kirim Jawaban Survei**.
   * Kembali ke menu **Dashboard Analisis** untuk melihat respons yang baru saja masuk secara *real-time*.

---

## 5. Mekanisme Ketahanan Sistem (Graceful Degradation)

Aplikasi dirancang dengan arsitektur toleransi kesalahan (*fault-tolerant*):
* **Penyimpanan Ganda:** Modul `src/app/db.py` mengimplementasikan fallback transparan ke `sys._MOCK_SURVEY_STORAGE` lokal.
* **Deteksi Gangguan Jaringan:** Jika koneksi Supabase terputus, kredensial salah, atau kuota habis, aplikasi tidak akan *crash*, melainkan tetap melayani responden dan administrator menggunakan memori runtime lokal.
* **Penyelarasan Skema Otomatis:** Trigger database PostgreSQL di `schema.sql` secara otomatis menyinkronkan nilai `score` primer dari kolom `q01_sat_satisfaction` jika ada data legacy yang dimasukkan tanpa kolom spesifik.

---

## 6. Prosedur Deployment ke Cloud PaaS

### 6.1 Menggunakan Streamlit Community Cloud
1. Pastikan seluruh commit terbaru sudah di-push ke branch `main` repositori GitHub.
2. Akses [share.streamlit.io](https://share.streamlit.io) dan klik **Create app**.
3. Konfigurasikan parameter aplikasi:
   * **Repository:** `mhmdhafiz07/Platform-Survei-Uji-AB`
   * **Branch:** `main`
   * **Main file path:** `src/app/main.py`
4. Buka menu **Advanced settings -> Secrets**, lalu tempelkan konfigurasi:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-public-key"
   ADMIN_PASSWORD = "your-admin-password"
   ```
5. Klik **Deploy**. Aplikasi akan online dalam waktu ~1–2 menit pada domain publik bertarif gratis dengan sertifikat SSL/HTTPS aktif.

---

## 7. Prosedur Pembersihan Resource Cloud (Teardown)

Sesuai instruksi resmi brief tugas komputasi awan, seluruh layanan cloud wajib dihapus setelah presentasi dan penilaian berakhir untuk memastikan tagihan tetap **\$0.00**:

1. **Teardown Database Supabase:**
   * Buka dashboard Supabase -> Pilih proyek -> Masuk ke **Project Settings -> General**.
   * Gulir ke bawah hingga bagian **Danger Zone** -> Klik **Delete Project**.
   * Masukkan nama proyek untuk konfirmasi penghapusan permanen.
2. **Teardown Hosting PaaS:**
   * Buka dashboard Streamlit Community Cloud -> Pilih aplikasi.
   * Klik ikon menu titik tiga -> Pilih **Delete app**.
3. **Verifikasi Billing:**
   * Periksa konsol akun penyedia untuk memastikan tidak ada instance, storage, atau compute resource aktif yang tertinggal.
   * Dokumentasikan screenshot saldo/tagihan \$0.00 ke dalam folder `docs/evidence/teardown_billing.png`.
