"""
errors.py
Kelas exception bersama antar-layer (Analysis Layer & Infrastructure Layer).
Mematuhi Interface Contract (docs/interface-contract.md Bagian 4 & 6).
"""


class AppBaseError(Exception):
    """Base class untuk seluruh custom error di aplikasi."""
    pass


class StatsError(AppBaseError):
    """Base exception untuk kesalahan komputasi / validasi analisis statistik."""
    pass


class InvalidScoreError(StatsError, ValueError):
    """Dilempar jika skor di luar rentang 1-5 atau bukan integer."""
    pass


class InvalidVariantError(StatsError, ValueError):
    """Dilempar jika varian bukan 'A' atau 'B'."""
    pass


class InsufficientSampleError(StatsError, ValueError):
    """Dilempar jika jumlah sampel responden per varian kurang dari batas minimum MIN_N."""
    pass


class DatabaseError(AppBaseError):
    """Base exception untuk kesalahan operasi database."""
    pass


class DuplicateSessionError(DatabaseError):
    """Dilempar jika session_id sudah pernah mengirim respons (pelanggaran UNIQUE constraint)."""
    pass


class DatabaseUnavailableError(DatabaseError):
    """Dilempar jika koneksi ke database Supabase gagal atau timeout setelah retry."""
    pass
