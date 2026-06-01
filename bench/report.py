"""Summarize a benchmark JSON: comparison tables, a wallet-weighted pick, and charts.

The "wallet score" ranks signature schemes for the dirac-crypto use case. Each metric
is min-max normalized across signature schemes (0 = best) and combined with weights
that reflect what a wallet cares about: signatures and public keys are stored/transmitted
a lot and verification is on the hot path, so those dominate.

Usage:
    python bench/report.py                       # uses benchmark_results/pqc_benchmark_latest.json
    python bench/report.py path/to/result.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "benchmark_results" / "pqc_benchmark_latest.json"

# Wallet-relevant weights (lower score is better). Documented and tunable.
#
# On a blockchain the signature travels in EVERY transaction, so its size is the
# dominant recurring cost and is weighted accordingly. The public key is registered
# essentially once, so it is weighted low. Verification is on the hot path (clients
# and validators check signatures); key generation happens once.
WEIGHTS = {
    "sig_bytes": 0.50,
    "verify_ms": 0.20,
    "sign_ms": 0.15,
    "pk_bytes": 0.10,
    "keygen_ms": 0.05,
}

# Default security category to recommend at (NIST cat 3 ~ 192-bit classical).
TARGET_CATEGORY = 3


def _norm(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def _sig_metrics(scheme: dict) -> dict:
    ops = scheme["ops"]
    return {
        "sig_bytes": scheme["sizes"]["sig"],
        "pk_bytes": scheme["sizes"]["pk"],
        "keygen_ms": ops["keygen"]["median_ms"],
        "sign_ms": ops["sign"]["median_ms"],
        "verify_ms": ops["verify"]["median_ms"],
    }


def score_signatures(sigs: list[dict]) -> dict[str, float]:
    metrics = {m: _norm([_sig_metrics(s)[m] for s in sigs]) for m in WEIGHTS}
    scores = {}
    for i, s in enumerate(sigs):
        scores[s["name"]] = sum(WEIGHTS[m] * metrics[m][i] for m in WEIGHTS)
    return scores


def _fmt_ms(x: float) -> str:
    return f"{x:.2f}" if x < 100 else f"{x:.0f}"


def render(doc: dict) -> str:
    sigs = [s for s in doc["schemes"] if s["kind"] == "signature"]
    kems = [s for s in doc["schemes"] if s["kind"] == "KEM"]
    lines = [
        f"# PQC benchmark — {doc['generated']}",
        f"Python {doc['python']}, pure-Python reference implementations"
        f"{' (quick mode)' if doc.get('quick') else ''}.",
        "",
    ]

    if sigs:
        scores = score_signatures(sigs)
        sigs_sorted = sorted(sigs, key=lambda s: scores[s["name"]])
        lines += [
            "## Signature schemes (lower wallet score = better)",
            "",
            "| Scheme | Cat | pk (B) | sig (B) | keygen (ms) | sign (ms) | verify (ms) | score |",
            "|---|--:|--:|--:|--:|--:|--:|--:|",
        ]
        for s in sigs_sorted:
            o = s["ops"]
            lines.append(
                f"| {s['name']} | {s['security_category']} | {s['sizes']['pk']} | "
                f"{s['sizes']['sig']} | {_fmt_ms(o['keygen']['median_ms'])} | "
                f"{_fmt_ms(o['sign']['median_ms'])} | {_fmt_ms(o['verify']['median_ms'])} | "
                f"{scores[s['name']]:.3f} |"
            )
        # Recommend within the target security category - scoring across categories
        # is apples-to-oranges (a cat-1 scheme always looks "cheaper" than cat-5).
        by_cat = {}
        for s in sigs_sorted:  # sigs_sorted is ascending by score
            by_cat.setdefault(s["security_category"], s)
        winner = by_cat.get(TARGET_CATEGORY, sigs_sorted[0])
        lines += [
            "",
            f"**Wallet pick (category {TARGET_CATEGORY}): `{winner['name']}`** "
            f"— sig {winner['sizes']['sig']} B, pk {winner['sizes']['pk']} B, "
            f"verify {_fmt_ms(winner['ops']['verify']['median_ms'])} ms.",
            "Best per security category: "
            + ", ".join(f"cat {c} → `{by_cat[c]['name']}`" for c in sorted(by_cat))
            + ".",
            "",
            "> Note: SLH-DSA has tiny keys but multi-kilobyte signatures (8–50 KB). "
            "Since a blockchain carries the signature in every transaction, those sizes "
            "are impractical on-chain despite a low raw score at low categories — ML-DSA "
            "is the right fit for a wallet.",
            "",
        ]

    if kems:
        lines += [
            "## KEM schemes",
            "",
            "| Scheme | Cat | ek (B) | dk (B) | ct (B) | keygen (ms) | encaps (ms) | decaps (ms) |",
            "|---|--:|--:|--:|--:|--:|--:|--:|",
        ]
        for s in sorted(kems, key=lambda s: s["security_category"]):
            o = s["ops"]
            sz = s["sizes"]
            lines.append(
                f"| {s['name']} | {s['security_category']} | {sz['ek']} | {sz['dk']} | "
                f"{sz['ct']} | {_fmt_ms(o['keygen']['median_ms'])} | "
                f"{_fmt_ms(o['encaps']['median_ms'])} | {_fmt_ms(o['decaps']['median_ms'])} |"
            )
        lines.append("")
    return "\n".join(lines)


def make_charts(doc: dict, out_dir: Path) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False
    sigs = [s for s in doc["schemes"] if s["kind"] == "signature"]
    if not sigs:
        return False
    out_dir.mkdir(parents=True, exist_ok=True)
    names = [s["name"].replace("ML-DSA-", "ML-DSA-").replace("SLH-DSA-SHAKE-", "SLH-")
             for s in sigs]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(names, [s["sizes"]["sig"] for s in sigs], color="#4C72B0")
    ax.set_ylabel("signature size (bytes)")
    ax.set_title("Signature size by scheme")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out_dir / "signature_sizes.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(names, [s["ops"]["verify"]["median_ms"] for s in sigs], color="#55A868")
    ax.set_ylabel("verify latency (ms, median)")
    ax.set_title("Verification latency by scheme")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out_dir / "verify_latency.png", dpi=120)
    plt.close(fig)
    return True


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    doc = json.loads(path.read_text())
    report = render(doc)
    print(report)
    md_path = path.with_suffix(".md")
    md_path.write_text(report + "\n")
    charts_dir = path.parent / (path.stem + "_charts")
    if make_charts(doc, charts_dir):
        print(f"\ncharts written to {charts_dir}")
    print(f"report written to {md_path}")


if __name__ == "__main__":
    main()
