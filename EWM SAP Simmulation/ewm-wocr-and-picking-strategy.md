# SAP EWM – Picking Strategy & Warehouse Order Creation Rule (WOCR)

Reference note for the logistics team. It explains how standard SAP EWM decides **where to pick from** (stock removal) and **how picks are grouped into picking lists** (WOCR). It is a companion to `ewm-wocr-animation.html`.

> Status: compiled from SAP Learning course material and SAP Help/Community pages. Customizing paths and field names vary by release. Verify them in your S/4HANA EWM system before configuring anything. Items marked **(verify)** are weaker sources.

---

## 1. The big picture

```
Outbound Delivery Order (DO)
        │  item: SKU, qty (base UoM)
        ▼
┌──────────────────────────────┐
│ A. STOCK REMOVAL (picking     │  decides WHICH quant / bin / batch / UoM to pick from
│    strategy)                  │  → output: Warehouse Tasks (WT)
└──────────────────────────────┘
        ▼
┌──────────────────────────────┐
│ B. WOCR                       │  decides HOW the WTs are grouped into picking lists
│    (Warehouse Order Creation) │  → output: Warehouse Orders (WO)
└──────────────────────────────┘
        ▼
   Picking list per worker / resource
```

- **Stock removal** answers: *which stock do we take?* It uses SKU, bin, batch, stock type and the UoM the stock is stored in.
- **WOCR** answers: *which tasks go on the same picking list?* It uses activity area, consolidation group, weight/volume/count limits and sorting.

The two are independent. Stock removal creates the WTs first. WOCR then groups the WTs that already exist.

---

## 2. Part A – Stock removal (picking strategy)

### 2.1 Determination flow

1. **Inputs**: the outbound delivery order, the warehouse product master, and the hazardous material master. The only mandatory input is the warehouse number. Other inputs include:
   - stock removal control indicator (from the warehouse product master)
   - warehouse process type
   - 2-step picking flag
   - **quantity classification** (derived from the packaging specification **or the alternative UoM**)
   - stock type group, and sales-order or project stock
2. **Storage type search sequence**: an ordered list of storage types to search (for example: fixed pick bin → carton rack → pallet reserve). The system checks them one at a time and stops when enough stock is found. The sequence can also hold **storage type groups**, which pool quants from several storage types.
3. **Stock removal rule**: sorts the quants inside the storage type (or group) so the system knows which one to take first. A rule can be assigned directly to a storage type, and that overrides the rule found through the search sequence.
4. **Warehouse tasks** are created from the selected source bins.

Customizing path (verify): *Extended Warehouse Management → Goods Issue Process → Strategies* → *Specify Storage Type Search Sequence* / *Specify Stock Removal Rule*.

### 2.2 The stock removal rule = a sort

A stock removal rule is a sort of available quants (table `/SCWM/AQUA`), with **up to 30 sort fields**, each ascending or descending. Only *fixed bin* exists as a built-in switch (a storage type flag). Every other strategy below is built by **choosing sort fields**, and they can be combined freely.

Useful sort fields:

| Field | Meaning |
|---|---|
| `WDATU` / `WDATU_DATE` | Goods receipt date (and time) → FIFO / LIFO |
| Shelf-life expiration date | Expiry → FEFO-style removal |
| Quantity | Smallest or largest quant first → partial vs. full units |
| Preferred UoM | Quants *not* in the preferred UoM first |
| `EMPTY_FIXBIN` | Empty fixed bin indicator |
| `PICK_ITM` | Open removal items per bin (spreads pickers across bins) |
| `SPICK_QTY` / `PICK_QT` | Open removal quantity per bin |
| `AISLE_ITM` | Open items per aisle/level (MFS only) |
| `SCORE`, `STOCK_POS` | Stock-determination score; positive stock only |

### 2.3 Standard strategies

