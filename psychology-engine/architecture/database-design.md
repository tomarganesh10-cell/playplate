# Database Design

> A privacy-first data model. Sensitive attributes are **unrepresentable by construction**;
> consent is a first-class table gating everything; erasure and portability are core
> operations. Schemas below are illustrative (PostgreSQL-flavoured) and per-service in a
> microservice deployment.

---

## 1. Design rules

1. **Sensitive-field firewall 🔒** — no column may store health, religion, caste, ethnicity,
   sexual orientation, political view, biometric identity, precise persistent location, or
   financial status beyond spend-with-us. A **data-catalog policy + CI test** fails the build
   if such a column/feature is introduced (Section 11.6).
2. **Consent gates access** — reads/writes of personal data check `consent` (enforced by the
   Consent & Ethics Guard, not just the DB).
3. **Pseudonymous keys** — `customer_id` is a UUID, not a real-world identifier; PII is
   minimised, encrypted, and separable.
4. **Erasure-ready** — personal data is structured so a delete request hard-deletes or
   irreversibly anonymises, and propagates to models on retrain.
5. **Retention-tagged** — every table has a retention policy (Section 11.7); shortest for
   sentiment/emotion.
6. **Auditable** — an append-only audit log records consequential access and change.

---

## 2. Core entities (ER overview)

```
 customer ──1:1── consent_ledger
   │  1:N
   ├── customer_preference        (favourites, seating, music, drinks — stated/derived)
   ├── customer_score             (derived scores + explanation + confidence + as_of)
   ├── visit ──1:N── order_item / game_session
   ├── loyalty_account ──1:N── loyalty_event (coins/xp/badge/mission)
   ├── feedback ──1:1── sentiment_read (short-retention)
   ├── social_edge (friends/squad; double-opt-in; either side can sever)
   └── data_request (access/export/erasure log)

 employee ──1:1── employee_consent
   ├── wellbeing_checkin (self-reported, short-retention)
   ├── schedule_shift / availability
   ├── growth_record (training, certs, recognition)
   └── ai_suggestion (assistive; human_decision required + recorded)

 store ── region ── (config, models)   |   forecast (demand/revenue/staffing/inventory)
 audit_log (append-only, tamper-evident)   |   automation_action (tier, consent-checked, logged)
```

---

## 3. Selected table sketches

### 3.1 `customer` (minimal PII, encrypted)
```sql
CREATE TABLE customer (
  customer_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  display_name     TEXT,                         -- greeting name (T1)
  birthday_mmdd    CHAR(5),                       -- OPTIONAL, volunteered only (MM-DD)
  relationship_status TEXT,                       -- OPTIONAL, volunteered only; nullable
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  status           TEXT NOT NULL DEFAULT 'active' -- active | erased
  -- NOTE: no sensitive-attribute columns permitted (firewall + CI guard) 🔒
);
-- contact identifiers (email/phone) live in a separate, encrypted, tokenised table
-- with their own consent scope; joined only when consented.
```

### 3.2 `consent_ledger` (the gatekeeper) 🔒
```sql
CREATE TABLE consent_ledger (
  customer_id   UUID REFERENCES customer(customer_id),
  purpose       TEXT NOT NULL,      -- 'personalisation','marketing_push','social', ...
  channel       TEXT,               -- for marketing purposes: push/email/whatsapp/sms
  granted       BOOLEAN NOT NULL,
  tier          SMALLINT,           -- 0..3
  policy_version TEXT NOT NULL,
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (customer_id, purpose, channel)
);
-- fail-closed: absence or granted=false ⇒ the action does not run.
```

### 3.3 `customer_score` (explainable, uncertainty-aware) 🧠
```sql
CREATE TABLE customer_score (
  customer_id UUID REFERENCES customer(customer_id),
  score_name  TEXT NOT NULL,   -- psychology, happiness, loyalty, churn_risk, clv, ...
  value       NUMERIC NOT NULL,
  confidence  NUMERIC,         -- 0..1; low-confidence flagged downstream
  explanation JSONB,           -- top drivers, human-readable
  as_of       TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (customer_id, score_name)
);
-- impulse_buying_score, if present, is policy-flagged: usable ONLY to add restraint (2.2).
```

