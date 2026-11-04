"""Build only the manifest-defined release, without network calls or a language model."""

from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path
from typing import Any

from common import ROOT, fact, load, resolve


def write_json(path: str, value: Any) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def jsonl(path: str, values: list[dict[str, Any]]) -> None:
    (ROOT / path).write_text(
        "".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values),
        encoding="utf-8",
    )


def render_table_html(table: dict[str, Any] | None) -> str:
    if not table:
        return ""
    header = (
        "<tr>"
        + "".join("<th>" + html.escape(cell) + "</th>" for cell in table["headers"])
        + "</tr>"
    )
    rows = "".join(
        "<tr>" + "".join("<td>" + html.escape(cell) + "</td>" for cell in row) + "</tr>"
        for row in table["rows"]
    )
    return "<table><thead>" + header + "</thead><tbody>" + rows + "</tbody></table>"


def build() -> None:
    facts = load("source/facts.yaml")
    documents = load("source/documents.json")
    manifest = load("source/document_manifest.json")
    metadata = {m["id"]: m for m in manifest}
    evidence: list[dict[str, Any]] = []
    (ROOT / "evaluation").mkdir(exist_ok=True)
    for original in documents:
        d = dict(original)
        d["sections"] = [dict(s, text=resolve(s["text"], facts)) for s in d["sections"]]
        for section in d["sections"]:
            if "table" in section:
                section["table"] = {
                    "headers": section["table"]["headers"],
                    "rows": [
                        [resolve(str(cell), facts) for cell in row]
                        for row in section["table"]["rows"]
                    ],
                }
        m = metadata[d["id"]]
        path = ROOT / m["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(m["source_path"], original)
        for section in d["sections"]:
            record = dict(
                id=section["id"],
                document_id=d["id"],
                heading=section["heading"],
                text=section["text"],
                fact_refs=section["fact_refs"],
                canonical_values={r: fact(r, facts) for r in section["fact_refs"]},
                locator={"kind": "heading", "value": section["heading"]},
            )
            if "parent_evidence_id" in section:
                record["parent_evidence_id"] = section["parent_evidence_id"]
            if "table" in section:
                record["table"] = section["table"]
                record["locator"] = {
                    "kind": "table_heading",
                    "value": section["heading"],
                }
            evidence.append(record)
        if d["format"] == "md":
            # All metadata lives in the manifest; no boilerplate enters retrieval text.
            path.write_text(
                "# "
                + d["title"]
                + "\n\n"
                + "\n\n".join(
                    "#" * s.get("level", 2) + " " + s["heading"] + "\n\n" + s["text"]
                    for s in d["sections"]
                )
                + "\n",
                encoding="utf-8",
            )
        elif d["format"] == "html":
            path.write_text(
                '<!doctype html>\n<html lang="en"><meta charset="utf-8"><title>'
                + html.escape(d["title"])
                + "</title><body><h1>"
                + html.escape(d["title"])
                + "</h1>"
                + "".join(
                    '<section id="'
                    + s["id"]
                    + '"><h2>'
                    + html.escape(s["heading"])
                    + "</h2>"
                    + render_table_html(s.get("table"))
                    + "".join(
                        "<p>" + html.escape(p) + "</p>" for p in s["text"].split("\n\n")
                    )
                    + "</section>"
                    for s in d["sections"]
                )
                + "</body></html>\n",
                encoding="utf-8",
            )
        elif d["format"] == "csv":
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle, lineterminator="\n")
                table = d["sections"][0]["table"]
                writer.writerow(table["headers"])
                writer.writerows(table["rows"])
        elif d["format"] == "pdf":
            import reportlab
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.platypus import (
                PageBreak,
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )

            fonts = Path(reportlab.__file__).parent / "fonts"
            pdfmetrics.registerFont(TTFont("CorpusBody", str(fonts / "Vera.ttf")))
            pdfmetrics.registerFont(TTFont("CorpusBold", str(fonts / "VeraBd.ttf")))
            styles = getSampleStyleSheet()
            for style in styles.byName.values():
                style.fontName = "CorpusBody"
            styles["Title"].fontName = styles["Heading1"].fontName = "CorpusBold"
            story = [Paragraph(d["title"], styles["Title"]), Spacer(1, 18)]
            for n, s in enumerate(d["sections"]):
                if (
                    (d["id"] == "D013" and n == 1)
                    or (d["id"] == "D031" and n == 1)
                    or (d["id"] == "D048" and n == 2)
                ):
                    story.append(PageBreak())
                story.append(
                    Paragraph(
                        s["heading"],
                        styles["Heading2" if s.get("level", 2) == 3 else "Heading1"],
                    )
                )
                for paragraph in s["text"].split("\n\n"):
                    story.extend(
                        [
                            Paragraph(html.escape(paragraph), styles["BodyText"]),
                            Spacer(1, 10),
                        ]
                    )
                if "table" in s:
                    data = [s["table"]["headers"], *s["table"]["rows"]]
                    tab = Table(
                        [
                            [
                                Paragraph(html.escape(cell), styles["BodyText"])
                                for cell in row
                            ]
                            for row in data
                        ],
                        repeatRows=1,
                    )
                    tab.setStyle(
                        TableStyle(
                            [
                                ("GRID", (0, 0), (-1, -1), 0.5, "#D9D9D9"),
                                ("BACKGROUND", (0, 0), (-1, 0), "#E7E6E6"),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ]
                        )
                    )
                    story.append(tab)

            def header(canvas: Any, doc: Any) -> None:
                canvas.setFont("CorpusBody", 8)
                canvas.drawString(40, 820, "Teralune Orbit | " + d["id"])
                canvas.drawString(40, 24, "Page " + str(doc.page))

            SimpleDocTemplate(
                str(path),
                pagesize=A4,
                invariant=1,
                title=d["title"],
                author="Teralune Corpus contributors",
            ).build(story, onFirstPage=header, onLaterPages=header)
        elif d["format"] == "docx":
            import zipfile

            from docx import Document
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            from docx.shared import Inches, Pt, RGBColor

            out = Document()
            sec = out.sections[0]
            sec.page_width = Inches(8.5)
            sec.page_height = Inches(11)
            sec.top_margin = sec.bottom_margin = Inches(0.8)
            for style in ["Title", "Heading 1", "Heading 2", "Normal"]:
                out.styles[style].font.color.rgb = RGBColor(0, 0, 0)
                out.styles[style].font.name = "Arial"
            for element in list(out.styles.element.iter(qn("w:pBdr"))):
                element.getparent().remove(element)
            out.styles["Normal"].font.size = Pt(11)
            out.add_heading(d["title"], 0)
            for s in d["sections"]:
                out.add_heading(s["heading"], s.get("level", 2) - 1)
                for p in s["text"].split("\n\n"):
                    out.add_paragraph(p)
                if "table" in s:
                    data = s["table"]
                    table = out.add_table(rows=1, cols=len(data["headers"]))
                    for cell, label in zip(table.rows[0].cells, data["headers"]):
                        cell.text = label
                        shade = OxmlElement("w:shd")
                        shade.set(qn("w:fill"), "E7E6E6")
                        cell._tc.get_or_add_tcPr().append(shade)
                    for row in data["rows"]:
                        for cell, value in zip(table.add_row().cells, row):
                            cell.text = value
                    for row in table.rows:
                        for cell in row.cells:
                            borders = OxmlElement("w:tcBorders")
                            for side in ["top", "left", "bottom", "right"]:
                                el = OxmlElement("w:" + side)
                                el.set(qn("w:val"), "single")
                                el.set(qn("w:sz"), "4")
                                el.set(qn("w:color"), "D9D9D9")
                                borders.append(el)
                            cell._tc.get_or_add_tcPr().append(borders)
            out.core_properties.author = "Teralune Corpus contributors"
            from datetime import datetime, timezone

            out.core_properties.created = out.core_properties.modified = datetime(
                2026, 10, 15, tzinfo=timezone.utc
            )
            out.save(path)
            # Normalize ZIP container times so rebuilds are byte reproducible.
            with zipfile.ZipFile(path) as z:
                entries = {n: z.read(n) for n in z.namelist()}
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
                for name, data in entries.items():
                    info = zipfile.ZipInfo(name, date_time=(2026, 10, 15, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(info, data)
        else:
            raise ValueError(d["format"])
    jsonl("evaluation/evidence.jsonl", evidence)
    questions = load("source/question_plan.json")
    jsonl("evaluation/questions.jsonl", questions)
    splits = load("source/evaluation_splits.json")
    for name in ["smoke", "test"]:
        jsonl(
            f"evaluation/{name}_questions.jsonl",
            [q for q in questions if q["id"] in splits[name]],
        )
    checksums = {
        m["path"]: hashlib.sha256((ROOT / m["path"]).read_bytes()).hexdigest()
        for m in manifest
        if m["phase"] == "release"
    }
    write_json("evaluation/content_checksums.json", checksums)
    print(
        f"Built {len(documents)} documents, {len(evidence)} passages, {len(questions)} questions."
    )


if __name__ == "__main__":
    build()