| # | Strategy | How it works | Driven by |
|---|---|---|---|
| 1 | **FIFO** | Oldest goods receipt date first | GR date |
| 2 | **Stringent FIFO** | FIFO across several storage types, using a storage type group | GR date + storage type group |
| 3 | **LIFO** | Newest goods receipt first, for example for stacked stock | GR date (descending) |
| 4 | **Shelf-life expiration** | Shortest remaining shelf life first | Expiry date (and batch if shelf life is batch-managed) |
| 5 | **Partial quantities first** | Takes full units when the request is a full unit, and opened or partial units when it is a partial quantity, to keep broken pallets to a minimum | Quantity classification + two rules (qty ascending / qty descending) + GR date |
| 6 | **By quantity** | Chooses the *storage type* by requested qty, for example cartons from rack A and full pallets from rack B | Quantity classification → different **search sequences** |
| 7 | **Fixed bin** | Picks from the fixed bin(s) in the warehouse product master. Pair it with `PICK_ITM` so pickers don't queue at one bin, and with replenishment so the bin isn't empty | Storage type flag + product master |
| 8 | **Preferred UoM last** | Proposes quants *without* the preferred UoM first, to protect the preferred pack for matching orders | Stock-specific UoM (SUoM) + preferred UoM |

Partial-quantity example from the course (standard pallet = 100 pcs):

| Request | Result |
|---|---|
| 100 | Oldest full pallet |
| 50 | From the oldest full pallet, which becomes "opened" |
| 60 | Opened pallet gives 50, then 10 come from the oldest full pallet |

The system does not search for the best-fitting quant (optimized picking). That needs a BAdI.

---

## 3. Mapping inventory attributes to strategy

| Inventory information | How EWM uses it | Where it is configured |
|---|---|---|
| **SKU / warehouse product** | Stock removal control indicator, fixed bin(s), preferred UoM, packaging specification, shelf-life data | Warehouse product master |
| **Bin / storage type / section** | Search sequence order, storage type groups (for stringent FIFO/LIFO), fixed-bin flag, negative-stock allowance, rounding | Storage type & search sequence Customizing |
| **Batch** | If the delivery item already has a batch, only that batch is picked. If not, batch determination uses selection criteria from the ERP side, which cannot be changed in EWM **(verify; community Q&A)**. Shelf-life or batch sort fields then decide the order | ERP batch determination + removal rule |
| **UoM the stock is stored in** | Quantity classification (from the packaging specification or the **alternative UoM**) selects the search sequence or rule. Stock-specific UoM (SUoM) is set at goods receipt, and the *preferred UoM last* rule compares it with the product's preferred UoM. Rounding to the operative UoM is a storage type setting **(verify)** | Packaging spec / alt UoM, storage type, sort field |
| **GR date** | FIFO / LIFO sort | Removal rule sort field |
| **Quantity per quant** | Partial vs. full unit selection | Removal rule sort field |

### Applied to the diagram example (DO PM#124)

| DO item | Request | Stock removal outcome |
|---|---|---|
| SKU A | 2 PC | One WT from the pick bin or loose-piece storage type |
| SKU B | 30 PC | Alt UoM (1 IBX = 10 PC) gives quantity classification "inner box" → 3 IBX from the IBX-holding storage type (WT2) |
| SKU C | 50 PC | 1 CAR = 20 PC → 2 CAR from the carton/pallet storage type (WT3) + 10 PC from loose stock (WT4). This is a partial-quantity / by-quantity result |
| SKU D | 10 PC | 1 IBX = 10 PC → 1 IBX (WT5) |

Each WT carries product, quantity in the **picked UoM**, source bin and batch (for example `B: JH23A`). Both SKU C tasks come from the same batch.

---

## 4. Part B – WOCR (grouping WTs into picking lists)

### 4.1 How the rule is found

1. The **activity area** comes from the source (or destination) bin of the WT, depending on the warehouse process type.
2. The **activity** comes from the warehouse process type.
3. Each activity area (or area + activity) has a **search sequence of WOCRs**. EWM works through them in order. A WOCR can also be set directly on the warehouse process type.
4. Fallback rules:
   - `UNDE`: takes WTs left over after all customer WOCRs have run.
   - `DEF`: used when no WOCR is assigned. It has no limits, but all WTs in a WO must share the same activity area, queue, and warehouse request or consolidation group.
   - `MFS`: for MFS-controlled storage types. Its default limit is one WT.

### 4.2 What a WOCR contains

