# Layered Stock Removal Logic – SAP EWM

As of 21 Oct 2026 · Arifin Dobson

## Expected logic

For every order item, EWM must choose the quant that wins a four-key test, applied in strict order. A later key only breaks ties left by the earlier one.

1. **UoM layer (filter).** Split the order quantity by alternative UoM, largest first: PAL → CAR → IBX → PC remainder. Each layer looks only at quants stored in exactly that UoM. A 1 PAL request searches only bins holding a full pallet (complete HU). A CAR request searches only full cartons, and IBX only full inner boxes.
2. **Earliest expiry (FEFO).** Within the layer, the lowest shelf-life expiration date wins.
3. **Storage type priority.** Same expiry → the storage type with the better priority in that layer's search sequence wins.
4. **First goods receipt (FIFO).** Same priority → the oldest GR date wins.

In short, each layer is a filter followed by a three-key sort:

```
rank(layer) = sort ascending by (expiry, Stype prio, GR date)
              over quants whose UoM = layer UoM
```

If the top-ranked quant holds less than the layer needs, the next-ranked quant supplies the rest. An opened pallet with 6 CAR left is a CAR quant, so it never competes in the PAL layer.

This is a **stock removal** rule, not a WOCR rule. It decides which quant becomes the warehouse task. WOCR only groups those tasks into warehouse orders afterwards.

## Worked example

An order of 620 PC of SKU E becomes 1 PAL + 2 CAR + 2 IBX. The three layers are settled at ③, ④ and ③. Alternative UoM: 1 PAL = 10 CAR = 500 PC, 1 CAR = 5 IBX = 50 PC, 1 IBX = 10 PC. All stock data is illustrative.

**Layer PAL (need 1 PAL)** – search sequence 0030 Pallet rack (prio 1) → 0040 Bulk storage (prio 2). Settled at ③ storage type.

| Rank | Bin | Stype (prio) | Stock | Expiry | GR date | Take |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 06-L9 | 0030 (1) | 1 PAL, HU P-1002 | 30 Nov 26 | 10 Sep 26 | 1 PAL |
| 2 | 09-L2 | 0040 (2) | 1 PAL, HU P-1005 | 30 Nov 26 | 28 Aug 26 | |
| 3 | 06-R11 | 0030 (1) | 1 PAL, HU P-1004 | 20 Dec 26 | 14 Sep 26 | |
| 4 | 07-R10 | 0030 (1) | 1 PAL, HU P-1001 | 15 Jan 27 | 2 Sep 26 | |

P-1005 in bulk storage has the same expiry and an older GR, but bulk is only prio 2 for pallets.

**Layer CAR (need 2 CAR)** – search sequence 0020 Carton rack (prio 1) → 0030 Pallet rack (prio 2). Settled at ④ GR date.

| Rank | Bin | Stype (prio) | Stock | Expiry | GR date | Take |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 04-R4 | 0020 (1) | 4 CAR | 10 Nov 26 | 12 Aug 26 | 2 CAR |
| 2 | 04-L2 | 0020 (1) | 3 CAR | 10 Nov 26 | 20 Aug 26 | |
| 3 | 07-L6 | 0030 (2) | 6 CAR, opened HU P-1003 | 10 Nov 26 | 5 Aug 26 | |
| 4 | 05-L5 | 0020 (1) | 5 CAR | 5 Dec 26 | 1 Sep 26 | |

Three quants tie on expiry. 07-L6 has the oldest GR but drops out at ③ because the pallet rack is only prio 2 for cartons. Then ④ picks 04-R4 over 04-L2.

**Layer IBX (need 2 IBX)** – search sequence 0010 Shelving (prio 1) → 0020 Carton rack (prio 2). Settled at ③ storage type.

| Rank | Bin | Stype (prio) | Stock | Expiry | GR date | Take |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 02-R3 | 0010 (1) | 4 IBX | 31 Oct 26 | 1 Sep 26 | 2 IBX |
| 2 | 05-R6 | 0020 (2) | 6 IBX | 31 Oct 26 | 2 Aug 26 | |
| 3 | 02-L5 | 0010 (1) | 3 IBX | 15 Dec 26 | 18 Aug 26 | |

