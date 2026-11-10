# Analisis Keamanan & Skalabilitas Sistem

---

## 1. Aspek Keamanan (Security)

1. **Prinsip Least Privilege & Secrets Management:**
   * Kunci rahasia API dan password admin tidak pernah di-*hardcode* di dalam kode repositori.
   * File `.env` dikecualikan secara ketat melalui `.gitignore`.
   * Di lingkungan cloud, konfigurasi diinjeksi via *Environment Variables / Secrets Management* platform hosting.
2. **Enkripsi Data in Transit:**
   * Seluruh lalu lintas data antara pengguna, aplikasi Streamlit, dan database Supabase diwajibkan menggunakan protokol HTTPS/TLS (SSL Port 443 dan Port 5432 SSL).
3. **Privasi Data & Anonimitas:**
   * Sesuai ketentuan brief, sistem tidak mengumpulkan data pribadi (PII) seperti nama lengkap, alamat email, nomor telepon, atau alamat IP. Setiap responden hanya diidentifikasi oleh `session_id` acak.
4. **Row Level Security (RLS) di Database:**
   * Skema database membatasi izin publik hanya untuk `INSERT` respon baru. Operasi modifikasi `UPDATE` dan `DELETE` dinonaktifkan untuk publik.

---

## 2. Aspek Skalabilitas (Scalability) & Keputusan Autoscaling

1. **Karakteristik Beban Kerja Survei:**
   * Beban kerja survei ini bersifat *I/O-bound* ringan dengan konkurensi rendah hingga menengah (puncak trafik diperkirakan saat tautan disebarkan: ~10–50 concurrent users).
2. **Keputusan Autoscaling:**
   * **Tidak Diperlukan Autoscaling Horizontal yang Agresif:** Database Supabase sanggup menangani hingga 200–500 koneksi bersamaan (*connection pooling*) secara default pada tier gratis.
   * Aplikasi Streamlit PaaS secara otomatis mengalokasikan resource memori hingga 1 GB, yang lebih dari cukup untuk menangani data agregat 1.000 baris.
3. **Mitigasi Lonjakan Beban (High Load):**
   * Jika sistem menerima lonjakan trafik mendadak (misal 5.000 responden sekaligus), strategi mitigasinya adalah:
     1. Menambahkan koneksi via Supavisor (Connection Pooler port 6543) untuk mencegah *database connection exhaustion*.
     2. Menerapkan *caching* kueri pada halaman analisis (`@st.cache_data(ttl=60)`) agar kueri agregasi tidak dieksekusi ulang di setiap refresh halaman.
