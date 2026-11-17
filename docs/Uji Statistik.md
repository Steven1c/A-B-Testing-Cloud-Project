# Laporan Analisis: Tingkat Kepuasan Pembelajaran (Luring vs. Daring) Menggunakan Uji Mann-Whitney U

## 1. Latar Belakang dan Tujuan Analisis

Platform Surverimen ini dirancang untuk membandingkan tingkat kepuasan peserta didik terhadap dua metode pembelajaran: **Luring (Tatap Muka/Offline)** dan **Daring (Online)**.

Melalui aplikasi web yang dibangun pada *Infrastructure Layer*, setiap pengunjung dialokasikan secara acak (rasio 50:50) ke dalam salah satu dari dua skenario:

- **Grup A (Kontrol):** Skenario/simulasi pembelajaran Luring
- **Grup B (Eksperimen):** Skenario/simulasi pembelajaran Daring

Metrik utama yang diukur adalah **Skor Kepuasan Pembelajaran**, menggunakan skala ordinal (skala Likert 1 sampai 5, di mana 1 = Sangat Tidak Puas dan 5 = Sangat Puas).

## 2. Perumusan Hipotesis (H₀ dan H₁)

Karena data yang dikumpulkan berskala ordinal (bertingkat), ukuran pemusatan data yang paling tepat adalah **median** atau distribusi peringkat (*mean rank*), bukan rata-rata (*mean*).

Rumusan hipotesis statistik dua arah (*two-tailed*) untuk eksperimen ini:

- **Hipotesis Nol (H₀):** Tidak ada perbedaan yang signifikan pada median skor kepuasan pembelajaran antara Grup Luring (A) dan Grup Daring (B).
- **Hipotesis Alternatif (H₁):** Terdapat perbedaan yang signifikan pada median skor kepuasan pembelajaran antara Grup Luring (A) dan Grup Daring (B).

## 3. Pemilihan Uji Statistik dan Justifikasi Metode

Uji statistik yang digunakan pada backend (melalui `stats_engine.py`) adalah **Mann-Whitney U Test** (atau *Wilcoxon rank-sum test*).

**Justifikasi pemilihan metode:**

1. **Sifat data ordinal.** Skala kepuasan 1-5 bukan data numerik kontinu. Jarak antara pilihan 3 (Netral) ke 4 (Puas) belum tentu setara secara psikologis dengan jarak 4 ke 5. Uji Mann-Whitney adalah metode non-parametrik yang dirancang untuk membandingkan *peringkat (rank)* data ordinal, sehingga hasilnya lebih akurat daripada memaksakan penggunaan *t-test*.
2. **Bebas asumsi distribusi (non-parametrik).** Uji ini tidak mensyaratkan data berdistribusi normal atau memiliki varians homogen. Hal ini membuat analisis *robust* terhadap jawaban ekstrem atau distribusi yang condong ke satu sisi (misalnya mayoritas responden memilih angka 4 atau 5).

## 4. Parameter Eksperimen dan *Power Analysis*

Agar eksperimen valid dan memiliki daya deteksi statistik yang memadai, mesin analisis mensyaratkan jumlah sampel minimum sebelum menarik kesimpulan:

- **Tingkat signifikansi (α):** 0,05 (toleransi *Type I error* sebesar 5%).
- **Target daya uji (*statistical power*, 1 − β):** 0,80 (80%).
- **Ukuran sampel minimum (N):** Berdasarkan estimasi ukuran efek menengah (*medium effect size*), dibutuhkan minimum **64 responden per grup** (total N ≥ 128).
- **Aturan eksekusi:** Jika total sampel belum memenuhi N ≥ 128, sistem akan menampilkan status "Pengumpulan data belum mencapai target Power Analysis".

## 5. Keamanan dan Anonimitas Data

Data respons dikumpulkan murni untuk analisis perilaku/preferensi (berupa ID grup dan skor 1-5). Sesuai batasan proyek, eksperimen ini **tidak mengumpulkan Informasi Identitas Pribadi (PII)** seperti nama atau email, sehingga kepatuhan privasi terjaga sepenuhnya.

## 6. Penafsiran Hasil dan Batas Kesimpulan

Keputusan akhir didasarkan pada *p-value* yang dihasilkan uji Mann-Whitney:

- **Tolak H₀** jika *p-value* < 0,05. Disimpulkan bahwa terdapat perbedaan tingkat kepuasan yang signifikan secara statistik antara metode Luring dan Daring. Grup dengan median lebih tinggi dinilai lebih unggul.
- **Gagal menolak H₀** jika *p-value* ≥ 0,05. Disimpulkan bahwa belum ada bukti statistik yang cukup untuk menyatakan bahwa satu format lebih baik daripada yang lain pada sampel ini.

**Batasan kesimpulan (*limitations*):**
Kesimpulan uji ini terbatas pada variabel internal platform dan tidak memperhitungkan faktor eksternal yang tidak terukur, seperti kecepatan internet responden saat simulasi Daring atau kenyamanan ruangan saat simulasi Luring. Interpretasi dibatasi pada persepsi yang diukur dari halaman web simulasi selama eksperimen berjalan.
