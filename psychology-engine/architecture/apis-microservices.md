# APIs & Microservices 🧩

> Bounded-context services with clear responsibilities and clean contracts. Every
> personal-data endpoint is fronted by the **Consent & Ethics Guard**; every people-affecting
> action carries a risk tier. Illustrative REST contracts below (GraphQL BFFs and event
> topics also supported).

---

## 1. Service map

| Service 🧩 | Responsibility | Key data |
|---|---|---|
| **identity-consent** | Accounts, auth, the consent ledger, data-rights ops | customer, consent_ledger, data_request |
| **customer-360** | Profile, preferences, derived scores | customer_preference, customer_score |
| **recommendation** | Candidate gen, ranking, explanations | features, item catalog |
| **loyalty-game** | Coins/XP/levels/missions/badges/squads | loyalty_account, loyalty_event |
| **emotion-sentiment** | Experience sentiment (voluntary only) 🔒 | sentiment_read |
| **employee-wellbeing** | Wellbeing, scheduling, growth (assistive) 🔒 | wellbeing_checkin, schedule, growth, ai_suggestion |
| **reservation-nfc** | Bookings, stations, NFC identify/pay | reservation, station, nfc |
| **ops-inventory** | Kitchen queue, prep, inventory suggestions | orders, inventory, forecast |
| **forecasting** | Demand/revenue/staffing/inventory/expansion | forecast |
| **notification-campaign** | Multi-channel, consented, capped comms | campaign, message, caps |
| **avatar-conversation** | Avatar dialogue & feedback capture | conversation |
| **audit** | Immutable audit log, explainability retrieval | audit_log |
| **consent-ethics-guard** | In-path policy enforcement 🔒 | (reads consent, caps, policy) |

All services publish/subscribe domain events on the backbone (see workflows.md).

---

## 2. Cross-cutting API conventions

- **AuthN/Z:** OIDC/JWT; RBAC/ABAC; least privilege. Guest, staff, manager, HR, marketing,
  exec scopes.
- **Consent header/context:** personal-data calls carry the guest context; the guard
  resolves consent + purpose and **fails closed**.
- **Risk tier:** action endpoints declare a tier (A/B/C/D); C/D cannot auto-execute
  (returns a "pending human approval" state).
- **Explainability:** AI outputs include an `explanation` object.
- **Idempotency & versioning:** idempotency keys on writes; `/v1` semantic versioning.
- **Rate limits & frequency caps** enforced at gateway + guard.
- **Errors:** typed problem+json; privacy errors are explicit (`consent_required`).

---

## 3. Representative endpoints

### identity-consent 🧩 🔒
```
POST   /v1/customers                         # create (pseudonymous)
GET    /v1/customers/{id}/consent            # view all consents
PUT    /v1/customers/{id}/consent            # grant/revoke {purpose, channel, tier}
POST   /v1/customers/{id}/data-requests      # access|export|correction|erasure|objection
GET    /v1/customers/{id}/data-requests/{rid}
```
Erasure request → triggers erasure workflow (database-design.md §5).

### customer-360 🧩
```
GET    /v1/customers/{id}/profile            # consented fields only (guard-filtered)
GET    /v1/customers/{id}/scores             # with explanation + confidence
PUT    /v1/customers/{id}/preferences        # guest-editable stated prefs
```
Response example (guard already applied):
```json
{ "customer_id":"...", "display_name":"A==","favourite_games":["..."],
  "scores":{"churn_risk":{"value":0.62,"confidence":0.8,
    "explanation":["6 weeks since last visit","fewer sessions than usual"]}},
  "consent_tier":2 }
```

### recommendation 🧩
```
POST   /v1/recommendations
  body: { customer_id?, context:{store, time, party_size, zone, activity} }
  returns: ranked items + why + dismiss token
POST   /v1/recommendations/{token}/feedback  # accepted|dismissed|show_fewer
```
No `customer_id` (unconsented) ⇒ popular/context-based results (still great).

### loyalty-game 🧩
```
GET    /v1/loyalty/{customer_id}             # level, coins, xp, badges, streak, squad
POST   /v1/loyalty/{customer_id}/events      # accrue (Tier A) — earn coins/xp
GET    /v1/loyalty/{customer_id}/missions
GET    /v1/rankings?scope=store|region&ladder=casual|serious
POST   /v1/squads ... /invite ... (double opt-in) 🔒
```

### emotion-sentiment 🧩 🔒
```
POST   /v1/sentiment/feedback                # voluntary text/rating in → sentiment out
GET    /v1/sentiment/{visit_id}              # short-lived experience read (service use)
```
Rejects any biometric/covert source by contract; short TTL.

### employee-wellbeing 🧩 🔒
```
POST   /v1/employees/{id}/checkin            # voluntary self-report
GET    /v1/employees/{id}/wellbeing          # employee's own view
GET    /v1/managers/{id}/support-queue       # burnout/relief FLAGS (support), not raw notes
GET    /v1/scheduling/proposals              # fair-roster proposals (Tier C → human approve)
POST   /v1/ai-suggestions/{id}/decision      # human accept/modify/reject (required for C/D)
```
No endpoint can emit discipline/penalty (Section 4, 11).

### reservation-nfc 🧩
```
POST   /v1/reservations                      # table/station/VR/sim/event
POST   /v1/nfc/identify                      # consented tap → recognise
POST   /v1/nfc/pay                            # tokenised, PCI-scoped
```

### ops-inventory & forecasting 🧩
```
GET    /v1/forecasts/demand?store=&horizon=  # with prediction intervals
GET    /v1/forecasts/revenue?scope=
GET    /v1/kitchen/{store}/queue
GET    /v1/inventory/{store}/suggestions     # reorder/prep (Tier C for big orders)
```

### notification-campaign 🧩
```
POST   /v1/campaigns                          # created; consent+caps checked; dark-pattern policy
POST   /v1/messages                           # send (guard: consent, channel, cap, quiet hours)
GET    /v1/customers/{id}/comms-preferences   # channels + frequency the guest set
```
Fails closed if consent/cap/quiet-hours not satisfied.

### avatar-conversation 🧩
```
POST   /v1/avatar/message                     # guest turn → avatar reply (guardrailed)
POST   /v1/avatar/handoff                      # escalate to human with (consented) context
```

### consent-ethics-guard 🧩 🔒 (internal)
```
POST   /internal/guard/check
  body: { subject, purpose, action, tier, content? }
  returns: { allow: bool, reason, obligations:[caps, redactions] }
```
Called in-path by every service before a personal-data op or guest-facing content.

---

## 4. Inter-service communication

- **Sync:** REST/gRPC for request/response (recommendation, profile fetch).
- **Async:** events on the backbone (order.placed, session.ended, booking.created,
  feedback.received, loyalty.levelup, forecast.updated) — see workflows.md.
- **Resilience:** timeouts, retries with backoff, circuit breakers, graceful fallbacks
  (rules/popular) so a store never fully stops.
- **Security:** mTLS between services; the guard is a hard dependency for personal-data paths.

---

## 5. External integrations

POS, payment gateway (tokenised), WhatsApp Business / email / SMS providers, review
platforms (consented), and NFC hardware — all via adapter services with their own
rate-limits, retries, and audit. No integration receives more personal data than its
purpose requires (minimisation, Section 11).

---

### Change log
- v1.0 — Initial API & microservice specification.
