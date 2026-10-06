# AI / ML Model Catalogue 🧠

> Every model, its purpose, inputs (non-sensitive only), method, outputs (with uncertainty),
> guardrails, and evaluation. DeepMind DNA: rigorous, honest about confidence, monitored for
> drift and fairness. No model may consume a sensitive or proxy feature (feature-store
> allow-list, Section 11.6).

---

## 0. Universal model governance

- **Allow-listed features only** — non-sensitive; proxy/fairness scan before deploy.
- **Calibrated + uncertainty** — probabilities calibrated; forecasts ship confidence
  intervals; low-confidence outputs handled conservatively.
- **Explainability** — top drivers exposed for every people-facing output.
- **Human-gate metadata** — outputs affecting Tier C/D carry "human decision required."
- **Monitoring** — drift, calibration, fairness, and business-metric monitoring; auto-alert
  and kill-switch on degradation.
- **Registry & versioning** — every model versioned, reproducible, rollback-able.

---

## 1. Customer archetype / personality clustering
- **Purpose:** behavioural archetypes (Section 2.4) to tailor tone/suggestions.
- **Method:** unsupervised clustering (k-means / HDBSCAN) + embeddings over *behavioural*
  features (game/food style, cadence, social lean).
- **Output:** archetype label + membership strength.
- **Guardrail:** clusters audited to ensure they don't proxy protected attributes; labels
  are behavioural descriptions, never identity claims.
- **Eval:** cluster stability, silhouette, and a fairness review; human-interpretability
  check.

## 2. Decision-style classifier
- **Purpose:** adapt UI/avatar (Maximiser/Satisficer/Habitual/Social, Section 1.3).
- **Method:** gradient-boosted classifier over choice-behaviour features.
- **Output:** style + confidence → interface adaptation.
- **Eval:** accuracy, calibration; guardrail: affects presentation only, never access/price.

## 3. Recommendation stack
- **Candidate generation:** collaborative filtering (matrix factorisation / two-tower),
  content-based matching, sequence models (next-in-visit), **contextual bandits**
  (explore/exploit, diversity term).
- **Ranking:** learning-to-rank with the **guest-value objective** (Section 7.1): relevance +
  predicted satisfaction + bounded business value − annoyance − guardrail penalties.
- **Filtering:** hard filters for stated dislikes/allergies, frequency caps, guardrail flags.
- **Output:** ranked items + **explanation** + easy-dismiss.
- **Eval:** post-hoc *satisfaction*, repeat-visit lift, discovery rate, **annoyance/opt-out
  (minimise)**, then attach/CLV lift. Offline replay + online A/B + bandit reward.
- **Guardrail 🔒:** no sensitive features (structurally); impulse/vulnerability protections
  reduce pressure; no fabricated scarcity.

## 4. Sentiment / Emotion model (experience-level) 🔒
- **Purpose:** experience sentiment (Section 6) from *voluntary* signals.
- **Method:** fine-tuned language/sentiment model over voluntary feedback text + rule-based
  operational signals; transparent fusion.
- **Output:** emotion label + polarity + confidence, **short TTL**, fast decay.
- **Guardrail:** *no* biometric/facial/voice-affect inputs; *no* sensitive/health inference;
  used only for service (recovery/help/delight), never adverse decisions.
- **Eval:** sentiment accuracy on labelled voluntary feedback; abuse/misuse red-team;
  precision on the "needs recovery" trigger.

## 5. CLV model
- **Purpose:** predicted lifetime value for *care/investment prioritisation* (Section 12.2).
- **Method:** survival/BG-NBD (frequency/retention) + gradient-boosted value model.
- **Output:** CLV + **confidence interval** + drivers.
- **Guardrail 🔒:** never used to deny/downgrade service or set individual penalty prices;
  fairness-audited.
- **Eval:** predictive error vs. realised value, calibration, stability.

## 6. Churn-risk model
- **Purpose:** trigger *care and win-back* (Section 2, 12).
- **Method:** classification/survival over recency/frequency/engagement features.
- **Output:** churn probability (calibrated) + drivers ("6 weeks since last visit").
- **Guardrail:** drives *care*, never punishment.
- **Eval:** AUC/PR, calibration, and — crucially — *win-back effectiveness*.

## 7. Propensity models (upsell / cross-sell)
- **Purpose:** rank *helpful* suggestions (Section 7.5).
- **Method:** gradient-boosted propensity; uplift modelling where feasible (target
  *persuadable* + *beneficial*, not everyone).
- **Guardrail:** frequency-capped; impulse guard reduces pressure; suggestions are
  better-fit, not just pricier.

## 8. Demand / peak-hour / gaming-demand forecasting
- **Purpose:** staffing, prep, inventory, queue smoothing (Section 12.3–12.4).
- **Method:** time-series + ML (e.g. gradient-boosted / temporal models) with weather,
  events, seasonality, promotions; hierarchical reconciliation store→region→network.
- **Output:** demand curves + **prediction intervals**.
- **Eval:** MAPE/WAPE, calibration of intervals, backtesting; drift monitoring.

## 9. Staffing & inventory optimisation
- **Purpose:** fair rosters (Section 4.5) and lean inventory (Section 12.4).
- **Method:** demand forecast → constrained optimisation (labour rules, rest, fairness;
  supplier lead times, waste).
- **Output:** proposed rosters/orders → **human approval** (Tier C).
- **Guardrail 🔒:** fairness constraints explicit; humane rest limits hard-coded.

## 10. Revenue & expansion models
- **Revenue:** hierarchical forecast + driver attribution + scenario modelling.
- **Expansion:** site/timing scoring from **area-level aggregate market data** (never
  individual sensitive data) + learned success drivers.
- **Eval:** forecast error, backtests; expansion model validated against realised store
  performance.

## 11. Employee wellbeing / burnout-risk model 🔒
- **Purpose:** *early support* (Section 4.4).
- **Method:** transparent composite over self-reported energy/mood + operational workload
  (hours, consecutive shifts, declined breaks, PTO gaps).
- **Output:** burnout risk + **explanation**, shown to the *employee first*.
- **Guardrail (hard) 🔒:** assistive only; routes to *relief/care*; **cannot** emit
  discipline/penalty; human-gated; fairness-audited; short retention.

## 12. Avatar / conversation model
- **Purpose:** the avatar (Section 5).
- **Method:** LLM with a brand-voice system prompt + guardrail policies + consent-scoped
  context (RAG over allowed profile/menu/booking data).
- **Guardrail:** always-clearly-AI, no manipulation, no sensitive talk, no clinical claims,
  graceful human handoff; generation-time safety + brand filter.
- **Eval:** helpfulness, task success, safety red-team, guardrail-violation rate (→0),
  satisfaction.

---

## 13. Model evaluation & MLOps summary

| Concern | Practice |
|---|---|
| Offline eval | Backtesting, replay, holdouts, calibration curves |
| Online eval | A/B tests, bandit reward, guardrail metrics (annoyance/opt-out) |
| Fairness | Pre-deploy proxy/fairness scan + scheduled audits (Section 11) |
| Uncertainty | Confidence intervals / calibrated probs surfaced everywhere |
| Monitoring | Drift, calibration, business + guardrail metrics; alerting |
| Safety | Kill switches, fallback to rules/popular, human-gate on C/D |
| Reproducibility | Registry, versioning, lineage, rollback |

The invariant across all of it: **models inform; humans decide where people are affected;
and no model ever touches a sensitive attribute.**

---

### Change log
- v1.0 — Initial model catalogue.
