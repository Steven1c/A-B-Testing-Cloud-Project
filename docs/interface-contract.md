# Interface Contract — Platform Survei & Uji A/B

**Versi:** 1.3 · **Tanggal:** _isi (tanggal revisi terakhir)_ · **Penanggung jawab:** Aufar Radifan (Data Integration)
**Layer terhubung:** Analysis (`src/analysis/`) ↔ Infrastructure & Operations (`src/app/`, `src/infra/`)
**Stack:** Streamlit (PaaS) + Supabase PostgreSQL

**Studi:** skor kepuasan pembelajaran (Likert 1–5), Luring (Varian A, kontrol) vs Daring (Varian B, eksperimen). Metrik utama **Q1 `sat_overall`**, diuji dengan Mann-Whitney U dua arah. Q2–Q20 hanya deskriptif (median per varian).
H₀: tidak ada perbedaan signifikan pada median (distribusi peringkat) Q1 antara Luring dan Daring. H₁: ada perbedaan signifikan.
**Konstanta bersama** (`src/contract.py`): `MIN_N` = 10 per varian (batas agar uji dihitung), `TARGET_N` = 64 per varian dan `TARGET_TOTAL_N` = 128 (target sampel dari power analysis), `PRIMARY_ITEM` = `sat_overall`, `ITEM_COLUMNS` (20 butir).

## 1. Format input (survei → database → analisis)

Tabel `survey_responses`, satu baris = satu responden anonim. Kolom yang ditulis `insert_response`:

| Field | Tipe | Aturan |
|---|---|---|
| `response_id` | UUID (string) | dibuat aplikasi |
| `session_id` | string ≤ 64 | anonim, acak, unik (1 jawaban per `session_id`) |
| `variant`, `variant_group` | `'A'` / `'B'` | dua kolom berisi nilai sama; A = Luring, B = Daring; diundi aplikasi |
| `score` | integer 1–5 | salinan `sat_overall` (kompatibilitas kontrak v1.0) |
| 20 kolom butir | integer 1–5, wajib | `sat_overall`, `sat_expectation`, `sat_effectiveness`, `sat_preference` · `mat_comprehension`, `mat_clarity`, `mat_retention`, `mat_readiness` · `int_lecturer`, `int_feedback`, `int_peers`, `int_focus` · `flx_time`, `flx_location`, `flx_comfort`, `flx_pace` · `tec_access`, `tec_stability`, `tec_submission`, `tec_attendance` |
| `created_at` | timestamp UTC | otomatis oleh database |

`schema.sql` harus memuat **semua** kolom di atas beserta `UNIQUE` pada `session_id` dan `CHECK 1–5` pada tiap butir; kolom yang tidak ada membuat INSERT ditolak. Pemeriksaan otomatis: `tests/test_contract.py`. Skala: 1 = Sangat tidak puas … 5 = Sangat puas. Tanpa data pribadi.

## 2. Format output (analisis → dashboard)

**Uji utama:** `test_name` (`"mann_whitney_u"`), `outcome_column` (`"sat_overall"`), `n_a`, `n_b`, `median_a`, `median_b`, `statistic` (U), `p_value` (0–1, dua arah, koreksi *ties*), `effect_size` (rank-biserial), `ci_lower`, `ci_upper` (metode: _Hodges–Lehmann / bootstrap, isi sesuai kode_), `alpha` (0.05), `decision` (`"tolak H0"` jika p < α, selain itu `"gagal menolak H0"`), `interpretation`.
**Deskriptif per butir:** `item`, `n_a`, `n_b`, `median_a`, `median_b`.

## 3. Tampilan survei per varian

Alur dua tahap. **Tahap 1 (skenario):** teks konteks dan empat kartu aktivitas (pemaparan materi, diskusi kelompok, tanya jawab, pengerjaan tugas), masing-masing dengan foto bila berkas ada di `src/app/assets/variant_a/` atau `variant_b/`. **Tahap 2 (kuesioner):** Q1 sebagai pertanyaan utama, lalu Q2–Q20 per dimensi.

| Aspek | Varian A: Luring | Varian B: Daring |
|---|---|---|
| Skenario | Tatap muka di kelas; papan tulis/proyektor; presensi dan evaluasi langsung | Konferensi video (Zoom/Meet) dan LMS; berbagi layar dan rekaman; diskusi, presensi, dan tugas online |
| Kartu aktivitas | Versi kelas fisik | Versi online |
| Redaksi 20 butir | Versi Luring | Versi Daring |

- Kedua tampilan memakai skala, 20 butir, dan field simpan yang **sama**; hanya teks skenario, foto, dan redaksi butir yang berbeda.
- Tampilan dan `variant` yang tersimpan berasal dari satu nilai undian per sesi, tanpa input dari responden.
- Redaksi Q13–Q20 berbeda isi antar varian, sehingga hanya dibandingkan secara deskriptif.

## 4. Jadwal / pemicu eksekusi

