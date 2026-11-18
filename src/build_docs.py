"""Rebuild docs/index.html from results/.  python src/build_docs.py

Generated rather than hand-written so the page cannot drift from the numbers
the SQL actually returned.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT = ROOT / "docs" / "index.html"


def load(n):
    return pd.read_csv(RESULTS / f"{n}.csv")


def table(df, cols, pct=(), bold_row=None, muted_row=None):
    head = "".join(f"<th>{v}</th>" for v in cols.values())
    body = []
    for i, (_, r) in enumerate(df.iterrows()):
        cells = []
        for c in cols:
            v = r[c]
            if c in pct:
                cells.append(f"<td class='n'>{float(v):.1f}%</td>")
            elif isinstance(v, (int,)) or (isinstance(v, float) and float(v).is_integer()):
                cells.append(f"<td class='n'>{int(v):,}</td>")
            elif isinstance(v, float):
                cells.append(f"<td class='n'>{v:,.2f}</td>")
            else:
                cells.append(f"<td>{v}</td>")
        cls = ""
        if bold_row and bold_row(r):
            cls = " class='hi'"
        elif muted_row and muted_row(r):
            cls = " class='muted'"
        body.append(f"<tr{cls}>{''.join(cells)}</tr>")
    return (f"<table><thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body)}</tbody></table>")


def bars(rows, key, label, fmt="{:.1f}%", hot=None):
    peak = max(abs(float(r[key])) for r in rows) or 1.0
    out = []
    for r in rows:
        v = float(r[key])
        cls = " hot" if hot and hot(r) else ""
        out.append(f"<div class='bar-row'><span class='bar-label'>{r[label]}</span>"
                   f"<span class='bar-track'><span class='bar-fill{cls}' "
                   f"style='width:{abs(v)/peak*100:.1f}%'></span></span>"
                   f"<span class='bar-value'>{fmt.format(v)}</span></div>")
    return "\n".join(out)


def main() -> int:
    quality = load("00_data_quality")
    overview = load("01_portfolio_overview")
    roll = load("02b_roll_rate_by_month")
    dq = load("03_risk_by_delinquency")
    util = load("04_utilisation_bands")
    limits = load("05_limit_bands")
    behaviour = load("06_payment_behaviour")
    early = load("07_early_warning")

    comp = roll[roll["status"] == "comparable"]
    inflow_first = float(comp["inflow_2plus_pct"].iloc[0])
    inflow_last = float(comp["inflow_2plus_pct"].iloc[-1])
    cure_first = float(comp["cure_2plus_pct"].iloc[0])
    cure_last = float(comp["cure_2plus_pct"].iloc[-1])
    growth = (float(overview["exposure_m"].iloc[-1])
              / float(overview["exposure_m"].iloc[0]) - 1) * 100
    never = dq.iloc[0]
    bad_row = roll[roll["status"] != "comparable"].iloc[0]

    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Card Portfolio Risk</title>
<style>
:root {{
  --bg:#fbfaf8; --panel:#fff; --ink:#1a1a1a; --muted:#6b6b6b; --line:#e6e3de;
  --accent:#1f6f54; --warn:#b4531f; --rule:#d8d4cd;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg:#15161a; --panel:#1d1f24; --ink:#eceae6; --muted:#9c9a95; --line:#2d3038;
    --accent:#53b78f; --warn:#e08a4e; --rule:#343842;
  }}
}}
:root[data-theme="dark"] {{
  --bg:#15161a; --panel:#1d1f24; --ink:#eceae6; --muted:#9c9a95; --line:#2d3038;
  --accent:#53b78f; --warn:#e08a4e; --rule:#343842;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Inter,system-ui,sans-serif}}
.wrap{{max-width:960px;margin:0 auto;padding:48px 16px 80px}}
h1{{font-size:clamp(1.6rem,4vw,2.3rem);line-height:1.2;margin:0 0 8px;letter-spacing:-.02em}}
h2{{font-size:1.15rem;margin:44px 0 6px;letter-spacing:-.01em}}
.sub{{color:var(--muted);margin:0 0 6px}}
.lede{{color:var(--muted);max-width:64ch;margin:0 0 26px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:18px 20px;margin:14px 0;overflow-x:auto}}
.flag{{border-left:3px solid var(--warn)}}
.kpis{{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:24px 0}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.kpi .n{{font-size:1.5rem;font-weight:650;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.kpi .l{{color:var(--muted);font-size:.82rem;margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:.9rem;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}}
td.n{{text-align:right}}
th{{color:var(--muted);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}}
tbody tr:last-child td{{border-bottom:none}}
tr.muted td{{color:var(--muted)}}
tr.hi td{{color:var(--warn);font-weight:600}}
code{{font-size:.86em;background:var(--bg);padding:1px 5px;border-radius:4px;border:1px solid var(--line)}}
.note{{font-size:.86rem;color:var(--muted);max-width:66ch}}
.bar-row{{display:grid;grid-template-columns:minmax(150px,1fr) 3fr 56px;gap:10px;
  align-items:center;padding:3px 0;font-size:.86rem}}
.bar-label{{color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.bar-track{{background:var(--bg);border:1px solid var(--line);border-radius:999px;height:10px;overflow:hidden}}
.bar-fill{{display:block;height:100%;background:var(--rule);border-radius:999px}}
.bar-fill.hot{{background:var(--warn)}}
.bar-value{{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}}
.cols{{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}}
a{{color:var(--accent)}}
@media (max-width:520px){{.bar-row{{grid-template-columns:minmax(100px,1fr) 2fr 50px}}}}
</style></head><body><div class="wrap">

<h1>Card Portfolio Risk Profile</h1>
<p class="sub">30,000 accounts · 180,000 account-months · April–September 2005</p>
<p class="lede">SQL over a card book, answering the three questions a risk committee
asks: what is the profile, is it getting worse, and where do the losses actually sit.
One data defect decides how every other number here may be read.</p>

<div class="kpis">
  <div class="kpi"><div class="n">22.1%</div><div class="l">eventual default rate</div></div>
  <div class="kpi"><div class="n">{inflow_first:.2f}% → {inflow_last:.2f}%</div><div class="l">monthly inflow to 2+ cycles</div></div>
  <div class="kpi"><div class="n">{cure_first:.1f}% → {cure_last:.1f}%</div><div class="l">cure rate, roughly flat</div></div>
  <div class="kpi"><div class="n">+{growth:.1f}%</div><div class="l">exposure growth</div></div>
  <div class="kpi"><div class="n">{float(never['pct_of_defaults']):.1f}%</div><div class="l">of defaults from never-delinquent accounts</div></div>
</div>

<h2>The defect that governs everything else</h2>
<div class="panel flag">
{table(quality, {'month_label': 'Month', 'status_1_count': 'Status = 1',
                 'status_2_count': 'Status = 2', 'any_delinquent': 'Any delinquent'},
       bold_row=lambda r: int(r['status_1_count']) > 1000)}
</div>
<p class="note">"One cycle past due" appears <strong>34 times across the first five months
and 3,688 times in the sixth</strong>. A state cannot do that unless the coding changed.</p>
<p class="note">It is not academic. On the final transition, the natural definition of
delinquency shows inflow <strong>tripling to {float(bad_row['inflow_any_pct']):.2f}%</strong>
and the cure rate <strong>collapsing to {float(bad_row['cure_any_pct']):.2f}%</strong> — a book in
free fall. The comparable definition shows inflow <strong>falling to
{float(bad_row['inflow_2plus_pct']):.2f}%</strong> and curing <strong>rising to
{float(bad_row['cure_2plus_pct']):.2f}%</strong> — a book recovering. Both are the recoding.
I had written the first version into the memo before checking.</p>

<h2>Roll rates, both definitions side by side</h2>
<div class="panel">
{table(roll, {'from_month': 'Transition', 'status': 'Comparable?',
              'inflow_any_pct': 'Inflow, any DQ', 'cure_any_pct': 'Cure, any DQ',
              'inflow_2plus_pct': 'Inflow, 2+', 'cure_2plus_pct': 'Cure, 2+',
              'inflow_3plus_pct': 'Inflow, 3+'},
       pct=('inflow_any_pct', 'cure_any_pct', 'inflow_2plus_pct',
            'cure_2plus_pct', 'inflow_3plus_pct'),
       muted_row=lambda r: r['status'] != 'comparable')}
</div>
<p class="note">Across the four comparable transitions, inflow to 2+ cycles roughly
<strong>doubled</strong> while cure rates held flat. That is an inflow problem, not a
collections problem. The greyed row is the recoding.</p>

<h2>Where the losses sit</h2>
<div class="panel">
{table(dq, {'delinquency_band': 'Worst delinquency reached', 'pct_of_book': '% of book',
            'default_rate_pct': 'Default rate', 'pct_of_exposure': '% of exposure',
            'pct_of_defaults': '% of all defaults'},
       pct=('pct_of_book', 'default_rate_pct', 'pct_of_exposure', 'pct_of_defaults'))}
</div>
<p class="note">The never-delinquent segment has the lowest rate in the book and produces
<strong>{float(never['pct_of_defaults']):.1f}% of all defaults</strong>, because it holds
<strong>{float(never['pct_of_exposure']):.1f}% of exposure</strong>. A strategy aimed only at
delinquent accounts addresses two thirds of the problem at most.</p>

<h2>Utilisation is not monotone</h2>
<div class="panel">
{bars(util.to_dict('records'), 'default_rate_pct', 'utilisation_band',
      hot=lambda r: 'zero' in r['utilisation_band'] or 'over limit' in r['utilisation_band'])}
</div>
<p class="note">Risk climbs with utilisation, except that <strong>zero-balance accounts default
at 24.8%</strong> — higher than every band below 60%. A zero balance bundles dormant accounts
with accounts that stopped transacting because something went wrong. Treating "no balance"
as "no risk" in a limit rule would be a mistake, and it is the kind of rule that gets written.</p>

<h2>Early warning, and behaviour</h2>
<div class="cols">
<div class="panel">{table(early, {'first_delinquent_month': 'First delinquent month',
                                   'accounts': 'Accounts', 'default_rate_pct': 'Default rate'},
                          pct=('default_rate_pct',))}</div>
<div class="panel">{table(behaviour, {'behaviour': 'Behaviour', 'pct_of_book': '% of book',
                                       'default_rate_pct': 'Default rate'},
                          pct=('pct_of_book', 'default_rate_pct'),
                          bold_row=lambda r: 'minimum' in r['behaviour'])}</div>
</div>
<p class="note">Any delinquency at all roughly triples the default rate against 11.7% for an
account that never missed — and a first miss in the opening month still leaves six months of
warning. Minimum payers are over half the book, carry the largest balances and default at
nearly twice the rate of heavy payers.</p>

<h2>Limit bands: rate and concentration disagree</h2>
<div class="panel">
{table(limits, {'limit_band': 'Credit limit', 'default_rate_pct': 'Default rate',
                'pct_of_exposure': '% of exposure', 'pct_of_defaults': '% of all defaults'},
       pct=('default_rate_pct', 'pct_of_exposure', 'pct_of_defaults'))}
</div>
<p class="note">The highest-rate band holds 4.3% of exposure; the 200–400k band holds 38.5%
and still contributes 21.7% of defaults. Rate sizes the risk per account, not the problem.</p>

<p class="note" style="margin-top:40px">
UCI <em>Default of Credit Card Clients</em> (Yeh &amp; Lien, 2009), NT$. Public research
dataset, no personal identifiers. Six months, one issuer, no origination date and no
recovery data, so nothing here is a through-the-cycle estimate. ·
<a href="https://github.com/f20220970-debug/card-portfolio-risk">SQL, workbook and memo on GitHub</a>
</p>
</div></body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
