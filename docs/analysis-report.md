# Laporan Metodologi & Hasil Analisis Statistik (Analysis Layer)

**Studi Kasus:** Komparasi Tingkat Kepuasan Pembelajaran: Luring (Varian A - Kontrol) vs. Daring (Varian B - Eksperimen)  
**Metode Inferensial:** Mann-Whitney U Test (Wilcoxon Rank-Sum Test) Dua Arah  
**Penanggung Jawab:** Aufar Radifan (Analysis Layer - Statistika)

---

## 1. Latar Belakang dan Tujuan Analisis

Platform survei dan eksperimen A/B ini dibangun untuk mengevaluasi perbedaan persepsi kepuasan mahasiswa terhadap dua moda pembelajaran: **Luring (Tatap Muka di Kelas fisik)** sebagai kelompok kontrol (Varian A), dan **Daring (Online via Video Conference & LMS)** sebagai kelompok eksperimen (Varian B).

Melalui arsitektur web layer, setiap responden dialokasikan secara acak (rasio *traffic splitting* 50:50) ke dalam salah satu dari dua kelompok perlakuan:
* **Grup A (Kontrol):** Menerima stimulus skenario pembelajaran Luring.
* **Grup B (Eksperimen):** Menerima stimulus skenario pembelajaran Daring.

Metrik utama yang diuji adalah **Skor Kepuasan Pembelajaran Keseluruhan (`sat_overall`)**, yang diukur menggunakan skala Likert ordinal 5 poin:
* `1` = Sangat Tidak Puas
* `2` = Tidak Puas
* `3` = Netral
* `4` = Puas
* `5` = Sangat Puas

---

## 2. Perumusan Hipotesis Statistik (H₀ dan H₁)

Karena data kepuasan berskala ordinal, parameter pemusatan yang tepat untuk diuji adalah **median** atau distribusi peringkat (*mean rank*), bukan rata-rata aritmetika (*mean*).

Rumusan hipotesis inferensial dua arah (*two-tailed*):
* **Hipotesis Nol (H₀):** Tidak ada perbedaan signifikan pada median / distribusi peringkat skor kepuasan pembelajaran antara metode Luring (Grup A) dan Daring (Grup B).
  ```text
  H₀: Median_A = Median_B  (atau P(X_A > X_B) = 0.5)
  ```
* **Hipotesis Alternatif (H₁):** Terdapat perbedaan signifikan pada median / distribusi peringkat skor kepuasan pembelajaran antara metode Luring (Grup A) dan Daring (Grup B).
  ```text
  H₁: Median_A ≠ Median_B  (atau P(X_A > X_B) ≠ 0.5)
  ```

---

## 3. Pemilihan Uji Statistik dan Justifikasi Metode

Mesin inferensi pada backend (`src/analysis/stats_engine.py`) mengimplementasikan **Mann-Whitney U Test** (dengan koreksi *ties* dan kontinuitas):

1. **Karakteristik Data Ordinal:** Skala Likert 1–5 bukan interval kontinu. Jarak psikologis antara skor 1 ke 2 tidak dapat dijamin setara dengan jarak antara skor 4 ke 5. Uji Mann-Whitney bekerja berdasarkan pemeringkatan data (*ranks*), sehingga terhindar dari bias asumsi skala interval pada *t-test*.
2. **Bebas Asumsi Distribusi (Non-Parametrik):** Uji ini tidak mensyaratkan normalitas populasi maupun homogenitas varians residual, sehingga sangat tahan (*robust*) terhadap skewness atau penumpukan skor responden pada batas atas (efek *ceiling*).
3. **Ukuran Efek (Effect Size):** Menggunakan korelasi rank-biserial (*r_B*):
   ```text
   r_B = (2 * U) / (n_A * n_B) - 1
   ```
   Rentang nilai r_B berkisar antara -1 hingga +1, mengukur keunggulan stokastik relatif Varian A terhadap Varian B.
4. **Selang Kepercayaan (Confidence Interval):** Menggunakan estimasi selisih median Hodges-Lehmann dengan metode *bootstrap resampling* (default 2000 iterasi, α = 0.05).

---

## 4. Power Analysis & Penentuan Ukuran Sampel

Untuk memastikan uji memiliki sensitivitas statistik yang cukup dalam mendeteksi perbedaan tanpa risiko *Type II error* (β):

* **Tingkat Signifikansi (α):** 0.05 (toleransi kesalahan tipe I sebesar 5%).
* **Daya Uji Statistik (1 - β):** 0.80 (80%).
* **Ukuran Efek (Effect Size Target):** Efek moderat (*medium effect size*, rank-biserial correlation ~ 0.35).
* **Ukuran Sampel Minimum:** Diperlukan minimum **N = 64 responden per varian (Total N ≥ 128 responden)**.
* **Aturan Eksekusi UI:** Jika sampel terkumpul belum mencapai batas minimum (N < 10 per grup untuk eksekusi fungsi, atau total N < 128 untuk konklusi formal), sistem analitik menampilkan status bahwa data belum memenuhi target *Power Analysis*.

---

## 5. Simulasi Data Survei (Monte Carlo Generator)

Untuk memfasilitasi pengujian end-to-end tanpa menunggu responden riil terkumpul, sistem dilengkapi modul simulasi Monte Carlo (`src/analysis/simulate_data.py`).

Distribusi probabilitas multinomial dirancang berdasarkan 5 dimensi evaluasi:
1. **Kepuasan Keseluruhan (`sat`):** Mengukur kepuasan umum, ekspektasi, efektivitas, dan preferensi penerapan.
2. **Pemahaman Materi (`mat`):** Mengukur kemudahan pemahaman, kejelasan dosen, retensi memori, dan kesiapan ujian.
3. **Interaksi & Keterlibatan (`int`):** Mengukur interaksi dosen, umpan balik, kerja sama tim, dan fokus belajar.
4. **Fleksibilitas & Lingkungan (`flx`):** Mengukur efisiensi waktu, fleksibilitas lokasi, kenyamanan ruangan, dan ritme belajar.
5. **Dukungan Teknis (`eff`/`tec`):** Mengukur aksesibilitas materi, stabilitas koneksi/fasilitas, pengumpulan tugas, dan administrasi presensi.

---

## 6. Penafsiran Hasil dan Batas Kesimpulan

Keputusan statistik ditarik secara otomatis berdasarkan *p-value* dua arah:
* **Tolak H₀ (p-value < 0.05):** Terdapat bukti statistik yang cukup bahwa terdapat perbedaan distribusi kepuasan antara metode pembelajaran Luring dan Daring. Varian dengan median lebih tinggi dinilai lebih memuaskan mahasiswa.
* **Gagal Menolak H₀ (p-value ≥ 0.05):** Tidak cukup bukti statistik untuk menyatakan adanya perbedaan tingkat kepuasan antara kedua metode pembelajaran pada tingkat signifikansi 5%.

**Batasan Studi (*Limitations*):**
Kesimpulan inferensial ini terikat pada instrumen persepsi yang diisi responden pada sesi survei dan tidak mengontrol variabel perancu eksternal (seperti variasi kecepatan internet personal responden daring atau suhu/akustik ruang kelas luring).
