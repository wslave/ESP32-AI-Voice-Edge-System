from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


CODE_PATTERNS = [
    "*.c",
    "*.cc",
    "*.cpp",
    "*.h",
    "*.hpp",
    "*.java",
    "*.py",
    "*.js",
    "*.jsx",
    "*.ts",
    "*.tsx",
    "*.vue",
    "*.scss",
    "*.css",
    "*.json",
    "*.yml",
    "*.yaml",
    "*.xml",
    "*.sql",
    "*.sh",
    "*.bat",
]


ALIASES = {
    "Wslave": {
        "names": {"Wslave", "Xu DeJia", "许德佳"},
        "emails": {
            "wslave@users.noreply.github.com",
            "95977522+wslave@users.noreply.github.com",
        },
        "color": "#2563eb",
    },
    "Charles-0509": {
        "names": {"Charles", "Charles-0509"},
        "emails": {"74674339+Charles-0509@users.noreply.github.com"},
        "color": "#f97316",
    },
}


@dataclass
class Stats:
    label: str
    churn: int
    additions: int
    deletions: int
    color: str


def run_git_log(repo: Path) -> str:
    cmd = [
        "git",
        "log",
        "--format=@@AUTHOR@@%an <%ae>",
        "--numstat",
        "--all",
        "--",
        *CODE_PATTERNS,
    ]
    return subprocess.check_output(cmd, cwd=repo, text=True, encoding="utf-8", errors="replace")


def match_alias(author_line: str) -> str | None:
    if "<" not in author_line or ">" not in author_line:
        return None
    name = author_line.split("<", 1)[0].strip()
    email = author_line.split("<", 1)[1].rsplit(">", 1)[0].strip()
    for label, info in ALIASES.items():
        if name in info["names"] or email in info["emails"]:
            return label
    return None


def collect_stats(repo: Path) -> list[Stats]:
    raw = run_git_log(repo)
    totals = {
        label: {"churn": 0, "additions": 0, "deletions": 0}
        for label in ALIASES
    }
    current_author: str | None = None

    for line in raw.splitlines():
        if line.startswith("@@AUTHOR@@"):
            current_author = match_alias(line.removeprefix("@@AUTHOR@@"))
            continue
        if not line or current_author is None:
            continue

        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add_raw, del_raw, _path = parts
        if add_raw == "-" or del_raw == "-":
            continue
        try:
            additions = int(add_raw)
            deletions = int(del_raw)
        except ValueError:
            continue

        totals[current_author]["additions"] += additions
        totals[current_author]["deletions"] += deletions
        totals[current_author]["churn"] += additions + deletions

    return [
        Stats(
            label=label,
            churn=totals[label]["churn"],
            additions=totals[label]["additions"],
            deletions=totals[label]["deletions"],
            color=ALIASES[label]["color"],
        )
        for label in ALIASES
    ]


def polar_to_cartesian(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg - 90)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def arc_path(cx: float, cy: float, r: float, start_angle: float, end_angle: float) -> str:
    start = polar_to_cartesian(cx, cy, r, end_angle)
    end = polar_to_cartesian(cx, cy, r, start_angle)
    large_arc = 1 if end_angle - start_angle > 180 else 0
    return (
        f"M {cx:.2f} {cy:.2f} "
        f"L {start[0]:.2f} {start[1]:.2f} "
        f"A {r:.2f} {r:.2f} 0 {large_arc} 0 {end[0]:.2f} {end[1]:.2f} Z"
    )


def build_svg(stats: list[Stats]) -> str:
    total = sum(item.churn for item in stats)
    if total <= 0:
        total = 1

    width = 960
    height = 540
    cx = 255
    cy = 270
    radius = 150

    slices: list[str] = []
    start_angle = 0.0
    non_zero = [item for item in stats if item.churn > 0]
    if len(non_zero) == 1:
        item = non_zero[0]
        slices.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{item.color}" />')
    else:
        for item in stats:
            if item.churn <= 0:
                continue
            angle = 360.0 * item.churn / total
            end_angle = start_angle + angle
            slices.append(f'<path d="{arc_path(cx, cy, radius, start_angle, end_angle)}" fill="{item.color}" />')
            start_angle = end_angle

    rows: list[str] = []
    row_y = 195
    for item in stats:
        percent = item.churn * 100 / total if total else 0
        rows.append(
            "\n".join(
                [
                    f'<rect x="500" y="{row_y}" width="18" height="18" rx="4" fill="{item.color}" />',
                    f'<text x="530" y="{row_y + 14}" class="label-text" font-size="24" font-weight="700">{item.label}</text>',
                    (
                        f'<text x="760" y="{row_y + 14}" class="value-text" font-size="22" text-anchor="end">'
                        f'{percent:.1f}%</text>'
                    ),
                    (
                        f'<text x="530" y="{row_y + 44}" class="muted-text" font-size="18">'
                        f'变更 {item.churn:,} 行（+{item.additions:,} / -{item.deletions:,}）</text>'
                    ),
                ]
            )
        )
        row_y += 92

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subtitle = "统计口径：main 分支全部历史提交，代码类文件新增行 + 删除行"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">贡献者代码行变更占比</title>
  <desc id="desc">按 git log numstat 统计代码类文件的新增与删除行总和。</desc>
  <style>
    :root {{
      --bg: #ffffff;
      --panel: #ffffff;
      --panel-stroke: #e2e8f0;
      --title: #0f172a;
      --text: #334155;
      --muted: #64748b;
      --ring-bg: #e2e8f0;
      --inner: #ffffff;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f172a;
        --panel: #111827;
        --panel-stroke: #334155;
        --title: #f8fafc;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --ring-bg: #1e293b;
        --inner: #0f172a;
      }}
    }}
    .bg {{ fill: var(--bg); }}
    .panel {{ fill: var(--panel); stroke: var(--panel-stroke); stroke-width: 1; }}
    .title-text {{ fill: var(--title); }}
    .label-text, .value-text {{ fill: var(--text); }}
    .muted-text {{ fill: var(--muted); }}
    .ring-bg {{ fill: var(--ring-bg); }}
    .inner-ring {{ fill: var(--inner); }}
  </style>
  <rect class="bg" width="100%" height="100%" rx="20"/>
  <rect class="panel" x="16" y="16" width="928" height="508" rx="18"/>
  <text x="48" y="64" class="title-text" font-size="32" font-weight="700">贡献者代码行变更占比</text>
  <text x="500" y="84" class="muted-text" font-size="18">{subtitle}</text>
  <text x="500" y="112" class="muted-text" font-size="16">自动更新时间：{updated_at}</text>
  <circle cx="{cx}" cy="{cy}" r="{radius}" class="ring-bg" />
  {''.join(slices)}
  <circle cx="{cx}" cy="{cy}" r="74" class="inner-ring" />
  <text x="{cx}" y="{cy - 4}" class="muted-text" text-anchor="middle" font-size="18">总变更</text>
  <text x="{cx}" y="{cy + 30}" class="title-text" text-anchor="middle" font-size="34" font-weight="700">{sum(item.churn for item in stats):,}</text>
  {''.join(rows)}
</svg>
"""


def write_pages_files(output_dir: Path, svg: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    (output_dir / "contribution-line-share.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    output_dir = Path(args.output_dir).resolve()
    stats = collect_stats(repo)
    svg = build_svg(stats)
    write_pages_files(output_dir, svg)


if __name__ == "__main__":
    main()
