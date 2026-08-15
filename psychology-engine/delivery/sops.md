# Standard Operating Procedures (SOPs)

> How people operate the engine day to day, safely and consistently. SOPs turn the
> constitution (Section 11) and the assistive-AI rules (Section 4) into repeatable practice.
> Each SOP: **when**, **who**, **steps**, **guardrail**.

---

## SOP-1 — Handling an AI suggestion (universal)

**When:** any dashboard surfaces an AI recommendation. **Who:** the relevant human owner.
1. Read the suggestion **and its "why" + confidence**.
2. Add context the model can't see (staffing, a difficult guest, a tiny sample).
3. Decide: **Approve / Modify / Reject** — you are accountable for the decision.
4. For Tier C/D (money, access, people) a decision is **required and recorded**.
**Guardrail 🔒:** the AI *informs*; you *decide*. Never rubber-stamp; never treat a score as
a verdict.

---

## SOP-2 — Service recovery (guest had a bad moment)

**When:** a recovery alert fires (long wait, wrong order, lost game). **Who:** nearest
staff/manager.
1. Go to the guest **fast**; acknowledge sincerely (no excuses).
2. Fix the immediate problem.
3. **Over-correct** with genuine generosity (comp/replacement + a small delight) — within
   your approval limit (Tier C above threshold → manager).
4. Close the loop: make sure they leave feeling *cared for*.
5. Log it so the engine and team learn.
**Guardrail:** warmth and honesty; recovery is human-led, never an automated brush-off (1.9).

---

## SOP-3 — Consent & privacy requests

**When:** a guest asks about their data / wants to opt out / export / delete. **Who:** any
staff → privacy centre / support.
1. Reassure: "Absolutely, it's your data and your choice."
2. Point to the **Privacy Centre** (self-serve) or log a data-request.
3. Never make opt-out feel like a loss or degrade their service for it.
4. Escalate anything complex to the DPO/privacy team; honour SLAs.
**Guardrail 🔒:** opting out is frictionless and penalty-free (Section 11.4).

---

## SOP-4 — Responding to a burnout/wellbeing flag (managers)

**When:** an employee shows elevated burnout risk. **Who:** their manager.
1. Treat it as **"how can we help?"**, never "you're underperforming."
2. Have a private, supportive conversation; listen.
3. Provide **relief**: rest, reschedule, redistribute load, PTO.
4. Follow up; record the *support action* (your action is measured, Section 9.6).
**Guardrail 🔒:** wellbeing data is the employee's; you act to support, never to penalise;
never share raw private notes (Section 4).

---

## SOP-5 — Recognition (managers)

**When:** the engine surfaces someone deserving praise (esp. the quiet high performer).
1. Recognise promptly and specifically (public or private per their preference).
2. Use the team recognition ritual; encourage peer kudos.
**Guardrail:** genuine, fair, and inclusive — spread recognition, don't hoard it on the
loudest.

---

## SOP-6 — Performance review (managers/HR)

**When:** periodic review. **Who:** manager + HR.
1. Use the balanced scorecard as **one input**, read **with context**.
2. Gather human observations, peer input, and the employee's self-view.
3. Write a **standalone human rationale** for any decision.
4. **AI never decides** pay/discipline/promotion/termination — you do, with documented,
   defensible reasoning; the employee can respond and appeal.
**Guardrail 🔒 (the line):** no AI output is the sole basis for a livelihood decision
(Section 4.8, 11.2).

---

## SOP-7 — Launching a campaign / offer (marketing)

**When:** any guest-facing campaign.
1. Define the guest value first ("why will they be glad to get this?").
2. Target by **behavioural** segment only; check consent + frequency caps.
3. Run the **dark-pattern checklist** (no fake scarcity/urgency, honest pricing, clear
   unsubscribe, no confirm-shaming).
4. Get ethics-gate sign-off if it *relies on a bias to change behaviour*.
5. Launch as an experiment: pre-register north-star **and** guardrail metrics.
6. Monitor annoyance/opt-out; pull it if guardrails deteriorate.
**Guardrail 🔒:** consent-scoped, capped, honest, and killable (Section 10, 11).

---

## SOP-8 — Model deployment (data/ML)

**When:** shipping/updating a model.
1. Confirm **allow-listed, non-sensitive features only**; run the **proxy/fairness scan**.
2. Verify calibration + uncertainty outputs and explanation metadata.
3. Confirm human-gate metadata for any people-affecting output.
4. Deploy behind an experiment with guardrail metrics + **kill switch**.
5. Register/version; set up drift/fairness monitoring + alerts.
**Guardrail 🔒:** no sensitive/proxy features; fail-safe fallback exists; rollback ready
(Section 11.6, ai-models.md).

---

## SOP-9 — New store opening (ops)

**When:** opening a store. **Who:** rollout team + store manager.
1. Provision store config; inherit region models (fast-start, Section 12.6).
2. Verify guard/consent/privacy flows live **before** any personalisation.
3. Train staff/managers on SOPs 1–6 (assistive, supportive use).
4. Baseline KPIs; enable Tier A/B automations with caps.
5. Ramp personalisation as data matures; monitor trust KPIs.
**Guardrail:** trust infrastructure and staff training **before** intelligence goes live.

---

## SOP-10 — Incident response (privacy/security/ethics)

**When:** a suspected breach, dark-pattern slip, unfair-model finding, or harm report.
1. Contain (kill switch the feature/model if needed).
2. Assess scope; notify DPO/security/ethics board.
3. Remediate; if personal data is involved, follow the **breach-notification** plan and
   legal obligations.
4. Root-cause; fix the *system* (schema/guard/policy), not just the instance.
5. Log, review at the ethics board, and update SOPs.
**Guardrail 🔒:** transparency and speed; protect people first, reputation second.

---

## SOP-11 — Responsible-play intervention (gaming/floor staff)

**When:** long sessions, self-set limits reached, or signs of distress.
1. Offer a friendly "take a break?" and refreshments; respect their choice.
2. Honour any self-set spend/time limits automatically surfaced.
3. For a minor, apply the stricter defaults; involve a guardian appropriately.
4. For genuine distress, respond with warmth and **route to a human / appropriate help** —
   never diagnose (Section 6.6).
**Guardrail 🔒:** care over revenue, always; especially for minors and vulnerable guests.

---

### Change log
- v1.0 — Initial SOP set.