### 3.4 `sentiment_read` (short retention) 🔒
```sql
CREATE TABLE sentiment_read (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES customer(customer_id),
  visit_id    UUID,
  label       TEXT,        -- happy/excited/confused/bored/angry/disappointed/satisfied/loyal
  polarity    NUMERIC,     -- -1..+1
  confidence  NUMERIC,
  source      TEXT,        -- feedback_text | rating | operational_signal (NEVER biometric)
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL   -- short TTL; purge job enforces
);
```

### 3.5 `social_edge` (double opt-in) 🔒
```sql
CREATE TABLE social_edge (
  a_customer_id UUID REFERENCES customer(customer_id),
  b_customer_id UUID REFERENCES customer(customer_id),
  edge_type     TEXT,      -- friend | squad
  a_consent     BOOLEAN NOT NULL,
  b_consent     BOOLEAN NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (a_customer_id, b_customer_id, edge_type)
);
-- edge is active only when a_consent AND b_consent; either revocation severs it.
```

### 3.6 Employee tables (assistive, human-gated) 🔒
```sql
CREATE TABLE wellbeing_checkin (      -- self-reported, voluntary, short retention
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employee_id UUID NOT NULL,
  mood_1to5   SMALLINT,               -- optional
  energy_1to5 SMALLINT,               -- optional
  note        TEXT,                   -- employee-owned; managers see support-flags, not raw note
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ NOT NULL
);

CREATE TABLE ai_suggestion (          -- ALWAYS assistive
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject_type TEXT,                  -- employee | customer | ops
  subject_id   UUID,
  kind         TEXT,                  -- shift_change, training, recognition, break, coaching...
  rationale    JSONB,
  risk_tier    CHAR(1) NOT NULL,      -- A|B|C|D (Section 10.1)
  human_decision TEXT,                -- required for C/D: accepted/modified/rejected + who
  decided_by   UUID,
  decided_at   TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- No 'discipline'/'penalty' kind is permitted to be emitted (Section 4, 11).
```

### 3.7 `data_request` (rights as operations) 🔒
```sql
CREATE TABLE data_request (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID,
  type   TEXT NOT NULL,   -- access | export | correction | erasure | objection
  status TEXT NOT NULL,   -- received | in_progress | completed
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);
```

### 3.8 `audit_log` (append-only)
```sql
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  actor       TEXT,       -- service | user id | model id
  action      TEXT,       -- read/write/automate/consent_change/human_decision
  subject     TEXT,       -- entity affected (pseudonymous)
  detail      JSONB,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
) WITH (append_only);      -- tamper-evident; retained per policy
```

---

## 4. Analytics & feature store 🔒

- The lakehouse enforces **column/row-level access control** and **tokenisation** of PII.
- The **feature store allow-list** (Section 3.4, architecture) means only approved,
  non-sensitive features are materialised; a registration-time check + pre-deploy
  proxy/fairness scan block sensitive-adjacent features.
- Aggregated/anonymised marts power dashboards without exposing individuals.

---

## 5. Data lifecycle jobs

- **TTL purge** — enforces retention (sentiment/emotion first).
- **Erasure worker** — on `data_request(type='erasure')`: hard-delete/anonymise personal
  rows, sever social edges, flag for model exclusion on next retrain, log completion. 🔒
- **Export worker** — machine-readable portability bundle.
- **Consent propagation** — a consent change immediately updates the guard's cache and
  disables affected processing.

---

## 6. Integrity, performance & partitioning

- Per-service databases (bounded contexts), event-sourced where it aids auditability.
- Time-series tables (visits, sessions, events) partitioned by time; region-sharded for
  residency and scale.
- Indexed for the hot paths (profile lookup, loyalty, recommendation feature fetch).
- Backups, PITR, and DR per delivery/risk-management.md.

---

### Change log
- v1.0 — Initial database design.
