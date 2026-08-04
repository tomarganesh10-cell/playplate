# UI Screens & Wireframes

> Apple-grade clarity, Disney-grade delight, privacy as a visible feature. Low-fidelity
> ASCII wireframes below convey layout and intent; a full design system (tokens, components,
> light/dark themes, accessibility) sits atop these. Colour/music/space rationale:
> Section 1.23–1.26.

---

## 1. Design system foundations

- **Voice:** warm, playful, honest, concise. Never pushy, never fake-urgent.
- **Layout:** one hero action per screen; progressive disclosure; generous space.
- **Themes:** full light/dark support; brand accent ownable and consistent.
- **Accessibility:** WCAG AA+ contrast, scalable type, screen-reader labels, keyboard/switch
  nav, captions, "essentials" mode, quiet/sensory-friendly options.
- **Motion:** delightful but respectful (reduced-motion honoured).
- **Trust surfaces:** every personalised element shows a subtle "why" affordance and an easy
  opt-out — privacy is *in the UI*, not buried.

---

## 2. Guest app — key screens

### 2.1 Home ("For You")
```
┌───────────────────────────── PLAYPLATE ─────────────────────────────┐
│  Hi A---  ·  Level 4 Pro  ·  ⨀ 1,240 coins        [profile] [privacy]│
├─────────────────────────────────────────────────────────────────────┤
│  ▶ TONIGHT FOR YOU                                     why? ⓘ  ✕     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │ Squad PS5 7pm │ │ Sharing plate │ │ Cold brew rnd │  ← easy "no"  │
│  │ book · reason │ │ you loved it  │ │ pairs w/ play │               │
│  └──────────────┘ └──────────────┘ └──────────────┘                 │
│                                                                     │
│  ▶ YOUR MISSIONS (daily)          ▶ WHAT'S ON                        │
│  ▢ Play with a friend  +50        · Summer Championship (Sat)        │
│  ▢ Try a new game      +80        · Creator night (Fri)             │
├─────────────────────────────────────────────────────────────────────┤
│  [Home]   [Play]   [Eat]   [Rewards]   [Avatar]                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Order / Eat
```
┌── EAT ────────────────────────── search ────────────────────────────┐
│  For you (because you love these)                       why? ⓘ       │
│  • Smoky peri-peri paneer  ⭐  ·  Add   [ + ]                         │
│  • Loaded nachos (shareable)   ·  Add   [ + ]                         │
│  ─ Full menu ▾ (categories, gaming-friendly filter, veg-forward) ─    │
│  Cart: 2 items · ₹—   [Review & pay]   split-bill · pay-at-table     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.3 Play / Book a station
```
┌── PLAY ─────────────────────────────────────────────────────────────┐
│  PS5 · PC · VR · Racing Sim · Coffee-bar chill                       │
│  Availability tonight:  PS5 ▮▮▮▮▯  (2 slots @7pm)  fair-queue ✓      │
│  Your usual: Station 4 · saved settings  [Quick book]               │
│  Skill-matched tournament: "Casual ladder 8pm"  [Join]              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.4 Rewards (the game layer, Section 8)
```
┌── REWARDS ──────────────────────────────────────────────────────────┐
│  Level 4 Pro  ▮▮▮▮▮▮▯▯  620/800 XP to Legend                        │
│  ⨀ 1,240 coins        🔥 4-visit streak (grace: 10 days)            │
│  Badges: ▣▣▣▢▢     Squad "NightOwls" · rank #3 (casual)            │
│  Missions: daily ▢▢  weekly ▢  monthly challenge ▶                  │
│  [Responsible play settings: limits · take-a-break]  ← always visible│
└─────────────────────────────────────────────────────────────────────┘
```

### 2.5 Avatar
```
┌── AVATAR (AI) ──────────────────────────────────────────────────────┐
│  🤖 "Hey! Want me to start your usual squad booking for 7?"          │
│  [Yes]  [No thanks]  [Talk to a human]        (I'm an AI · privacy ⓘ)│
│  ...  how was your last visit?  😀 🙂 😐 🙁                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.6 Privacy Centre (flagship trust surface) 🔒
```
┌── MY PRIVACY ───────────────────────────────────────────────────────┐
│  Personalisation        [ ON  ●]   what this uses ⓘ                  │
│  Marketing · push       [ ON  ●]   ·  email [OFF ○] · whatsapp [ON ●]│
│  Social / squads        [ ON  ●]   (both friends must agree)         │
│  ── What we hold about you ──  [View all]                            │
│  Your scores explained:  Churn risk 0.62 — "6 wks since last visit" │
│  [Export my data]   [Delete everything]      response within SLA    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Staff app — key screens

### 3.1 Shift home
```
┌── STAFF · Today ────────────────────────────────────────────────────┐
│  Your shift 4–10pm · break due 7:15 (protected)  [Wellbeing check-in]│
│  Floor: 62% full · queue 4 · 2 recovery alerts ▶                    │
│  Recognise a teammate  [＋ kudos]                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Service-recovery alert
```
┌── RECOVERY ─────────────────────────────────────────────────────────┐
│  Table 12 · long wait flagged · guest: regular                      │
│  Suggested: apologise + comp a drink (needs your OK)  [Do it] [Other]│
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Manager / CEO / HR / Marketing dashboards

Layouts follow Section 9. Pattern for every dashboard tile:

```
┌── <TILE> ───────────────────────────────┐
│  <one hero metric>   trend ▲/▼  target   │
│  AI suggestion: "<action>"   why ⓘ  conf │
│  [Approve]  [Modify]  [Dismiss]   ← C/D  │
└─────────────────────────────────────────┘
```

- **Manager "Today":** footfall-by-hour, prep guidance, staffing vs demand, action queue,
  recovery inbox, team wellbeing flags (support-oriented).
- **CEO:** north-star tiles, network map, psychology→revenue view, **Ethics & Trust panel**
  (consent/opt-out/fairness/responsible-play).
- **HR:** burnout heatmap (→ relief), fairness monitors, growth pipeline, manager
  accountability, guardrail banner.
- **Marketing:** campaign performance (satisfaction+retention lift), behavioural segments,
  offer engine with annoyance/opt-out monitoring, community/creator.
- **Kitchen / Gaming:** live queues, demand-driven prep, station status, tournament ops.

Every dashboard: explainable AI, human-approval controls on Tier C/D, role-minimised access,
light/dark, responsive.

---

## 5. In-venue surfaces

- **Kiosk / self-order:** the guest app's order flow, accessible, multilingual, calm.
- **Screens:** ambient "what's on," real (not fake) "popular tonight," tournament hype —
  floor-level social proof, never "we're watching you" individual call-outs. 🔒
- **NFC tap points:** identify (consented), pay (tokenised), start session, apply rewards —
  one tap, minimal data.

---

## 6. Wireframe → design-system handoff

These low-fi frames map to a component library (buttons, cards, tiles, "why" popovers,
consent toggles, mission chips, dashboard tiles) with tokens for colour (zone-aware,
Section 1.23), type, spacing, and motion — themed for light/dark and built accessible-first.
Figma/high-fidelity production is the next step from this spec.

---

### Change log
- v1.0 — Initial UI & wireframe specification.
