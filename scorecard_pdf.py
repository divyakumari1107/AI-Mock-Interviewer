import os
import xml.sax.saxutils as saxutils
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import inch
from config import Config


def escape_xml(text):
    """Safely escape text for ReportLab Paragraph parsing."""
    if not text:
        return ""
    return saxutils.escape(str(text))


def generate_scorecard_pdf(eval_data, output_filename=None):
    """
    Generate an executive, publication-ready Candidate Interview Scorecard PDF using ReportLab.
    """
    if not output_filename:
        output_filename = f"scorecard_{eval_data.get('session_id', 'session')}_{os.urandom(3).hex()}.pdf"

    file_path = os.path.join(Config.SCORECARD_FOLDER, output_filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    # Colors
    navy_dark = colors.HexColor("#0B192C")
    blue_primary = colors.HexColor("#0066FF")
    slate_gray = colors.HexColor("#475569")
    line_light = colors.HexColor("#E2E8F0")

    rec = eval_data.get("recommendation", "Hire")
    if "Strong Hire" in rec:
        verdict_color = colors.HexColor("#10B981")
    elif "Hire" in rec:
        verdict_color = colors.HexColor("#0066FF")
    elif "Lean" in rec:
        verdict_color = colors.HexColor("#F59E0B")
    else:
        verdict_color = colors.HexColor("#EF4444")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=navy_dark
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=slate_gray
    )
    sec_style = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=blue_primary,
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=navy_dark
    )
    code_style = ParagraphStyle(
        'CodeStyleCustom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=navy_dark
    )

    # 1. Header Banner
    story.append(Paragraph("AI TECHNICAL INTERVIEW SCORECARD", title_style))
    meta_info = f"Candidate: <b>{escape_xml(eval_data.get('candidate_name', 'Candidate'))}</b>  |  Role: {escape_xml(eval_data.get('target_role', 'SDE'))}  |  Company: {escape_xml(eval_data.get('target_company', 'Google'))}  |  Question: {escape_xml(eval_data.get('question_title', 'DSA'))}"
    story.append(Paragraph(meta_info, sub_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=blue_primary, spaceAfter=8))

    # 2. Executive Verdict Box
    overall_score = eval_data.get("overall_score", 0)
    verdict_text = f"<b>OVERALL RATING: {overall_score}/100</b>  •  VERDICT: <b>{escape_xml(rec).upper()}</b>"
    
    verdict_table = Table(
        [[Paragraph(verdict_text, ParagraphStyle('VText', fontName='Helvetica-Bold', fontSize=12, leading=15, textColor=colors.white, alignment=1))]],
        colWidths=[7.4 * inch],
        rowHeights=[28]
    )
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), verdict_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 8))

    # 3. Four Evaluation Pillars Breakdown Table
    story.append(Paragraph("EVALUATION CRITERIA BREAKDOWN", sec_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=line_light, spaceAfter=5))

    corr = eval_data.get("correctness_score", 0)
    comp = eval_data.get("complexity_score", 0)
    qual = eval_data.get("quality_score", 0)
    comm = eval_data.get("communication_score", 0)

    criteria_data = [
        ["Criterion", "Weight", "Score", "Performance Evaluation"],
        ["Algorithmic Correctness", "40%", f"{corr}/100", f"Test cases execution: {eval_data.get('correctness_score')}% pass rate."],
        ["Computational Complexity", "25%", f"{comp}/100", f"Derived Time: {eval_data.get('time_complexity', 'O(N)')} | Space: {eval_data.get('space_complexity', 'O(1)')}"],
        ["Code Modularity & Cleanliness", "20%", f"{qual}/100", "AST syntax audit, naming, and structural standards."],
        ["Communication & Hint Usage", "15%", f"{comm}/100", f"Asked clarifying questions. Hints used: {eval_data.get('feedback', {}).get('hints_used', 0)}"]
    ]

    crit_table = Table(criteria_data, colWidths=[2.2 * inch, 0.8 * inch, 0.9 * inch, 3.5 * inch])
    crit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F8FAFC")),
        ('TEXTCOLOR', (0, 0), (-1, 0), navy_dark),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('GRID', (0, 0), (-1, -1), 0.5, line_light),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(crit_table)
    story.append(Spacer(1, 8))

    # 4. Summary Feedback & Recommendations
    story.append(Paragraph("INTERVIEWER FEEDBACK & ACTION ITEMS", sec_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=line_light, spaceAfter=5))
    
    fb = eval_data.get("feedback", {})
    summary_text = fb.get("summary", "Candidate demonstrated functional coding capabilities.")
    story.append(Paragraph(f"<b>Summary:</b> {escape_xml(summary_text)}", body_style))
    story.append(Spacer(1, 4))

    strengths = fb.get("strengths", [])
    if strengths:
        story.append(Paragraph("<b>Key Strengths:</b>", body_style))
        for s in strengths:
            story.append(Paragraph(f"• {escape_xml(s)}", body_style))
        story.append(Spacer(1, 3))

    weaknesses = fb.get("weaknesses", [])
    if weaknesses:
        story.append(Paragraph("<b>Improvement Areas:</b>", body_style))
        for w in weaknesses:
            story.append(Paragraph(f"• {escape_xml(w)}", body_style))
        story.append(Spacer(1, 3))

    # 5. Optimal vs Submitted Code Comparison Snippet
    story.append(Paragraph("OPTIMAL REFERENCE SOLUTION (PYTHON)", sec_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=line_light, spaceAfter=5))
    solution_code = eval_data.get("solution_code", "# Reference solution")
    story.append(Paragraph(escape_xml(solution_code).replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    doc.build(story)
    return file_path, output_filename
