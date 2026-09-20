from __future__ import annotations

from ._latex import escape
from .bibtex import _cite_key


def render(
    used: dict[str, list[str]], items: dict[str, dict], style: str = "plainnat"
) -> str:
    """
    Render used items as a complete, compilable LaTeX document containing a bibliography.
    """
    if not used:
        return "% No citations tracked in this session."

    lines = [
        "\\documentclass[11pt,a4paper]{article}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage[T1]{fontenc}",
        "\\usepackage{hyperref}",
        "\\usepackage[authoryear,round]{natbib}",
        "\\usepackage{geometry}",
        "\\geometry{margin=1in}",
        "",
        "\\begin{document}",
        "",
        "\\section*{Acknowledgments \\& Software Citations}",
        "This work was supported by the following software, algorithms, and datasets:\\\\",
        "",
    ]

    # We use a \nocite{*} approach with an embedded filecontents block for the bibtex
    lines.append("\\begin{itemize}")
    for item_id, used_by in used.items():
        item = items.get(item_id, {"title": item_id})
        title = item.get("title", item_id)
        title = escape(str(title))

        safe_key = _cite_key(item_id)
        lines.append(f"    \\item \\textbf{{{title}}} \\citep{{{safe_key}}}")
        if used_by:
            used_str = escape(", ".join(used_by))
            lines.append(f"    \\\\ \\textit{{(Used via: {used_str})}}")
    lines.append("\\end{itemize}")

    lines.extend(
        [
            "",
            f"\\bibliographystyle{{{style}}}",
            "\\bibliography{ackredit_report}",
            "",
            "\\end{document}",
            "",
        ]
    )

    return "\n".join(lines)