| Setting | Purpose |
|---|---|
| **Creation category** | Grouping logic: consolidation group, pick path, pick-pack-pass, load/unload, physical inventory |
| **Item filter** | Tests each WT, for example min/max weight, volume, processing time, route. A WT that fails is skipped |
| **Subtotal filter** | Tests running totals per consolidation group |
| **Limits** | Max or min number of items or weight per WO (for example "max 50 WTs"). Maximums are checked first. If a minimum isn't met, the WTs move to the next WOCR |
| **Inbound sorting** | Sorts WTs at the start of WO creation |
| **WO sorting** | Sorts WTs inside the finished WO (for example by pick path) |
| **Packing profile (pick HUs)** | Simple or complex algorithm, or BAdI. Options to split a WT if it doesn't fit an HU, and to check length/width/height |
| **Shipping pack profile** | Determines shipping HUs |
| **Preparation time** | Time a worker needs to prepare the WO |
| **Destination storage / work center** | Destination type, section and bin, or work center determination |
| **Storage process** | Process-oriented storage control for outbound |

Sort rules: up to 15 predefined fields, ascending or descending.

Customizing path (verify): *Extended Warehouse Management → Cross-Process Settings → Warehouse Task → Define Warehouse Order Creation Rules*.

### 4.3 What this means for WO1 / WO2

Unit of measure is **not** a standard WOCR split criterion. In the diagram, WO1 = {WT1, WT4} and WO2 = {WT2, WT3, WT5} could come from:

- **Activity area**: WT1 and WT4 are picked in one area (for example the loose-piece zone), the others in another. This is the most natural fit. (Area follows the *source bin*, and the bin is where the UoM happens to be stored.)
- **Limits**: a max WT, weight or volume per WO reached part-way through the list.
- **Consolidation group**, **route**, or **pick path** sorting.

Confirm which one applies to your warehouse in the WOCR search sequence for each activity area.

---

## 5. Putting it together

| Question | Mechanism |
|---|---|
| Which bin and batch do we take stock from? | Search sequence → stock removal rule |
| Full pallet, carton or loose piece? | Quantity classification (packaging spec / alt UoM) + partial-quantity or by-quantity strategy |
| Oldest or shortest-expiry first? | FIFO / LIFO / shelf-life sort fields |
| Keep pickers from crowding one bin? | Fixed bin + `PICK_ITM` / `SPICK_QTY` |
| Which tasks share one picking list? | WOCR (activity area, consolidation group, limits, filters) |
| What order does the picker walk? | WOCR WO sorting |

## 6. Open questions to confirm in the system

- [ ] Search sequences and storage types configured per warehouse process type
- [ ] Stock removal rules in use (and their sort fields)
- [ ] Whether alternative UoM or packaging specifications drive the quantity classification
- [ ] Whether SUoM (stock-specific UoM) is active
- [ ] WOCR search sequence per activity area, and the limits/filters set on each
- [ ] Batch determination: ERP-side or EWM-side

---

## 7. Part C – Packing and consolidation groups

Packing happens **after** picking. It decides which goods go into the same shipping handling unit (HU), for example a pallet.

- Every outbound delivery item carries a **consolidation group (CG)**. The CG decides which items may be picked or packed together into one HU.
- CG rules are maintained in Customizing (transaction `/SCWM/DSGR`, **verify** in your release). The simplest rule is 1:1 (one CG per delivery).
- Rules can combine deliveries, for example items for the **same customer** into one HU. The sources do not show ship-to as a default criterion, so keying the CG on ship-to is a **configuration decision**.
- Items with the **same CG** may share an HU. Items with **different CGs** may not.
- Packing happens at a **packing work center**. One documented setup routes all items of a CG to the same work center (a putaway rule on the packing storage type, rule "Consolidation Group"), so that they end up in one shipping HU.
- A WOCR can also create **pick HUs** during picking (packing profile). Then the pick HU is already the shipping HU (see pick-pack-pass).
- A wave is not a CG: the wave is a **release / picking** tool, the CG is a **packing / staging** tool.

Known pitfalls (from community sources, **verify**):
- SAP KBA 3058611 describes products with different CGs ending up in one HU, so check that the CG check is enforced in your packing setup.
- Packing HUs of **several deliveries** into one transport HU is not a clearly documented standard flow. Validate with your functional design before committing.

