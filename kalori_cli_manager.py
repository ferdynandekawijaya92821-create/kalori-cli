import argparse
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "makanan.csv"
LOG_PATH = BASE_DIR / "kalori_log.txt"

DEFAULT_FOOD = {
    "nasi": 200,
    "ayam": 250,
    "telur": 80,
    "apel": 95,
    "pisang": 100,
    "indomie": 350
}

def ensure_db():
    if not DATA_PATH.exists():
        with DATA_PATH.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nama", "kalori"])
            for n, k in DEFAULT_FOOD.items():
                writer.writerow([n, k])

def load_food_db():
    ensure_db()
    db = {}
    with DATA_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            db[r["nama"].strip().lower()] = int(r["kalori"])
    return db

def save_food_db(db):
    with DATA_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["nama", "kalori"])
        for n, k in sorted(db.items()):
            writer.writerow([n, k])

def log_calorie_session(total, detail):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"\n=== SESSION {now} ===\n")
        for nama, kal in detail:
            f.write(f"{nama} : {kal}\n")
        f.write(f"TOTAL = {total} kalori\n")

def handle_calc(args):
    db = load_food_db()
    daftar = args.makanan

    total = 0
    rincian = []

    for item in daftar:
        nama = item.lower()
        if nama in db:
            kal = db[nama]
            rincian.append((nama, kal))
            total += kal
        else:
            rincian.append((nama, "Tidak ada"))

    print("\n=== PERHITUNGAN KALORI ===")
    for n, k in rincian:
        print(f"{n:<15} : {k}")

    print(f"\nTOTAL KALORI : {total} kalori")

    log_calorie_session(total, rincian)
    print("Log disimpan ke kalori_log.txt")

def handle_list_food(args):
    db = load_food_db()
    print("\n=== DAFTAR MAKANAN TERDAFTAR ===")
    print(f"{'Makanan':<20}Kalori")
    print("-" * 30)
    for nama, kal in sorted(db.items()):
        print(f"{nama:<20}{kal}")

def handle_add_food(args):
    nama = args.nama.lower()
    try:
        kal = int(args.kalori)
    except:
        print("Kalori harus berupa angka!")
        return

    db = load_food_db()
    update = nama in db
    db[nama] = kal
    save_food_db(db)

    if update:
        print(f"Makanan '{nama}' diperbarui menjadi {kal} kalori.")
    else:
        print(f"Makanan '{nama}' ditambahkan ({kal} kalori).")

def build_parser():
    parser = argparse.ArgumentParser(
        description="Kalori CLI Manager - 1 File Version"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("calc", help="Hitung total kalori")
    c.add_argument("-m", "--makanan", nargs="+", required=True)
    c.set_defaults(func=handle_calc)

    l = sub.add_parser("list-food", help="List semua makanan")
    l.set_defaults(func=handle_list_food)

    a = sub.add_parser("add-food", help="Tambah makanan")
    a.add_argument("nama")
    a.add_argument("kalori")
    a.set_defaults(func=handle_add_food)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
