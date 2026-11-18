# PRD — Aplikasi Web Platform Survei & Uji A/B

**Versi:** 1.0 · **Tanggal:** 18 November 2026  
**Penanggung Jawab:** Muhamad Hafiz (Infrastructure & Operations Layer)  
**Stack:** Python · Streamlit · Supabase PostgreSQL · Plotly · SciPy  
**Deployment Target:** Render (PaaS) — kredensial via Environment Variables (`os.getenv`)

---

## 1. Tujuan Produk

Membangun satu aplikasi web Streamlit (`src/app/main.py`) yang menjalankan dua fungsi utama:
1. **Survei Responden** — mengumpulkan skor kepuasan pembelajaran (Likert 1–5) dari responden yang dialokasikan secara acak ke Varian A (Luring) atau Varian B (Daring).
2. **Dashboard Analisis Admin** — menjalankan uji Mann-Whitney U atas data terkumpul dan menampilkan hasil inferensial secara visual.

---

## 2. Arsitektur Navigasi

Aplikasi dibagi menjadi dua area via `st.sidebar`:

```
Sidebar
├── 📋 Survei         ← halaman publik (default)
└── 📊 Dashboard      ← halaman admin, dilindungi password
```

**Halaman Survei** terdiri dari dua step yang dikendalikan `st.session_state`:

```
st.session_state["step"]
├── "scenario"   → Step 1: Halaman Stimulus Skenario
└── "questions"  → Step 2: Halaman Kuesioner
```

---

## 3. Spesifikasi Halaman Survei

### 3.1 Inisialisasi Sesi

Ketika responden pertama kali membuka halaman, sistem melakukan hal berikut secara otomatis:
- Generate `session_id` unik: `uuid.uuid4().hex[:16]` → disimpan di `st.session_state["session_id"]`.
- Alokasi varian secara acak 50:50: `random.choice(["A", "B"])` → disimpan di `st.session_state["variant"]`.
- Set `st.session_state["step"] = "scenario"`.
- Set `st.session_state["submitted"] = False`.

Jika `st.session_state["submitted"] == True`, semua step dilewati dan langsung tampil **halaman terima kasih**.

---

### 3.2 Step 1 — Halaman Stimulus Skenario

**Tujuan:** Membangun persepsi konteks penilaian responden sebelum mengisi kuesioner.

**Komponen UI:**

| Elemen | Detail |
|---|---|
| Header | `st.title("Survei Kepuasan Pembelajaran")` |
| Subheader | "Anda mendapatkan skenario berikut:" |
| Kotak stimulus | `st.info(...)` — isi berbeda per varian (lihat 3.2.1 dan 3.2.2) |
| Instruksi | Paragraf singkat: "Bayangkan Anda mengikuti perkuliahan dengan metode di atas. Jawablah pertanyaan berikut berdasarkan persepsi Anda." |
| Tombol aksi | `st.button("Mulai Mengisi Survei →")` → set `session_state["step"] = "questions"` |

#### 3.2.1 Stimulus Varian A (Luring)

> **Konteks Skenario: Pembelajaran Luring (Tatap Muka)**
> - Perkuliahan dilaksanakan secara tatap muka langsung di ruang kelas kampus sesuai jadwal tetap.
> - Materi disampaikan melalui papan tulis/proyektor dengan diskusi interaktif secara fisik bersama dosen dan rekan kelas.
> - Presensi, tanya jawab, dan evaluasi dilakukan langsung di dalam ruangan kelas.

#### 3.2.2 Stimulus Varian B (Daring)

> **Konteks Skenario: Pembelajaran Daring (Online)**
> - Perkuliahan dilaksanakan secara jarak jauh melalui platform konferensi video (Zoom/Google Meet) dan LMS.
> - Materi disampaikan melalui berbagi layar (screen sharing) serta rekaman digital yang dapat diakses ulang.
> - Presensi, diskusi melalui kolom chat/mic, dan pengumpulan tugas dilakukan sepenuhnya secara online.

---

### 3.3 Step 2 — Halaman Kuesioner

**Tujuan:** Mengumpulkan 20 skor Likert 1–5 dari responden.

**Tata Letak:**

