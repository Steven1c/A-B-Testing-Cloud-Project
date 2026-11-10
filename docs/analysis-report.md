# Laporan Metodologi & Hasil Analisis Statistik (Analysis Layer)

## 1. Perumusan Masalah & Hipotesis Statistik

Eksperimen ini menguji efektivitas penambahan elemen *Social Proof* dan *Urgency Badge* pada landing page terhadap minat dan kesediaan membayar program pelatihan data.

### Hipotesis Uji Utama (Skor Kesediaan Membayar - Metrik Kontinu):
* **H₀: μ_B ≤ μ_A** (Rata-rata kesediaan membayar pada Varian B tidak lebih tinggi dibanding Varian A).
* **H₁: μ_B > μ_A** (Rata-rata kesediaan membayar pada Varian B secara signifikan lebih tinggi dibanding Varian A — *Uji Satu Arah / One-tailed*).

### Hipotesis Uji Sekunder (Tingkat Konversi Klik - Metrik Proporsi):
* **H₀: p_B = p_A** (Proporsi klik tombol pendaftaran Varian B sama dengan Varian A).
* **H₁: p_B ≠ p_A** (Proporsi klik tombol pendaftaran Varian B berbeda signifikan dari Varian A).

---

## 2. Power Analysis & Penentuan Ukuran Sampel

Sebelum pengumpulan data, ukuran sampel minimum dihitung menggunakan *Power Analysis* untuk mencegah risiko kesalahan tipe II (*underpowered test*):

* **Tingkat Signifikansi (α):** 0.05
* **Daya Uji Statistik (1 - β):** 0.80 (80%)
* **Minimum Detectable Effect Size (Cohen's d):** 0.35 (efek moderat-rendah)
* **Hasil Perhitungan:** Diperlukan sampel minimum **N = 130 per varian (Total N = 260 responden)**.

---

## 3. Pemeriksaan Asumsi Statistik

1. **Uji Normalitas Residual (Shapiro-Wilk):**
   * Diuji secara terpisah pada grup A dan grup B. Jika p-value > 0.05, asumsi distribusi normal terpenuhi.
2. **Uji Homogenitas Varians (Levene's Test):**
   * Diuji untuk memeriksa kesamaan varians antar dua populasi. Jika p-value ≤ 0.05, varians tidak sama, sehingga digunakan varian *Welch's t-test* (tanpa asumsi equal variance).

---

## 4. Hasil Inferensial & Kesimpulan

* **Statistik Uji:** Dilaporkan nilai t-hitung, derajat bebas (df), dan p-value.
* **95% Confidence Interval:** Interval estimasi selisih parameter rata-rata `(μ_B - μ_A)`.
* **Bahasa Keputusan Formal:**
  * Wajib menggunakan format: **"Tolak H₀"** atau **"Gagal menolak H₀"**.
  * Dilengkapi interpretasi praktis batasan generalisasi kesimpulan.
