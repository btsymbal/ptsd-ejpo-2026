"""
Render production/manuscript.md to production/manuscript.pdf.

Pipeline: Markdown → (inject tables & supplementary figures) → Pandoc (HTML) → WeasyPrint (PDF)
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Raise PIL decompression bomb limit — our own high-res figures are trusted
from PIL import Image
Image.MAX_IMAGE_PIXELS = 200_000_000

# ---------------------------------------------------------------------------
# 0. Project root
# ---------------------------------------------------------------------------
os.chdir(Path(__file__).resolve().parent.parent)

PRODUCTION = Path("production")
MANUSCRIPT = PRODUCTION / "manuscript.md"
TABLES_DIR = PRODUCTION / "tables"
FIGURES_DIR = PRODUCTION / "figures"
OUTPUT_PDF = PRODUCTION / "manuscript.pdf"

PANDOC = "/opt/anaconda3/envs/jupyter_env/bin/pandoc"

# ---------------------------------------------------------------------------
# 1. Read source files
# ---------------------------------------------------------------------------
manuscript = MANUSCRIPT.read_text(encoding="utf-8")

# Load all table files keyed by table number (e.g. "1", "S1")
table_contents: dict[str, str] = {}
for p in sorted(TABLES_DIR.glob("*.md")):
    # Extract table id from filename: table_1_... -> "1", table_s1_... -> "S1"
    m = re.match(r"table_(s?\d+)_", p.name, re.IGNORECASE)
    if m:
        tid = m.group(1).upper() if m.group(1)[0].lower() == "s" else m.group(1)
        table_contents[tid] = p.read_text(encoding="utf-8").strip()

print(f"Loaded {len(table_contents)} tables: {sorted(table_contents.keys(), key=lambda x: (x.startswith('S'), x))}")

# ---------------------------------------------------------------------------
# 2. Inject main tables (1-7) after the paragraph that first references them
# ---------------------------------------------------------------------------

def inject_main_table(md: str, table_id: str, table_md: str) -> str:
    """Insert table markdown after the paragraph that first mentions 'Table <id>'."""
    # Pattern: find 'Table N' (possibly as part of 'Table N;' or 'Table N)')
    pattern = re.compile(rf'\bTable\s+{re.escape(table_id)}\b')
    match = pattern.search(md)
    if not match:
        print(f"  WARNING: No reference found for Table {table_id}")
        return md

    # Find end of the paragraph containing this reference:
    # look for \n\n (blank line) after the match position
    para_end = md.find("\n\n", match.end())
    if para_end == -1:
        para_end = len(md)

    # Check if next non-blank content is a figure (![) — if so, skip past the
    # figure block (image line + caption line) to avoid splitting figure+caption
    rest_after_para = md[para_end:]
    fig_block = re.match(r'\n\n(!\[.*?\]\(.*?\)\n\n\*Figure.*?\*.*?\n)', rest_after_para)
    if fig_block:
        para_end += len(fig_block.group(0))

    injection = f"\n\n{table_md}\n\n"
    return md[:para_end] + injection + md[para_end:]


for tid in ["1", "2", "3", "4", "5", "6", "7"]:
    if tid in table_contents:
        manuscript = inject_main_table(manuscript, tid, table_contents[tid])
        print(f"  Injected Table {tid}")
    else:
        print(f"  WARNING: Table {tid} not found in tables directory")

# ---------------------------------------------------------------------------
# 3. Inject supplementary tables — replace bullet list in Supplementary Tables
# ---------------------------------------------------------------------------

def inject_supplementary_tables(md: str, tables: dict[str, str]) -> str:
    """Replace the supplementary tables bullet list with actual table content."""
    # Find the "### Supplementary Tables" section
    header_match = re.search(r'### Supplementary Tables\n', md)
    if not header_match:
        print("  WARNING: '### Supplementary Tables' header not found")
        return md

    start = header_match.end()

    # The bullet list starts right after the header and continues until end of file
    # or next section header
    rest = md[start:]
    # Find end of bullet list (next heading or end of string)
    end_match = re.search(r'\n(?=## |\n---)', rest)
    end = start + end_match.start() if end_match else len(md)

    # Build replacement: each supplementary table in order
    sup_ids = sorted(
        [k for k in tables if k.startswith("S")],
        key=lambda x: int(x[1:])
    )
    replacement = "\n"
    for sid in sup_ids:
        replacement += f"\n{tables[sid]}\n\n"

    return md[:start] + replacement + md[end:]


manuscript = inject_supplementary_tables(manuscript, table_contents)
print(f"  Injected {len([k for k in table_contents if k.startswith('S')])} supplementary tables")

# ---------------------------------------------------------------------------
# 4. Embed supplementary figures — replace bullet references with images
# ---------------------------------------------------------------------------

def embed_supplementary_figures(md: str) -> str:
    """Replace bullet-point figure references with actual image embeds."""
    # Pattern matches lines like:
    # - **Figure S1.** Description text (`filename.png`).
    # or with (filename.png) instead of backticks
    def replace_fig_bullet(m):
        label = m.group(1)       # e.g. "Figure S1."
        description = m.group(2) # description text
        filename = m.group(3)    # e.g. "figure_s1_violin_h2_dwell_variability.png"
        return (
            f"![{label} {description}](figures/{filename})\n\n"
            f"*{label}* {description}\n"
        )

    pattern = re.compile(
        r'^- \*\*(.+?)\*\*\s+(.+?)\s+\(`?([^)`]+\.png)`?\)\.?$',
        re.MULTILINE
    )
    result = pattern.sub(replace_fig_bullet, md)

    count = len(pattern.findall(md))
    print(f"  Embedded {count} supplementary figures")
    return result


manuscript = embed_supplementary_figures(manuscript)

# ---------------------------------------------------------------------------
# 5. Write combined markdown to temp file and convert to HTML via Pandoc
# ---------------------------------------------------------------------------
with tempfile.NamedTemporaryFile(
    mode="w", suffix=".md", dir=str(PRODUCTION), delete=False, encoding="utf-8"
) as tmp_md:
    tmp_md.write(manuscript)
    tmp_md_path = tmp_md.name

with tempfile.NamedTemporaryFile(
    mode="w", suffix=".html", dir=str(PRODUCTION), delete=False, encoding="utf-8"
) as tmp_html:
    tmp_html_path = tmp_html.name

try:
    print("\nRunning Pandoc...")
    result = subprocess.run(
        [
            PANDOC,
            tmp_md_path,
            "-f", "markdown",
            "-t", "html5",
            "--standalone",
            "--embed-resources",
            f"--resource-path={PRODUCTION}",
            "-o", tmp_html_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Pandoc STDERR:\n{result.stderr}")
        sys.exit(1)
    if result.stderr:
        print(f"Pandoc warnings:\n{result.stderr}")
    print("  Pandoc conversion complete.")

    # ------------------------------------------------------------------
    # 6. Inject CSS and render PDF via WeasyPrint
    # ------------------------------------------------------------------
    html = Path(tmp_html_path).read_text(encoding="utf-8")

    CSS = """
