# Laporan Estimasi & Realisasi Biaya Cloud

Dokumen pelaporan biaya komputasi awan sesuai rubrik *Operations, Cost & Security* untuk **Platform Survei & Uji A/B (Luring vs. Daring)**.

---

## 1. Estimasi Biaya Awal (Sebelum Deployment)

Estimasi dihitung menggunakan kalkulasi batas kuota gratis (*Free Tier*) dari penyedia layanan:

| Komponen Layanan | Penyedia | Metrik Penggunaan yang Diproyeksikan | Estimasi Biaya Bulanan |
| :--- | :--- | :--- | :--- |
| **Web Hosting PaaS** | Posit Connect Cloud | 1 Aplikasi Streamlit aktif, Shared vCPU & RAM, HTTPS otomatis | **\$0.00** (Free Tier) |
| **Managed Database** | Supabase PostgreSQL | Kapasitas < 50 MB (proyeksi hingga 1.000 baris respon), batas 500 MB | **\$0.00** (Free Tier hingga 500 MB) |
| **Bandwidth Keluar (Egress)** | Supabase / PaaS | < 100 MB per bulan (payload JSON REST API ringan) | **\$0.00** (Batas gratis hingga 2–5 GB) |
| **Source Control & CI/CD** | GitHub | 1 Repositori kolaborasi tim, integrasi *redeploy* ke PaaS | **\$0.00** (Free Plan) |
| **Total Estimasi Biaya** | - | - | **\$0.00 / bulan** |

---

## 2. Realisasi Biaya Aktual (Tagihan Riil)

- **Periode Proyek:** 3 Minggu (November 2026)
- **Tagihan Riil di Dashboard Billing:** **\$0.00** (Rp 0,-)
- **Selisih (Variance):** **\$0.00** (Realisasi sesuai dengan estimasi awal).

---

## 3. Analisis & Pembahasan Selisih Biaya

1. **Efisiensi Service Model PaaS & DBaaS:**
   Penggunaan kombinasi PaaS terkelola (**Posit Connect Cloud**) dan DBaaS (**Supabase**) berhasil menekan biaya operasional menjadi nol dolar dibandingkan menyewa Virtual Machine (IaaS) seperti AWS EC2 `t2.micro` yang berisiko mengenakan biaya apabila melewati kuota 750 jam *free tier*, serta tidak memerlukan verifikasi kartu kredit saat *deployment*.
2. **Efisiensi Kapasitas Penyimpanan:**
   Tabel `survey_responses` (25 kolom dengan tipe data numerik ringkas `SMALLINT` dan `UUID`) hanya membutuhkan ruang penyimpanan sekitar **~0,2 MB** untuk 260 baris data simulasi maupun respon riil ($N \ge 128$), jauh di bawah batas kuota gratis 500 MB Supabase (< 0,05% kapasitas).
3. **Pemberhentian Resource (Teardown) & Kebersihan Data:**
   Data uji coba dibersihkan sebelum pengumpulan sampel riil dimulai, dan seluruh *resource* aplikasi serta basis data dijadwalkan untuk dinonaktifkan (*teardown*) setelah evaluasi dan presentasi akhir selesai guna mencegah penumpukan *resource idle*.