```
┌─────────────────────────────────────────────────┐
│  [Label varian] "Anda menilai: Pembelajaran     │
│   Luring / Daring"                              │
│                                                 │
│  ★ PERTANYAAN UTAMA (Q1 — sat_overall)          │
│  "Secara keseluruhan, seberapa puas Anda..."    │
│  ○ 1   ○ 2   ○ 3   ○ 4   ○ 5                   │
│  Label: Sangat Tidak Puas ... Sangat Puas       │
│                                                 │
│  ▼ Kepuasan & Efektivitas (Q2–Q4)               │
│  ▼ Pedagogis & Pemahaman Materi (Q5–Q8)         │
│  ▼ Interaksi & Keterlibatan (Q9–Q12)            │
│  ▼ Fleksibilitas & Lingkungan (Q13–Q16)         │
│  ▼ Dukungan Teknis (Q17–Q20)                    │
│                                                 │
│  [Kirim Respons]  ← disabled kalau ada yg kosong│
└─────────────────────────────────────────────────┘
```

**Detail Komponen:**

| Elemen | Implementasi |
|---|---|
| Label varian | `st.caption(...)` menampilkan varian yang didapat |
| Q1 (metrik utama) | `st.radio` dengan marker `#### ⬛ Pertanyaan Utama` di atas |
| Q2–Q20 | Masing-masing `st.radio` di dalam `st.expander` per dimensi |
| Label skala | Teks kecil di bawah radio: `1 = Sangat Tidak Puas ... 5 = Sangat Puas` |
| Validasi | Tombol "Kirim Respons" dinonaktifkan (`disabled=True`) selama ada pertanyaan yang belum dijawab (`None`) |
| Submit | Memanggil `db.insert_response(session_id, variant, score, **diagnostic_scores)` → set `submitted = True` → rerun ke halaman terima kasih |
| Error handling | Catch `DuplicateSessionError` → tampil warning "Anda sudah mengisi survei ini." |

**Teks pertanyaan** per varian mengikuti `docs/survey-instrument.md` secara verbatim — teks Varian A untuk kelompok A, teks Varian B untuk kelompok B.

---

### 3.4 Halaman Terima Kasih

Ditampilkan setelah `submitted == True`:
- `st.success("Terima kasih! Respons Anda telah berhasil disimpan.")`
- Tampilkan varian yang didapat dan skor Q1 yang diberikan.
- Tombol "Isi Ulang Survei (Sesi Baru)" → reset seluruh `session_state` dan rerun (untuk testing/demo).

---

## 4. Spesifikasi Halaman Dashboard Analisis

### 4.1 Autentikasi

```python
password = st.text_input("Password Admin", type="password")
if password != os.getenv("ADMIN_PASSWORD", "admin123"):
    st.warning("Password salah.")
    st.stop()
```

Password default fallback `"admin123"` hanya untuk mode lokal. Di Render, diisi via Environment Variable `ADMIN_PASSWORD`.

---

### 4.2 Tata Letak Dashboard

```
┌──────────────────────────────────────────────────────┐
│  📊 Dashboard Analisis — Mann-Whitney U Test         │
│                                                      │
│  Progress Sampel:                                    │
│  [████████░░░░░░░░░░░░] N=89/128 (69%)              │
│  Luring (A): 45 responden | Daring (B): 44 responden│
│                                                      │
│  [⚠ Banner kuning jika N < 64 per varian]           │
│                                                      │
│  ┌── KPI Cards ──────────────────────────────────┐  │
│  │ Median A │ Median B │ U statistic │ p-value   │  │
│  │ Effect size (r_B) │ 95% CI │ N per varian     │  │
│  └───────────────────────────────────────────────┘  │
│                                                      │
│  Keputusan: ✅ TOLAK H₀ / ℹ️ GAGAL MENOLAK H₀      │
│  Interpretasi: [teks dari result.interpretation]    │
│                                                      │
│  [Bar Chart Distribusi Skor] [Box/Violin Plot]       │
│                                                      │
│  [Perbarui Hasil]   [Injeksi Data Simulasi (N=70)]  │
└──────────────────────────────────────────────────────┘
```

---

### 4.3 Komponen Dashboard

#### Progress Bar & Banner Peringatan

```python
total_n = len(scores_a) + len(scores_b)
st.progress(min(total_n / 128, 1.0), text=f"N = {total_n} / 128 target")

if min(len(scores_a), len(scores_b)) < 10:
    st.error("Sampel belum cukup untuk menjalankan uji (min. 10 per varian).")
    # tombol Perbarui Hasil di-disable
elif min(len(scores_a), len(scores_b)) < 64:
    st.warning("Sampel belum mencapai target Power Analysis (N = 64 per varian). Interpretasi bersifat tentatif.")
```

