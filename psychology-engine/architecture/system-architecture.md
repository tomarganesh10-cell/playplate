# System Architecture

> Enterprise-grade, multi-tenant, region-federated, privacy-by-design. Built to run one
> store on day one and 1,000+ stores at scale, with the **Consent & Ethics Guard** in the
> path of every personal-data operation.

---

## 1. Architectural principles

1. **Privacy by design & by default** — the Consent & Ethics Guard is a mandatory in-path
   service; sensitive fields are unrepresentable; fail-closed everywhere (Section 11).
2. **Multi-tenant, region-federated** — one platform, per-region "Brain," per-store config.
   New stores inherit everything on opening day.
3. **Event-driven & real-time** — a streaming backbone lets the engine react in the moment
   (recommendations, service recovery) and batch-learn overnight.
4. **Microservices, bounded contexts** — independently deployable services around clear
   domains (identity, profile, recommendation, loyalty, emotion, employee, forecasting, ops).
5. **Human-in-the-loop by construction** — Tier C/D actions cannot auto-execute.
6. **Observability & auditability** — everything logged, traced, explainable, kill-switchable.
7. **Cloud-native, elastic, cost-aware** — scales with footfall; per-store marginal cost of
   intelligence trends to zero.

---

## 2. High-level topology

```
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ CLIENTS                                                                        │
 │  Guest app (iOS/Android/Web) · In-venue kiosk/screens · Avatar · POS ·         │
 │  NFC readers · Staff app · Manager/CEO/HR/Marketing dashboards                 │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 │  (HTTPS / WSS)
        ┌────────▼─────────┐
        │  API GATEWAY      │  authN/Z, rate limit, routing, versioning
        │  + BFFs           │  (per-client backends-for-frontend)
        └────────┬─────────┘
                 │
        ┌────────▼───────────────────────────────────────────────────────────────┐
        │  CONSENT & ETHICS GUARD 🔒 (in-path for every personal-data op)          │
        │  consent check · purpose · frequency caps · tier · dark-pattern policy   │
        │  · human-gate enforcement · fail-closed                                  │
        └────────┬───────────────────────────────────────────────────────────────┘
                 │
 ┌───────────────▼───────────────────────────────────────────────────────────────┐
 │  DOMAIN MICROSERVICES (the Brain)                                              │
 │  Identity/Consent · Customer 360 Profile · Recommendation · Loyalty/Game ·     │
 │  Emotion/Sentiment · Employee Wellbeing · Reservation/NFC · Ops/Inventory ·    │
 │  Forecasting · Notification/Campaign · Avatar/Conversation · Audit             │
 └───────┬───────────────────────┬───────────────────────────┬───────────────────┘
         │                       │                           │
 ┌───────▼───────┐      ┌────────▼─────────┐        ┌────────▼─────────┐
 │ EVENT BACKBONE │      │  FEATURE STORE 🧠 │        │  DATA PLATFORM    │
 │ (Kafka/PubSub) │◀────▶│ (allow-listed,    │◀──────▶│ OLTP + Lakehouse  │
 │ streams        │      │  non-sensitive)   │        │ + Warehouse + ML  │
 └───────┬───────┘      └────────┬─────────┘        └────────┬─────────┘
         │                       │                           │
 ┌───────▼───────────────────────▼───────────────────────────▼───────────────────┐
 │  ML PLATFORM 🧠  training · serving · bandits · monitoring · fairness/proxy    │
 │                  checks · model registry · kill switches                        │
 └────────────────────────────────────────────────────────────────────────────────┘
         (Cross-cutting: IAM, Secrets, Observability, Audit Log, CI/CD, IaC)
```

---

## 3. Core platform components

### 3.1 API Gateway + BFFs 🧩
AuthN/Z (OIDC/JWT), rate limiting, request routing, API versioning, per-client BFFs (guest
app, staff, dashboards) that compose domain services into client-shaped responses.

### 3.2 Consent & Ethics Guard 🧩 🔒
The keystone. A high-availability, low-latency service (with local caching of the consent
ledger) that every personal-data read/write passes through. Responsibilities:
- Verify **consent** for the purpose; enforce **purpose limitation** and **tier**.
- Enforce **frequency caps / quiet hours** on outbound actions.
- Apply **dark-pattern / persuasion policy** checks on guest-facing content.
- Enforce **human-gate** on Tier C/D (Section 10.1) — reject auto-execution.
- **Fail closed**: if it can't verify, the action doesn't run.
- Emit an audit record for every decision.

