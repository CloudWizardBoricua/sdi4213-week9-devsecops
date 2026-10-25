"""Build the submission from genuine screenshots and the evidence index.

Run from any directory with Python 3.13 and reportlab installed.
The PDF embeds original PNG files without modifying their content.
"""

from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence"
OUTPUT = ROOT / "output/pdf/Week9_DevSecOps_Evidence.pdf"
REPO = "https://github.com/CloudWizardBoricua/sdi4213-week9-devsecops"
W, H = landscape(A3)
MARGIN = 48
NAVY = colors.HexColor("#0f172a")
TEAL = colors.HexColor("#0f766e")
PURPLE = colors.HexColor("#6d28d9")
BLUE = colors.HexColor("#1d4ed8")
MUTED = colors.HexColor("#475569")


def markup(text):
    return re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', escape(text))


def paragraph(canvas, text, x, top, width, size=15, color=NAVY, bold=False):
    style = ParagraphStyle(
        "text", fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=size * 1.4, textColor=color,
        spaceBefore=0, spaceAfter=0,
    )
    item = Paragraph(text, style)
    _, height = item.wrap(width, H)
    assert top - height > 40, "Text would overlap footer"
    item.drawOn(canvas, x, top - height)
    return top - height


def chrome(canvas, page, section):
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    for i, color in enumerate((BLUE, TEAL, PURPLE, colors.HexColor("#92400e"), colors.HexColor("#b91c1c"))):
        canvas.setFillColor(color)
        canvas.rect(i * W / 5, H - 9, W / 5, 9, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, H - 34, "SDI 4213 | WEEK 9 DEVSECOPS")
    canvas.drawRightString(W - MARGIN, H - 34, section.upper())
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.line(MARGIN, 35, W - MARGIN, 35)
    canvas.setFont("Helvetica", 10)
    canvas.drawString(MARGIN, 20, "CloudWizardBoricua | Execution evidence: October 25, 2026")
    canvas.drawRightString(W - MARGIN, 20, f"{page} / 12")


