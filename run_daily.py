"""
run_daily.py
------------
Entry point for the daily automated run:

    scan declared pairs -> update reports/history.csv (persistence trail)
    -> render charts -> write dated markdown report under reports/

The CI workflow commits reports/ afterwards, so both the daily report AND
the accumulating history file end up versioned in the repo.

Usage:
    python run_daily.py
"""
from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

from main import run, DEFAULT_PAIRS, SIGNIFICANCE
from report import make_pair_chart, build_report
from persistence import update_history, persistence_stats

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def main():
    run_date = date.today()
    n_pairs = len(DEFAULT_PAIRS)
    bonf_alpha = SIGNIFICANCE / n_pairs

    results = run(pairs=DEFAULT_PAIRS)

    if not results:
        logging.error("No results produced — nothing to report.")
        return

    # ── Persistence trail (real-data runs only count toward evidence) ────
    history = update_history(results, run_date, bonf_alpha)
    persistence = {
        f"{r['a']}/{r['b']}": persistence_stats(history, f"{r['a']}/{r['b']}")
        for r in results
    }

    # ── Charts ────────────────────────────────────────────────────────────
    chart_paths = {}
    for r in results:
        try:
            cp = make_pair_chart(r, run_date, out_root="reports/charts")
            if cp:
                chart_paths[f"{r['a']}/{r['b']}"] = cp
        except Exception as e:
            logging.warning("Chart failed for %s/%s: %s", r["a"], r["b"], e)

    # ── Report ────────────────────────────────────────────────────────────
    md = build_report(results, run_date, chart_paths,
                      persistence=persistence,
                      bonf_alpha=bonf_alpha,
                      n_pairs=n_pairs)

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    out = reports_dir / f"{run_date}.md"
    out.write_text(md, encoding="utf-8")
    logging.info("Report written: %s", out)
    print(f"\nReport: {out}  ({len(results)} pairs, {len(chart_paths)} charts, "
          f"history rows: {len(history)})")


if __name__ == "__main__":
    main()
