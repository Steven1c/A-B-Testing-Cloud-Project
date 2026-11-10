# Analysis Report: Tingkat Kepuasan Pembelajaran (Luring vs. Daring) Menggunakan Uji Mann Whitney U Test

## 1. Latar Belakang dan Tujuan Analisis

Platform Surverimen ini dirancang untuk membandingka tingkat kepuasan peserta didik terhadap dua metode  pembelajaran: **Luring (Tatap Muka/Offline)** dan **Daring (Online)**.

Melalui aplikasi web yang dibangun pada *Infrastructure Layer*, setiap pengunjung akan dialokasikan secara acak (rasio 50:50) ke dalam salah satu dari dua skenario:

* **Grup A (Kontrol):** Skenario/Simulasi Pembelajaran Luring

* **Grup B (Eksperimen):** Skenario/Simulasi Pembelajaran Daring

Metrik utama yang diukur adalah **Skor Kepuasan Pembelajaran**, diukur menggunakan skala ordinal (skala Likert 1 hingga 5, di mana 1 = Sangat Tidak Puas, 5 = Sangat Puas).

## 2. Perumusan Hipotesis ($H_0$ dan $H_1$)

Karena data yang dikumpulkan berskala ordinal (bertingkat), ukuran pemusatan data yang paling merepresentasikan hasil adalah **median** atau distribusi peringkat (*mean rank*), bukan rata-rata mutlak (*mean*).

Rumusan hipotesis statistik dua arah (*two-tailed*) untuk eksperimen ini adalah:

* **Hipotesis Nol (**$H_0$**):** Tidak ada perbedaan yang signifikan pada median skor kepuasan pembelajaran antara Grup Luring (A) dan Grup Daring (B).

* **Hipotesis Alternatif (**$H_1$**):** Terdapat perbedaan yang signifikan pada median skor kepuasan pembelajaran antara Grup Luring (A) dan Grup Daring (B).

## 3. Pemilihan Uji Statistik dan Justifikasi Metode

Uji statistik yang digunakan pada backend (melalui `stats_engine.py`) adalah **Mann-Whitney U Test** (atau *Wilcoxon rank-sum test*).

**Justifikasi Pemilihan Metode:**

1. **Sifat Data Ordinal:** Skala kepuasan 1-5 bukan merupakan data kontinu numerik. Jarak interval antara pilihan 3 (Netral) ke 4 (Puas) belum tentu ekuivalen secara psikologis dengan 4 ke 5. Uji Mann-Whitney adalah metode non-parametrik yang dirancang khusus untuk membandingkan *peringkat (rank)* dari data ordinal, sehingga hasilnya jauh lebih akurat daripada memaksakan penggunaan *t-test*.

2. **Bebas Asumsi Distribusi (Distribusi Bebas/Non-Parametrik):** Uji ini tidak mewajibkan asumsi bahwa data harus berdistribusi normal atau memiliki varians yang homogen. Hal ini membuat model analisis sangat kebal (*robust*) terhadap jawaban ekstrem atau distribusi data yang condong ke satu sisi (misalnya mayoritas responden menekan angka 4 atau 5).

## 4. Parameter Eksperimen dan *Power Analysis*

Agar eksperimen ini valid dan memiliki daya deteksi statistik yang memadai, mesin analisis mensyaratkan batas pengumpulan sampel minimum sebelum kesimpulan:

* **Tingkat Signifikansi (**$\alpha$**):** 0.05 (Tingkat toleransi *Type I error* sebesar 5%).

* **Target Daya Uji (*Statistical Power* /** $1-\beta$**):** 0.80 (80%).

* **Ukuran Sampel Minimum (**$N$**):** Berdasarkan estimasi ukuran efek menengah (*medium effect size*), syarat jumlah responden minimum sebesar **64 sampel per grup** (total $N \ge 128$).

* *Aturan Eksekusi:* Jika sistem mendeteksi total sampel belum memenuhi $N \ge 128$, maka sistem akan memberikan status "Pengumpulan data belum mencapai target Power Analysis".

## 5. Keamanan dan Anonimitas Data

Data respons dikumpulkan murni untuk analisis perilaku/preferensi (berupa ID grup dan skor 1-5). Sesuai dengan batasan proyek, eksperimen ini **tidak mengumpulkan Informasi Identitas Pribadi (PII)** seperti nama atau *email*, memastikan 100% kepatuhan privasi.

## 6. Penafsiran Hasil dan Batas Kesimpulan

Hasil akhir analisis diputuskan berdasarkan nilai *p-value* yang dikembalikan oleh algoritma uji Mann-Whitney:

* **Tolak** $H_0$**:** Jika *p-value* < 0.05. Disimpulkan bahwa secara statistik terdapat perbedaan tingkat kepuasan yang terbukti signifikan antara metode Luring dan Daring. (Grup dengan median lebih tinggi dinilai lebih superior).

* **Gagal Menolak** $H_0$**:** Jika *p-value* $\ge$ 0.05. Disimpulkan bahwa belum ada bukti statistik yang cukup untuk menyatakan format yang satu lebih baik daripada yang lain pada sampel ini.

**Batas Kesimpulan (Limitations):**
Kesimpulan uji ini bersifat terbatas pada variabel internal platform dan tidak memperhitungkan faktor eksternal tak terukur, seperti kecepatan sinyal internet personal responden saat simulasi skenario Daring atau kenyamanan fisik ruang saat simulasi Luring. Interpretasi dibatasi hanya pada persepsi yang diukur dari halaman web simulasi saat eksperimen berjalan.