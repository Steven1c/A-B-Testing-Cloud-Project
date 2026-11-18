"""Ukur waktu respons dan cetak baris tabel siap tempel ke docs/evidence/response-time-log.md.

Contoh:
  python tests/measure_response_time.py                    # hanya waktu hitung uji
  python tests/measure_response_time.py --db               # + fetch_scores() ke database
  python tests/measure_response_time.py --db-write         # + insert_response() (MENULIS data uji ke database)

Muat halaman survei dan tampilkan dashboard TIDAK diukur skrip ini:
ukur manual di browser (DevTools > Network), 10 kali, lalu tulis angkanya sendiri.
"""
import argparse, os, statistics, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.analysis.simulate_data import generate_responses
from src.analysis.stats_engine import run_mann_whitney


def timeit(fn, n):
    out = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        out.append(time.perf_counter() - t0)
    return out


def row(name, target, times):
    cells = " | ".join(f"{t:.2f}" for t in times)
    ok = "✅" if max(times) <= target else "☐ (melebihi target)"
    return f"| {name} | ≤ {target} | {cells} | {statistics.mean(times):.2f} | {max(times):.2f} | {ok} |"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="jumlah ulangan")
    ap.add_argument("--size", type=int, default=70, help="responden per varian untuk uji")
    ap.add_argument("--db", action="store_true", help="ukur fetch_scores()")
    ap.add_argument("--db-write", action="store_true", help="ukur insert_response() (menulis data uji)")
    args = ap.parse_args()

    df = generate_responses(args.size, args.size, seed=0)
    v_col = "variant_group" if "variant_group" in df.columns else "variant"
    s_col = "sat_overall" if "sat_overall" in df.columns else "score"
    a = df.loc[df[v_col] == "A", s_col].tolist()
    b = df.loc[df[v_col] == "B", s_col].tolist()

    print(f"Uji dijalankan {args.n}x, n per varian = {args.size}. Satuan: detik.\n")
    print("| Operasi | Target | " + " | ".join(f"U{i}" for i in range(1, args.n + 1)) + " | Rata-rata | Maks | Lolos? |")
    print("|---|---|" + "---|" * (args.n + 3))
    print(row("Hitung uji Mann-Whitney", 2, timeit(lambda: run_mann_whitney(a, b), args.n)))

    if args.db or args.db_write:
        from src.app import db  # sesuaikan dengan db.py tim
        if args.db:
            print(row("fetch_scores (DB)", 2, timeit(db.fetch_scores, args.n)))
        if args.db_write:
            print(row("Simpan jawaban (insert_response)", 2,
                      timeit(lambda: db.insert_response(f"bench_{os.urandom(5).hex()}", "A", 3), args.n)))


if __name__ == "__main__":
    main()
