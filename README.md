# integral-connectors

Connectors for [`integral-job-search`](https://github.com/nuncaeslupus/integral-job-search):
one small package per job board, saying how to read that board's listings.

A connector is **four files and no code**:

```
connectors/<package>/
  connector.yaml     which URL to fetch, and which element holds which field
  meta.yaml          site, country, language, maintainer, robots.txt policy, fixture provenance
  fixture/list.html  a recorded listing page, so the connector can be checked without the network
  fixture/detail.html
```

`connector.yaml` is data, not a program. Its selectors are single elements —
tag, `#id`, `.class`, `[attr]`, contiguous — with **no CSS combinators at all**,
so reading it can never mean evaluating it.

## The rule: crawlers, never adverts

**This repository collects crawlers. It does not collect job adverts.**

Job adverts are the boards' content, not ours, and the *set* of adverts a person
reads is not public information at all — it carries their field, their level,
their city, and the fact that they are looking. A fixture committed here carries
whatever it was made from, permanently, and no later deletion reaches a clone.

So every fixture must:

- be **sampled for this purpose** — a category listing and one offer from it,
  fetched deliberately. Never an advert a candidate was reading. `meta.yaml`
  declares `fixture: provenance: sampled`, and a package that declares anything
  else, or declares nothing, is refused rather than reviewed by hand;
- carry **excerpted bodies**. A fixture proves the connector finds the right
  fields in real markup; it does not need whole adverts to do that. Cut them,
  and say so with `fixture: bodies: excerpted`.

Excerpt in the **raw bytes** — `tools/excerpt_fixture.py` upstream does this.
Parsing and re-serialising silently repairs whatever the server got wrong, and
repaired markup is exactly what a fixture must not be: it would stop testing the
thing it exists to test.

## Adding a board

Check `robots.txt` first, and record the answer in `meta.yaml` under `policy`.
A board that disallows automated access is not a board to write a connector for,
however easy its markup is. Then open a pull request with the four files.

`manifest.json` is **generated**, not edited — the tool fetches exactly the file
names it lists, so a hand-typed list omits files silently. Upstream regenerates
it with `tools/publish_connectors.py`.
