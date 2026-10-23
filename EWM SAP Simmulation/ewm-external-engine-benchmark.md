# External Picking Engine vs. Internal EWM Limits: WOCR and WPT Benchmark

Benchmark of `Requirements/external-picking-engine-requirements.tex` (draft v0.2) against SAP EWM documentation and community material. It checks the consultant's concern that **WOCR** (warehouse order creation rule) and **WPT** (warehouse process type) may limit what `createWOWT` can do.

> **Evidence labels.** **[DOC]** = SAP Help / SAP Learning. **[KBA]** = SAP Knowledge Base Article. **[COMM]** = SAP Community Q&A or blog (not authoritative). **[GAP]** = I found no source, so it must be tested in a sandbox. Nothing here was tested in a live system. Customizing names vary by release.

---

## 1. Verdict

| Consultant's concern | Verdict | Why |
|---|---|---|
| WOCR is an internal limit | **Confirmed, and it is the bigger risk** | EWM always groups WTs into WOs through WOCR rules. The documentation describes no way for an outside system to dictate the grouping or the in-WO sequence. The requirements note assumes it can. |
| WPT limits the ability to create WO/WT | **Partly confirmed** | The WPT does not cap how many WTs or WOs you can create. But it decides *which WOCR and which activity area* apply, and several WPT flags can block or alter externally supplied tasks. |
| Fixed-source WT creation (`sourceBin`, `sourceHU`, `quantId`) | **Not supported by a released API (new finding)** | A KBA reports the cloud warehouse order API overriding a supplied HU with its own FIFO choice. On-premise function modules exist but are mostly unreleased. |

**Bottom line.** The v0.2 note treats `createWOWT` as "write my plan, EWM obeys". Standard EWM does not work that way. At best EWM accepts the **WT layer** (what to pick, from where). The **WO layer** (grouping, queue, sequence) is re-derived by WOCR unless Customizing is shaped to reproduce it, or custom code intervenes.

---

## 2. How standard EWM builds WTs and WOs

