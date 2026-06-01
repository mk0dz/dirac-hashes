"""Fetch and trim NIST ACVP test vectors for vendored KAT validation.

Source: https://github.com/usnistgov/ACVP-Server (gen-val/json-files).

Each ACVP ``internalProjection.json`` file contains both the test inputs (seeds,
keys, messages) and the expected outputs (keys, signatures, pass/fail), so a single
vendored file is a complete known-answer test. We trim each test group to a handful
of cases to keep the repo light while still exercising every parameter set.

Usage:
    python kat/fetch_acvp.py                       # fetch the default lattice sets
    python kat/fetch_acvp.py --per-group 20        # keep more cases per group
    python kat/fetch_acvp.py --only ML-DSA-keyGen-FIPS204
    python kat/fetch_acvp.py --all                 # include SLH-DSA (large)
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

BASE = (
    "https://raw.githubusercontent.com/usnistgov/ACVP-Server/master/"
    "gen-val/json-files"
)
HERE = Path(__file__).resolve().parent
VEC = HERE / "vectors"

# ACVP directory name -> vendored output filename (short name).
DATASETS: dict[str, str] = {
    "ML-KEM-keyGen-FIPS203": "ml_kem_keygen.json",
    "ML-KEM-encapDecap-FIPS203": "ml_kem_encapdecap.json",
    "ML-DSA-keyGen-FIPS204": "ml_dsa_keygen.json",
    "ML-DSA-sigGen-FIPS204": "ml_dsa_siggen.json",
    "ML-DSA-sigVer-FIPS204": "ml_dsa_sigver.json",
    "SLH-DSA-keyGen-FIPS205": "slh_dsa_keygen.json",
    "SLH-DSA-sigGen-FIPS205": "slh_dsa_siggen.json",
    "SLH-DSA-sigVer-FIPS205": "slh_dsa_sigver.json",
}

# The lattice schemes we implement first; SLH-DSA files are big so they are opt-in.
DEFAULT = [d for d in DATASETS if d.startswith(("ML-KEM", "ML-DSA"))]


def fetch(dirname: str) -> dict:
    url = f"{BASE}/{dirname}/internalProjection.json"
    with urllib.request.urlopen(url, timeout=180) as resp:
        return json.load(resp)


def trim(doc: dict, per_group: int) -> dict:
    if per_group:
        for tg in doc.get("testGroups", []):
            if "tests" in tg:
                tg["tests"] = tg["tests"][:per_group]
    return doc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-group", type=int, default=10,
                    help="max test cases kept per test group (0 = keep all)")
    ap.add_argument("--only", nargs="*", help="ACVP dir names to fetch")
    ap.add_argument("--all", action="store_true",
                    help="fetch every dataset, including SLH-DSA")
    args = ap.parse_args()

    VEC.mkdir(parents=True, exist_ok=True)
    if args.only:
        names = args.only
    elif args.all:
        names = list(DATASETS)
    else:
        names = DEFAULT

    for dirname in names:
        outname = DATASETS.get(dirname)
        if outname is None:
            print(f"SKIP {dirname}: unknown dataset")
            continue
        try:
            doc = trim(fetch(dirname), args.per_group)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"SKIP {dirname}: {exc}")
            continue
        out = VEC / outname
        out.write_text(json.dumps(doc, indent=1))
        groups = doc.get("testGroups", [])
        ntests = sum(len(tg.get("tests", [])) for tg in groups)
        print(f"{outname}: {len(groups)} groups, {ntests} tests, "
              f"{out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
