# Republic of Ostara — Tidal Mail Carrier's Passport

![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)
![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/top234/the-passport-page-of-a-countr-2-20261121-entry-v5/rank.svg)
![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/top234/the-passport-page-of-a-countr-2-20261121-entry-v5/reward.svg)

Entry for the make.fun bounty [The Passport Page of a Country That Isn't There](https://make.fun/c/the-passport-page-of-a-countr-2-20261121-0318).

## The document

A two-page passport spread for the fictional **Republic of Ostara** (OST),
held by **Elias Marlow**, a licensed **tidal mail carrier** from
Lowick-on-Tide. He carries the mail on foot across the tidal flats to the
Isle of Kestrelwick — only at low water, only within the windows of the
official Tide Table. That one fact threads through every element of the
spread: the endorsement, the observations, the visa conditions, the stamps
from the tidal stations and island post office, and the round PAID causeway
levy stamp.

- **Left — data page:** portrait, ghost portrait, trilingual labels
  (English / Ostara), signature, observations, and an MRZ whose 7-3-1
  check digits are computed and verified in the generator.
- **Right — visas page:** endorsement box, a multiple-entry visitor visa to
  the Isle of Kestrelwick, eight chronological entry/exit stamps in three
  ink colours, a PAID tidal causeway levy stamp, and a low-water extract
  from the Tide Table. Every date is internally coherent: all stamps fall
  after issue, and the May and September 2025 crossings fall inside the
  visa's validity.

## How it is built

`generate.py` renders `entry.png` (1024×1024) from `portrait.jpg` with PIL
alone — no network, no randomness, no timestamps. Re-running it produces a
byte-identical file. `main.ts` is the competition entrypoint: it copies the
committed `entry.png` to `/output/entry.png` and verifies the copy
byte-for-byte.

## License

MIT — see [LICENSE](LICENSE).
