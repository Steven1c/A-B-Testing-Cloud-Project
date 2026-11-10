# Runbook Operasional & Panduan Penggelaran (Infrastructure Layer)

Dokumen ini menjelaskan langkah-langkah mereproduksi dan menjalankan sistem dari nol.

---

## 1. Menjalankan di Lingkungan Lokal

### Prasyarat:
* Python 3.10 atau lebih baru.
* Git.

### Langkah Eksekusi:
1. Clone repositori dan masuk ke direktori proyek:
   ```bash
   git clone <URL_REPOSITORY>
   cd Project
   ```
2. Buat virtual environment dan aktifkan:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. Pasang seluruh dependensi:
   ```bash
   pip install -r requirements.txt
   ```
4. Salin file environment:
   ```bash
   copy src\config\.env.example .env   # Windows
   cp src/config/.env.example .env      # Linux/macOS
   ```
5. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run src/app/main.py
   ```
   Aplikasi akan terbuka otomatis di peramban pada alamat `http://localhost:8501`.

---

## 2. Setup Database Supabase

1. Buka [supabase.com](https://supabase.com) dan buat proyek baru (Region: Singapore).
2. Masuk ke menu **SQL Editor**, buka file `src/infra/schema.sql`, salin seluruh isinya, dan klik **Run**.
3. Masuk ke **Project Settings -> API**, salin `Project URL` dan `anon public key` ke dalam file `.env`.

---

## 3. Deployment ke Cloud (PaaS)

### Menggunakan Streamlit Community Cloud:
1. Push repositori ini ke GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io).
3. Pilih repositori, branch `main`, dan set *Main file path* ke `src/app/main.py`.
4. Di bagian **Advanced Settings -> Secrets**, masukkan konfigurasi dari `.env`:
   ```toml
   SUPABASE_URL = "https://your-id.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ADMIN_PASSWORD = "your-admin-password"
   ```
5. Klik **Deploy**. Layanan akan online dengan URL publik HTTPS.

---

## 4. Prosedur Teardown (Pembersihan Resource)

Setelah presentasi dan penilaian selesai:
1. Masuk ke dashboard Supabase -> Project Settings -> General -> **Delete Project**.
2. Masuk ke dashboard Streamlit Cloud -> Settings -> **Delete App**.
3. Pastikan tidak ada resource komputasi atau database yang tersisa agar tidak menimbulkan tagihan tak terduga.
