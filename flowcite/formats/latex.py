from __future__ import annotations


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
        # escape special latex chars
        title = (
            title.replace("&", "\\&")
            .replace("%", "\\%")
            .replace("#", "\\#")
            .replace("_", "\\_")
        )

        safe_key = item_id.replace(":", "_").replace(" ", "_")
        lines.append(f"    \\item \\textbf{{{title}}} \\citep{{{safe_key}}}")
        if used_by:
            used_str = ", ".join(used_by).replace("_", "\\_")
            lines.append(f"    \\\\ \\textit{{(Used via: {used_str})}}")
    lines.append("\\end{itemize}")

    lines.extend(
        [
            "",
            f"\\bibliographystyle{{{style}}}",
            "\\bibliography{flowcite_report}",
            "",
            "\\end{document}",
            "",
        ]
    )

    return "\n".join(lines)
