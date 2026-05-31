#!/usr/bin/env python3
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

OUTPUT = "report/project_completion_summary.pdf"


def p(text, style):
    return Paragraph(text, style)


def bullet_paragraphs(items, style):
    paragraphs = []
    for item in items:
        paragraphs.append(Paragraph(f"&#8226; {item}", style))
        paragraphs.append(Spacer(1, 2))
    return paragraphs


def build_pdf() -> None:
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "title",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=10,
    )

    sub = ParagraphStyle(
        "sub",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=10,
        spaceAfter=6,
    )

    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )

    emph = ParagraphStyle(
        "emph",
        parent=body,
        fontSize=11,
        textColor=colors.HexColor("#0b5"),
        spaceAfter=8,
    )

    story = []

    story.append(p("Assignment 13 - AI for Undefined Behaviour Detection in C/C++ Programs", title))
    story.append(Spacer(1, 4))

    story.append(p("Project Problem Description", sub))
    story.append(
        p(
            "Study whether an LLM can detect undefined behaviour (UB) in C/C++ source code before LLVM/Clang optimizations exploit that UB and transform the program in surprising ways.",
            body,
        )
    )
    story.append(
        p(
            "In C/C++, operations such as signed integer overflow, null dereference, invalid shifts, and out-of-bounds access may have undefined behaviour. LLVM can legally optimize under the assumption that UB does not occur, which can change program behaviour in surprising ways.",
            body,
        )
    )
    story.append(
        p(
            "Objective: Evaluate whether an LLM can (a) identify UB patterns, (b) explain UB causes, (c) predict LLVM optimization effects, and (d) compare with UBSan, clang-tidy, and static analyzers.",
            body,
        )
    )

    story.append(p("Overall Completion Percentage", sub))
    story.append(p("Project completion: <b>100%</b> for assignment deliverables.", emph))

    story.append(p("What Has Been Done (Non-Technical Summary)", sub))
    done_items = [
        "Prepared a full benchmark set of UB examples, plus safe examples for false-positive checking.",
        "Ran compiler experiments to show how optimization changes behaviour or reasoning.",
        "Collected outputs from UBSan, clang warnings, clang-tidy, and cppcheck.",
        "Collected LLM analysis results for all benchmark files.",
        "Built final comparison table and summary percentages.",
        "Wrote final report and generated PDF.",
        "Prepared final presentation and generated PPTX.",
        "Added a user-facing UI for uploading a file and running 5-way comparison (UBSan, Clang warnings, clang-tidy, cppcheck, LLM).",
    ]
    story.extend(bullet_paragraphs(done_items, body))

    story.append(p("Deliverables Status", sub))
    deliverable_items = [
        "Benchmark set of UB programs: Completed.",
        "LLVM/Clang optimization experiment artifacts: Completed.",
        "LLM vs tool comparison: Completed.",
        "Report with soundness/completeness/FP/FN discussion: Completed.",
        "Final presentation with hybrid pipeline proposal: Completed.",
    ]
    story.extend(bullet_paragraphs(deliverable_items, body))

    story.append(p("Is Anything Left?", sub))
    story.append(
        p(
            "No required assignment deliverable is pending. Optional polish items (not required) include visual refinement of slides and optional cleanup of accidental/unneeded files.",
            body,
        )
    )

    story.append(p("Final Readiness", sub))
    story.append(
        p(
            "The project is ready for submission according to the provided Assignment 13 description and deliverables.",
            body,
        )
    )

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT)
