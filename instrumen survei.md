# Instrumen Survei Uji A/B: Tingkat Kepuasan Pembelajaran (Luring vs. Daring)

Daftar 20 butir pertanyaan survei yang terbagi ke dalam **5 dimensi utama** (masing-masing 4 pertanyaan), pemetaan kolom database. Instrumen ini dirancang khusus untuk analisis non-parametrik **Mann-Whitney U Test**.

## 1. Spesifikasi Eksperimen & Kepatuhan Privasi

* **Metode Pengundian (*Traffic Splitting*):** Acak 50:50 saat pengunjung membuka halaman survei.
  * **Varian A (Kontrol):** Pembelajaran Luring (Tatap Muka di Kelas).
  * **Varian B (Eksperimen):** Pembelajaran Daring (Online via *Video Conference* & LMS).
* **Skala Pengukuran:** Skala Likert Ordinal 5 Poin (`1` = Sangat Tidak Puas, `2` = Tidak Puas, `3` = Netral, `4` = Puas, `5` = Sangat Puas).
* **Target Sampel Minimum:** minimal 64 responden per grup (Total minimal 128)

## 2. Skenario Stimulus Halaman Web

Sebelum butir pertanyaan ditampilkan, halaman web wajib menampilkan konteks skenario sesuai varian yang didapatkan responden agar persepsi penilaian seragam:

### Tampilan Varian A (Kontrol — Pembelajaran Luring)

> **Konteks Skenario: Pembelajaran Luring (Tatap Muka)**
> * Perkuliahan dilaksanakan secara tatap muka langsung di ruang kelas kampus sesuai jadwal tetap.
> * Materi disampaikan melalui papan tulis/proyektor dengan diskusi interaktif secara fisik bersama dosen dan rekan kelas.
> * Presensi, tanya jawab, dan evaluasi dilakukan langsung di dalam ruangan kelas.

### Tampilan Varian B (Eksperimen — Pembelajaran Daring)

> **Konteks Skenario: Pembelajaran Daring (Online)**
> * Perkuliahan dilaksanakan secara jarak jauh melalui platform konferensi video (*Zoom/Google Meet*) dan LMS.
> * Materi disampaikan melalui berbagi layar (*screen sharing*) serta rekaman digital yang dapat diakses ulang.
> * Presensi, diskusi melalui kolom *chat/mic*, dan pengumpulan tugas dilakukan sepenuhnya secara online.

## 3. Daftar Butir Pertanyaan Survei (5 Dimensi × 4 Pertanyaan)

Pada aplikasi web, responden Varian A hanya melihat teks versi **[Varian A — Luring]**, sedangkan responden Varian B hanya melihat teks versi **[Varian B — Daring]**.

---

### Dimensi 1: Kepuasan & Efektivitas Keseluruhan (*Overall Satisfaction*)

| No | Kolom DB | Redaksi Pertanyaan (Varian A: Luring vs. Varian B: Daring) | Peran Analisis |
| :--- | :--- | :--- | :--- |
| **Q1** | `sat_overall` | **[Varian A — Luring]:** Secara keseluruhan, seberapa puas Anda dengan pengalaman mengikuti metode pembelajaran Luring (tatap muka di kelas)? 
**[Varian B — Daring]:** Secara keseluruhan, seberapa puas Anda dengan pengalaman mengikuti metode pembelajaran Daring (online via Zoom/LMS)? | **Metrik Utama Uji Hipotesis (H0 vs H1)** |
| **Q2** | `sat_expectation` | **[Varian A — Luring]:** Seberapa puas Anda dengan kesesuaian proses pembelajaran Luring terhadap ekspektasi belajar Anda? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kesesuaian proses pembelajaran Daring terhadap ekspektasi belajar Anda? | Metrik Diagnostik |
| **Q3** | `sat_effectiveness` | **[Varian A — Luring]:** Seberapa puas Anda terhadap efektivitas pencapaian tujuan perkuliahan melalui metode Luring? 
**[Varian B — Daring]:** Seberapa puas Anda terhadap efektivitas pencapaian tujuan perkuliahan melalui metode Daring? | Metrik Diagnostik |
| **Q4** | `sat_preference` | **[Varian A — Luring]:** Seberapa puas Anda apabila metode pembelajaran Luring ini terus diterapkan pada mata kuliah serupa? 
**[Varian B — Daring]:** Seberapa puas Anda apabila metode pembelajaran Daring ini terus diterapkan pada mata kuliah serupa? | Metrik Diagnostik |

---

### Dimensi 2: Pedagogis & Pemahaman Materi (*Material Comprehension*)

