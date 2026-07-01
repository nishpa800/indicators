# Heavy Weapons ULTRA — ATOM REGISTRY (queryable alert contract)

The indicator emits **one `alert()` per closed bar** carrying **one record per fired atom**, so the
output is a queryable database feed. No OR-collapsing: every atom is individually identifiable with an
explicit direction. Composites (PBJ+X, HV+D+X, Nag+Strong…) are reconstructed **downstream** by
joining records that share the same `t` (and a window of bars for the windowed composites).

## Wire format
```
HWULTRA|v=1|tkr=<tickerid>|tf=<timeframe>|t=<bar time ms>     ← header, once
atom=<ID>|name=<NAME>|eng=<ENGINE>|dir=<bull|bear|neutral>|val=<metric>   ← one line per fired atom
```
Parse: split on `\n`; line 1 = header context; each subsequent line = one DB row (carry header fields).

## Registry (66 atoms)
| ID | name | engine | dir | val |
|--|--|--|--|--|
| R1 | SAAB | RVOL | bull | bb_normalizedPrice |
| R2 | KRATOS | RVOL | bear | bb_normalizedPrice |
| R3 | BULL_RVOL_1X | RVOL | bull | bb_normalizedPrice |
| R4 | BEAR_RVOL_1X | RVOL | bear | bb_normalizedPrice |
| R5 | GRAND_SLAM | RVOL | bull | bb_normalizedPrice |
| R6 | MOAB | RVOL | bear | bb_normalizedPrice |
| T1 | PENTAGON | REGT | neutral | relVolRatio |
| T2 | WTC | REGT | neutral | relVolRatio |
| T3 | HIROSHIMA | REGT | neutral | relVolRatio |
| N1 | NAGASAKI | NAG | neutral | volume |
| M1–M5 | LONG1..LONG5 | MOM | bull | hybRegRatio |
| M6 | SHORT1 | MOM | bear | hybRegRatio |
| M7 | SHORT2 | MOM | bear | hybRegRatio |
| Q1/Q2/Q3 | UU/UUU/UUUU | SEQ | bull | — |
| Q4/Q5/Q6 | DD/DDD/DDDD | SEQ | bear | — |
| B1 | 2X_SAAB | B2B | bull | — |
| B3 | 2X_BULL_1X | B2B | bull | — |
| B5 | MID_BULL | B2B | bull | — |
| B2 | 2X_KRATOS | B2B | bear | — |
| B4 | 2X_BEAR_1X | B2B | bear | — |
| B6 | MID_BEAR | B2B | bear | — |
| D1 | DISP_BULL | DISP | bull | disp_bullStreak |
| D2 | DISP_BEAR | DISP | bear | disp_bearStreak |
| D3/D5 | CDISP_BULL_2P/3P | DISP | bull | disp_bullStreak |
| D4/D6 | CDISP_BEAR_2P/3P | DISP | bear | disp_bearStreak |
| V75/V150/V250/V500/V1000 | HV75..HV1000 | HV | neutral | — |
| P1 | PBJ_BULL | PBJ | bull | — |
| P2 | PBJ_BEAR | PBJ | bear | — |
| H1 | HVD_BULL | HVD | bull | baseRank |
| H2 | HVD_BEAR | HVD | bear | baseRank |
| K1 | HVD_PBJ_BULL | HVDPBJ | bull | — |
| K2 | HVD_PBJ_BEAR | HVDPBJ | bear | — |
| G1 | GZI_BULL_HV | GZI | bull | — |
| G2 | GZI_BULL_GZI | GZI | bull | — |
| C1 | CS1_BULL | CS | bull | — |
| C2 | CS2_BULL | CS | bull | — |
| C3 | CS1_CS2_BULL | CS | bull | — |
| U1 | PUP | PUP | bull | — |
| F1–F7 | FAUNA_{MB,RE,TA,GG,TR,ES,GDR}_BULL | FAUNA | bull | — |
| F8–F14 | FAUNA_{MB,RE,TA,GG,TR,ES,GDR}_BEAR | FAUNA | bear | — |

## Notes
- **Emitted regardless of `show_*` visual toggles** — the DB always has the data even when a plot is hidden.
- Offset −1 atoms (V*, H*, K*) describe the **prior** bar; `t` is the firing (current) bar's time.
- FAUNA (F1–F14) was computed internally but never surfaced before — now queryable.
- Example query for "PBJ+SAAB bull setup": rows where `name in (PBJ_BULL, SAAB)` share the same `t`.

## Example payload (bar with SAAB + Long2 + bull PBJ)
```
HWULTRA|v=1|tkr=AMEX:BRF|tf=5|t=1718712000000
atom=R1|name=SAAB|eng=RVOL|dir=bull|val=12.34
atom=M2|name=LONG2|eng=MOM|dir=bull|val=4.01
atom=P1|name=PBJ_BULL|eng=PBJ|dir=bull|val=
```