#### KPI Cards

Gunakan `st.columns(4)` untuk menampilkan:
- **Median A** dan **Median B**
- **U statistic**
- **p-value** (merah jika < 0.05, hijau jika ≥ 0.05)
- **Effect size** (rank-biserial r_B)
- **95% CI** (Hodges-Lehmann bootstrap)
- **N per varian**

#### Keputusan & Interpretasi

```python
if result.decision == "tolak H0":
    st.success(f"✅ TOLAK H₀ — {result.interpretation}")
else:
    st.info(f"ℹ️ GAGAL MENOLAK H₀ — {result.interpretation}")
```

#### Grafik (Plotly)

**Grafik 1 — Bar Chart Distribusi Skor:**
- X: Skor (1–5), Y: Proporsi (%), warna: Varian A (biru) vs Varian B (oranye).
- `st.plotly_chart(fig, use_container_width=True)`

**Grafik 2 — Box Plot / Violin Plot:**
- X: Varian (A / B), Y: Skor `sat_overall`.
- Tampilkan median line dan jitter titik data individual.

#### Tombol Aksi

| Tombol | Fungsi |
|---|---|
| `Perbarui Hasil` | Panggil `db.fetch_scores()` → `run_mann_whitney()` → cache hasil di `st.session_state["last_result"]` dengan timestamp. Cache kadaluarsa setelah 60 detik. |
| `Injeksi Data Simulasi (N=70 per varian)` | Panggil `generate_responses(70, 70, seed=42)` → loop `db.insert_response()` per baris → tampilkan `st.toast("140 baris data simulasi berhasil diinjeksi.")` |

---

## 5. Validasi & Error Handling

| Kondisi | Lokasi Deteksi | Respons UI |
|---|---|---|
| Q1 / pertanyaan belum diisi | `main.py` (Step 2) | Tombol "Kirim" dinonaktifkan |
| Skor di luar 1–5 | `db.py` → `InvalidScoreError` | `st.error("Skor tidak valid.")` |
| Varian bukan A/B | `db.py` → `InvalidVariantError` | `st.error("Varian tidak valid.")` |
| Jawaban ganda satu sesi | `db.py` → `DuplicateSessionError` | `st.warning("Anda sudah mengisi survei ini.")` |
| N per varian < `MIN_N` (10) | `stats_engine.py` → `InsufficientSampleError` | Tombol "Perbarui Hasil" dinonaktifkan + `st.error(...)` |
| DB tidak merespons | `db.py` → `DatabaseUnavailableError` | `st.error("Layanan sedang tidak tersedia. Coba lagi nanti.")` |

---

## 6. Konfigurasi Deployment (Render)

**Start Command:**
```bash
streamlit run src/app/main.py --server.port $PORT --server.address 0.0.0.0
```

**Environment Variables yang wajib diisi di Render:**

| Variable | Keterangan |
|---|---|
| `SUPABASE_URL` | URL project Supabase |
| `SUPABASE_KEY` | Anon public key Supabase |
| `ADMIN_PASSWORD` | Password halaman dashboard analisis |

**File `render.yaml`:**
```yaml
services:
  - type: web
    name: ab-testing-survey
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run src/app/main.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: ADMIN_PASSWORD
        sync: false
```

---

## 7. Dependensi

`requirements.txt` sudah mencakup seluruh dependensi yang dibutuhkan:
```
streamlit>=1.30.0
supabase>=2.3.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
python-dotenv>=1.0.0
plotly>=5.18.0
```

---

## 8. Ringkasan File yang Dimodifikasi / Dibuat

| File | Status | Keterangan |
|---|---|---|
| `src/app/main.py` | **Ditulis Ulang** | Implementasi penuh UI survei multi-step + dashboard analisis |
| `render.yaml` | **Dibuat Baru** | Konfigurasi auto-deploy ke Render |
| `src/app/db.py` | Selesai | `insert_response` + `fetch_scores` sudah sesuai kontrak |
| `src/errors.py` | Selesai | Semua custom exception sudah tersedia |
| `src/analysis/stats_engine.py` | Tidak diubah | Sudah benar sesuai kontrak |
| `src/analysis/simulate_data.py` | Selesai | `generate_responses` sudah sesuai kontrak |
