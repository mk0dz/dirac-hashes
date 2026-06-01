"""Benchmark every registered PQC scheme: timings + canonical byte sizes.

Each operation is timed with ``time.perf_counter`` over an adaptive number of
iterations (slow operations fall back to a single run). A correctness round-trip is
performed before timing so we never benchmark broken code. Results are written as JSON
under ``benchmark_results/`` for :mod:`bench.report` to summarize.

Usage:
    python bench/run.py                 # all schemes
    python bench/run.py --quick         # fewer iterations
    python bench/run.py --filter ML-DSA # only matching scheme names
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

# Importing the packages registers their schemes.
import quantum_hash.pqc.ml_kem  # noqa: E402,F401
import quantum_hash.pqc.ml_dsa  # noqa: E402,F401
import quantum_hash.pqc.slh_dsa  # noqa: E402,F401
from quantum_hash.pqc.common.base import (KEM, SignatureScheme,  # noqa: E402
                                          get_scheme, list_schemes)

OUT_DIR = ROOT / "benchmark_results"


def _time(fn, target_seconds: float, max_iters: int) -> dict:
    fn()  # warmup
    t0 = time.perf_counter()
    fn()
    dt = time.perf_counter() - t0
    iters = max(1, min(max_iters, int(target_seconds / dt) if dt > 0 else max_iters))
    samples = []
    for _ in range(iters):
        t0 = time.perf_counter()
        fn()
        samples.append(time.perf_counter() - t0)
    median = statistics.median(samples)
    return {
        "median_ms": median * 1e3,
        "mean_ms": statistics.fmean(samples) * 1e3,
        "stdev_ms": (statistics.stdev(samples) * 1e3) if len(samples) > 1 else 0.0,
        "ops_per_sec": (1.0 / median) if median > 0 else None,
        "iters": iters,
    }


def bench_signature(scheme: SignatureScheme, target: float, max_iters: int) -> dict:
    pk, sk = scheme.keygen()
    msg = b"benchmark message"
    sig = scheme.sign(sk, msg)
    assert scheme.verify(pk, msg, sig), f"{scheme.name} self-check failed"
    return {
        "keygen": _time(lambda: scheme.keygen(), target, max_iters),
        "sign": _time(lambda: scheme.sign(sk, msg), target, max_iters),
        "verify": _time(lambda: scheme.verify(pk, msg, sig), target, max_iters),
    }


def bench_kem(scheme: KEM, target: float, max_iters: int) -> dict:
    ek, dk = scheme.keygen()
    ct, ss = scheme.encaps(ek)
    assert scheme.decaps(dk, ct) == ss, f"{scheme.name} self-check failed"
    return {
        "keygen": _time(lambda: scheme.keygen(), target, max_iters),
        "encaps": _time(lambda: scheme.encaps(ek), target, max_iters),
        "decaps": _time(lambda: scheme.decaps(dk, ct), target, max_iters),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="fewer iterations")
    ap.add_argument("--filter", default="", help="substring match on scheme name")
    ap.add_argument("--target-seconds", type=float, default=1.0)
    args = ap.parse_args()

    target = 0.25 if args.quick else args.target_seconds
    max_iters = 20 if args.quick else 200

    results = []
    for name in list_schemes():
        if args.filter and args.filter not in name:
            continue
        scheme = get_scheme(name)
        kind = "KEM" if isinstance(scheme, KEM) else "signature"
        print(f"benchmarking {name} ({kind}) ...", flush=True)
        ops = (bench_kem if kind == "KEM" else bench_signature)(scheme, target, max_iters)
        results.append({
            "name": name,
            "kind": kind,
            "security_category": scheme.security_category,
            "sizes": scheme.sizes,
            "ops": ops,
        })

    OUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    doc = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "quick": args.quick,
        "schemes": results,
    }
    out = OUT_DIR / f"pqc_benchmark_{stamp}.json"
    out.write_text(json.dumps(doc, indent=2))
    latest = OUT_DIR / "pqc_benchmark_latest.json"
    latest.write_text(json.dumps(doc, indent=2))
    print(f"\nwrote {out}\nwrote {latest}")


if __name__ == "__main__":
    main()
