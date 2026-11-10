# Interface Contract — Platform Survei & Uji A/B

> Kontrak ini mengunci format data dan fungsi antara **Analysis Layer** (`src/analysis/`) dan **Infrastructure & Operations Layer** (`src/app/`, `src/infra/`). Perubahan apa pun harus mengikuti Bagian 8.

## 1. Ruang lingkup & versi

| Item | Isi |
|---|---|
| Versi | 1.0 (draf) |
| Tanggal | 10 November 2026 |
| Penanggung jawab | _nama kamu_ (Data Integration & Contract Specialist) |
| Layer terhubung | Analysis (`stats_engine.py`, `simulate_data.py`) ↔ App (`main.py`, `db.py`) ↔ Infra (`schema.sql`) |
| Stack | Streamlit (PaaS) + Supabase PostgreSQL |

**Konteks studi.** Membandingkan skor kepuasan pembelajaran (skala Likert 1–5) antara metode **Luring (Varian A)** dan **Daring (Varian B)**.

**Hipotesis (Mann-Whitney U, dua arah):**
- H₀: Tidak ada perbedaan signifikan pada median (distribusi peringkat) skor kepuasan antara Luring dan Daring.
- H₁: Ada perbedaan signifikan pada median (distribusi peringkat) skor kepuasan antara Luring dan Daring.

**Alasan memakai Mann-Whitney.** Data bersifat ordinal dan banyak nilai kembar (*ties*), sehingga uji berbasis peringkat lebih tepat daripada Welch's t-test atau Z-test. Konsekuensinya, `stats_engine.py` harus diubah dari Welch/Z menjadi Mann-Whitney.

## 2. Kontrak input (kuesioner → database → analisis)

Satu baris = satu jawaban dari satu sesi anonim.

| Field | Tipe | Aturan | Contoh |
|---|---|---|---|
| `response_id` | UUID | otomatis, unik (primary key) | `3f2a...` |
| `session_id` | string (maks 64) | anonim, acak, **1 jawaban per sesi** (unik) | `s_9c1e7b` |
| `variant` | enum (`'A'`/`'B'`) | A = Luring, B = Daring; huruf kapital | `'A'` |
| `score` | integer | hanya 1, 2, 3, 4, atau 5 | `4` |
| `created_at` | timestamp UTC | otomatis oleh database | `2026-11-10T08:15:00Z` |

**Skala `score`:** 1 = Sangat tidak puas, 2 = Tidak puas, 3 = Netral, 4 = Puas, 5 = Sangat puas.

**Larangan:** tidak boleh menyimpan data pribadi (nama, email, NIM, IP address).

**Format data sintetis** (`simulate_data.py`) harus identik: kolom `session_id`, `variant`, `score` dengan aturan di atas.

## 3. Kontrak output (analisis → dashboard)

| Field | Tipe | Keterangan |
|---|---|---|
| `test_name` | string | selalu `"mann_whitney_u"` |
| `n_a`, `n_b` | int | jumlah responden per varian |
| `median_a`, `median_b` | float | median skor per varian |
| `statistic` | float | statistik U (untuk Varian A) |
| `p_value` | float | 0 ≤ p ≤ 1, dua arah, dengan koreksi *ties* |
| `effect_size` | float | *rank-biserial correlation*, −1 s.d. 1 |
| `ci_lower`, `ci_upper` | float | selang kepercayaan (1 − α) untuk selisih lokasi (Hodges–Lehmann) atau selisih median hasil bootstrap; metode disepakati dengan tim Analysis |
| `alpha` | float | default 0.05 |
| `decision` | string | `"tolak H0"` atau `"gagal menolak H0"` |
| `interpretation` | string | kalimat singkat Bahasa Indonesia untuk dashboard |

Aturan keputusan: `decision = "tolak H0"` jika `p_value < alpha`, selain itu `"gagal menolak H0"`.

## 4. Signature fungsi antar-layer

### 4.1 `db.py` → dipanggil `main.py`

```python
def insert_response(session_id: str, variant: str, score: int) -> str:
    """Simpan satu jawaban. Return response_id (UUID string).
    Raises: DuplicateSessionError, DatabaseUnavailableError."""

def fetch_scores() -> dict[str, list[int]]:
    """Ambil semua skor per varian.
    Return: {"A": [..], "B": [..]}  (nilai 1-5)
    Raises: DatabaseUnavailableError."""
```

### 4.2 `stats_engine.py` → dipanggil `main.py`

```python
from dataclasses import dataclass
from typing import Sequence

@dataclass
class TestResult:
    test_name: str
    n_a: int
    n_b: int
    median_a: float
    median_b: float
    statistic: float
    p_value: float
    effect_size: float
    ci_lower: float
    ci_upper: float
    alpha: float
    decision: str
    interpretation: str

def run_mann_whitney(
    scores_a: Sequence[int],
    scores_b: Sequence[int],
    alpha: float = 0.05,
    alternative: str = "two-sided",
) -> TestResult:
    """Uji Mann-Whitney U antara Luring (A) dan Daring (B).
    Raises: InvalidScoreError (nilai di luar 1-5 / bukan integer),
            InsufficientSampleError (n per varian < MIN_N)."""
```

### 4.3 `simulate_data.py`

