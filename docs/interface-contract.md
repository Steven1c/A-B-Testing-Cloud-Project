# Interface Contract — Platform Survei & Uji A/B

**Versi:** 1.0 · **Tanggal:** 10 November 2026 · **Penanggung jawab:** Aufar Radifan(Data Integration)
**Layer terhubung:** Analysis (`src/analysis/`) ↔ Infrastructure & Operations (`src/app/`, `src/infra/`)
**Stack:** Streamlit (PaaS) + Supabase PostgreSQL

**Studi:** skor kepuasan pembelajaran (Likert 1–5), Luring (Varian A) vs Daring (Varian B), uji Mann-Whitney U dua arah.
H₀: tidak ada perbedaan signifikan pada median (distribusi peringkat) skor antara Luring dan Daring. H₁: ada perbedaan signifikan.

## 1. Format input (survei → database → analisis)

| Field | Tipe | Aturan |
|---|---|---|
| `response_id` | UUID | otomatis, primary key |
| `session_id` | string ≤ 64 | anonim, acak, unik (1 jawaban per sesi) |
| `variant` | `'A'` / `'B'` | A = Luring, B = Daring |
| `score` | integer | 1–5 (1 = sangat tidak puas, 5 = sangat puas) |
| `created_at` | timestamp UTC | otomatis oleh database |

Tanpa data pribadi (nama, email, NIM, IP). Data simulasi (`simulate_data.py`) memakai kolom dan aturan yang sama. Constraint `UNIQUE`, `CHECK (variant IN ('A','B'))`, dan `CHECK (score BETWEEN 1 AND 5)` ada di `schema.sql`.

## 2. Format output (analisis → dashboard)

`test_name` (`"mann_whitney_u"`), `n_a`, `n_b`, `median_a`, `median_b`, `statistic` (U), `p_value` (0–1, dua arah, koreksi *ties*), `effect_size` (rank-biserial), `ci_lower`, `ci_upper` (selang kepercayaan 1 − α; metode: _Hodges–Lehmann / bootstrap, isi sesuai kesepakatan_), `alpha` (0.05), `decision` (`"tolak H0"` / `"gagal menolak H0"`, tolak jika p < α), `interpretation` (kalimat Bahasa Indonesia).

## 3. Jadwal / pemicu eksekusi

- **Simpan jawaban:** langsung saat pengguna menekan "Kirim".
- **Hitung uji:** sesuai permintaan, saat halaman hasil dibuka atau tombol "Perbarui hasil" ditekan. Hasil di-*cache* maksimal 60 detik. Tidak ada job terjadwal.
- **Backup database:** _isi, sesuai keputusan tim Infrastructure_.

## 4. Fungsi antar-layer

```python
# src/app/db.py
insert_response(session_id: str, variant: str, score: int) -> str   # response_id
fetch_scores() -> dict[str, list[int]]                               # {"A": [...], "B": [...]}

# src/analysis/stats_engine.py
run_mann_whitney(scores_a, scores_b, alpha=0.05) -> TestResult       # field = Bagian 2

# src/analysis/simulate_data.py
generate_responses(n_a: int, n_b: int, seed: int | None = None) -> DataFrame
```
Exception bersama: `InvalidScoreError`, `InvalidVariantError`, `InsufficientSampleError`, `DuplicateSessionError`, `DatabaseUnavailableError`.

## 5. Target kinerja (usulan, diukur di Minggu 2)

| Operasi | Target |
|---|---|
| Muat halaman survei | ≤ 3 detik |
| Simpan jawaban | ≤ 2 detik |
| Hitung uji (N hingga 10.000) | ≤ 2 detik |
| Tampilkan halaman hasil | ≤ 5 detik |

## 6. Perilaku saat gagal

Ukuran sampel minimum: **`MIN_N` = _isi_ per varian** (dari perhitungan ukuran sampel dan daya uji di `analysis-report.md`).

| Kondisi | Dideteksi di | Perilaku | Data disimpan? | Pesan ke pengguna |
|---|---|---|---|---|
| Skor kosong | `main.py` | blok tombol kirim | Tidak | "Pilih satu skor (1–5) sebelum mengirim." |
| Skor di luar 1–5 / bukan integer | `main.py` + DB | tolak | Tidak | "Skor tidak valid. Pilih 1 sampai 5." |
| Varian kosong / bukan A/B | `main.py` + DB | tolak | Tidak | "Pilih metode: Luring atau Daring." |
| Jawaban ganda satu sesi | `db.py` (UNIQUE) | tolak | Hanya yang pertama | "Anda sudah mengisi survei ini." |
| Sampel per varian < `MIN_N` | `stats_engine.py` | uji tidak dihitung | n/a | "Data belum cukup (min. `MIN_N` per metode). Saat ini: Luring n=…, Daring n=…." |
| Database/layanan tidak merespons | `db.py` | retry 2×, lalu gagal | Tidak | "Layanan sedang tidak tersedia. Coba lagi nanti." |
| Galat tak terduga | `main.py` | catat ke log, tanpa stack trace ke pengguna | Tidak | "Terjadi kesalahan. Silakan coba lagi." |

## 7. Riwayat revisi dan persetujuan

Perubahan setelah Minggu 1 dicatat sebagai revisi bertanggal, disetujui kedua layer.

| Versi | Tanggal | Perubahan | Disetujui (Analysis / Infra) |
|---|---|---|---|
| 1.0 | _isi_ | Kontrak awal | _nama_ / _nama_ |
