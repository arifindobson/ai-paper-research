# ParaExpress Phase 0 — Foundations

**Execution plan, months 0–4 · technical and business**

Companion to [ROADMAP.md](ROADMAP.md) and `paraexpress.tex`.
Audience: engineering leads, commercial, legal, finance, HR, and field operations. Written so that a non-engineer can read the whole thing.
Status: planning draft. Figures marked *(est.)* are planning-grade; figures marked *(TBC)* require an owner's input before the plan is committed.

---

## 0. TL;DR for the steering committee

**What Phase 0 delivers:** not a delivery service. It delivers the *instrument and the plumbing* that let us open fulfillment nodes without guessing — plus signed agreements and trained people, so that Phase 1 can switch on 15–25 store nodes without a single new negotiation.

**No consumer sees anything in Phase 0.** That is intentional. The paper's Theorem 1 proves the network design problem is NP-hard: there is no spreadsheet that tells us where to put nodes. We build the calculator before we spend on concrete.

| | |
|---|---|
| **Duration** | 4 months at 11 engineering FTE — **or 7 months at 6 FTE**. This is decision D-1 and everything else follows from it. |
| **Engineering effort** | 182 engineer-weeks across 4 squads |
| **Non-engineering effort** | 8 legal/compliance items, 6 commercial, 9 process, 7 people/org, 5 data, 4 finance, 3 property |
| **Longest lead time** | Marketplace instant-program enrolment: **3–6 months, outside our control.** Must start in week 1 or it becomes the Phase 1 blocker. |
| **Exit gate** | Digital twin certified (≤10% replay deviation) · zero oversells under a 72-hour stress test · all Phase 1 agreements signed · 25 candidate store doors ranked and 15 contracted |
| **Biggest risk** | Staffing. Not technology. See [§15](#15-phase-0-risks). |

**Three things that must start in week 1** even though they look like they could wait:

1. **Marketplace enrolment** (C-01) — longest lead time in the whole programme, and we do not control it.
2. **Calibration data capture** (T-18) — the only item where deferral is *permanent*. History we do not record cannot be recovered, and the twin has nothing to learn from.
3. **Consignment addendum drafting** (L-01) — it gates every single store node, and it must be a template we replicate, not a negotiation we repeat 25 times.

---

## 1. What Phase 0 is, in business terms

ParaExpress promises a beauty order delivered in under 60 minutes, from the ParagonCorp-controlled point nearest the consumer, on whatever channel they bought it. Phase 0 builds four things that make that promise possible and honest:

**1. A truthful stock picture across the whole network.**
Today, stock sitting in a consignment store is visible to that store. It is not visible as *sellable-right-now* inventory to Shopee, to brand.com, or to a router deciding where an order should go. The Virtual Inventory Service creates one authoritative answer to "can this specific item be sold from this specific location this second?" — and makes that answer safe to act on even while the store is also selling the same shelf to a walk-in customer.

**Why it matters commercially:** overselling on a marketplace instant programme is not a bug ticket. It is an account-level penalty and a public trust failure. This is the item that cannot be rushed.

**2. A computed delivery promise.**
Most competitors quote delivery from a static table by postcode. We compute it per order, live, from actual stock, actual queue length at the node, and an actual courier ETA. The consumer sees an honest promise *before* they pay.

**Why it matters commercially:** across every benchmark in the paper, the pre-checkout promise is the conversion lever — more than the delivery itself. A promise we can keep 95% of the time and show up front is worth more than a faster one we show after payment.

**3. Consignment doors converted into fulfillment points.**
Roughly 2,000 SKUs sit across ParagonCorp's brands, and a network of consignment stores already carries them. Corollary 1 of the paper says something commercially unusual: because activating a door costs approximately nothing in fixed cost, *any* door that adds coverage adds profit. Competitors without a store estate cannot copy this. Phase 0 builds the app, the ledger separation, and the contract template that turn a shop into a fulfillment node.

**Why it matters commercially:** this is the moat. Astro and Shopee must lease every square metre of their coverage. We start with an endowment.

**4. A digital twin that decides where nodes go.**
Because the design problem is provably unsolvable by inspection, we build a simulator calibrated on our own history. It answers: how many nodes in this metro, which doors first, what stock in each, how many pickers per shift. Nothing opens without it.

**Why it matters commercially:** it converts network expansion from a capital argument into a measurable forecast with confidence intervals. It is also the governance mechanism that stops the Getir failure mode — growth funded by promotion into markets that were never going to clear break-even.

### 1.1 What Phase 0 is explicitly *not*

- Not a pilot. No consumer orders are fulfilled. That is Phase 1.
- Not a new storefront or app. ParaExpress is a capability behind existing channels.
- Not a fleet. We rent last-mile capacity from Grab/GoSend throughout. Owning riders is deliberately excluded until a measured trigger fires.
- Not a warehouse programme. The existing NDC/DC backbone is untouched — Tegal keeps shipping standard parcels exactly as today.

---

## 2. Plain-language glossary

Read this once and the rest of the document is readable without an engineering background.

| Term | What it actually means |
|---|---|
| **PX1 / PX2 / PX3** | The three delivery promises. PX1 = under 60 minutes, kept 95% of the time. PX2 = same-day within a 4-hour slot. PX3 = next-day, which is what we already do from Tegal today. |
| **Node** | Any place an order can be picked and handed to a courier. Three kinds: a **store node** (a consignment shop with a locked ParaExpress shelf), a **dark MFC** (a small 150–300 m² warehouse with no shopfront), and a **flagship MFC** (larger, holds the long tail). |
| **MFC** | Micro-Fulfillment Center. A small warehouse optimised for speed, not storage. No customers walk in. |
| **ATP — Available to Promise** | The number that answers "can I actually sell this item from this location right now?" It is on-hand stock minus what is already reserved minus a safety buffer. Getting this wrong means overselling. |
| **VIS / DOM** | Virtual Inventory Service / Distributed Order Management. The system that owns ATP for the whole network and decides cross-node questions (split the order? substitute a size? this node just went down, where does the order go?). |
| **ORE** | Order Routing Engine. Given an order and all nodes that could serve it, picks the cheapest one that will make the promise. |
| **ADR / Promise API** | Available-to-Deliver Rate. The service that produces the live delivery promise shown at checkout, in under 50 milliseconds. |
| **ParaTwin** | The digital twin — a simulator of the whole network, calibrated on real history, used to decide where nodes go and what they stock before we commit money. |
| **Pre-matching** | Booking the courier at the moment picking *starts* rather than when packing *finishes*, so the rider is arriving while we are still packing. Small change, large effect — see below. |
| **`t_node`** | Total minutes an order spends inside a node: waiting, picking, packing, handover. Every minute cut here widens our reach and reduces the number of nodes we need. |
| **`ℓ` (posting latency)** | How long it takes a store's walk-in sale to reach our system. If this is slow, we must hold a larger safety buffer, which wastes shelf space. Target: under 5 minutes. |
| **Forward assortment** | The subset of SKUs held at a node. A store node holds 150–300; a dark MFC 400–600. Chosen per neighbourhood, not by a national planogram. |
| **Twin-gated** | A governance rule: no node opens, and no assortment changes, without the twin's forecast and sign-off. |

### 2.1 The one number worth memorising

Cutting **`t_node` from 15 minutes to 8 minutes removes about 25% of the fulfillment nodes we need** — because reach grows linearly with saved time, and the area covered grows with the square of reach.

Courier pre-matching alone recovers roughly 3 of those minutes. It is about six weeks of engineering work, and it means **around 12% fewer nodes** — each of which costs IDR 35–60M per month in rent. It pays for itself inside one quarter and keeps paying.

This is why the Phase 0 backlog is weighted toward speed inside the node, not toward building more nodes.

---

## 3. Objectives and definition of done

Phase 0 is complete when all five gates pass. Each has a named owner who signs.

| Gate | Criterion | Owner signs |
|---|---|---|
| **G1 — Twin certified** | Feed one historical week of real orders through ParaTwin; every KPI within 10% of what actually happened. Then forecast the following week ahead of time and score the prediction intervals. | Head of Data/R&D |
| **G2 — Inventory correctness proven** | 72-hour stress test with store posting latency deliberately degraded to 15 minutes: **zero oversells**. Plus VIS sustaining 5,000 reservations/second with an availability-zone failure injected mid-test. | Head of Platform Engineering |
| **G3 — Commercial ready** | Marketplace instant-programme enrolment confirmed for at least one platform; Grab and GoSend commercial terms signed; consignment addendum template approved by counsel. | Head of Commercial |
| **G4 — Field ready** | 25 candidate doors ranked by the twin's marginal-coverage order; at least 15 contracted; store staff trained; PX app accepted in field trial at 3 doors. | Head of Field Operations |
| **G5 — Governance live** | Node-opening approval workflow operating; oversell incident runbook rehearsed once; accuracy-score dispute process agreed with a partner representative. | Programme Director |

**What we deliberately do not gate on:** delivery speed. No consumer order is fulfilled in Phase 0, so any speed number would be theatre. Speed is Phase 1's gate.

---

## 4. Track T — Technical backlog

Mapped to the ROADMAP workstream IDs. "Business meaning" is what a non-engineer should understand about each.

| ID | Item | Business meaning | Squad | Eng-wk |
|---|---|---|---|---|
| **T-01** | VIS ATP ledger core *(W1)* | The single truthful answer to "is this sellable right now" — and the thing that stops us overselling | A | 24 |
| **T-02** | VIS buffer engine *(W1b)* | Automatically sizes each store's safety buffer from how fast that store actually reports its walk-in sales. Good stores get to use more of their shelf. | A | 6 |
| **T-03** | Event bus + transactional outbox *(W21)* | The wiring. Guarantees a message is never lost and never double-counted between systems. | A | 12 |
| **T-04** | Security baseline *(W25)* | Service-to-service authentication, node-level access control, and consumer addresses tokenised so they exist only where they are needed and are purged after delivery. Retrofitting this later costs 3–4×. | A | 8 |
| **T-05** | Promise API / ADR *(W11)* | Produces the delivery promise shown at checkout in under 50 ms | B | 12 |
| **T-06** | Order state machine + SLA clocks + waterfall *(W12)* | Tracks every order against its promise, and gracefully downgrades PX1→PX2→PX3 rather than promising and then cancelling | B | 10 |
| **T-07** | brand.com + WhatsApp adapters *(W13a)* | Our own channels first — they need no partner permission, so they de-risk the marketplace dependency | B | 6 |
| **T-08** | Bundle explosion with co-location *(W14)* | Beauty sells in regimen sets and gift bundles. This keeps a bundle in one node so it ships as one parcel — splitting destroys the unit economics. | B | 6 |
| **T-09** | SLA cockpit *(W15)* | The screen where operations sees promise attainment by zone and node, with the reason for every breach. Without it, Phase 1's gate cannot be measured. | B | 6 |
| **T-10** | ORE feasibility filter, cost model, **decision log** *(W5)* | Chooses the node. The decision log matters more than the chooser: every decision is replayable, which is what lets the twin and the live network stay in sync. | B | 10 |
| **T-11** | Exagon+ reserved virtual location *(W3b)* | ParaExpress stock kept as a separate ledger location and a physically locked shelf — not mixed with the shop's floor stock | C | 6 |
| **T-12** | Exagon+ PX store app *(W3)* | The Android app a shop assistant uses to accept, pick, pack and hand over an order, with timers and photo proof | C | 14 |
| **T-13** | Exagon+ accuracy scoring *(W4)* | Scores each door on stock accuracy and pick reliability; low scorers get sent fewer orders. Self-correcting, and it makes quality a partner's own commercial interest. | C | 4 |
| **T-14** | POS sale posting within 5 minutes *(W2)* | Walk-in sales must reach us fast, or we must reserve more buffer stock. **Mostly an operations and integration problem, not a coding one.** | C | 8 |
| **T-15** | **Courier pre-matching *(W7)*** | Book the rider at pick start, not pack end. Highest return per unit of effort in the entire programme. | C | 6 |
| **T-16** | Rate shop + dual-carrier failover *(W8)* | Quote Grab and GoSend per order, fail over in under 30 seconds. Protects us from one carrier's surge pricing or outage. | C | 10 |
| **T-17** | ParaTwin analytical layer *(W18)* | The calculator: how many nodes, which doors in what order, what stock, how many pickers. Six weeks of work that answers most Phase 0–1 planning questions. | D | 6 |
| **T-18** | **Calibration data contracts + lakehouse *(W20)*** | Starts recording the history the twin learns from. **The only irreversible item — unrecorded history cannot be recovered.** | D | 14 |
| **T-19** | ParaTwin simulation kernel + trace replay *(W19a)* | The simulator itself, plus the replay test that gate G1 depends on | D | 14 |
| | | | **Total** | **182** |

---

## 5. Track P — People & Organisation

The most common way a programme like this fails is not technical. It is that eleven engineers were assumed and six were available, or that nobody owned the store partner relationship.

### 5.1 Backlog

| ID | Item | Owner | Lead time | Why it matters |
|---|---|---|---|---|
| **P-01** | **Confirm Phase 0 engineering headcount** — 11 FTE for 4 months, or 6 FTE for 7 months | CTO / Programme Director | **Week 1 — blocks everything** | Every date in this plan is a function of this number. Deciding it late does not delay the decision; it delays the programme. |
| **P-02** | Appoint Programme Director with cross-functional authority | CEO / CTO | 2 weeks | Phase 0 spans engineering, commercial, legal, field ops and finance. Without single-point authority, the non-technical tracks will each wait for the others. |
| **P-03** | Hire or second **2 specialist engineers**: one operations-research/optimisation, one simulation | HR + CTO | **8–12 weeks** | ParagonCorp is unlikely to have discrete-event simulation and min-cost-flow experience in-house. This is the longest people lead time. Start immediately; consider contract-to-hire or an academic partnership as a bridge. |
| **P-04** | Recruit Field Operations Lead for store nodes | HR + Head of Field Ops | 6 weeks | Owns door recruitment, training, and the partner relationship. This role does not exist today and it is the difference between 25 signed doors and 25 unreturned phone calls. |
| **P-05** | Define squad topology and decision rights (RACI) | Programme Director | 2 weeks | See §12. Publish who decides what, especially who can say no to a node opening. |
| **P-06** | Build store-staff training curriculum and certification | Field Ops Lead | 6 weeks | A shop assistant must pick, pack and hand over within 7 minutes. That is a trained skill, not an instruction sheet. |
| **P-07** | Change-management plan for existing DC and B2B teams | HR + Head of Supply Chain | 4 weeks | The B2B organisation will reasonably read this as cannibalisation. The paper's answer — store nodes share the economics with the very doors that would otherwise lose the sale — needs to be communicated by leadership, early, before it is inferred. |

### 5.2 Capability gaps to resolve

| Capability | Likely position today | Recommendation |
|---|---|---|
| Discrete-event simulation | Gap | Hire or partner (university OR group). Highest-risk gap — G1 depends on it. |
| Optimisation / min-cost flow | Gap | Hire one; the theory is settled in the paper, so this is implementation not research. |
| Distributed ledger correctness (linearizability, RPO 0) | Partial | Senior platform engineer with payments or ledger background. Do not staff T-01 with generalists. |
| Android field application | Partial | Existing mobile capability likely sufficient for T-12. |
| Data engineering / lakehouse | Present | Redeploy from existing analytics function. |
| Field partner operations | Gap | P-04 hire. |

---

## 6. Track L — Legal & Compliance

> Every item below is a **backlog item for counsel to own and resolve**, not a legal conclusion. Regulatory positions must be confirmed against current Indonesian law and current BPOM/BPJPH guidance before Phase 1 commits.

| ID | Item | Owner | Lead time | The exposure |
|---|---|---|---|---|
| **L-01** | **Consignment agreement addendum** — reserved stock ownership, pick SLA, per-order fulfillment fee, cycle-count duty, accuracy obligations, termination | Legal + Commercial | **8–12 weeks** | Gates every store node. Must be a **template**, negotiated once and replicated. Door-by-door negotiation makes 25 doors a 6-month exercise. |
| **L-02** | **Employment / outsourcing exposure at store nodes** | Legal + HR | 6 weeks | A shop assistant performing ParaExpress picking, to our SLA, using our app, paid a per-order fee. Counsel must confirm this does not create an employment or prohibited-outsourcing relationship under prevailing manpower regulation. **This is the least obvious and most consequential legal item in Phase 0.** |
| **L-03** | **Personal data protection review** (UU PDP) | Legal + Security | 6 weeks | Consumer names, addresses, phone numbers flow from marketplaces through our systems to couriers. Confirm lawful basis, retention limits, cross-border position, and breach-notification duties. T-04's tokenisation design should be reviewed against counsel's conclusions, not the reverse. |
| **L-04** | **Cosmetics storage & distribution compliance** (BPOM) | Regulatory Affairs | 6 weeks | Storing registered cosmetics in a consignment shop's back room and in a leased dark MFC. Confirm storage-condition, record-keeping, batch-traceability and recall obligations at each node type. **A recall must be executable across 25 store nodes** — confirm the mechanism before doors are signed. |
| **L-05** | **Halal certification chain integrity** (BPJPH) | Regulatory Affairs | 6 weeks | ParagonCorp's halal positioning is a core brand asset. Confirm what storage segregation and handling obligations follow the product into a third-party store node, and what documentation each node must retain. |
| **L-06** | **Courier liability and goods-in-transit insurance** | Legal + Risk | 4 weeks | GrabExpress and GoSend cap their liability by declared value. A basket of premium skincare can exceed that cap. Confirm who bears loss, and whether supplementary insurance is needed. |
| **L-07** | **Marketplace instant-programme terms review** | Legal + Commercial | 4 weeks | Seller-fulfilled instant programmes carry SLA penalty regimes and liability terms. Understand the penalty exposure *before* enrolling, and feed it into the Phase 1 economics. |
| **L-08** | **Tax treatment of per-order fulfillment fees and consignment settlement** | Tax + Finance | 6 weeks | New money flow: a per-order fee paid to a partner store. Confirm VAT and withholding treatment, and design it into the Exagon settlement cycle rather than bolting it on. |

---

## 7. Track C — Commercial & Partnership

| ID | Item | Owner | Lead time | Note |
|---|---|---|---|---|
| **C-01** | **Marketplace instant-programme enrolment** (Shopee and/or TikTok Shop/Tokopedia) | Head of Commercial | **3–6 months** | **Longest lead time in the programme and entirely outside our control.** Start week 1. Phase 1's gate depends on at least one platform confirmed. Decision D-2 selects which platform leads. |
| **C-02** | Grab / GoSend commercial terms — volume-tiered per-km, API access, pre-matching support | Commercial | 8 weeks | Dual-carrier from day one. Single-carrier terms create surge exposure that no amount of routing intelligence can price around. |
| **C-03** | Store-node partner recruitment — 25 candidates, 15 contracted | Field Ops Lead | 8 weeks | **Recruit against the twin's marginal-coverage ranking, not by store size or standalone sales.** The paper is explicit that the intuitive ordering is the wrong one. Requires T-17 to be running first. |
| **C-04** | Store-node fee structure design | Commercial + Finance | 6 weeks | The per-order fee sits inside the router's cost function. Set too high and the system will route *around* the store estate the whole strategy depends on. Requires modelling with T-17. |
| **C-05** | MOSTRANS mid-mile framework agreement | Commercial | 8 weeks | Deferrable to late Phase 1 — Parama covers a single pilot cluster — but negotiating early costs nothing and de-risks Phase 3. |
| **C-06** | Partner communications pack for consignment doors | Commercial + Marketing | 4 weeks | The pitch to a shop owner: instant-commerce capability they could not build alone, plus a new revenue line. This is what makes the addendum signable. |

---

## 8. Track PR — Process & Governance

These are processes that **do not exist today** and cannot be improvised in Phase 1.

| ID | Process | Owner | Lead time | Why it is needed |
|---|---|---|---|---|
| **PR-01** | **Node-opening approval workflow** | Programme Director | 4 weeks | The twin-gated rule made real: a documented path from twin forecast → business case → approval → opening. Without it, "twin-gated" is a slogan and nodes will open on enthusiasm. |
| **PR-02** | **Twin certification governance** | Head of Data/R&D | 4 weeks | Who certifies a twin version, what the artifact looks like, what invalidates it, and the monthly re-certification cadence. A twin nobody re-certifies drifts silently — the classic failure. |
| **PR-03** | **Oversell incident runbook** | Ops + Platform Eng | 4 weeks | What happens in the first 15 minutes after an oversell: consumer communication, marketplace notification, root cause, buffer adjustment. Rehearse once before Phase 1. |
| **PR-04** | **Accuracy-score dispute process** | Field Ops + Commercial | 4 weeks | Scores gate a partner's order volume, therefore their income. They *will* be disputed. Agree the appeal path with a partner representative before the first score is published. |
| **PR-05** | **Cycle-count SOP for store nodes** | Field Ops + Supply Chain | 6 weeks | Blind counting on an ABC schedule, executed by shop staff, reconciled in Exagon. This is the control that keeps the inventory picture honest. |
| **PR-06** | **Weekly assortment re-optimisation process** | Category + Supply Chain | 4 weeks | The twin proposes a new forward assortment weekly. Who reviews it, who can override it, and how the change reaches the shelf. |
| **PR-07** | **SLA breach root-cause taxonomy and review cadence** | Ops | 3 weeks | Every breach tagged queue / pick / courier / traffic. The tags matter more than the rate — each points at a different fix and a different owner. |
| **PR-08** | **Gate review cadence and artifact pack** | Programme Director | 2 weeks | Fortnightly steering review; the Phase 0 exit pack defined in §16 so it is assembled continuously rather than written in the final week. |
| **PR-09** | **Recall execution procedure across distributed nodes** | Regulatory Affairs + Supply Chain | 6 weeks | Stock sits in 25 third-party locations. A batch recall must reach all of them, verifiably, within the regulatory window. Links to L-04. |

---

## 9. Track D — Data & Master Data

Quietly one of the most common Phase 0 blockers: the algorithms are fine, but the master data is not good enough to feed them.

| ID | Item | Owner | Lead time | Why |
|---|---|---|---|---|
| **D-01** | **Item master enrichment** — dimensions, slot class, brand block, halal lot and expiry attributes for ~2,000 SKUs | Master Data + Category | 8 weeks | The assortment optimiser needs slot requirements per SKU. If dimensions are missing or wrong, every shelf plan is wrong. **Audit early — this is usually worse than expected.** |
| **D-02** | Bundle bill-of-materials | Category | 6 weeks | T-08 cannot explode a bundle it cannot resolve into components. |
| **D-03** | Demand-zone polygon definition (kelurahan-level) and pilot cluster boundary | Data/R&D + Commercial | 4 weeks | Defines the area `A`, which drives the required node count, which drives the entire Phase 1 build list. Decision D-3. |
| **D-04** | Historical order and basket extraction from MagPie for calibration | Data Engineering | 4 weeks | The raw material for gate G1. Confirm at least one clean historical week exists at the required granularity **before** committing to the gate date. |
| **D-05** | Brand campaign calendar feed | Marketing | 4 weeks | Live-commerce events create 10× demand bursts. The twin models them as shocks; without the calendar it will forecast a normal Tuesday. |

---

## 10. Track F — Finance

| ID | Item | Owner | Lead time | Note |
|---|---|---|---|---|
| **F-01** | Phase 0 budget approval | Finance + CTO | 4 weeks | Cost structure in §10.1. Figures (TBC) pending Finance input. |
| **F-02** | **Unit-economics baseline validation** | Finance + Commercial | 6 weeks | The paper's Table IV is explicitly labelled *design targets, not commitments*. Validate AOV, gross margin, rider fee net of consumer delivery fee, and pick labour cost against actual ParagonCorp data before Phase 1 capital is committed. **If break-even is materially above 40–80 orders/day, the node-count plan changes.** |
| **F-03** | Settlement design for store-node fees within the Exagon statement cycle | Finance + Commercial | 6 weeks | Partners must see their fulfillment income in a statement they already understand. Links to L-08 and C-04. |
| **F-04** | Capex vs. opex classification and Phase 1 funding envelope | Finance | 4 weeks | The asset-light thesis means Phase 1 is mostly opex — a materially different approval path than a warehouse build. Confirm early. |

### 10.1 Phase 0 cost structure *(TBC — Finance to populate)*

| Category | Driver | Magnitude |
|---|---|---|
| Engineering headcount | 11 FTE × 4 months, or 6 FTE × 7 months (D-1) | Dominant cost |
| Specialist hires | 2 roles, possibly contract-to-hire (P-03) | Material |
| Cloud & infrastructure | Two-AZ active-active, event bus, lakehouse. Low volume in Phase 0 — this is a Phase 2 cost, not a Phase 0 one. | Low |
| Field devices | Tablets / Android devices for ~25 doors + training units | Low |
| Legal & regulatory advisory | 8 workstreams, some requiring external counsel | Low–moderate |
| Twin compute | Batch simulation, ≥30 replications per scenario | Low |
| **Not in Phase 0** | MFC leases, forward stock, courier fees, store fees — all Phase 1 | — |

---

## 11. Track FAC — Property & Facilities

Phase 1 needs leases signed. Site acquisition takes 3–4 months, so it happens *during* Phase 0.

| ID | Item | Owner | Lead time | Note |
|---|---|---|---|---|
| **FAC-01** | Site selection for 2 dark MFCs + 1 flagship in the pilot cluster | Property + Field Ops | **12–16 weeks** | Three filters from the paper §VI-A: centroid of a demand cell in the twin's solution · motorcycle access to arterials in **all** catchment directions (drive-time, not straight-line) · rent ≤30–40% of equivalent retail frontage. Class-B/C space — second-row shophouses, light-industrial mezzanines. |
| **FAC-02** | Short-lease negotiation strategy | Property + Legal | 6 weeks | **Reversibility is a designed feature of this programme, not an accident.** Every node opening must be undoable. Resist long leases offered at a discount — the discount is not worth the optionality. |
| **FAC-03** | Reference node fit-out specification | Field Ops + Supply Chain | 6 weeks | The layout from the paper's Fig. 3: velocity-slotted shelving with top-50 SKUs within 3 m of the pack bench, pack benches, rider door, inbound door. Specify once, replicate. |

---

## 12. Organisation design

### 12.1 Squad topology (11 engineering FTE)

| Squad | FTE | Owns | Eng-wk |
|---|---|---|---|
| **A — Ledger & Platform** | 3 | T-01 VIS core, T-02 buffer engine, T-03 event bus, T-04 security | 50 |
| **B — Channel & Promise** | 3 | T-05 promise API, T-06 state machine, T-07 direct adapters, T-08 bundles, T-09 cockpit, T-10 ORE | 50 |
| **C — Node & Store** | 3 | T-11 reserved location, T-12 PX app, T-13 accuracy scoring, T-14 POS posting, T-15 pre-matching, T-16 rate shop | 48 |
| **D — Twin & Data** | 2 | T-17 analytical layer, T-18 data contracts, T-19 simulation kernel | 34 |
| | **11** | | **182** |

Plus, outside the 11: **1 Programme Director**, **1 Technical Programme Manager**, and **~1 shared QA/SRE**. Squad A must include at least one engineer with ledger or payments-grade correctness experience — do not staff T-01 with generalists.

### 12.2 Cross-functional working group

Meets fortnightly, chaired by the Programme Director. Standing members: Engineering (4 squad leads), Commercial, Legal, Finance, Field Operations, Regulatory Affairs, Master Data, HR.

### 12.3 Decision rights

| Decision | Decides | Consulted |
|---|---|---|
| Node opens / does not open | Programme Director on twin recommendation | Finance, Field Ops |
| Twin version certified for decision use | Head of Data/R&D | Programme Director |
| Store door activated / demoted | Field Ops Lead on accuracy score | Commercial |
| Buffer policy (oversell risk appetite) | Head of Commercial | Platform Eng, Finance |
| Promise degraded during an incident | Ops on-call, per PR-03 | — |
| Phase gate passed | Steering committee | All track owners |

---

## 13. Month-by-month milestone map

Assumes decision **D-1 = 11 FTE**. At 6 FTE, extend the technical column by ~3 months; the non-technical columns are unchanged because they are calendar-bound, not headcount-bound.

| | Technical | Commercial & Legal | People & Process |
|---|---|---|---|
| **Month 1** | Event bus live · data capture recording *(T-18)* · pre-matching shipped *(T-15)* · analytical twin usable *(T-17)* | **Marketplace enrolment initiated *(C-01)*** · consignment addendum drafting *(L-01)* · PDP and BPOM reviews opened | Headcount decided *(P-01)* · specialist recruitment opened *(P-03)* · Field Ops Lead search opened |
| **Month 2** | VIS core in integration · ORE filter + decision log · order state machine · POS posting integration at 3 pilot doors | Grab/GoSend terms in negotiation · addendum in counsel review · employment-exposure opinion *(L-02)* | Squad topology published · store training curriculum drafted · node-approval workflow drafted *(PR-01)* |
| **Month 3** | Promise API meeting 50 ms · PX store app in field trial · buffer engine tuning on real posting-latency data · simulation kernel running | Addendum approved · door recruitment against twin ranking *(C-03)* · fee structure modelled *(C-04)* | Store staff trained at 3 doors · oversell runbook rehearsed · cycle-count SOP agreed |
| **Month 4** | **G2 stress test** · **G1 trace replay + holdout** · cockpit live | **15 doors contracted** · marketplace confirmation · site shortlist for Phase 1 leases | **G5 governance live** · Phase 1 team confirmed · gate pack assembled |

---

## 14. Decisions required, with deadlines

| ID | Decision | Needed by | Consequence of delay |
|---|---|---|---|
| **D-1** | **Phase 0 engineering headcount: 11 FTE / 4 months, or 6 FTE / 7 months** | **Week 1** | Every downstream date is unknowable until this is answered. Delaying the decision delays the programme one-for-one. |
| **D-2** | Which marketplace leads — Shopee (~63% of platform beauty GMV, the volume answer) or TikTok Shop/Tokopedia | Week 2 | C-01's 3–6 month clock does not start until this is chosen. This is the second-most schedule-critical decision. |
| **D-3** | Pilot cluster boundary within South Jakarta | Week 6 | Sets the area, therefore the node count, therefore the entire Phase 1 build and budget. |
| **D-4** | Store-node per-order fee level | Week 10 | Sits inside the routing cost function. Too high and the router avoids the store estate the strategy rests on. |
| **D-5** | Oversell risk appetite (the buffer setting) | Week 12 | A commercial trade-off between oversell probability and usable shelf space. Engineering must not choose this silently. |
| **D-6** | Own-fleet: confirm exclusion for Phase 0–2 | Week 4 | Cheap to confirm, expensive to leave ambiguous. The reversal trigger is measured, not debated: sustained >35–45 orders/day per rider-equivalent at ≥70% utilisation. |

---

## 15. Phase 0 risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Engineering staffed below 11 FTE while the 4-month date is held** | **High** | **High** | Re-baseline the calendar, do not cut scope — every Phase 0 item is a gate item or an irreversible one. Decide D-1 in week 1 and publish the resulting date honestly. |
| Marketplace enrolment exceeds 6 months | Medium | High | Sequence brand.com and WhatsApp first *(T-07)* so Phase 1 can pilot on our own channels if a platform slips. This is why direct channels are in Phase 0 rather than Phase 1. |
| Specialist hires (simulation, optimisation) not filled | Medium | High | Contract-to-hire or academic partnership as a bridge. G1 depends on this capability existing. |
| Master data (dimensions, bundle BOM) worse than assumed | **Medium-High** | Medium | Audit in month 1 *(D-01)*, not month 3. This is a routine surprise, not an exotic one. |
| Consignment addendum negotiated door-by-door | Medium | High | Template-first discipline. Escalate any door demanding bespoke terms rather than accommodating it. |
| Employment-relationship exposure at store nodes *(L-02)* | Low-Medium | **High** | Counsel opinion before doors are signed, not after. Structure the fee and the app's instruction model around the opinion. |
| Historical data insufficient for twin calibration | Low-Medium | High | Verify one clean week exists *(D-04)* in month 1. If it does not, G1's date moves — better to know in week 4 than week 16. |
| Internal resistance from B2B / DC organisation | Medium | Medium | P-07 change plan, led visibly by leadership, before the programme is inferred as a threat. |

---

## 16. Gate review pack

Assembled continuously through Phase 0, presented at the exit review. Each item has a named owner from §3.

1. **Twin certification report** — trace-replay deviation per KPI, holdout forecast scoring, certified version identifier *(G1)*
2. **Inventory correctness test report** — 72-hour degraded-latency stress test, oversell count, AZ-failure resilience result *(G2)*
3. **Commercial pack** — marketplace confirmation, signed courier terms, counsel-approved addendum template *(G3)*
4. **Field readiness pack** — ranked door list with twin marginal-coverage scores, contracted doors, training completion, PX app field-trial results *(G4)*
5. **Governance pack** — node-approval workflow, rehearsed oversell runbook, agreed dispute process *(G5)*
6. **Legal & regulatory register** — status of all eight L-items with residual risks named
7. **Phase 1 plan and budget** — node list, assortments, staffing, funding envelope, with the twin's forecast and confidence intervals
8. **Re-baselined estimates** — actual velocity against the 182 eng-wk estimate, and a corrected Phase 1–2 forecast

**The honest question for the exit review is not "did we build it?" but "does the twin tell us the truth, and can a shop assistant pick an order in seven minutes?"** Everything else in Phase 0 exists to make those two things answerable.

---

*Traceability: technical items map to ROADMAP workstream IDs (W-numbers) and thence to the theorems and propositions in `paraexpress.tex`. Legal and regulatory items are backlog items for counsel and regulatory affairs to own — they state exposures to be resolved, not positions to be relied upon.*
