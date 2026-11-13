# Profile redesign report

Implemented in `/home/vispl/projects/Mananlabs/MananLabs`, the actual Git repository. Its `origin` is `https://github.com/MananLabs/MananLabs.git`, confirming the profile repository. No commits or pushes were made.

## Files

- Modified: `README.md` — replaced the JSON profile, placeholder projects, and placeholder contact links with a compact portfolio.
- Created: `assets/ascii-portrait.gif`, `assets/ascii-portrait.png`, `assets/typing-intro.gif`.
- Created: `scripts/generate_ascii_portrait.py` and this report.
- Preserved: the source JPEG and existing `banner.gif`; no unrelated application files changed.

## Visuals and animation

- ASCII portrait uses the actual 1080 × 1920 photograph, EXIF-aware loading, a face-centered crop `(330, 246, 775, 801)`, contrast adjustment, sharpening, brightness-to-character mapping, and aspect-correct monospace cells.
- Portrait: **508 × 680**, **41 frames**, **308,946 bytes** (302 KiB), **5.76-second loop**, including a **2.6-second final hold**, progressive scan reveal, and fade back to the dark terminal.
- Static fallback: **508 × 680**, **140,320 bytes**. Clicking the portrait opens it.
- Local typing introduction: **352 × 96**, **44 frames**, **27,270 bytes**. All four roles also appear as ordinary text.
- Total animated payload: approximately **328 KiB**. A shared GIF palette avoids frame-to-frame color flicker.
- Visually inspected the source crop, static portrait, and a four-frame reveal contact sheet. Hair silhouette, glasses, face orientation, nose, and jaw remain apparent. Recognition is subjective; this is deliberately character-based artwork.

## Mobile compatibility

- One content column; stacked project sections and statistics.
- No tables, fixed-width attributes, JSON/code blocks, CSS, scripts, iframes, or layout dependencies.
- Header images retain their intrinsic sizes and use GitHub's normal responsive image constraints. The README does not rely on custom `max-width` styles surviving sanitization.
- Skills use short, separately wrapping inline-code items and small category symbols.
- Checked inline-code widths against a 320px viewport with 16px side margins; the longest item fits the 288px content area.
- A temporary HTML approximation was prepared for a 390px browser preview. Chrome could not launch because this environment denies a required socket operation. Actual GitHub/mobile rendering remains unverified; the structural and width checks are not a browser rendering test.

## Validation

- All local Markdown/HTML image and link targets exist; internal navigation anchors resolve.
- HTTPS URL syntax and query formatting checked, including the `MananLabs` username on each statistics card.
- Both GIFs contain multiple distinct frames, loop indefinitely, and decode correctly in Pillow.
- Verified the portrait's longest-held GIF frame matches the static PNG within palette-quantization tolerance.
- `git diff --check` passes. No unsupported active content is present in the README.

## External services and outstanding details

- Only the statistics images depend on external services: GitHub Readme Stats (`github-readme-stats.vercel.app`) and GitHub Readme Streak Stats (`streak-stats.demolab.com`). Both use matching dark colors. Text and a direct GitHub link remain available if cards fail.
- Header animations and portrait fallback are local. No unconfigured contribution snake or external typing service was added.
- GitHub API access failed due to network/DNS restrictions; web retrieval also failed, and searches did not establish the requested repositories. Statistics service availability could not be verified. Correct URL formatting does not establish service uptime.
- Added user-supplied LinkedIn (`manan-mittal1123482`), GitHub (`MananLabs`), email (`mittalmanan81@gmail.com`), and Twitter / X (`Manan1123482`) links. No portfolio URL has been supplied, so it remains omitted. Contact URL syntax was checked; account ownership is based on the user’s supplied details.
- Project descriptions use the task's supplied information. Framework stacks, project repository URLs, and live demos could not be verified and are omitted. Technology/integration focus lines describe only the supplied concepts, not inferred framework choices.
- SocialIQ has no available local documentation. Its entry retains only the supplied social-intelligence description; features and technologies need source documentation.

## Regeneration

Requires Python and Pillow. From the repository root:

```sh
python -m pip install Pillow
python scripts/generate_ascii_portrait.py --photo ../Snapchat-108467442.jpg
```

Run `python scripts/generate_ascii_portrait.py --help` for output directory, normalized crop, character-column count, and font options. For a new photograph, adjust `--crop`; the default crop is specific to the supplied portrait. The source image is opened read-only and is never saved over.
