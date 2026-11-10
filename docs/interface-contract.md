# Interface Contract Antar-Layer

*Disepakati pada akhir Minggu 1 antara Analysis Layer (STAT) dan Infrastructure & Operations Layer (STI).*

---

## 1. Spesifikasi Skema Database (`survey_responses`)

Koneksi pertukaran data antara aplikasi web (pengumpul data) dan script analitik dilakukan melalui satu tabel database PostgreSQL di Supabase:

| Nama Kolom | Tipe Data | Nullable | Deskripsi & Batasan Nilai |
| :--- | :--- | :--- | :--- |
| `id` | UUID | NO | Primary key otomatis (`gen_random_uuid()`) |
| `session_id` | TEXT | NO | ID unik per sesi pengisian responden |
| `assigned_variant` | CHAR(1) | NO | Pilihan varian: `'A'` (Kontrol) atau `'B'` (Treatment) |
| `willingness_to_pay` | NUMERIC | NO | Skor minat/kesediaan bayar: integer 1 s.d. 10 |
| `perceived_trust` | INT | NO | Skor persepsi kepercayaan: integer 1 s.d. 5 |
| `clicked_signup` | BOOLEAN | NO | Konversi klik tombol daftar: `true` atau `false` |
| `time_spent_sec` | NUMERIC | NO | Waktu di halaman sebelum submit (detik) |
| `created_at` | TIMESTAMPTZ | NO | Waktu pencatatan UTC |

---

## 2. Kontrak Pemanggilan Fungsi Komputasi Statistik

Analysis Layer menyediakan modul `src/analysis/stats_engine.py` dengan signature fungsi wajib:

```python
def analyze_ab_test(df: pd.DataFrame, alpha: float = 0.05) -> dict
```

### Format Payload Output (Return Dictionary):
```json
{
  "status": "success",
  "sample_size": {"total": 260, "n_a": 130, "n_b": 130},
  "descriptive": {"mean_a": 5.82, "std_a": 1.48, "mean_b": 6.61, "std_b": 1.39, "diff_mean": 0.79},
  "assumptions": {"is_normal": true, "is_equal_var": true},
  "continuous_test": {
    "test_name": "Welch's Two-Sample t-test (One-tailed)",
    "t_statistic": 4.4120,
    "p_value": 0.0001,
    "ci_95": [0.44, 1.14],
    "decision": "Tolak H₀",
    "conclusion": "Tolak H₀ pada tingkat signifikansi 5%. Varian B unggul signifikan."
  },
  "proportion_test": {
    "cr_a": 22.3,
    "cr_b": 36.2,
    "z_statistic": 2.5120,
    "p_value": 0.0060,
    "decision": "Tolak H₀"
  }
}
```

---

## 3. Batas Kinerja & Perilaku Saat Gagal (Error Handling)

1. **Target Waktu Respons:**
   * Waktu submit formulir survei ke Supabase: `< 500 ms`.
   * Waktu eksekusi komputasi analitik statistik: `< 200 ms` untuk N = 1.000.
2. **Penanganan Data Kosong / Kurang:**
   * Jika baris data di database `< 6` (kurang dari 3 per varian), modul analitik mengembalikan status `"warning"` dan web menampilkan instruksi injeksi data simulasi.
3. **Koneksi Database Terputus:**
   * Jika API Supabase tidak merespons (timeout > 3 detik), antarmuka web beralih ke cache lokal in-memory tanpa memicu crash (unhandled exception).

---

## 4. Riwayat Revisi Bertanggal

* **v1.0 (Nov 10, 2026):** Rilis awal kontrak skema tabel dan signature fungsi `analyze_ab_test`. Disepakati seluruh anggota kedua layer.
