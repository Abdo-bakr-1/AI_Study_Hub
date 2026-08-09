"""PDF generation for notes export using ReportLab."""

from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="NoteTitle",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#4f46e5"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NoteMeta",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#6b7280"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NoteBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=12,
        )
    )
    return styles


def build_notes_pdf(user, notes):
    """Return an HttpResponse containing a PDF of the user's notes."""
    response = HttpResponse(content_type="application/pdf")
    filename = f"notes_{user.username}_{timezone.now():%Y%m%d}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        title="AI Study Hub - Notes Export",
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = _styles()
    story = []

    # Header
    story.append(Paragraph("AI Study Hub", styles["Title"]))
    story.append(
        Paragraph(
            f"Notes export for <b>{user.username}</b> &mdash; "
            f"{timezone.now():%B %d, %Y %H:%M}",
            styles["NoteMeta"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    header_table = Table(
        [[f"Total notes: {notes.count()}"]],
        colWidths=[doc.width],
    )
    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eef2ff")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#4338ca")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c7d2fe")),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))

    if not notes:
        story.append(
            Paragraph("You have no notes to export yet.", styles["NoteBody"])
        )
    else:
        for index, note in enumerate(notes, start=1):
            story.append(
                Paragraph(f"{index}. {_escape(note.title)}", styles["NoteTitle"])
            )
            cats = ", ".join(c.name for c in note.categories.all()) or "Uncategorized"
            story.append(
                Paragraph(
                    f"Categories: {_escape(cats)} &nbsp;|&nbsp; "
                    f"Updated: {note.updated_at:%Y-%m-%d %H:%M}",
                    styles["NoteMeta"],
                )
            )
            body = _escape(note.content).replace("\n", "<br/>")
            story.append(Paragraph(body, styles["NoteBody"]))
            story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return response


def _escape(text):
    """Escape characters that would break ReportLab's mini-HTML paragraphs."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
