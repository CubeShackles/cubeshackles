# Translation Review Checklist

**Owner: CubeShackles (founder-led).**

Use before flipping a `README.pt.md`'s `translation_status` from
`machine-assisted` to `reviewed` (see
[`LOCALIZATION_POLICY.md`](LOCALIZATION_POLICY.md) §5/§7).

## Structural

- [ ] Language-navigation line present and correct in both files.
- [ ] Every English `##`/`###` heading has a Portuguese counterpart, same
      order.
- [ ] All relative links resolve to real files/anchors.
- [ ] Code blocks, commands, filenames, env vars are byte-identical to the
      English source.
- [ ] Translation metadata footer present, `canonical_commit` and
      `last_synchronized` set correctly.

## Terminology

- [ ] Every controlled term matches [`GLOSSARY.en-pt.md`](GLOSSARY.en-pt.md).
- [ ] No product/brand name, identifier, path, or currency code was
      translated.
- [ ] Acronyms defined on first use, matching the glossary's approved
      expansion.

## Claims and maturity

- [ ] Portuguese status/maturity wording does not exceed the English source
      (`LOCALIZATION_POLICY.md` §4).
- [ ] No claim appears in Portuguese that is absent from English.
- [ ] Numbers, percentages, dates, currency amounts, and units match the
      English source exactly.
- [ ] No prohibited-claim language introduced (`DOCUMENTATION_STANDARD.md` §3).

## Language quality

- [ ] Formal Angola-appropriate Portuguese; no Brazilian colloquialisms
      (`STYLE_GUIDE.pt.md`).
- [ ] No literal translation that distorts financial-market meaning (e.g.
      "compensação" vs. "liquidação" used correctly).

## Sign-off

- [ ] Reviewer name/handle and date recorded in the metadata footer before
      setting `translation_status: reviewed`.
