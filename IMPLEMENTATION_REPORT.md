# MananLabs profile implementation report

The existing profile has been refined in place: centered introduction, emoji headings, dividers, a short code-block tagline, logo badges, and concise project descriptions. The ASCII portrait remains the main visual element.

## Files and visual components

- Updated `README.md`: original-style introduction; branded social links; two-sentence About Me; six badge categories; ten compact project entries; Odoo experience; vertically stacked dashboard; contribution sections; goals and animated footer.
- Updated `scripts/generate_ascii_portrait.py` and `assets/ascii-portrait.gif`: slower photo-derived reveal. The same generator also creates the typing GIF, scan accent, footer GIF, and static portrait fallback.
- Added `assets/terminal-accent.gif` and `assets/coding-footer.gif`.
- Added `assets/dashboard/{overview,streak,languages,activity,milestones}.svg` and `assets/contribution-snake.svg`. These currently contain explicit first-sync status messages, **not fabricated data or a synthetic contribution graph**.
- Added `scripts/generate_github_dashboard.py`, `scripts/normalize_snake.py`, `scripts/test_profile_visuals.py`, and `.github/workflows/profile-visuals.yml`.
- Updated this report. Original photograph and legacy `banner.gif` remain untouched. No application code changed. No commits or pushes were performed in this session.

The actual repository is `/home/vispl/projects/Mananlabs/MananLabs` and its remote is `https://github.com/MananLabs/MananLabs.git`. The differently capitalized `/home/vispl/projects/MananLabs` path does not exist on this Linux filesystem.

## Animations and assets

| Asset | Dimensions | Frames | Size | Loop |
| --- | --- | --- | --- | --- |
| ASCII portrait | 508 × 680 | 41 | 308,946 bytes | 7.16 seconds |
| Typing roles | 352 × 96 | 44 | 27,270 bytes | 9.20 seconds |
| Terminal scan accent | 480 × 12 | 32 | 6,801 bytes | 2.88 seconds |
| Coding footer / status light | 352 × 140 | 6 | 7,073 bytes | 5.40 seconds |

Total local GIF payload: approximately **342 KiB**. The portrait holds its completed frame for **2.6 seconds** and fades back to its dark opening. It uses the supplied photo, a face-centered crop, brightness-to-character mapping, and aspect-correct monospace cells. The static fallback is linked directly from the GIF. Green/cyan accents and small purple highlights remain consistent across assets.

The portrait reveal provides the terminal boot effect; role typing and footer status lights supply secondary motion. The scan accent is used once to avoid simultaneous motion across every section. The contribution snake becomes animated only after the first successful GitHub Actions generation.

## Dashboard integration

Dashboard SVGs are generated from **GitHub's own authenticated GraphQL API**, rather than embedding unavailable third-party statistics services. Each is a thin-bordered dark card at 480px intrinsic width:

- Overview: stars across owned public non-fork repositories; public commit contributions in the past year; accessible pull requests and issues opened across all time; contribution-calendar totals in the past year.
- Streak: contribution total, current streak with a circular indicator, and longest streak within the returned past-year calendar. A still-empty current UTC day does not prematurely end a streak.
- Languages: language-byte percentages, official language colors, top six languages plus Other, across owned public non-fork repositories. This describes repository composition, not personal proficiency. Repository listings are paginated; up to 100 language entries are read per repository.
- Activity: real weekly contribution counts across the last twelve complete UTC weeks, stacked as a compact graph that remains legible on mobile.
- Trophies: a custom account-milestone summary of public repositories, received stars, and opened pull requests. It does not pretend to reproduce official GitHub achievement badges or award unearned trophies.

Cards include their refresh date where appropriate. API failures occur before replacement of existing SVGs, preserving the previous successful images. Initial setup cards use the same styling and avoid broken-image placeholders.

Shields.io supplies the technology and contact badge images. No profile-view counter was added because service availability could not be established. No portfolio link was invented. No external typing, statistics, trophy, or animation servers are required for the dashboard/header.

## Enable dashboard and snake

After **you** publish these files to `MananLabs/MananLabs`:

1. Enable GitHub Actions for the repository if disabled.
2. Open **Actions → Profile visuals → Run workflow** on the default branch. No custom secret or personal access token is needed: the workflow uses `secrets.GITHUB_TOKEN`.
3. The workflow fetches public GitHub data and invokes `Platane/snk/svg-only@v3` with `github_user_name: MananLabs` and a dark green/cyan palette.
4. A normalization step preserves the generated snake's viewBox and animation while limiting its intrinsic width to 480px.
5. A separate publishing job commits only `assets/dashboard/` and `assets/contribution-snake.svg` to the default branch. Subsequent refreshes are scheduled daily at **03:23 UTC**. Publishing the workflow on main/master also triggers its first run.

