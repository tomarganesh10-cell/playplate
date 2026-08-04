# Section 6 — Emotion AI (Sentiment, Not Sensitive Inference)

> The engine senses **how a visit is going** so it can make it better — from what guests
> *choose* to tell and do. It is a **satisfaction radar**, not a mind-reader. This section
> is written tightly because emotion AI is the area most prone to overreach, and PLAYPLATE
> deliberately takes the narrow, respectful path.

---

## 6.1 The one rule of Emotion AI 🔒

> **Infer sentiment from voluntary signals to improve service. Never infer, store, or act on
> a sensitive attribute or a psychological/medical state — and never from covert biometrics.**

What that means concretely:
- ✅ We detect **"this guest seems delighted / bored / frustrated with the wait"** from
  feedback, ratings, and *operational* service signals.
- ❌ We do **not** detect or guess "this person is depressed / anxious / neurodivergent /
  their mood reveals a health condition," and we do **not** scan faces, voices-as-biometrics,
  or bodies to read emotion covertly.

The difference is *sentiment about an experience* (fair game, service-improving) vs.
*diagnosis of a person* (off-limits, harmful, banned).

---

## 6.2 The emotions we recognise (per your brief) — as *experience sentiment*

| Label | What it means here | Primary signals (voluntary/operational) | Response |
|---|---|---|---|
| **Happy** | Visit going well | Positive feedback, high rating, reorders, smiles-in-words | Reinforce; deepen delight; capture as a great memory (peak-end) |
| **Excited** | High positive arousal | Tournament sign-ups, hype language, streaks | Amplify (celebrate, community) |
| **Confused** | Needs help/clarity | "how do I…", hesitation, avatar questions | Proactive help, simplify, guide |
| **Bored** | Under-stimulated | Long idle, low engagement in a lull | Suggest something fun; check in |
| **Angry** | Something went wrong | Complaint, low rating, escalation words | **Immediate human service recovery** |
| **Disappointed** | Below expectation | Negative feedback, unmet request | Recover, make it right (reciprocity 1.9) |
| **Satisfied** | Solidly good | Positive-neutral feedback, repeat behaviour | Nurture toward loyalty |
| **Loyal** | Advocacy/attachment | Repeat, referrals, UGC, high affinity | Recognise, reward, elevate to champion |

> These are **experience states inferred from consented interaction**, decaying quickly and
> used only to serve the guest better in the moment or fix a problem.

---

## 6.3 Where the signals come from (allowed sources only)

1. **Voluntary feedback** — avatar check-ins (Section 5), ratings, reviews, surveys, free
   text (sentiment-analysed).
2. **Service/operational patterns** — wait time exceeded, order remade, session interrupted,
   long idle — *situational* signals about the *experience*, not the person.
3. **Consented interaction behaviour** — engagement with offers/content, reorders,
   sign-ups.

**Explicitly excluded sources 🔒:** covert facial-emotion recognition, voice-biometric
affect scoring, body/gait reading, any camera/mic used to score an individual's emotion
without their knowledge and consent. These are banned by policy *and* absent from the
architecture (Section 11, system-architecture.md).

---

## 6.4 How it works 🧠

- **Text/feedback sentiment** — a sentiment/intent model over *voluntary* language,
  producing a session `mood_score` (−1…+1) and emotion label with a confidence.
- **Operational rules** — deterministic signals (wait breach, order error) map to
  friction/emotion flags.
- **Fusion** — a transparent combiner yields the current experience-emotion + confidence,
  with **fast decay** (session-scoped) and **low retention**.
- **Uncertainty honoured** — low-confidence reads produce *gentle* responses ("everything
  good?"), never confident assumptions.

Full model and retention specs: `architecture/ai-models.md`, Section 11 retention schedule.

---

## 6.5 What the engine *does* with an emotion read

- **Negative (angry/disappointed) → recover.** Trigger human-led service recovery, an
  apology, and an over-correction (1.9). This is the highest-priority path.
- **Confused → help.** Proactive, simple assistance from avatar or staff.
- **Bored → offer fun.** A light, easy-to-decline suggestion.
- **Happy/excited → amplify & remember.** Deepen the peak, celebrate, and store the *good*
  memory to inform future delight.
- **Satisfied/loyal → nurture & recognise.** Move toward loyalty and advocacy.

Every response is a *service* action. An emotion read **never** feeds price, access denial,
profiling, or any adverse individual decision. 🔒

---

## 6.6 Vulnerability & duty of care 🔒

If voluntary input suggests genuine distress or a safety concern, the system does **not**
diagnose or exploit. It responds with human warmth, avoids clinical claims, and **routes to
a human and to appropriate help/resources**. Care, not analysis. This is a wellbeing
safeguard, not a data-collection opportunity, and any such data is minimised and protected.

---

## 6.7 Guardrails, restated 🔒

- Sentiment about *experiences*, from *voluntary* signals — yes.
- Inference of *sensitive personal attributes or health/psychological states* — **never.**
- Covert biometric/facial/voice emotion scoring — **never.**
- Emotion reads used adversely (price, access, profiling) — **never.**
- Short retention, fast decay, guest-inspectable, deletable.

Emotion AI at PLAYPLATE is, deliberately, the *humble* kind: it knows when a guest is
having a rough visit and rushes to fix it — and it knows to stay firmly out of the business
of deciding who a person is.

---

### Change log
- v1.0 — Initial emotion-AI specification.
