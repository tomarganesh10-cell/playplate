# Section 11 — Ethics & Privacy (The Constitution)

> This is not an appendix. It is the constitution the rest of the engine obeys. Where any
> feature conflicts with a principle here, **the principle wins** — in design reviews, in
> code, and at runtime. This section is written to be *enforceable*, not aspirational.

---

## 11.1 The First Principle

> **We use AI to make people happier, better served, and more valued — using data they
> knowingly give us, for purposes they would be glad to know about. We never infer or act on
> sensitive personal attributes, and no automated system is ever the sole basis for a
> decision that materially affects a person.**

Everything below operationalises this sentence.

---

## 11.2 The Ten Commitments (the enforceable rules)

1. **Consent-first, always.** No personal-data processing without a clear, specific,
   revocable opt-in. Everything works (generically) without consent; consent unlocks
   *better*, never *access* to basic service. (Sections 2, 3.)
2. **Behaviour, not identity.** We model what people *do and prefer*. We **never** infer,
   store, or act on: health/medical/disability, mental-health state, religion, caste,
   ethnicity/race, nationality-as-identity, sexual orientation, gender identity (beyond a
   volunteered greeting/address preference), political views, biometric identity, precise
   persistent location, or financial status beyond spend-with-us. The **schema forbids these
   fields and a CI guard fails the build if one appears** (see database-design.md).
3. **No covert sensing.** No hidden cameras/mics scoring individuals, no facial/voice-
   biometric emotion inference, no gait/movement tracking, no keystroke/panopticon employee
   monitoring. (Sections 3, 6, 4.)
4. **Human-in-the-loop for consequential decisions.** Any decision materially adverse to a
   person (employee discipline/pay, account restriction, denial/degradation of service,
   individualised pricing) is made by an accountable human. AI may inform; it may not decide.
   The system **refuses to emit** "penalise this person" outputs (Section 4). 
5. **No dark patterns.** Banned outright: fake scarcity/urgency/social-proof, drip/hidden
   pricing, pre-ticked paid add-ons, forced continuity, confirm-shaming, hard-to-cancel,
   manufactured expiry pressure, and manipulative loops. (Sections 1.2, 7, 8, 10.)
6. **No exploitation of vulnerability.** High-impulse guests, distressed guests, and
   **minors** get *more* protection and *less* pressure — never targeting. Responsible-play
   and spend/time safeguards are built in. (Sections 2.2, 6.6, 8.8.)
7. **Fairness & non-discrimination.** Models are tested so they don't disadvantage any group
   or use protected proxies; segments are behavioural and audited. No individualised
   *penalty* pricing. (All sections.)
8. **Transparency & explainability.** Guests and employees can see what's held, what scores
   mean, and *why*. AI suggestions carry reasons and confidence. No black-box verdicts about
   people. (Section 9.)
9. **Data rights are first-class operations.** Access, correction, portability (export),
   objection, and **erasure ("right to be forgotten")** are one-tap, honoured promptly, and
   propagate to models on retrain. (Section 2.6.)
10. **Security & minimisation.** Collect the least, keep it the shortest time, protect it the
    hardest (encryption, access control, tokenised payments). Purpose-bound; no silent
    repurposing. (11.6–11.8.)

---

## 11.3 Legal & regulatory alignment

Designed to comply with applicable data-protection and consumer law wherever PLAYPLATE
operates, including (as a baseline) India's **DPDP Act 2023** and **GDPR**-grade principles,
plus consumer-protection rules on advertising, pricing transparency, and unfair practices,
and employment/labour law for the employee system.

Core mappings:
- **Lawful basis:** consent (personalisation, marketing) and legitimate/contractual basis
  (fulfilling an order/booking) — cleanly separated in the consent ledger.
- **Purpose limitation & minimisation:** each field tied to a stated purpose; no scope creep.
- **Data-principal rights:** access, correction, erasure, portability, grievance redressal —
  built into the product (Section 2.6, 9.5).
- **Children:** verifiable parental consent; no behavioural profiling/targeting of minors;
  strictest defaults (11.5).
- **Cross-border & retention:** documented residency and retention schedule (11.7).
- **Grievance officer / DPO** and a published, plain-language privacy policy.

> This bible is a design specification, not legal advice; the program is deployed under
> qualified legal counsel and **Data Protection Impact Assessments (DPIAs)** per region.

---

## 11.4 Consent architecture 🔒

- **Granular & purpose-specific** — separate toggles for personalisation, each social
  feature, each marketing channel, and any enhanced processing. No bundled "accept all or
  leave."
