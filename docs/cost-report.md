# Laporan Estimasi & Realisasi Biaya Cloud

Dokumen pelaporan biaya komputasi awan sesuai rubrik *Operations, Cost & Security*.

---

## 1. Estimasi Biaya Awal (Sebelum Deployment)

Estimasi dihitung menggunakan kalkulasi batas kuota gratis (*Free Tier*) dari penyedia layanan:

| Komponen Layanan | Penyedia | Metrik Penggunaan yang Diproyeksikan | Estimasi Biaya Bulanan |
| :--- | :--- | :--- | :--- |
| **Web Hosting PaaS** | Streamlit Community Cloud | 1 App aktif, 1 GB RAM, Shared vCPU | **\$0.00** (Free Tier gratis permanen) |
| **Managed Database** | Supabase PostgreSQL | Kapasitas < 50 MB (proyeksi 1.000 baris respon), 500 MB limit | **\$0.00** (Free Tier hingga 500 MB) |
| **Bandwidth Keluar (Egress)** | Supabase / PaaS | < 100 MB per bulan (payload JSON ringan) | **\$0.00** (Batas gratis hingga 2–5 GB) |
| **Total Estimasi Biaya** | - | - | **\$0.00 / bulan** |

---

## 2. Realisasi Biaya Aktual (Tagihan Riil)

* **Periode Proyek:** 3 Minggu (Nov 2026)
* **Tagihan Riil di Dashboard Billing:** **\$0.00** (Rp 0,-)
* **Selisih (Variance):** **\$0.00** (Realisasi sesuai dengan estimasi awal).

---

## 3. Analisis & Pembahasan Selisih Biaya

1. **Efisiensi Service Model PaaS:**
   Penggunaan model PaaS terkelola berhasil menekan biaya operasional menjadi nol dolar dibanding menyewa Virtual Machine (IaaS) seperti AWS EC2 t2.micro yang mengenakan biaya jika melampaui 750 jam free tier.
2. **Kapasitas Penyimpanan:**
   Tabel `survey_responses` hanya membutuhkan ukuran penyimpanan ~0.2 MB untuk 260 baris data simulasi dan respon riil, jauh di bawah batas kuota gratis 500 MB Supabase.
3. **Pemberhentian Resource (Teardown):**
   Seluruh proyek dan database dihapus segera setelah presentasi berakhir untuk mencegah penumpukan resource idle.
