# Level 2 — Presidio PII discovery (outbound traffic)

Presidio (en_core_web_lg) over outbound bodies. UNPLANTED hits are candidates requiring manual review, not confirmed leaks.

## grammarly  (17 outbound bodies scanned)

**Planted PII detected (expected):** 14 entity instances
- types: ORGANIZATION, PERSON, PHONE_NUMBER, URL, US_DRIVER_LICENSE

**UNPLANTED PII candidates (review):** 28
| type | detected text | score |
|---|---|---|
| DATE_TIME | `2026-05-23` | 0.95 |
| DATE_TIME | `2026-05-23\nPrepared` | 0.85 |
| DATE_TIME | `4372-45c2-b756-1affdd2e7723` | 0.85 |
| LOCATION | `Q3` | 0.85 |
| ORGANIZATION | `Q2` | 0.85 |
| ORGANIZATION | `Allocated` | 0.85 |
| ORGANIZATION | `Non-Disclosure` | 0.85 |
| ORGANIZATION | `BDSG` | 0.85 |
| ORGANIZATION | `writingExpert","globalPart","globalPartPlaceholder","hide...` | 0.85 |
| URL | `eyJraWQiOiJjMzRkZDk0Zi00NTZlLTRkN2QtYmY4OS03MzE1N2E4YzJjM...` | 0.5 |
| US_BANK_NUMBER | `33894851` | 0.4 |
| US_DRIVER_LICENSE | `a840` | 0.65 |
| US_DRIVER_LICENSE | `a265` | 0.65 |
| US_DRIVER_LICENSE | `33894851` | 0.4 |
| US_DRIVER_LICENSE | `e615` | 0.3 |
| US_DRIVER_LICENSE | `Q2` | 0.3 |
| US_DRIVER_LICENSE | `FY2026` | 0.3 |
| US_DRIVER_LICENSE | `Q1` | 0.3 |
| US_DRIVER_LICENSE | `Q3` | 0.3 |
| US_DRIVER_LICENSE | `b756` | 0.3 |
| US_DRIVER_LICENSE | `b490` | 0.3 |
| US_DRIVER_LICENSE | `716766` | 0.01 |
| US_DRIVER_LICENSE | `1752409` | 0.01 |
| US_DRIVER_LICENSE | `2435522` | 0.01 |
| US_DRIVER_LICENSE | `2668809` | 0.01 |
| US_DRIVER_LICENSE | `2669025` | 0.01 |
| US_DRIVER_LICENSE | `3125674` | 0.01 |
| US_DRIVER_LICENSE | `3132918` | 0.01 |

## languagetool  (4 outbound bodies scanned)

**Planted PII detected (expected):** 4 entity instances
- types: URL, US_DRIVER_LICENSE

**UNPLANTED PII candidates (review):** 10
| type | detected text | score |
|---|---|---|
| DATE_TIME | `2026-05-23` | 0.95 |
| ORGANIZATION | `true&level=picky&language` | 0.85 |
| URL | `40priv-research-demo.in` | 0.5 |
| US_DRIVER_LICENSE | `Q2` | 0.65 |
| US_DRIVER_LICENSE | `E2` | 0.65 |
| US_DRIVER_LICENSE | `A742` | 0.65 |
| US_DRIVER_LICENSE | `Q3` | 0.65 |
| US_DRIVER_LICENSE | `232026` | 0.4 |
| US_DRIVER_LICENSE | `FY2026` | 0.3 |
| US_DRIVER_LICENSE | `Q1` | 0.3 |