Loose pieces in 01-R4 expire earlier (20 Oct) but are never considered, because they are not full IBX.

**Spill-over:** 380 PC = 7 CAR + 3 IBX takes 4 CAR from 04-R4 and the remaining 3 CAR from 04-L2, the next rank.

**Several orders (wave):** orders run in sequence, and each one only sees the stock left by the ones before it. In the simulation's 4-order wave (tab 7), PM#124 takes pallet P-1002. PM#125 then gets P-1005 from bulk storage, settled at ② because it is now the only pallet expiring on 30 Nov. For SKU F, inner boxes in 04-R8 win at ② for two orders, even though the carton rack is only prio 2 for IBX.

## How it maps to EWM

The logic needs three standard building blocks: quantity classification, a storage type group per layer, and a stock removal rule with three sort fields.

| Step | EWM object | Setting |
| --- | --- | --- |
| ① UoM layer | Quantity classification (from alternative UoM or packaging specification) | One storage type search sequence per classification: PAL → 0030 · CAR → 0020, 0030 · IBX → 0010, 0020 · PC → 0010 |
| ② Expiry | Stock removal rule, sort field 1 | Shelf-life expiration date (`VFDAT`) ascending |
| ③ Storage type priority | Storage type group + sort field 2 | Storage type ascending. This works only if the numbering follows the priority; otherwise a BAdI is needed |
| ④ First GR | Stock removal rule, sort field 3 | GR date (`WDATU`) ascending |

**Pitfall: the search sequence alone gets ② and ③ backwards.** EWM searches the storage types in a sequence one by one and stops once it finds enough stock. Storage type would then win over expiry. A **storage type group** pools the quants of all its storage types first and then applies the sort, which gives expiry → storage type → GR ([SAP Learning](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/applying-the-stock-removal-strategies)).

Full-pallet tasks are HU warehouse tasks: the whole pallet moves without being opened. Many warehouses route them to their own WOCR or forklift queue.

## Warehouse structure terms

The hierarchy runs warehouse number → storage type → storage section → storage bin → quant. Definitions follow [SAP Learning – Outlining Warehouse Structures](https://learning.sap.com/courses/processes-in-sap-s-4hana-ewm/outlining-warehouse-structures). The codes are example values.

| Term | Definition | Example |
| --- | --- | --- |
| Storage type | Physical or logical subdivision of a warehouse (4 characters). Its settings control putaway and stock removal | 0010 Shelving, 0020 Carton rack, 0030 Pallet rack |
| Storage section | Organizational subdivision of a storage type that groups bins with similar attributes, used by putaway | 0001 fast movers, 0002 slow movers |
| Storage bin | Smallest addressable unit of space; coordinates up to 18 characters (aisle–stack–level) | 03-R5 |
| Quant | Quantity of one product in one bin, with batch, GR date and expiry | 4 CAR in 03-R4 |
| Storage type group | Pools several storage types so one sort runs across all of them | 0020 + 0030 for the CAR layer |

## Open points to verify

- [ ] Is the quantity classification derived from the alternative UoM or from packaging specifications?
- [ ] Is storage type available as a sort field in the stock removal rule in our release, or is a BAdI needed for ③?
- [ ] Are the storage type priorities the same for every layer, so the numbering can follow them?
- [ ] What happens when a layer runs short: fall back to the next smaller UoM, or create a shortage?
- [ ] Is shelf-life expiry batch-managed for these products, so that `VFDAT` is filled on every quant?
- [ ] Do full-pallet HU tasks need their own WOCR / forklift queue?

## Sources

- [SAP Learning – Applying the Stock Removal Strategies](https://learning.sap.com/courses/basic-customizing-in-sap-s-4hana-ewm/applying-the-stock-removal-strategies)
- [SAP Learning – Outlining Warehouse Structures](https://learning.sap.com/courses/processes-in-sap-s-4hana-ewm/outlining-warehouse-structures)
- [SAP Community – EWM stock removal strategies (VFDAT sort)](https://community.sap.com/t5/supply-chain-management-q-a/ewm-stock-removal-strategies/qaq-p/11464648)
- Interactive simulation: `ewm-wocr-animation.html`, tabs 6 (one order, editable quantity) and 7 (4-order wave)