```python
def generate_responses(n_a: int, n_b: int, seed: int | None = None) -> "pandas.DataFrame":
    """Kolom: session_id (str), variant ('A'/'B'), score (int 1-5)."""
```

### 4.4 Exception bersama

| Exception | Dilempar oleh | Arti |
|---|---|---|
| `InvalidScoreError` | `stats_engine`, validasi `main.py` | skor bukan integer 1–5 |
| `InvalidVariantError` | `main.py`, `db.py` | varian selain `A`/`B` |
| `InsufficientSampleError` | `stats_engine` | sampel terlalu kecil untuk uji |
| `DuplicateSessionError` | `db.py` | sesi sudah pernah menjawab |
| `DatabaseUnavailableError` | `db.py` | database tidak terjangkau / timeout |

## 5. Pemetaan ke skema database (`schema.sql`)

```sql
CREATE TABLE responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  VARCHAR(64) NOT NULL UNIQUE,
    variant     CHAR(1)     NOT NULL CHECK (variant IN ('A', 'B')),
    score       SMALLINT    NOT NULL CHECK (score BETWEEN 1 AND 5),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Constraint `UNIQUE`, `CHECK`, dan `NOT NULL` adalah lapis pertahanan terakhir. Validasi utama tetap di aplikasi.

## 6. Target kinerja

> Angka berikut adalah usulan awal. Sepakati dengan tim Infrastructure dan sesuaikan dengan hasil ukur nyata.

| Operasi | Target | Cara ukur |
|---|---|---|
| Muat halaman survei | ≤ 3 detik | stopwatch/DevTools Network, rata-rata 10 kali |
| Submit jawaban (simpan ke DB) | ≤ 2 detik | `time.perf_counter()` di sekitar `insert_response` |
| Hitung uji (N total hingga 10.000) | ≤ 2 detik | `time.perf_counter()` di sekitar `run_mann_whitney` |
| Tampilkan dashboard hasil | ≤ 5 detik | stopwatch/DevTools Network, rata-rata 10 kali |

Bukti (screenshot atau log) disimpan di `docs/evidence/`.

## 7. Protokol error handling

Ukuran sampel minimum: **`MIN_N = 10` responden per varian** (usulan; sepakati dengan Analysis).

| Kondisi | Dideteksi di | Perilaku sistem | Data disimpan? | Pesan ke pengguna |
|---|---|---|---|---|
| Skor kosong / belum dipilih | `main.py` | blok tombol kirim | Tidak | "Pilih satu skor kepuasan (1–5) sebelum mengirim." |
| Skor di luar 1–5 atau bukan integer | `main.py` + CHECK DB | tolak | Tidak | "Skor tidak valid. Pilih angka 1 sampai 5." |
| Varian kosong / bukan A/B | `main.py` + CHECK DB | tolak | Tidak | "Metode pembelajaran tidak valid. Pilih Luring atau Daring." |
| Jawaban ganda dari sesi yang sama | `db.py` (UNIQUE) | tolak, tangkap `DuplicateSessionError` | Tidak (data pertama dipertahankan) | "Anda sudah mengisi survei ini. Terima kasih." |
| Sampel salah satu varian < `MIN_N` | `stats_engine.py` | lempar `InsufficientSampleError`, uji tidak dihitung | n/a | "Data belum cukup untuk uji (minimal 10 responden per metode). Saat ini: Luring n=…, Daring n=…." |
| Semua skor identik di kedua varian | `stats_engine.py` | uji tetap dijalankan, ditandai peringatan; p-value ditampilkan apa adanya | n/a | "Seluruh skor sama; hasil uji kurang informatif." |
| Database tidak terjangkau | `db.py` | retry 2 kali (jeda 1 detik), lalu lempar `DatabaseUnavailableError` | Tidak | "Layanan sedang tidak tersedia. Coba lagi beberapa saat." |
| Galat tak terduga | `main.py` | tangkap, catat ke log, jangan tampilkan stack trace | Tidak | "Terjadi kesalahan. Silakan coba lagi." |

Prinsip: validasi di tiga lapis (UI → fungsi → constraint DB), pesan ke pengguna selalu Bahasa Indonesia tanpa detail teknis, dan detail galat hanya masuk log.

## 8. Aturan perubahan kontrak

1. Perubahan hanya lewat penanggung jawab kontrak (Data Integration) setelah disetujui anggota Analysis dan Infrastructure.
2. Setiap perubahan menaikkan nomor versi dan dicatat di tabel riwayat di bawah.
3. Anggota layer terdampak diberi tahu lewat grup tim sebelum kode diubah, dan commit-nya merujuk nomor versi kontrak.

| Versi | Tanggal | Perubahan | Disetujui oleh |
|---|---|---|---|
| 1.0 | _isi_ | Draf awal | _isi_ |

## 9. Catatan koordinasi

- **Analysis:** `stats_engine.py` perlu memuat `run_mann_whitney` sesuai Bagian 4.2 (struktur repo awal menyebut Welch's t-test dan Z-test). Tentukan juga metode selang kepercayaan.
- **Infrastructure:** `schema.sql` mengikuti Bagian 5; `db.py` mengimplementasikan Bagian 4.1.
- **Keterbatasan desain:** varian (luring/daring) adalah metode yang dialami responden, bukan hasil penugasan acak, sehingga ini perbandingan observasional. Tulis catatan ini di `analysis-report.md`.