Example used in the simulation (scenario 2): PM#124 and PM#125 are both for Store 17 (CG-ST17), PM#126 is for Store 22 (CG-ST22). Result: HU-1 holds PM#124 + PM#125, HU-2 holds PM#126.

## 8. Other picking scenarios (simulation tabs)

| # | Scenario | What changes | EWM building blocks |
|---|---|---|---|
| 1 | **Single delivery** | One DO, WOs split by activity area, pickers work in parallel, one pallet | Stock removal, WOCR by activity area, packing |
| 2 | **Same ship-to → one pallet** | Several DOs with the same CG are packed together | Consolidation group, pack station, shipping HU |
| 3 | **Batch picking (two-step)** | Total quantity of a wave is withdrawn once, then split per delivery in staging | Two-step picking: withdrawal WT (default warehouse process type 2020) + allocation WTs, wave |
| 4 | **Batch-managed stock (FEFO)** | Min. remaining shelf life excludes a batch, one item splits into two WTs (two batches) | Batch determination, shelf-life sort field, FEFO |
| 5 | **Pick-pack-pass** | Pickers work one after the other in their own zone, the same pick HU passes through the zones | WOCR category pick-pack-pass, pass point, pick HU |
| 6 | **Layered removal** | Order split by alt UoM; per layer: full-UoM bins only → expiry → storage type priority → GR date | Quantity classification, search sequence per layer, storage type group, removal rule sort fields |
| 7 | **Wave, layered removal** | 4 deliveries, 3 SKUs run the layered logic in sequence on the remaining stock; full-pallet HU WTs go to a forklift WO and straight to the door | Same as 6 + WOCR for HU WTs, consolidation groups |

Notes:
- "Batch picking" is used in two senses. Scenario 3 is the multi-order sense (picking several orders at once). Scenario 4 is the batch/lot-managed stock sense.
- Two-step picking is relevant when many deliveries need the same products. It reduces trips to the racks, but adds an allocation step. EWM decides per product whether it is two-step relevant, and the wave can override it.
- Cluster picking (several orders on one cart at once) is **not** shown, because the sources I found did not describe it as a named EWM feature.
- Other candidates not yet simulated: full-pallet picking from reserve, replenishment of a fixed pick bin, and wave-based release.

---

## 9. Warehouse structure (storage type, section, bin)

| Level | SAP EWM definition | Example in the simulation |
|---|---|---|
| **Warehouse number** | Highest organizational unit in warehouse management, usually one building or DC (4 characters) | WH01 |
| **Storage type** | Physical or logical subdivision of a warehouse complex (4 characters). Its role and settings control putaway, stock removal and stock movements | 0010 Shelving (aisles 01–03), 0020 Carton rack (04–05), 0030 Pallet rack (06–08), 0040 Bulk storage (09), 9010 GI staging, 9020 GR zone, 9030 Pack station |
| **Storage section** | Organizational subdivision of a storage type. Groups bins with similar attributes (fast movers, heavy goods…), used by putaway | 0001 fast movers (half nearer the docks), 0002 slow movers |
| **Storage bin** | Smallest addressable unit of space, the exact position of a product. Coordinates up to 18 characters, e.g. aisle–stack–level | 04-R5 = aisle 04, side R, bay 5 |
| **Bin type** | Bin attribute for relative size or actual dimensions | S1 shelf, C1 carton, P1 pallet slot, B1 block lane |
| **Quant** | Quantity of one product in one bin, resource or TU | Each stock row |
| **Activity area** | Logical group of bins, can span storage types; drives e.g. WOCR | PCK-P, PCK-R |