| No | Kolom DB | Redaksi Pertanyaan (Varian A: Luring vs. Varian B: Daring) | Peran Analisis |
| :--- | :--- | :--- | :--- |
| **Q5** | `mat_comprehension` | **[Varian A — Luring]:** Seberapa puas Anda terhadap kemudahan memahami konsep perkuliahan melalui metode Luring (tatap muka langsung)? 
**[Varian B — Daring]:** Seberapa puas Anda terhadap kemudahan memahami konsep perkuliahan melalui metode Daring (konferensi video & modul digital)? | Metrik Diagnostik |
| **Q6** | `mat_clarity` | **[Varian A — Luring]:** Seberapa puas Anda dengan kejelasan penyampaian penjelasan dosen melalui papan tulis/proyektor pada perkuliahan Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kejelasan penyampaian penjelasan dosen melalui berbagi layar (*screen sharing*) pada perkuliahan Daring? | Metrik Diagnostik |
| **Q7** | `mat_retention` | **[Varian A — Luring]:** Seberapa puas Anda terhadap daya ingat dan pemahaman jangka panjang materi setelah mengikuti kelas Luring? 
**[Varian B — Daring]:** Seberapa puas Anda terhadap daya ingat dan pemahaman jangka panjang materi setelah mengikuti kelas Daring? | Metrik Diagnostik |
| **Q8** | `mat_readiness` | **[Varian A — Luring]:** Seberapa puas Anda dengan tingkat kesiapan Anda mengerjakan tugas atau ujian setelah mengikuti pembelajaran Luring?
**[Varian B — Daring]:** Seberapa puas Anda dengan tingkat kesiapan Anda mengerjakan tugas atau ujian setelah mengikuti pembelajaran Daring? | Metrik Diagnostik |

---

### Dimensi 3: Interaksi & Keterlibatan Belajar (*Interaction & Engagement*)

| No | Kolom DB | Redaksi Pertanyaan (Varian A: Luring vs. Varian B: Daring) | Peran Analisis |
| :--- | :--- | :--- | :--- |
| **Q9** | `int_lecturer` | **[Varian A — Luring]:** Seberapa puas Anda terhadap kemudahan mengajukan pertanyaan langsung kepada dosen pada perkuliahan Luring?
**[Varian B — Daring]:** Seberapa puas Anda terhadap kemudahan mengajukan pertanyaan (via *mic*/kolom *chat*) kepada dosen pada perkuliahan Daring? | Metrik Diagnostik |
| **Q10** | `int_feedback` | **[Varian A — Luring]:** Seberapa puas Anda dengan kecepatan dan kejelasan umpan balik (*feedback*) dosen saat diskusi Luring di kelas? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kecepatan dan kejelasan umpan balik (*feedback*) dosen saat diskusi Daring di ruang virtual? | Metrik Diagnostik |
| **Q11** | `int_peers` | **[Varian A — Luring]:** Seberapa puas Anda dengan kualitas komunikasi dan diskusi kelompok bersama rekan kelas dalam pembelajaran Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kualitas komunikasi dan diskusi kelompok bersama rekan kelas dalam pembelajaran Daring? | Metrik Diagnostik |
| **Q12** | `int_focus` | **[Varian A — Luring]:** Seberapa puas Anda dengan kemampuan menjaga fokus dan konsentrasi penuh selama mengikuti sesi pembelajaran Luring di ruang kelas? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kemampuan menjaga fokus dan konsentrasi penuh selama mengikuti sesi pembelajaran Daring dari jarak jauh? | Metrik Diagnostik |

---

### Dimensi 4: Fleksibilitas & Kenyamanan Lingkungan (*Flexibility & Environment*)

| No | Kolom DB | Redaksi Pertanyaan (Varian A: Luring vs. Varian B: Daring) | Peran Analisis |
| :--- | :--- | :--- | :--- |
| **Q13** | `flx_time` | **[Varian A — Luring]:** Seberapa puas Anda dengan keteraturan dan efisiensi pengaturan waktu pada metode pembelajaran Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan efisiensi waktu belajar dan penghematan waktu perjalanan pada metode pembelajaran Daring? | Metrik Diagnostik |
| **Q14** | `flx_location` | **[Varian A — Luring]:** Seberapa puas Anda dengan pelaksanaan perkuliahan Luring yang terpusat di ruang kelas kampus? 
**[Varian B — Daring]:** Seberapa puas Anda dengan fleksibilitas lokasi belajar yang dapat diakses dari mana saja pada perkuliahan Daring? | Metrik Diagnostik |
| **Q15** | `flx_comfort` | **[Varian A — Luring]:** Seberapa puas Anda terhadap kenyamanan fisik ruang kelas dalam mendukung proses pembelajaran Luring? 
**[Varian B — Daring]:** Seberapa puas Anda terhadap kenyamanan suasana ruang belajar mandiri dalam mendukung proses pembelajaran Daring? | Metrik Diagnostik |
| **Q16** | `flx_pace` | **[Varian A — Luring]:** Seberapa puas Anda dengan ritme dan kecepatan penyampaian materi secara langsung pada kelas Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan keleluasaan mengatur ritme belajar ulang (melalui rekaman/materi LMS) pada kelas Daring? | Metrik Diagnostik |

