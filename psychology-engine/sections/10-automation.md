# Section 10 — Automation

> Automate the *loop* (understand → anticipate → delight → reinforce), not the *judgement*.
> Routine, reversible, low-risk actions run automatically; anything affecting a person
> adversely, or that's irreversible, keeps a human in the loop.

---

## 10.1 Automation risk tiers 🔒

Every automated action is classified. This table governs the whole section.

| Tier | Definition | Examples | Control |
|---|---|---|---|
| **A — Auto** | Low-risk, reversible, consented, guest-benefiting | "Your usual?" prompt, coin award, birthday reward, prep suggestion, off-peak offer | Runs automatically within guardrails; logged |
| **B — Auto + easy undo** | Reversible but guest-visible | Reservation reminder, mission assignment, push (within caps) | Auto with instant opt-out/undo; frequency-capped |
| **C — Human-approved** | Affects money, access, or a person's treatment | Refund above threshold, comp, campaign launch, roster publish | Engine drafts; human approves |
| **D — Human-only** | Adverse to a person / irreversible / sensitive | Employee discipline, account restriction, safety action, pricing changes | AI may inform; human decides & is accountable (Sections 4, 11) |

**No tier-D action is ever automated.** Marketing/comms automations respect consent and
frequency caps (below). This tiering is enforced in the workflow layer (`architecture/
workflows.md`).

---

## 10.2 The automations (per your brief)

### Reservations 🧩
- Frictionless booking (app/avatar/web) for tables, stations, VR, sim, events.
- Smart availability + off-peak nudging (Section 12 demand smoothing).
- Auto reminders + easy modify/cancel (Tier B); waitlist auto-fill.
- No-show handling that's *fair and forgiving* (grace, not punitive), 🔒.

### NFC Card 🧩
- Tap-to-identify (consented) for instant recognition, loyalty, saved settings, and
  seamless pay (tokenised, PCI-scoped).
- Tap starts a game session, applies rewards, and (opt-in) loads preferences to a station.
- Card loss/erase is one action; data on it is minimal and revocable (🔒).

### Loyalty 🧩
- Automatic coin/XP accrual, level-ups, badge unlocks, streak tracking (Tier A).
- Auto-personalised missions and challenges (Section 8), fairness-bounded.
- Auto-celebration moments (well-timed hype, peak-end delight).

### Birthday campaigns 🧩
- Triggered *only* from a **volunteered** birthday (🔒), within the window.
- Auto reward + a warm, memorable gesture (reciprocity, 1.9) — the signature family/loyalty
  moment.
- Easy opt-out; never used to pressure a visit, just to delight.

### Push notifications 🧩
- Behaviour- and context-triggered, **strictly frequency-capped**, quiet-hours-respecting,
  channel-preference-honouring (Tier B).
- The "stop bothering me" principle (3.5): back off fast on ignores; fewer, better, relevant.

### WhatsApp / Email / SMS 🧩
- Opt-in, consented, preference-managed messaging: booking confirmations, receipts,
  relevant offers, event invites.
- Transactional (booking/receipt) vs. marketing (opt-in, capped) cleanly separated.
- Every message: clear sender, clear value, one-tap unsubscribe (compliance, Section 11).

### CRM 🧩
- The consented Customer 360 (Section 2) as the single source of truth, syncing across
  service, loyalty, and marketing — access-controlled and audited.
- Lifecycle automations: welcome, nurture, win-back, VIP care — all consent-scoped.

### Inventory suggestions 🧩
- Demand-forecast-driven reorder and prep suggestions (Section 12), waste reduction,
  supplier lead-time aware.
- **Suggestions** to a human for approval on significant orders (Tier C); routine top-ups
  can auto within limits.

---

## 10.3 The automation guardrails (cross-cutting) 🔒

1. **Consent-scoped** — an automation touching personal data checks the consent ledger
   first (the Consent & Ethics Guard is in the path).
2. **Frequency & quiet hours** — global and per-channel caps; the engine optimises for the
   *fewest* touches that delight, not the most.
3. **Easy off** — every automated comms stream has one-tap opt-out; opting out never
   degrades core service.
4. **Reversible by default** — Tier A/B actions can be undone; the guest is never trapped.
5. **Human gates on Tier C/D** — money, access, and people decisions get a human.
6. **Everything logged** — for audit, explainability, and the guest's own transparency view
   (Section 9.5).
7. **Fail safe** — if a guardrail check can't be evaluated (e.g. consent unknown), the
   automation *doesn't fire*.

---

## 10.4 How automations are built (the trigger model) 🧩

```
 EVENT (booking, order, session end, birthday, lapse, forecast) 
      │
      ▼
 RULE / MODEL evaluates (is this worth an action? which one? which guest?)
      │
      ▼
 CONSENT & ETHICS GUARD 🔒 (allowed? consented? within caps? not a dark pattern?)
      │
      ▼
 RISK TIER (A/B → act; C → queue for human; D → never auto)
      │
      ▼
 ACT via channel  ──▶  LOG + measure (did it delight or annoy? feed learning)
```

Event/streaming and workflow-orchestration details: `architecture/workflows.md` and
`architecture/apis-microservices.md`.

---

### Change log
- v1.0 — Initial automation specification.