Typical storage type rules: storage type role; putaway with storage section check and bin type check; capacity / mixed storage; stock removal via search sequence and removal rule (a rule set directly on the storage type overrides the search sequence's rule); storage type groups for one sort across several types; full stock removal (HU WT) in pallet storage **(verify)**.

## 10. Layered stock removal (scenario 6)

Required logic:

1. Split the order quantity by **alternative UoM**, largest first (PAL → CAR → IBX → PC). A 1-PAL request only looks at bins with a **full pallet**; the same for CAR and IBX.
2. Within each layer, **earliest expiry** first.
3. Same expiry → **storage type priority**.
4. Same storage type priority → **first goods receipt**.

This is a **stock removal** topic, not WOCR: it decides which quant becomes the WT. WOCR only groups the WTs afterwards.

How it maps to EWM **(verify in your system)**:

| Step | EWM building block |
|---|---|
| 1 | Quantity classification from the alternative UoM / packaging specification → one storage type search sequence per classification |
| 2 | Stock removal rule, sort field shelf-life expiration date (`VFDAT`) ascending |
| 3 | The storage types of a layer must be in a **storage type group**. Without a group, EWM searches storage type by storage type and stops when enough stock is found – storage type would then win over expiry. With a group, all quants are pooled first, then sorted. Second sort field: storage type (works when the numbering follows the priority), otherwise a BAdI |
| 4 | Third sort field GR date (`WDATU`) ascending |

Example (SKU E: 1 PAL = 10 CAR = 500 PC, 1 CAR = 5 IBX = 50 PC, 1 IBX = 10 PC), order 620 PC = 1 PAL + 2 CAR + 2 IBX:

| Layer | Search sequence | Decided at | Result |
|---|---|---|---|
| PAL | 0030 → 0040 | ③ storage type | HU P-1002 (06-L9, 30 Nov) beats P-1005 in bulk (same expiry, prio 2). Opened pallet P-1003 is not a full PAL |
| CAR | 0020 → 0030 | ④ GR date | 04-R4 (12 Aug). 07-L6 is older but in storage type prio 2 |
| IBX | 0010 → 0020 | ③ storage type | 02-R3. 05-R6 has the same expiry and older GR but prio 2; loose PC in 01-R4 is never considered |

---

## Sources

- [SAP Learning – Applying the Stock Removal Strategies](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/applying-the-stock-removal-strategies)
- [SAP Learning – Outlining the Goods Issue Process in SAP EWM](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/outlining-the-goods-issue-process-in-sap-ewm)
- [SAP Learning – Creating Warehouse Orders](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/creating-warehouse-orders)
- [SAP Help – Warehouse Order Creation (EWM 7.0 EhP2)](https://help.sap.com/doc/saphelp_ewm700_ehp02/7.0.2/en-US/48/890776d2b21b5ae10000000a42189c/content.htm)
- [SAP Community – WOCR determination based on activity area](https://answers.sap.com/t5/supply-chain-management-blogs-by-members/sap-ewm-wocr-determination-based-on-activity-area/ba-p/13575056)
- [SAP Community – Embedded EWM batch determination (Q&A)](https://community.sap.com/t5/supply-chain-management-q-a/embedded-ewm-batch-determination/qaq-p/12373828)
- [SAP Learning – Implementing Two-Step Picking](https://learning.sap.com/courses/resource-management-in-sap-ewm/implementing-two-step-picking)
- [SAP Press blog – Two-step picking in SAP EWM](https://blog.sap-press.com/two-step-picking-in-sap-ewm)
- [SAP Learning – Setting Up the Pick, Pack, and Pass Process](https://learning.sap.com/courses/resource-management-in-sap-ewm/setting-up-the-pick-pack-and-pass-process)
- [SAP Community – Deep dive into SAP EWM consolidation groups during packing](https://blogs.sap.com/t5/supply-chain-management-blogs-by-members/deep-dive-into-sap-ewm-consolidation-groups-during-packing/bc-p/13573768)
- [SAP Knowledge Base Article 3058611](https://userapps.support.sap.com/sap/support/knowledge/en/3058611)
- [SAP Learning – Outlining Warehouse Structures](https://learning.sap.com/courses/processes-in-sap-s-4hana-ewm/outlining-warehouse-structures)
- [SAP Community – EWM stock removal strategies (VFDAT sort)](https://community.sap.com/t5/supply-chain-management-q-a/ewm-stock-removal-strategies/qaq-p/11464648)
- [ArchLynk – Warehouse order creation process](https://archlynk.com/blog/warehouse-order-creation-process-and-its-benefits)
