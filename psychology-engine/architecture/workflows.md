# Event & Workflow Design

> The engine is event-driven. This doc catalogues the key domain events and the end-to-end
> workflows that stitch services together — each passing the **Consent & Ethics Guard** and
> respecting the **risk tiers** (Section 10.1).

---

## 1. Core domain events (backbone topics)

| Event | Emitted by | Consumed by (examples) |
|---|---|---|
| `customer.consent_changed` 🔒 | identity-consent | guard cache, customer-360, campaign |
| `visit.started` / `visit.ended` | reservation-nfc/POS | customer-360, sentiment, loyalty, forecasting |
| `order.placed` / `order.fulfilled` | POS/ops | customer-360, loyalty, kitchen, forecasting |
| `session.started` / `session.ended` | gaming/station | customer-360, loyalty, recommendation |
| `booking.created` / `booking.reminded` | reservation-nfc | notification, ops |
| `feedback.received` | avatar/app/staff | emotion-sentiment, service-recovery, dashboards |
| `sentiment.read` 🔒 | emotion-sentiment | service-recovery, avatar, dashboards |
| `loyalty.event` (coins/xp/level/badge) | loyalty-game | avatar (celebrate), customer-360 |
| `forecast.updated` | forecasting | ops-inventory, scheduling, dashboards |
| `wellbeing.checkin` 🔒 | employee-wellbeing | burnout model, HR dashboard (flags only) |
| `automation.action` | any (via guard) | audit |

All events carry a consent/purpose tag; PII is minimised/tokenised on the wire.

---

## 2. Workflow: Guest arrival → delight (real-time)

```
booking.created / nfc.identify (consented)
   └▶ guard 🔒 (consent? tier?)
        └▶ customer-360 assembles profile (consented fields)
             └▶ pre-warm station/settings (Tier A)
             └▶ recommendation: context-aware "for you" (guard-filtered, explained)
             └▶ avatar: warm "welcome back" (clearly-AI, easy-decline)
   ... during visit ...
   session/order events ─▶ mid-visit prompts (Tier B, capped) ─▶ well-timed delight (peak)
   visit.ended ─▶ warm send-off + loyalty celebrate (peak-end, 1.29) ─▶ feedback ask
```

Unconsented guest: same flow, **generic** (popular/context) — no personalisation, no
degradation.

---

## 3. Workflow: Service recovery (the highest-priority loop)

```
feedback.received (negative) OR operational friction (wait breach, order error)
   └▶ emotion-sentiment: label = angry/disappointed (short TTL) 🔒
        └▶ service-recovery workflow:
             ├▶ alert nearest staff/manager (human) — Tier C/D as needed
             ├▶ avatar: empathetic acknowledgement + human handoff
             ├▶ over-correction offer (comp/replacement) — human-approved (Tier C)
             └▶ close the loop: "here's what we did" + log + learn
```

Recovery is human-led warmth, scaled by the engine — never an automated brush-off.

---

## 4. Workflow: Recommendation request

(See system-architecture.md §5 for the step-by-step.) Key: guard → consented profile +
context → candidate gen → guest-value ranking → guardrail filter → explanation →
delivery → interaction event → learning. Fails safe to popular items if a model is down.

---

## 5. Workflow: Birthday delight (opt-in only) 🔒

```
scheduler (daily) ─▶ query volunteered birthdays in window
   └▶ guard 🔒 (birthday provided? marketing consent for the channel?)
        └▶ notification-campaign: warm reward + memorable gesture (Tier B, easy opt-out)
        └▶ in-venue: staff/avatar surprise if they visit (reciprocity, 1.9)
```
No volunteered birthday ⇒ no processing. Never used to pressure a visit.

---

## 6. Workflow: Off-peak demand smoothing

```
forecast.updated (quiet window predicted)
   └▶ identify flexible, consented guests (behaviour-based)
        └▶ guard 🔒 (marketing consent, caps)
             └▶ honest off-peak *incentive* (discount/mission), capped, easy-decline (Tier B)
   (peak windows: NO gouging — only ops prep + fair queueing; Section 1.27)
```

---

## 7. Workflow: Employee wellbeing / burnout (assistive, human-gated) 🔒

```
wellbeing.checkin (voluntary) + workload signals (hours, consecutive shifts, breaks)
   └▶ burnout-risk model 🧠 (explainable)
        ├▶ employee sees their own risk + drivers FIRST
        └▶ if elevated: manager support-flag (relief action), NOT a performance flag
             └▶ ai_suggestion (Tier C/D) ─▶ REQUIRES human decision (recorded)
   (never emits discipline/penalty; manager accountability tracked, Section 9.6)
```

---

## 8. Workflow: Scheduling & inventory (forecast → human approve)

```
forecast.updated ─▶ scheduling optimiser (fairness+rest constraints) ─▶ roster PROPOSAL
                                                                          └▶ manager approves (Tier C)
forecast.updated ─▶ inventory optimiser ─▶ reorder/prep SUGGESTION
                                              └▶ auto within limits / human-approve big orders (Tier C)
```

---

## 9. Workflow: Data-rights (access / export / erasure) 🔒

```
data-request received
   ├▶ access/export: assemble machine-readable bundle ─▶ deliver ─▶ log
   └▶ erasure: erasure-worker hard-deletes/anonymises PII, severs social edges,
               flags for model exclusion on next retrain ─▶ confirm ─▶ log
```
SLA-tracked; the guest sees status in the privacy centre (Section 9.5).

---

## 10. Orchestration & reliability

- **Choreography** for high-throughput real-time flows (events), **orchestration**
  (a workflow engine) for multi-step, human-in-the-loop, or SLA-bound processes (recovery,
  data-rights, scheduling approvals).
- **Sagas + compensation** for multi-service transactions (booking + pay + loyalty).
- **Dead-letter + retry** on every consumer; **idempotency** on effects.
- **Guard is a hard gate** on any step touching personal data or guest-facing persuasion;
  a guard failure aborts the step (fail-closed) and logs it.
- **Everything audited** — each workflow step writes to the audit log for explainability and
  appeal.

---

### Change log
- v1.0 — Initial workflow specification.