<style>
@page {
    size: A4;
    margin: 1in;
    @bottom-center {
        content: counter(page);
        font-family: "Palatino Linotype", Palatino, Georgia, serif;
        font-size: 9pt;
        color: #555;
    }
}

body {
    font-family: "Palatino Linotype", Palatino, Georgia, serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
    max-width: none;
}

h1 {
    font-size: 16pt;
    text-align: center;
    margin-top: 0;
    margin-bottom: 0.5em;
    line-height: 1.3;
}

h2 {
    font-size: 14pt;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    break-before: page;
}

/* Don't page-break before the very first h2 (right after the title) */
h1 + hr + h2, body > h2:first-of-type {
    break-before: auto;
}

h3 {
    font-size: 12pt;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}

h4 {
    font-size: 11pt;
    margin-top: 1em;
    margin-bottom: 0.3em;
}

/* Horizontal rules as section separators */
hr {
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.5em 0;
}

/* --- Tables --- */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
    line-height: 1.35;
    margin: 1em 0;
    table-layout: fixed;
    word-wrap: break-word;
    overflow-wrap: break-word;
    break-inside: avoid;
}

thead th {
    background-color: #f0f0f0;
    border-bottom: 2px solid #333;
    padding: 6px 5px;
    text-align: left;
    font-weight: bold;
    vertical-align: bottom;
}

tbody td {
    padding: 4px 5px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}

tbody tr:nth-child(even) {
    background-color: #f9f9f9;
}

/* Table caption/title (h1/h2 inside table context — rendered from markdown ## headers) */
table + p, table + p + p {
    font-size: 9pt;
}

/* --- Figures --- */
figure, p:has(> img) {
    text-align: center;
    margin: 1.2em 0;
    break-inside: avoid;
}

img {
    max-width: 100%;
    height: auto;
}

/* Figure captions (italic paragraphs after images) */
p > em:first-child:last-child {
    /* This targets standalone italic paragraphs used as captions */
}

/* --- Lists --- */
ul, ol {
    margin: 0.5em 0;
    padding-left: 2em;
}

li {
    margin-bottom: 0.3em;
}

/* --- References --- */
p a[href] {
    color: #1a0dab;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* --- Supplementary section --- */
h2:last-of-type ~ h3 {
    break-before: auto;
}

/* Avoid orphan headings */
h2, h3, h4 {
    break-after: avoid;
}

/* Keep note paragraphs with their tables */
table + p > em:first-child {
    font-size: 8.5pt;
    color: #444;
}
</style>
"""

    # Inject CSS into <head>
    html = html.replace("</head>", CSS + "\n</head>")

    # Write modified HTML
    Path(tmp_html_path).write_text(html, encoding="utf-8")

    print("Rendering PDF with WeasyPrint...")
    import weasyprint
    import warnings

    wp_warnings: list[str] = []

    # Capture WeasyPrint warnings
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        html_doc = weasyprint.HTML(filename=tmp_html_path)
        pdf_doc = html_doc.render()
        pdf_doc.write_pdf(str(OUTPUT_PDF))

    for w in caught:
        wp_warnings.append(str(w.message))

    # ------------------------------------------------------------------
    # 7. Validation
    # ------------------------------------------------------------------
    assert OUTPUT_PDF.exists(), "PDF file was not created!"
    pdf_size = OUTPUT_PDF.stat().st_size
    assert pdf_size > 0, "PDF file is empty!"

    page_count = len(pdf_doc.pages)

    print(f"\n{'='*50}")
    print(f"SUCCESS: {OUTPUT_PDF}")
    print(f"  Size: {pdf_size / 1024:.0f} KB")
    print(f"  Pages: ~{page_count}")
    print(f"  WeasyPrint warnings: {len(wp_warnings)}")
    if wp_warnings:
        for w in wp_warnings[:10]:
            print(f"    - {w}")
    print(f"{'='*50}")

finally:
    # Clean up temp files
    for p in [tmp_md_path, tmp_html_path]:
        try:
            os.unlink(p)
        except OSError:
            pass