def build():
    index = (EVIDENCE / "README.md").read_text(encoding="utf-8")
    rows = [line.split("|")[1:-1] for line in index.splitlines() if re.match(r"\| \d+ -", line)]
    assert len(rows) == 10
    reflections = re.findall(r"### (.+?)\n\n(.+?)(?=\n\n###|\Z)", index, re.S)
    assert len(reflections) == 4
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = Canvas(str(OUTPUT), pagesize=(W, H), pageCompression=1)
    c.setTitle("Week 9 DevSecOps - Ten Milestones and Four Reflections")
    c.setAuthor("CloudWizardBoricua")
    c.setSubject("SDI 4213 Help Desk security hardening execution evidence")

    chrome(c, 1, "Submission overview")
    top = paragraph(c, "Securing the Help Desk<br/>CI/CD Pipeline", MARGIN, H - 85, W - 2 * MARGIN, 38, NAVY, True)
    top = paragraph(c, "Ten milestones. Four reflections. Verified local execution and GitHub checks.", MARGIN, top - 20, W - 2 * MARGIN, 19, TEAL)
    top = paragraph(c, f'<link href="{REPO}" color="#1d4ed8">CloudWizardBoricua/sdi4213-week9-devsecops</link>', MARGIN, top - 27, W - 2 * MARGIN, 18)
    top = paragraph(c, f'<link href="{REPO}/issues/1" color="#1d4ed8">Issue #1</link> | <link href="{REPO}/pull/3" color="#1d4ed8">Merged security PR #3</link> | <link href="{REPO}/tree/main/docs/evidence/logs" color="#1d4ed8">Complete command records</link>', MARGIN, top - 14, W - 2 * MARGIN, 16)

    top -= 33
    for heading, body in [
        ("Verified outcome", "The original two tests passed before and after hardening in Python 3.13 containers. Streamlit, PostgreSQL, and Adminer ran locally; request creation, listing, status changes, and persistence were exercised. The hardened image returned UID 10001, and both GitHub workflows passed on PR #3 and its merge to main."),
        ("Security findings", "Docker Scout recorded 97 baseline findings: 5 critical, 41 high, 23 medium, and 28 low across 19 vulnerable packages. These are dated observations of the preserved baseline image. Non-root execution limits privileges; it does not remove vulnerable packages."),
        ("How to read the evidence", "Pages 2-11 contain Milestones 1-10 in assignment order, with one caption per screenshot. Page 12 continues Milestone 10 with four reflections. The screenshots are embedded at their original aspect ratio and can be enlarged in a PDF viewer."),
        ("Capture provenance", "Milestones 1, 2, 4, 5, and 7 are browser screenshots of explicitly labeled, read-only views of actual captured command output; they are not native terminal screenshots. Milestones 3, 6, 8, 9, and 10 show the live GitHub interface. Full logs and UTC execution metadata accompany the report in the repository."),
    ]:
        top = paragraph(c, heading, MARGIN, top, W - 2 * MARGIN, 17, PURPLE, True)
        top = paragraph(c, body, MARGIN, top - 5, W - 2 * MARGIN, 14)
        top -= 20
    c.showPage()

    sources = [
        "/blob/main/docs/evidence/logs/baseline-tests.txt",
        "/tree/main/docs/evidence/logs",
        "/blob/main/.github/dependabot.yml",
        "/blob/main/docs/evidence/logs/baseline-cves.txt",
        "/blob/main/docs/evidence/logs/baseline-recommendations.txt",
        "/blob/b87c619eeab12c7f8ac729c6b4ddaaa7a2ce6e5c/Dockerfile",
        "/blob/main/docs/evidence/logs/hardened-uid.txt",
        "/blob/b87c619eeab12c7f8ac729c6b4ddaaa7a2ce6e5c/.github/workflows/security.yml",
        "/actions/runs/40234477168",
        "/pull/3/files",
    ]
    for number, row in enumerate(rows, 1):
        label, _, caption = (value.strip() for value in row)
        title = "Milestone " + label
        chrome(c, number + 1, f"Evidence {number:02d} of 10")
        c.bookmarkPage(f"milestone-{number}")
        c.addOutlineEntry(title, f"milestone-{number}")
        paragraph(c, escape(title), MARGIN, H - 57, W - 2 * MARGIN, 24, NAVY, True)
        shot = ImageReader(str(EVIDENCE / "screenshots" / f"milestone-{number:02d}.png"))
        iw, ih = shot.getSize()
        scale = min((W - 2 * MARGIN) / iw, (H - 220) / ih)
        sw, sh = iw * scale, ih * scale
        x, y = (W - sw) / 2, H - 115 - sh
        c.drawImage(shot, x, y, sw, sh, mask="auto")
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.rect(x, y, sw, sh, stroke=1, fill=0)
        end = paragraph(c, "<b>Caption.</b> " + markup(caption), MARGIN, y - 12, W - 2 * MARGIN, 14)
        source = sources[number - 1]
        paragraph(c, f'<link href="{REPO}{source}" color="#1d4ed8">Open supporting source on GitHub</link> | Captured October 25, 2026', MARGIN, end - 10, W - 2 * MARGIN, 11)
        c.showPage()

    chrome(c, 12, "Milestone 10 continued")
    top = paragraph(c, "Milestone 10 - Final Pull Request and Reflection", MARGIN, H - 66, W - 2 * MARGIN, 27, NAVY, True)
    top = paragraph(c, "Reflections beneath Screenshot 10 (continued from the preceding page)", MARGIN, top - 14, W - 2 * MARGIN, 16, TEAL)
    top -= 32
    for number, (question, answer) in enumerate(reflections, 1):
        top = paragraph(c, f"{number}. {escape(question)}", MARGIN, top, W - 2 * MARGIN, 18, PURPLE, True)
        top = paragraph(c, markup(answer.strip()), MARGIN, top - 8, W - 2 * MARGIN, 16)
        top -= 25
    paragraph(c, f'<link href="{REPO}/pull/3" color="#1d4ed8">Security PR #3 merged October 25, 2026 at 21:16:51 UTC</link><br/>Merge commit: ca2035c8aeca9a7dae107e403f77e270ed8b4392', MARGIN, top - 5, W - 2 * MARGIN, 11, MUTED)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
