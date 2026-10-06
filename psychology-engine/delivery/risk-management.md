# Risk Management

> A living risk register for the Psychology Engine, spanning ethical, legal, technical,
> operational, reputational and human risks — each with a likelihood/impact read, the
> mitigation already designed into this bible, and an owner. Risk management here is not
> paperwork; the highest risks (trust and harm to people) shape the architecture itself.

Scoring: Likelihood/Impact each Low/Med/High. Priority = the combination.

---

## 1. Ethical & privacy risks (highest priority)

| # | Risk | L | I | Mitigation (designed-in) | Owner |
|---|------|---|---|--------------------------|-------|
| E1 | Sensitive-attribute inference/use creeps in | Med | High | Sensitive-field firewall (schema + CI guard), feature allow-list, proxy/fairness scans, ethics board (§11.6) | Privacy/ML |
| E2 | Dark patterns creep in under KPI pressure | Med | High | Nudge charter, dark-pattern ban, ethics gate on persuasive features, guardrail metrics (§1.2, 11.2, kpis) | Product/Ethics |
| E3 | Manipulation of vulnerable/minors | Low | High | Impulse guard, responsible-play, strict minor defaults, verifiable parental consent (§2.2, 8.8, 11.5) | Product/Legal |
| E4 | Covert emotion/biometric surveillance | Low | High | Banned by policy **and** absent from architecture; voluntary-only sentiment (§3, 6, 11.3) | Architecture |
| E5 | Consent fatigue / dark-consent | Med | Med | Granular, benefit-led, symmetric opt-out; great baseline without consent (§11.4) | Product |
| E6 | Model bias harms a group | Med | High | Behavioural features, fairness audits (scheduled + on change), segment-fair KPIs (§11.9) | ML/Ethics |

## 2. Legal & regulatory risks

| # | Risk | L | I | Mitigation | Owner |
|---|------|---|---|-----------|-------|
| L1 | DPDP/GDPR non-compliance | Med | High | Lawful-basis mapping, DPIAs per capability/region, DPO, data-rights ops, retention schedule (§11.3, 11.7) | Legal/Privacy |
| L2 | Children's-data violations | Low | High | Parental consent, no minor profiling, walled data (§11.5) | Legal |
| L3 | Consumer-protection (pricing/ads) | Med | Med | All-in honest pricing, no fake scarcity, no drip pricing (§1.27, 1.8) | Legal/Marketing |
| L4 | Employment-law / surveillance claims | Med | High | Assistive-only employee AI, human-gated decisions, works-council alignment, no covert monitoring (§4, 11) | HR/Legal |
| L5 | Cross-border data transfer | Low | Med | Region federation, residency, transfer safeguards (§11.7, architecture §4) | Privacy/Infra |

## 3. Technical & security risks

| # | Risk | L | I | Mitigation | Owner |
|---|------|---|---|-----------|-------|
| T1 | Data breach | Med | High | Encryption, tokenised PCI payments, least-privilege, mTLS, secrets vault, pen-testing, breach plan (§11.8) | Security |
| T2 | Model drift / degraded quality | Med | Med | Drift/calibration monitoring, alerts, retrain, fallback to rules/popular, kill switches (ai-models) | ML |
| T3 | Guard becomes a bottleneck / SPOF | Med | High | HA + local consent cache, low-latency design, fail-closed but graceful degradation of *personalisation* only (architecture §3.2) | Platform |
| T4 | Over-automation causes a bad action | Low | High | Risk tiers; Tier C/D human-gated; reversibility; audit; kill switches (§10.1) | Platform |
| T5 | Scaling/reliability failures at fleet size | Med | High | Multi-AZ/region HA, autoscaling on forecast, DR runbooks, graceful degradation | Infra |
| T6 | Vendor/third-party (POS, comms) failure | Med | Med | Adapter isolation, retries/circuit breakers, DPAs, minimised data sharing (apis §5) | Platform |

## 4. Operational & business risks

| # | Risk | L | I | Mitigation | Owner |
|---|------|---|---|-----------|-------|
| O1 | Staff misuse AI as authority (e.g. auto-blame) | Med | High | SOPs, training on assistive use, guardrail banners, manager-accountability metrics (§4, SOPs) | Ops/HR |
| O2 | Forecast errors → over/understaffing, waste | Med | Med | Uncertainty-aware forecasts, human approval on rosters/big orders, monitoring (§12, 10.1) | Ops/ML |
| O3 | Loyalty economy unsustainable (breakage/inflation) | Med | Med | Economy modelling & monitoring, fairness + margin audits (§8.3) | Finance/Product |
| O4 | Personalisation filter-bubble / staleness | Low | Med | Diversity/serendipity terms, exploration bandits (§7.4) | ML |
| O5 | New-store rollout inconsistency | Med | Med | Rollout playbook + SOP-9, inherited platform, baseline+monitor (§roadmap) | Ops |

## 5. Reputational & human risks

| # | Risk | L | I | Mitigation | Owner |
|---|------|---|---|-----------|-------|
| R1 | "Creepy AI" perception / trust loss | Med | High | Radical transparency, privacy-as-feature, no covert sensing, authentic marketing, trust KPIs to board (§9, 11, kpis) | Exec/Brand |
| R2 | Employee morale harmed by monitoring feel | Med | High | Wellbeing-first framing, employee voice in governance, self-report centrality, transparency (§4) | HR |
| R3 | Problem-gaming/spending association | Low | High | No real-money gambling mechanics, responsible-play safeguards, healthy-engagement KPIs (§1.11, 8.8) | Product/Ethics |
| R4 | Public incident (breach/bias) mishandled | Low | High | Incident SOP-10, breach plan, honest disclosure, root-cause-the-system | Security/Comms |

---

## 6. Risk governance

- **Ownership & review:** each risk has an owner; the register is reviewed by the **AI Ethics
  & Privacy Board** on a schedule and on any major change.
- **Pre-launch gates:** DPIA + fairness audit + "would they thank us?" gate for high-impact
  features (§11.9).
- **Kill switches:** per-feature and global — any capability found harmful is disabled
  immediately (architecture §3.6).
- **Red-teaming:** adversarial testing for manipulation, bias, and misuse before and after
  launch.
- **Whistleblowing:** a safe channel for staff to raise ethical concerns; concerns are acted
  on.
- **Guardrail-linked KPIs:** the KPI framework (kpis.md) makes many of these risks *visible
  and self-braking* — a rising opt-out or annoyance rate surfaces a risk before it becomes a
  crisis.

---

## 7. The overriding risk principle

> The two risks that can end this program are **harming people** and **losing trust** —
> and they are the same risk. Every other risk is subordinate. That is why the constitution
> (Section 11) sits above the roadmap, and why no KPI is ever a reason to cross a bright
> line. Managed well, the very controls that mitigate these risks become PLAYPLATE's most
> durable competitive advantage.

---

### Change log
- v1.0 — Initial risk register.
