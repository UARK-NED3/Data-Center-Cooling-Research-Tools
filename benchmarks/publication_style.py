"""Shared figure conventions for benchmark publication figures.

Figures are drawn at their final printed size for the IEEE two-column format
(3.5 in single column, 7.16 in double column).  Nothing is scaled after export,
so the 8 pt label and 7 pt tick sizes below are the sizes that appear in print.

Each entity keeps one color and marker across every figure.  Physical streams
use the conventional supply/return pair; benchmark models and local diagnostic
variants use separate hues so that the public synthetic family M1--M3 cannot
be confused with the local M100 diagnostic family D0--D2.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


SINGLE_COLUMN_IN = 3.5
DOUBLE_COLUMN_IN = 7.16
MINIMUM_FONT_PT = 7.0

RC_PARAMS = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    # STIX Sans is close to Arial and, unlike Arial in matplotlib's custom
    # mathtext mode, places superscripts correctly (kg s^-1, m^3 h^-1).
    "mathtext.fontset": "stixsans",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    # Fixed salt so SVG element IDs, and therefore committed files, are stable.
    "svg.hashsalt": "dc-cooling-research-tools",
    "savefig.dpi": 600,
    # Keep the exported page equal to the drawn size; a tight bounding box
    # would crop it and LaTeX would then rescale the text.
    "savefig.bbox": "standard",
    "figure.constrained_layout.use": True,
    "figure.constrained_layout.h_pad": 0.02,
    "figure.constrained_layout.w_pad": 0.02,
    # Full box, inward ticks on all sides, boxed legend.
    "axes.linewidth": 0.8,
    "axes.spines.top": True,
    "axes.spines.right": True,
    "axes.grid": False,
    "axes.labelpad": 3.0,
    "axes.formatter.use_mathtext": True,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "xtick.minor.size": 2.0,
    "ytick.minor.size": 2.0,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.minor.width": 0.6,
    "ytick.minor.width": 0.6,
    "lines.linewidth": 1.2,
    "lines.markersize": 4.0,
    "lines.markeredgewidth": 0.8,
    "legend.frameon": True,
    "legend.framealpha": 1.0,
    "legend.edgecolor": "0.3",
    "legend.fancybox": False,
    "legend.borderpad": 0.4,
    "legend.handlelength": 1.8,
    "legend.handletextpad": 0.5,
    "legend.columnspacing": 1.0,
    "legend.borderaxespad": 0.4,
}

# Okabe-Ito colors, one entity each.
ENTITY_STYLE = {
    "measured": {"color": "#000000", "linestyle": "-", "marker": None},
    "supply": {"color": "#0072B2", "linestyle": "-", "marker": None},
    "return": {"color": "#D55E00", "linestyle": "-", "marker": None},
    "residual_air": {"color": "#7F7F7F", "linestyle": "-", "marker": None},
    "M1": {"color": "#56B4E9", "linestyle": "-", "marker": "o"},
    "M2": {"color": "#E69F00", "linestyle": "--", "marker": "s"},
    "M3": {"color": "#009E73", "linestyle": ":", "marker": "^"},
    "D0": {"color": "#CC79A7", "linestyle": "-", "marker": "o"},
    "D1": {"color": "#CC79A7", "linestyle": "--", "marker": "s"},
    "D2": {"color": "#CC79A7", "linestyle": "-.", "marker": "D"},
}
REFERENCE_GRAY = "#4D4D4D"


def use_style() -> None:
    """Apply the publication rcParams for the current process."""
    plt.rcParams.update(RC_PARAMS)


def panel_label(ax, letter: str, *, x: float = -0.16, y: float = 1.02) -> None:
    """Write a bold (a), (b), ... label outside the upper-left corner of an axis."""
    ax.text(x, y, f"({letter})", transform=ax.transAxes, fontweight="bold", va="bottom", ha="left")


def text_size_violations(fig, minimum_pt: float = MINIMUM_FONT_PT) -> list[str]:
    """Return visible text objects smaller than the minimum printed size."""
    fig.canvas.draw()
    problems = []
    for artist in fig.findobj(matplotlib.text.Text):
        if artist.get_visible() and artist.get_text().strip() and artist.get_fontsize() < minimum_pt - 1.0e-9:
            problems.append(f"{artist.get_text()!r} at {artist.get_fontsize():.1f} pt")
    return problems


def save_figure(fig, stem: Path, *, formats: tuple[str, ...] = ("pdf", "svg", "png")) -> dict[str, Path]:
    """Save a figure at its drawn size after checking the minimum text size."""
    problems = text_size_violations(fig)
    if problems:
        raise ValueError("figure text below the printed minimum: " + "; ".join(problems))
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    # Drop creation timestamps so regenerated vector files are byte-stable.
    metadata = {"pdf": {"CreationDate": None}, "svg": {"Date": None}}
    for extension in formats:
        path = stem.with_suffix(f".{extension}")
        fig.savefig(path, metadata=metadata.get(extension))
        paths[extension] = path
    if "svg" in paths:
        # Matplotlib pads SVG path rows with trailing spaces; strip them so the
        # committed vector files pass repository whitespace checks.
        svg = paths["svg"]
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    return paths
