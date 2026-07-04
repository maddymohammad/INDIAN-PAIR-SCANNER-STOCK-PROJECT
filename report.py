"""
report.py
---------
Builds the daily markdown report and per-pair charts for the pairs scanner.

Honesty constraints baked in:
  - Charts and text describe SPREAD CONVERGENCE signals, never "growth
    forecasts". A pairs engine has no growth model.
  - Simulated results (is_real=False) are loudly flagged.
  - Non-cointegrating pairs are shown as "no valid signal", not hidden.
  - Every report carries the multiple-testing methodology up front:
    expected false positives per run, the Bonferroni strict tier, and
    per-pair persistence counts across real-data runs.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_BG = "#0d0d0d"; _WHITE = "#ffffff"; _GREY = "#888888"
_GREEN = "#00e676"; _RED = "#ff5252"; _BLUE = "#5b8def"; _AMBER = "#ffa726"
_DGREY = "#333333"


def _ax(ax):
    ax.set_facecolor(_BG)
    for s in ax.spines.values():
        s.set_color(_DGREY)
    ax.tick_params(colors=_GREY, labelsize=8)
    ax.grid(True, color=_DGREY, lw=0.4, alpha=0.5)


def make_pair_chart(r: dict, run_date: date, out_root="charts") -> str | None:
    """
    Three panels: (1) both price series with train/test split line,
    (2) out-of-sample z-score with entry/exit bands,
    (3) out-of-sample strategy equity curve.
    Returns path relative to the reports/ directory.
    """
    prices, z, eq = r["prices"], r["z_test"], r["equity"]
    a, b = r["a"], r["b"]

    fig, axes = plt.subplots(3, 1, figsize=(11, 10), facecolor=_BG)

    _ax(axes[0])
    axes[0].plot(prices.index, prices[a], color=_BLUE, lw=1.0, label=a)
    axes[0].plot(prices.index, prices[b], color=_AMBER, lw=1.0, label=b)
    axes[0].axvline(r["split_date"], color=_GREY, ls="--", lw=0.8)
    axes[0].set_title(f"{a} vs {b} — price series (dashed = train/test split)",
                      color=_WHITE, fontsize=11, loc="left")
    axes[0].legend(fontsize=8, facecolor="#1a1a1a", edgecolor=_DGREY,
                   labelcolor="#cccccc", loc="upper left")

    _ax(axes[1])
    axes[1].plot(z.index, z.values, color="#b98cff", lw=0.9)
    for lvl, st in [(r["entry_z"], "--"), (-r["entry_z"], "--"),
                    (r["exit_z"], ":"), (-r["exit_z"], ":")]:
        axes[1].axhline(lvl, color=_GREY, ls=st, lw=0.8)
    axes[1].set_title("Spread z-score (out-of-sample) with entry/exit bands",
                      color=_WHITE, fontsize=10, loc="left")

    _ax(axes[2])
    axes[2].plot(eq.index, eq.values, color=_GREEN, lw=1.2)
    axes[2].axhline(1.0, color=_DGREY, lw=0.6)
    axes[2].set_title("Out-of-sample strategy equity (net of costs)",
                      color=_WHITE, fontsize=10, loc="left")

    fig.tight_layout()
    out_dir = Path(out_root) / str(run_date)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = f"{a}_{b}".replace("/", "_").replace(".", "-")
    path = out_dir / f"{safe}.png"
    fig.savefig(path, dpi=150, facecolor=_BG)
    plt.close(fig)
    return f"charts/{run_date}/{safe}.png"


def _tier_mark(r: dict) -> str:
    """✓✓ = Bonferroni pass, ✓ = 5% only, ✗ = fail."""
    if r.get("coint_bonf"):
        return "✓✓"
    if r["coint"]["cointegrated_5pct"]:
        return "✓"
    return "✗"


def _persist_cell(stats: dict | None) -> str:
    if not stats or stats["real_runs"] == 0:
        return "0/0*"
    return f"{stats['passes_5pct']}/{stats['real_runs']}"


def build_report(results: list, run_date: date, chart_paths: dict,
                 persistence: dict | None = None,
                 bonf_alpha: float | None = None,
                 n_pairs: int | None = None) -> str:
    persistence = persistence or {}
    n_pairs = n_pairs or len(results)
    bonf_alpha = bonf_alpha or (0.05 / max(1, n_pairs))

    L = []
    L.append(f"# Indian Pairs-Trading Scanner — {run_date}")
    L.append("")
    L.append("> **What this is:** a market-neutral *pairs mean-reversion* "
             "scanner. It flags when two related NSE stocks have drifted apart "
             "far enough that their historical relationship signals a possible "
             "convergence trade. It does **not** forecast growth, rank \"best\" "
             "stocks, or predict company performance. A signal means the *spread "
             "between two stocks* is stretched — nothing about either stock being "
             "a good investment. Not investment advice; do your own research.")
    L.append("")

    # ── Methodology / multiple-testing block ─────────────────────────────
    L.append("## Methodology (fixed in advance)")
    L.append("")
    L.append(f"- **Universe:** {n_pairs} declared sector-mate pairs. "
             f"Parameters (3y window, 60/40 train-test, z-entry 2.0, "
             f"z-exit 0.5, 5 bps costs) are pre-registered; changes are "
             f"logged in the README changelog *before* looking at results.")
    L.append(f"- **Multiple testing:** at the 5% level across {n_pairs} pairs, "
             f"**≈{0.05 * n_pairs:.1f} false positives per run are expected by "
             f"chance alone** even if nothing truly cointegrates. A single-day "
             f"pass is a candidate, not a discovery.")
    L.append(f"- **Strict tier:** Bonferroni-corrected threshold "
             f"p < {bonf_alpha:.4f} (marked ✓✓).")
    L.append("- **Evidence = persistence:** the Persistence column counts how "
             "often each pair has passed the 5% test across all *real-data* "
             "daily runs recorded in `reports/history.csv`. Pairs deserve "
             "attention only when they pass persistently.")
    L.append("")

    any_sim = any(not r["is_real"] for r in results)
    if any_sim:
        L.append("> ⚠️ **Some results use SIMULATED fallback data** (real data "
                 "was unreachable this run) and are not real market results. "
                 "These are marked below and are EXCLUDED from persistence "
                 "counts.")
        L.append("")

    # ── Summary table ─────────────────────────────────────────────────────
    L.append("## Summary")
    L.append("")
    L.append("| Pair | p-value | Coint. | Persistence | Current z | Signal | OOS Sharpe |")
    L.append("|---|---|---|---|---|---|---|")
    for r in results:
        sim = " *(sim)*" if not r["is_real"] else ""
        pkey = f"{r['a']}/{r['b']}"
        z = f"{r['current_z']:+.2f}"
        short_sig = r["signal"].split(" (")[0]
        L.append(
            f"| {pkey}{sim} | {r['coint']['p_value']:.4f} | {_tier_mark(r)} "
            f"| {_persist_cell(persistence.get(pkey))} | {z} | {short_sig} "
            f"| {r['perf']['sharpe']:.2f} |"
        )
    L.append("")
    L.append("_Legend: ✓✓ passes strict Bonferroni tier · ✓ passes 5% only · "
             "✗ fails. Persistence = 5%-passes / real-data runs recorded. "
             "\\*no real-data history yet._")
    L.append("")

    L.append("---")
    for r in results:
        sim_tag = " · _SIMULATED_" if not r["is_real"] else ""
        pkey = f"{r['a']}/{r['b']}"
        L.append("")
        L.append(f"### {r['a']} / {r['b']}{sim_tag}")
        L.append("")
        L.append(f"- **Latest prices:** {r['a']} ₹{r['price_a']:,.2f} · "
                 f"{r['b']} ₹{r['price_b']:,.2f}")
        L.append(f"- **Hedge ratio (train-fitted):** {r['beta']:.4f}")
        c = r["coint"]
        L.append(f"- **Cointegration (train):** "
                 f"{'PASS' if c['cointegrated_5pct'] else 'FAIL'} at 5% "
                 f"— ADF {c['adf_stat']:.2f}, p={c['p_value']:.4f}"
                 f"{' · **passes strict Bonferroni tier**' if r.get('coint_bonf') else ''}")
        st = persistence.get(pkey)
        if st and st["real_runs"] > 0:
            L.append(f"- **Persistence:** passed 5% in {st['passes_5pct']} of "
                     f"{st['real_runs']} real-data runs "
                     f"(strict tier: {st['passes_bonf']}/{st['real_runs']})")
        else:
            L.append("- **Persistence:** no real-data history yet")
        hl = r["half_life"]
        L.append(f"- **Spread half-life:** "
                 f"{f'{hl:.1f} days' if hl == hl else 'n/a (not mean-reverting)'}")
        L.append(f"- **Current z-score:** {r['current_z']:+.2f}")
        L.append(f"- **Signal today:** {r['signal']}")
        if not c["cointegrated_5pct"]:
            L.append("- ⚠️ _Pair did not cointegrate on training data. Any signal "
                     "here is not statistically justified — observation only._")
        L.append("")
        p = r["perf"]
        L.append("**Out-of-sample backtest** (beta frozen from train window):")
        L.append("")
        L.append("| Metric | Value |")
        L.append("|---|---|")
        L.append(f"| Sharpe | {p['sharpe']:.2f} |")
        L.append(f"| Sortino | {p['sortino']:.2f} |")
        L.append(f"| Annualised return | {p['annualised_return']:.2%} |")
        L.append(f"| Annualised vol | {p['annualised_vol']:.2%} |")
        L.append(f"| Max drawdown | {p['max_drawdown']:.2%} |")
        L.append(f"| Round-trip trades | {p['round_trip_trades']} |")
        L.append("")
        cp = chart_paths.get(pkey)
        if cp:
            L.append(f"![{pkey} chart]({cp})")
            L.append("")
        L.append("---")

    L.append("")
    L.append(f"_Generated {run_date} · pairs mean-reversion scanner · "
             f"out-of-sample backtest · multiple-testing-aware · "
             f"not investment advice._")
    L.append("")
    return "\n".join(L)