- **Tiered** (T0–T3, Section 2.5) — plain-language asks with a benefit preview.
- **Revocable, symmetric** — turning consent *off* is as easy as turning it on and takes
  effect immediately (and deletes associated data on request).
- **Versioned & logged** — the consent ledger records what, when, which policy version.
- **Fail-closed** — unknown/expired consent ⇒ the personalised action does not run
  (Section 10.3).

---

## 11.5 Minors & vulnerable guests 🔒

- **Highest protection by default:** strictest privacy settings, opt-in only, no behavioural
  profiling or targeted marketing, spend/time limits on, no data retention beyond service
  need.
- **Verifiable parental consent** for anything beyond basic service; children's data walled
  off and never fed to profiling/ad models.
- **Vulnerability-aware design:** the impulse/responsible-play safeguards (2.2, 8.8) and the
  duty-of-care routing (6.6) protect at-risk guests — *reducing* pressure, never exploiting.

---

## 11.6 The technical enforcement layer (how principles become code)

Ethics here is **architecturally enforced**, not merely promised:

- **Consent & Ethics Guard 🧩** — an in-request-path service every read/write passes; it
  checks consent, purpose, caps, tier, and dark-pattern rules, and *fails closed*.
- **Sensitive-field firewall** — a schema + data-catalog policy that makes sensitive fields
  *unrepresentable*; a CI test fails the build if a prohibited field/feature is introduced.
- **Feature-store allow-list 🧠** — models can only consume approved, non-sensitive features;
  a proxy-detection/fairness check runs pre-deployment.
- **Human-gate enforcement** — Tier C/D actions (Section 10.1) are technically incapable of
  auto-execution; discipline/penalty outputs are not emitted at all.
- **Immutable audit log** — every AI suggestion, automated action, consent change, and human
  decision is logged for audit, explainability, and appeal.
- **Kill switches** — per-feature and global switches to instantly disable any capability
  found harmful.

Details: `architecture/system-architecture.md`, `architecture/database-design.md`.

---

## 11.7 Data retention & residency schedule 🔒

| Data class | Retention (default) | Notes |
|---|---|---|
| Sentiment/emotion (session) | Days (short) | Fast decay; earliest to purge |
| Behavioural events (raw) | Rolling window (e.g. 12–24 mo) | Then aggregated/anonymised |
| Customer 360 profile | While account active + grace | Deleted on erasure request |
| Loyalty/transaction records | As required by law/finance | Minimised, access-controlled |
| Employee wellbeing (self-report) | Short | Employee-owned; not long-kept |
| Employee growth records | Tenure + as agreed | The employee's portfolio |
| Audit logs | As required for accountability | Tamper-evident |

Data residency per regional law; cross-border transfers only with safeguards. Anonymised/
aggregated analytics may persist for product improvement.

---

## 11.8 Security posture (summary)

Encryption in transit and at rest; tokenised, PCI-scoped payments (no raw card data);
least-privilege, role-based, logged access; secrets management; regular security review and
pen-testing; breach response and notification plan; vendor/DPA due diligence for any
processor. (Cross-references delivery/risk-management.md.)

---

## 11.9 Governance & accountability

- **AI Ethics & Privacy Board** — cross-functional (product, legal, security, ops, and an
  employee representative); approves any feature that *relies on a bias to change behaviour*,
  touches sensitive-adjacent data, or affects people's livelihoods.
- **DPIA per capability & region** before launch of anything high-impact.
- **Fairness audits** on all people-affecting models, on a schedule and on change.
- **The "Would they thank us?" gate** — every persuasive feature must pass: *would the guest/
  employee, fully informed, thank us for this?* If not, it doesn't ship.
- **Grievance & appeal** — a clear, human, timely channel for guests and employees to
  question or contest any data use or AI-informed decision.
- **Whistleblowing & red-teaming** — staff can flag ethical concerns safely; the system is
  adversarially tested for manipulation and misuse.

---

## 11.10 The bright lines (never, under any KPI pressure)

- Never infer or act on a sensitive attribute. 
- Never covertly sense individuals (face/voice/gait/keystroke).
- Never let AI be the sole basis for a decision adverse to a person.
- Never deploy a dark pattern or fabricate scarcity/social proof.
- Never individualise *penalty* pricing or exploit vulnerability/impulse.
- Never profile or target minors' behaviour.
- Never sell personal data.
- Never make opt-out costly or basic service worse for the unconsented.

These lines hold **even when crossing them would raise a metric.** A number is never a
reason to break the constitution. The trust these lines buy is the deepest moat PLAYPLATE
has (Executive Summary; Gen-Z authenticity, 1.18).

---

### Change log
- v1.0 — Initial ethics & privacy constitution.