### 3.3 Event backbone 🧩
Streaming platform (Kafka / cloud Pub/Sub) carrying domain events (order, session, booking,
feedback, level-up, forecast). Enables real-time reactions and decoupled services.
Personal data on streams is minimised/tokenised and consent-tagged.

### 3.4 Feature Store 🧠 🔒
Serves features to models online and offline. **Allow-list enforced**: only approved,
non-sensitive features exist; a proxy-detection/fairness gate runs before any feature or
model reaches production. Sensitive-adjacent features are blocked at registration.

### 3.5 Data platform
- **OLTP** (per-domain databases, e.g. PostgreSQL) for transactional state.
- **Lakehouse/warehouse** for analytics and ML (with PII governance, tokenisation,
  row/column-level access control).
- **Data catalog + policy engine** implementing the sensitive-field firewall (database-
  design.md).

### 3.6 ML Platform 🧠
Training pipelines, model registry, online serving, contextual-bandit infrastructure,
monitoring (drift, calibration, fairness), and **kill switches** per model. Human-gate and
explanation metadata travel with every model output.

### 3.7 Cross-cutting
IAM (least-privilege, RBAC/ABAC), secrets management, full observability (logs/metrics/
traces), **immutable audit log**, CI/CD with the sensitive-field CI guard, and IaC for
reproducible multi-region deployment.

---

## 4. Multi-tenancy & region federation

```
        GLOBAL CONTROL PLANE (config, policy, model registry, catalog)
                 │
     ┌───────────┼───────────┐
   REGION A     REGION B     REGION C     ← per-region "Brain" (data residency 🔒)
     │             │            │
  stores…       stores…      stores…      ← per-store config, inherits region models
```

- **Data residency** honoured per region (Section 11.7).
- **Region-level models** learn from aggregated, privacy-preserving data across that
  region's stores; **no raw cross-region PII pooling**.
- **New store** = new config record + inherited models → instant capability, weeks-to-
  maturity (Section 12.6).

---

## 5. Request lifecycle (a guest recommendation, end to end)

```
 1. Guest opens app → BFF request
 2. API Gateway authN/Z
 3. Consent & Ethics Guard 🔒: is personalisation consented? within caps? allowed content?
 4. Customer 360 (consented fields) + live context assembled
 5. Recommendation service 🧠: candidate gen → rank (guest-value objective) → guardrail filter
 6. Explanation attached; dark-pattern policy re-checked
 7. Response to guest (with "why" + easy dismiss)
 8. Interaction event → backbone → learning + audit log
```

If step 3 fails (no consent), the guest gets a **generic, still-great** experience — no
personalisation, no degradation of core service.

---

## 6. Reliability, scale & cost

- **Elastic autoscaling** on footfall patterns (the forecasting service even pre-warms
  capacity for predicted peaks).
- **Graceful degradation** — if a model service is down, fall back to popular/rule-based
  defaults; the store never stops working.
- **Multi-AZ / multi-region HA**, backups, DR runbooks (delivery/risk-management.md).
- **Cost governance** — per-store cost dashboards; models sized for per-store economics.

---

## 7. Security architecture (summary)

Zero-trust between services (mTLS), least-privilege IAM, encryption in transit/at rest,
tokenised PCI-scoped payments, secrets vault, WAF/rate-limiting at the edge, continuous
security scanning, and the immutable audit log. Full posture: Section 11.8 + delivery/risk-
management.md.

---

## 8. Technology choices (reference, not prescriptive)

| Layer | Reference choice(s) |
|---|---|
| Clients | React/React Native, TypeScript |
| Gateway/BFF | Cloud API Gateway + Node/Go BFFs |
| Services | Go / Python (FastAPI) / Node, containerised (K8s) |
| Events | Kafka or cloud Pub/Sub |
| OLTP | PostgreSQL (per-service) |
| Analytics | Lakehouse (e.g. BigQuery/Snowflake + object store) |
| Feature store | Feast-style / managed |
| ML | Python, managed training/serving, model registry |
| Infra | Kubernetes, IaC (Terraform), multi-region |

These are interchangeable; the *architecture and the guardrails* are the invariants, not the
vendors.

---

### Change log
- v1.0 — Initial system architecture.