- **Pengundian varian:** acak 50:50 (`random.choice`) sekali per sesi. "Mulai Sesi Baru" membuat `session_id` dan varian baru (keterbatasan: satu orang dapat mengirim lebih dari sekali).
- **Simpan jawaban:** saat "Kirim Jawaban" ditekan, hanya jika 20 butir terjawab.
- **Dashboard:** hanya untuk admin (kata sandi dari environment `ADMIN_PASSWORD`, tanpa nilai bawaan di produksi). Uji dihitung saat halaman dibuka; hasil di-*cache* 60 detik; "Perbarui Data" menghapus cache.
- **Operasi admin:** "Injeksi Data Uji (N=70/grup)" menulis data simulasi (`session_id` berawalan `sim_`); "Reset Data" menghapus seluruh baris. Keduanya hanya untuk pengujian dan harus dikosongkan sebelum pengumpulan data nyata.
- **Backup database:** _isi, sesuai keputusan Infrastructure_.

## 5. Fungsi antar-layer

```python
# src/app/db.py
insert_response(session_id: str, variant: str, answers: dict[str, int]) -> str   # response_id
fetch_scores() -> dict[str, list[int]]                       # Q1: {"A": [...], "B": [...]}
fetch_all_item_scores() -> dict[str, dict[str, list[int]]]   # {butir: {"A": [...], "B": [...]}}
fetch_all_responses() -> DataFrame                           # data mentah untuk dashboard
reset_database() -> int                                      # jumlah baris terhapus

# src/analysis/stats_engine.py
run_mann_whitney(scores_a, scores_b, alpha=0.05, outcome_column="sat_overall") -> TestResult
describe_items(item_scores) -> list[dict]

# src/analysis/simulate_data.py
generate_responses(n_a: int, n_b: int, seed: int | None = None) -> DataFrame   # session_id, variant_group, 20 butir
```
Exception bersama (`src/errors.py`): `InvalidScoreError`, `InvalidVariantError`, `IncompleteResponseError`, `InsufficientSampleError`, `DuplicateSessionError`, `DatabaseUnavailableError`.

## 6. Target kinerja dan hasil ukur

| Operasi | Target | Terukur (isi dari `evidence/response-time-log.md`) |
|---|---|---|
| Muat halaman survei | ≤ 3 detik | _isi atau "tidak diukur"_ |
| Simpan jawaban | ≤ 2 detik | _isi atau "tidak diukur"_ |
| Ambil data + hitung uji (N hingga 10.000) | ≤ 2 detik | _isi atau "tidak diukur"_ |
| Tampilkan dashboard | ≤ 5 detik | _isi atau "tidak diukur"_ |

## 7. Perilaku saat gagal

| Kondisi | Dideteksi di | Perilaku | Data disimpan? | Pesan ke pengguna |
|---|---|---|---|---|
| Butir belum lengkap | `main.py` + `db.py` | tombol kirim nonaktif | Tidak | "Jawab seluruh 20 pertanyaan sebelum mengirimkan formulir." |
| Skor di luar 1–5 / bukan integer | `db.py` + DB | tolak | Tidak | "Skor tidak valid. Pilih 1 sampai 5." |
| Varian bukan A/B | `db.py` + DB | tolak | Tidak | "Varian tidak valid. Muat ulang halaman." |
| `session_id` sama mengirim ulang | `db.py` (UNIQUE) | tolak | Hanya yang pertama | "Sesi ini sudah pernah mengirimkan jawaban survei." |
| Sampel per varian < `MIN_N` | `main.py` (gerbang) + `stats_engine.py` | uji tidak dihitung | n/a | "Sampel belum mencukupi … (minimum 10 per varian). Kondisi saat ini: Luring n=…, Daring n=…." |
| Kata sandi admin salah | `main.py` | akses ditolak | n/a | "Password salah. Silakan coba lagi." |
| Database/layanan tidak merespons | `db.py` | retry 2×, lalu gagal | Tidak | "Layanan sedang tidak tersedia. Coba lagi nanti." |
| Galat tak terduga | `main.py` | catat ke log, tanpa detail teknis | Tidak | "Terjadi kesalahan. Silakan coba lagi." |

Penyimpangan kode dari tabel ini dicatat di `docs/evidence/contract-check.md` (tes `xfail` di `tests/`).

## 8. Riwayat revisi dan persetujuan

Bukti kepatuhan: `docs/evidence/contract-check.md` dan `pytest tests/`.

| Versi | Tanggal | Perubahan | Disetujui (Analysis / Infra) |
|---|---|---|---|
| 1.0 | 10 Nov 2026 | Kontrak awal: satu skor per responden, tabel `responses` | Kamal / Hafiz |
| 1.1 | 13 Nov 2026 | Mengikuti instrumen 20 butir: tabel `survey_responses`, 20 kolom butir, `session_id` unik, uji utama pada Q1, `outcome_column`, `describe_items`, `IncompleteResponseError`, target 64 per varian | Kamal / Hafiz |
| 1.2 | 15 Nov 2026 | Web survei dengan dua tampilan berbeda (Luring/Daring), varian diundi acak per sesi | Kamal / Hafiz |
| 1.3 | 16 Nov 2026 | Menyelaraskan dengan implementasi: alur dua tahap dengan kartu aktivitas, kolom `variant`/`variant_group`/`score`, fungsi `fetch_all_responses` dan `reset_database`, konstanta `TARGET_N` dan `TARGET_TOTAL_N`, akses dashboard dengan kata sandi admin, operasi injeksi dan reset data, pesan gagal disamakan dengan UI | Kamal / Hafiz |
