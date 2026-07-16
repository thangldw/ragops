"""Render the release-note screenshot and social preview from real core output.

Run with the bundled artifact Python (Pillow is intentionally not a RAGOps
runtime dependency):

    /path/to/artifact-python scripts/render_demo_assets.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ragops.demo import DEMO_BASELINE, DEMO_CANDIDATE, DEMO_SCENARIO  # noqa: E402
from ragops.engine import compare  # noqa: E402
from ragops.loader import responses_from_data, scenario_from_dict  # noqa: E402

WIDTH, HEIGHT = 1200, 675
INK = "#17152f"
MUTED = "#625f72"
PAPER = "#fffef9"
CANVAS = "#f7f5ef"
PURPLE = "#7357ff"
YELLOW = "#ffdc7c"
BLUE = "#bfe8ff"
PINK = "#ffc0dd"
GREEN = "#aee8c9"
RED = "#c8344d"


def font(size: int, *, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    if mono:
        path = "/System/Library/Fonts/SFNSMono.ttf"
    elif bold:
        path = "/System/Library/Fonts/SFNS.ttf"
    else:
        path = "/System/Library/Fonts/SFNS.ttf"
    return ImageFont.truetype(path, size=size)


def base_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), CANVAS)
    draw = ImageDraw.Draw(image)
    for x in range(0, WIDTH, 22):
        for y in range(0, HEIGHT, 22):
            draw.ellipse((x, y, x + 2, y + 2), fill="#d6d2c8")
    draw.rounded_rectangle((45, 35, 1155, 640), radius=24, fill=PAPER, outline=INK, width=3)
    draw.rounded_rectangle((45, 35, 1155, 96), radius=24, fill=INK)
    draw.rectangle((45, 72, 1155, 96), fill=INK)
    draw.ellipse((72, 58, 88, 74), fill=PINK)
    draw.ellipse((98, 58, 114, 74), fill=YELLOW)
    draw.ellipse((124, 58, 140, 74), fill=GREEN)
    draw.text((170, 52), "RAGOps · credential-free demo", fill="white", font=font(22, bold=True))
    return image, draw


def command(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.rounded_rectangle((78, 125, 1122, 196), radius=12, fill=INK)
    draw.text((104, 145), "$", fill=GREEN, font=font(25, bold=True, mono=True))
    draw.text((135, 145), text, fill="white", font=font(25, mono=True))


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    status: str,
    detail: str,
    color: str,
) -> None:
    draw.rounded_rectangle(box, radius=16, fill=color, outline=INK, width=2)
    x1, y1, _, _ = box
    draw.text((x1 + 24, y1 + 20), label, fill=MUTED, font=font(16, bold=True))
    draw.text((x1 + 24, y1 + 52), status, fill=INK if status == "PASS" else RED, font=font(40, bold=True))
    draw.text((x1 + 24, y1 + 105), detail, fill=INK, font=font(18))


def render(stage: int, metrics: list[tuple[str, float, float, float]], gates: tuple[str, ...]) -> Image.Image:
    image, draw = base_frame()
    command(draw, "uvx ragops demo")
    if stage >= 1:
        card(draw, (78, 230, 488, 390), "ACCEPTED BASELINE", "PASS", "Meets every release gate", BLUE)
    if stage >= 3:
        card(
            draw,
            (712, 230, 1122, 390),
            "CANDIDATE",
            "BLOCK" if stage >= 6 else "RUNNING",
            "Citation evidence was removed",
            PINK,
        )
    if stage >= 2:
        draw.line((488, 310, 575, 310), fill=INK, width=4)
        draw.polygon(((575, 302), (591, 310), (575, 318)), fill=INK)
        draw.rounded_rectangle((585, 270, 705, 350), radius=12, fill=YELLOW, outline=INK, width=2)
        draw.text((605, 284), "COMPARE", fill=MUTED, font=font(14, bold=True))
        draw.text((617, 310), "policy", fill=INK, font=font(21, bold=True))
        if stage >= 3:
            draw.line((705, 310, 712, 310), fill=INK, width=4)
    if stage >= 4:
        y = 430
        draw.text((78, y), "METRIC CHANGE", fill=PURPLE, font=font(15, bold=True))
        for index, (name, baseline, candidate, delta) in enumerate(metrics[: stage - 3]):
            row_y = y + 31 + index * 37
            draw.text((78, row_y), name, fill=INK, font=font(19, mono=True))
            draw.text(
                (700, row_y),
                f"{baseline:g}  →  {candidate:g}",
                fill=MUTED,
                font=font(19, mono=True),
            )
            draw.text((1005, row_y), f"{delta:+g}", fill=RED, font=font(19, bold=True, mono=True))
    if stage >= 7:
        draw.rounded_rectangle((78, 565, 1122, 612), radius=10, fill=INK)
        reason = " · ".join(gate.replace("_regression", "") for gate in gates if "regression" in gate)
        draw.text((98, 577), f"RELEASE BLOCKED  ·  {reason}", fill="white", font=font(18, bold=True))
    if stage >= 8:
        draw.text((820, 620), "Open ragops-demo/release-report.html →", fill=PURPLE, font=font(15, bold=True))
    return image


def render_social(metrics: list[tuple[str, float, float, float]]) -> Image.Image:
    image = Image.new("RGB", (1280, 640), CANVAS)
    draw = ImageDraw.Draw(image)
    for x in range(0, 1280, 22):
        for y in range(0, 640, 22):
            draw.ellipse((x, y, x + 2, y + 2), fill="#d6d2c8")
    draw.text((72, 60), "RAG", fill=PURPLE, font=font(38, bold=True))
    draw.text((155, 60), "Ops", fill=INK, font=font(38, bold=True))
    draw.text((72, 132), "Catch RAG and agent regressions", fill=INK, font=font(52, bold=True))
    draw.text((72, 194), "before they reach production.", fill=PURPLE, font=font(52, bold=True))
    draw.rounded_rectangle((72, 292, 558, 480), radius=18, fill=BLUE, outline=INK, width=3)
    draw.text((102, 323), "ACCEPTED BASELINE", fill=MUTED, font=font(18, bold=True))
    draw.text((102, 365), "PASS", fill=INK, font=font(52, bold=True))
    draw.rounded_rectangle((700, 292, 1186, 480), radius=18, fill=PINK, outline=INK, width=3)
    draw.text((730, 323), "REGRESSED CANDIDATE", fill=MUTED, font=font(18, bold=True))
    draw.text((730, 365), "BLOCK", fill=RED, font=font(52, bold=True))
    draw.line((558, 386, 700, 386), fill=INK, width=5)
    draw.polygon(((684, 376), (704, 386), (684, 396)), fill=INK)
    metric_text = "  ·  ".join(f"{name.replace('_', ' ')} {delta:+g}" for name, _, _, delta in metrics)
    draw.text((72, 520), metric_text, fill=INK, font=font(18, mono=True))
    draw.rounded_rectangle((72, 565, 386, 610), radius=9, fill=INK)
    draw.text((94, 576), "$ uvx ragops demo", fill="white", font=font(20, mono=True))
    return image


def main() -> None:
    report = compare(
        scenario_from_dict(DEMO_SCENARIO),
        responses_from_data(DEMO_BASELINE),
        responses_from_data(DEMO_CANDIDATE),
    )
    metrics = [
        (name, report.baseline.metrics[name], report.candidate.metrics[name], delta)
        for name, delta in report.deltas.items()
        if name in {"citation_coverage", "citation_precision", "lexical_groundedness"}
    ]
    frames = [render(stage, metrics, report.failed_gates) for stage in range(9)]
    output_dir = ROOT / "docs" / "demo"
    frames[-1].save(output_dir / "ragops-demo-screenshot.png", optimize=True)
    render_social(metrics).save(output_dir / "social-preview.png", optimize=True)


if __name__ == "__main__":
    main()
