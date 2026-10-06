# Implementation Roadmap

> From spec to 1,000 stores. Phased to de-risk (privacy and trust first), prove value in one
> store, then scale the *platform* — so each new store inherits the whole engine on opening
> day. Timeboxes are indicative and should be re-baselined against real team capacity.

---

## Phase 0 — Foundations & Trust (≈ Months 0–3)

**Goal:** the non-negotiables before any personalisation ships.

- Stand up the **Consent & Ethics Guard**, consent ledger, and the **sensitive-field
  firewall** (schema + CI guard). 🔒
- Data platform basics: OLTP, event backbone, audit log, IAM, security baseline.
- Legal foundation: privacy policy, DPIA framework, DPDP/GDPR mapping, retention schedule,
  grievance/DPO setup.
- **AI Ethics & Privacy Board** chartered; "would they thank us?" gate live.
- Guest data-rights ops (access/export/erasure) working end-to-end.

**Exit criteria:** a guest can opt in/out granularly, see their data, and delete it — and no
sensitive field can enter the system. *Trust infrastructure before intelligence.*

## Phase 1 — Single-Store MVP (≈ Months 3–7)

**Goal:** prove the core loop in one flagship store.

- **Customer 360** (T0–T2), basic **recommendation** (context + collaborative), **loyalty/
  game** layer (levels, coins, XP, missions, badges), **reservation/NFC**, guest app + avatar
  (Guide + one more).
- **Emotion/sentiment** (voluntary feedback only), **service-recovery** workflow.
- **Manager + Kitchen + Gaming dashboards**; core automations (Tier A/B) with caps.
- Instrumentation for the KPI framework (delivery/kpis.md).

**Exit criteria:** measurable lift in repeat visits / satisfaction / attach rate vs.
baseline in the flagship, with opt-in rates healthy and annoyance/opt-out low.

## Phase 2 — Employee AI & Forecasting (≈ Months 7–11)

**Goal:** the wellbeing and foresight layers.

- **Employee wellbeing/burnout** (assistive, human-gated), **fair scheduling**, growth/
  recognition, **HR dashboard** with manager accountability. 🔒
- **Forecasting**: demand, peak hours, staffing, inventory; kitchen prep automation;
  off-peak smoothing.
- **CEO + Marketing dashboards**; campaign engine (consented, capped).

**Exit criteria:** demonstrable ops efficiency (labour match, waste down) and employee eNPS/
retention improvement — with fairness audits passing.

## Phase 3 — Multi-Store & Federation (≈ Months 11–18)

**Goal:** make it a *platform*, not an app.

- **Multi-tenant, region-federated** deployment; per-store config; region-level models with
  privacy-preserving aggregation.
- **New-store fast-start** (inherit models day one, weeks-to-maturity).
- Full avatar family; richer recommendation (bandits, sequence models); seasons/tournaments
  at scale.
- CLV/churn/expansion models; expansion intelligence.

**Exit criteria:** open a new store and reach personalisation maturity in weeks; region
models measurably lift every store; unit economics of intelligence proven.

## Phase 4 — Scale to 100 (≈ Months 18–30)

**Goal:** industrialise the rollout.

- Rollout playbook + SOPs (delivery/sops.md) for opening stores fast and consistently.
- Cost governance per store; reliability/DR hardened; observability at fleet scale.
- Continuous experimentation platform; model monitoring/fairness at fleet scale.
- Community & creator programs scaled; brand-trust reporting to the board.

**Exit criteria:** 100 stores live on one platform, consistent guest/employee outcomes,
trust KPIs strong, positive engine ROI network-wide.

## Phase 5 — 1,000+ & Emerging AI (≈ Months 30+)

**Goal:** compounding advantage.

- Deepen the learning flywheel; digital-twin/simulation; generative avatar/content;
  predictive service recovery — all constitution-bound with DPIAs.
- International/region expansion with residency compliance.
- Continuous ethics evolution as capabilities grow.

**Exit criteria:** durable category leadership in guest happiness, employee satisfaction, and
trust — the moat compounding with every store and guest.

---

## Cross-phase workstreams (always on)

- **Ethics & privacy** — DPIAs, fairness audits, red-teaming, the "would they thank us?"
  gate on every feature (Section 11).
- **Measurement** — the KPI framework instrumented from Phase 1; every feature A/B-tested
  with guardrail metrics.
- **Change management** — training staff/managers on the *supportive, assistive* use of the
  system (SOPs).
- **Security & reliability** — continuous.

---

## Team shape (indicative)

Product + design; platform/backend; data/ML; mobile/web; **privacy & ethics** (first-class,
not an afterthought); ops/store enablement; security; and an **employee representative** in
governance. Start lean for Phase 0–1; scale with the rollout.

---

## Sequencing principle

**Trust → prove → platform → scale.** Never ship personalisation ahead of the guardrails
that make it safe, and never scale a store experience that isn't yet loved in one store.

---

### Change log
- v1.0 — Initial roadmap.
