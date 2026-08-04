# Section 9 — AI Dashboards

> One brain, many windows. Each role sees exactly what helps them act — no more (privacy
> minimisation 🔒), no less. Dashboards turn the engine's understanding into decisions, and
> every dashboard surfaces **AI recommendations with their reasoning and confidence**, never
> opaque orders.

Design language (Apple DNA): clarity over density, one hero insight per screen, "what
should I do now?" answered at a glance, drill-down on demand. Wireframes: `design/ui-
screens-wireframes.md`. Metrics defined in `delivery/kpis.md` 📊.

---

## 9.1 CEO / Executive Dashboard

**Question it answers:** *Is the whole system healthy and paying off — across regions and
stores?*

- **North-star tiles:** Guest happiness (CSAT/NPS), repeat-visit rate, CLV, revenue,
  employee eNPS — with trend and target.
- **Psychology → behaviour → revenue causal view:** how engagement/loyalty drives revenue,
  per region/store.
- **Store network map:** performance, maturity, and outliers across the 100→1,000 rollout.
- **Cohort & retention curves;** loyalty tier distribution; churn trend.
- **Ethics & trust panel 🔒:** consent opt-in rates, opt-outs, data requests honoured,
  fairness-audit status, responsible-play flags. *Trust is a board-level KPI here.*
- **Forecasts (Section 12):** demand, revenue, staffing, expansion readiness.

---

## 9.2 Store Manager Dashboard

**Question:** *What does my store need today?*

- **Today panel:** forecasted footfall by hour, prep guidance, staffing vs. demand, weather/
  event context.
- **Action queue:** the engine's top suggestions — "regulars likely in tonight, delight
  these," "station 4 due maintenance," "you're understaffed 7–9pm."
- **Live floor (aggregate 🔒):** occupancy, queue/wait, station utilisation, current
  experience-sentiment trend (Section 6) — *for service, not surveillance*.
- **Service recovery inbox:** live negative signals needing a human touch (Section 3).
- **Team snapshot:** who's on, wellbeing/burnout flags to *support* (Section 4), break
  compliance — assistive, human-led.

---

## 9.3 Kitchen Dashboard

**Question:** *What to make, when, in what order?*

- **Live order queue** with smart sequencing and per-item timing.
- **Demand-driven prep 🧠:** "prep +20% paneer for the 7pm rush" (Section 12 forecast).
- **Freshness & waste control:** make-to-forecast to cut waste (sustainability + margin).
- **Accurate ETAs** fed to guests (waiting psychology, 1.25) — honest, not padded.
- **Quality/feedback loop:** dish-level satisfaction signals to improve recipes/portions.

---

## 9.4 Gaming Dashboard

**Question:** *Are the stations, sessions and tournaments running great?*

- **Station status:** utilisation, health, maintenance due, availability for booking.
- **Session & queue view:** fair allocation, wait transparency (1.26).
- **Tournament ops:** brackets, skill-matching (1.21), sign-ups, hype scheduling.
- **Popular-now & demand:** which games/platforms are hot (real social proof, 1.7).
- **Experience quality:** session-level satisfaction, flow-match effectiveness.

---

## 9.5 Customer Dashboard (the guest-facing "my PLAYPLATE")

**Question (for the guest):** *What's here for me — and what do you know about me?* 🔒

- **For You:** recommendations (Section 7), events, tournaments, "what's on."
- **My game (loyalty):** level, coins, XP, missions, badges, streaks, squad, rankings
  (Section 8).
- **My preferences:** favourites, seat, saved settings — editable.
- **My privacy centre 🔒:** *the flagship transparency surface* — what data is held, every
  consent (toggle any off), what each score means and why, one-tap export, one-tap delete.
  Privacy as a **feature the guest controls**, not fine print (Apple DNA, Section 11).

---

## 9.6 HR Dashboard

**Question:** *Is our team well, growing, and treated fairly?* 🔒

- **Wellbeing (aggregate + supportive individual):** burnout-risk heatmap → *relief
  actions*, not rankings (Section 4).
- **Fairness monitors:** schedule fairness, break compliance, preference-honour rate,
  workload balance — and **manager accountability** (are managers acting on flags?).
- **Growth & recognition:** training progress, certifications, recognition given, leadership
  pipeline.
- **Retention & eNPS:** turnover risk, satisfaction trends, exit-reason themes.
- **Guardrail banner:** a persistent reminder that all people-decisions require human
  judgement; the dashboard *informs*, HR *decides* (Section 4 constitution).

---

## 9.7 Marketing Dashboard

**Question:** *What campaigns, offers and community moves work — ethically?*

- **Campaign performance:** reach, engagement, *satisfaction* and retention lift (not just
  clicks), by segment.
- **Segments (behavioural 🔒):** value/lifecycle cohorts (new, regular, champion, at-risk,
  lapsed) — behaviour-based, never sensitive-attribute-based; fairness-audited.
- **Offer & promo engine:** off-peak fill, win-back, referral quality — with annoyance/
  opt-out monitoring (a rising opt-out rate is a red flag, not ignored).
- **Community & creator:** UGC, creator activity, referral network growth, brand affinity.
- **Ethics guardrail:** frequency-cap compliance, consent-scoped targeting, no-dark-pattern
  checks baked into campaign approval (Section 11).

---

## 9.8 Cross-cutting dashboard principles

- **Explainable AI everywhere 🧠:** every AI suggestion shows *why* + *confidence*; nothing
  is a black box.
- **Action-oriented:** each insight pairs with a recommended, human-approvable action.
- **Privacy-minimised access 🔒:** role-based; each role sees the *least* needed; individual-
  level personal data is gated by need + consent; access is logged.
- **Consistent, calm design:** the Apple-grade "one clear thing to do" ethos, in light and
  dark themes, responsive across devices.

---

### Change log
- v1.0 — Initial dashboards specification.