1. Stock removal (search sequence plus removal rule) creates WTs from the delivery request.
2. WTs are grouped by **activity area**. The area comes from the source bin for picking and the destination bin for putaway, as set by the WPT's "WOCR Activity Area" field. [DOC: [Creating Warehouse Orders](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/creating-warehouse-orders), [SAP Press: WPT fields](https://blog.sap-press.com/warehouse-process-type-fields-and-attributes-in-sap-s4hana-ewm)]
3. EWM applies WOCRs in a **search sequence** per activity area (and activity). A rule can also be set directly on the WPT. Tasks that fail that rule fall back to `DEF`. [DOC: [SAP Help WO creation](https://help.sap.com/doc/saphelp_ewm700_ehp02/7.0.2/en-US/48/890776d2b21b5ae10000000a42189c/content.htm), [SAP Press](https://blog.sap-press.com/warehouse-process-type-fields-and-attributes-in-sap-s4hana-ewm)]
4. Each rule uses item filters, subtotal filters and **limits** (number of items, weight, volume, consolidation groups). When a limit is hit, the order closes and a new one opens. [DOC]
5. "No warehouse tasks must be left over". A remainder rule (`UNDE`) groups any leftover WTs by activity area, queue and consolidation group. [DOC]
6. WOs are created when the wave is released. A wave can create them locked, and users can unlock them. [DOC]

---

## 3. WOCR: requirement-by-requirement benchmark

| Requirement in the `.tex` | Standard EWM behavior | Gap | Evidence |
|---|---|---|---|
| `createWOWT` "replaces WOCR for these items" (Sec. 2, Table 1) | WO creation is a standard step and I found no switch that bypasses it. The most you can do is pin a dedicated WOCR on the WPT. | **High** | [DOC] describes no external grouping. [GAP] on any bypass. |
| `woRef`: the PDE decides which WTs share a WO | The WOCR decides: category, filters, limits, sort. The PDE grouping survives only if the rule happens to reproduce it. | **High** | [DOC] |
| One WO may span several activity areas (path through all bins) | Tasks are grouped **by activity area first**. A rule works inside one area, and `DEF` requires the same activity area, queue and request/CG. A WO that crosses areas looks unsupported. | **High** | [DOC], [COMM: WOCR blog](https://answers.sap.com/t5/supply-chain-management-blogs-by-members/sap-ewm-wocr-determination-based-on-activity-area/ba-p/13575056) |
| `seqNo` / shortest-walk order inside the WO | The order comes from the WOCR **WO sort rule**, which has at most **15 sort fields**. An external sequence number is not a standard sort field. | **High** | [DOC] (the 15-field limit is in [Creating Warehouse Orders](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/creating-warehouse-orders)). Whether a custom field can feed the sort is [GAP]. |
| `queue`, `resourceType` set per WO by the PDE | The queue is a WT attribute, and the standard grouping separates by queue. I believe it is derived from queue determination Customizing at WT creation. The doc does not say an API can force it. | **Medium** | [DOC] (grouping by queue). Derivation from Customizing is my understanding: **verify**. |
| `consolidationGroup` on the WO | CG belongs to the delivery item. It is a WOCR creation category and limit, not a free WO attribute. | **Medium** | [DOC] |
| WO limits per activity area (WTs, weight, volume) as PDE inputs | These live in the WOCR, so the PDE should read them (as the note says). Note that `DEF` has **no limits** and MFS rules cap at 1 WT per WO. | **Low** (design is consistent) | [DOC] |
| Full-pallet HU tasks in a forklift WO | Needs a dedicated WOCR or queue selected through the WPT or activity area. Feasible in Customizing. | **Low** | [DOC] |
| Atomic "all-or-nothing per WO" (NFR table) | WT creation and WO creation are separate steps. Whether one call can roll back a whole WO, including WOs closed by limits, is not documented. | **Medium** | [GAP] |
| `plannedDistance` / `plannedDuration` stored on the WO | No documented standard fields. The WO has a "preparation time" in the WOCR only. | **Low** (drop or keep in the PDE) | [DOC] |

**Likely failure mode.** The PDE sends one 12-WT forklift WO. EWM groups the WTs by activity area and applies the WOCR limits, which may split the WO or reorder its tasks. `STOCK_CHANGED` and the other documented reject codes would never fire, because the damage happens silently at grouping time.

---

## 4. WPT: where it can limit `createWOWT`

The WPT does not cap the number of WTs or WOs. The fields below are the ones that matter for an external creator. The field names are from [SAP Press: WPT fields](https://blog.sap-press.com/warehouse-process-type-fields-and-attributes-in-sap-s4hana-ewm) [COMM, quoting the Customizing screen].

| WPT field | Effect | Impact on the PDE | Check |
|---|---|---|---|
| **WO Rule** | WOCR applied to tasks of this WPT. Tasks failing it go to `DEF`. | Primary lever for steering grouping. Needs a **dedicated WPT per WO shape** (for example FULL_HU vs PICK). | Is `.tex` `processType` one value or one per `woType`? |
| **WOCR Activity Area** | Source area for picking, destination for putaway. | Decides which area-level rule sequence is searched. A wrong setting sends all tasks to the wrong rules. | Set to *source* for outbound pick. |
| **Activity** (via process category) | Combined with the area to find the rule sequence. | Several WPTs can share one activity. | Confirm mapping. |
| **Manual WT Forbidden** | The system "does not allow the manual creation of warehouse tasks". | **Possible blocker.** Whether it also blocks API or function-module WT creation is [GAP]. | Test in sandbox. |
| **Source Stor.Ty / Source Bin** | Fixes the source for stock removal. | Conflicts with a PDE-chosen `sourceBin` if set. Leave blank for picking. | Inspect WPT. |
| **Completely Pick WR** | Pick tasks are created only if the whole request can be fulfilled. | Blocks partial coverage when a layer runs short (open point in Sec. 12 of the `.tex`). | Check flag. |
| **Round Whole Units** | Rounds the WT quantity. | May alter PDE quantities such as 3 IBX vs 30 PC. | Check flag. |
| **Confirm Immediately / Propose Confirmation** | Auto-confirms when the WT is created. | Breaks the "WT confirmed" event and the shadow-mode comparison. | Must be off for picking. |
| **Priority** | Affects the order of WTs inside a WO. | Competes with the PDE sequence. | Check. |
| **Pick Denial Ctrl** | Controls pick denial behavior. | Affects how rejects and re-plans behave. | Check. |
| **Rough Bin Determination** | Source bins from the removal strategy, used for waves. | Relevant to the 2-step wave scenario. | Check. |

**Interpretation.** The consultant is most likely right on two points. (a) The WPT is the hook into WOCR, so a single generic WPT makes every PDE-created task share one rule sequence. (b) A WPT flag such as Manual WT Forbidden, Completely Pick WR or Confirm Immediately can silently change or reject tasks created from outside. Neither is a numeric cap, so describing it as "WPT limits the ability to create WOWT" is only half accurate.

---

## 5. Fixed-source WT creation (the `createWOWT` write path)

| Option | Finding | Evidence |
|---|---|---|
| Cloud warehouse order API | A KBA reports that when a WT is created through the warehouse order API for an outbound delivery, the system can **assign a different HU by FIFO even when HU and bin are supplied**. WTs are not created against outbound delivery orders through this API. | [KBA 3778521](https://userapps.support.sap.com/sap/support/knowledge/en/3778521) [KBA, preview only; read the full text in the portal] |
| Cloud events | The `Warehouse/Task/Created` event is not triggered unless the task is created in Open status. The `TaskActivated` event (CE2502) is the workaround. | [KBA 3584400](https://userapps.support.sap.com/sap/support/knowledge/en/3584400) [KBA preview; I could not confirm this article's content, so treat it as unverified] |
| Cloud read APIs | The 2022 release notes describe a Warehouse Order and Task API for **reading** (expanded fields). The Handling Unit API can create empty HUs. | [SAP blog 2202](https://blogs.sap.com/2022/02/16/sap-warehouse-management-in-sap-s-4hana-cloud-2202-whats-new/) [COMM] |
| On-premise `/SCWM/TO_CREATE` | Usable (pass a table, set `WTCODE`, call `/SCWM/TO_POST`) but **not released** from 1909. A thread says there is no BAPI except the cloud WT API. | [COMM](https://community.sap.com/t5/supply-chain-management-q-a/fm-scwm-to-create-move-hu/qaq-p/12535972) |
| `/SCWM/TO_CREATE_MOVE_HU`, `/SCWM/TO_CREA_HU_INT` | Candidate function modules for whole-HU and multi-item WTs. Their pick usage is **not documented**. Developers are told to copy standard usage from where-used lists. | [COMM] (same thread) |
| Mixed-batch HU | Picking WTs need the destination HU set to the source HU and the destination bin set to the source bin, via a custom step. KBA 2698615 reports NLENR blank on full-HU pick WTs with several batches. | [COMM](https://community.sap.com/t5/supply-chain-management-q-a/ewm-stock-removal-mix-product-picking/qaq-p/631491), [KBA 2698615](https://userapps.support.sap.com/sap/support/knowledge/en/2698615) |
| BAdI in stock removal | Existing note (section 2.3): the system does not search for the best fitting quant. Optimized picking needs a BAdI. | existing `ewm-wocr-and-picking-strategy.md` [DOC] |

**Consequence.** For PAL (full HU) and CAR (partial) layers, the engine should probably influence *which quant EWM selects* (BAdI in stock removal, or pre-set inputs) rather than push a finished WT. The BAdI route keeps EWM-native WTs, WOCR, confirmation and events, and removes the need for an unreleased API.

---

## 6. Corrections to the `.tex` note

1. **Sec. 2 / Table 1 "replacing WOCR".** Reword to "influencing or constraining WOCR". Add that WO grouping is a Customizing result unless proven otherwise.
2. **Sec. 7 (`createWOWT`).** Split the contract into a WT layer (feasible) and a WO layer (hint only). Mark `woRef`, `queue`, `seqNo`, `plannedDistance` and `plannedDuration` as hints until the sandbox test passes.
3. **Atomicity claim (NFR).** Remove "all-or-nothing per WO" until verified.
4. **Cross-activity-area WOs.** Add a design constraint: one WO is one activity area. Either reshape the areas, or accept per-area WOs.
5. **`processType` (marked *verify*).** Make it a list: one WPT per WO shape, each pointing to its own WOCR.
6. **Table 9 (Cloud vs on-prem).** Add the KBA 3778521 finding for the cloud API. Say "supports read, fixed-source create unconfirmed" instead of "check that creation with a fixed source is supported".
7. **Open points.** Add: does Manual WT Forbidden block API creation, and can the WOCR sort use a custom field?
8. **Risks.** Add "WOCR regroups PDE orders" as a top-3 risk, ahead of the layout-graph drift.

---

## 7. Sandbox test plan (needs consultant access)

| # | Test | Pass condition | Decides |
|---|---|---|---|
| T1 | Create a WT with fixed bin, batch and HU through the intended path (function module, or cloud API) for an outbound pick. | EWM takes the exact source. No FIFO override. | Fixed-source path vs BAdI route |
| T2 | Same call on a WPT with **Manual WT Forbidden** on and off. | State whether the flag blocks it. | WPT blocker |
| T3 | Create 12 WTs in one activity area under a dedicated WPT plus WOCR with large limits. | One WO with 12 WTs. | WO grouping feasible |
| T4 | Repeat T3 with WTs in two activity areas. | Expect two WOs. | Confirms the activity-area limit |
| T5 | Vary the WOCR maximum WTs, weight and volume. | The WO splits at the limit. | Confirms limits override the PDE grouping |
| T6 | Try a custom sort field (or the standard pick path) for the WO sort. | The sequence follows the intended path. | Sequencing feasibility |
| T7 | Create a WT with Confirm Immediately on and off. | State the effect on the confirmation feed. | WPT impact |
| T8 | Stock changes between read and write. | Confirm which reject EWM raises. | Validity of the reject codes |
| T9 | Time a 500-item wave. | Compare against the 10 s target. | NFR latency |

---

## 8. Recommended direction

1. **Stage the scope.** First phase: the PDE decides **which quant and UoM** (WT layer) through the stock removal BAdI or a verified creation path. WOCR keeps grouping, tuned per WPT. Second phase: the PDE influences WO grouping only if T3 to T6 pass.
2. **Customizing first.** Dedicated WPT plus WOCR for FULL_HU (forklift) and PICK. Align activity areas with the layout graph so PDE paths match the grouping area.
3. **Shadow mode stays.** Compare the PDE plan with what EWM actually grouped and sequenced. That gap measures the WOCR limit directly.
4. **Open the consultant discussion with two questions.** Is a custom WOCR sort field or a BAdI in WO creation allowed on this system? Which deployment model is it (cloud, embedded or decentralized)?

---

## 9. Source quality and unknowns

- **Not found:** an official SAP statement on external WO grouping, on the exact WO API entity and payload, or on whether Manual WT Forbidden applies to APIs. Confirm in the SAP Business Accelerator Hub and in the system.
- **Weak sources:** KBA pages returned only previews. The SAP Community answers contradict each other on whether an activity area is required. A Scribd interview-prep document was ignored.
- **The `.tex` note's own claim** (SAP Note 3093108, released APIs are cloud only) was not re-verified here.

## Sources

- [SAP Learning: Creating Warehouse Orders](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/creating-warehouse-orders)
- [SAP Help: Warehouse Order Creation (EWM 7.0 EhP2)](https://help.sap.com/doc/saphelp_ewm700_ehp02/7.0.2/en-US/48/890776d2b21b5ae10000000a42189c/content.htm)
- [SAP Press: WPT fields and attributes in SAP S/4HANA EWM](https://blog.sap-press.com/warehouse-process-type-fields-and-attributes-in-sap-s4hana-ewm)
- [SAP Community: WOCR determination based on activity area](https://answers.sap.com/t5/supply-chain-management-blogs-by-members/sap-ewm-wocr-determination-based-on-activity-area/ba-p/13575056) (page returned 403 to my fetch; used only through search snippets)
- [SAP Community: FM /SCWM/TO_CREATE_MOVE_HU](https://community.sap.com/t5/supply-chain-management-q-a/fm-scwm-to-create-move-hu/qaq-p/12535972)
- [SAP Community: EWM stock removal mix product picking](https://community.sap.com/t5/supply-chain-management-q-a/ewm-stock-removal-mix-product-picking/qaq-p/631491)
- [SAP KBA 3778521](https://userapps.support.sap.com/sap/support/knowledge/en/3778521), [KBA 3584400](https://userapps.support.sap.com/sap/support/knowledge/en/3584400), [KBA 2698615](https://userapps.support.sap.com/sap/support/knowledge/en/2698615)
- [SAP blog: Warehouse Management in S/4HANA Cloud 2202](https://blogs.sap.com/2022/02/16/sap-warehouse-management-in-sap-s-4hana-cloud-2202-whats-new/)
- Internal: `ewm-wocr-and-picking-strategy.md`, `Requirements/external-picking-engine-requirements.tex`
