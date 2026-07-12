# Authorship and Tooling Policy

**Applies to:** Every repository in the CubeShackles platform.  
**Canonical owner:** `cubeshackles` (this umbrella repository).  
**Authority:** CubeShackles is founder-led.

---

## Purpose

State who owns CubeShackles narrative, code, and merge decisions — and how AI
coding tools may be used without becoming authors, owners, or brands in platform
documentation.

## Requirements

1. **Founder-led ownership.** CubeShackles intellectual property, product
   narrative, architectural doctrine, and merge authority are founder-led under
   the CubeShackles organization. Every repository README must state:

   `Owner: CubeShackles (founder-led)`

2. **Tools are assistants, not authors.** AI coding assistants (including Cursor,
   Claude, Devin, Codex, Copilot, and similar) may be used for drafting. They are
   not co-authors in documentation, required PR attribution, or platform owners.

3. **Honest tool mentions.** Technical mentions of a CI system or editor as a
   *tool* are allowed (for example GitHub Actions). Ownership and authorship
   claims for tool vendors are not.

4. **Umbrella is canonical.** Contribution rules and this policy are defined in
   `cubeshackles`. Sibling repositories point here; they do not invent alternate
   ownership stories.

## Prohibited in docs, READMEs, PR templates, and manifests

- Marketing badges or blocks that brand AI vendors as platform authors or
  required co-authors (for example “Open with Devin”, “Made with Cursor”, or
  Copilot/Codex/Claude presented as product owners).
- Language that presents a tool vendor as the author, owner, or steward of
  CubeShackles.
- Required `Co-authored-by` lines for AI tools in contribution guides or PR
  templates.

## Allowed

- Using AI assistants during development.
- Naming a tool when documenting how to run a workflow (for example “install
  dependencies with pip”).
- Product repositories whose *CubeShackles product name* contains “agent”
  (for example `cubeshackles-agent`) — that is platform vocabulary, not vendor
  attribution.

## Related

- [`repository-policy.md`](repository-policy.md)
- [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md)
- [`../../docs/repo-governance.md`](../../docs/repo-governance.md)