Generation runs with `contents: read`; only publishing receives `contents: write`. The generator checkout does not persist credentials. The workflow is restricted to `MananLabs/MananLabs`, uses concurrency control, and does not run on pull requests. If GitHub policy or branch protection blocks bot pushes, allow this workflow's scoped updates or review/publish the generated artifact manually. Scheduled workflows in inactive public repositories may need to be re-enabled through GitHub.

Inspect failed generation steps and warnings if a card remains on setup status. A failed dashboard or snake refresh retains that component's previous file; successful components can still publish. No fake snake has been generated locally. This workflow has **not been run on GitHub** in this session, so token/API behavior and end-to-end publication still require the first real run.

Reference: [snk's documented SVG action and palette options](https://github.com/Platane/snk#usage), [GitHub token permissions](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token).

## Project evidence and limits

- **CareNest:** local `Dementia_Care/dementia-care-platform` remote verifies `MananLabs/Dementia_Care`; source confirms CareNest branding, Next.js, Supabase/PostgreSQL, Storage uploads, and Sarvam speech integration.
- **Airway:** local `Uber` remote verifies `MananLabs/Airway`; README confirms React Native, Expo, Supabase, and prototype/demo scope. Clerk was omitted because this checkout documents Supabase authentication instead.
- **FLOWGRID:** local `Aarambh_Haccathon` remote verifies `MananLabs/build-flowgrid-logistics-platform`; README confirms Next.js/FastAPI, OR-Tools, matching, routing, and simulated tracking. AI recovery is documented as planned, so it is not claimed as implemented.
- **DDXPlus:** retained the user's supplied dataset/technology description without inventing a repository URL. The available `ML/med-ai-diagnostic-support-system` checkout documents a different MedAI stack (FAISS/BM25/MongoDB), so it was not presented as proof of the DDXPlus implementation.
- **Odoo:** the user's work context and local Odoo meeting transcripts support CRM stages, activities, and spreadsheet imports; no unsupported integration claims were added.
- Remaining projects use only user-supplied descriptions/stacks. No local documentation established additional SocialIQ or overtime functionality. Unverified repository/demo links are omitted.
- Real contact details came directly from the user: LinkedIn, GitHub, Gmail, and Twitter/X. Ownership was not independently audited.

## Verification and mobile preview

- Seven offline tests pass: streak handling, missing dates, empty data, repository pagination, safe SVG rendering, API-failure preservation, and snake normalization without removing its animation.
- Workflow YAML parses correctly; trigger names, account identity, artifact paths, and separate read/write permissions were inspected. No live Actions run was performed; `actionlint` is unavailable.
- All local links/assets exist; SVGs parse; four GIFs decode, have distinct frames, and loop. The original JPEG's SHA-256 remains `ba34d0a5361db85d38b62f186fc96c4e5a135eac8a389134952debf2b6de4e04`.
- README contains no scripts, custom CSS, iframes, tables, or fixed-width layout attributes. Markdown/HTML wrappers balance. Badge URLs and repository/contact URL syntax are valid. `git diff --check` passes.
- A complete layout approximation was rendered with WeasyPrint at **375px** and **896px**: **zero content boxes extended beyond the content area** at either width. Images scale down, badges wrap individually, and projects/cards remain vertical. Temporary PDFs/PNGs are in `/tmp/manan-preview-{375,896}.*`; the 375px preview was visually inspected.
- This preview approximates GitHub layout; it is not the GitHub sanitizer or mobile app. Badge dimensions were simulated locally because network access is restricted; the preview does not verify remote logo rendering. GIFs appear at their opening frame in this static preview. Chrome itself could not launch because the environment denies a required socket operation.
- GitHub/API and image-service live requests were attempted but unavailable here; network/DNS restrictions and web cache misses prevented uptime checks. Therefore actual remote repository reachability, all Shields logo responses, live statistics, and snake generation remain unverified. The local dashboard/status assets still render without any statistics server.

## Regeneration and tests

```sh
python -m pip install Pillow
python scripts/generate_ascii_portrait.py --photo ../Snapchat-108467442.jpg
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s scripts -p 'test_*.py' -v
```

`generate_ascii_portrait.py --help` lists crop, font, output, and character-column options. The default normalized crop is specific to this photograph. The dashboard generator uses only Python's standard library and takes `GITHUB_TOKEN` from the environment; never place tokens in the README or script.
