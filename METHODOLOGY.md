# Development and verification methodology

## Purpose and provenance

These five exercises are synthetic quantity-takeoff fixtures. They were created by Takeoff Field Tools from fictional, deliberately simple scopes and known dimensions. No customer drawing, active project, bid, estimate, or field observation was used.

The drawings and answer sheets were generated in Python with ReportLab. The generator filenames and commands are recorded in [`source-manifest.json`](source-manifest.json). The generator source files are maintained by the publisher but are not included in this education-only repository. This document, the machine-readable check set, the audit utility, the exact published PDFs, and their SHA-256 hashes are public so the current answers can be inspected and reproduced.

At the stated scale, one drawing foot is represented by 9 PDF points: 72 points per inch divided by 8 for a scale of 1/8 inch equals 1 foot. Labeled dimensions are authoritative. The graphic scale is a practice aid and must be recalibrated if a viewer or printer resizes a sheet.

## How the exercises were developed

Each plan began with a small set of declared geometry and scope inputs, such as room dimensions, partition lengths, assembly thicknesses, opening sizes, or symbol counts. Page 1 presents those inputs as a measurable drawing and a written takeoff basis. Page 2 presents the intended scope interpretation, formula, unit, rounding, and answer.

The five exercises cover:

- drywall partitions, openings, track, and ceilings;
- concrete slabs, footings, sidewalk, forms, and pad counts;
- flooring, wall and ceiling paint, base, and frame counts;
- landscape area, mulch volume, edging, irrigation, trees, and shrubs; and
- a simplified mixed-trade remodel with flooring, partitions, cabinets, counters, doors, fixtures, and ceiling paint.

The same declared geometry informed the drawing annotations and answer schedules. That makes the files internally controlled, but generator consistency by itself is not independent validation. The separate arithmetic audit below exists to catch formula or transcription errors.

## Verification record

On 2026-08-27, the published collection received this review:

1. The five public PDFs were matched to the byte counts and SHA-256 values in `source-manifest.json`.
2. Text was extracted from both pages of every PDF. All 42 expected check IDs, units, and displayed results were found on the answer sheets.
3. Every formula in [`methodology/quantity-checks.json`](methodology/quantity-checks.json) was recalculated with decimal arithmetic and compared with the published rounded answer. Result: 42 of 42 passed.
4. All 10 PDF pages were rendered at 2448 by 1584 pixels and inspected for clipped text, overlapping objects, unreadable tables, and broken symbols. No visual defect was found.
5. The visible count fixtures were checked against the schedules: 7 drywall door openings, 6 concrete pads, 6 painted frames, 12 trees, 48 shrubs, 3 remodel doors, and 4 remodel plumbing fixtures.

The audit is reproducible with:

```text
python methodology/verify_quantity_checks.py
python -m pip install pypdf
python methodology/verify_quantity_checks.py --verify-pdf-text
```

The first command verifies the formula results, IDs, units, published PDF byte counts, and SHA-256 hashes using only the Python standard library. The optional second pass also extracts page 2 from each PDF and confirms that every audited ID and displayed result is present in its answer row.

## Rounding and units

- Counts use `EA`, lengths use `LF`, areas use `SF`, and volumes use `CY`.
- Count, length, and area answers are whole numbers in this collection.
- Cubic-yard answers are rounded to two decimal places using round-half-up.
- The printed 4-inch sidewalk formula abbreviates 4/12 foot as 0.3333 foot. The audit uses the exact 4/12 conversion; both produce the published 2.47 CY after rounding.
- Waste factors and fixed pricing inputs are not part of the 42 quantity answers. They are controlled workflow examples, not current market-price evidence.

## Review status

As of 2026-08-27:

- automated formula, artifact-hash, PDF-text, and rendered-layout review has been completed;
- a separate manual pass checked the displayed symbol counts and scope boundaries;
- no independent licensed professional review has been completed; and
- no classroom trial, learning-outcome study, or external pedagogical review has been completed.

Instructors and learners should treat the collection as an openly licensed practice aid, not as a validated curriculum or professional standard. Corrections are welcome at support@takeofffieldtools.com.

## Known limitations and intended-use boundaries

- The geometry is intentionally simplified and mostly orthogonal. Real projects contain incomplete details, revisions, alternates, conflicts, and concealed conditions that these exercises do not model.
- Each answer schedule reflects one stated scope interpretation. A different defensible scope may produce a different result; record assumptions before comparing answers.
- Symbol-count answers depend on the markers shown on page 1. They are not equipment, door, fixture, planting, or procurement schedules.
- A PDF viewer or printer can resize a sheet. Calibrate from a labeled dimension before measuring and do not assume an 11-by-17 print remained at the intended scale.
- Fixed QA prices are historical control inputs for testing arithmetic and exports. They are not bids, supplier quotes, productivity claims, or market-price benchmarks.
- These files do not address code compliance, structural design, permitting, safety planning, specifications, procurement, contracting, or construction means and methods.
- A correct result on these exercises does not establish estimator competency or prove that a real bid is complete.

The collection is not for construction, permitting, procurement, contracting, or professional reliance.
