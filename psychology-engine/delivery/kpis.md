# KPIs & Measurement 📊

> What gets measured gets managed — so we measure the *right* things. Guest happiness,
> employee wellbeing, and **trust** are first-class KPIs, and every engagement metric is
> paired with a **guardrail metric** that stops us from "winning" by harming people. A metric
> that rises while its guardrail deteriorates is a **failure**, not a success.

---

## 1. North-star metrics (the seven outcomes)

| # | North star | Definition | Target direction |
|---|---|---|---|
| 1 | **Guest happiness** | CSAT / post-visit sentiment + NPS | ▲ |
| 2 | **Repeat visits** | 30/60/90-day return rate; visit frequency | ▲ |
| 3 | **Gaming usage** | Sessions/visit; station utilisation | ▲ (healthy) |
| 4 | **Food sales** | Attach rate; avg basket; food-per-gaming-hour | ▲ |
| 5 | **Customer Lifetime Value** | Predicted + realised CLV; retention curve | ▲ |
| 6 | **Employee satisfaction** | eNPS; retention; self-reported wellbeing | ▲ |
| 7 | **Brand loyalty & community** | Tier progression; referral *quality*; UGC; brand affinity | ▲ |

---

## 2. Guardrail metrics (each paired to prevent gaming the system) 🔒

| If we push… | We must watch (guardrail) | Rule |
|---|---|---|
| Recommendations / offers | **Annoyance rate** (dismissals, opt-outs, mutes) | Must stay low; rising = back off |
| Engagement / session time | **Responsible-play flags**, take-a-break uptake | Rise = intervene, not celebrate |
| Spend / basket | **Satisfaction + responsible-spend flags** | Spend↑ with satisfaction↓ = failure |
| Loyalty engagement | **Fairness of reward attainment** (casual vs heavy) | Casuals must make real progress |
| Personalisation | **Consent opt-in / opt-out balance** | Opt-outs↑ = trust problem |
| Employee performance | **Wellbeing, fairness, manager-support action rate** | Output↑ with wellbeing↓ = failure |
| Marketing reach | **Frequency-cap compliance, unsubscribe rate** | Caps honoured; unsub↑ = red flag |

**Golden rule:** a north-star gain that comes *with* a guardrail deterioration is reported as
a **net loss** to leadership, and the feature is rolled back or fixed.

---

## 3. Trust & ethics KPIs (board-level) 🔒

| KPI | Definition |
|---|---|
| Consent opt-in rate | % of eligible guests opting into personalisation |
| Opt-out / withdrawal rate | consent withdrawals (watch for spikes) |
| Data-request SLA | % of access/export/erasure done within SLA |
| Fairness-audit status | models passing scheduled fairness audits |
| Dark-pattern incidents | count (target: 0) |
| Responsible-play interventions | offered & taken up (a *good* number to see) |
| Minor-protection compliance | audits passed (target: 100%) |
| Security posture | incidents, time-to-remediate, audit findings |

Trust is treated as an asset with a measurable balance — the deepest moat (Executive
Summary).

---

## 4. Engine effectiveness KPIs

| Area | KPIs |
|---|---|
| Recommendations | Post-hoc *satisfaction*, repeat-visit lift, discovery rate, then attach/CLV lift |
| Loyalty | Repeat rate, tier progression, squad formation, referral quality, program satisfaction |
| Emotion/recovery | Recovery trigger precision, time-to-recover, post-recovery loyalty lift |
| Forecasting | Demand MAPE/WAPE, interval calibration, waste reduction, labour-match |
| Avatar | Task success, helpfulness, guardrail-violation rate (→0), satisfaction, human-handoff quality |
| Employee AI | Burnout-flag → relief-action rate, schedule fairness, retention, eNPS |

---

## 5. Operational & business KPIs

Footfall, table/station utilisation, wait times (actual + *perceived*), kitchen ticket
times, waste %, labour cost vs. demand, revenue per store/hour, membership conversion, and
off-peak fill rate — all sliced by store/region and trended against forecast.

---

## 6. Measurement discipline

- **Every feature is an experiment.** A/B or bandit-tested, with north-star **and** guardrail
  metrics pre-registered.
- **Causal, not just correlational** where it matters (holdouts, geo-experiments) so we know
  the engine *caused* the lift.
- **Confidence intervals** on reported metrics (no false precision).
- **Segment fairness** — results checked across behavioural segments to ensure no group is
  harmed.
- **Leading + lagging** — pair fast leading indicators (engagement, sentiment) with slow
  lagging ones (retention, CLV, eNPS).

---

## 7. Reporting cadence

- **Real-time / daily:** ops dashboards (manager, kitchen, gaming) — Section 9.
- **Weekly:** engine effectiveness + guardrails per store.
- **Monthly:** north-stars, trust KPIs, fairness audits — region & network.
- **Quarterly (board):** north-stars + **trust scorecard** + engine ROI + expansion
  readiness.

The scorecard leadership sees always shows **outcomes next to their guardrails** — so
success is never declared by ignoring the cost to people.

---

### Change log
- v1.0 — Initial KPI framework.
