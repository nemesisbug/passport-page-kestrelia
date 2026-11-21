# The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/nemesisbug/passport-page-kestrelia/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/nemesisbug/passport-page-kestrelia/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

An open passport spread of the **Republic of Kestrelia**, a country that
isn't there. Entry for the
[make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

## The document

Left page — the data page of cartographer **Elara Miren Voss** of Port
Aureline: portrait, holder details, the Seal of the Republic, and a
machine-readable zone (ICAO 9303 check digits computed for real).
Right page — visas, stamps and endorsements: a Sularis visa, arrival and
departure stamps from Dravna, Sularis and the Meridian Free Port, a revenue
stamp, a small map of the Three Isles, and one telling piece of paperwork —
the endorsement that the holder may not enter the **Northern Marches**
without a separate permit from the Warden of the Marches.

Every date agrees: the passport was issued 14 Mar 2024, and every stamp
falls after it, in a plausible travel history (Dravna Apr 2024, Sularis
Sep 2025, Meridian Free Port Nov 2026).

## Run

```sh
python3 main.py
```

Writes the spread to `/output/entry.png` (1024×1024 PNG, under 1 MiB).
Set `ENTRY_OUTPUT_PATH` to write it somewhere else instead. Deterministic,
procedural, no network — Pillow only.