---

### Dimensi 5: Dukungan Teknis & Kelancaran Operasional (*Technical & Operational Flow*)

| No | Kolom DB | Redaksi Pertanyaan (Varian A: Luring vs. Varian B: Daring) | Peran Analisis |
| :--- | :--- | :--- | :--- |
| **Q17** | `tec_access` | **[Varian A — Luring]:** Seberapa puas Anda dengan kemudahan mengakses bahan ajar cetak/papan tulis saat perkuliahan Luring berlangsung? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kemudahan mengunduh dan mengakses file materi digital pada platform LMS Daring? | Metrik Diagnostik |
| **Q18** | `tec_stability` | **[Varian A — Luring]:** Seberapa puas Anda dengan kelancaran jalannya perkuliahan Luring tanpa gangguan fasilitas ruang kelas (audio/proyektor)? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kelancaran jalannya perkuliahan Daring tanpa gangguan koneksi internet maupun kendala teknis aplikasi? | Metrik Diagnostik |
| **Q19** | `tec_submission` | **[Varian A — Luring]:** Seberapa puas Anda dengan mekanisme pengumpulan tugas dan pelaksanaan evaluasi secara langsung pada perkuliahan Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan mekanisme pengumpulan tugas dan pelaksanaan evaluasi berbasis sistem online pada perkuliahan Daring? | Metrik Diagnostik |
| **Q20** | `tec_attendance` | **[Varian A — Luring]:** Seberapa puas Anda dengan kejelasan prosedur presensi dan administrasi kehadiran pada perkuliahan Luring? 
**[Varian B — Daring]:** Seberapa puas Anda dengan kejelasan prosedur presensi dan pencatatan kehadiran otomatis pada perkuliahan Daring? | Metrik Diagnostik |

---

## 4. Skema Tabel Database SQL (`schema.sql`)

```sql
CREATE TABLE survey_responses (
    id SERIAL PRIMARY KEY,
    variant_group CHAR(1) NOT NULL CHECK (variant_group IN ('A', 'B')),
    
    -- Dimensi 1: Kepuasan & Efektivitas Keseluruhan (Q1 = Metrik Utama)
    sat_overall SMALLINT NOT NULL CHECK (sat_overall BETWEEN 1 AND 5),
    sat_expectation SMALLINT NOT NULL CHECK (sat_expectation BETWEEN 1 AND 5),
    sat_effectiveness SMALLINT NOT NULL CHECK (sat_effectiveness BETWEEN 1 AND 5),
    sat_preference SMALLINT NOT NULL CHECK (sat_preference BETWEEN 1 AND 5),
    
    -- Dimensi 2: Pedagogis & Pemahaman Materi
    mat_comprehension SMALLINT NOT NULL CHECK (mat_comprehension BETWEEN 1 AND 5),
    mat_clarity SMALLINT NOT NULL CHECK (mat_clarity BETWEEN 1 AND 5),
    mat_retention SMALLINT NOT NULL CHECK (mat_retention BETWEEN 1 AND 5),
    mat_readiness SMALLINT NOT NULL CHECK (mat_readiness BETWEEN 1 AND 5),
    
    -- Dimensi 3: Interaksi & Keterlibatan Belajar
    int_lecturer SMALLINT NOT NULL CHECK (int_lecturer BETWEEN 1 AND 5),
    int_feedback SMALLINT NOT NULL CHECK (int_feedback BETWEEN 1 AND 5),
    int_peers SMALLINT NOT NULL CHECK (int_peers BETWEEN 1 AND 5),
    int_focus SMALLINT NOT NULL CHECK (int_focus BETWEEN 1 AND 5),
    
    -- Dimensi 4: Fleksibilitas & Kenyamanan Lingkungan
    flx_time SMALLINT NOT NULL CHECK (flx_time BETWEEN 1 AND 5),
    flx_location SMALLINT NOT NULL CHECK (flx_location BETWEEN 1 AND 5),
    flx_comfort SMALLINT NOT NULL CHECK (flx_comfort BETWEEN 1 AND 5),
    flx_pace SMALLINT NOT NULL CHECK (flx_pace BETWEEN 1 AND 5),
    
    -- Dimensi 5: Dukungan Teknis & Kelancaran Operasional
    tec_access SMALLINT NOT NULL CHECK (tec_access BETWEEN 1 AND 5),
    tec_stability SMALLINT NOT NULL CHECK (tec_stability BETWEEN 1 AND 5),
    tec_submission SMALLINT NOT NULL CHECK (tec_submission BETWEEN 1 AND 5),
    tec_attendance SMALLINT NOT NULL CHECK (tec_attendance BETWEEN 1 AND 5),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_survey_variant_group ON survey_responses (variant_group);
```